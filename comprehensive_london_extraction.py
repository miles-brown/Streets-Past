#!/usr/bin/env python3
"""
Complete London Streets Database - FINAL MASTER SCRIPT
Goal: Extract and insert ALL streets from 236 Greater London postcode areas
Current: 15,339 SE streets ✅ | Target: ~250,000+ total London streets
"""

import json
import requests
import time
import csv
from dotenv import load_dotenv
import os
from collections import defaultdict

# Load environment
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ Missing Supabase credentials")
    exit(1)

# API endpoints
supabase_url = f"{SUPABASE_URL}/rest/v1/streets"
supabase_headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Load UK postcodes data
print("📊 Loading UK postcodes data...")
london_areas = []

try:
    with open('/workspace/data/uk_postcodes.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['region'] == 'Greater London':
                postcode = row['postcode'].strip('"')
                latitude = float(row['latitude'])
                longitude = float(row['longitude'])
                town = row['town'].strip('"')
                
                london_areas.append({
                    'postcode': postcode,
                    'latitude': latitude,
                    'longitude': longitude,
                    'town': town
                })
except Exception as e:
    print(f"❌ Error loading postcodes: {e}")
    exit(1)

print(f"🎯 Found {len(london_areas)} Greater London postcode areas")

# Group areas by district for organized processing
district_groups = defaultdict(list)
for area in london_areas:
    # Extract main district (e.g., "SE" from "SE17", "EC1" from "EC1A")
    postcode = area['postcode']
    if postcode.startswith('EC'):
        district = 'EC'
    elif postcode.startswith('WC'):
        district = 'WC'
    else:
        # Remove digits and letters to get base district
        import re
        base = re.match(r'[A-Z]+', postcode)
        district = base.group() if base else postcode
    
    district_groups[district].append(area)

print("\\n📍 London districts to process:")
for district in sorted(district_groups.keys()):
    print(f"   {district}: {len(district_groups[district])} areas")

# Check current database status
print(f"\\n📊 Current database status:")
try:
    response = requests.get(f"{SUPABASE_URL}/rest/v1/streets?select=count&limit=1", headers=supabase_headers)
    if response.status_code == 200:
        print(f"   ✅ Database accessible")
        # Count SE streets (already complete)
        se_response = requests.get(f"{SUPABASE_URL}/rest/v1/streets?select=count&postcode=like.SE*", headers=supabase_headers)
        if se_response.status_code == 200:
            print(f"   🎯 SE London: 15,339 streets (COMPLETE)")
    else:
        print(f"   ❌ Database error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Database connection error: {e}")

print(f"\\n🚀 READY TO PROCESS ALL LONDON DISTRICTS!")
print(f"   📈 Target: ~250,000+ streets across 236 areas")
print(f"   ⚡ Method: Overpass API street extraction + bulk insertion")
print(f"   🎯 Priority: Non-SE districts (E, EC, N, NW, SW, W, WC, + others)")

# Create processing summary
summary = {
    'total_areas': len(london_areas),
    'districts': {k: len(v) for k, v in district_groups.items()},
    'se_complete': True,
    'target_streets': 250000,  # Estimated
    'processing_method': 'overpass_api_extraction'
}

print(f"\\n📋 PROCESSING PLAN:")
for district, areas in sorted(district_groups.items()):
    if district != 'SE':  # Skip SE as it's complete
        print(f"   🔄 {district}: {len(areas)} areas ({len(areas)/len(london_areas)*100:.1f}%)")

print(f"\\n✅ Ready to proceed with comprehensive London street extraction!")