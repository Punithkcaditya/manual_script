#!/usr/bin/env python3
"""
Flats Video Sitemap Generator Script
Fetches flats with video data (videos, youtube_url) and generates video XML sitemap.
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
    """Fetch flats with video data from flats table joined with properties"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Query to fetch flats data with video information
        query = """
        SELECT f.name, f.videos, f.youtube_url, f.meta_title, f.meta_description, 
               f.slug, f.flat_type, 
               RTRIM(p.user_friendly_url, '/') || '/' || f.slug AS flat_url 
        FROM flats f 
        JOIN properties p ON f.property_id = p.id;
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

def extract_location_from_url(flat_url):
    """Extract location from flat_url (e.g., /bangalore/hennur/kots-arbre/k12b102 -> hennur)"""
    if not flat_url:
        return None
    
    # Split URL by '/' and get location (usually the 3rd segment: /bangalore/hennur/...)
    parts = [p for p in flat_url.strip().split('/') if p]
    if len(parts) >= 2:
        return parts[1]  # After 'bangalore' or first location segment
    return None

def generate_tags(name, slug, flat_type, location):
    """Generate video tags from flat data"""
    tags = []
    
    # Add common tags
    tags.extend(['apartment', 'bangalore', 'flat', 'furnished', 'rent', 'kots'])
    
    # Add location if available
    if location:
        tags.append(location.lower())
    
    # Add flat type if available (e.g., "1 BHK" -> "1-bhk")
    if flat_type:
        flat_type_tag = flat_type.lower().replace(' ', '-')
        tags.append(flat_type_tag)
    
    # Add flat slug if available
    if slug:
        tags.append(slug.lower())
    elif name:
        # Extract slug-like part from name if needed
        name_slug = name.lower().replace(' ', '-')
        tags.append(name_slug)
    
    return tags

def generate_xml_sitemap(flats_data):
    """Generate video XML sitemap for all flats with videos"""
    # Base URL for flats
    base_url = 'https://www.kots.world'
    
    # Create root element with video namespace
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:video', 'http://www.google.com/schemas/sitemap-video/1.1')
    
    # Process each flat
    for name, videos, youtube_url, meta_title, meta_description, slug, flat_type, flat_url in flats_data:
        # Skip if no video content (both videos and youtube_url are empty)
        if not videos and not youtube_url:
            logger.debug(f"Skipping flat '{name}' - no video content")
            continue
        
        # Skip if no flat_url
        if not flat_url:
            logger.debug(f"Skipping flat '{name}' - no flat_url")
            continue
        
        # Create URL element for this flat
        url_elem = ET.SubElement(urlset, 'url')
        
        # Add location - construct full URL from flat_url
        loc_elem = ET.SubElement(url_elem, 'loc')
        clean_url = flat_url.strip()
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
        
        # Add video content location - prefer videos (virtual tour), fallback to youtube_url
        content_loc = videos if videos else youtube_url
        if content_loc:
            video_content_loc_elem = ET.SubElement(video_elem, 'video:content_loc')
            video_content_loc_elem.text = content_loc.strip()
        
        # Add thumbnail location (using default logo for now)
        video_thumbnail_elem = ET.SubElement(video_elem, 'video:thumbnail_loc')
        video_thumbnail_elem.text = 'https://www.kots.world/images/logo.png'
        
        # Add video title - use meta_title or fallback to name
        video_title_elem = ET.SubElement(video_elem, 'video:title')
        video_title = meta_title if meta_title else (name if name else 'KOTS Flat')
        video_title_elem.text = video_title
        
        # Add video description - use meta_description or default
        video_description_elem = ET.SubElement(video_elem, 'video:description')
        video_description = meta_description if meta_description else 'KOTS'
        video_description_elem.text = video_description
        
        # Extract location from flat_url for tags
        location = extract_location_from_url(flat_url)
        
        # Add video tags
        tags = generate_tags(name, slug, flat_type, location)
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
        logger.info("Starting flats video sitemap generation...")
        
        # Fetch flats from database
        rows = fetch_flats()
        
        # Process flats data
        total_records = 0
        records_with_videos = 0
        
        flats_data = []
        for row in rows:
            total_records += 1
            name = row[0]
            videos = row[1]
            youtube_url = row[2]
            meta_title = row[3]
            meta_description = row[4]
            slug = row[5]
            flat_type = row[6]
            flat_url = row[7]
            
            # Only include if has video content and flat_url
            if (videos or youtube_url) and flat_url:
                records_with_videos += 1
                flats_data.append((name, videos, youtube_url, meta_title, meta_description, 
                                 slug, flat_type, flat_url))
                video_type = 'videos' if videos else 'youtube_url'
                logger.debug(f"Record {total_records} ({name}): Has {video_type}, URL: {flat_url}")
            else:
                logger.debug(f"Record {total_records} ({name}): No video content or URL")
        
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Records with videos: {records_with_videos}")
        
        if not flats_data:
            logger.warning("No flats with videos found in database. Generating empty sitemap.")
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
            
            with open('flats_video_sitemap.xml', 'w', encoding='utf-8') as f:
                f.write(empty_sitemap)
            
            logger.info("Empty sitemap saved to flats_video_sitemap.xml")
            return
        
        # Generate XML sitemap
        logger.info("Generating video XML sitemap...")
        xml_content = generate_xml_sitemap(flats_data)
        
        # Save to file
        output_file = 'flats_video_sitemap.xml'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"Flats video sitemap generated successfully: {output_file}")
        logger.info(f"Total flats with videos in sitemap: {len(flats_data)}")
        
    except Exception as e:
        logger.error(f"Error generating flats video sitemap: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

