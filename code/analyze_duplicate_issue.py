#!/usr/bin/env python3
"""
Analyze the duplicate detection issue in the current import process
"""

import json
from collections import Counter

def analyze_duplicate_issue():
    """Analyze how current duplicate detection works"""
    print("=== DUPLICATE ANALYSIS ===")
    
    # Load OSM data
    try:
        with open('/workspace/data/osm_sample_uk_streets.json', 'r') as f:
            osm_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
    
    streets_data = osm_data.get('streets', [])
    print(f"Total OSM streets: {len(streets_data)}")
    
    # Current duplicate detection logic (from import script)
    seen_names = set()
    unique_streets = []
    
    for record in streets_data:
        street_name = record.get('street_name', '').strip()
        
        if street_name and street_name.lower() not in seen_names:
            seen_names.add(street_name.lower())
            unique_streets.append(record)
    
    print(f"Current approach (street name only): {len(unique_streets)} unique streets")
    print(f"Records skipped as duplicates: {len(streets_data) - len(unique_streets)}")
    
    # Show some examples of potential duplicates that are being skipped
    street_name_counts = Counter([record.get('street_name', '').strip() for record in streets_data if record.get('street_name')])
    
    print(f"\nTop 10 most common street names:")
    for name, count in street_name_counts.most_common(10):
        if count > 1:
            print(f"  '{name}': {count} occurrences")
    
    # Show sample records for a common street name
    high_street_records = [record for record in streets_data if record.get('street_name', '').lower() == 'high street']
    
    if high_street_records:
        print(f"\nExample: 'High Street' appears {len(high_street_records)} times")
        print("Current logic treats them all as duplicates - only 1 would be imported!")
        
        for i, record in enumerate(high_street_records[:5]):  # Show first 5
            print(f"  #{i+1}: OSM ID {record.get('osm_id')} (would all be skipped except first)")
    
    print(f"\n=== THE PROBLEM ===")
    print("Current duplicate detection is TOO SIMPLE:")
    print("- It only checks 'street_name' field")
    print("- Treats 'High Street, Orpington' and 'High Street, Chislehurst' as SAME")
    print("- Only imports the first occurrence of any street name")
    print()
    print("=== THE SOLUTION ===")
    print("Should check for duplicates using:")
    print("- street_name + postcode/locality combination")
    print("- OR use a unique identifier like osm_id")
    print("- OR check street_name + geographic area")

if __name__ == "__main__":
    analyze_duplicate_issue()