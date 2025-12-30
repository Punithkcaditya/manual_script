#!/usr/bin/env python3
"""
Flat Description Update Script
Updates the description column in the flats table based on Excel data matching Flat Master Name to name column.
Only updates flats that already have existing description data.
Cleans and trims the description content before updating.
"""

import pandas as pd
import psycopg2
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flat_description_update.log'),
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

def clean_description(description):
    """
    Clean and normalize description text
    Removes leading/trailing spaces, extra whitespace, and normalizes the content
    """
    if pd.isna(description) or description is None:
        return None
    
    try:
        # Convert to string and strip leading/trailing spaces
        cleaned = str(description).strip()
        
        # Handle empty strings
        if not cleaned or cleaned.lower() in ['null', 'none', 'n/a', 'na', '-', '']:
            return None
        
        # Remove excessive whitespace (multiple spaces, tabs, newlines)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove null bytes and other control characters except newlines and tabs
        cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\t\n\r')
        
        # Final trim
        cleaned = cleaned.strip()
        
        if not cleaned:
            return None
            
        return cleaned
        
    except Exception as e:
        logger.warning(f"Error cleaning description '{str(description)[:50]}...': {e}")
        return None

def clean_flat_name(flat_name):
    """Clean and normalize flat name for matching"""
    if pd.isna(flat_name) or flat_name is None:
        return None
    
    try:
        cleaned = str(flat_name).strip()
        if not cleaned or cleaned.lower() in ['null', 'none', 'n/a', 'na', '-', '']:
            return None
        return cleaned
    except Exception:
        return None

def read_excel_file(excel_file_path):
    """
    Read Excel file and return cleaned data
    Returns dictionary mapping flat names to descriptions
    """
    if not os.path.exists(excel_file_path):
        logger.error(f"Excel file not found: {excel_file_path}")
        return {}
    
    try:
        # Try reading with different engines and parameters
        df = None
        
        # Try openpyxl engine first
        try:
            df = pd.read_excel(excel_file_path, engine='openpyxl')
            logger.info(f"Successfully read Excel file with openpyxl engine")
        except Exception as e:
            logger.warning(f"Failed to read with openpyxl: {e}")
            
            # Try xlrd engine as fallback
            try:
                df = pd.read_excel(excel_file_path, engine='xlrd')
                logger.info(f"Successfully read Excel file with xlrd engine")
            except Exception as e2:
                logger.error(f"Failed to read with xlrd: {e2}")
                return {}
        
        if df is None or df.empty:
            logger.error("Excel file is empty or could not be read")
            return {}
        
        logger.info(f"Excel file contains {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Column names: {list(df.columns)}")
        
        # Look for the required columns (case-insensitive)
        flat_name_col = None
        description_col = None
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if 'flat' in col_lower and 'master' in col_lower and 'name' in col_lower:
                flat_name_col = col
            elif 'long' in col_lower and 'description' in col_lower:
                description_col = col
            elif col_lower in ['description', 'long description']:
                description_col = col
        
        if flat_name_col is None:
            logger.error("Could not find 'Flat Master Name' column in Excel file")
            logger.info("Available columns: " + ", ".join(df.columns))
            return {}
        
        if description_col is None:
            logger.error("Could not find 'Long Description' column in Excel file")
            logger.info("Available columns: " + ", ".join(df.columns))
            return {}
        
        logger.info(f"Using columns: '{flat_name_col}' -> '{description_col}'")
        
        # Create mapping dictionary
        flat_descriptions = {}
        processed_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            try:
                flat_name = clean_flat_name(row[flat_name_col])
                description = clean_description(row[description_col])
                
                if flat_name is None:
                    skipped_count += 1
                    logger.debug(f"Row {index + 1}: Skipping - empty flat name")
                    continue
                
                if description is None:
                    skipped_count += 1
                    logger.debug(f"Row {index + 1}: Skipping - empty description for flat '{flat_name}'")
                    continue
                
                # Check for duplicates
                if flat_name in flat_descriptions:
                    logger.warning(f"Row {index + 1}: Duplicate flat name '{flat_name}' found. Using latest description.")
                
                flat_descriptions[flat_name] = description
                processed_count += 1
                
                # Log first few processed items for verification
                if processed_count <= 3:
                    logger.info(f"Processed: '{flat_name}' -> '{description[:100]}...'")
                
            except Exception as e:
                logger.warning(f"Row {index + 1}: Error processing row - {e}")
                skipped_count += 1
                continue
        
        logger.info(f"Successfully processed {processed_count} flat descriptions")
        logger.info(f"Skipped {skipped_count} rows due to missing data")
        
        return flat_descriptions
        
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return {}

