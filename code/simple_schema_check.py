#!/usr/bin/env python3

from supabase import create_client
import json

url = "https://nadbmxfqknnnyuadhdtk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

supabase = create_client(url, key)

try:
    # Get count first
    response = supabase.table('streets').select('*', count='exact').execute()
    print(f"Total records: {response.count}")
    
    # Get sample
    sample = supabase.table('streets').select('*').limit(1).execute()
    if sample.data:
        record = sample.data[0]
        print("\nColumns in database:")
        for key, value in record.items():
            print(f"  {key}: {type(value).__name__}")
    
    # Get a few records to see the data structure
    records = supabase.table('streets').select('*').limit(3).execute()
    print(f"\nSample records:")
    for i, record in enumerate(records.data, 1):
        print(f"{i}. {record}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()