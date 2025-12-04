#!/usr/bin/env python3
"""
Check existing local_authority_area values
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
        f"{SUPABASE_URL}/rest/v1/streets?select=county,local_authority_area&limit=10",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("Existing county and local_authority_area values:")
        for i, record in enumerate(data, 1):
            print(f"{i}. County: {record.get('county')}, LAA: {record.get('local_authority_area')}")
    else:
        print(f"Request failed: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
