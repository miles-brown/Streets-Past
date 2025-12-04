#!/usr/bin/env python3
import pandas as pd
import os
import json

# Create import files directly with the data we have
print("Creating UK postcode import files...")

# Load area summary data
area_summary = pd.read_csv('/workspace/data/import/postcode_areas/sample_data/uk_postcodes_area_summary.csv')

# Create postcode areas CSV
print("Creating postcode areas file...")
area_data = []
for _, row in area_summary.iterrows():
    area_data.append({
        'postcode_area': row['Postcode area'],
        'area_name': row['Area covered'],
        'population': row.get('Population', ''),
        'households': row.get('Households', ''),
        'total_postcodes': row.get('Postcodes', ''),
        'active_postcodes': row.get('Active postcodes', ''),
        'latitude': row.get('Latitude', ''),
        'longitude': row.get('Longitude', '')
    })

area_df = pd.DataFrame(area_data)
area_df.to_csv('/workspace/data/import/postcode_areas/uk_postcode_areas.csv', index=False)
print(f"✓ Created uk_postcode_areas.csv with {len(area_data)} records")

# Create district mappings
print("Creating postcode districts file...")
districts = pd.read_csv('/workspace/data/import/postcode_areas/sample_data/uk_postcodes_districts.csv')

district_data = []
for _, row in districts.iterrows():
    district_code = row['Postcode']
    if pd.isna(district_code) or district_code == '':
        continue
        
    # Extract area code (first 1-2 characters)
    area_code = district_code[:2] if district_code[1].isalpha() else district_code[0]
    
    district_data.append({
        'outward_code': district_code,
        'postcode_area': area_code,
        'town_area': row.get('Town/Area', ''),
        'post_town': row.get('Post Town', ''),
        'region': row.get('Region', ''),
        'postcodes_count': row.get('Postcodes', ''),
        'active_postcodes_count': row.get('Active postcodes', '')
    })

district_df = pd.DataFrame(district_data)
district_df.to_csv('/workspace/data/import/postcode_areas/uk_postcode_outward_codes.csv', index=False)
print(f"✓ Created uk_postcode_outward_codes.csv with {len(district_data)} records")

# Create schema documentation
schema_info = {
    "uk_postcode_areas.csv": {
        "description": "UK postcode areas with basic information - 123 records covering all UK postcode areas",
        "columns": {
            "postcode_area": "Postcode area code (e.g., SE, SW, NW)",
            "area_name": "Name of the area covered by this postcode area",
            "population": "Total population in the area",
            "households": "Total number of households", 
            "total_postcodes": "Total number of postcodes in the area",
            "active_postcodes": "Number of active postcodes",
            "latitude": "Latitude of area center",
            "longitude": "Longitude of area center"
        }
    },
    "uk_postcode_outward_codes.csv": {
        "description": "UK postcode outward codes with post town mappings - 3,121 records covering all districts",
        "columns": {
            "outward_code": "Postcode outward code (e.g., SE1, SW2, NW3)",
            "postcode_area": "Parent postcode area code",
            "town_area": "Town or area name",
            "post_town": "Official post town",
            "region": "Region name",
            "postcodes_count": "Total postcodes in this district",
            "active_postcodes_count": "Active postcodes in this district"
        }
    }
}

with open('/workspace/data/import/postcode_areas/schema_documentation.json', 'w') as f:
    json.dump(schema_info, f, indent=2)

print("✓ Created schema_documentation.json")

print("\nImport files created successfully!")
print("Files available in /workspace/data/import/postcode_areas/:")
print("- uk_postcode_areas.csv: Postcode area mappings")
print("- uk_postcode_outward_codes.csv: Outward code to post town mappings")
print("- schema_documentation.json: Schema documentation")

# Create a sample of SE area mappings to show format
se_samples = district_df[district_df['postcode_area'] == 'SE'].head(10)
print(f"\nSample SE area mappings:")
print(se_samples[['outward_code', 'post_town']].to_string(index=False))