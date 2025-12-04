#!/usr/bin/env python3
import csv
import re

# Read the CSV file and generate INSERT statements
input_file = '/workspace/data/import/postcode_areas/sample_data/uk_postcodes_districts.csv'
output_file = '/workspace/insert_districts_batch.sql'

# UK region mapping for different postal areas
region_mapping = {
    # London regions
    'E': 'Greater London', 'EC': 'Greater London', 'N': 'Greater London', 
    'NW': 'Greater London', 'SE': 'Greater London', 'SW': 'Greater London',
    'W': 'Greater London', 'WC': 'Greater London',
    
    # Major UK cities and regions
    'B': 'West Midlands',      # Birmingham
    'BN': 'South East',        # Brighton  
    'BR': 'South East',        # Bromley
    'CR': 'Greater London',    # Croydon
    'DA': 'South East',        # Dartford
    'EN': 'East of England',   # Enfield
    'HA': 'Greater London',    # Harrow
    'IG': 'East of England',   # Ilford
    'KT': 'South East',        # Kingston
    'NW': 'Greater London',    # Northwest London
    'SM': 'Greater London',    # Sutton
    'SW': 'Greater London',    # Southwest London
    'UB': 'South East',        # Uxbridge
    'WD': 'East of England',   # Watford
    
    # Other major regions
    'AL': 'East of England', 'BD': 'Yorkshire and The Humber',
    'BH': 'South West', 'CA': 'North West', 'CF': 'Wales',
    'CH': 'North West', 'CM': 'East of England', 'CO': 'East of England',
    'CT': 'South East', 'CV': 'West Midlands', 'CW': 'North West',
    'DA': 'South East', 'DD': 'Scotland', 'DE': 'East Midlands',
    'DH': 'North East', 'DL': 'North East', 'DN': 'Yorkshire and The Humber',
    'DT': 'South West', 'DY': 'West Midlands', 'EH': 'Scotland',
    'EX': 'South West', 'FK': 'Scotland', 'FY': 'North West',
    'G': 'Scotland', 'GL': 'South West', 'GU': 'South East',
    'GY': 'Crown Dependencies', 'HA': 'Greater London', 'HD': 'Yorkshire and The Humber',
    'HG': 'Yorkshire and The Humber', 'HP': 'South East', 'HS': 'Scotland',
    'HU': 'Yorkshire and The Humber', 'IM': 'Crown Dependencies', 'IP': 'East of England',
    'IV': 'Scotland', 'JE': 'Crown Dependencies', 'KA': 'Scotland',
    'KT': 'South East', 'KW': 'Scotland', 'KY': 'Scotland',
    'L': 'North West', 'LA': 'North West', 'LD': 'Wales',
    'LE': 'East Midlands', 'LL': 'Wales', 'LN': 'East Midlands',
    'LS': 'Yorkshire and The Humber', 'LU': 'East of England', 'ME': 'South East',
    'ML': 'Scotland', 'NE': 'North East', 'NG': 'East Midlands',
    'NP': 'Wales', 'NR': 'East of England', 'NW': 'Greater London',
    'OL': 'North West', 'OX': 'South East', 'PA': 'Scotland',
    'PE': 'East of England', 'PH': 'Scotland', 'PL': 'South West',
    'PO': 'South East', 'PR': 'North West', 'RG': 'South East',
    'RH': 'South East', 'RM': 'East of England', 'S': 'Yorkshire and The Humber',
    'SA': 'Wales', 'SE': 'Greater London', 'SG': 'East of England',
    'SK': 'North West', 'SL': 'South East', 'SM': 'Greater London',
    'SN': 'South West', 'SO': 'South East', 'SP': 'South West',
    'SR': 'North East', 'SS': 'East of England', 'ST': 'West Midlands',
    'SW': 'Greater London', 'SY': 'Wales', 'TA': 'South West',
    'TD': 'Scotland', 'TF': 'West Midlands', 'TN': 'South East',
    'TR': 'South West', 'TS': 'North East', 'TW': 'Greater London',
    'UB': 'South East', 'WA': 'North West', 'WC': 'Greater London',
    'WD': 'East of England', 'WF': 'Yorkshire and The Humber',
    'WN': 'North West', 'WR': 'West Midlands', 'WS': 'West Midlands',
    'WV': 'West Midlands', 'YO': 'Yorkshire and The Humber', 'ZE': 'Scotland'
}

