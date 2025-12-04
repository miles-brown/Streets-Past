#!/usr/bin/env python3
"""
Check exact field positions in the failing row
"""

import requests

# Supabase credentials
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

try:
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/streets?select=*&limit=1",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print("Field order and values:")
            for i, (key, value) in enumerate(data[0].items(), 1):
                print(f"{i:2d}. {key}: {repr(value)}")
        else:
            print("No data found")
    else:
        print(f"Request failed: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
