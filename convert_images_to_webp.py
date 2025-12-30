#!/usr/bin/env python3
"""
Image Format Conversion Script for Flats
Converts non-WebP images to WebP format and updates the database records.
Handles both featured_image and images JSON fields.
"""

import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging
import psycopg2
from PIL import Image
import shutil
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_conversion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Warning: Could not load .env file: {e}")
    logger.info("Continuing with system environment variables...")

def connect_db():
    """Create database connection using environment variables"""
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            options=os.getenv("DB_OPTIONS", "")
        )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def get_image_extension(filename):
    """Get file extension from filename"""
    if not filename:
        return None
    return Path(filename).suffix.lower()

def change_extension_to_webp(filename):
    """Change file extension to .webp while preserving the base name"""
    if not filename:
        return None
    path = Path(filename)
    return str(path.with_suffix('.webp'))

def parse_json_safely(json_str):
    """Safely parse JSON string, return None if invalid"""
    if not json_str:
        return None
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {json_str[:100]}... Error: {e}")
        return None

def get_flats_with_images(conn):
    """
    Fetch flats with image data from database
    Returns list of dictionaries with flat information
    """
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT id, featured_image, images 
            FROM flats 
            WHERE (featured_image IS NOT NULL AND featured_image != '') 
               OR (images IS NOT NULL AND images != '')
            ORDER BY id DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        flats_data = []
        for flat_id, featured_image, images in results:
            flats_data.append({
                'id': flat_id,
                'featured_image': featured_image,
                'images': images
            })
        
        cursor.close()
        logger.info(f"Found {len(flats_data)} flats with image data")
        
        return flats_data
        
    except Exception as e:
        logger.error(f"Error fetching flats data: {e}")
        return []

def convert_image_to_webp(source_path, target_path, quality=85):
    """
    Convert image to WebP format
    Returns True if successful, False otherwise
    """
    try:
        # Check if source file exists
        if not os.path.exists(source_path):
            logger.warning(f"Source image not found: {source_path}")
            return False
        
        # Open and convert image
        with Image.open(source_path) as img:
            # Convert RGBA to RGB if necessary (WebP supports both, but RGB is more compatible)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Save as WebP
            img.save(target_path, 'WebP', quality=quality, optimize=True)
            
        logger.debug(f"Successfully converted {source_path} to {target_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to convert {source_path} to WebP: {e}")
        return False

