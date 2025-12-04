#!/usr/bin/env python3
"""
Direct database schema checker - queries Supabase to get actual column structure
"""

import os
import requests
import json

# Database connection details
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def query_database_schema():
    """Query the database to get actual schema information"""
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("Querying streets table schema...")
    
    # Query 1: Get column information using information_schema
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/rpc/describe_table",
            headers=headers,
            params={'table_name': 'streets'}
        )
        print(f"RPC query response: {response.status_code}")
        if response.status_code == 200:
            print(f"RPC data: {response.text}")
        else:
            print(f"RPC error: {response.text}")
    except Exception as e:
        print(f"RPC query failed: {e}")
    
    # Query 2: Try to get existing data to see what columns are actually there
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/streets?select=*&limit=1",
            headers=headers
        )
        print(f"\nSample data query response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"Found {len(data)} records")
                print("Sample record keys:")
                for key in data[0].keys():
                    print(f"  - {key}")
            else:
                print("No records found in streets table")
        else:
            print(f"Sample data error: {response.text}")
    except Exception as e:
        print(f"Sample data query failed: {e}")
    
    # Query 3: Try raw SQL query for schema
    try:
        sql_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'streets' 
        ORDER BY ordinal_position;
        """
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={'query': sql_query}
        )
        print(f"\nSQL query response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Schema information:")
            for row in data:
                print(f"  {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']}, default: {row['column_default']})")
        else:
            print(f"SQL error: {response.text}")
    except Exception as e:
        print(f"SQL query failed: {e}")

if __name__ == "__main__":
    query_database_schema()