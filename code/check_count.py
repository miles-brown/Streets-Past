#!/usr/bin/env python3
"""
Simple street count checker
"""
import requests

def check_street_count():
    """Check current street count in database"""
    
    headers = {
        'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get all streets to count them
        response = requests.get(
            "https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/streets?select=street_name,street_type",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data)
            
            print(f"=== DATABASE STATUS ===")
            print(f"Total streets: {count}")
            
            # Show sample of streets
            if data:
                print(f"\nSample streets:")
                for i, street in enumerate(data[:15], 1):
                    print(f"{i:2d}. {street['street_name']} ({street['street_type']})")
            
            if count > 29:  # More than the original 29
                print(f"\n✅ SUCCESS! Database grew from 29 to {count} streets")
                print(f"✅ Import successful: {count - 29} new streets added")
            else:
                print(f"\n❌ No change in street count - import may have failed")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_street_count()