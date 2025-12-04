#!/usr/bin/env python3
"""
Data Quality Filter for OSM Street Names
Remove obviously fake/invalid street names before import
"""

import json
import re
from pathlib import Path

def is_valid_uk_street_name(street_name):
    """Check if street name looks like a legitimate UK street name"""
    
    if not street_name or len(street_name.strip()) < 3:
        return False
    
    # Remove extra spaces and normalize
    name = street_name.strip().lower()
    
    # Patterns that indicate fake/corrupted data
    fake_patterns = [
        # Looks like random characters or corrupted text
        r'^[a-z]{5,}$',  # All lowercase, 5+ chars, no spaces (e.g., "anatoolpad")
        r'\d{4,}',       # 4+ consecutive digits
        r'[xzq]{3,}',    # 3+ consecutive uncommon letters
        r'^.{15,}$',     # Very long single words
        # Specific known fake entries from the data
        'anatoolpad', 'penderry', 'birkhall', 'ardoch', 'greenside'
    ]
    
    # Check for fake patterns
    for pattern in fake_patterns:
        if re.match(pattern, name):
            return False
    
    # Must contain at least one valid street suffix or be a common street name
    street_suffixes = [
        'street', 'road', 'lane', 'avenue', 'close', 'drive', 'way', 'place', 
        'square', 'grove', 'crescent', 'court', 'park', 'hill', 'field', 'wood',
        'green', 'common', 'meadow', 'bridge', 'parkway', 'circular', 'walk',
        'terrace', 'row', 'yard', 'alley', 'passage', 'arcade', 'mews',
        'heights', 'estates', 'gardens', 'orchard', 'valley', 'mount',
        'cross', 'corner', 'junction', 'station', 'market', 'high',
        'church', 'main', 'north', 'south', 'east', 'west', 'old', 'new'
    ]
    
    # Check if contains valid suffix
    for suffix in street_suffixes:
        if suffix in name:
            return True
    
    # Check for compound names (e.g., "St Mary Street")
    if ' ' in name and any(word in name for word in ['saint', 'st', 'st.', 'mary', 'john', 'paul', 'peter', 'michael']):
        return True
    
    # Check for royal names, common town names, or well-known locations
    common_uk_places = [
        'bridge', 'tower', 'royal', 'palace', 'cathedral', 'abbey', 'castle',
        'hampstead', 'camden', 'islington', 'notting', 'fulham', 'chelsea',
        'kensington', 'westminster', 'mayfair', 'soho', ' Covent Garden',
        'borough', 'borough', 'southwark', 'lambeth', 'vauxhall', 'charing',
        'victoria', 'baker', 'oxford', 'bond', 'regent', 'madison', 'fleet',
        'temple', 'aldgate', 'canary', 'greenwich', 'woolwich', 'richmond',
        'kingston', 'wimbledon', 'putney', 'chelsea', 'fulham', ' hammersmith'
    ]
    
    if any(place in name for place in common_uk_places):
        return True
    
    # If it's just a single word and doesn't match any pattern, likely fake
    if ' ' not in name and not any(suffix in name for suffix in ['street', 'road', 'lane', 'avenue', 'close', 'drive']):
        return False
    
    return True

def filter_valid_streets():
    """Filter out invalid street names and show results"""
    
    # Load OSM data
    try:
        with open('/workspace/data/osm_sample_uk_streets.json', 'r') as f:
            osm_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
    
    streets_data = osm_data.get('streets', [])
    print(f"=== DATA QUALITY FILTER ===")
    print(f"Original total streets: {len(streets_data)}")
    
    # Filter valid streets
    valid_streets = []
    invalid_streets = []
    
    for record in streets_data:
        street_name = record.get('street_name', '').strip()
        
        if is_valid_uk_street_name(street_name):
            valid_streets.append(record)
        else:
            invalid_streets.append((street_name, record.get('osm_id')))
    
    print(f"Valid streets: {len(valid_streets)}")
    print(f"Invalid/fake streets removed: {len(invalid_streets)}")
    
    # Show examples of removed invalid names
    print(f"\nExamples of REMOVED invalid street names:")
    for i, (name, osm_id) in enumerate(invalid_streets[:10]):
        print(f"  {i+1:2d}. '{name}' (OSM ID: {osm_id})")
    
    if len(invalid_streets) > 10:
        print(f"  ... and {len(invalid_streets) - 10} more")
    
    # Show examples of kept valid names
    print(f"\nExamples of KEPT valid street names:")
    valid_names = [record.get('street_name', '').strip() for record in valid_streets[:10]]
    for i, name in enumerate(valid_names):
        print(f"  {i+1:2d}. {name}")
    
    # Save cleaned data
    cleaned_data = {
        'metadata': {
            **osm_data.get('metadata', {}),
            'original_count': len(streets_data),
            'valid_count': len(valid_streets),
            'removed_count': len(invalid_streets),
            'filtered_at': '2025-12-05T05:22:02'
        },
        'streets': valid_streets
    }
    
    output_file = '/workspace/data/cleaned_osm_streets.json'
    with open(output_file, 'w') as f:
        json.dump(cleaned_data, f, indent=2)
    
    print(f"\n=== FILTERING COMPLETE ===")
    print(f"Cleaned data saved to: {output_file}")
    print(f"Ready for import: {len(valid_streets)} valid UK street records")
    
    return cleaned_data

if __name__ == "__main__":
    filter_valid_streets()