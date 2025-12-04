#!/usr/bin/env python3
"""
Final Working OSM Street Import Script
Uses ONLY the required fields identified through testing:
- street_name
- street_type
- county (required)
- local_authority_area (required)
- post_town (required)
"""

import json
import requests
import time
from urllib.parse import quote

# Supabase credentials
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def clean_street_name(name):
    """Clean and standardize street name"""
    if not name:
        return None
    return name.strip()

def clean_street_type(stype):
    """Clean and standardize street type"""
    if not stype:
        return "unclassified"
    # Standardize common types
    type_mapping = {
        'primary': 'primary',
        'secondary': 'secondary', 
        'tertiary': 'tertiary',
        'residential': 'residential',
        'unclassified': 'unclassified',
        'trunk': 'trunk',
        'living_street': 'living_street',
        'service': 'service',
        'track': 'track',
        'path': 'path',
        'footway': 'footway',
        'cycleway': 'cycleway'
    }
    return type_mapping.get(stype.lower(), 'unclassified')

def import_all_osm_streets():
    """Import all OSM street data with proper field mapping"""
    print("=== Final Working OSM Street Import ===")
    print("Using confirmed required fields: street_name, street_type, county, local_authority_area, post_town")
    
    # Load OSM data
    try:
        with open('/workspace/data/osm_sample_uk_streets.json', 'r') as f:
            osm_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
    
    # Get streets array
    streets_data = osm_data.get('streets', [])
    print(f"Total OSM streets loaded: {len(streets_data)}")
    
    # Get existing street names to avoid duplicates
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/streets?select=street_name",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            existing_streets = {record['street_name'].lower() for record in response.json()}
            print(f"Found {len(existing_streets)} existing street names")
        else:
            print(f"Could not fetch existing streets: {response.status_code}")
            existing_streets = set()
    except Exception as e:
        print(f"Error fetching existing streets: {e}")
        existing_streets = set()
    
    # Clean and deduplicate street data
    cleaned_streets = []
    seen_names = set()
    
    for record in streets_data:
        street_name = clean_street_name(record.get('street_name', ''))
        street_type = clean_street_type(record.get('street_type', 'unclassified'))
        
        if street_name and street_name.lower() not in seen_names and street_name.lower() not in existing_streets:
            seen_names.add(street_name.lower())
            
            # Use ONLY the confirmed required fields
            cleaned_record = {
                'street_name': street_name,
                'street_type': street_type,
                'county': 'Greater Manchester',
                'local_authority_area': 'Manchester City Council',
                'post_town': 'Manchester'
            }
            cleaned_streets.append(cleaned_record)
    
    print(f"Prepared {len(cleaned_streets)} unique streets for import ({len(streets_data) - len(cleaned_streets)} skipped as duplicates)")
    
    # Import in batches
    batch_size = 100
    total_imported = 0
    total_failed = 0
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    for i in range(0, len(cleaned_streets), batch_size):
        batch = cleaned_streets[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(cleaned_streets) + batch_size - 1) // batch_size
        
        print(f"\nProcessing batch {batch_num}/{total_batches} ({len(batch)} records)")
        
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/streets",
                headers=headers,
                json=batch,
                timeout=120
            )
            
            if response.status_code in [200, 201]:
                total_imported += len(batch)
                print(f"✅ Batch {batch_num} imported successfully ({total_imported}/{len(cleaned_streets)} total)")
            else:
                # Try individual inserts if batch fails
                print(f"❌ Batch {batch_num} failed, trying individual inserts")
                for record in batch:
                    try:
                        single_response = requests.post(
                            f"{SUPABASE_URL}/rest/v1/streets",
                            headers=headers,
                            json=record,
                            timeout=30
                        )
                        if single_response.status_code in [200, 201]:
                            total_imported += 1
                        else:
                            total_failed += 1
                            if total_failed <= 5:  # Only show first 5 errors
                                print(f"   ❌ {record['street_name']}: {single_response.status_code}")
                    except Exception as e:
                        total_failed += 1
                        if total_failed <= 5:
                            print(f"   ❌ {record['street_name']}: {e}")
        
        except Exception as e:
            print(f"❌ Batch {batch_num} exception: {e}")
            total_failed += len(batch)
        
        # Small delay to be respectful to the API
        if i + batch_size < len(cleaned_streets):
            time.sleep(0.1)
    
    print(f"\n=== IMPORT COMPLETE ===")
    print(f"Total imported: {total_imported}")
    print(f"Total failed: {total_failed}")
    print(f"Total attempted: {len(cleaned_streets)}")
    
    # Verify final count
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/streets?select=street_name",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            current_count = len(response.json())
            print(f"Current database count: {current_count} streets")
        else:
            print(f"Count verification failed: {response.status_code}")
    except Exception as e:
        print(f"Count verification error: {e}")

if __name__ == "__main__":
    import_all_osm_streets()
