#!/usr/bin/env python3
"""
Properties URL Sitemap Generator Script
Fetches name, slug, meta_title, meta_description, and user_friendly_url from properties table 
and generates standard XML sitemap for all property URLs.
"""

import psycopg2
import os
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
    """Fetch name, slug, meta_title, meta_description, user_friendly_url from properties table"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Query to fetch properties data
        query = "SELECT name, slug, meta_title, meta_description, user_friendly_url FROM public.properties ORDER BY id DESC;"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        logger.info(f"Fetched {len(rows)} records from properties table")
        
        cursor.close()
        conn.close()
        
        return rows
        
    except Exception as e:
        logger.error(f"Error fetching properties from database: {e}")
        raise

def generate_xml_sitemap(properties_data):
    """Generate standard XML sitemap for all property URLs"""
    # Get current date for lastmod
    current_date = datetime.now().isoformat().split('T')[0]
    
    # Base URL for properties
    base_url = 'https://www.kots.world'
    
    # Create root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # Process each property
    for name, slug, meta_title, meta_description, user_friendly_url in properties_data:
        # Skip if user_friendly_url is None or empty
        if not user_friendly_url:
            logger.debug(f"Skipping property '{name}' - no user_friendly_url")
            continue
        
        # Create URL element for this property
        url_elem = ET.SubElement(urlset, 'url')
        
        # Add location - construct full URL from user_friendly_url
        loc_elem = ET.SubElement(url_elem, 'loc')
        # Ensure user_friendly_url starts with / and doesn't have trailing slash issues
        clean_url = user_friendly_url.strip()
        if not clean_url.startswith('/'):
            clean_url = '/' + clean_url
        loc_elem.text = f"{base_url}{clean_url}"
        
        # Add lastmod
        lastmod_elem = ET.SubElement(url_elem, 'lastmod')
        lastmod_elem.text = current_date
        
        # Add changefreq
        changefreq_elem = ET.SubElement(url_elem, 'changefreq')
        changefreq_elem.text = 'weekly'
        
        # Add priority
        priority_elem = ET.SubElement(url_elem, 'priority')
        priority_elem.text = '0.8'  # Higher priority for property pages
    
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
        logger.info("Starting properties URL sitemap generation...")
        
        # Fetch properties from database
        rows = fetch_properties()
        
        # Process properties data
        total_records = 0
        records_with_urls = 0
        
        properties_data = []
        for row in rows:
            total_records += 1
            name = row[0]
            slug = row[1]
            meta_title = row[2]
            meta_description = row[3]
            user_friendly_url = row[4]
            
            if user_friendly_url:
                records_with_urls += 1
                properties_data.append((name, slug, meta_title, meta_description, user_friendly_url))
                logger.debug(f"Record {total_records} ({name}): URL: {user_friendly_url}")
            else:
                logger.debug(f"Record {total_records} ({name}): No user_friendly_url")
        
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Records with URLs: {records_with_urls}")
        
        if not properties_data:
            logger.warning("No properties with URLs found in database. Generating empty sitemap.")
            # Generate empty sitemap
            current_date = datetime.now().isoformat().split('T')[0]
            empty_sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.kots.world/</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
            
            with open('properties_url_sitemap.xml', 'w', encoding='utf-8') as f:
                f.write(empty_sitemap)
            
            logger.info("Empty sitemap saved to properties_url_sitemap.xml")
            return
        
        # Generate XML sitemap
        logger.info("Generating XML sitemap...")
        xml_content = generate_xml_sitemap(properties_data)
        
        # Save to file
        output_file = 'properties_url_sitemap.xml'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"Properties URL sitemap generated successfully: {output_file}")
        logger.info(f"Total properties in sitemap: {len(properties_data)}")
        
    except Exception as e:
        logger.error(f"Error generating properties URL sitemap: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