def get_region(postcode):
    """Extract the region based on the postal area"""
    if not postcode:
        return 'Unknown'
    
    # Handle multi-character areas first (EC, WC, etc.)
    for area_length in [2, 1]:
        area = postcode[:area_length]
        if area in region_mapping:
            return region_mapping[area]
    
    # If no match found, use the first letter
    first_letter = postcode[0] if postcode else 'Unknown'
    if first_letter in region_mapping:
        return region_mapping[first_letter]
    
    return 'Unknown'

def get_postal_area(postcode):
    """Extract the postal area (first 1-2 letters)"""
    if not postcode:
        return 'Unknown'
    
    # Handle multi-character areas first
    if len(postcode) >= 2 and postcode[:2] in ['EC', 'WC', 'SW', 'NW', 'SE', 'NE', 'SW']:
        return postcode[:2]
    
    # Otherwise use first letter
    return postcode[0]

print("Processing UK postcode districts data...")

# Read CSV and process data
districts_data = []
skipped_count = 0
processed_count = 0

with open(input_file, 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    
    for row in csv_reader:
        postcode = row['Postcode'].strip()
        town_area = row['Town/Area'].strip()
        post_town = row['Post Town'].strip()
        
        # Skip empty or invalid postcodes
        if not postcode or len(postcode) < 2:
            skipped_count += 1
            continue
            
        # Skip non-geographic postcodes
        if 'non-geographic' in town_area.lower() or 'Non-geographic' in town_area:
            skipped_count += 1
            continue
            
        # Use post_town if available, otherwise fall back to town_area
        final_post_town = post_town if post_town else town_area
        if not final_post_town:
            final_post_town = town_area
        
        if not final_post_town:
            skipped_count += 1
            continue
            
        # Extract postal area and create record
        postal_area = get_postal_area(postcode)
        region = get_region(postcode)
        
        districts_data.append({
            'postal_area': postal_area,
            'postal_district': postcode,
            'post_town': final_post_town,
            'region': region,
            'country': 'England' if region != 'Wales' and region != 'Scotland' and 'Crown Dependencies' not in region else region.replace('Crown Dependencies', 'England')
        })
        
        processed_count += 1

print(f"Processed {processed_count} valid postal districts")
print(f"Skipped {skipped_count} invalid/non-geographic postcodes")
print(f"Found {len(districts_data)} districts to insert")

# Generate INSERT statements in batches
batch_size = 500
batch_count = 0
total_inserted = 0

with open(output_file, 'w', encoding='utf-8') as sql_file:
    sql_file.write("-- Insert UK Postal Districts\n")
    sql_file.write("-- Generated from comprehensive UK postcode data\n\n")
    
    for i in range(0, len(districts_data), batch_size):
        batch = districts_data[i:i + batch_size]
        batch_count += 1
        
        sql_file.write(f"-- Batch {batch_count}: {len(batch)} records\n")
        sql_file.write("INSERT INTO postal_districts (postal_area, postal_district, post_town, region, country) VALUES\n")
        
        values = []
        for district in batch:
            # Escape single quotes in post_town
            post_town = district['post_town'].replace("'", "''")
            values.append(f"('{district['postal_area']}', '{district['postal_district']}', '{post_town}', '{district['region']}', '{district['country']}')")
        
        sql_file.write(",\n".join(values))
        sql_file.write("\nON CONFLICT (postal_district) DO NOTHING;\n\n")
        
        total_inserted += len(batch)
        print(f"Generated batch {batch_count} with {len(batch)} records")

print(f"Generated {batch_count} SQL batches")
print(f"Total records to insert: {total_inserted}")
print(f"SQL file saved to: {output_file}")