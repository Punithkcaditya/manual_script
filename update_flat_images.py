#!/usr/bin/env python3
"""
Flat Images Update Script
Updates flats table with images and featured_image based on CSV data.
Processes comma-separated image names and converts them to JSON format.
"""

import csv
import psycopg2
import os
import sys
import json
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        raise

def convert_images_to_json(images_string):
    """
    Convert comma-separated image names to JSON array format
    Input: "image1.jpg,image2.jpg,image3.jpg"
    Output: [{"savedName": "image1.jpg"}, {"savedName": "image2.jpg"}, {"savedName": "image3.jpg"}]
    """
    if not images_string or images_string.strip() == '':
        return None
    
    try:
        # Split by comma and clean up whitespace
        image_names = [img.strip() for img in images_string.split(',') if img.strip()]
        
        if not image_names:
            return None
        
        # Convert to JSON format
        images_json = [{"savedName": img} for img in image_names]
        return json.dumps(images_json)
    
    except Exception as e:
        logger.error(f"Error converting images to JSON: {e}")
        return None

def get_featured_image_json(images_string):
    """
    Get the first image as featured image JSON
    Input: "image1.jpg,image2.jpg,image3.jpg"
    Output: {"savedName": "image1.jpg"}
    """
    if not images_string or images_string.strip() == '':
        return None
    
    try:
        # Get first image
        first_image = images_string.split(',')[0].strip()
        
        if not first_image:
            return None
        
        # Convert to JSON format
        featured_json = {"savedName": first_image}
        return json.dumps(featured_json)
    
    except Exception as e:
        logger.error(f"Error creating featured image JSON: {e}")
        return None

def get_youtube_link_json(video_value):
    """
    Convert video value to youtube_link JSON format
    Input: "17478290946122K7_A01.mp4" or any video filename/value from CSV
    Output: [{"savedName": "17478290946122K7_A01.mp4"}]
    """
    if not video_value or video_value.strip() == '':
        return None
    
    try:
        # Clean the value
        cleaned_value = video_value.strip()
        
        if not cleaned_value:
            return None
        
        # Convert to JSON format - array with single object containing savedName
        youtube_json = [{"savedName": cleaned_value}]
        return json.dumps(youtube_json)
    
    except Exception as e:
        logger.error(f"Error creating youtube link JSON: {e}")
        return None

