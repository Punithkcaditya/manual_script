import json

# Read the nearby places data
with open('nearby_places.json', 'r', encoding='utf-8') as f:
    places = json.load(f)

# Extract just the names
place_names = [place.get("name") for place in places if place.get("name")]

# Save to a new JSON file
output = {
    "total_places": len(place_names),
    "place_names": place_names
}

with open('place_names_only.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Total places found: {len(place_names)}")
print(f"\nPlace names saved to: place_names_only.json")
print(f"\nFirst 10 places:")
for i, name in enumerate(place_names[:10], 1):
    print(f"{i}. {name}")
