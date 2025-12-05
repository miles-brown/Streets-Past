#!/usr/bin/env python3
"""
Accurate SE London Street Extraction
Uses proper geographical boundaries to extract only legitimate SE London streets
"""

import json
import requests
import time
from collections import defaultdict

# SE London geographical boundaries (approximate)
SE_LONDON_BOUNDARIES = {
    'SE1': {'lat_min': 51.485, 'lat_max': 51.505, 'lon_min': -0.115, 'lon_max': -0.085},  # Bankside, Southwark
    'SE2': {'lat_min': 51.455, 'lat_max': 51.475, 'lon_min': 0.145, 'lon_max': 0.175},   # Abbey Wood
    'SE3': {'lat_min': 51.465, 'lat_max': 51.495, 'lon_min': 0.010, 'lon_max': 0.050},  # Blackheath, Greenwich
    'SE4': {'lat_min': 51.445, 'lat_max': 51.475, 'lon_min': -0.045, 'lon_max': -0.015}, # Brockley, Telegraph Hill
    'SE5': {'lat_min': 51.465, 'lat_max': 51.485, 'lon_min': -0.105, 'lon_max': -0.075}, # Camberwell
    'SE7': {'lat_min': 51.475, 'lat_max': 51.505, 'lon_min': 0.000, 'lon_max': 0.020},   # Charlton
    'SE8': {'lat_min': 51.475, 'lat_max': 51.505, 'lon_min': -0.025, 'lon_max': 0.005},  # Deptford
    'SE9': {'lat_min': 51.435, 'lat_max': 51.465, 'lon_min': 0.055, 'lon_max': 0.085},   # Eltham
    'SE11': {'lat_min': 51.485, 'lat_max': 51.505, 'lon_min': -0.125, 'lon_max': -0.095}, # Lambeth
    'SE12': {'lat_min': 51.435, 'lat_max': 51.465, 'lon_min': 0.015, 'lon_max': 0.045},   # Lee, Grove Park
    'SE13': {'lat_min': 51.435, 'lat_max': 51.465, 'lon_min': -0.015, 'lon_max': 0.015},  # Lewisham
    'SE14': {'lat_min': 51.465, 'lat_max': 51.495, 'lon_min': -0.065, 'lon_max': -0.035}, # New Cross
    'SE15': {'lat_min': 51.465, 'lat_max': 51.495, 'lon_min': -0.085, 'lon_max': -0.055}, # Peckham
    'SE16': {'lat_min': 51.495, 'lat_max': 51.515, 'lon_min': -0.055, 'lon_max': -0.025}, # Rotherhithe, Bermondsey
    'SE17': {'lat_min': 51.475, 'lat_max': 51.495, 'lon_min': -0.105, 'lon_max': -0.075}, # Elephant & Castle
    'SE18': {'lat_min': 51.455, 'lat_max': 51.485, 'lon_min': 0.035, 'lon_max': 0.065}    # Woolwich
}

# Streets that should NOT appear in SE London (geographical mismatches)
EXCLUDED_STREETS = [
    'Clapham', 'Wimbledon', 'Putney', 'Chelsea', 'Kensington', 'Notting Hill',
    'Richmond', 'Twickenham', 'Kingston', 'Camden', 'Hampstead', 'Highgate',
    'Islington', 'Hackney', 'Westminster', 'Mayfair', 'Covent Garden'
]

def is_valid_se_street(street_name, lat, lon):
    """Check if street is valid for SE London based on name and location"""
    name_lower = street_name.lower()
    
    # Exclude streets from other London areas
    for excluded in EXCLUDED_STREETS:
        if excluded.lower() in name_lower:
            return False
    
    # Must have reasonable coordinates for London
    if not (51.4 <= lat <= 51.6 and -0.3 <= lon <= 0.2):
        return False
    
    # Skip obviously fake entries
    if any(pattern in name_lower for pattern in ['unnamed', 'unknown', 'null', 'tbd']):
        return False
    
    return True

def assign_se_area_geographically(lat, lon):
    """Assign SE area based on geographical coordinates"""
    for area, bounds in SE_LONDON_BOUNDARIES.items():
        if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
            bounds['lon_min'] <= lon <= bounds['lon_max']):
            return area
    return None

def extract_accurate_se_streets():
    """Extract streets with proper geographical validation"""
    print("=== EXTRACTING ACCURATE SE LONDON STREETS ===")
    
    # Overpass API query for SE London area
    bbox = "51.4,-0.3,51.6,0.2"  # SE London bounding box
    query = f"""
    [out:json][timeout:180];
    (
      way["highway"]["name"]({bbox});
      relation["route"]["name"]({bbox});
    );
    out center;
    """
    
    response = requests.post(
        'https://overpass-api.de/api/interpreter',
        data={'data': query},
        timeout=200
    )
    
    if response.status_code != 200:
        print(f"Overpass API error: {response.status_code}")
        return {}
    
    data = response.json()
    streets_by_area = defaultdict(list)
    total_processed = 0
    valid_count = 0
    
    print("Processing OpenStreetMap data...")
    
    for element in data.get('elements', []):
        if element['type'] == 'way' and 'tags' in element:
            total_processed += 1
            
            if total_processed % 1000 == 0:
                print(f"  Processed: {total_processed}, Valid: {valid_count}")
            
            street_name = element['tags'].get('name', '').strip()
            if not street_name:
                continue
            
            # Get coordinates from center or geometry
            if 'center' in element:
                lat, lon = element['center']['lat'], element['center']['lon']
            elif 'geometry' in element and element['geometry']:
                # Calculate center from geometry
                lats = [node['lat'] for node in element['geometry']]
                lons = [node['lon'] for node in element['geometry']]
                lat = sum(lats) / len(lats)
                lon = sum(lons) / len(lons)
            else:
                continue
            
            # Validate street
            if not is_valid_se_street(street_name, lat, lon):
                continue
            
            # Assign to SE area based on location
            se_area = assign_se_area_geographically(lat, lon)
            if not se_area:
                continue
            
            # Determine street type
            highway_type = element['tags'].get('highway', 'street')
            street_type = {
                'primary': 'primary',
                'secondary': 'secondary',
                'tertiary': 'tertiary',
                'residential': 'residential',
                'unclassified': 'unclassified',
                'trunk': 'trunk',
                'service': 'service',
                'track': 'track',
                'footway': 'footway',
                'cycleway': 'cycleway'
            }.get(highway_type, 'residential')
            
            streets_by_area[se_area].append({
                'name': street_name,
                'type': street_type,
                'latitude': lat,
                'longitude': lon
            })
            
            valid_count += 1
    
    print(f"\nExtraction complete:")
    print(f"  Total processed: {total_processed}")
    print(f"  Valid SE London streets: {valid_count}")
    
    # Print distribution
    print("\nStreets by SE area:")
    for area in sorted(streets_by_area.keys()):
        print(f"  {area}: {len(streets_by_area[area])} streets")
    
    return streets_by_area

def main():
    """Main execution"""
    streets_by_area = extract_accurate_se_streets()
    
    if not streets_by_area:
        print("No valid streets extracted")
        return
    
    # Save accurate data
    output_file = '/workspace/data/accurate_se_streets.json'
    with open(output_file, 'w') as f:
        json.dump(dict(streets_by_area), f, indent=2)
    
    print(f"\n✓ Saved accurate street data to {output_file}")
    
    # Summary
    total_streets = sum(len(streets) for streets in streets_by_area.values())
    print(f"✓ Total accurate SE London streets: {total_streets}")

if __name__ == "__main__":
    main()
