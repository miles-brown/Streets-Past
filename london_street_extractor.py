#!/usr/bin/env python3
"""
Extract streets for specific London area using Overpass API
Target: Individual postcode areas with lat/lng coordinates
"""

import requests
import json
import time
import csv
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def extract_streets_for_area(postcode, lat, lng, radius=2000):
    """Extract streets for a specific postcode area using Overpass API"""
    
    # Create bounding box around the center point
    lat_offset = radius / 111320  # Rough conversion to degrees
    lng_offset = radius / (111320 * abs(lat * 3.14159 / 180))  # Account for longitude convergence
    
    south = lat - lat_offset
    north = lat + lat_offset
    west = lng - lng_offset  
    east = lng + lng_offset
    
    # Overpass query to get streets in the area
    query = f"""
    [out:json][timeout:25];
    (
      way["highway"]["name"]({south},{west},{north},{east});
      relation["highway"]["name"]({south},{west},{north},{east});
    );
    out body;
    """
    
    try:
        response = requests.post(OVERPASS_URL, data={'data': query}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            streets = []
            
            for element in data.get('elements', []):
                if 'tags' in element and 'name' in element['tags']:
                    name = element['tags']['name']
                    highway_type = element['tags'].get('highway', 'residential')
                    
                    # Extract coordinates if available
                    if 'geometry' in element and element['geometry']:
                        # Use first and last points for approximate bounds
                        coords = element['geometry']
                        if len(coords) >= 2:
                            start_lat = coords[0][0]
                            start_lng = coords[0][1]
                            end_lat = coords[-1][0]
                            end_lng = coords[-1][1]
                            
                            # Calculate approximate center
                            center_lat = (start_lat + end_lat) / 2
                            center_lng = (start_lng + end_lng) / 2
                        else:
                            center_lat = lat
                            center_lng = lng
                    else:
                        center_lat = lat
                        center_lng = lng
                    
                    streets.append({
                        'name': name,
                        'type': highway_type,
                        'latitude': center_lat,
                        'longitude': center_lng,
                        'postcode': postcode
                    })
            
            return streets
        else:
            print(f"❌ Overpass API error for {postcode}: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error extracting streets for {postcode}: {e}")
        return []

def process_district(district_code, max_areas=5):
    """Process a specific district with limited areas for testing"""
    
    print(f"\\n🎯 Processing {district_code} district...")
    
    # Load postcode data
    london_areas = []
    try:
        with open('/workspace/data/uk_postcodes.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['region'] == 'Greater London':
                    postcode = row['postcode'].strip('"')
                    if postcode.startswith(district_code):
                        london_areas.append({
                            'postcode': postcode,
                            'latitude': float(row['latitude']),
                            'longitude': float(row['longitude']),
                            'town': row['town'].strip('"')
                        })
    except Exception as e:
        print(f"❌ Error loading postcodes: {e}")
        return
    
    # Process limited areas for testing
    areas_to_process = london_areas[:max_areas]
    print(f"   📍 Processing {len(areas_to_process)} areas: {[a['postcode'] for a in areas_to_process]}")
    
    all_streets = []
    
    for i, area in enumerate(areas_to_process, 1):
        print(f"   🔍 Extracting {area['postcode']} ({i}/{len(areas_to_process)}) - {area['town']}")
        
        streets = extract_streets_for_area(
            area['postcode'], 
            area['latitude'], 
            area['longitude']
        )
        
        all_streets.extend(streets)
        print(f"      Found {len(streets)} streets")
        
        # Small delay to respect API limits
        time.sleep(1)
    
    print(f"\\n📊 {district_code} District Summary:")
    print(f"   • Areas processed: {len(areas_to_process)}")
    print(f"   • Total streets found: {len(all_streets)}")
    print(f"   • Average per area: {len(all_streets)/len(areas_to_process):.0f} streets")
    
    # Save results
    if all_streets:
        filename = f"/workspace/data/{district_code}_streets.json"
        with open(filename, 'w') as f:
            json.dump(all_streets, f, indent=2)
        print(f"   💾 Saved to: {filename}")
    
    return all_streets

if __name__ == "__main__":
    # Test with E district (East London)
    print("🚀 Testing street extraction with E district (East London)")
    e_streets = process_district('E', max_areas=3)
    
    if e_streets:
        print(f"\\n✅ SUCCESS! Extracted {len(e_streets)} streets from E district")
        print("🎯 Ready to scale to all 20 London districts!")
    else:
        print("\\n❌ No streets extracted. Check Overpass API connectivity.")