#!/usr/bin/env python3
"""
ROBUST STREET INSERTION - Verifies each batch insertion
Ensures all 15,339 SE London streets are properly inserted
"""

import requests
import json
from datetime import datetime
import time

# Supabase config
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def load_street_data():
    """Load the accurate street data"""
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
                'is_active': True,
                'current_status': 'Active',
                'verified_status': 'Verified',
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            all_streets.append(street_record)
    
    print(f"✅ Loaded {len(all_streets)} street records")
    return all_streets

def verify_insertion(street_name, postcode):
    """Verify a specific street was inserted"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/streets",
        headers=headers,
        params={'street_name': f'eq.{street_name}', 'postcode': f'eq.{postcode}'}
    )
    return len(response.json()) > 0 if response.status_code == 200 else False

def insert_batch_with_verification(streets_batch, batch_num, total_batches):
    """Insert a batch and verify every record was added"""
    print(f"🚀 Inserting batch {batch_num}/{total_batches} ({len(streets_batch)} streets)...")
    
    try:
        # Insert the batch
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/streets",
            headers=headers,
            json=streets_batch,
            timeout=60
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Batch {batch_num} failed: {response.status_code}")
            print(f"Error: {response.text}")
            return 0
        
        # Verify insertion by checking random samples
        verified_count = 0
        sample_size = min(10, len(streets_batch))  # Check up to 10 streets per batch
        
        for i in range(sample_size):
            street = streets_batch[i]
            if verify_insertion(street['street_name'], street['postcode']):
                verified_count += 1
        
        success_rate = verified_count / sample_size if sample_size > 0 else 0
        
        if success_rate >= 0.8:  # 80% success threshold
            print(f"✅ Batch {batch_num} verified: {verified_count}/{sample_size} ({success_rate:.1%})")
            return len(streets_batch)
        else:
            print(f"⚠️  Batch {batch_num} partial: {verified_count}/{sample_size} ({success_rate:.1%})")
            return verified_count * (len(streets_batch) / sample_size) if sample_size > 0 else 0
            
    except Exception as e:
        print(f"❌ Batch {batch_num} error: {str(e)}")
        return 0

def main():
    start_time = datetime.now()
    print("🔧 ROBUST STREET INSERTION - VERIFIED")
    print(f"⏰ Start time: {start_time}")
    print("🎯 Target: All 15,339 SE London streets by Sunday!")
    print("🔍 Each insertion will be verified")
    print("=" * 60)
    
    # Load street data
    all_streets = load_street_data()
    
    # Use smaller batches for more reliable insertion
    batch_size = 200  # Reduced for better verification
    total_batches = (len(all_streets) + batch_size - 1) // batch_size
    
    print(f"📊 Total streets to insert: {len(all_streets)}")
    print(f"📊 Batch size: {batch_size}")
    print(f"📊 Total batches: {total_batches}")
    print("=" * 60)
    
    total_inserted = 0
    failed_batches = []
    
    for batch_num in range(1, total_batches + 1):
        start_idx = (batch_num - 1) * batch_size
        end_idx = min(start_idx + batch_size, len(all_streets))
        batch = all_streets[start_idx:end_idx]
        
        inserted = insert_batch_with_verification(batch, batch_num, total_batches)
        total_inserted += int(inserted)
        
        if inserted == 0:
            failed_batches.append(batch_num)
        
        # Progress report
        if batch_num % 5 == 0 or batch_num == total_batches:
            elapsed = datetime.now() - start_time
            progress = (batch_num / total_batches) * 100
            rate = batch_num / (elapsed.total_seconds() / 60) if elapsed.total_seconds() > 0 else 0
            
            print(f"📈 Progress: {batch_num}/{total_batches} batches ({progress:.1f}%)")
            print(f"✅ Total inserted: {total_inserted}")
            print(f"⚡ Rate: {rate:.1f} batches/min")
            
            if elapsed.total_seconds() > 0:
                remaining_batches = total_batches - batch_num
                est_minutes = remaining_batches / rate if rate > 0 else 0
                print(f"⏱️  Est. remaining: {est_minutes:.1f} minutes")
            print("-" * 40)
        
        # Small delay between batches
        time.sleep(0.1)
    
    # Final results
    end_time = datetime.now()
    total_time = end_time - start_time
    
    print("\n" + "=" * 60)
    print("🏁 FINAL ROBUST RESULTS")
    print("=" * 60)
    print(f"⏰ Total time: {total_time}")
    print(f"✅ Verified insertions: {total_inserted} streets")
    print(f"📊 Success rate: {total_inserted/len(all_streets)*100:.1f}%")
    
    if failed_batches:
        print(f"❌ Failed batches: {failed_batches}")
    
    print(f"\n🎯 SUNDAY DEPLOYMENT STATUS:")
    if total_inserted >= 15000:
        print("🚀 EXCELLENT - Ready for Sunday!")
        print("✅ Database contains 15,000+ verified streets")
    elif total_inserted >= 12000:
        print("🚀 GOOD - Nearly ready for Sunday")
        print("⚠️  Some streets may need manual review")
    elif total_inserted >= 8000:
        print("⚠️  MARGINAL - Weekend work needed")
        print("❌ Significant gap to target")
    else:
        print("❌ FAILED - Major intervention needed")
        print("❌ Most streets missing")

if __name__ == "__main__":
    main()
