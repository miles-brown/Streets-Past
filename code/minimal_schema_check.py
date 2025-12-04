#!/usr/bin/env python3
"""
Minimal schema discovery script
"""
import requests
import json

def get_schema():
    """Get the actual database schema by examining existing data"""
    
    # Database connection
    url = "https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/streets?select=*&limit=1"
    headers = {
        'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200 and response.text:
            data = response.json()
            if data:
                print("\n=== ACTUAL SCHEMA (from existing data) ===")
                print("Columns that exist in the database:")
                for i, column in enumerate(sorted(data[0].keys()), 1):
                    print(f"{i:2d}. {column}")
                
                print(f"\n=== SAMPLE RECORD ===")
                print(json.dumps(data[0], indent=2))
            else:
                print("No records found")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    get_schema()