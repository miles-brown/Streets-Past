#!/usr/bin/env python3

import json

def count_accurate_streets():
    """Count streets in accurate_se_streets.json"""
    try:
        with open('/workspace/data/accurate_se_streets.json', 'r') as f:
            data = json.load(f)
        
        total_streets = 0
        area_counts = {}
        
        print("📊 Accurate SE Streets Data Analysis")
        print("=" * 50)
        
        for area, streets in data.items():
            count = len(streets)
            total_streets += count
            area_counts[area] = count
            print(f"{area}: {count:>4} streets")
        
        print(f"\n📈 Total: {total_streets} streets")
        print(f"📈 Area count: {len(data)} areas")
        
        # Check SE3 specifically
        if 'SE3' in data:
            print(f"\n🏠 SE3 Sample Streets (showing first 10):")
            print("-" * 50)
            for i, street in enumerate(data['SE3'][:10], 1):
                name = street.get('name', 'N/A')
                street_type = street.get('type', 'N/A')
                lat = street.get('latitude', 'N/A')
                lon = street.get('longitude', 'N/A')
                print(f"{i:2d}. {name} ({street_type}) - {lat}, {lon}")
            
            print(f"\n✅ SE3 has {len(data['SE3'])} streets")
        else:
            print("\n❌ SE3 not found in data")
        
        return total_streets, area_counts
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return 0, {}

if __name__ == "__main__":
    count_accurate_streets()