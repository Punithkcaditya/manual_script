#!/usr/bin/env python3
"""
Meta Data Generation Script for Flats
Generates meta_title and meta_description based on flat_type and updates the flats table.
"""

import psycopg2
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meta_data_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

def clean_string_value(value):
    """Clean and normalize string values"""
    if value is None:
        return None
    
    try:
        str_value = str(value).strip()
        if not str_value or str_value.lower() in ['null', 'none', 'n/a', 'na', '-', '']:
            return None
        return str_value
    except Exception:
        return None

def get_flats_data(conn):
    """
    Fetch flats data from database
    Returns list of dictionaries with flat information
    """
    try:
        cursor = conn.cursor()
        
        # Get flats with their current meta data and related information
        query = """
            SELECT 
                id, 
                flat_number, 
                name,
                meta_title, 
                meta_description,
                flat_mailing_city,
                flat_mailing_state,
                property_master,
                flat_category
            FROM flats 
            WHERE property_id = 1169 
              AND meta_title IS NULL 
              AND meta_description IS NULL
              AND flat_number IS NOT NULL AND flat_number != ''
            ORDER BY flat_number
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        flats_data = []
        for row in results:
            flat_id, flat_number, name, current_meta_title, current_meta_desc, city, state, property_master, flat_category = row
            
            flats_data.append({
                'id': flat_id,
                'flat_number': clean_string_value(flat_number),
                'name': clean_string_value(name),
                'current_meta_title': clean_string_value(current_meta_title),
                'current_meta_description': clean_string_value(current_meta_desc),
                'city': clean_string_value(city) or 'Koramangala',  # Default to Koramangala
                'state': clean_string_value(state) or 'Bangalore',
                'property_master': clean_string_value(property_master) or 'Kots Rive',
                'flat_category': clean_string_value(flat_category) or 'Studio'
            })
        
        cursor.close()
        logger.info(f"Found {len(flats_data)} flats with flat_number data for property_id 1169")
        
        return flats_data
        
    except Exception as e:
        logger.error(f"Error fetching flats data: {e}")
        return []

def determine_flat_category(flat_number, existing_category):
    """
    Determine flat category based on flat_number or existing category
    """
    if existing_category and existing_category.lower() not in ['null', 'none', '']:
        return existing_category
    
    # Try to determine from flat_number (though this is less reliable)
    flat_number_lower = flat_number.lower() if flat_number else ''
    
    if any(keyword in flat_number_lower for keyword in ['studio', '1rk', '1 rk']):
        return 'Studio'
    elif any(keyword in flat_number_lower for keyword in ['1bhk', '1 bhk', '1-bhk']):
        return '1BHK'
    elif any(keyword in flat_number_lower for keyword in ['2bhk', '2 bhk', '2-bhk']):
        return '2BHK'
    elif any(keyword in flat_number_lower for keyword in ['3bhk', '3 bhk', '3-bhk']):
        return '3BHK'
    else:
        return 'Studio'  # Default fallback

def generate_meta_title(flat_number, flat_category, city, property_master):
    """
    Generate meta title based on the pattern:
    {flat_number}: Fully Furnished {flat_category} Flat in {city} | {property_master}
    """
    try:
        # Clean inputs
        flat_number = flat_number or 'A601'
        flat_category = flat_category or 'Studio'
        city = city or 'Koramangala'
        property_master = property_master or 'Kots Rive'
        
        # Generate meta title
        # meta_title = f"{flat_number}: Fully Furnished {flat_category} Flat in {city} | {property_master}"
        meta_title = f"{flat_number}:  Fully furnished 1 BHK flat in Whitefield | Kots Bien"
        
        # Ensure it's not too long (recommended max 60 characters for SEO)
        if len(meta_title) > 60:
            # Try shorter version
            # meta_title = f"{flat_number}: {flat_category} Flat in {city} | {property_master}"
            meta_title = f"{flat_number}:  Fully furnished 1 BHK flat in Whitefield | Kots Bien"

            
        return meta_title
        
    except Exception as e:
        logger.warning(f"Error generating meta title for {flat_number}: {e}")
        return f"{flat_number}: Fully Furnished Studio Flat in Koramangala | Kots Rive"

def generate_meta_description(flat_number, flat_category, city, property_master):
    """
    Generate meta description based on the pattern:
    {flat_number} is a fully furnished {flat_category} flat for rent in {city} at {property_master}. 
    Book now with no Hidden cost, hassle free living near Maruti Nagar for men, women and couples
    """
    try:
        # Clean inputs
        flat_number = flat_number or 'A601'
        flat_category = flat_category.lower() if flat_category else 'studio'
        city = city or 'Koramangala'
        property_master = property_master or 'Kots Rive'
        
        # Generate meta description
        # meta_description = (
        #     f"{flat_number} is a fully furnished {flat_category} flat for rent in {city} at {property_master}. "
        #     f"Book now with no Hidden cost, hassle free living near Maruti Nagar for men, women and couples"
        # )
        meta_description = (
            f"{flat_number} is a fully furnished 1 BHK rental flat in Siddapura, Whitefield. Book now and experience premium living with world class amenities at Kots Bien."
        )
        
        # Ensure it's not too long (recommended max 160 characters for SEO)
        if len(meta_description) > 160:
            # Try shorter version
            # meta_description = (
            #     f"{flat_number} is a fully furnished {flat_category} flat for rent in {city} at {property_master}. "
            #     f"Book now with no hidden cost, hassle free living for men, women and couples"
            # )
            meta_description = (
                f"{flat_number} is a fully furnished 1 BHK rental flat in Siddapura, Whitefield. Book now and experience premium living with world class amenities at Kots Bien."
            )
        
        return meta_description
        
    except Exception as e:
        logger.warning(f"Error generating meta description for {flat_number}: {e}")
        return f"{flat_number} is a fully furnished studio flat for rent in Koramangala at Kots Rive. Book now with no Hidden cost, hassle free living near Maruti Nagar for men, women and couples"

def update_meta_data(conn, flats_data, force_update=False):
    """
    Update meta_title and meta_description for flats
    """
    stats = {
        'processed': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    try:
        cursor = conn.cursor()
        
        # Prepare update query
        update_query = """
            UPDATE flats 
            SET meta_title = %s, meta_description = %s, modified_date = %s 
            WHERE id = %s
        """
        
        current_time = datetime.now()
        
        for flat_data in flats_data:
            try:
                stats['processed'] += 1
                flat_id = flat_data['id']
                flat_number = flat_data['flat_number']
                
                if not flat_number:
                    stats['skipped'] += 1
                    logger.debug(f"Skipping flat ID {flat_id}: No flat_number")
                    continue
                
                # Determine flat category
                flat_category = determine_flat_category(flat_number, flat_data['flat_category'])
                
                # Generate new meta data
                new_meta_title = generate_meta_title(
                    flat_number, 
                    flat_category, 
                    flat_data['city'], 
                    flat_data['property_master']
                )
                
                new_meta_description = generate_meta_description(
                    flat_number, 
                    flat_category, 
                    flat_data['city'], 
                    flat_data['property_master']
                )
                
                # Check if update is needed
                current_meta_title = flat_data['current_meta_title']
                current_meta_desc = flat_data['current_meta_description']
                
                if not force_update:
                    if (current_meta_title == new_meta_title and 
                        current_meta_desc == new_meta_description):
                        stats['skipped'] += 1
                        logger.debug(f"Skipping flat {flat_number}: Meta data unchanged")
                        continue
                
                # Perform the update
                cursor.execute(update_query, (new_meta_title, new_meta_description, current_time, flat_id))
                
                if cursor.rowcount > 0:
                    stats['updated'] += 1
                    logger.info(f"Updated meta data for flat {flat_number} (ID: {flat_id})")
                    logger.debug(f"  Meta Title: {new_meta_title}")
                    logger.debug(f"  Meta Description: {new_meta_description}")
                else:
                    stats['errors'] += 1
                    logger.warning(f"No rows updated for flat {flat_number} (ID: {flat_id})")
                
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error updating flat {flat_data.get('flat_number', 'Unknown')}: {e}")
                conn.rollback()  # Rollback this transaction
                continue
        
        # Commit all successful updates
        conn.commit()
        cursor.close()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error in update process: {e}")
        conn.rollback()
        stats['errors'] += len(flats_data)
        return stats

def preview_changes(flats_data, limit=5):
    """
    Preview the changes that would be made (first few records)
    """
    logger.info("=" * 80)
    logger.info("PREVIEW OF CHANGES (First {} records)".format(min(limit, len(flats_data))))
    logger.info("=" * 80)
    
    for i, flat_data in enumerate(flats_data[:limit]):
        flat_number = flat_data['flat_number']
        if not flat_number:
            continue
            
        flat_category = determine_flat_category(flat_number, flat_data['flat_category'])
        
        new_meta_title = generate_meta_title(
            flat_number, 
            flat_category, 
            flat_data['city'], 
            flat_data['property_master']
        )
        
        new_meta_description = generate_meta_description(
            flat_number, 
            flat_category, 
            flat_data['city'], 
            flat_data['property_master']
        )
        
        logger.info(f"\nFlat Number: {flat_number}")
        logger.info(f"Current Meta Title: {flat_data['current_meta_title'] or 'None'}")
        logger.info(f"New Meta Title: {new_meta_title}")
        logger.info(f"Current Meta Description: {flat_data['current_meta_description'] or 'None'}")
        logger.info(f"New Meta Description: {new_meta_description}")
        logger.info("-" * 40)

def generate_report(stats, total_flats):
    """Generate a summary report of the update process"""
    
    logger.info("=" * 60)
    logger.info("META DATA GENERATION SUMMARY REPORT")
    logger.info("=" * 60)
    
    logger.info(f"Total flats in database: {total_flats}")
    logger.info(f"Flats processed: {stats['processed']}")
    logger.info(f"Successfully updated: {stats['updated']}")
    logger.info(f"Skipped (unchanged): {stats['skipped']}")
    logger.info(f"Errors during update: {stats['errors']}")
    
    if stats['updated'] > 0:
        logger.info(f"\n✅ Successfully generated meta data for {stats['updated']} flats!")
    else:
        logger.info(f"\nℹ️  No meta data was updated")
    
    logger.info("=" * 60)

def main():
    """Main function to run the meta data generation"""
    
    # Parse command line arguments
    force_update = False
    preview_only = False
    
    if len(sys.argv) > 1:
        if '--force' in sys.argv:
            force_update = True
        if '--preview' in sys.argv:
            preview_only = True
        if '--help' in sys.argv or '-h' in sys.argv:
            print("Usage: python generate_meta_data.py [--force] [--preview]")
            print("  --force   : Update all records even if meta data already exists")
            print("  --preview : Show preview of changes without updating database")
            print("  --help    : Show this help message")
            sys.exit(0)
    
    logger.info("Starting meta data generation for flats...")
    logger.info(f"Log file: meta_data_generation.log")
    logger.info(f"Force update: {force_update}")
    logger.info(f"Preview only: {preview_only}")
    
    # Verify environment variables
    required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please ensure your .env file contains all required database connection details")
        sys.exit(1)
    
    # Connect to database
    logger.info("Connecting to database...")
    conn = connect_db()
    
    if conn is None:
        logger.error("Could not connect to database. Exiting.")
        sys.exit(1)
    
    try:
        # Get flats data
        logger.info("Fetching flats data from database...")
        flats_data = get_flats_data(conn)
        
        if not flats_data:
            logger.error("No flats found with flat_number data for property_id 1169 where meta data is NULL. Exiting.")
            sys.exit(1)
        
        # Preview changes
        if preview_only or len(flats_data) > 0:
            preview_changes(flats_data, limit=10)
        
        if preview_only:
            logger.info("Preview mode - no changes made to database.")
            sys.exit(0)
        
        # Ask for confirmation if not forcing
        if not force_update and len(flats_data) > 10:
            response = input(f"\nProceed to update meta data for {len(flats_data)} flats? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                logger.info("Operation cancelled by user.")
                sys.exit(0)
        
        # Update meta data
        logger.info("Updating meta data...")
        stats = update_meta_data(conn, flats_data, force_update)
        
        # Generate report
        generate_report(stats, len(flats_data))
        
    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}")
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
    
    logger.info("Meta data generation process completed.")

if __name__ == "__main__":
    main()
