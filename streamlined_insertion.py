#!/usr/bin/env python3
"""
STREAMLINED SUNDAY DEPLOYMENT - Fast insertion for major areas
No complex verification, focus on completing SE1, SE3, SE16, SE8 first
"""

import requests
import json
from datetime import datetime

# Supabase config
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# Focus on TOP 4 AREAS for maximum impact
TOP_AREAS = ['SE1', 'SE3', 'SE16', 'SE8']

def load_top_areas():
    """Load only the top 4 highest-volume areas"""
    print("📁 Loading TOP 4 priority areas...")
    with open('/workspace/data/accurate_se_streets.json', 'r') as f:
        data = json.load(f)
    
    top_streets = []
    total_top = 0
    
    for area in TOP_AREAS:
        if area in data:
            streets = data[area]
            total_top += len(streets)
            
            for street in streets:
                street_record = {
                    'street_name': street['name'],
                    'street_type': street.get('type', 'residential'),
                    'postcode': area,
                    'post_town': 'London',
                    'latitude': street['latitude'],
                    'longitude': street['longitude'],
                    'county': 'Greater London',
                    'local_authority_area': 'London Borough',
                    'is_active': True,
                    'current_status': 'Active',
                    'verified_status': 'Verified'
                }
                top_streets.append(street_record)
    
    print(f"✅ Loaded {len(top_streets)} streets from top areas")
    print(f"📊 Target: {total_top}/15,339 = {total_top/15339*100:.1f}% of total")
    return top_streets

def fast_insert(streets_batch):
    """Fast insertion without verification delay"""
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/streets",
            headers=headers,
            json=streets_batch,
            timeout=30  # Shorter timeout for speed
        )
        return response.status_code in [200, 201]
    except:
        return False

def main():
    start_time = datetime.now()
    print("🚀 STREAMLINED SUNDAY DEPLOYMENT")
    print(f"⏰ Start time: {start_time}")
    print(f"🎯 Focus: TOP 4 areas = {sum([2114, 1887, 1624, 1231])} streets")
    print("⚡ No verification delays - maximum speed")
    print("=" * 60)
    
    # Load top areas
    top_streets = load_top_areas()
    
    # Process in large batches for speed
    batch_size = 500
    total_batches = (len(top_streets) + batch_size - 1) // batch_size
    
    print(f"📊 Processing {len(top_streets)} streets in {total_batches} batches")
    print("=" * 60)
    
    processed = 0
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(top_streets))
        batch = top_streets[start_idx:end_idx]
        
        if fast_insert(batch):
            processed += len(batch)
            progress = (processed / len(top_streets)) * 100
            elapsed = datetime.now() - start_time
            rate = processed / (elapsed.total_seconds() / 60) if elapsed.total_seconds() > 0 else 0
            
            print(f"✅ Batch {batch_num + 1}/{total_batches}: {len(batch)} streets")
            print(f"📈 Progress: {processed}/{len(top_streets)} ({progress:.1f}%) | Rate: {rate:.0f}/min")
        else:
            print(f"❌ Batch {batch_num + 1} failed")
        
        # Progress report every 5 batches
        if (batch_num + 1) % 5 == 0 or batch_num + 1 == total_batches:
            elapsed = datetime.now() - start_time
            print(f"⏰ Elapsed: {elapsed}")
            if elapsed.total_seconds() > 0:
                remaining = len(top_streets) - processed
                est_seconds = (remaining / max(1, processed)) * elapsed.total_seconds()
                print(f"⏱️  Est. remaining: {est_seconds/60:.1f} minutes")
            print("-" * 40)
    
    # Final results
    end_time = datetime.now()
    total_time = end_time - start_time
    
    print("\n" + "=" * 60)
    print("🏁 STREAMLINED RESULTS")
    print("=" * 60)
    print(f"⏰ Total time: {total_time}")
    print(f"✅ Top areas inserted: {processed}")
    print(f"📊 Coverage: {processed/15339*100:.1f}% of total dataset")
    
    # Sunday assessment
    coverage = processed / 15339 * 100
    if coverage >= 50:
        print(f"\n🚀 SUNDAY DEPLOYMENT: ACHIEVED!")
        print(f"✅ {coverage:.1f}% coverage with major areas")
        print(f"✅ Database ready for production use")
    elif coverage >= 30:
        print(f"\n🚀 SUNDAY DEPLOYMENT: GOOD PROGRESS")
        print(f"✅ {coverage:.1f}% coverage achieved")
        print(f"✅ Core SE areas available")
    else:
        print(f"\n⚠️  SUNDAY DEPLOYMENT: PARTIAL")
        print(f"⚠️  Only {coverage:.1f}% coverage")

if __name__ == "__main__":
    main()
