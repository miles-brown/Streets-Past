#!/usr/bin/env python3
"""
Minimal test import script - Only 10 records
Uses ONLY confirmed existing fields: street_name, street_type, county
"""

import json
import requests
import os
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

def test_import_10_records():
    """Test import with only first 10 records"""
    print("Starting minimal test import with 10 records...")
    
    # Load OSM data
    try:
        with open('/workspace/data/osm_sample_uk_streets.json', 'r') as f:
            osm_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
    
    # Get streets array from the JSON structure
    streets_data = osm_data.get('streets', [])
    
    # Get first 10 records and clean them
    test_records = []
    seen_names = set()
    
    for record in streets_data[:50]:  # Check first 50 to get 10 unique
        if len(test_records) >= 10:
            break
            
        street_name = clean_street_name(record.get('street_name', ''))
        street_type = clean_street_type(record.get('street_type', 'unclassified'))
        
        if street_name and street_name.lower() not in seen_names:
            seen_names.add(street_name.lower())
            
            # Only the confirmed existing fields (including required fields)
            cleaned_record = {
                'street_name': street_name,
                'street_type': street_type,
                'county': 'Greater Manchester',  # Use existing county value
                'local_authority_area': 'Manchester City Council',  # Use existing LAA value
                'post_town': 'Manchester'  # Use existing post_town value
            }
            test_records.append(cleaned_record)
    
    print(f"Prepared {len(test_records)} unique test records")
    
    # Display test records
    print("\nTest records to be inserted:")
    for i, record in enumerate(test_records, 1):
        print(f"{i}. {record['street_name']} ({record['street_type']}) - {record['county']}")
    
    # Insert test records
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    success_count = 0
    error_count = 0
    
    for i, record in enumerate(test_records, 1):
        try:
            print(f"\nInserting record {i}: {record['street_name']}")
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/streets",
                headers=headers,
                json=record,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Record {i} inserted successfully")
                success_count += 1
            else:
                print(f"❌ Record {i} failed: {response.status_code} - {response.text}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Record {i} exception: {e}")
            error_count += 1
    
    print(f"\n=== Test Results ===")
    print(f"Successful insertions: {success_count}")
    print(f"Failed insertions: {error_count}")
    print(f"Total attempted: {len(test_records)}")
    
    # Check current count
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/streets?select=count",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            # PostgREST returns count in Content-Range header
            content_range = response.headers.get('Content-Range', '')
            if content_range:
                count_info = content_range.split('/')[-1]
                print(f"Current database count: {count_info}")
            else:
                print("Could not get count from Content-Range header")
        else:
            print(f"Count check failed: {response.status_code}")
    except Exception as e:
        print(f"Count check error: {e}")

if __name__ == "__main__":
    test_import_10_records()