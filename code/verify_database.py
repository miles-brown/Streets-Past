#!/usr/bin/env python3

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def get_street_count():
    """Get total count of streets in database"""
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Prefer": "count=exact"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        count_header = response.headers.get('content-range', '')
        if '/' in count_header:
            total = count_header.split('/')[-1]
            print(f"📊 Total streets in database: {total}")
            return int(total)
        else:
            print(f"📊 Database response: {response.status_code}")
            return 0
    else:
        print(f"❌ Error getting count: {response.status_code}")
        return 0

def get_se3_streets(limit=20):
    """Get sample of SE3 streets"""
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }
    
    params = {
        "postcode": "eq.SE3",
        "limit": limit
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        streets = response.json()
        print(f"\n🏠 Sample SE3 Streets ({len(streets)} shown):")
        print("=" * 60)
        for i, street in enumerate(streets, 1):
            print(f"{i:2d}. {street.get('name', 'N/A')} - {street.get('city', 'N/A')} - {street.get('postcode', 'N/A')}")
        return streets
    else:
        print(f"❌ Error getting SE3 streets: {response.status_code}")
        return []

def get_area_distribution():
    """Get distribution of streets across SE areas"""
    areas = ['SE1', 'SE3', 'SE4', 'SE8', 'SE9', 'SE10', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18']
    
    print(f"\n📈 Street Distribution by SE Area:")
    print("=" * 40)
    
    for area in areas:
        url = f"{SUPABASE_URL}/rest/v1/streets"
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Prefer": "count=exact"
        }
        
        params = {"postcode": f"eq.{area}"}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            count_header = response.headers.get('content-range', '')
            if '/' in count_header:
                count = count_header.split('/')[-1]
                print(f"{area}: {count:>5} streets")
            else:
                print(f"{area}: ERROR")
        else:
            print(f"{area}: ERROR ({response.status_code})")

def main():
    print("🔍 Database Verification Report")
    print("=" * 50)
    
    # Get total count
    total_count = get_street_count()
    
    # Get area distribution
    get_area_distribution()
    
    # Get SE3 sample
    se3_streets = get_se3_streets()
    
    print(f"\n📋 Summary:")
    print(f"   Total database entries: {total_count}")
    print(f"   Expected (accurate data): 15,339")
    print(f"   Difference: {total_count - 15339}")
    
    if total_count > 15339:
        print("⚠️  WARNING: Database contains more than expected - likely has old/corrupted data mixed in")
    elif total_count < 15339:
        print("⚠️  WARNING: Database contains fewer than expected - some data may be missing")
    else:
        print("✅ Database count matches expected accurate data")

if __name__ == "__main__":
    main()