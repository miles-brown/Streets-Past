#!/usr/bin/env python3
"""
Create sample UK street data for testing the etymology website.
Uses existing postal district data and creates common UK street names.
"""

import json
import random
from supabase import create_client

# Supabase configuration
supabase_url = "https://nadbmxfqknnnyuadhdtk.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

supabase = create_client(supabase_url, supabase_key)

# Common UK street name components
street_prefixes = [
    "High", "Main", "Church", "Mill", "School", "Market", "King", "Queen", "Prince", "Princess",
    "Victoria", "Albert", "George", "Edward", "William", "Mary", "Elizabeth", "John", "Thomas",
    "Oak", "Elm", "Ash", "Cedar", "Maple", "Pine", "Birch", "Willow", "Hawthorn", "Spruce",
    "Park", "Garden", "Field", "Green", "Meadow", "Brook", "River", "Hill", "Mount", "Valley",
    "North", "South", "East", "West", "Old", "New", "Lower", "Upper", "Great", "Little",
    "King's", "Queen's", "Saint", "St", "Cross", "Union", "Liberty", "Liberty", "Freedom",
    "Station", "Railway", "London", "Manchester", "Birmingham", "Leeds", "York", "Oxford"
]

street_suffixes = [
    "Street", "Road", "Lane", "Close", "Avenue", "Drive", "Place", "Square", "Gardens",
    "Way", "Grove", "Walk", "Path", "Row", "Terrace", "Rise", "Crescent", "View",
    "Park", "Court", "Grange", "House", "Manor", "Hall", "Lodge", "Cottage", "Farm",
    "Wood", "Woods", "Hill", "Hills", "Heights", "Mews", "Gate", "Yard", "Alley",
    "Head", "End", "Corner", "Turn", "Bridge", "Water", "Well", "Spring", "Field"
]

# County and city mappings based on postal areas
postal_area_mappings = {
    'B': {'county': 'West Midlands', 'city': 'Birmingham'},
    'M': {'county': 'Greater Manchester', 'city': 'Manchester'},
    'NE': {'county': 'Tyne and Wear', 'city': 'Newcastle upon Tyne'},
    'NG': {'county': 'Nottinghamshire', 'city': 'Nottingham'},
    'NN': {'county': 'Northamptonshire', 'city': 'Northampton'},
    'W': {'county': 'London', 'city': 'London'},
    'N': {'county': 'London', 'city': 'London'},
    'NW': {'county': 'London', 'city': 'London'},
    'SW': {'county': 'London', 'city': 'London'},
    'SE': {'county': 'London', 'city': 'London'},
    'EC': {'county': 'London', 'city': 'London'},
    'WC': {'county': 'London', 'city': 'London'},
    'S': {'county': 'South Yorkshire', 'city': 'Sheffield'},
    'L': {'county': 'Merseyside', 'city': 'Liverpool'},
    'G': {'county': 'Scotland', 'city': 'Glasgow'},
    'H': {'county': 'London', 'city': 'London'},
    'T': {'county': 'South East', 'city': 'Tonbridge'},
    'P': {'county': 'Cornwall', 'city': 'Plymouth'},
    'Y': {'county': 'Yorkshire', 'city': 'York'}
}

# Approximate coordinates for major postal areas (using area centers)
postal_area_coords = {
    'B': (52.4649, -1.88859),    # Birmingham
    'M': (53.4808, -2.2426),     # Manchester
    'NE': (54.9783, -1.6174),    # Newcastle
    'NG': (52.9548, -1.1581),    # Nottingham
    'NN': (52.2405, -0.8993),    # Northampton
    'W': (51.5074, -0.1278),     # London
    'N': (51.5074, -0.1278),     # London
    'NW': (51.5074, -0.1278),    # London
    'SW': (51.5074, -0.1278),    # London
    'SE': (51.5074, -0.1278),    # London
    'EC': (51.5074, -0.1278),    # London
    'WC': (51.5074, -0.1278),    # London
    'S': (53.3811, -1.4701),     # Sheffield
    'L': (53.4084, -2.9916),     # Liverpool
    'G': (55.8642, -4.2518),     # Glasgow
    'H': (51.5074, -0.1278),     # London
    'T': (51.1837, 0.2606),      # Tonbridge
    'P': (50.3715, -4.1439),     # Plymouth
    'Y': (53.9594, -1.0815)      # York
}

