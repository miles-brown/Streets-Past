#!/usr/bin/env python3
"""
Check database schema and create simplified import
"""

import json
from supabase import create_client

# Supabase configuration
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

try:
    # Try to get a sample record to see what columns exist
    response = supabase.table('streets').select('*').limit(1).execute()
    
    if response.data:
        sample_record = response.data[0]
        print("=== DATABASE SCHEMA ===")
        print("Available columns:")
        for key in sorted(sample_record.keys()):
            print(f"  - {key}: {type(sample_record[key]).__name__}")
        
        print(f"\nSample record:")
        for key, value in sample_record.items():
            print(f"  {key}: {value}")
    else:
        print("No records in database")
        
    # Also get count
    count_response = supabase.table('streets').select('id', count='exact').execute()
    if hasattr(count_response, 'count'):
        print(f"\nTotal records: {count_response.count}")
    
except Exception as e:
    print(f"Error: {e}")