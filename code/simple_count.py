#!/usr/bin/env python3
"""
Simple database count query
"""

import os
from supabase import create_client

# Supabase configuration  
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def get_count():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Get count
        response = supabase.table('streets').select('id', count='exact').execute()
        count = response.count if hasattr(response, 'count') and response.count else 0
        
        print(f"Current database count: {count:,}")
        
        # Get sample of existing records
        response2 = supabase.table('streets').select('*').limit(5).execute()
        print(f"\nSample records:")
        for i, record in enumerate(response2.data, 1):
            print(f"{i}. {record.get('street_name', 'N/A')} ({record.get('county', 'N/A')})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_count()