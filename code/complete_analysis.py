#!/usr/bin/env python3

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def get_all_streets():
    """Get all streets from database"""
    url = f"{SUPABASE_URL}/rest/v1/streets"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }
    
    all_streets = []
    offset = 0
    limit = 1000
    
    print("📥 Fetching all streets from database...")
    
    while True:
        params = {
            "offset": offset,
            "limit": limit,
            "select": "id,name,postcode,city"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            batch = response.json()
            if not batch:
                break
            
            all_streets.extend(batch)
            offset += limit
            
            print(f"   Fetched {len(all_streets)} streets...", end='\r')
            
            if len(batch) < limit:
                break
        else:
            print(f"❌ Error: {response.status_code}")
            break
    
    print(f"\n✅ Total streets fetched: {len(all_streets)}")
    return all_streets

def analyze_geographic_consistency(streets):
    """Analyze which streets might need postcode corrections"""
    
    # London area indicators that should be in specific postcodes
    area_indicators = {
        'Wimbledon': ['SE1', 'SE3', 'SE4', 'SE5', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18'],
        'Clapham': ['SE1', 'SE3', 'SE4', 'SE5', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18'],
        'Putney': ['SE1', 'SE3', 'SE4', 'SE5', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18'],
        'Chelsea': ['SE1', 'SE3', 'SE4', 'SE5', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18'],
        'Highgate': ['SE1', 'SE3', 'SE4', 'SE5', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18'],
        'Islington': ['SE1', 'SE3', 'SE4', 'SE5', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18'],
        'Hackney': ['SE1', 'SE3', 'SE4', 'SE5', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18'],
        'Camden': ['SE1', 'SE3', 'SE4', 'SE5', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18'],
        'Westminster': ['SE1', 'SE3', 'SE4', 'SE5', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18'],
        'Kensington': ['SE1', 'SE3', 'SE4', 'SE5', 'SE8', 'SE9', 'SE11', 'SE12', 'SE13', 'SE14', 'SE15', 'SE16', 'SE17', 'SE18']
    }
    
    # Proper postcode for each area
    area_postcodes = {
        'Wimbledon': 'SW19',
        'Clapham': 'SW4',
        'Putney': 'SW15',
        'Chelsea': 'SW3',
        'Highgate': 'N6',
        'Islington': 'N1',
        'Hackney': 'E8',
        'Camden': 'NW1',
        'Westminster': 'SW1',
        'Kensington': 'SW5'
    }
    
    problematic_streets = []
    
    print("\n🔍 Analyzing geographic consistency...")
    
    for street in streets:
        name = street.get('name', '').lower()
        postcode = street.get('postcode', '')
        city = street.get('city', '')
        
        # Check if this street contains area indicators
        for area, indicators in area_indicators.items():
            if area.lower() in name:
                if postcode not in [f'eq.{area_postcodes[area]}']:
                    problematic_streets.append({
                        'id': street.get('id'),
                        'name': street.get('name'),
                        'current_postcode': postcode,
                        'area': area,
                        'should_be_postcode': area_postcodes[area],
                        'city': city
                    })
    
    return problematic_streets

def main():
    print("🧹 Complete Database Analysis")
    print("=" * 50)
    
    # Get all streets
    all_streets = get_all_streets()
    
    # Analyze for geographic issues
    problematic = analyze_geographic_consistency(all_streets)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Total streets in database: {len(all_streets)}")
    print(f"   Expected accurate streets: 15,339")
    print(f"   Difference: {len(all_streets) - 15339}")
    print(f"   Streets needing postcode correction: {len(problematic)}")
    
    if problematic:
        print(f"\n⚠️  Streets that need postcode correction:")
        print("-" * 60)
        for street in problematic[:10]:  # Show first 10
            print(f"   {street['name']} ({street['current_postcode']} -> {street['should_be_postcode']})")
        
        if len(problematic) > 10:
            print(f"   ... and {len(problematic) - 10} more")
    
    # Save analysis to file
    with open('/workspace/database_analysis.txt', 'w') as f:
        f.write(f"Database Analysis Report\n")
        f.write(f"========================\n\n")
        f.write(f"Total streets in database: {len(all_streets)}\n")
        f.write(f"Expected accurate streets: 15,339\n")
        f.write(f"Excess streets: {len(all_streets) - 15339}\n")
        f.write(f"Streets needing postcode correction: {len(problematic)}\n\n")
        
        if problematic:
            f.write("Streets needing postcode correction:\n")
            f.write("-" * 40 + "\n")
            for street in problematic:
                f.write(f"{street['name']} ({street['current_postcode']} -> {street['should_be_postcode']})\n")
    
    print(f"\n✅ Analysis saved to database_analysis.txt")

if __name__ == "__main__":
    main()