def process_csv_and_update_flats(csv_file_path):
    """
    Process CSV file and update flats table with images and featured_image
    """
    if not os.path.exists(csv_file_path):
        logger.error(f"CSV file not found: {csv_file_path}")
        return False
    
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
            
            # Find the slug, images, terms conditions, and videos columns
            slug_col_idx = None
            images_col_idx = None
            terms_col_idx = None
            videos_col_idx = None
            
            for i, header in enumerate(headers):
                header_clean = header.strip().lower()
                if 'slug' in header_clean:
                    slug_col_idx = i
                    logger.info(f"Found slug column at index {i}: '{header}'")
                elif 'image' in header_clean and header_clean != 'featuredimage':
                    images_col_idx = i
                    logger.info(f"Found images column at index {i}: '{header}'")
                elif 'termsconditions' in header_clean.replace(' ', '').replace('_', '') or 'terms_conditions' in header_clean or 'terms & conditions' in header_clean:
                    terms_col_idx = i
                    logger.info(f"Found terms conditions column at index {i}: '{header}'")
                elif 'video' in header_clean or 'youtube' in header_clean or 'link' in header_clean:
                    videos_col_idx = i
                    logger.info(f"Found videos column at index {i}: '{header}'")
            
            if slug_col_idx is None:
                logger.error("Could not find slug column in CSV")
                return False
            
            if images_col_idx is None:
                logger.error("Could not find images column in CSV")
                logger.info("Available headers:")
                for i, header in enumerate(headers):
                    logger.info(f"  {i}: {header}")
                return False
            
            # Terms conditions and videos columns are optional
            if terms_col_idx is None:
                logger.warning("Could not find terms conditions column in CSV - will skip terms_conditions updates")
            
            if videos_col_idx is None:
                logger.warning("Could not find videos column in CSV - will skip youtube_link updates")
            
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
                        required_cols = [slug_col_idx, images_col_idx]
                        if terms_col_idx is not None:
                            required_cols.append(terms_col_idx)
                        if videos_col_idx is not None:
                            required_cols.append(videos_col_idx)
                        
                        if len(row) <= max(required_cols):
                            logger.warning(f"Row {row_num}: Not enough columns, skipping")
                            continue
                        
                        slug = row[slug_col_idx].strip() if slug_col_idx < len(row) else ''
                        images_string = row[images_col_idx].strip() if images_col_idx < len(row) else ''
                        terms_conditions = row[terms_col_idx].strip() if terms_col_idx is not None and terms_col_idx < len(row) else None
                        if terms_conditions and terms_conditions.upper() == 'NULL':
                            terms_conditions = None
                        video_url = row[videos_col_idx].strip() if videos_col_idx is not None and videos_col_idx < len(row) else None
                        
                        if not slug:
                            logger.warning(f"Row {row_num}: Empty slug, skipping")
                            continue
                        
                        if not images_string or images_string.upper() == 'NULL':
                            logger.warning(f"Row {row_num}: Empty or NULL images for slug '{slug}', skipping")
                            continue
                        
                        # Convert images and video to JSON
                        images_json = convert_images_to_json(images_string)
                        featured_image_json = get_featured_image_json(images_string)
                        youtube_link_json = get_youtube_link_json(video_url) if video_url and video_url.upper() != 'NULL' else None
                        
                        if not images_json:
                            logger.warning(f"Row {row_num}: Could not convert images for slug '{slug}', skipping")
                            continue
                        
                        # Debug logging for first few rows
                        if rows_processed < 3:
                            logger.info(f"Row {row_num}: slug='{slug}'")
                            logger.info(f"Row {row_num}: images_string='{images_string}'")
                            logger.info(f"Row {row_num}: images_json='{images_json}'")
                            logger.info(f"Row {row_num}: featured_image_json='{featured_image_json}'")
                            if terms_conditions:
                                logger.info(f"Row {row_num}: terms_conditions='{terms_conditions[:100]}...' (truncated)")
                            if youtube_link_json:
                                logger.info(f"Row {row_num}: youtube_link_json='{youtube_link_json}'")
                        
                        # Check if flat exists with this slug
                        cursor.execute("SELECT id FROM flats WHERE slug = %s", (slug,))
                        flat_record = cursor.fetchone()
                        
                        if not flat_record:
                            logger.warning(f"Row {row_num}: No flat found with slug '{slug}'")
                            rows_not_found += 1
                            continue
                        
                        flat_id = flat_record[0]
                        
                        # Prepare update query and parameters based on available data
                        update_fields = ["images = %s::jsonb", "featured_image = %s::jsonb"]
                        update_params = [images_json, featured_image_json]
                        
                        if terms_conditions:
                            update_fields.append("terms_conditions = %s")
                            update_params.append(terms_conditions)
                        
                        if youtube_link_json:
                            update_fields.append("youtube_link = %s::jsonb")
                            update_params.append(youtube_link_json)
                        
                        update_params.append(slug)  # Add slug for WHERE clause
                        
                        update_query = f"""
                            UPDATE flats 
                            SET {', '.join(update_fields)}
                            WHERE slug = %s
                        """
                        
                        try:
                            cursor.execute(update_query, update_params)
                            
                            if cursor.rowcount > 0:
                                rows_updated += 1
                                logger.info(f"Row {row_num}: Updated flat ID {flat_id} with slug '{slug}'")
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
                        
                        # Commit every 100 rows
                        if rows_processed % 100 == 0:
                            conn.commit()
                            logger.info(f"Processed {rows_processed} rows, updated {rows_updated} flats...")
                    
                    except Exception as e:
                        logger.error(f"Error processing row {row_num}: {e}")
                        logger.error(f"Row data: {row[:5]}...")  # Show first 5 columns for debugging
                        rows_failed += 1
                        continue
            
            # Final commit
            conn.commit()
            
            logger.info(f"Processing complete!")
            logger.info(f"Total rows processed: {rows_processed}")
            logger.info(f"Flats updated: {rows_updated}")
            logger.info(f"Flats not found: {rows_not_found}")
            logger.info(f"Failed rows: {rows_failed}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to run the image update"""
    if len(sys.argv) != 2:
        print("Usage: python update_flat_images.py <csv_file_path>")
        print("Example: python update_flat_images.py flats.csv")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    
    logger.info(f"Starting flat images update from: {csv_file_path}")
    
    # Verify environment variables
    required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please ensure your .env file contains all required database connection details")
        sys.exit(1)
    
    success = process_csv_and_update_flats(csv_file_path)
    
    if success:
        logger.info("Flat images update completed successfully!")
        sys.exit(0)
    else:
        logger.error("Flat images update failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
