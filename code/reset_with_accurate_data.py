#!/usr/bin/env python3

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def clear_database():
    """Clear all streets from database"""
    print("🗑️  Clearing database...")
    
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }
    
    # Delete in batches
    batch_size = 100
    deleted = 0
    
    while True:
        # Get batch of IDs to delete
        select_params = {
            "select": "id",
            "limit": batch_size
        }
        
        get_response = requests.get(url, headers=headers, params=select_params)
        if get_response.status_code != 200:
            break
            
        batch = get_response.json()
        if not batch:
            break
        
        # Delete this batch
        ids = [record['id'] for record in batch]
        delete_response = requests.delete(
            url,
            headers=headers,
            json={"id": {"in": ids}}
        )
        
        if delete_response.status_code == 204:
            deleted += len(ids)
            print(f"   Deleted {deleted} records...", end='\r')
        else:
            print(f"❌ Error deleting batch: {delete_response.status_code}")
            break
        
        if len(batch) < batch_size:
            break
    
    print(f"\n✅ Database cleared: {deleted} records deleted")
    return deleted

def import_accurate_data():
    """Import accurate SE streets data"""
    print("\n📥 Importing accurate SE London streets...")
    
    # Load accurate data
    with open('/workspace/data/accurate_se_streets.json', 'r') as f:
        accurate_data = json.load(f)
    
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    imported = 0
    
    # Process each area
    for area, streets in accurate_data.items():
        print(f"   Importing {area} ({len(streets)} streets)...")
        
        for street in streets:
            record = {
                "name": street['name'],
                "postcode": area,
                "city": "London",
                "type": street.get('type', 'unknown'),
                "latitude": street.get('latitude'),
                "longitude": street.get('longitude')
            }
            
            response = requests.post(url, headers=headers, json=record)
            if response.status_code == 201:
                imported += 1
            else:
                print(f"   ❌ Error importing {street['name']}: {response.status_code}")
    
    print(f"\n✅ Import complete: {imported} streets imported")
    return imported

def verify_database():
    """Verify final database state"""
    print("\n🔍 Verifying database...")
    
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Prefer": "count=exact"
    }
    
    # Get total count
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        count_header = response.headers.get('content-range', '')
        if '/' in count_header:
            total = int(count_header.split('/')[-1])
            print(f"📊 Total streets in database: {total}")
            
            # Check SE3 specifically
            se3_params = {
                "postcode": "eq.SE3",
                "limit": 10,
                "select": "name,postcode,city"
            }
            
            se3_response = requests.get(url, headers=headers, params=se3_params)
            if se3_response.status_code == 200:
                se3_streets = se3_response.json()
                print(f"\n🏠 SE3 Sample Streets:")
                for i, street in enumerate(se3_streets, 1):
                    print(f"   {i:2d}. {street['name']} - {street['city']}")
            
            return total
    else:
        print(f"❌ Error verifying database: {response.status_code}")
        return 0

def main():
    print("🧹 Complete Database Reset with Accurate Data")
    print("=" * 60)
    
    # Step 1: Clear database
    deleted = clear_database()
    
    # Step 2: Import accurate data
    imported = import_accurate_data()
    
    # Step 3: Verify
    final_count = verify_database()
    
    print(f"\n📋 Final Summary:")
    print(f"   Deleted: {deleted} records")
    print(f"   Imported: {imported} accurate streets")
    print(f"   Final count: {final_count}")
    print(f"   Expected: 15,339")
    
    if final_count == 15339:
        print("✅ SUCCESS: Database matches expected accurate data!")
    else:
        print("⚠️  WARNING: Count mismatch - check data integrity")

if __name__ == "__main__":
    main()