def get_existing_flats_with_descriptions(conn):
    """
    Get existing flats from database that already have description data
    Returns dictionary mapping flat names to their IDs and current descriptions
    """
    try:
        cursor = conn.cursor()
        
        # Get flats that already have descriptions (not NULL and not empty)
        query = """
            SELECT id, name, description 
            FROM flats 
            WHERE name IS NOT NULL AND name != ''
              AND description IS NOT NULL AND description != ''
            ORDER BY name
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        existing_flats = {}
        for flat_id, name, current_desc in results:
            clean_name = clean_flat_name(name)
            if clean_name:
                existing_flats[clean_name] = {
                    'id': flat_id,
                    'current_description': current_desc
                }
        
        cursor.close()
        logger.info(f"Found {len(existing_flats)} existing flats with description data in database")
        
        return existing_flats
        
    except Exception as e:
        logger.error(f"Error fetching existing flats: {e}")
        return {}

def update_flat_descriptions(conn, flat_descriptions, existing_flats, force_update=False):
    """
    Update flat descriptions in the database
    Only updates flats that already have existing description data
    Returns statistics about the update process
    """
    stats = {
        'matched': 0,
        'updated': 0,
        'unchanged': 0,
        'not_found': 0,
        'no_existing_description': 0,
        'errors': 0
    }
    
    try:
        cursor = conn.cursor()
        
        # Prepare update query
        update_query = """
            UPDATE flats 
            SET description = %s, modified_date = %s 
            WHERE id = %s
        """
        
        current_time = datetime.now()
        
        for flat_name, new_description in flat_descriptions.items():
            try:
                # Check if flat exists in database
                if flat_name not in existing_flats:
                    stats['not_found'] += 1
                    logger.debug(f"Flat '{flat_name}' not found in database or has no existing description")
                    continue
                
                stats['matched'] += 1
                flat_info = existing_flats[flat_name]
                current_description = flat_info['current_description']
                
                # Check if description actually needs updating
                if not force_update and current_description == new_description:
                    stats['unchanged'] += 1
                    logger.debug(f"Flat '{flat_name}' description unchanged")
                    continue
                
                # Perform the update
                cursor.execute(update_query, (new_description, current_time, flat_info['id']))
                
                if cursor.rowcount > 0:
                    stats['updated'] += 1
                    logger.info(f"Updated description for flat '{flat_name}' (ID: {flat_info['id']})")
                    logger.debug(f"  Old: {current_description[:100]}...")
                    logger.debug(f"  New: {new_description[:100]}...")
                else:
                    stats['errors'] += 1
                    logger.warning(f"No rows updated for flat '{flat_name}' (ID: {flat_info['id']})")
                
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error updating flat '{flat_name}': {e}")
                conn.rollback()  # Rollback this transaction
                continue
        
        # Commit all successful updates
        conn.commit()
        cursor.close()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error in update process: {e}")
        conn.rollback()
        stats['errors'] += len(flat_descriptions)
        return stats

def preview_updates(flat_descriptions, existing_flats, limit=5):
    """Preview the updates that would be made"""
    logger.info("=" * 80)
    logger.info("PREVIEW OF DESCRIPTION UPDATES (First {} records)".format(min(limit, len(flat_descriptions))))
    logger.info("=" * 80)
    
    preview_count = 0
    for flat_name, new_description in flat_descriptions.items():
        if preview_count >= limit:
            break
            
        if flat_name in existing_flats:
            flat_info = existing_flats[flat_name]
            current_description = flat_info['current_description']
            
            logger.info(f"\nFlat Name: {flat_name}")
            logger.info(f"Current Description: {current_description[:100]}...")
            logger.info(f"New Description: {new_description[:100]}...")
            logger.info(f"Will Update: {'Yes' if current_description != new_description else 'No (Same content)'}")
            logger.info("-" * 40)
            preview_count += 1
        else:
            logger.info(f"\nFlat Name: {flat_name}")
            logger.info("Status: Not found in database or no existing description")
            logger.info("-" * 40)

def generate_report(stats, flat_descriptions, existing_flats):
    """Generate a summary report of the update process"""
    
    logger.info("=" * 60)
    logger.info("DESCRIPTION UPDATE SUMMARY REPORT")
    logger.info("=" * 60)
    
    logger.info(f"Excel file contained: {len(flat_descriptions)} flat descriptions")
    logger.info(f"Database flats with existing descriptions: {len(existing_flats)}")
    logger.info(f"Matched flats: {stats['matched']}")
    logger.info(f"Successfully updated: {stats['updated']}")
    logger.info(f"Unchanged (same description): {stats['unchanged']}")
    logger.info(f"Not found or no existing description: {stats['not_found']}")
    logger.info(f"Errors during update: {stats['errors']}")
    
    # List flats not found in database or without existing descriptions
    if stats['not_found'] > 0:
        logger.info("\nFlats from Excel not found in database or without existing descriptions:")
        for flat_name in flat_descriptions.keys():
            if flat_name not in existing_flats:
                logger.info(f"  - {flat_name}")
    
    logger.info("=" * 60)

def main():
    """Main function to run the description update"""
    if len(sys.argv) < 2:
        print("Usage: python update_flat_descriptions_from_excel.py <excel_file_path> [--force] [--preview]")
        print("Example: python update_flat_descriptions_from_excel.py flatdescription.xlsx")
        print("  --force   : Update all records even if description is the same")
        print("  --preview : Show preview of changes without updating database")
        sys.exit(1)
    
    excel_file_path = sys.argv[1]
    force_update = '--force' in sys.argv
    preview_only = '--preview' in sys.argv
    
    logger.info(f"Starting flat description update from: {excel_file_path}")
    logger.info(f"Log file: flat_description_update.log")
    logger.info(f"Force update: {force_update}")
    logger.info(f"Preview only: {preview_only}")
    
    # Verify environment variables
    required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please ensure your .env file contains all required database connection details")
        sys.exit(1)
    
    # Step 1: Read Excel file
    logger.info("Step 1: Reading Excel file...")
    flat_descriptions = read_excel_file(excel_file_path)
    
    if not flat_descriptions:
        logger.error("No valid data found in Excel file. Exiting.")
        sys.exit(1)
    
    # Step 2: Connect to database
    logger.info("Step 2: Connecting to database...")
    conn = connect_db()
    
    if conn is None:
        logger.error("Could not connect to database. Exiting.")
        sys.exit(1)
    
    try:
        # Step 3: Get existing flats with descriptions
        logger.info("Step 3: Fetching existing flats with descriptions from database...")
        existing_flats = get_existing_flats_with_descriptions(conn)
        
        if not existing_flats:
            logger.error("No flats found in database with existing descriptions. Exiting.")
            sys.exit(1)
        
        # Step 4: Preview changes
        logger.info("Step 4: Previewing changes...")
        preview_updates(flat_descriptions, existing_flats, limit=10)
        
        if preview_only:
            logger.info("Preview mode - no changes made to database.")
            sys.exit(0)
        
        # Ask for confirmation
        if len(flat_descriptions) > 5:
            response = input(f"\nProceed to update descriptions for matched flats? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                logger.info("Operation cancelled by user.")
                sys.exit(0)
        
        # Step 5: Update descriptions
        logger.info("Step 5: Updating flat descriptions...")
        stats = update_flat_descriptions(conn, flat_descriptions, existing_flats, force_update)
        
        # Step 6: Generate report
        logger.info("Step 6: Generating summary report...")
        generate_report(stats, flat_descriptions, existing_flats)
        
        if stats['updated'] > 0:
            logger.info(f"✅ Successfully updated {stats['updated']} flat descriptions!")
        else:
            logger.info("ℹ️  No descriptions were updated (all were either unchanged or had errors)")
        
    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}")
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
    
    logger.info("Description update process completed.")

if __name__ == "__main__":
    main()

