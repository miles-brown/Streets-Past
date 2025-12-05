#!/usr/bin/env python3

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def check_schema():
    """Check current database schema"""
    print("🔍 Checking database schema...")
    
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }
    
    # Try to get a sample record to see the schema
    params = {"limit": 1}
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print("Current record structure:")
            for key, value in data[0].items():
                print(f"  {key}: {type(value).__name__}")
    else:
        print(f"Error: {response.text}")

def test_single_insert():
    """Test inserting a single record"""
    print("\n🧪 Testing single record insert...")
    
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test with a simple record
    test_record = {
        "name": "Test Street",
        "postcode": "SE3", 
        "city": "London",
        "type": "residential"
    }
    
    response = requests.post(url, headers=headers, json=test_record)
    print(f"Test insert status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Single insert successful")
        return True
    else:
        print(f"❌ Single insert failed: {response.text}")
        return False

def clear_and_rebuild():
    """Clear database and rebuild with correct schema"""
    print("\n🗑️ Clearing and rebuilding database...")
    
    # Clear existing data
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }
    
    # Delete all records
    delete_response = requests.delete(f"{url}?id=gte.0", headers=headers)
    print(f"Delete status: {delete_response.status_code}")
    
    if delete_response.status_code in [200, 204]:
        print("✅ Database cleared")
        
        # Test single insert again
        if test_single_insert():
            print("✅ Schema verification successful")
            return True
    else:
        print(f"❌ Failed to clear: {delete_response.text}")
        return False

if __name__ == "__main__":
    check_schema()
    clear_and_rebuild()