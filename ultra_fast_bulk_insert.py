#!/usr/bin/env python3
"""
ULTRA-FAST BULK INSERT - Get all 15,339 SE London streets online by Sunday
Inserts all missing streets from accurate_se_streets.json in batches
"""

import requests
import json
import os
from datetime import datetime

# Supabase config
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

def load_street_data():
    """Load and process the comprehensive street data"""
    print("📁 Loading accurate_se_streets.json...")
    with open('/workspace/data/accurate_se_streets.json', 'r') as f:
        data = json.load(f)
    
    all_streets = []
    for postcode, streets in data.items():
        for street in streets:
            street_record = {
                'street_name': street['name'],
                'street_type': street.get('type', 'residential'),
                'postcode': postcode,
                'post_town': 'London',
                'latitude': street['latitude'],
                'longitude': street['longitude'],
                'county': 'Greater London',
                'local_authority_area': 'London Borough',
                'country': 'England',
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            all_streets.append(street_record)
    
    print(f"✅ Loaded {len(all_streets)} street records")
    return all_streets

def bulk_insert_streets(streets_batch, batch_num, total_batches):
    """Insert a batch of streets using Supabase bulk API"""
    print(f"🚀 Inserting batch {batch_num}/{total_batches} ({len(streets_batch)} streets)...")
    
    try:
        # Supabase bulk insert
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/streets",
            headers=headers,
            json=streets_batch,
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Batch {batch_num} inserted successfully")
            return len(streets_batch)
        else:
            print(f"❌ Batch {batch_num} failed: {response.status_code}")
            print(f"Error: {response.text}")
            return 0
            
    except Exception as e:
        print(f"❌ Batch {batch_num} error: {str(e)}")
        return 0

def main():
    start_time = datetime.now()
    print("🔥 ULTRA-FAST BULK INSERT - SPEED MODE")
    print(f"⏰ Start time: {start_time}")
    print("=" * 60)
    
    # Load all street data
    all_streets = load_street_data()
    
    # Calculate batch size for optimal performance (1000 records per batch)
    batch_size = 1000
    total_batches = (len(all_streets) + batch_size - 1) // batch_size
    
    print(f"📊 Total streets to insert: {len(all_streets)}")
    print(f"📊 Batch size: {batch_size}")
    print(f"📊 Total batches: {total_batches}")
    print("=" * 60)
    
    # Process all batches
    total_inserted = 0
    failed_batches = []
    
    for batch_num in range(1, total_batches + 1):
        start_idx = (batch_num - 1) * batch_size
        end_idx = min(start_idx + batch_size, len(all_streets))
        batch = all_streets[start_idx:end_idx]
        
        inserted = bulk_insert_streets(batch, batch_num, total_batches)
        total_inserted += inserted
        
        if inserted == 0:
            failed_batches.append(batch_num)
        
        # Progress report every 10 batches
        if batch_num % 10 == 0 or batch_num == total_batches:
            elapsed = datetime.now() - start_time
            progress = (batch_num / total_batches) * 100
            rate = batch_num / (elapsed.total_seconds() / 60) if elapsed.total_seconds() > 0 else 0
            print(f"📈 Progress: {batch_num}/{total_batches} batches ({progress:.1f}%)")
            print(f"⚡ Rate: {rate:.1f} batches/min")
            print(f"✅ Total inserted: {total_inserted}")
            
            # Estimate time remaining
            if progress > 0:
                remaining_batches = total_batches - batch_num
                est_minutes = remaining_batches / rate if rate > 0 else 0
                print(f"⏱️  Est. time remaining: {est_minutes:.1f} minutes")
            print("-" * 40)
    
    # Final summary
    end_time = datetime.now()
    total_time = end_time - start_time
    
    print("\n" + "=" * 60)
    print("🏁 FINAL RESULTS")
    print("=" * 60)
    print(f"⏰ Total time: {total_time}")
    print(f"✅ Successfully inserted: {total_inserted} streets")
    print(f"📊 Success rate: {total_inserted/len(all_streets)*100:.1f}%")
    
    if failed_batches:
        print(f"❌ Failed batches: {failed_batches}")
    
    # Project completion for Sunday
    print(f"\n🎯 SUNDAY DEADLINE STATUS:")
    if total_inserted >= len(all_streets) * 0.95:  # 95% success
        print("✅ TARGET ACHIEVED - Ready for Sunday deployment!")
        print(f"🕐 Completed by: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        missing = len(all_streets) - total_inserted
        print(f"⚠️  Still need {missing} streets")
        print(f"📅 Estimated additional time needed: {(missing/1000)*2:.1f} minutes")

if __name__ == "__main__":
    main()
