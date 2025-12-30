#!/usr/bin/env python3
"""
Image Sitemap Generator Script
Fetches images from flats table and generates XML sitemap for all images.
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

def fetch_images_from_flats():
    """Fetch images column from flats table"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Query as requested: select images from flats
        query = "select name, images from flats where property_id=1142;"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        logger.info(f"Fetched {len(rows)} records from flats table")
        
        cursor.close()
        conn.close()
        
        return rows
        
    except Exception as e:
        logger.error(f"Error fetching images from database: {e}")
        raise

def parse_images_json(images_data):
    """Parse JSON images data and extract savedName values"""
    image_names = []
    
    if images_data is None:
        return image_names
    
    try:
        # If it's already a string, parse it
        if isinstance(images_data, str):
            images_list = json.loads(images_data)
        else:
            # If it's already a list/dict, use it directly
            images_list = images_data
        
        # Handle list of image objects
        if isinstance(images_list, list):
            for img in images_list:
                if isinstance(img, dict) and 'savedName' in img:
                    image_names.append(img['savedName'])
        # Handle single image object
        elif isinstance(images_list, dict) and 'savedName' in images_list:
            image_names.append(images_list['savedName'])
            
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON: {e}, data: {images_data}")
    except Exception as e:
        logger.warning(f"Error parsing images data: {e}")
    
    return image_names

def generate_xml_sitemap(flats_with_images):
    """Generate XML sitemap for all images grouped by flat"""
    # Get current date for lastmod (equivalent to: new Date().toISOString().split('T')[0])
    current_date = datetime.now().isoformat().split('T')[0]
    
    # CDN base URL for images
    cdn_base_url = 'https://kots-world.b-cdn.net/Final'
    
    # Create root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
    
    # Group images by flat - create one URL entry per flat with all its images
    for flat_name, image_names in flats_with_images.items():
        if not image_names:  # Skip flats with no images
            continue
        
        # Create URL element for this flat
        url_elem = ET.SubElement(urlset, 'url')
        
        # Add location - using generic URL structure since we only have images column
        # You can customize this URL structure based on your needs
        loc_elem = ET.SubElement(url_elem, 'loc')
        # Using flat identifier in URL, adjust as needed for your URL structure
        loc_elem.text = f'https://www.kots.world/bangalore/hsr/kots-bilva'
        
        # Add lastmod
        lastmod_elem = ET.SubElement(url_elem, 'lastmod')
        lastmod_elem.text = current_date
        
        # Add changefreq
        changefreq_elem = ET.SubElement(url_elem, 'changefreq')
        changefreq_elem.text = 'weekly'
        
        # Add priority
        priority_elem = ET.SubElement(url_elem, 'priority')
        priority_elem.text = '0.5'
        
        # Add all images for this flat
        for image_name in image_names:
            if not image_name:  # Skip empty image names
                continue
                
            # Add image element
            image_elem = ET.SubElement(url_elem, 'image:image')
            
            # Add image location
            image_loc_elem = ET.SubElement(image_elem, 'image:loc')
            image_loc_elem.text = f"{cdn_base_url}/productImages/Finall/{image_name}"
            
            # Add image title
            image_title_elem = ET.SubElement(image_elem, 'image:title')
            image_title_elem.text = f"{flat_name}: Fully furnished 1BHK Flat for rent in HSR Layout | Kots Bilva"
            
            # Add image caption
            image_caption_elem = ET.SubElement(image_elem, 'image:caption')
            image_caption_elem.text = f"Book Now: Kots Bilva {flat_name} is a furnished 1 BHK rental flat in HSR Layout at Kots Bilva. Book now and enjoy premium living with high-speed internet and world-class amenities."
    
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
        logger.info("Starting image sitemap generation...")
        
        # Fetch images from database
        rows = fetch_images_from_flats()
        
        # Parse all images grouped by flat
        flats_with_images = {}
        total_records = 0
        records_with_images = 0
        total_images = 0
        
        for row in rows:
            total_records += 1
            flat_name = row[0]  # name column
            images_data = row[1]  # images column
            
            if images_data is None:
                logger.debug(f"Record {total_records}: No images data (null)")
                continue
            
            image_names = parse_images_json(images_data)
            
            if image_names:
                records_with_images += 1
                total_images += len(image_names)
                # Store flat name with images - use name as key, or fallback to index if name is None
                key = flat_name if flat_name else f"flat_{total_records}"
                flats_with_images[key] = image_names
                logger.debug(f"Record {total_records} ({key}): Found {len(image_names)} images")
        
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Records with images: {records_with_images}")
        logger.info(f"Total images found: {total_images}")
        logger.info(f"Flats with images: {len(flats_with_images)}")
        
        if not flats_with_images:
            logger.warning("No images found in database. Generating empty sitemap.")
            # Generate empty sitemap
            current_date = datetime.now().isoformat().split('T')[0]
            empty_sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://www.kots.world/</loc>
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
            
            with open('image_sitemap.xml', 'w', encoding='utf-8') as f:
                f.write(empty_sitemap)
            
            logger.info("Empty sitemap saved to image_sitemap.xml")
            return
        
        # Generate XML sitemap
        logger.info("Generating XML sitemap...")
        xml_content = generate_xml_sitemap(flats_with_images)
        
        # Save to file
        output_file = 'image_sitemap.xml'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"Image sitemap generated successfully: {output_file}")
        logger.info(f"Total flats in sitemap: {len(flats_with_images)}")
        logger.info(f"Total images in sitemap: {total_images}")
        
    except Exception as e:
        logger.error(f"Error generating image sitemap: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

