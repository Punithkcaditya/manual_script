import requests
import json
from typing import List, Dict, Optional


def fetch_nearby_places(
    latitude: float,
    longitude: float,
    radius: int = 1500,
    place_type: str = "point_of_interest",
    api_key: str = None
) -> List[Dict]:
    """
    Fetch nearby places from Google Maps Places API
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        radius: Search radius in meters (default: 1500)
        place_type: Type of place to search for (default: point_of_interest)
        api_key: Google Maps API key
    
    Returns:
        List of places formatted for database storage
    """
    
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "type": place_type,
        "key": api_key
    }
    
    all_results = []
    
    try:
        # Initial request
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK":
            print(f"API Error: {data.get('status')} - {data.get('error_message', 'No error message')}")
            return []
        
        # Process results
        all_results.extend(format_places(data.get("results", [])))
        
        # Handle pagination (next_page_token)
        next_page_token = data.get("next_page_token")
        
        while next_page_token:
            # Google requires a short delay before using next_page_token
            import time
            time.sleep(2)
            
            response = requests.get(base_url, params={"pagetoken": next_page_token, "key": api_key})
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "OK":
                all_results.extend(format_places(data.get("results", [])))
                next_page_token = data.get("next_page_token")
            else:
                break
        
        return all_results
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return []


def format_places(results: List[Dict]) -> List[Dict]:
    """
    Format API results for database storage
    
    Args:
        results: Raw results from Google Places API
    
    Returns:
        Formatted list of places
    """
    formatted_places = []
    
    for place in results:
        formatted_place = {
            "place_id": place.get("place_id"),
            "name": place.get("name"),
            "business_status": place.get("business_status"),
            "vicinity": place.get("vicinity"),
            "types": place.get("types", []),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "location": {
                "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                "lng": place.get("geometry", {}).get("location", {}).get("lng")
            },
            "viewport": place.get("geometry", {}).get("viewport"),
            "icon": place.get("icon"),
            "icon_background_color": place.get("icon_background_color"),
            "icon_mask_base_uri": place.get("icon_mask_base_uri"),
            "permanently_closed": place.get("permanently_closed", False),
            "opening_hours": {
                "open_now": place.get("opening_hours", {}).get("open_now")
            } if place.get("opening_hours") else None,
            "photos": [
                {
                    "photo_reference": photo.get("photo_reference"),
                    "height": photo.get("height"),
                    "width": photo.get("width"),
                    "html_attributions": photo.get("html_attributions", [])
                }
                for photo in place.get("photos", [])
            ] if place.get("photos") else [],
            "plus_code": place.get("plus_code"),
            "international_phone_number": place.get("international_phone_number"),
            "reference": place.get("reference"),
            "scope": place.get("scope")
        }
        
        formatted_places.append(formatted_place)
    
    return formatted_places


def save_to_json_file(places: List[Dict], filename: str = "places.json"):
    """
    Save places to a JSON file
    
    Args:
        places: List of formatted places
        filename: Output filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(places, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(places)} places to {filename}")


def get_places_json_string(places: List[Dict]) -> str:
    """
    Convert places to JSON string for database storage
    
    Args:
        places: List of formatted places
    
    Returns:
        JSON string ready for database column
    """
    return json.dumps(places, ensure_ascii=False)


# Example usage
if __name__ == "__main__":
    # Configuration
    LATITUDE = 12.98517320460296  # Change these coordinates as needed
    LONGITUDE = 77.7055420499836 # Change these coordinates as needed
    RADIUS = 1500
    PLACE_TYPE = "point_of_interest"
    API_KEY = "AIzaSyBa2LbkV8qAxmclYs65pId0LmwhpPpPbRA"  # Replace with your actual API key
    
    # Fetch places
    print(f"Fetching places near ({LATITUDE}, {LONGITUDE}) within {RADIUS}m...")
    places = fetch_nearby_places(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        radius=RADIUS,
        place_type=PLACE_TYPE,
        api_key=API_KEY
    )
    
    print(f"Found {len(places)} places")
    
    # Save to file
    save_to_json_file(places, "nearby_places.json")
    
    # Get JSON string for database
    json_string = get_places_json_string(places)
    print(f"\nJSON string length: {len(json_string)} characters")
    print(f"\nFirst place: {json.dumps(places[0], indent=2) if places else 'No places found'}")
    
    # Example: Insert into database (pseudocode)
    """
    import psycopg2  # or your database library
    
    conn = psycopg2.connect("your_connection_string")
    cursor = conn.cursor()
    
    # Assuming you have a table with a JSONB column
    cursor.execute(
        "INSERT INTO locations (name, coordinates, places_data) VALUES (%s, %s, %s)",
        ("Bangalore Location", f"POINT({LONGITUDE} {LATITUDE})", json_string)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    """
