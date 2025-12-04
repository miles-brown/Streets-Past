#!/usr/bin/env python3
"""
Check the current count of streets in the database
"""

import os
import json
from supabase import create_client

# Supabase configuration
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def check_street_count():
    """Query database to get current street count"""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Query total count
        print("Querying database for street count...")
        response = supabase.table('streets').select('*', count='exact').execute()
        
        # Get count from response
        if hasattr(response, 'count') and response.count is not None:
            total_count = response.count
        else:
            # Alternative approach - count rows
            response2 = supabase.table('streets').select('id', count='exact').execute()
            total_count = response2.count if hasattr(response2, 'count') and response2.count is not None else 0
            
        print(f"\n=== DATABASE STATUS ===")
        print(f"Total records in streets table: {total_count:,}")
        
        # Also get count by county (top 10)
        print(f"\n=== TOP 10 COUNTIES BY RECORD COUNT ===")
        county_response = supabase.table('streets').select('county').execute()
        if county_response.data:
            from collections import Counter
            county_counts = Counter(record.get('county', 'Unknown') for record in county_response.data)
            for county, count in county_counts.most_common(10):
                print(f"{county}: {count:,}")
        
        # Get recent additions (last 50 records)
        print(f"\n=== SAMPLE OF RECENT ADDITIONS ===")
        recent_response = supabase.table('streets').select('*').order('created_at', desc=True).limit(10).execute()
        if recent_response.data:
            for i, record in enumerate(recent_response.data, 1):
                print(f"{i:2d}. {record.get('street_name', 'N/A')} ({record.get('county', 'N/A')})")
        
        return total_count
        
    except Exception as e:
        print(f"Error querying database: {e}")
        return 0

if __name__ == "__main__":
    count = check_street_count()
    print(f"\nFinal count: {count:,} records")