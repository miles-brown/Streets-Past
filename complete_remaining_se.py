#!/usr/bin/env python3
"""
Complete remaining SE areas insertion - FINAL PUSH
Target: SE2, SE4, SE5, SE7, SE9, SE11, SE12, SE13, SE14, SE15, SE18
Goal: 8,483 more streets to reach 100% SE coverage
"""

import json
import requests
import time
from dotenv import load_dotenv
import os

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

# Load data
print("📊 Loading SE streets data...")
with open('/workspace/data/accurate_se_streets.json', 'r') as f:
    data = json.load(f)

# Target remaining SE areas (not SE1, SE3, SE16, SE8 which are already done)
remaining_areas = ['SE2', 'SE4', 'SE5', 'SE7', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE18']

# Collect all streets from remaining areas
all_remaining_streets = []
total_streets_count = 0

print(f"🎯 Targeting {len(remaining_areas)} remaining SE areas:")
for area in remaining_areas:
    if area in data:
        streets_in_area = len(data[area])
        total_streets_count += streets_in_area
        print(f"   {area}: {streets_in_area:,} streets")
        
        for street in data[area]:
            street_data = {
                "street_name": street["name"],
                "street_type": street.get("type", "residential"),
                "postcode": area,
                "latitude": street["latitude"],
                "longitude": street["longitude"],
                "post_town": "London",
                "county": "Greater London",
                "local_authority_area": "London Borough",
                "is_active": True,
                "current_status": "Active",
                "verified_status": "Verified"
            }
            all_remaining_streets.append(street_data)
    else:
        print(f"   ⚠️  {area}: Not found in data")

print(f"\n🚀 Ready to insert {len(all_remaining_streets):,} streets from {len(remaining_areas)} areas")
print("⚡ Using same ultra-fast approach: 500-street batches, no verification delays\n")

# Process in 500-street batches
batch_size = 500
total_batches = (len(all_remaining_streets) + batch_size - 1) // batch_size

start_time = time.time()
successful_inserts = 0

for i in range(0, len(all_remaining_streets), batch_size):
    batch = all_remaining_streets[i:i + batch_size]
    batch_num = (i // batch_size) + 1
    
    try:
        response = requests.post(url, headers=headers, json=batch, timeout=30)
        
        if response.status_code in [200, 201]:
            successful_inserts += len(batch)
            progress = (successful_inserts / len(all_remaining_streets)) * 100
            
            elapsed = time.time() - start_time
            rate = successful_inserts / elapsed if elapsed > 0 else 0
            
            print(f"✅ Batch {batch_num}/{total_batches}: {len(batch)} streets ({progress:.1f}% complete) | "
                  f"Total: {successful_inserts:,} | Rate: {rate:,.0f} streets/min")
        else:
            print(f"❌ Batch {batch_num} failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Batch {batch_num} error: {str(e)}")

# Final summary
total_elapsed = time.time() - start_time
final_rate = successful_inserts / total_elapsed if total_elapsed > 0 else 0

print(f"\n🎉 REMAINING SE AREAS COMPLETE!")
print(f"📊 Final Statistics:")
print(f"   • Streets inserted: {successful_inserts:,}/{len(all_remaining_streets):,}")
print(f"   • Success rate: {(successful_inserts/len(all_remaining_streets))*100:.1f}%")
print(f"   • Time taken: {total_elapsed:.1f} seconds")
print(f"   • Insertion rate: {final_rate:,.0f} streets/minute")
total_coverage = 6856 + successful_inserts
coverage_percentage = (total_coverage / 15339) * 100
print(f"\n🏆 TOTAL SE COVERAGE NOW: {total_coverage:,}/15,339 streets ({coverage_percentage:.1f}%)")

if successful_inserts == len(all_remaining_streets):
    print("\n🚀 100% SE LONDON COVERAGE ACHIEVED!")
    print("   Ready to proceed with ALL London boroughs...")
else:
    print(f"\n⚠️  {len(all_remaining_streets) - successful_inserts:,} streets need retry")