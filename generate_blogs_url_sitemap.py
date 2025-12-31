#!/usr/bin/env python3
"""
Blogs URL Sitemap Generator Script
Fetches slug from blogs table and generates standard XML sitemap for all blog URLs.
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

def fetch_blogs():
    """Fetch slug from blogs table"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Query to fetch blogs data
        query = "select slug from blogs;"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        logger.info(f"Fetched {len(rows)} records from blogs table")
        
        cursor.close()
        conn.close()
        
        return rows
        
    except Exception as e:
        logger.error(f"Error fetching blogs from database: {e}")
        raise

def generate_xml_sitemap(blogs_data):
    """Generate standard XML sitemap for all blog URLs"""
    # Get current date for lastmod
    current_date = datetime.now().isoformat().split('T')[0]
    
    # Base URL for blogs
    base_url = 'https://www.kots.world'
    
    # Create root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # Process each blog
    for (slug,) in blogs_data:
        # Skip if slug is None or empty
        if not slug:
            logger.debug(f"Skipping blog - no slug")
            continue
        
        # Create URL element for this blog
        url_elem = ET.SubElement(urlset, 'url')
        
        # Add location - construct full URL from slug
        loc_elem = ET.SubElement(url_elem, 'loc')
        # Construct blog URL: /blogs/{slug}
        clean_slug = slug.strip()
        blog_url = f"/blogs/{clean_slug}"
        loc_elem.text = f"{base_url}{blog_url}"
        
        # Add lastmod
        lastmod_elem = ET.SubElement(url_elem, 'lastmod')
        lastmod_elem.text = current_date
        
        # Add changefreq
        changefreq_elem = ET.SubElement(url_elem, 'changefreq')
        changefreq_elem.text = 'weekly'
        
        # Add priority
        priority_elem = ET.SubElement(url_elem, 'priority')
        priority_elem.text = '0.6'  # Standard priority for blog pages
    
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
        logger.info("Starting blogs URL sitemap generation...")
        
        # Fetch blogs from database
        rows = fetch_blogs()
        
        # Process blogs data
        total_records = 0
        records_with_slugs = 0
        
        blogs_data = []
        for row in rows:
            total_records += 1
            slug = row[0]
            
            if slug:
                records_with_slugs += 1
                blogs_data.append((slug,))
                logger.debug(f"Record {total_records}: Slug: {slug}")
            else:
                logger.debug(f"Record {total_records}: No slug")
        
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Records with slugs: {records_with_slugs}")
        
        if not blogs_data:
            logger.warning("No blogs with slugs found in database. Generating empty sitemap.")
            # Generate empty sitemap
            current_date = datetime.now().isoformat().split('T')[0]
            empty_sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.kots.world/blogs</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
            
            with open('blogs_url_sitemap.xml', 'w', encoding='utf-8') as f:
                f.write(empty_sitemap)
            
            logger.info("Empty sitemap saved to blogs_url_sitemap.xml")
            return
        
        # Generate XML sitemap
        logger.info("Generating XML sitemap...")
        xml_content = generate_xml_sitemap(blogs_data)
        
        # Save to file
        output_file = 'blogs_url_sitemap.xml'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"Blogs URL sitemap generated successfully: {output_file}")
        logger.info(f"Total blogs in sitemap: {len(blogs_data)}")
        
    except Exception as e:
        logger.error(f"Error generating blogs URL sitemap: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

