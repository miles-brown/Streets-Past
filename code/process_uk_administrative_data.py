#!/usr/bin/env python3
"""
Process UK Administrative Geography Data for Supabase Import
Transforms ONS Names & Codes datasets into the required format for counties and local_authorities tables.
"""

import pandas as pd
import uuid
import re
from pathlib import Path

def get_country_from_gss_code(gss_code):
    """Extract country from GSS code"""
    if gss_code.startswith('E'):
        return 'England'
    elif gss_code.startswith('W'):
        return 'Wales'
    elif gss_code.startswith('S'):
        return 'Scotland'
    elif gss_code.startswith('N'):
        return 'Northern Ireland'
    else:
        return 'Unknown'

def get_authority_type_from_name_and_code(name, gss_code):
    """Determine authority type from name and code patterns"""
    # Patterns to identify unitary authorities vs districts
    unitary_indicators = [
        'unitary authority', 'city of', 'borough of', 'city council',
        'county of', 'metropolitan borough', 'london borough'
    ]
    
    # Specific patterns in GSS codes
    if gss_code.startswith('E06') or gss_code.startswith('W06') or gss_code.startswith('S06') or gss_code.startswith('N09'):
        return 'Unitary Authority'
    
    # Check for metropolitan districts
    if gss_code.startswith('E08'):
        return 'Metropolitan District'
    
    # Check for London boroughs
    if gss_code.startswith('E09'):
        return 'London Borough'
    
    # Check for English districts
    if gss_code.startswith('E07'):
        return 'District'
    
    # Default to unitary for non-English areas
    if gss_code.startswith(('W', 'S', 'N')):
        return 'Unitary Authority'
    
    return 'Unitary Authority'  # Default

def extract_county_info(gss_code):
    """Extract county information from combined county/unitary authority file"""
    country = get_country_from_gss_code(gss_code)
    
    # For county unitary authorities (like E100xxx codes), these are actual counties
    if gss_code.startswith('E10'):
        return country, 'County'
    elif gss_code.startswith('E06'):
        return country, 'Unitary Authority'
    elif gss_code.startswith('W06'):
        return country, 'Unitary Authority'
    elif gss_code.startswith('S12'):
        return country, 'Council Area'
    elif gss_code.startswith('N09'):
        return country, 'District Council'
    else:
        return country, 'Unitary Authority'

def process_counties_file(input_file, output_file):
    """Process the County and Unitary Authority names and codes file"""
    print(f"Processing counties file: {input_file}")
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Clean and process the data
    processed_records = []
    
    for _, row in df.iterrows():
        gss_code = row['CTYUA24CD']
        name = row['CTYUA24NM']
        welsh_name = row['CTYUA24NMW'] if pd.notna(row['CTYUA24NMW']) else None
        
        country, authority_type = extract_county_info(gss_code)
        
        # Generate UUID for the county
        county_id = str(uuid.uuid4())
        
        # Determine if this is actually a county vs unitary authority
        if authority_type == 'County':
            # This is a traditional county
            county_name = name
            primary_name = name
            welsh_name_field = welsh_name
        else:
            # This is a unitary authority
            county_name = name  # Use the full name
            primary_name = name
            welsh_name_field = welsh_name
        
        record = {
            'county_id': county_id,
            'county_name': primary_name,
            'county_name_welsh': welsh_name_field,
            'gss_county_code': gss_code,
            'country': country,
            'authority_type': authority_type,
            'source_reference': 'County and Unitary Authority (December 2024) Names and Codes'
        }
        
        processed_records.append(record)
    
    # Create DataFrame and save
    result_df = pd.DataFrame(processed_records)
    result_df.to_csv(output_file, index=False)
    print(f"Created counties import file: {output_file}")
    print(f"Total records: {len(result_df)}")
    
    # Print summary by country and type
    print("\nSummary by country:")
    print(result_df.groupby(['country', 'authority_type']).size().reset_index(name='count'))
    
    return result_df

