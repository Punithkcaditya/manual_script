#!/usr/bin/env python3
"""
All Images Checker Script
Connects to database, fetches images from flats table,
extracts all savedName values and checks if images exist on CDN.
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

def extract_saved_names(images_json):
    """
    Extract all savedName values from images JSON array
    Input: [{"savedName": "img1.jpg"}, {"savedName": "img2.jpg"}]
    Output: ["img1.jpg", "img2.jpg"]
    """
    if not images_json:
        return []
    
    try:
        # Parse JSON if it's a string
        if isinstance(images_json, str):
            images_data = json.loads(images_json)
        else:
            images_data = images_json
        
        # Handle if it's not a list
        if not isinstance(images_data, list):
            return []
        
        # Extract all savedName values
        saved_names = []
        for image_obj in images_data:
            if isinstance(image_obj, dict) and 'savedName' in image_obj:
                saved_names.append(image_obj['savedName'])
        
        return saved_names
    
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        logger.error(f"Error parsing images JSON: {e}")
        return []

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

def check_all_images():
    """
    Main function to check all images in flats table
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Query to fetch flats with images data
        query = """
            SELECT id, slug, flat_number, name, images 
            FROM flats 
            WHERE images IS NOT NULL 
            ORDER BY id
        """
        
        cursor.execute(query)
        flats = cursor.fetchall()
        
        logger.info(f"Found {len(flats)} flats with images data")
        
        total_flats_checked = 0
        total_images_checked = 0
        total_images_found = 0
        total_images_missing = 0
        flats_with_missing_images = 0
        invalid_json_flats = 0
        
        print("\n" + "="*100)
        print("CHECKING ALL IMAGES ON CDN")
        print("="*100)
        
        for flat_id, slug, flat_number, name, images in flats:
            total_flats_checked += 1
            
            # Extract all savedName values from images JSON array
            saved_names = extract_saved_names(images)
            
            if not saved_names:
                invalid_json_flats += 1
                print(f"❌ INVALID JSON - Slug: {slug}, Flat: {flat_number}, Name: {name}")
                continue
            
            flat_has_missing_images = False
            flat_images_found = 0
            flat_images_missing = 0
            missing_images_list = []
            
            # Check each image in this flat
            for saved_name in saved_names:
                total_images_checked += 1
                
                if check_image_exists(saved_name):
                    total_images_found += 1
                    flat_images_found += 1
                    logger.debug(f"✅ Image found: {saved_name}")
                else:
                    total_images_missing += 1
                    flat_images_missing += 1
                    flat_has_missing_images = True
                    missing_images_list.append(saved_name)
            
            # Report flats with missing images
            if flat_has_missing_images:
                flats_with_missing_images += 1
                print(f"❌ MISSING IMAGES - Slug: {slug}, Flat: {flat_number}, Name: {name}")
                print(f"   📊 Images: {flat_images_found} found, {flat_images_missing} missing")
                print(f"   📋 Missing files: {', '.join(missing_images_list[:3])}{'...' if len(missing_images_list) > 3 else ''}")
                print()
            else:
                logger.debug(f"✅ All images found for flat: {slug} ({len(saved_names)} images)")
            
            # Progress indicator
            if total_flats_checked % 50 == 0:
                logger.info(f"Processed {total_flats_checked} flats, checked {total_images_checked} images...")
        
        # Summary
        print("\n" + "="*100)
        print("SUMMARY")
        print("="*100)
        print(f"Total flats checked: {total_flats_checked}")
        print(f"Total images checked: {total_images_checked}")
        print(f"Images found on CDN: {total_images_found}")
        print(f"Images missing from CDN: {total_images_missing}")
        print(f"Flats with missing images: {flats_with_missing_images}")
        print(f"Flats with invalid JSON: {invalid_json_flats}")
        print(f"Image success rate: {(total_images_found/total_images_checked)*100:.2f}%" if total_images_checked > 0 else "N/A")
        print(f"Flats success rate: {((total_flats_checked - flats_with_missing_images - invalid_json_flats)/total_flats_checked)*100:.2f}%" if total_flats_checked > 0 else "N/A")
        
        # Additional statistics
        if total_flats_checked > 0:
            avg_images_per_flat = total_images_checked / total_flats_checked
            print(f"Average images per flat: {avg_images_per_flat:.1f}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking all images: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    """Main function"""
    logger.info("Starting all images check...")
    
    # Verify environment variables
    required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please ensure your .env file contains all required database connection details")
        return False
    
    success = check_all_images()
    
    if success:
        logger.info("All images check completed!")
        return True
    else:
        logger.error("All images check failed!")
        return False

if __name__ == "__main__":
    main()
