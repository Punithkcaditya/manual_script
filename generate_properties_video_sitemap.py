#!/usr/bin/env python3
"""
Properties Video Sitemap Generator Script
Fetches properties with video data (virtual_tour, youtube_link) and generates video XML sitemap.
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
    """Fetch properties with video data from properties table"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Query to fetch properties data with video information
        query = """
        SELECT id, name, slug, meta_title, meta_description, location_slug, 
               virtual_tour, youtube_link, user_friendly_url 
        FROM properties 
        ORDER BY id DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        logger.info(f"Fetched {len(rows)} records from properties table")
        
        cursor.close()
        conn.close()
        
        return rows
        
    except Exception as e:
        logger.error(f"Error fetching properties from database: {e}")
        raise

def generate_tags(name, slug, location_slug):
    """Generate video tags from property data"""
    tags = []
    
    # Add common tags
    tags.extend(['apartment', 'bangalore', 'flat', 'furnished', 'rent', 'kots'])
    
    # Add location if available
    if location_slug:
        tags.append(location_slug.lower())
    
    # Add property name/slug if available
    if slug:
        tags.append(slug.lower())
    elif name:
        # Extract slug-like part from name if needed
        name_slug = name.lower().replace(' ', '-')
        tags.append(name_slug)
    
    return tags

def generate_xml_sitemap(properties_data):
    """Generate video XML sitemap for all properties with videos"""
    # Base URL for properties
    base_url = 'https://www.kots.world'
    
    # Create root element with video namespace
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:video', 'http://www.google.com/schemas/sitemap-video/1.1')
    
    # Process each property
    for id, name, slug, meta_title, meta_description, location_slug, virtual_tour, youtube_link, user_friendly_url in properties_data:
        # Skip if no video content (both virtual_tour and youtube_link are empty)
        if not virtual_tour and not youtube_link:
            logger.debug(f"Skipping property '{name}' (ID: {id}) - no video content")
            continue
        
        # Skip if no user_friendly_url
        if not user_friendly_url:
            logger.debug(f"Skipping property '{name}' (ID: {id}) - no user_friendly_url")
            continue
        
        # Create URL element for this property
        url_elem = ET.SubElement(urlset, 'url')
        
        # Add location - construct full URL from user_friendly_url
        loc_elem = ET.SubElement(url_elem, 'loc')
        clean_url = user_friendly_url.strip()
        if not clean_url.startswith('/'):
            clean_url = '/' + clean_url
        loc_elem.text = f"{base_url}{clean_url}"
        
        # Add changefreq
        changefreq_elem = ET.SubElement(url_elem, 'changefreq')
        changefreq_elem.text = 'monthly'
        
        # Add priority
        priority_elem = ET.SubElement(url_elem, 'priority')
        priority_elem.text = '0.2'
        
        # Add video element
        video_elem = ET.SubElement(url_elem, 'video:video')
        
        # Add video content location - prefer virtual_tour, fallback to youtube_link
        content_loc = virtual_tour if virtual_tour else youtube_link
        if content_loc:
            video_content_loc_elem = ET.SubElement(video_elem, 'video:content_loc')
            video_content_loc_elem.text = content_loc.strip()
        
        # Add thumbnail location (using default logo for now)
        video_thumbnail_elem = ET.SubElement(video_elem, 'video:thumbnail_loc')
        video_thumbnail_elem.text = 'https://www.kots.world/images/logo.png'
        
        # Add video title - use meta_title or fallback to name
        video_title_elem = ET.SubElement(video_elem, 'video:title')
        video_title = meta_title if meta_title else (name if name else 'KOTS Property')
        video_title_elem.text = video_title
        
        # Add video description - use meta_description or default
        video_description_elem = ET.SubElement(video_elem, 'video:description')
        video_description = meta_description if meta_description else 'KOTS'
        video_description_elem.text = video_description
        
        # Add video tags
        tags = generate_tags(name, slug, location_slug)
        for tag in tags:
            if tag:  # Only add non-empty tags
                video_tag_elem = ET.SubElement(video_elem, 'video:tag')
                video_tag_elem.text = tag
        
        # Add video category
        video_category_elem = ET.SubElement(video_elem, 'video:category')
        video_category_elem.text = 'kots'
    
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
        logger.info("Starting properties video sitemap generation...")
        
        # Fetch properties from database
        rows = fetch_properties()
        
        # Process properties data
        total_records = 0
        records_with_videos = 0
        
        properties_data = []
        for row in rows:
            total_records += 1
            id = row[0]
            name = row[1]
            slug = row[2]
            meta_title = row[3]
            meta_description = row[4]
            location_slug = row[5]
            virtual_tour = row[6]
            youtube_link = row[7]
            user_friendly_url = row[8]
            
            # Only include if has video content and user_friendly_url
            if (virtual_tour or youtube_link) and user_friendly_url:
                records_with_videos += 1
                properties_data.append((id, name, slug, meta_title, meta_description, 
                                      location_slug, virtual_tour, youtube_link, user_friendly_url))
                video_type = 'virtual_tour' if virtual_tour else 'youtube_link'
                logger.debug(f"Record {total_records} ({name}): Has {video_type}, URL: {user_friendly_url}")
            else:
                logger.debug(f"Record {total_records} ({name}): No video content or URL")
        
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Records with videos: {records_with_videos}")
        
        if not properties_data:
            logger.warning("No properties with videos found in database. Generating empty sitemap.")
            # Generate empty sitemap
            current_date = datetime.now().isoformat().split('T')[0]
            empty_sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
  <url>
    <loc>https://www.kots.world/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
            
            with open('properties_video_sitemap.xml', 'w', encoding='utf-8') as f:
                f.write(empty_sitemap)
            
            logger.info("Empty sitemap saved to properties_video_sitemap.xml")
            return
        
        # Generate XML sitemap
        logger.info("Generating video XML sitemap...")
        xml_content = generate_xml_sitemap(properties_data)
        
        # Save to file
        output_file = 'properties_video_sitemap.xml'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"Properties video sitemap generated successfully: {output_file}")
        logger.info(f"Total properties with videos in sitemap: {len(properties_data)}")
        
    except Exception as e:
        logger.error(f"Error generating properties video sitemap: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

