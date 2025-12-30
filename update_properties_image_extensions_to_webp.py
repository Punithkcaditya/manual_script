#!/usr/bin/env python3
"""
Update Properties Image Extensions to WebP in Database
Only updates the database records by changing file extensions from other formats to .webp
Does NOT convert actual image files - only updates the JSON data in featured_image, image, mobile_image, and meta_image columns
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
        logging.FileHandler('properties_image_extension_update.log'),
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

def get_properties_with_images(conn):
    """
    Fetch properties with image data from database
    Returns list of dictionaries with property information
    """
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT id, featured_image, image, mobile_image, meta_image 
            FROM properties 
            WHERE featured_image IS NOT NULL 
               OR image IS NOT NULL
               OR mobile_image IS NOT NULL
               OR meta_image IS NOT NULL
            ORDER BY id DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        properties_data = []
        for property_id, featured_image, image, mobile_image, meta_image in results:
            properties_data.append({
                'id': property_id,
                'featured_image': featured_image,
                'image': image,
                'mobile_image': mobile_image,
                'meta_image': meta_image
            })
        
        cursor.close()
        logger.info(f"Found {len(properties_data)} properties with image data")
        
        return properties_data
        
    except Exception as e:
        logger.error(f"Error fetching properties data: {e}")
        return []

def process_single_image_field(image_data, field_name, property_id, preview_only=False):
    """
    Process a single image field (featured_image, mobile_image, meta_image)
    Returns (updated_data, extensions_updated_count)
    """
    extensions_updated = 0
    
    if not image_data:
        return image_data, extensions_updated
    
    parsed_data = parse_json_safely(image_data)
    if parsed_data and isinstance(parsed_data, dict) and 'savedName' in parsed_data:
        original_filename = parsed_data['savedName']
        extension = get_image_extension(original_filename)
        
        if extension and extension != '.webp':
            webp_filename = change_extension_to_webp(original_filename)
            
            # Update the JSON data
            updated_data = parsed_data.copy()
            updated_data['savedName'] = webp_filename
            extensions_updated = 1
            
            if preview_only:
                logger.info(f"  [PREVIEW] {field_name}: {original_filename} -> {webp_filename}")
            else:
                logger.info(f"  {field_name}: {original_filename} -> {webp_filename}")
            
            return updated_data, extensions_updated
        else:
            logger.debug(f"  {field_name} already WebP or no extension: {original_filename}")
    
    return image_data, extensions_updated

def process_image_array_field(image_data, field_name, property_id, preview_only=False):
    """
    Process an image array field (image)
    Returns (updated_data, extensions_updated_count)
    """
    extensions_updated = 0
    
    if not image_data:
        return image_data, extensions_updated
    
    parsed_data = parse_json_safely(image_data)
    if parsed_data and isinstance(parsed_data, list):
        updated_images_data = []
        
        for img_obj in parsed_data:
            if isinstance(img_obj, dict) and 'savedName' in img_obj:
                original_filename = img_obj['savedName']
                extension = get_image_extension(original_filename)
                
                if extension and extension != '.webp':
                    webp_filename = change_extension_to_webp(original_filename)
                    
                    # Update the JSON data
                    img_obj_copy = img_obj.copy()
                    img_obj_copy['savedName'] = webp_filename
                    updated_images_data.append(img_obj_copy)
                    extensions_updated += 1
                    
                    if preview_only:
                        logger.info(f"  [PREVIEW] {field_name}: {original_filename} -> {webp_filename}")
                    else:
                        logger.info(f"  {field_name}: {original_filename} -> {webp_filename}")
                else:
                    # Keep as is (already WebP or no extension)
                    updated_images_data.append(img_obj)
                    logger.debug(f"  {field_name} already WebP or no extension: {original_filename}")
            else:
                # Keep malformed entries as is
                updated_images_data.append(img_obj)
        
        return updated_images_data, extensions_updated
    
    return image_data, extensions_updated

def process_property_extension_updates(properties_data, preview_only=False):
    """
    Process image extension updates for all properties
    Only changes extensions in JSON data - does not touch actual files
    Returns update statistics and updated data
    """
    stats = {
        'properties_processed': 0,
        'extensions_updated': 0,
        'extensions_skipped': 0,
        'properties_updated': 0,
        'properties_failed': 0
    }
    
    updated_properties = []
    failed_updates = []
    
    for property_data in properties_data:
        try:
            stats['properties_processed'] += 1
            property_id = property_data['id']
            
            logger.info(f"Processing property ID: {property_id}")
            
            # Track if any changes were made to this property
            property_updated = False
            property_extensions_updated = 0
            
            # Process each image field
            new_featured_image = property_data['featured_image']
            new_image = property_data['image']
            new_mobile_image = property_data['mobile_image']
            new_meta_image = property_data['meta_image']
            
            # Process featured_image (single image object)
            if property_data['featured_image']:
                new_featured_image, updated_count = process_single_image_field(
                    property_data['featured_image'], 'featured_image', property_id, preview_only
                )
                if updated_count > 0:
                    property_updated = True
                    property_extensions_updated += updated_count
            
            # Process image (array of image objects)
            if property_data['image']:
                new_image, updated_count = process_image_array_field(
                    property_data['image'], 'image', property_id, preview_only
                )
                if updated_count > 0:
                    property_updated = True
                    property_extensions_updated += updated_count
            
            # Process mobile_image (single image object)
            if property_data['mobile_image']:
                new_mobile_image, updated_count = process_single_image_field(
                    property_data['mobile_image'], 'mobile_image', property_id, preview_only
                )
                if updated_count > 0:
                    property_updated = True
                    property_extensions_updated += updated_count
            
            # Process meta_image (single image object)
            if property_data['meta_image']:
                new_meta_image, updated_count = process_single_image_field(
                    property_data['meta_image'], 'meta_image', property_id, preview_only
                )
                if updated_count > 0:
                    property_updated = True
                    property_extensions_updated += updated_count
            
            # Add to update list if changes were made
            if property_updated:
                # Ensure data is properly serialized for database
                try:
                    # Convert to JSON string if it's a Python object
                    if isinstance(new_featured_image, (dict, list)):
                        new_featured_image = json.dumps(new_featured_image)
                    if isinstance(new_image, (dict, list)):
                        new_image = json.dumps(new_image)
                    if isinstance(new_mobile_image, (dict, list)):
                        new_mobile_image = json.dumps(new_mobile_image)
                    if isinstance(new_meta_image, (dict, list)):
                        new_meta_image = json.dumps(new_meta_image)
                        
                    updated_properties.append({
                        'id': property_id,
                        'featured_image': new_featured_image,
                        'image': new_image,
                        'mobile_image': new_mobile_image,
                        'meta_image': new_meta_image
                    })
                    stats['properties_updated'] += 1
                    stats['extensions_updated'] += property_extensions_updated
                except Exception as e:
                    logger.error(f"Error preparing data for property {property_id}: {e}")
                    stats['properties_failed'] += 1
            
        except Exception as e:
            stats['properties_failed'] += 1
            failed_updates.append({
                'property_id': property_data['id'],
                'error': str(e)
            })
            logger.error(f"Error processing property {property_data['id']}: {e}")
            continue
    
    return stats, updated_properties, failed_updates

def update_database(conn, updated_properties):
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
            UPDATE properties 
            SET featured_image = %s, image = %s, mobile_image = %s, meta_image = %s, modified_date = %s 
            WHERE id = %s
        """
        
        current_time = datetime.now()
        
        for property_data in updated_properties:
            try:
                cursor.execute(update_query, (
                    property_data['featured_image'],
                    property_data['image'],
                    property_data['mobile_image'],
                    property_data['meta_image'],
                    current_time,
                    property_data['id']
                ))
                
                if cursor.rowcount > 0:
                    update_stats['successful_updates'] += 1
                    logger.info(f"Updated database for property ID: {property_data['id']}")
                else:
                    update_stats['failed_updates'] += 1
                    failed_db_updates.append({
                        'property_id': property_data['id'],
                        'error': 'No rows affected'
                    })
                    logger.warning(f"No rows updated for property ID: {property_data['id']}")
                
            except Exception as e:
                update_stats['failed_updates'] += 1
                failed_db_updates.append({
                    'property_id': property_data['id'],
                    'error': str(e)
                })
                logger.error(f"Database update failed for property {property_data['id']}: {e}")
                conn.rollback()
                continue
        
        # Commit all successful updates
        conn.commit()
        cursor.close()
        
    except Exception as e:
        logger.error(f"Database update process failed: {e}")
        conn.rollback()
        update_stats['failed_updates'] = len(updated_properties)
    
    return update_stats, failed_db_updates