def process_image_conversions(flats_data, images_directory, dry_run=False):
    """
    Process image conversions for all flats
    Returns conversion statistics and updated data
    """
    stats = {
        'flats_processed': 0,
        'images_converted': 0,
        'images_skipped': 0,
        'conversion_failures': 0,
        'flats_updated': 0,
        'flats_failed': 0
    }
    
    updated_flats = []
    failed_updates = []
    
    for flat_data in flats_data:
        try:
            stats['flats_processed'] += 1
            flat_id = flat_data['id']
            featured_image = flat_data['featured_image']
            images = flat_data['images']
            
            logger.info(f"Processing flat ID: {flat_id}")
            
            # Track if any changes were made to this flat
            flat_updated = False
            new_featured_image = featured_image
            new_images = images
            
            # Process featured_image
            if featured_image:
                featured_data = parse_json_safely(featured_image)
                if featured_data and isinstance(featured_data, dict) and 'savedName' in featured_data:
                    original_filename = featured_data['savedName']
                    extension = get_image_extension(original_filename)
                    
                    if extension and extension != '.webp':
                        webp_filename = change_extension_to_webp(original_filename)
                        
                        if not dry_run:
                            # Convert the actual image file
                            source_path = os.path.join(images_directory, original_filename)
                            target_path = os.path.join(images_directory, webp_filename)
                            
                            if convert_image_to_webp(source_path, target_path):
                                # Update the JSON data
                                featured_data['savedName'] = webp_filename
                                new_featured_image = json.dumps(featured_data)
                                flat_updated = True
                                stats['images_converted'] += 1
                                logger.info(f"  Featured image: {original_filename} -> {webp_filename}")
                            else:
                                stats['conversion_failures'] += 1
                                logger.error(f"  Failed to convert featured image: {original_filename}")
                        else:
                            logger.info(f"  [DRY RUN] Would convert featured image: {original_filename} -> {webp_filename}")
                            stats['images_converted'] += 1
                            flat_updated = True
                    else:
                        stats['images_skipped'] += 1
                        logger.debug(f"  Featured image already WebP or no extension: {original_filename}")
            
            # Process images array
            if images:
                images_data = parse_json_safely(images)
                if images_data and isinstance(images_data, list):
                    updated_images_data = []
                    
                    for img_obj in images_data:
                        if isinstance(img_obj, dict) and 'savedName' in img_obj:
                            original_filename = img_obj['savedName']
                            extension = get_image_extension(original_filename)
                            
                            if extension and extension != '.webp':
                                webp_filename = change_extension_to_webp(original_filename)
                                
                                if not dry_run:
                                    # Convert the actual image file
                                    source_path = os.path.join(images_directory, original_filename)
                                    target_path = os.path.join(images_directory, webp_filename)
                                    
                                    if convert_image_to_webp(source_path, target_path):
                                        # Update the JSON data
                                        img_obj_copy = img_obj.copy()
                                        img_obj_copy['savedName'] = webp_filename
                                        updated_images_data.append(img_obj_copy)
                                        flat_updated = True
                                        stats['images_converted'] += 1
                                        logger.info(f"  Image: {original_filename} -> {webp_filename}")
                                    else:
                                        # Keep original if conversion failed
                                        updated_images_data.append(img_obj)
                                        stats['conversion_failures'] += 1
                                        logger.error(f"  Failed to convert image: {original_filename}")
                                else:
                                    logger.info(f"  [DRY RUN] Would convert image: {original_filename} -> {webp_filename}")
                                    img_obj_copy = img_obj.copy()
                                    img_obj_copy['savedName'] = webp_filename
                                    updated_images_data.append(img_obj_copy)
                                    stats['images_converted'] += 1
                                    flat_updated = True
                            else:
                                # Keep as is (already WebP or no extension)
                                updated_images_data.append(img_obj)
                                stats['images_skipped'] += 1
                                logger.debug(f"  Image already WebP or no extension: {original_filename}")
                        else:
                            # Keep malformed entries as is
                            updated_images_data.append(img_obj)
                    
                    if flat_updated and updated_images_data:
                        new_images = json.dumps(updated_images_data)
            
            # Add to update list if changes were made
            if flat_updated:
                updated_flats.append({
                    'id': flat_id,
                    'featured_image': new_featured_image,
                    'images': new_images
                })
                stats['flats_updated'] += 1
            
        except Exception as e:
            stats['flats_failed'] += 1
            failed_updates.append({
                'flat_id': flat_data['id'],
                'error': str(e)
            })
            logger.error(f"Error processing flat {flat_data['id']}: {e}")
            continue
    
    return stats, updated_flats, failed_updates

def update_database(conn, updated_flats):
    """
    Update database with converted image data
    Returns update statistics
    """
    update_stats = {
        'successful_updates': 0,
        'failed_updates': 0
    }
    
    failed_db_updates = []
    
    try:
        cursor = conn.cursor()
        
        update_query = """
            UPDATE flats 
            SET featured_image = %s, images = %s, modified_date = %s 
            WHERE id = %s
        """
        
        current_time = datetime.now()
        
        for flat_data in updated_flats:
            try:
                cursor.execute(update_query, (
                    flat_data['featured_image'],
                    flat_data['images'],
                    current_time,
                    flat_data['id']
                ))
                
                if cursor.rowcount > 0:
                    update_stats['successful_updates'] += 1
                    logger.info(f"Updated database for flat ID: {flat_data['id']}")
                else:
                    update_stats['failed_updates'] += 1
                    failed_db_updates.append({
                        'flat_id': flat_data['id'],
                        'error': 'No rows affected'
                    })
                    logger.warning(f"No rows updated for flat ID: {flat_data['id']}")
                
            except Exception as e:
                update_stats['failed_updates'] += 1
                failed_db_updates.append({
                    'flat_id': flat_data['id'],
                    'error': str(e)
                })
                logger.error(f"Database update failed for flat {flat_data['id']}: {e}")
                conn.rollback()
                continue
        
        # Commit all successful updates
        conn.commit()
        cursor.close()
        
    except Exception as e:
        logger.error(f"Database update process failed: {e}")
        conn.rollback()
        update_stats['failed_updates'] = len(updated_flats)
    
    return update_stats, failed_db_updates

