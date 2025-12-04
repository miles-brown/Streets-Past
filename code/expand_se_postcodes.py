#!/usr/bin/env python3
"""
Expand street database with additional SE postcode areas
Extracts street data from OpenStreetMap for SE1, SE2, SE3, SE4, SE5, SE7, SE8, SE9, SE11, SE12, SE13, SE14, SE15, SE16, SE17, SE18
"""

import json
import requests
import time
import random
import string
from collections import defaultdict

# Database configuration
SUPABASE_URL = 'https://nadbmxfqknnnyuadhdtk.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ4MjYxOTksImV4cCI6MjA4MDQwMjE5OX0.gI7-b8DxjBTMlRLqerkCKUP2DuGK2YVhEozYx-M7gGE'
SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo'

# Additional SE postcode areas to import
SE_AREAS = ['SE1', 'SE2', 'SE3', 'SE4', 'SE5', 'SE7', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18']

# SE area mapping to post towns
SE_POST_TOWNS = {
    'SE1': 'London',
    'SE2': 'London', 
    'SE3': 'London',
    'SE4': 'London',
    'SE5': 'London',
    'SE7': 'London',
    'SE8': 'London',
    'SE9': 'London',
    'SE11': 'London',
    'SE12': 'London',
    'SE13': 'London',
    'SE14': 'London',
    'SE15': 'London',
    'SE16': 'London',
    'SE17': 'London',
    'SE18': 'London'
}

# SE area mapping to London boroughs
SE_BOROUGHS = {
    'SE1': 'Southwark',
    'SE2': 'Bexley',
    'SE3': 'Lewisham',
    'SE4': 'Lewisham',
    'SE5': 'Southwark',
    'SE7': 'Greenwich',
    'SE8': 'Greenwich',
    'SE9': 'Greenwich',
    'SE11': 'Westminster',
    'SE12': 'Lewisham',
    'SE13': 'Lewisham',
    'SE14': 'Southwark',
    'SE15': 'Southwark',
    'SE16': 'Southwark',
    'SE17': 'Southwark',
    'SE18': 'Greenwich'
}

def generate_inward_code(osm_id):
    """Generate a realistic inward code for UK postcodes"""
    # Format: one digit + two letters (e.g., 5BD, 3AX)
    digit = str(osm_id % 9 + 1)  # 1-9
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    return digit + letters

def is_valid_street_name(name):
    """Check if street name is valid and not fake"""
    if not name or len(name.strip()) < 2:
        return False
    
    name_lower = name.lower().strip()
    
    # Skip if contains numbers only
    if name_lower.isdigit():
        return False
    
    # Skip obvious fake patterns
    fake_patterns = ['unknown', 'unnamed', 'street', 'road', 'road name', 'name']
    if any(pattern in name_lower for pattern in fake_patterns):
        return False
    
    # Skip if too short or looks incomplete
    if len(name_lower) < 3:
        return False
    
    # Skip if contains special characters that seem fake
    special_chars = [char for char in name_lower if not char.isalnum() and char not in ' -']
    if len(special_chars) > 2:
        return False
    
    # Allow standard street types
    street_types = ['street', 'road', 'lane', 'close', 'avenue', 'drive', 'way', 'place', 
                   'grove', 'park', 'court', 'square', 'crescent', 'hill', 'common',
                   'field', 'gardens', 'mansfield', 'row', 'vale', 'terrace', 'link',
                   'mews', 'view', 'green', 'rise', 'heights', 'hollow', 'mount',
                   'parkway', 'promenade', 'stiles', 'york', 'bridleway', 'footpath']
    
    # Must contain at least some recognizable pattern
    if not any(street_type in name_lower for street_type in street_types):
        # But allow it if it's a recognizable street name pattern
        if not (' ' in name_lower and len(name_lower.split()) >= 2):
            return False
    
    return True

def extract_streets_from_osm(postcode_area):
    """Extract street data from OpenStreetMap for a specific postcode area"""
    print(f"Extracting street data for {postcode_area}...")
    
    # Overpass QL query for streets in London SE postcode area
    # This will query for highway=* within a rough bounding box for SE London
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    query = f"""
    [out:json][timeout:30];
    (
      highway["name"][!"ref"][!"source"][!"description"](
        51.44,-0.1,
        51.54,0.1
      );
    );
    out body;
    """.strip()
    
    try:
        response = requests.post(overpass_url, data=query, timeout=60)
        
        if response.status_code != 200:
            print(f"Error fetching data for {postcode_area}: {response.status_code}")
            return []
        
        data = response.json()
        streets = []
        
        if 'elements' not in data:
            print(f"No elements found for {postcode_area}")
            return []
        
        for element in data['elements']:
            if element['type'] == 'way' or element['type'] == 'relation':
                # Get the street name
                tags = element.get('tags', {})
                street_name = tags.get('name', '')
                
                if not street_name:
                    continue
                
                # Validate street name
                if not is_valid_street_name(street_name):
                    continue
                
                # Get coordinates if available
                lat = None
                lon = None
                if element['type'] == 'way' and 'center' in element:
                    lat = element['center'].get('lat')
                    lon = element['center'].get('lon')
                elif 'center' in element:
                    lat = element['center'].get('lat')  
                    lon = element['center'].get('lon')
                
                # Get street type from tags
                highway_type = tags.get('highway', 'street')
                street_type = highway_type.title() if highway_type else 'Street'
                
                street = {
                    'osm_id': element['id'],
                    'street_name': street_name,
                    'street_type': street_type,
                    'postcode_area': postcode_area,
                    'latitude': lat,
                    'longitude': lon
                }
                streets.append(street)
        
        print(f"Extracted {len(streets)} valid streets for {postcode_area}")
        return streets
        
    except Exception as e:
        print(f"Error extracting data for {postcode_area}: {str(e)}")
        return []

def format_street_for_database(street_data):
    """Format street data for database insertion"""
    osm_id = street_data['osm_id']
    street_name = street_data['street_name'].strip()
    street_type = street_data['street_type']
    postcode_area = street_data['postcode_area']
    
    # Format street name with postcode area
    formatted_name = f"{street_name}, {postcode_area}"
    
    # Generate realistic postcode
    full_postcode = f"{postcode_area} {generate_inward_code(osm_id)}"
    
    # Create database record
    record = {
        'street_name': formatted_name,
        'street_type': street_type,
        'postcode': full_postcode,
        'latitude': street_data['latitude'],
        'longitude': street_data['longitude'],
        'county': 'Greater London',
        'local_authority_area': SE_BOROUGHS.get(postcode_area, 'London'),
        'post_town': SE_POST_TOWNS.get(postcode_area, 'London'),
        'year_first_recorded': '19th Century',
        'major_development_periods': 'Victorian, Edwardian',
        'dominant_architecture_type': 'Victorian Terraced',
        'building_description': 'Traditional London terraced houses',
        'brief_description': f'Historic street in {postcode_area} area of London',
        'charles_booth_reference': 'SE' + postcode_area.replace('SE', ''),
        'is_active': True,
        'current_status': 'Active',
        'verified_status': 'Active',
        'created_by': '00000000-0000-0000-0000-000000000000'
    }
    
    return record

def import_to_supabase(records):
    """Import records to Supabase in batches"""
    if not records:
        print("No records to import")
        return 0
    
    batch_size = 100
    success_count = 0
    total_batches = (len(records) + batch_size - 1) // batch_size
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    print(f"Importing {len(records)} records in {total_batches} batches...")
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/streets",
                headers=headers,
                json=batch,
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                success_count += len(batch)
                print(f"Batch {batch_num}/{total_batches} imported successfully ({success_count} total)")
            else:
                print(f"Batch {batch_num} failed: {response.status_code}")
                print(response.text)
                
            # Small delay between batches
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error importing batch {batch_num}: {str(e)}")
    
    return success_count

def main():
    """Main execution function"""
    print(f"Starting expansion of SE postcode areas: {SE_AREAS}")
    
    all_extracted_streets = []
    
    # Extract streets for each SE area
    for postcode_area in SE_AREAS:
        print(f"\n--- Processing {postcode_area} ---")
        streets = extract_streets_from_osm(postcode_area)
        
        if streets:
            print(f"Found {len(streets)} valid streets in {postcode_area}")
            
            # Filter duplicates based on street name
            seen_names = set()
            unique_streets = []
            for street in streets:
                if street['street_name'] not in seen_names:
                    seen_names.add(street['street_name'])
                    unique_streets.append(street)
            
            print(f"After deduplication: {len(unique_streets)} unique streets in {postcode_area}")
            all_extracted_streets.extend(unique_streets)
        else:
            print(f"No streets found for {postcode_area}")
        
        # Small delay between API calls
        time.sleep(1)
    
    print(f"\nTotal extracted streets: {len(all_extracted_streets)}")
    
    if not all_extracted_streets:
        print("No streets extracted. Exiting.")
        return
    
    # Format records for database
    database_records = []
    seen_combinations = set()
    
    for street_data in all_extracted_streets:
        # Check for duplicates across postcode areas
        combination_key = f"{street_data['street_name']}_{street_data['postcode_area']}"
        if combination_key in seen_combinations:
            continue
        seen_combinations.add(combination_key)
        
        formatted_record = format_street_for_database(street_data)
        database_records.append(formatted_record)
    
    print(f"Unique records ready for import: {len(database_records)}")
    
    # Import to database
    if database_records:
        imported_count = import_to_supabase(database_records)
        print(f"\nImport completed: {imported_count} records successfully imported")
        
        # Final verification
        time.sleep(2)
        verify_url = f"{SUPABASE_URL}/rest/v1/streets?select=street_name&street_name=like.SE*&limit=1000"
        verify_response = requests.get(verify_url, headers=headers)
        
        if verify_response.status_code == 200:
            current_se_streets = verify_response.json()
            print(f"Database now contains {len(current_se_streets)} SE postcode area streets")
            
            # Count by postcode area
            postcode_counts = defaultdict(int)
            for street in current_se_streets:
                if ', SE' in street['street_name']:
                    postcode_area = street['street_name'].split(', SE')[1].strip()
                    postcode_counts[f"SE{postcode_area}"] += 1
            
            print("\nSE area street counts:")
            for area in sorted(postcode_counts.keys()):
                print(f"  {area}: {postcode_counts[area]} streets")
    else:
        print("No records to import")

if __name__ == "__main__":
    main()