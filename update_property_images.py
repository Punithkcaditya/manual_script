#!/usr/bin/env python3
"""
Script to update properties table with featured_image and youtube_link from CSV
Based on slug matching, updates:
- featured_image column with JSON data from CSV
- youtube_link column with JSON data from CSV
"""

import os
import csv
import json
import psycopg2
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv('staging.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('property_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', 5432)
        )
        logger.info("Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def process_featured_image_json(featured_image_value):
    """
    Process featured_image value from CSV
    If it's already JSON, return as is
    If it's a simple string, convert to JSON format
    
    Args:
        featured_image_value (str): Featured image value from CSV
        
    Returns:
        str: JSON string or None
    """
    if not featured_image_value or featured_image_value.strip() == '' or featured_image_value.upper() == 'NULL':
        return None
    
    try:
        cleaned_value = featured_image_value.strip()
        
        # Check if it's already JSON
        if cleaned_value.startswith('{') and cleaned_value.endswith('}'):
            # Validate it's proper JSON
            json.loads(cleaned_value)
            return cleaned_value
        else:
            # Convert simple string to JSON format
            featured_json = {"savedName": cleaned_value}
            return json.dumps(featured_json)
    except Exception as e:
        logger.error(f"Error processing featured image JSON: {e}")
        return None

def process_youtube_link_json(youtube_value):
    """
    Convert youtube link value to JSON array format for youtube_link column
    
    Args:
        youtube_value (str): YouTube link or video value from CSV
        
    Returns:
        str: JSON string in format [{"savedName": "video_value"}] or None
    """
    if not youtube_value or youtube_value.strip() == '' or youtube_value.upper() == 'NULL':
        return None
    
    try:
        cleaned_value = youtube_value.strip()
        
        # Check if it's already JSON array
        if cleaned_value.startswith('[') and cleaned_value.endswith(']'):
            # Validate it's proper JSON
            json.loads(cleaned_value)
            return cleaned_value
        else:
            # Convert to JSON array format
            youtube_json = [{"savedName": cleaned_value}]
            return json.dumps(youtube_json)
    except Exception as e:
        logger.error(f"Error creating youtube link JSON: {e}")
        return None

def process_csv_and_update_properties(csv_file_path):
    """
    Process CSV file and update properties table with featured_image and youtube_link
    """
    logger.info(f"Starting property update from: {csv_file_path}")
    
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # First, check what columns exist in the CSV
        # Try different delimiters to handle various CSV formats
        with open(csv_file_path, 'r', encoding='utf-8', errors='replace') as file:
            # Read first line to detect delimiter
            first_line = file.readline().strip()
            file.seek(0)  # Reset file pointer
            
            # Detect delimiter
            if ';' in first_line and first_line.count(';') > first_line.count(','):
                logger.info("Detected semicolon-delimited CSV")
                csv_reader = csv.reader(file, delimiter=';')
            else:
                logger.info("Using comma-delimited CSV")
                csv_reader = csv.reader(file)
            
            headers = next(csv_reader)  # Get headers
            
            # Clean headers - remove quotes and extra whitespace
            headers = [header.strip().strip('"').strip("'") for header in headers]
            
            logger.info(f"CSV Headers: {headers}")
            
            # Find the slug, featured_image, and youtube_link columns
            slug_col_idx = None
            featured_image_col_idx = None
            youtube_link_col_idx = None
            
            for i, header in enumerate(headers):
                header_clean = header.strip().lower()
                if header_clean == 'slug':  # Exact match to avoid location_slug
                    slug_col_idx = i
                    logger.info(f"Found slug column at index {i}: '{header}'")
                elif 'featured_image' in header_clean or 'featuredimage' in header_clean:
                    featured_image_col_idx = i
                    logger.info(f"Found featured_image column at index {i}: '{header}'")
                elif 'youtube_link' in header_clean or 'youtubelink' in header_clean or 'youtube' in header_clean:
                    youtube_link_col_idx = i
                    logger.info(f"Found youtube_link column at index {i}: '{header}'")
            
            # Check required columns
            if slug_col_idx is None:
                logger.error("Could not find slug column in CSV")
                logger.info("Available headers:")
                for i, header in enumerate(headers):
                    logger.info(f"  {i}: {header}")
                logger.error("Property update failed!")
                return
            
            if featured_image_col_idx is None:
                logger.warning("Could not find featured_image column in CSV - will skip featured_image updates")
            
            if youtube_link_col_idx is None:
                logger.warning("Could not find youtube_link column in CSV - will skip youtube_link updates")
            
            if featured_image_col_idx is None and youtube_link_col_idx is None:
                logger.error("No updateable columns found in CSV!")
                return
            
            # Process each row
            rows_processed = 0
            rows_updated = 0
            rows_not_found = 0
            rows_failed = 0
            
            # Re-open file for processing data rows with the same delimiter
            with open(csv_file_path, 'r', encoding='utf-8', errors='replace') as file:
                # Use the same delimiter detection logic
                first_line = file.readline().strip()
                file.seek(0)
                
                if ';' in first_line and first_line.count(';') > first_line.count(','):
                    csv_reader = csv.reader(file, delimiter=';')
                else:
                    csv_reader = csv.reader(file)
                
                # Skip header row
                next(csv_reader)
                
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because headers are row 1
                    # Clean row data - remove quotes and extra whitespace
                    row = [cell.strip().strip('"').strip("'") for cell in row]
                    try:
                        # Check minimum required columns
                        required_cols = [slug_col_idx]
                        if featured_image_col_idx is not None:
                            required_cols.append(featured_image_col_idx)
                        if youtube_link_col_idx is not None:
                            required_cols.append(youtube_link_col_idx)
                        
                        if len(row) <= max(required_cols):
                            logger.warning(f"Row {row_num}: Not enough columns, skipping")
                            continue
                        
                        slug = row[slug_col_idx].strip() if slug_col_idx < len(row) else ''
                        featured_image_value = row[featured_image_col_idx].strip() if featured_image_col_idx is not None and featured_image_col_idx < len(row) else None
                        youtube_link_value = row[youtube_link_col_idx].strip() if youtube_link_col_idx is not None and youtube_link_col_idx < len(row) else None
                        
                        if not slug:
                            logger.warning(f"Row {row_num}: Empty slug, skipping")
                            continue
                        
                        # Process the values
                        featured_image_json = process_featured_image_json(featured_image_value) if featured_image_value else None
                        youtube_link_json = process_youtube_link_json(youtube_link_value) if youtube_link_value else None
                        
                        # Skip if no data to update
                        if not featured_image_json and not youtube_link_json:
                            logger.warning(f"Row {row_num}: No data to update for slug '{slug}', skipping")
                            continue
                        
                        # Debug logging for first few rows
                        if rows_processed < 3:
                            logger.info(f"Row {row_num}: slug='{slug}'")
                            if featured_image_value:
                                logger.info(f"Row {row_num}: featured_image_value='{featured_image_value}'")
                                logger.info(f"Row {row_num}: featured_image_json='{featured_image_json}'")
                            if youtube_link_value:
                                logger.info(f"Row {row_num}: youtube_link_value='{youtube_link_value}'")
                                logger.info(f"Row {row_num}: youtube_link_json='{youtube_link_json}'")
                        
                        # Check if property exists with this slug
                        cursor.execute("SELECT id FROM properties WHERE slug = %s", (slug,))
                        property_record = cursor.fetchone()
                        
                        if not property_record:
                            logger.warning(f"Row {row_num}: No property found with slug '{slug}'")
                            rows_not_found += 1
                            continue
                        
                        property_id = property_record[0]
                        
                        # Prepare update query and parameters based on available data
                        update_fields = []
                        update_params = []
                        
                        if featured_image_json:
                            update_fields.append("featured_image = %s::jsonb")
                            update_params.append(featured_image_json)
                        
                        if youtube_link_json:
                            update_fields.append("youtube_link = %s::jsonb")
                            update_params.append(youtube_link_json)
                        
                        update_params.append(slug)  # Add slug for WHERE clause
                        
                        update_query = f"""
                            UPDATE properties 
                            SET {', '.join(update_fields)}
                            WHERE slug = %s
                        """
                        
                        try:
                            cursor.execute(update_query, update_params)
                            
                            if cursor.rowcount > 0:
                                rows_updated += 1
                                logger.info(f"Row {row_num}: Updated property ID {property_id} with slug '{slug}'")
                            else:
                                logger.warning(f"Row {row_num}: No rows updated for slug '{slug}'")
                        except Exception as db_error:
                            logger.error(f"Row {row_num}: Database error: {db_error}")
                            logger.error(f"Row {row_num}: Query: {update_query}")
                            logger.error(f"Row {row_num}: Params: {update_params}")
                            # Rollback the transaction and start fresh
                            conn.rollback()
                            raise db_error
                        
                        rows_processed += 1
                        
                        # Commit every 10 rows (smaller batches for properties)
                        if rows_processed % 10 == 0:
                            conn.commit()
                            logger.info(f"Processed {rows_processed} rows, updated {rows_updated} properties...")
                    
                    except Exception as e:
                        logger.error(f"Error processing row {row_num}: {e}")
                        logger.error(f"Row data: {row[:5]}...")  # Show first 5 columns for debugging
                        rows_failed += 1
                        continue
            
            # Final commit
            conn.commit()
            
            logger.info(f"Processing complete!")
            logger.info(f"Total rows processed: {rows_processed}")
            logger.info(f"Properties updated: {rows_updated}")
            logger.info(f"Properties not found: {rows_not_found}")
            logger.info(f"Failed rows: {rows_failed}")
            
        cursor.close()
        conn.close()
        logger.info("Property update completed successfully!")
        
    except Exception as e:
        logger.error(f"Property update failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python update_property_images.py <csv_file_path>")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' not found")
        sys.exit(1)
    
    try:
        process_csv_and_update_properties(csv_file_path)
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        sys.exit(1)
