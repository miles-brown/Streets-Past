#!/usr/bin/env python3
"""
Clean Fake Street Data from Database
Removes clearly fake entries that don't belong in SE London postcodes
"""

import requests
import json

# Database configuration
SUPABASE_URL = 'https://nadbmxfqknnnyuadhdtk.supabase.co'
SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo'

headers = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

# Fake street patterns that clearly don't belong in SE London
FAKE_PATTERNS = [
    # Streets that belong to other London areas
    'Clapham%',
    'Wimbledon%',
    'Putney%',
    'Chelsea%',
    'Notting Hill%',
    'Kensington%',
    'Richmond%',
    'Twickenham%',
    'Kingston%',
    
    # Other obvious geographical mismatches
    'Camden%',
    'Hampstead%',
    'Highgate%',
    'Islington%',
    'Hackney%',
    'City of London%',
    
    # Completely fake or mismatched patterns
    '%, SE3'  # Any street just listed as "Street Name, SE3" without proper geographic correlation
]

def identify_fake_streets():
    """Identify all fake street entries"""
    fake_entries = []
    
    # Check for streets with clear geographical mismatches
    for pattern in FAKE_PATTERNS:
        if pattern.endswith('%'):
            # Street name pattern search
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/streets?street_name=like.{pattern}',
                headers=headers
            )
        else:
            # Exact postcode search
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/streets?street_name=eq.{pattern}',
                headers=headers
            )
        
        if response.status_code == 200:
            entries = response.json()
            fake_entries.extend(entries)
    
    return fake_entries

def delete_fake_entries(fake_entries):
    """Delete fake entries from database"""
    deleted_count = 0
    
    for entry in fake_entries:
        street_id = entry.get('id')
        street_name = entry.get('street_name')
        
        if street_id:
            response = requests.delete(
                f'{SUPABASE_URL}/rest/v1/streets?id=eq.{street_id}',
                headers=headers
            )
            
            if response.status_code == 204:
                deleted_count += 1
                print(f"✓ Deleted: {street_name}")
            else:
                print(f"✗ Failed to delete: {street_name} (Status: {response.status_code})")
    
    return deleted_count

def main():
    print("=== CLEANING FAKE STREET DATA ===")
    print("Identifying fake entries...")
    
    fake_entries = identify_fake_streets()
    print(f"Found {len(fake_entries)} fake entries to delete")
    
    # Remove duplicates based on ID
    seen_ids = set()
    unique_fake_entries = []
    for entry in fake_entries:
        entry_id = entry.get('id')
        if entry_id and entry_id not in seen_ids:
            seen_ids.add(entry_id)
            unique_fake_entries.append(entry)
    
    print(f"Unique fake entries: {len(unique_fake_entries)}")
    
    if unique_fake_entries:
        print("\nDeleting fake entries...")
        deleted_count = delete_fake_entries(unique_fake_entries)
        print(f"\n✓ Successfully deleted {deleted_count} fake street entries")
    else:
        print("No fake entries found to delete")

if __name__ == "__main__":
    main()
