#!/usr/bin/env python3
"""
Flats URL Sitemap Generator Script
Fetches name, slug, flat_type, and flat_url from flats table (joined with properties)
and generates standard XML sitemap for all flat URLs.
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

def fetch_flats():
    """Fetch name, slug, flat_type, and flat_url from flats table joined with properties"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Query to fetch flats data with property URL
        query = """
        SELECT
            f.name,
            f.slug,
            f.flat_type,
            RTRIM(p.user_friendly_url, '/') || '/' || f.slug AS flat_url
        FROM flats f
        JOIN properties p
            ON f.property_id = p.id;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        logger.info(f"Fetched {len(rows)} records from flats table")
        
        cursor.close()
        conn.close()
        
        return rows
        
    except Exception as e:
        logger.error(f"Error fetching flats from database: {e}")
        raise

def generate_xml_sitemap(flats_data):
    """Generate standard XML sitemap for all flat URLs"""
    # Get current date for lastmod
    current_date = datetime.now().isoformat().split('T')[0]
    
    # Base URL for flats
    base_url = 'https://www.kots.world'
    
    # Create root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # Process each flat
    for name, slug, flat_type, flat_url in flats_data:
        # Skip if flat_url is None or empty
        if not flat_url:
            logger.debug(f"Skipping flat '{name}' - no flat_url")
            continue
        
        # Create URL element for this flat
        url_elem = ET.SubElement(urlset, 'url')
        
        # Add location - construct full URL from flat_url
        loc_elem = ET.SubElement(url_elem, 'loc')
        # Ensure flat_url starts with / and doesn't have trailing slash issues
        clean_url = flat_url.strip()
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
        priority_elem.text = '0.7'  # Slightly lower than properties but still important
    
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
        logger.info("Starting flats URL sitemap generation...")
        
        # Fetch flats from database
        rows = fetch_flats()
        
        # Process flats data
        total_records = 0
        records_with_urls = 0
        
        flats_data = []
        for row in rows:
            total_records += 1
            name = row[0]
            slug = row[1]
            flat_type = row[2]
            flat_url = row[3]
            
            if flat_url:
                records_with_urls += 1
                flats_data.append((name, slug, flat_type, flat_url))
                logger.debug(f"Record {total_records} ({name} - {flat_type}): URL: {flat_url}")
            else:
                logger.debug(f"Record {total_records} ({name}): No flat_url")
        
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Records with URLs: {records_with_urls}")
        
        if not flats_data:
            logger.warning("No flats with URLs found in database. Generating empty sitemap.")
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
            
            with open('flats_url_sitemap.xml', 'w', encoding='utf-8') as f:
                f.write(empty_sitemap)
            
            logger.info("Empty sitemap saved to flats_url_sitemap.xml")
            return
        
        # Generate XML sitemap
        logger.info("Generating XML sitemap...")
        xml_content = generate_xml_sitemap(flats_data)
        
        # Save to file
        output_file = 'flats_url_sitemap.xml'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"Flats URL sitemap generated successfully: {output_file}")
        logger.info(f"Total flats in sitemap: {len(flats_data)}")
        
    except Exception as e:
        logger.error(f"Error generating flats URL sitemap: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

