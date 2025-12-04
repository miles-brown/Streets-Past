#!/usr/bin/env python3
"""
Check current database schema to verify fields
"""

import requests

SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ4MjYxOTksImV4cCI6MjA4MDQwMjE5OX0.gI7-b8DxjBTMlRLqerkCKUP2DuGK2YVhEozYx-M7gGE"

def check_current_schema():
    """Check what fields currently exist in the database"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get a sample record to see current fields
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/streets?limit=1",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            records = response.json()
            if records:
                print("Current database fields:")
                for field in records[0].keys():
                    print(f"  - {field}")
            else:
                print("No records found in database")
        else:
            print(f"Failed to fetch data: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_current_schema()