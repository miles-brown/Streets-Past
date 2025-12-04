#!/usr/bin/env python3
import csv
import re

# Read the CSV file and generate INSERT statements
input_file = '/workspace/data/import/postcode_areas/sample_data/uk_postcodes_districts.csv'
output_file = '/workspace/insert_districts_fixed.sql'

# Enhanced UK region mapping with specific postal areas
region_mapping = {
    # Scotland
    'AB': 'Scotland', 'DD': 'Scotland', 'EH': 'Scotland', 'FK': 'Scotland',
    'G': 'Scotland', 'HS': 'Scotland', 'IV': 'Scotland', 'KA': 'Scotland',
    'KW': 'Scotland', 'KY': 'Scotland', 'ML': 'Scotland', 'PA': 'Scotland',
    'PH': 'Scotland', 'TD': 'Scotland', 'ZE': 'Scotland',
    
    # Wales
    'CF': 'Wales', 'LD': 'Wales', 'LL': 'Wales', 'NP': 'Wales',
    'SA': 'Wales', 'SY': 'Wales',
    
    # Crown Dependencies
    'GY': 'Crown Dependencies', 'IM': 'Crown Dependencies', 'JE': 'Crown Dependencies',
    
    # London regions (precise areas)
    'E': 'Greater London', 'EC': 'Greater London', 'N': 'Greater London', 
    'NW': 'Greater London', 'SE': 'Greater London', 'SW': 'Greater London',
    'W': 'Greater London', 'WC': 'Greater London', 'TW': 'Greater London',
    
    # Single letter mappings for areas not covered above
    'A': 'Scotland', 'B': 'West Midlands', 'BN': 'South East',
    'BR': 'South East', 'CA': 'North West', 'CH': 'North West',
    'CM': 'East of England', 'CO': 'East of England', 'CR': 'Greater London',
    'CT': 'South East', 'CV': 'West Midlands', 'CW': 'North West',
    'DA': 'South East', 'DE': 'East Midlands', 'DH': 'North East',
    'DL': 'North East', 'DN': 'Yorkshire and The Humber', 'DT': 'South West',
    'DY': 'West Midlands', 'EN': 'East of England', 'EX': 'South West',
    'FY': 'North West', 'GL': 'South West', 'GU': 'South East',
    'HA': 'Greater London', 'HD': 'Yorkshire and The Humber', 'HG': 'Yorkshire and The Humber',
    'HP': 'South East', 'HU': 'Yorkshire and The Humber', 'IG': 'East of England',
    'IP': 'East of England', 'KT': 'South East', 'L': 'North West',
    'LA': 'North West', 'LE': 'East Midlands', 'LN': 'East Midlands',
    'LS': 'Yorkshire and The Humber', 'LU': 'East of England', 'ME': 'South East',
    'M': 'North West', 'NE': 'North East', 'NG': 'East Midlands',
    'NR': 'East of England', 'OL': 'North West', 'OX': 'South East',
    'PE': 'East of England', 'PL': 'South West', 'PO': 'South East',
    'PR': 'North West', 'RG': 'South East', 'RH': 'South East',
    'RM': 'East of England', 'S': 'Yorkshire and The Humber',
    'SL': 'South East', 'SM': 'Greater London', 'SN': 'South West',
    'SO': 'South East', 'SP': 'South West', 'SR': 'North East',
    'SS': 'East of England', 'ST': 'West Midlands', 'TF': 'West Midlands',
    'TN': 'South East', 'TR': 'South West', 'TS': 'North East',
    'UB': 'South East', 'WA': 'North West', 'WD': 'East of England',
    'WF': 'Yorkshire and The Humber', 'WN': 'North West', 'WR': 'West Midlands',
    'WS': 'West Midlands', 'WV': 'West Midlands', 'YO': 'Yorkshire and The Humber'
}

def get_region(postcode):
    """Extract the region based on the postal area with enhanced matching"""
    if not postcode:
        return 'Unknown'
    
    # Check for specific 2-letter areas first
    for area_length in [2, 1]:
        area = postcode[:area_length]
        if area in region_mapping:
            return region_mapping[area]
    
    # Fallback to first letter
    first_letter = postcode[0] if postcode else 'Unknown'
    return region_mapping.get(first_letter, 'Unknown')

def get_postal_area(postcode):
    """Extract the postal area (first 1-2 letters)"""
    if not postcode:
        return 'Unknown'
    
    # Handle multi-character areas first
    if len(postcode) >= 2 and postcode[:2] in ['EC', 'WC', 'SW', 'NW', 'SE', 'NE', 'SW', 'AB', 'DD', 'EH', 'FK']:
        return postcode[:2]
    
    # Otherwise use first letter
    return postcode[0]

def get_country(region):
    """Determine country based on region"""
    if region == 'Wales':
        return 'Wales'
    elif region == 'Scotland':
        return 'Scotland'  
    elif 'Crown Dependencies' in region:
        return 'England'
    else:
        return 'England'

print("Processing UK postcode districts data with fixed region mapping...")

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
        country = get_country(region)
        
        districts_data.append({
            'postal_area': postal_area,
            'postal_district': postcode,
            'post_town': final_post_town,
            'region': region,
            'country': country
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
    sql_file.write("-- Insert UK Postal Districts (Fixed Region Mapping)\n")
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