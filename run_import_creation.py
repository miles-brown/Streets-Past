#!/usr/bin/env python3
import csv
import os
from collections import defaultdict

# Set up paths
base_dir = '/workspace/data/import/postcode_areas'
sample_data_dir = f'{base_dir}/sample_data'
import_dir = base_dir

# Ensure import directory exists
os.makedirs(f'{import_dir}/final_imports', exist_ok=True)

print("Processing sample data to create import files...")

# 1. Process area summary data to get area -> area_covered mapping
print("1. Processing area summary data...")
area_mappings = {}
with open(f'{sample_data_dir}/uk_postcodes_area_summary.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        area = row['Postcode area'].strip()
        area_covered = row['Area covered'].strip()
        area_mappings[area] = area_covered

print(f"Found {len(area_mappings)} postcode areas")

# 2. Process district data to get outward_code -> post_town mappings
print("2. Processing district data...")
outward_to_post_town = {}
with open(f'{sample_data_dir}/uk_postcodes_districts.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        postcode = row['Postcode'].strip()
        post_town = row['Post Town'].strip()
        if post_town:  # Only include if post town is not empty
            outward_to_post_town[postcode] = post_town

print(f"Found {len(outward_to_post_town)} postcode outward codes with post towns")

# 3. Create postcode_areas import file
print("3. Creating postcode_areas import file...")
with open(f'{import_dir}/final_imports/postcode_areas_import.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['area_code', 'area_covered', 'sample_outward_codes', 'primary_post_towns'])
    
    # Sort areas alphabetically
    for area_code in sorted(area_mappings.keys()):
        area_covered = area_mappings[area_code]
        
        # Find sample outward codes and post towns for this area
        sample_outward_codes = []
        sample_post_towns = []
        
        for outward_code, post_town in outward_to_post_town.items():
            if outward_code.startswith(area_code):
                sample_outward_codes.append(outward_code)
                sample_post_towns.append(post_town)
        
        # Take first few examples
        sample_outward_codes_str = ', '.join(sample_outward_codes[:5])
        primary_post_towns_str = ', '.join(sorted(set(sample_post_towns))[:5])
        
        writer.writerow([
            area_code,
            area_covered,
            sample_outward_codes_str,
            primary_post_towns_str
        ])

# 4. Create postcode_outward_codes import file
print("4. Creating postcode_outward_codes import file...")
with open(f'{import_dir}/final_imports/postcode_outward_codes_import.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['outward_code', 'post_town', 'area_code', 'sample_area_covered'])
    
    for outward_code, post_town in sorted(outward_to_post_town.items()):
        area_code = outward_code[:2] if len(outward_code) >= 2 else outward_code[0]
        sample_area_covered = area_mappings.get(area_code, 'Unknown')
        
        writer.writerow([
            outward_code,
            post_town,
            area_code,
            sample_area_covered
        ])

# 5. Create summary report
print("5. Creating summary report...")
with open(f'{import_dir}/final_imports/import_summary.txt', 'w', encoding='utf-8') as f:
    f.write("UK Postcode Area Data Import Summary\n")
    f.write("=====================================\n\n")
    f.write(f"Processing Date: 2025-12-04\n")
    f.write(f"Source: Sample data from Doogal and ONS datasets\n\n")
    f.write(f"Total postcode areas: {len(area_mappings)}\n")
    f.write(f"Total outward codes with post towns: {len(outward_to_post_town)}\n\n")
    f.write("Files created:\n")
    f.write("- postcode_areas_import.csv: Area-level data with coverage and sample mappings\n")
    f.write("- postcode_outward_codes_import.csv: Detailed outward code to post town mappings\n")
    f.write("- import_summary.txt: This summary file\n\n")
    f.write("Sample data preview:\n")
    f.write("-------------------\n")
    
    # Show first few area mappings
    f.write("Postcode Areas (first 10):\n")
    for area_code in sorted(list(area_mappings.keys())[:10]):
        area_covered = area_mappings[area_code]
        f.write(f"  {area_code}: {area_covered}\n")
    
    f.write(f"\nOutward Code Mappings (first 10):\n")
    count = 0
    for outward_code, post_town in sorted(outward_to_post_town.items()):
        if count < 10:
            area_code = outward_code[:2] if len(outward_code) >= 2 else outward_code[0]
            sample_area_covered = area_mappings.get(area_code, 'Unknown')
            f.write(f"  {outward_code} ({area_code}): {post_town} - {sample_area_covered}\n")
            count += 1

print("\nImport files created successfully!")
print(f"Files saved to: {import_dir}/final_imports/")
print("- postcode_areas_import.csv")
print("- postcode_outward_codes_import.csv")
print("- import_summary.txt")