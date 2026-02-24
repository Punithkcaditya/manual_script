"""
Standalone script to generate individual JSON files for each blog by slug
Fetches slugs from /getBlogs API, then fetches detail from /blog_detail/{slug}

Usage:
    python generate_blog_detail_by_slug.py
    
Output:
    Creates blog-detail-{slug}.json files in cdn_json_files/blogs/
"""

import json
import requests
import time
from pathlib import Path


BASE_URL = "https://kots-website-staging.quantaops.com/api"


def get_all_blog_slugs_from_api():
    """
    Fetch all blog slugs from paginated API
    Iterates through all pages to collect all slugs
    
    Returns:
        List of blog slugs
    """
    slugs = []
    page = 1
    limit = 50  # Fetch more per page to reduce API calls
    
    print("Fetching all blog slugs from API...")
    
    while True:
        try:
            url = f"{BASE_URL}/getBlogs?page={page}&limit={limit}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            blogs = data.get('blogs', [])
            
            if not blogs:
                break
            
            # Extract slugs from this page
            page_slugs = [blog['slug'] for blog in blogs if blog.get('slug')]
            slugs.extend(page_slugs)
            
            print(f"  Page {page}: Found {len(page_slugs)} slugs")
            
            # Check if there are more pages
            pagination = data.get('pagination', {})
            if not pagination.get('has_next', False):
                break
            
            page += 1
            time.sleep(0.3)  # Small delay between requests
            
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching page {page}: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"  Error parsing JSON for page {page}: {e}")
            break
    
    print(f"\nTotal slugs collected: {len(slugs)}")
    return slugs


def get_blog_detail_by_slug(slug):
    """
    Fetch blog detail by slug from API
    
    Args:
        slug: The blog slug
        
    Returns:
        Blog detail data or None if error
    """
    try:
        # Use path parameter: /api/blog_detail/{slug}
        url = f"{BASE_URL}/blog_detail/{slug}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching blog '{slug}': {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"  Error parsing JSON for '{slug}': {e}")
        return None


def generate_blog_detail_files(output_dir="cdn_json_files/blogs"):
    """
    Generate individual JSON files for each blog by slug
    
    Args:
        output_dir: Directory where JSON files will be saved
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all blog slugs from API
    slugs = get_all_blog_slugs_from_api()
    
    if not slugs:
        print("No blogs found!")
        return
    
    print(f"\nGenerating JSON files for {len(slugs)} blogs...")
    print("-" * 50)
    
    success_count = 0
    error_count = 0
    
    # Generate JSON file for each blog
    for i, slug in enumerate(slugs, 1):
        try:
            # Get blog detail from API
            blog_data = get_blog_detail_by_slug(slug)
            
            if not blog_data:
                print(f"  [{i}/{len(slugs)}] X Blog not found: {slug}")
                error_count += 1
                continue
            
            # Check if API returned error
            if blog_data.get('status') == 'error':
                print(f"  [{i}/{len(slugs)}] X API error for: {slug}")
                error_count += 1
                continue
            
            # Save to JSON file
            filename = f"blog-detail-{slug}.json"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(blog_data, f, ensure_ascii=False, indent=2)
            
            print(f"  [{i}/{len(slugs)}] OK Generated: {filename}")
            success_count += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.2)
            
        except IOError as e:
            print(f"  [{i}/{len(slugs)}] X Error saving file for '{slug}': {e}")
            error_count += 1
        except Exception as e:
            print(f"  [{i}/{len(slugs)}] X Unexpected error for '{slug}': {e}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("Generation complete!")
    print(f"  Success: {success_count} files")
    print(f"  Errors:  {error_count} files")
    print(f"  Output:  {output_path.absolute()}")
    print("=" * 50)
    
    # Show CDN upload instructions
    print("\nNext steps:")
    print(f"1. Upload all files from '{output_path.absolute()}' to your Bunny CDN")
    print("2. Upload to path: /api/blogs/")
    print("3. Files will be accessible at:")
    print("   https://kots-world.b-cdn.net/api/blogs/blog-detail-{slug}.json")


if __name__ == "__main__":
    print("=" * 60)
    print(" Blog Detail JSON Generator (by Slug)")
    print("=" * 60 + "\n")
    
    # You can customize the output directory here
    output_directory = "cdn_json_files/blogs"
    
    generate_blog_detail_files(output_directory)