def generate_report(stats, update_stats, failed_updates, failed_db_updates):
    """Generate comprehensive report"""
    logger.info("=" * 70)
    logger.info("PROPERTIES IMAGE EXTENSION UPDATE SUMMARY REPORT")
    logger.info("=" * 70)
    
    logger.info(f"Properties processed: {stats['properties_processed']}")
    logger.info(f"Extensions updated: {stats['extensions_updated']}")
    logger.info(f"Extensions skipped (already WebP): {stats['extensions_skipped']}")
    logger.info(f"Properties requiring updates: {stats['properties_updated']}")
    
    if 'successful_updates' in update_stats:
        logger.info(f"Database updates successful: {update_stats['successful_updates']}")
        logger.info(f"Database updates failed: {update_stats['failed_updates']}")
    
    # Report failed processing
    if failed_updates:
        logger.info(f"\nFailed processing ({len(failed_updates)}):")
        for failure in failed_updates:
            logger.info(f"  Property ID {failure['property_id']}: {failure['error']}")
    
    # Report failed database updates
    if failed_db_updates:
        logger.info(f"\nFailed database updates ({len(failed_db_updates)}):")
        for failure in failed_db_updates:
            logger.info(f"  Property ID {failure['property_id']}: {failure['error']}")
    
    logger.info("=" * 70)

def main():
    """Main function"""
    preview_only = '--preview' in sys.argv
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python update_properties_image_extensions_to_webp.py [--preview]")
        print("  --preview : Show what would be updated without making changes")
        print("  --help    : Show this help message")
        print()
        print("This script ONLY updates database records by changing file extensions")
        print("from .jpg/.jpeg/.png to .webp in the JSON data for properties table.")
        print("It processes: featured_image, image, mobile_image, and meta_image columns.")
        print("It does NOT convert actual image files.")
        sys.exit(0)
    
    logger.info(f"Starting properties image extension update process...")
    logger.info(f"Preview only: {preview_only}")
    logger.info(f"Log file: properties_image_extension_update.log")
    
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
        # Get properties with images
        logger.info("Fetching properties with image data...")
        properties_data = get_properties_with_images(conn)
        
        if not properties_data:
            logger.error("No properties found with image data. Exiting.")
            sys.exit(1)
        
        # Process extension updates
        logger.info("Processing image extension updates...")
        stats, updated_properties, failed_updates = process_property_extension_updates(
            properties_data, preview_only
        )
        
        update_stats = {}
        failed_db_updates = []
        
        # Update database if not preview
        if not preview_only and updated_properties:
            logger.info("Updating database...")
            update_stats, failed_db_updates = update_database(conn, updated_properties)
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
    
    logger.info("Properties image extension update process completed.")

if __name__ == "__main__":
    main()
