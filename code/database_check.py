#!/usr/bin/env python3
"""
Check current database status and create simple report
"""

from supabase import create_client
import json

# Supabase config
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def check_database():
    """Check database status and create report"""
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("=== DATABASE STATUS REPORT ===\n")
    
    try:
        # Get total count
        response = supabase.table('streets').select('*', count='exact').execute()
        total_count = response.count if hasattr(response, 'count') else 0
        print(f"Total streets in database: {total_count}")
        
        # Get sample of records
        sample_response = supabase.table('streets').select('*').limit(5).execute()
        if sample_response.data:
            print(f"\nSample records:")
            for i, record in enumerate(sample_response.data, 1):
                print(f"{i}. {record}")
        
        # Count by source
        all_response = supabase.table('streets').select('source').execute()
        if all_response.data:
            from collections import Counter
            source_counts = Counter(record.get('source', 'Unknown') for record in all_response.data)
            print(f"\nRecords by source:")
            for source, count in source_counts.items():
                print(f"  {source}: {count}")
        
        # Save report
        report = {
            'timestamp': '2025-12-05 01:53:00',
            'total_count': total_count,
            'sample_records': sample_response.data if sample_response.data else [],
            'source_breakdown': dict(source_counts) if all_response.data else {}
        }
        
        with open('/workspace/data/database_status_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: /workspace/data/database_status_report.json")
        
        return total_count
        
    except Exception as e:
        print(f"Database check failed: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    check_database()