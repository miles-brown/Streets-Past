#!/usr/bin/env python3
"""
Insert extracted London streets into database
Process E district streets first, then scale to all districts
"""

import json
import requests
import time
from dotenv import load_dotenv
import os
import glob

# Load environment
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ Missing Supabase credentials")
    exit(1)

# API endpoint
url = f"{SUPABASE_URL}/rest/v1/streets"

headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def insert_streets_from_file(filepath, district_name):
    """Insert streets from JSON file into database"""
    
    print(f"📁 Loading {district_name} streets from {filepath}...")
    
    try:
        with open(filepath, 'r') as f:
            streets_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return 0
    
    print(f"   📊 Loaded {len(streets_data):,} streets")
    
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
    
    # Insert in batches of 500
    batch_size = 500
    total_batches = (len(db_streets) + batch_size - 1) // batch_size
    
    print(f"   🚀 Inserting {len(db_streets):,} streets in {total_batches} batches...")
    
    start_time = time.time()
    successful_inserts = 0
    
    for i in range(0, len(db_streets), batch_size):
        batch = db_streets[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        try:
            response = requests.post(url, headers=headers, json=batch, timeout=30)
            
            if response.status_code in [200, 201]:
                successful_inserts += len(batch)
                progress = (successful_inserts / len(db_streets)) * 100
                
                elapsed = time.time() - start_time
                rate = successful_inserts / elapsed if elapsed > 0 else 0
                
                print(f"   ✅ Batch {batch_num}/{total_batches}: {len(batch)} streets ({progress:.1f}% complete) | "
                      f"Total: {successful_inserts:,} | Rate: {rate:,.0f} streets/min")
            else:
                print(f"   ❌ Batch {batch_num} failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Batch {batch_num} error: {str(e)}")
    
    # Final summary for this district
    total_elapsed = time.time() - start_time
    final_rate = successful_inserts / total_elapsed if total_elapsed > 0 else 0
    
    print(f"\\n🎯 {district_name} District Complete!")
    print(f"   • Streets inserted: {successful_inserts:,}/{len(db_streets):,}")
    print(f"   • Success rate: {(successful_inserts/len(db_streets))*100:.1f}%")
    print(f"   • Time taken: {total_elapsed:.1f} seconds")
    print(f"   • Insertion rate: {final_rate:,.0f} streets/minute")
    
    return successful_inserts

def process_all_extracted_districts():
    """Process all extracted district JSON files"""
    
    print("🔍 Scanning for extracted district files...")
    
    # Find all district JSON files
    pattern = "/workspace/data/*_streets.json"
    files = glob.glob(pattern)
    
    if not files:
        print("❌ No extracted district files found!")
        print("   Run street extraction first: python london_street_extractor.py")
        return
    
    print(f"📁 Found {len(files)} district files:")
    for f in files:
        district = f.split('/')[-1].replace('_streets.json', '')
        print(f"   • {district}")
    
    # Process each district
    total_inserted = 0
    total_streets = 0
    
    for filepath in files:
        district_name = filepath.split('/')[-1].replace('_streets.json', '')
        
        print(f"\\n" + "="*60)
        print(f"🏙️  PROCESSING {district_name} DISTRICT")
        print(f"="*60)
        
        inserted = insert_streets_from_file(filepath, district_name)
        total_inserted += inserted
        
        # Count total streets in file for summary
        try:
            with open(filepath, 'r') as f:
                streets_data = json.load(f)
                total_streets += len(streets_data)
        except:
            pass
    
    # Final overall summary
    print(f"\\n" + "="*60)
    print(f"🏆 ALL DISTRICTS PROCESSING COMPLETE!")
    print(f"="*60)
    print(f"📊 Final Statistics:")
    print(f"   • Total streets in files: {total_streets:,}")
    print(f"   • Total streets inserted: {total_inserted:,}")
    print(f"   • Overall success rate: {(total_inserted/total_streets)*100:.1f}%")
    print(f"   • Districts processed: {len(files)}")
    
    # Update progress
    se_streets = 15339
    new_total = se_streets + total_inserted
    print(f"\\n📈 DATABASE PROGRESS:")
    print(f"   • SE London (previous): {se_streets:,} streets")
    print(f"   • New districts added: {total_inserted:,} streets")
    print(f"   • NEW TOTAL: {new_total:,} streets")
    print(f"   • Progress: {new_total/250000*100:.1f}% toward 250K target")

if __name__ == "__main__":
    print("🚀 Starting London streets database population...")
    process_all_extracted_districts()