def process_local_authorities_file(input_file, output_file):
    """Process the Local Authority Districts names and codes file"""
    print(f"\nProcessing local authorities file: {input_file}")
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Clean and process the data
    processed_records = []
    
    for _, row in df.iterrows():
        gss_code = row['LAD25CD']
        name = row['LAD25NM']
        welsh_name = row['LAD25NMW'] if pd.notna(row['LAD25NMW']) else None
        
        country = get_country_from_gss_code(gss_code)
        authority_type = get_authority_type_from_name_and_code(name, gss_code)
        
        # Generate UUID for the local authority
        la_id = str(uuid.uuid4())
        
        record = {
            'la_id': la_id,
            'la_name': name,
            'la_name_welsh': welsh_name,
            'gss_la_code': gss_code,
            'country': country,
            'authority_type': authority_type,
            'source_reference': 'Local Authority Districts (April 2025) Names and Codes'
        }
        
        processed_records.append(record)
    
    # Create DataFrame and save
    result_df = pd.DataFrame(processed_records)
    result_df.to_csv(output_file, index=False)
    print(f"Created local authorities import file: {output_file}")
    print(f"Total records: {len(result_df)}")
    
    # Print summary by country and type
    print("\nSummary by country and authority type:")
    print(result_df.groupby(['country', 'authority_type']).size().reset_index(name='count'))
    
    return result_df

def validate_data(counties_df, local_authorities_df):
    """Validate the processed data for consistency and quality"""
    print("\n=== DATA VALIDATION ===")
    
    # Check for duplicates in GSS codes
    county_dupes = counties_df['gss_county_code'].duplicated().sum()
    la_dupes = local_authorities_df['gss_la_code'].duplicated().sum()
    
    print(f"Duplicate GSS codes in counties: {county_dupes}")
    print(f"Duplicate GSS codes in local authorities: {la_dupes}")
    
    # Check for missing values
    county_missing = counties_df.isnull().sum()
    la_missing = local_authorities_df.isnull().sum()
    
    print(f"\nMissing values in counties data:")
    print(county_missing[county_missing > 0])
    
    print(f"\nMissing values in local authorities data:")
    print(la_missing[la_missing > 0])
    
    # Check country distribution
    print(f"\nCounty distribution by country:")
    print(counties_df['country'].value_counts())
    
    print(f"\nLocal Authority distribution by country:")
    print(local_authorities_df['country'].value_counts())
    
    # Check GSS code format
    print(f"\nGSS code format validation:")
    valid_county_pattern = counties_df['gss_county_code'].str.match(r'^[EWNS]\d{2,3}\d{4,6}$')
    valid_la_pattern = local_authorities_df['gss_la_code'].str.match(r'^[EWNS]\d{2,3}\d{4,6}$')
    
    print(f"Valid county GSS codes: {valid_county_pattern.sum()}/{len(counties_df)}")
    print(f"Valid LA GSS codes: {valid_la_pattern.sum()}/{len(local_authorities_df)}")
    
    if not valid_county_pattern.all():
        invalid_counties = counties_df[~valid_county_pattern]['gss_county_code'].tolist()
        print(f"Invalid county GSS codes: {invalid_counties}")
    
    if not valid_la_pattern.all():
        invalid_las = local_authorities_df[~valid_la_pattern]['gss_la_code'].tolist()
        print(f"Invalid LA GSS codes: {invalid_las}")

def main():
    """Main processing function"""
    # Define file paths
    base_dir = Path('/workspace')
    data_dir = base_dir / 'data' / 'import'
    counties_input = data_dir / 'counties' / 'county_unitary_authority_december_2024.csv'
    local_auths_input = data_dir / 'local_authorities' / 'local_authority_districts_april_2025.csv'
    
    counties_output = data_dir / 'counties' / 'counties_import_supabase.csv'
    local_auths_output = data_dir / 'local_authorities' / 'local_authorities_import_supabase.csv'
    
    # Create output directories if they don't exist
    counties_output.parent.mkdir(parents=True, exist_ok=True)
    local_auths_output.parent.mkdir(parents=True, exist_ok=True)
    
    print("=== UK ADMINISTRATIVE DATA PROCESSING ===")
    print(f"Processing ONS Names & Codes datasets for Supabase import")
    print(f"Base directory: {base_dir}")
    print(f"Data directory: {data_dir}")
    
    try:
        # Process the datasets
        counties_df = process_counties_file(counties_input, counties_output)
        local_auths_df = process_local_authorities_file(local_auths_input, local_auths_output)
        
        # Validate the results
        validate_data(counties_df, local_auths_df)
        
        print(f"\n=== PROCESSING COMPLETE ===")
        print(f"Counties import file: {counties_output}")
        print(f"Local Authorities import file: {local_auths_output}")
        print(f"\nFiles are ready for Supabase import!")
        
        return counties_df, local_auths_df
        
    except Exception as e:
        print(f"Error during processing: {e}")
        raise

if __name__ == "__main__":
    counties_df, local_auths_df = main()