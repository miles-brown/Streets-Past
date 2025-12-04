#!/usr/bin/env python3
import zipfile
import os

# Extract ONSPD file
onspd_zip = '/workspace/data/import/postcode_areas/downloads/ONSPD_Feb2025.zip'
onspd_extracted_dir = '/workspace/data/import/postcode_areas/downloads/extracted_onspd'

print(f"Extracting {onspd_zip}...")
os.makedirs(onspd_extracted_dir, exist_ok=True)
with zipfile.ZipFile(onspd_zip, 'r') as zip_ref:
    zip_ref.extractall(onspd_extracted_dir)
print(f"ONSPD extracted to {onspd_extracted_dir}")

# Extract NSPL file
nspl_zip = '/workspace/data/import/postcode_areas/downloads/NSPL_May2025.zip'
nspl_extracted_dir = '/workspace/data/import/postcode_areas/downloads/extracted_nspl'

print(f"Extracting {nspl_zip}...")
os.makedirs(nspl_extracted_dir, exist_ok=True)
with zipfile.ZipFile(nspl_zip, 'r') as zip_ref:
    zip_ref.extractall(nspl_extracted_dir)
print(f"NSPL extracted to {nspl_extracted_dir}")

print("All files extracted successfully!")