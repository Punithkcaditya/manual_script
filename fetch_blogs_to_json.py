"""
Script to fetch blog data from API and save to JSON files.
Fetches pages 1-23 and saves each response to blogs-page-{page}.json
"""

import requests
import json
import time


def fetch_and_save_blogs(base_url: str, start_page: int = 1, end_page: int = 23, limit: int = 12):
    """
    Fetch blog data from API and save each page response to a JSON file.
    
    Args:
        base_url: The API base URL
        start_page: Starting page number (default: 1)
        end_page: Ending page number (default: 23)
        limit: Number of blogs per page (default: 12)
    """
    
    for page in range(start_page, end_page + 1):
        url = f"{base_url}?page={page}&limit={limit}"
        output_file = f"blogs-page-{page}.json"
        
        try:
            print(f"Fetching page {page}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Saved {output_file}")
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching page {page}: {e}")
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing JSON for page {page}: {e}")
        except IOError as e:
            print(f"✗ Error saving file for page {page}: {e}")
    
    print(f"\nDone! Fetched pages {start_page} to {end_page}")


if __name__ == "__main__":
    BASE_URL = "https://kots-website-staging.quantaops.com/api/getBlogs"
    
    fetch_and_save_blogs(BASE_URL, start_page=1, end_page=23, limit=12)
