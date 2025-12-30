#!/usr/bin/env python3
"""
Featured Images Checker Script
Connects to database, fetches featured_image from flats table,
extracts savedName and checks if images exist on CDN.
"""

import psycopg2
import os
import json
import requests
import logging
from dotenv import load_dotenv
from urllib.parse import quote

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

def extract_saved_name(featured_image_json):
    """
    Extract savedName from featured_image JSON
    Handles both formats:
    - {"savedName": "filename.jpg", "originalName": "original.jpg"}
    - {"savedName": "filename.jpg"}
    """
    if not featured_image_json:
        return None
    
    try:
        # Parse JSON if it's a string
        if isinstance(featured_image_json, str):
            image_data = json.loads(featured_image_json)
        else:
            image_data = featured_image_json
        
        # Extract savedName
        saved_name = image_data.get('savedName')
        return saved_name
    
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        logger.error(f"Error parsing featured_image JSON: {e}")
        return None

def check_image_exists(saved_name):
    """
    Check if image exists on CDN
    Returns True if image exists (200 OK), False otherwise
    """
    if not saved_name:
        return False
    
    try:
        # Construct CDN URL - encode the filename to handle special characters
        encoded_filename = quote(saved_name)
        cdn_url = f"https://kots-world.b-cdn.net/renting/productImages/full/{encoded_filename}"
        
        # Make HEAD request to check if image exists (faster than GET)
        response = requests.head(cdn_url, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            logger.debug(f"Image not found: {cdn_url} (Status: {response.status_code})")
            return False
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking image {saved_name}: {e}")
        return False

def check_featured_images():
    """
    Main function to check all featured images in flats table
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Query to fetch flats with featured_image data
        query = """
            SELECT id, slug, flat_number, name, featured_image 
            FROM flats 
            WHERE featured_image IS NOT NULL 
            ORDER BY id
        """
        
        cursor.execute(query)
        flats = cursor.fetchall()
        
        logger.info(f"Found {len(flats)} flats with featured_image data")
        
        total_checked = 0
        images_found = 0
        images_missing = 0
        invalid_json = 0
        
        print("\n" + "="*80)
        print("CHECKING FEATURED IMAGES ON CDN")
        print("="*80)
        
        for flat_id, slug, flat_number, name, featured_image in flats:
            total_checked += 1
            
            # Extract savedName from featured_image JSON
            saved_name = extract_saved_name(featured_image)
            
            if not saved_name:
                invalid_json += 1
                print(f"❌ INVALID JSON - Slug: {slug}, Flat: {flat_number}, Name: {name}")
                continue
            
            # Check if image exists on CDN
            if check_image_exists(saved_name):
                images_found += 1
                logger.debug(f"✅ Image found: {saved_name}")
            else:
                images_missing += 1
                print(f"❌ IMAGE MISSING - Slug: {slug}, Flat: {flat_number}, Name: {name}, Image: {saved_name}")
            
            # Progress indicator
            if total_checked % 100 == 0:
                logger.info(f"Processed {total_checked} flats...")
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total flats checked: {total_checked}")
        print(f"Images found on CDN: {images_found}")
        print(f"Images missing from CDN: {images_missing}")
        print(f"Invalid JSON entries: {invalid_json}")
        print(f"Success rate: {(images_found/total_checked)*100:.2f}%" if total_checked > 0 else "N/A")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking featured images: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    """Main function"""
    logger.info("Starting featured images check...")
    
    # Verify environment variables
    required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please ensure your .env file contains all required database connection details")
        return False
    
    success = check_featured_images()
    
    if success:
        logger.info("Featured images check completed!")
        return True
    else:
        logger.error("Featured images check failed!")
        return False

if __name__ == "__main__":
    main()
