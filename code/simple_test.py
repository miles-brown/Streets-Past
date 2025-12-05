#!/usr/bin/env python3

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def test_basic_connectivity():
    """Test basic connectivity and get schema info"""
    print("🧪 Basic Database Test")
    print("=" * 40)
    
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }
    
    # Try to get one record to see current schema
    params = {"limit": 1}
    
    print("Testing GET request...")
    response = requests.get(url, headers=headers, params=params)
    print(f"GET Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print("Current record structure:")
            for key, value in data[0].items():
                print(f"  {key}: {type(value).__name__} = {value}")
        else:
            print("No records found")
    
    # Try inserting a minimal record
    print("\nTesting POST request...")
    test_record = {
        "name": "Test Street",
        "postcode": "SE3"
    }
    
    post_response = requests.post(url, headers=headers, json=test_record)
    print(f"POST Status: {post_response.status_code}")
    
    if post_response.status_code != 201:
        print(f"POST Error Response: {post_response.text}")
    else:
        print("✅ Basic insert successful")
        
        # Clean up the test record
        record_id = post_response.json().get('id')
        if record_id:
            delete_response = requests.delete(f"{url}?id=eq.{record_id}", headers=headers)
            print(f"Cleanup Status: {delete_response.status_code}")

if __name__ == "__main__":
    test_basic_connectivity()