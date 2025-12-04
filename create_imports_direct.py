#!/usr/bin/env python3
"""
Direct creation of import files bypassing bash environment
"""
import csv
import os

print("Creating UK Postcode Import Files")
print("=================================")

# Set up directories
base_dir = '/workspace/data/import/postcode_areas'
sample_data_dir = f'{base_dir}/sample_data'
final_dir = f'{base_dir}/final_imports'

# Create final imports directory
os.makedirs(final_dir, exist_ok=True)

print("Processing sample data...")

# Read and process area summary data
area_data = {}
print("1. Reading area summary data...")
with open(f'{sample_data_dir}/uk_postcodes_area_summary.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        area_code = row['Postcode area'].strip()
        area_covered = row['Area covered'].strip()
        area_data[area_code] = area_covered

print(f"   Found {len(area_data)} postcode areas")

# Read and process district data for post town mappings
outward_mappings = []
print("2. Reading district data for post town mappings...")
with open(f'{sample_data_dir}/uk_postcodes_districts.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        postcode = row['Postcode'].strip()
        post_town = row['Post Town'].strip()
        if post_town:  # Only include rows with post town
            outward_mappings.append((postcode, post_town))

print(f"   Found {len(outward_mappings)} postcode outward codes with post towns")

# Create postcode_areas import file
print("3. Creating postcode_areas import file...")
areas_file = f'{final_dir}/postcode_areas_import.csv'
with open(areas_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['area_code', 'area_covered', 'sample_outward_codes', 'primary_post_towns'])
    
    for area_code in sorted(area_data.keys()):
        area_covered = area_data[area_code]
        
        # Find sample outward codes and post towns for this area
        sample_outward_codes = []
        sample_post_towns = []
        
        for outward_code, post_town in outward_mappings:
            if outward_code.startswith(area_code):
                sample_outward_codes.append(outward_code)
                sample_post_towns.append(post_town)
        
        # Take first few examples (max 5)
        sample_outward_str = ', '.join(sample_outward_codes[:5])
        post_towns_str = ', '.join(sorted(set(sample_post_towns))[:5])
        
        writer.writerow([
            area_code,
            area_covered,
            sample_outward_str,
            post_towns_str
        ])

print(f"   Created: {areas_file}")

# Create outward codes import file
print("4. Creating outward_codes import file...")
outward_file = f'{final_dir}/postcode_outward_codes_import.csv'
with open(outward_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['outward_code', 'post_town', 'area_code', 'area_covered'])
    
    for outward_code, post_town in sorted(outward_mappings):
        # Extract area code (first 1-2 characters)
        if len(outward_code) >= 2:
            area_code = outward_code[:2]
        else:
            area_code = outward_code[0]
        
        area_covered = area_data.get(area_code, 'Unknown')
        
        writer.writerow([
            outward_code,
            post_town,
            area_code,
            area_covered
        ])

print(f"   Created: {outward_file}")

# Create summary documentation
print("5. Creating documentation...")
summary_file = f'{final_dir}/import_documentation.md'
with open(summary_file, 'w', encoding='utf-8') as f:
    f.write("# UK Postcode Area Data Import Files\n\n")
    f.write("## Overview\n")
    f.write(f"Generated on: December 4, 2025\n")
    f.write(f"Source: Sample data from UK postcode datasets\n\n")
    f.write("## Files Generated\n\n")
    f.write("### 1. postcode_areas_import.csv\n")
    f.write("Contains area-level data with postcode areas and their coverage.\n\n")
    f.write("**Columns:**\n")
    f.write("- `area_code`: Postcode area code (e.g., 'SE', 'B', 'AB')\n")
    f.write("- `area_covered`: Description of area coverage (e.g., 'South East London', 'Birmingham', 'Aberdeen')\n")
    f.write("- `sample_outward_codes`: Sample outward codes for this area\n")
    f.write("- `primary_post_towns`: Main post towns in this area\n\n")
    f.write(f"**Total records:** {len(area_data)} postcode areas\n\n")
    
    f.write("### 2. postcode_outward_codes_import.csv\n")
    f.write("Contains detailed mapping from outward codes to post towns.\n\n")
    f.write("**Columns:**\n")
    f.write("- `outward_code`: Outward code (e.g., 'SE1', 'B1', 'AB10')\n")
    f.write("- `post_town`: Associated post town (e.g., 'London', 'Birmingham', 'Aberdeen')\n")
    f.write("- `area_code`: Parent area code\n")
    f.write("- `area_covered`: Area description\n\n")
    f.write(f"**Total records:** {len(outward_mappings)} outward code mappings\n\n")
    
    f.write("## Sample Data Preview\n\n")
    f.write("### Postcode Areas (first 10)\n")
    for area_code in sorted(list(area_data.keys())[:10]):
        area_covered = area_data[area_code]
        f.write(f"- **{area_code}**: {area_covered}\n")
    
    f.write(f"\n### Outward Code Mappings (first 10)\n")
    for outward_code, post_town in sorted(outward_mappings)[:10]:
        if len(outward_code) >= 2:
            area_code = outward_code[:2]
        else:
            area_code = outward_code[0]
        area_covered = area_data.get(area_code, 'Unknown')
        f.write(f"- **{outward_code}** ({area_code}): {post_town} - {area_covered}\n")

print(f"   Created: {summary_file}")

print("\n✅ Import files created successfully!")
print(f"\nLocation: {final_dir}/")
print("Files:")
print("- postcode_areas_import.csv")
print("- postcode_outward_codes_import.csv") 
print("- import_documentation.md")
print(f"\nTotal: {len(area_data)} areas, {len(outward_mappings)} outward code mappings")

# Also create a simple completion marker file
marker_file = f'{final_dir}/generation_complete.txt'
with open(marker_file, 'w', encoding='utf-8') as f:
    f.write(f"UK Postcode import files generated successfully on 2025-12-04\n")
    f.write(f"Areas: {len(area_data)}\n")
    f.write(f"Outward codes: {len(outward_mappings)}\n")

print(f"   Marker file: {marker_file}")