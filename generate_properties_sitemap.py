#!/usr/bin/env python3
"""
Properties Image Sitemap Generator Script
Fetches featured_image, image, meta_title, and meta_description from properties table 
and generates XML sitemap for all property images.
"""

import psycopg2
import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom

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

def fetch_properties():
    """Fetch featured_image, image, meta_title, meta_description from properties table"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Query to fetch properties data
        query = "SELECT featured_image, image, meta_title, meta_description FROM public.properties ORDER BY id DESC;"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        logger.info(f"Fetched {len(rows)} records from properties table")
        
        cursor.close()
        conn.close()
        
        return rows
        
    except Exception as e:
        logger.error(f"Error fetching properties from database: {e}")
        raise

def parse_featured_image_json(featured_image_data):
    """Parse JSON featured_image data and extract savedName"""
    saved_name = ""
    
    if featured_image_data is None:
        return saved_name
    
    try:
        # If it's already a string, parse it
        if isinstance(featured_image_data, str):
            featured_dict = json.loads(featured_image_data)
        else:
            # If it's already a dict, use it directly
            featured_dict = featured_image_data
        
        # Extract savedName
        if isinstance(featured_dict, dict) and 'savedName' in featured_dict:
            saved_name = featured_dict['savedName']
            
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON featured_image: {e}, data: {featured_image_data}")
    except Exception as e:
        logger.warning(f"Error parsing featured_image data: {e}")
    
    return saved_name

def parse_image_array_json(image_data):
    """Parse JSON image array data and extract all savedName values"""
    saved_names = []
    
    if image_data is None:
        return saved_names
    
    try:
        # If it's already a string, parse it
        if isinstance(image_data, str):
            image_list = json.loads(image_data)
        else:
            # If it's already a list, use it directly
            image_list = image_data
        
        # Handle list of image objects
        if isinstance(image_list, list):
            for img in image_list:
                if isinstance(img, dict) and 'savedName' in img:
                    saved_names.append(img['savedName'])
        # Handle single image object (fallback)
        elif isinstance(image_list, dict) and 'savedName' in image_list:
            saved_names.append(image_list['savedName'])
            
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON image array: {e}, data: {image_data}")
    except Exception as e:
        logger.warning(f"Error parsing image array data: {e}")
    
    return saved_names

def generate_xml_sitemap(properties_data):
    """Generate XML sitemap for all property images"""
    # Get current date for lastmod
    current_date = datetime.now().isoformat().split('T')[0]
    
    # CDN base URLs for property images
    thumb_base_url = 'https://kots-world.b-cdn.net/Final/categoryImages/thumb'
    full_base_url = 'https://kots-world.b-cdn.net/Final/categoryImages/full'
    
    # Create root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
    
    # Process each property
    for featured_image, image, meta_title, meta_description in properties_data:
        # Parse featured_image and image data
        featured_saved_name = parse_featured_image_json(featured_image)
        image_saved_names = parse_image_array_json(image)
        
        # Skip if no images at all
        if not featured_saved_name and not image_saved_names:
            continue
        
        # Create URL element for this property
        url_elem = ET.SubElement(urlset, 'url')
        
        # Add location - using generic properties URL structure
        # You can customize this URL structure based on your needs
        loc_elem = ET.SubElement(url_elem, 'loc')
        loc_elem.text = 'https://www.kots.world/properties'
        
        # Add lastmod
        lastmod_elem = ET.SubElement(url_elem, 'lastmod')
        lastmod_elem.text = current_date
        
        # Add changefreq
        changefreq_elem = ET.SubElement(url_elem, 'changefreq')
        changefreq_elem.text = 'weekly'
        
        # Add priority
        priority_elem = ET.SubElement(url_elem, 'priority')
        priority_elem.text = '0.5'
        
        # Prepare title and caption with fallbacks
        image_title = meta_title if meta_title else "KOTS - Premium Furnished Flats for Rent in Bangalore"
        image_caption = meta_description if meta_description else "KOTS - Your trusted partner for premium rental apartments"
        
        # Add featured_image as image element (thumb)
        if featured_saved_name:
            image_elem = ET.SubElement(url_elem, 'image:image')
            
            # Add image location - featured_image goes to thumb
            image_loc_elem = ET.SubElement(image_elem, 'image:loc')
            image_loc_elem.text = f"{thumb_base_url}/{featured_saved_name}"
            
            # Add image title
            image_title_elem = ET.SubElement(image_elem, 'image:title')
            image_title_elem.text = image_title
            
            # Add image caption
            image_caption_elem = ET.SubElement(image_elem, 'image:caption')
            image_caption_elem.text = image_caption
        
        # Add all images from image array as image elements (full)
        for saved_name in image_saved_names:
            if not saved_name:  # Skip empty image names
                continue
                
            image_elem = ET.SubElement(url_elem, 'image:image')
            
            # Add image location - images go to full
            image_loc_elem = ET.SubElement(image_elem, 'image:loc')
            image_loc_elem.text = f"{full_base_url}/{saved_name}"
            
            # Add image title
            image_title_elem = ET.SubElement(image_elem, 'image:title')
            image_title_elem.text = image_title
            
            # Add image caption
            image_caption_elem = ET.SubElement(image_elem, 'image:caption')
            image_caption_elem.text = image_caption
    
    # Convert to string with proper formatting
    rough_string = ET.tostring(urlset, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    
    # Add XML declaration
    xml_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + reparsed.toprettyxml(indent="  ")
    
    # Remove extra blank lines
    lines = [line for line in xml_string.split('\n') if line.strip()]
    return '\n'.join(lines)

def main():
    """Main function"""
    try:
        logger.info("Starting properties image sitemap generation...")
        
        # Fetch properties from database
        rows = fetch_properties()
        
        # Process properties data
        total_records = 0
        records_with_images = 0
        total_images = 0
        
        properties_data = []
        for row in rows:
            total_records += 1
            featured_image = row[0]
            image = row[1]
            meta_title = row[2]
            meta_description = row[3]
            
            # Parse to check if we have any images
            featured_saved_name = parse_featured_image_json(featured_image)
            image_saved_names = parse_image_array_json(image)
            
            if featured_saved_name or image_saved_names:
                records_with_images += 1
                image_count = (1 if featured_saved_name else 0) + len(image_saved_names)
                total_images += image_count
                properties_data.append((featured_image, image, meta_title, meta_description))
                logger.debug(f"Record {total_records}: Found {image_count} images (featured: {bool(featured_saved_name)}, array: {len(image_saved_names)})")
            else:
                logger.debug(f"Record {total_records}: No images found")
        
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Records with images: {records_with_images}")
        logger.info(f"Total images found: {total_images}")
        
        if not properties_data:
            logger.warning("No images found in database. Generating empty sitemap.")
            # Generate empty sitemap
            current_date = datetime.now().isoformat().split('T')[0]
            empty_sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://www.kots.world/properties</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
    <image:image>
      <image:loc>https://www.kots.world/images/logo.png</image:loc>
      <image:title>KOTS - Premium Furnished Flats for Rent in Bangalore</image:title>
      <image:caption>KOTS - Your trusted partner for premium rental apartments</image:caption>
    </image:image>
  </url>
</urlset>'''
            
            with open('properties_sitemap.xml', 'w', encoding='utf-8') as f:
                f.write(empty_sitemap)
            
            logger.info("Empty sitemap saved to properties_sitemap.xml")
            return
        
        # Generate XML sitemap
        logger.info("Generating XML sitemap...")
        xml_content = generate_xml_sitemap(properties_data)
        
        # Save to file
        output_file = 'properties_sitemap.xml'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"Properties image sitemap generated successfully: {output_file}")
        logger.info(f"Total properties in sitemap: {len(properties_data)}")
        logger.info(f"Total images in sitemap: {total_images}")
        
    except Exception as e:
        logger.error(f"Error generating properties sitemap: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