def generate_report(stats, update_stats, failed_updates, failed_db_updates):
    """Generate comprehensive report"""
    logger.info("=" * 70)
    logger.info("IMAGE CONVERSION SUMMARY REPORT")
    logger.info("=" * 70)
    
    logger.info(f"Flats processed: {stats['flats_processed']}")
    logger.info(f"Images converted successfully: {stats['images_converted']}")
    logger.info(f"Images skipped (already WebP): {stats['images_skipped']}")
    logger.info(f"Image conversion failures: {stats['conversion_failures']}")
    logger.info(f"Flats requiring updates: {stats['flats_updated']}")
    
    if 'successful_updates' in update_stats:
        logger.info(f"Database updates successful: {update_stats['successful_updates']}")
        logger.info(f"Database updates failed: {update_stats['failed_updates']}")
    
    # Report failed conversions
    if failed_updates:
        logger.info(f"\nFailed conversions ({len(failed_updates)}):")
        for failure in failed_updates:
            logger.info(f"  Flat ID {failure['flat_id']}: {failure['error']}")
    
    # Report failed database updates
    if failed_db_updates:
        logger.info(f"\nFailed database updates ({len(failed_db_updates)}):")
        for failure in failed_db_updates:
            logger.info(f"  Flat ID {failure['flat_id']}: {failure['error']}")
    
    logger.info("=" * 70)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python convert_images_to_webp.py <images_directory> [--dry-run] [--quality=85]")
        print("Example: python convert_images_to_webp.py /path/to/images --dry-run")
        print("  --dry-run : Show what would be converted without making changes")
        print("  --quality : WebP quality (1-100, default: 85)")
        sys.exit(1)
    
    images_directory = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    # Parse quality parameter
    quality = 85
    for arg in sys.argv:
        if arg.startswith('--quality='):
            try:
                quality = int(arg.split('=')[1])
                quality = max(1, min(100, quality))  # Clamp between 1-100
            except ValueError:
                logger.warning("Invalid quality value, using default 85")
    
    logger.info(f"Starting image conversion process...")
    logger.info(f"Images directory: {images_directory}")
    logger.info(f"Dry run mode: {dry_run}")
    logger.info(f"WebP quality: {quality}")
    logger.info(f"Log file: image_conversion.log")
    
    # Verify images directory exists
    if not os.path.exists(images_directory):
        logger.error(f"Images directory not found: {images_directory}")
        sys.exit(1)
    
    # Verify environment variables
    required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Connect to database
    logger.info("Connecting to database...")
    conn = connect_db()
    
    if conn is None:
        logger.error("Could not connect to database. Exiting.")
        sys.exit(1)
    
    try:
        # Get flats with images
        logger.info("Fetching flats with image data...")
        flats_data = get_flats_with_images(conn)
        
        if not flats_data:
            logger.error("No flats found with image data. Exiting.")
            sys.exit(1)
        
        # Process conversions
        logger.info("Processing image conversions...")
        stats, updated_flats, failed_updates = process_image_conversions(
            flats_data, images_directory, dry_run
        )
        
        update_stats = {}
        failed_db_updates = []
        
        # Update database if not dry run
        if not dry_run and updated_flats:
            logger.info("Updating database...")
            update_stats, failed_db_updates = update_database(conn, updated_flats)
        elif dry_run:
            logger.info("Dry run completed - no database changes made")
        else:
            logger.info("No updates needed")
        
        # Generate report
        generate_report(stats, update_stats, failed_updates, failed_db_updates)
        
        if stats['images_converted'] > 0:
            logger.info(f"✅ Successfully processed {stats['images_converted']} image conversions!")
        else:
            logger.info("ℹ️  No images needed conversion")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
    
    logger.info("Image conversion process completed.")

if __name__ == "__main__":
    main()
