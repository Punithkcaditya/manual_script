#!/usr/bin/env python3
"""
Blog Image Sitemap Generator Script
Fetches banner images and meta data from blogs table and generates XML sitemap.
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

def fetch_blogs():
    """Fetch thumbnail, banner, and meta from blogs table"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Query to fetch blogs data
        query = "select thumbnail, banner, meta from blogs;"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        logger.info(f"Fetched {len(rows)} records from blogs table")
        
        cursor.close()
        conn.close()
        
        return rows
        
    except Exception as e:
        logger.error(f"Error fetching blogs from database: {e}")
        raise

def parse_meta_json(meta_data):
    """Parse JSON meta data and extract metaTitle and metaDescription"""
    meta_title = ""
    meta_description = ""
    
    if meta_data is None:
        return meta_title, meta_description
    
    try:
        # If it's already a string, parse it
        if isinstance(meta_data, str):
            meta_dict = json.loads(meta_data)
        else:
            # If it's already a dict, use it directly
            meta_dict = meta_data
        
        # Extract metaTitle and metaDescription
        if isinstance(meta_dict, dict):
            meta_title = meta_dict.get('metaTitle', '')
            meta_description = meta_dict.get('metaDescription', '')
            
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON meta: {e}, data: {meta_data}")
    except Exception as e:
        logger.warning(f"Error parsing meta data: {e}")
    
    return meta_title, meta_description

def generate_xml_sitemap(blogs_data):
    """Generate XML sitemap for all blog banner images"""
    # Get current date for lastmod
    current_date = datetime.now().isoformat().split('T')[0]
    
    # CDN base URL for blog images
    cdn_base_url = 'https://kots-world.b-cdn.net/Final/blogs/full'
    
    # Create root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
    
    # Process each blog
    for thumbnail, banner, meta in blogs_data:
        # Skip if banner is None or empty
        if not banner:
            continue
        
        # Create URL element for this blog
        url_elem = ET.SubElement(urlset, 'url')
        
        # Add location - using generic blog URL structure
        # You can customize this URL structure based on your needs
        loc_elem = ET.SubElement(url_elem, 'loc')
        loc_elem.text = 'https://www.kots.world/blogs'
        
        # Add lastmod
        lastmod_elem = ET.SubElement(url_elem, 'lastmod')
        lastmod_elem.text = current_date
        
        # Add changefreq
        changefreq_elem = ET.SubElement(url_elem, 'changefreq')
        changefreq_elem.text = 'weekly'
        
        # Add priority
        priority_elem = ET.SubElement(url_elem, 'priority')
        priority_elem.text = '0.5'
        
        # Parse meta data
        meta_title, meta_description = parse_meta_json(meta)
        
        # Add image element
        image_elem = ET.SubElement(url_elem, 'image:image')
        
        # Add image location - append banner to CDN base URL
        image_loc_elem = ET.SubElement(image_elem, 'image:loc')
        image_loc_elem.text = f"{cdn_base_url}/{banner}"
        
        # Add image title from metaTitle
        image_title_elem = ET.SubElement(image_elem, 'image:title')
        image_title_elem.text = meta_title if meta_title else "KOTS - Premium Furnished Flats for Rent in Bangalore"
        
        # Add image caption from metaDescription
        image_caption_elem = ET.SubElement(image_elem, 'image:caption')
        image_caption_elem.text = meta_description if meta_description else "KOTS - Your trusted partner for premium rental apartments"
    
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
        logger.info("Starting blog image sitemap generation...")
        
        # Fetch blogs from database
        rows = fetch_blogs()
        
        # Process blogs data
        total_records = 0
        records_with_banners = 0
        
        blogs_data = []
        for row in rows:
            total_records += 1
            thumbnail = row[0]
            banner = row[1]
            meta = row[2]
            
            if banner:
                records_with_banners += 1
                blogs_data.append((thumbnail, banner, meta))
                logger.debug(f"Record {total_records}: Found banner: {banner}")
            else:
                logger.debug(f"Record {total_records}: No banner (null or empty)")
        
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Records with banners: {records_with_banners}")
        
        if not blogs_data:
            logger.warning("No banners found in database. Generating empty sitemap.")
            # Generate empty sitemap
            current_date = datetime.now().isoformat().split('T')[0]
            empty_sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://www.kots.world/blogs</loc>
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
            
            with open('blog_sitemap.xml', 'w', encoding='utf-8') as f:
                f.write(empty_sitemap)
            
            logger.info("Empty sitemap saved to blog_sitemap.xml")
            return
        
        # Generate XML sitemap
        logger.info("Generating XML sitemap...")
        xml_content = generate_xml_sitemap(blogs_data)
        
        # Save to file
        output_file = 'blog_sitemap.xml'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"Blog image sitemap generated successfully: {output_file}")
        logger.info(f"Total blogs in sitemap: {len(blogs_data)}")
        
    except Exception as e:
        logger.error(f"Error generating blog sitemap: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