def generate_street_name():
    """Generate a random UK street name."""
    # 70% chance of prefix + suffix, 30% chance of just suffix
    if random.random() < 0.7:
        prefix = random.choice(street_prefixes)
        suffix = random.choice(street_suffixes)
        
        # Handle possessive forms
        if prefix.endswith('s') and not prefix.endswith('ss'):
            name = f"{prefix}' {suffix}"
        else:
            name = f"{prefix} {suffix}"
    else:
        name = random.choice(street_suffixes)
    
    return name

def generate_coordinate_variation(base_lat, base_lng, radius_km=5):
    """Generate a coordinate variation within a radius."""
    import math
    
    # Convert radius to degrees (approximate)
    lat_variation = random.uniform(-radius_km/111, radius_km/111)
    lng_variation = random.uniform(-radius_km/(111*math.cos(math.radians(base_lat))), radius_km/(111*math.cos(math.radians(base_lat))))
    
    return base_lat + lat_variation, base_lng + lng_variation

def create_sample_streets():
    """Create sample street data based on existing postal districts."""
    print("Fetching existing postal districts...")
    
    # Get existing postal districts from database
    districts_result = supabase.table('postal_districts').select('postal_area, postal_district, post_town, region, country').execute()
    
    if districts_result.error:
        print(f"Error fetching districts: {districts_result.error}")
        return
    
    districts = districts_result.data
    print(f"Found {len(districts)} postal districts")
    
    # Generate streets for each district
    streets_to_insert = []
    
    for district in districts:
        postal_area = district['postal_area']
        postal_district = district['postal_district']
        post_town = district['post_town']
        
        # Skip if we don't have mapping for this postal area
        if postal_area not in postal_area_mappings:
            continue
            
        # Get base coordinates for this area
        if postal_area in postal_area_coords:
            base_lat, base_lng = postal_area_coords[postal_area]
            
            # Generate 3-8 streets per postal district
            num_streets = random.randint(3, 8)
            
            for i in range(num_streets):
                street_name = generate_street_name()
                
                # Add some variation to coordinates
                lat, lng = generate_coordinate_variation(base_lat, base_lng, 2)
                
                # Determine county and city
                mapping = postal_area_mappings[postal_area]
                county = mapping['county']
                city = mapping['city']
                
                # Add postal district suffix for uniqueness
                full_street_name = f"{street_name} ({postal_district})"
                
                street_data = {
                    'name': full_street_name,
                    'county': county,
                    'city': city,
                    'postcode_area': postal_district,
                    'latitude': round(lat, 6),
                    'longitude': round(lng, 6),
                    'etymology_verified': False,
                    'created_at': 'now()',
                    'updated_at': 'now()'
                }
                
                streets_to_insert.append(street_data)
    
    print(f"Generated {len(streets_to_insert)} street records")
    
    # Insert streets in batches
    batch_size = 100
    for i in range(0, len(streets_to_insert), batch_size):
        batch = streets_to_insert[i:i+batch_size]
        
        print(f"Inserting batch {i//batch_size + 1}/{(len(streets_to_insert)-1)//batch_size + 1}...")
        
        result = supabase.table('streets').insert(batch).execute()
        
        if result.error:
            print(f"Error inserting batch: {result.error}")
            # Continue with next batch
            continue
        else:
            print(f"Successfully inserted batch of {len(batch)} records")
    
    print(f"Completed inserting street data!")

if __name__ == "__main__":
    create_sample_streets()