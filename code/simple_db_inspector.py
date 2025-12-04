#!/usr/bin/env python3
"""
Simple database inspector - uses direct HTTP requests to check schema
"""

import requests
import json

# Database connection details
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ4MjYxOTksImV4cCI6MjA4MDQwMjE5OX0.gI7-b8DxjBTMlRLqerkCKUP2DuGK2YVhEozYx-M7gGE"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def inspect_database():
    """Inspect the database schema and existing data"""
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    print("=== CHECKING STREETS TABLE SCHEMA ===")
    
    # Try to get one sample record to see what columns exist
    try:
        print("1. Attempting to get sample record...")
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/streets?select=*&limit=1",
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"✓ Successfully retrieved {len(data)} records")
                print("\nAvailable columns in streets table:")
                for i, key in enumerate(data[0].keys(), 1):
                    print(f"  {i}. {key}")
                print(f"\nSample record: {json.dumps(data[0], indent=2)}")
            else:
                print("✓ Table exists but no records found")
        else:
            print(f"✗ Error accessing table: {response.text}")
            
    except Exception as e:
        print(f"✗ Exception during sample query: {e}")
    
    # Try to get current count
    try:
        print("\n2. Getting current record count...")
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/streets?select=count",
            headers=headers
        )
        
        print(f"Count response: {response.status_code}")
        print(f"Count response text: {response.text}")
        
    except Exception as e:
        print(f"✗ Exception during count query: {e}")

    # Try direct column inspection via information_schema
    try:
        print("\n3. Querying information_schema...")
        sql_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'streets' 
        ORDER BY ordinal_position;
        """
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/pg_sql",
            headers=headers,
            json={'sql': sql_query}
        )
        
        print(f"Schema query response: {response.status_code}")
        print(f"Schema query text: {response.text}")
        
    except Exception as e:
        print(f"✗ Exception during schema query: {e}")

if __name__ == "__main__":
    inspect_database()