#!/usr/bin/env python3

import json

try:
    with open('/workspace/data/accurate_se_streets.json', 'r') as f:
        data = json.load(f)
    
    total = 0
    area_stats = {}
    
    with open('/workspace/accurate_data_analysis.txt', 'w') as out:
        out.write("SE London Accurate Data Analysis\n")
        out.write("=" * 40 + "\n\n")
        
        for area in sorted(data.keys()):
            count = len(data[area])
            total += count
            area_stats[area] = count
            out.write(f"{area}: {count} streets\n")
        
        out.write(f"\nTotal accurate streets: {total}\n")
        
        # Check SE3 specifically
        if 'SE3' in data:
            out.write(f"\nSE3 Streets Sample (first 10):\n")
            out.write("-" * 30 + "\n")
            for i, street in enumerate(data['SE3'][:10], 1):
                name = street.get('name', 'N/A')
                out.write(f"{i:2d}. {name}\n")
            out.write(f"\nTotal SE3 streets: {len(data['SE3'])}\n")
        else:
            out.write("\nSE3 not found in data\n")
    
    print(f"Analysis complete. Total: {total} streets")
    
except Exception as e:
    print(f"Error: {e}")
