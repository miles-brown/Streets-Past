#!/usr/bin/env python3

import requests
import json
import time

# Supabase configuration
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def write_log(message):
    """Write to log file"""
    with open('/workspace/database_reset_log.txt', 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message)

def clear_database():
    """Clear all streets from database"""
    write_log("🗑️ Starting database cleanup...")
    
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }
    
    # Use SQL delete for efficiency
    delete_url = f"{SUPABASE_URL}/rest/v1/rpc/delete_all_streets"
    delete_headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Try RPC first, fallback to batch delete
    try:
        response = requests.post(delete_url, headers=delete_headers)
        write_log(f"RPC delete result: {response.status_code}")
    except:
        write_log("RPC delete failed, using batch method...")
        
        # Fallback: batch delete
        batch_size = 100
        deleted = 0
        
        while True:
            select_params = {"select": "id", "limit": batch_size}
            get_response = requests.get(url, headers=headers, params=select_params)
            
            if get_response.status_code != 200:
                break
                
            batch = get_response.json()
            if not batch:
                break
            
            # Delete this batch
            ids = [record['id'] for record in batch]
            delete_response = requests.delete(
                f"{url}?id=in.({','.join(map(str, ids))})",
                headers=headers
            )
            
            if delete_response.status_code in [200, 204]:
                deleted += len(ids)
                write_log(f"Deleted batch: {len(ids)} records (total: {deleted})")
            else:
                write_log(f"Delete error: {delete_response.status_code}")
                break
            
            if len(batch) < batch_size:
                break
        
        write_log(f"✅ Cleanup complete: {deleted} records deleted")
        return deleted
    
    write_log("✅ Database cleared")
    return 0

def import_data():
    """Import accurate data"""
    write_log("📥 Loading accurate data...")
    
    with open('/workspace/data/accurate_se_streets.json', 'r') as f:
        data = json.load(f)
    
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    imported = 0
    
    for area, streets in data.items():
        write_log(f"Processing {area}: {len(streets)} streets")
        
        for street in streets:
            record = {
                "name": street['name'],
                "postcode": area,
                "city": "London", 
                "type": street.get('type', 'residential'),
                "latitude": street.get('latitude'),
                "longitude": street.get('longitude')
            }
            
            try:
                response = requests.post(url, headers=headers, json=record)
                if response.status_code == 201:
                    imported += 1
                    if imported % 1000 == 0:
                        write_log(f"Imported {imported} streets...")
                else:
                    write_log(f"Import error for {street['name']}: {response.status_code}")
            except Exception as e:
                write_log(f"Exception importing {street['name']}: {e}")
    
    write_log(f"✅ Import complete: {imported} streets")
    return imported

def verify():
    """Verify final state"""
    write_log("🔍 Verifying database...")
    
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Prefer": "count=exact"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        count_header = response.headers.get('content-range', '')
        if '/' in count_header:
            total = int(count_header.split('/')[-1])
            write_log(f"📊 Final database count: {total}")
            
            # Check SE3
            se3_params = {
                "postcode": "eq.SE3", 
                "limit": 5,
                "select": "name"
            }
            
            se3_response = requests.get(url, headers=headers, params=se3_params)
            if se3_response.status_code == 200:
                se3_streets = se3_response.json()
                write_log("SE3 Sample Streets:")
                for street in se3_streets:
                    write_log(f"  - {street['name']}")
            
            return total
    
    write_log("❌ Verification failed")
    return 0

# Main execution
try:
    write_log("=== DATABASE RESET STARTED ===")
    
    deleted = clear_database()
    imported = import_data()
    final_count = verify()
    
    write_log("=== SUMMARY ===")
    write_log(f"Deleted: {deleted}")
    write_log(f"Imported: {imported}")
    write_log(f"Final count: {final_count}")
    write_log(f"Expected: 15339")
    
    if final_count == 15339:
        write_log("✅ SUCCESS: Database reset complete!")
    else:
        write_log("⚠️ Count mismatch detected")
        
    write_log("=== COMPLETED ===")
    
except Exception as e:
    write_log(f"❌ CRITICAL ERROR: {e}")
