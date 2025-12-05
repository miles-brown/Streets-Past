#!/usr/bin/env python3
"""
Database Schema Checker and Postal Code Corrector
Checks the actual database schema and corrects postal codes for existing streets.
"""

import json
import os
from datetime import datetime
import requests
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def check_database_schema():
    """Check the actual database schema to understand the structure."""
    print("=== DATABASE SCHEMA ANALYSIS ===")
    
    # Test basic connection and get schema info
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Try to get basic table info using raw SQL
        print("Testing basic database connection...")
        
        # First, let's see what tables exist
        response = supabase.table('streets').select("*").limit(1).execute()
        print(f"✓ Successfully connected to streets table")
        print(f"Sample record structure: {response.data[0] if response.data else 'No data found'}")
        
        # Check if we can get column information via information_schema
        try:
            schema_response = supabase.rpc('get_table_info', {'table_name': 'streets'}).execute()
            if schema_response.data:
                print(f"Table schema info: {schema_response.data}")
        except Exception as e:
            print(f"Could not get schema via RPC: {e}")
            
        # Try to understand the current data structure
        count_response = supabase.table('streets').select("*", count="exact").limit(0).execute()
        print(f"Total records in streets table: {count_response.count}")
        
        # Get a sample of actual data to understand structure
        sample_response = supabase.table('streets').select("*").limit(5).execute()
        if sample_response.data:
            print("\nSample records:")
            for i, record in enumerate(sample_response.data):
                print(f"Record {i+1}: {record}")
        
        return supabase
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def load_accurate_street_data():
    """Load the accurate SE streets data."""
    print("\n=== LOADING ACCURATE STREET DATA ===")
    
    try:
        with open('/workspace/data/accurate_se_streets.json', 'r') as f:
            accurate_data = json.load(f)
        
        total_streets = sum(len(streets) for streets in accurate_data.values())
        print(f"✓ Loaded accurate data: {len(accurate_data)} postcode areas, {total_streets} total streets")
        
        # Show structure
        print(f"Postcode areas: {list(accurate_data.keys())}")
        
        return accurate_data
        
    except Exception as e:
        print(f"❌ Failed to load accurate data: {e}")
        return None

def match_and_correct_postcodes(supabase, accurate_data):
    """Match existing streets with accurate data and correct postcodes."""
    print("\n=== CORRECTING POSTAL CODES ===")
    
    if not supabase:
        print("❌ No database connection available")
        return False
    
    corrected_count = 0
    matched_count = 0
    total_checks = 0
    
    try:
        # Get all existing streets from database
        print("Fetching existing streets from database...")
        all_streets = []
        offset = 0
        batch_size = 1000
        
        while True:
            response = supabase.table('streets').select("*").range(offset, offset + batch_size - 1).execute()
            if not response.data:
                break
            all_streets.extend(response.data)
            print(f"Fetched {len(all_streets)} streets so far...")
            offset += batch_size
        
        print(f"✓ Loaded {len(all_streets)} existing streets from database")
        
        # Build lookup dictionary from accurate data for faster matching
        print("Building lookup dictionary from accurate data...")
        accurate_lookup = {}
        
        for postcode, streets in accurate_data.items():
            for street in streets:
                key = f"{street['name'].lower().strip()}|{postcode}"
                accurate_lookup[key] = {
                    'postcode': postcode,
                    'name': street['name'],
                    'latitude': street['latitude'],
                    'longitude': street['longitude'],
                    'type': street['type']
                }
        
        print(f"✓ Built lookup with {len(accurate_lookup)} accurate street entries")
        
        # Process each existing street
        print("Matching and correcting postal codes...")
        
        for existing_street in all_streets:
            total_checks += 1
            if total_checks % 1000 == 0:
                print(f"Processed {total_checks}/{len(all_streets)} streets...")
            
            street_name = existing_street.get('name', '').lower().strip()
            current_postcode = existing_street.get('postcode', '')
            
            if not street_name:
                continue
            
            # Try to match by name and postcode
            lookup_key = f"{street_name}|{current_postcode}"
            
            if lookup_key in accurate_lookup:
                matched_count += 1
                correct_postcode = accurate_lookup[lookup_key]['postcode']
                
                # If the postcode is already correct, skip
                if current_postcode == correct_postcode:
                    continue
                
                # Update the street with correct postcode
                try:
                    update_response = supabase.table('streets').update({
                        'postal_code': correct_postcode,
                        'updated_at': datetime.now().isoformat()
                    }).eq('id', existing_street['id']).execute()
                    
                    corrected_count += 1
                    print(f"✓ Corrected {street_name}: {current_postcode} -> {correct_postcode}")
                    
                except Exception as e:
                    print(f"❌ Failed to update {street_name}: {e}")
                    continue
            
            # If no direct match, try name-only matching with nearby coordinates
            else:
                # Look for this street name in any postcode area
                name_matches = []
                for postcode, streets in accurate_data.items():
                    for street in streets:
                        if street['name'].lower().strip() == street_name:
                            name_matches.append({
                                'postcode': postcode,
                                'latitude': street['latitude'],
                                'longitude': street['longitude']
                            })
                
                if name_matches:
                    # We found the street name but with different postcode
                    # Check if we can determine correct postcode based on coordinates
                    existing_lat = existing_street.get('latitude')
                    existing_lng = existing_street.get('longitude')
                    
                    if existing_lat and existing_lng:
                        # Find the closest match by coordinates
                        closest_match = None
                        min_distance = float('inf')
                        
                        for match in name_matches:
                            # Simple distance calculation (not geometrically accurate but good enough)
                            distance = ((match['latitude'] - existing_lat) ** 2 + (match['longitude'] - existing_lng) ** 2) ** 0.5
                            if distance < min_distance:
                                min_distance = distance
                                closest_match = match
                        
                        if closest_match and min_distance < 0.01:  # Within reasonable distance
                            correct_postcode = closest_match['postcode']
                            
                            if current_postcode != correct_postcode:
                                try:
                                    update_response = supabase.table('streets').update({
                                        'postal_code': correct_postcode,
                                        'updated_at': datetime.now().isoformat()
                                    }).eq('id', existing_street['id']).execute()
                                    
                                    corrected_count += 1
                                    print(f"✓ Corrected {street_name}: {current_postcode} -> {correct_postcode} (coordinate match)")
                                    
                                except Exception as e:
                                    print(f"❌ Failed to update {street_name}: {e}")
                                    continue
        
        print(f"\n=== CORRECTION SUMMARY ===")
        print(f"Total streets processed: {total_checks}")
        print(f"Streets matched with accurate data: {matched_count}")
        print(f"Postal codes corrected: {corrected_count}")
        print(f"Success rate: {(corrected_count/total_checks*100):.2f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during correction process: {e}")
        return False

def main():
    """Main function to check schema and correct postcodes."""
    print("Starting Database Schema Check and Postal Code Correction")
    print("=" * 60)
    
    # Step 1: Check database schema
    supabase = check_database_schema()
    
    if not supabase:
        print("❌ Cannot proceed without database connection")
        return
    
    # Step 2: Load accurate data
    accurate_data = load_accurate_street_data()
    
    if not accurate_data:
        print("❌ Cannot proceed without accurate data")
        return
    
    # Step 3: Correct postal codes
    success = match_and_correct_postcodes(supabase, accurate_data)
    
    if success:
        print("\n✅ Postal code correction completed successfully!")
    else:
        print("\n❌ Postal code correction failed!")

if __name__ == "__main__":
    main()