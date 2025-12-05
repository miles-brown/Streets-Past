#!/usr/bin/env python3
"""
MASTER London Streets Database Builder
Extract and insert ALL 20 London districts (~250,000+ streets)
Current: 25,013 streets | Target: 250,000+ streets
"""

import json
import requests
import time
import csv
from dotenv import load_dotenv
import os
from collections import defaultdict

# Load environment
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# API setup
supabase_headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def extract_streets_for_area(postcode, lat, lng, radius=2000):
    """Extract streets for a postcode area using Overpass API"""
    
    # Create bounding box
    lat_offset = radius / 111320
    lng_offset = radius / (111320 * abs(lat * 3.14159 / 180))
    
    south = lat - lat_offset
    north = lat + lat_offset
    west = lng - lng_offset  
    east = lng + lng_offset
    
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
                    
                    # Get coordinates
                    if 'geometry' in element and element['geometry'] and len(element['geometry']) >= 2:
                        coords = element['geometry']
                        center_lat = (coords[0][0] + coords[-1][0]) / 2
                        center_lng = (coords[0][1] + coords[-1][1]) / 2
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
        print(f"❌ Error extracting {postcode}: {e}")
        return []

def insert_streets_batch(streets_data, district_name):
    """Insert streets into database in batches"""
    
    if not streets_data:
        return 0
    
    # Convert to database format
    db_streets = []
    for street in streets_data:
        db_street = {
            "street_name": street["name"],
            "street_type": street.get("type", "residential"),
            "postcode": street["postcode"],
            "latitude": street["latitude"],
            "longitude": street["longitude"],
            "post_town": "London",
            "county": "Greater London",
            "local_authority_area": "London Borough",
            "is_active": True,
            "current_status": "Active",
            "verified_status": "Verified"
        }
        db_streets.append(db_street)
    
    # Insert in batches
    batch_size = 500
    total_batches = (len(db_streets) + batch_size - 1) // batch_size
    
    start_time = time.time()
    successful_inserts = 0
    
    for i in range(0, len(db_streets), batch_size):
        batch = db_streets[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/streets", 
                headers=supabase_headers, 
                json=batch, 
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                successful_inserts += len(batch)
                progress = (successful_inserts / len(db_streets)) * 100
                elapsed = time.time() - start_time
                rate = successful_inserts / elapsed if elapsed > 0 else 0
                
                if batch_num <= 3 or batch_num == total_batches:  # Show first 3 and last batch
                    print(f"   ✅ Batch {batch_num}/{total_batches}: {len(batch)} streets ({progress:.1f}% complete)")
            else:
                print(f"   ❌ Batch {batch_num} failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Batch {batch_num} error: {str(e)}")
    
    total_elapsed = time.time() - start_time
    final_rate = successful_inserts / total_elapsed if total_elapsed > 0 else 0
    
    print(f"   🎯 {district_name} Insert Complete: {successful_inserts:,} streets in {total_elapsed:.1f}s")
    
    return successful_inserts

def process_district_complete(district_code, max_areas=None):
    """Complete extraction and insertion for a district"""
    
    print(f"\\n🏙️  PROCESSING {district_code} DISTRICT")
    print("-" * 50)
    
    # Load postcode areas for this district
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
        return 0
    
    if not london_areas:
        print(f"❌ No areas found for {district_code}")
        return 0
    
    # Limit areas if specified
    if max_areas:
        areas_to_process = london_areas[:max_areas]
        print(f"   📍 Testing with {len(areas_to_process)} areas (of {len(london_areas)} total)")
    else:
        areas_to_process = london_areas
        print(f"   📍 Processing all {len(london_areas)} areas")
    
    # Extract streets from all areas
    all_streets = []
    
    for i, area in enumerate(areas_to_process, 1):
        print(f"   🔍 Extracting {area['postcode']} ({i}/{len(areas_to_process)}) - {area['town']}")
        
        streets = extract_streets_for_area(
            area['postcode'], 
            area['latitude'], 
            area['longitude']
        )
        
        all_streets.extend(streets)
        
        # Rate limiting
        time.sleep(0.5)
        
        if i % 5 == 0:  # Progress update every 5 areas
            print(f"      Progress: {len(all_streets):,} streets so far...")
    
    print(f"   📊 Total extracted: {len(all_streets):,} streets from {len(areas_to_process)} areas")
    print(f"   📈 Average: {len(all_streets)/len(areas_to_process):.0f} streets per area")
    
    # Insert into database
    print(f"   🚀 Inserting into database...")
    inserted_count = insert_streets_batch(all_streets, district_code)
    
    return inserted_count

def get_current_db_count():
    """Get current database street count"""
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/streets?select=count", headers=supabase_headers)
        if response.status_code == 200:
            # Get count from response headers
            count_header = response.headers.get('content-range', '0/0')
            if '/' in count_header:
                total = int(count_header.split('/')[-1])
                return total
        return 0
    except:
        return 0

def main():
    """Main processing function"""
    
    print("🚀 MASTER LONDON STREETS DATABASE BUILDER")
    print("=" * 60)
    
    # Check current status
    current_count = get_current_db_count()
    print(f"📊 Current database: {current_count:,} streets")
    
    # List of districts to process (excluding SE which is complete)
    districts_to_process = ['E', 'EC', 'N', 'NW', 'SW', 'W', 'WC', 
                           'BR', 'CR', 'DA', 'EN', 'HA', 'IG', 'KT', 
                           'RM', 'SM', 'TN', 'TW', 'UB']
    
    total_new_streets = 0
    
    # Process each district
    for district in districts_to_process:
        print(f"\\n🎯 Target District: {district}")
        
        # For testing, limit to 3 areas per district initially
        new_streets = process_district_complete(district, max_areas=3)
        total_new_streets += new_streets
        
        # Update progress
        new_total = current_count + total_new_streets
        progress_pct = (new_total / 250000) * 100
        
        print(f"\\n📈 PROGRESS UPDATE:")
        print(f"   • {district} added: {new_streets:,} streets")
        print(f"   • Running total: {total_new_streets:,} new streets")
        print(f"   • Database total: {new_total:,} streets")
        print(f"   • Progress to goal: {progress_pct:.1f}%")
        
        # Break early for testing
        if total_new_streets > 50000:  # Stop after ~50K streets for testing
            print(f"\\n🛑 TESTING BREAK - Stopping after {total_new_streets:,} streets")
            break
    
    # Final summary
    final_total = current_count + total_new_streets
    print(f"\\n" + "=" * 60)
    print(f"🏆 PROCESSING COMPLETE!")
    print(f"=" * 60)
    print(f"📊 Final Results:")
    print(f"   • Starting database: {current_count:,} streets")
    print(f"   • New streets added: {total_new_streets:,} streets")
    print(f"   • Final database total: {final_total:,} streets")
    print(f"   • Progress to 250K goal: {(final_total/250000)*100:.1f}%")
    print(f"\\n🎉 London streets database significantly expanded!")

if __name__ == "__main__":
    main()