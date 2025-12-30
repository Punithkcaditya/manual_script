#!/usr/bin/env python3
"""
Update Image Extensions to WebP in Database
Only updates the database records by changing file extensions from other formats to .webp
Does NOT convert actual image files - only updates the JSON data in featured_image and images columns
"""

import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging
import psycopg2
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_extension_update.log'),
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

def parse_json_safely(json_data):
    """Safely handle JSON data - could be string or already parsed object"""
    if not json_data:
        return None
    
    # If it's already a Python object (dict or list), return it directly
    if isinstance(json_data, (dict, list)):
        return json_data
    
    # If it's a string, try to parse it
    if isinstance(json_data, str):
        try:
            return json.loads(json_data)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse JSON string: {str(json_data)[:100]}... Error: {e}")
            return None
    
    # For any other type, try to convert to string first then parse
    try:
        json_str = str(json_data)
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON data: {str(json_data)[:100]}... Error: {e}")
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
            WHERE featured_image IS NOT NULL 
               OR images IS NOT NULL
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

def process_image_extension_updates(flats_data, preview_only=False):
    """
    Process image extension updates for all flats
    Only changes extensions in JSON data - does not touch actual files
    Returns update statistics and updated data
    """
    stats = {
        'flats_processed': 0,
        'extensions_updated': 0,
        'extensions_skipped': 0,
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
            
            # Debug: Log data types
            logger.debug(f"  featured_image type: {type(featured_image)}, value: {str(featured_image)[:100]}")
            logger.debug(f"  images type: {type(images)}, value: {str(images)[:100]}")
            
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
                        
                        # Update the JSON data
                        featured_data['savedName'] = webp_filename
                        new_featured_image = json.dumps(featured_data)
                        flat_updated = True
                        stats['extensions_updated'] += 1
                        
                        if preview_only:
                            logger.info(f"  [PREVIEW] Featured image: {original_filename} -> {webp_filename}")
                        else:
                            logger.info(f"  Featured image: {original_filename} -> {webp_filename}")
                    else:
                        stats['extensions_skipped'] += 1
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
                                
                                # Update the JSON data
                                img_obj_copy = img_obj.copy()
                                img_obj_copy['savedName'] = webp_filename
                                updated_images_data.append(img_obj_copy)
                                flat_updated = True
                                stats['extensions_updated'] += 1
                                
                                if preview_only:
                                    logger.info(f"  [PREVIEW] Image: {original_filename} -> {webp_filename}")
                                else:
                                    logger.info(f"  Image: {original_filename} -> {webp_filename}")
                            else:
                                # Keep as is (already WebP or no extension)
                                updated_images_data.append(img_obj)
                                stats['extensions_skipped'] += 1
                                logger.debug(f"  Image already WebP or no extension: {original_filename}")
                        else:
                            # Keep malformed entries as is
                            updated_images_data.append(img_obj)
                    
                    if updated_images_data:
                        try:
                            new_images = json.dumps(updated_images_data)
                        except Exception as e:
                            logger.error(f"  Error serializing updated images data: {e}")
                            new_images = images  # Keep original if serialization fails
            
            # Add to update list if changes were made
            if flat_updated:
                # Ensure data is properly serialized for database
                try:
                    # Convert to JSON string if it's a Python object
                    if isinstance(new_featured_image, (dict, list)):
                        new_featured_image = json.dumps(new_featured_image)
                    if isinstance(new_images, (dict, list)):
                        new_images = json.dumps(new_images)
                        
                    updated_flats.append({
                        'id': flat_id,
                        'featured_image': new_featured_image,
                        'images': new_images
                    })
                    stats['flats_updated'] += 1
                except Exception as e:
                    logger.error(f"Error preparing data for flat {flat_id}: {e}")
                    stats['flats_failed'] += 1
            
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
    Update database with new WebP extensions
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
        # print("Last query:", update_query)
        # exit()
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
    logger.info("IMAGE EXTENSION UPDATE SUMMARY REPORT")
    logger.info("=" * 70)
    
    logger.info(f"Flats processed: {stats['flats_processed']}")
    logger.info(f"Extensions updated: {stats['extensions_updated']}")
    logger.info(f"Extensions skipped (already WebP): {stats['extensions_skipped']}")
    logger.info(f"Flats requiring updates: {stats['flats_updated']}")
    
    if 'successful_updates' in update_stats:
        logger.info(f"Database updates successful: {update_stats['successful_updates']}")
        logger.info(f"Database updates failed: {update_stats['failed_updates']}")
    
    # Report failed processing
    if failed_updates:
        logger.info(f"\nFailed processing ({len(failed_updates)}):")
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
    preview_only = '--preview' in sys.argv
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python update_image_extensions_to_webp.py [--preview]")
        print("  --preview : Show what would be updated without making changes")
        print("  --help    : Show this help message")
        print()
        print("This script ONLY updates database records by changing file extensions")
        print("from .jpg/.jpeg/.png to .webp in the JSON data.")
        print("It does NOT convert actual image files.")
        sys.exit(0)
    
    logger.info(f"Starting image extension update process...")
    logger.info(f"Preview only: {preview_only}")
    logger.info(f"Log file: image_extension_update.log")
    
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
        
        # Process extension updates
        logger.info("Processing image extension updates...")
        stats, updated_flats, failed_updates = process_image_extension_updates(
            flats_data, preview_only
        )
        
        update_stats = {}
        failed_db_updates = []
        
        # Update database if not preview
        if not preview_only and updated_flats:
            logger.info("Updating database...")
            update_stats, failed_db_updates = update_database(conn, updated_flats)
        elif preview_only:
            logger.info("Preview completed - no database changes made")
        else:
            logger.info("No updates needed")
        
        # Generate report
        generate_report(stats, update_stats, failed_updates, failed_db_updates)
        
        if stats['extensions_updated'] > 0:
            logger.info(f"SUCCESS: Successfully processed {stats['extensions_updated']} extension updates!")
        else:
            logger.info("INFO: No extensions needed updating")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
    
    logger.info("Image extension update process completed.")

if __name__ == "__main__":
    main()
