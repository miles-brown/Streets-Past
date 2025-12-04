#!/usr/bin/env python3

from supabase import create_client
import os

url = "https://nadbmxfqknnnyuadhdtk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

supabase = create_client(url, key)

# Query count directly
try:
    response = supabase.table('streets').select('*', count='exact').execute()
    print(f"Total count: {response.count}")
    
    # Also get some sample data
    sample = supabase.table('streets').select('street_name', 'county').limit(3).execute()
    print("Sample records:")
    for record in sample.data:
        print(f"  - {record.get('street_name')} ({record.get('county')})")
        
except Exception as e:
    print(f"Error: {e}")