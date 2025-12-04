#!/usr/bin/env python3
"""
Quick analysis of OS Open Names data to understand feature types
"""

import pandas as pd
import glob

def analyze_feature_types():
    """Analyze feature types in the OS Open Names data"""
    
    data_dir = "/workspace/data/Data"
    csv_files = glob.glob(f"{data_dir}/*.csv")
    
    print(f"Analyzing {len(csv_files)} CSV files...")
    
    # Analyze first few files to understand data structure
    local_types = {}
    feature_types = {}
    sample_data = []
    
    for i, csv_file in enumerate(csv_files[:10]):  # Check first 10 files
        print(f"Analyzing file {i+1}: {csv_file}")
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)
            
            # Count LOCAL_TYPE values
            if 'LOCAL_TYPE' in df.columns:
                local_counts = df['LOCAL_TYPE'].value_counts()
                for local_type, count in local_counts.items():
                    if local_type and pd.notna(local_type):
                        local_types[local_type] = local_types.get(local_type, 0) + count
            
            # Count TYPE values  
            if 'TYPE' in df.columns:
                type_counts = df['TYPE'].value_counts()
                for feature_type, count in type_counts.items():
                    if feature_type and pd.notna(feature_type):
                        feature_types[feature_type] = feature_types.get(feature_type, 0) + count
            
            # Collect sample records
            if len(sample_data) < 20:
                for _, row in df.head(2).iterrows():
                    sample_data.append({
                        'NAME1': row.get('NAME1', ''),
                        'LOCAL_TYPE': row.get('LOCAL_TYPE', ''),
                        'TYPE': row.get('TYPE', ''),
                        'POPULATED_PLACE': row.get('POPULATED_PLACE', '')
                    })
                    
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
    
    print("\n" + "="*50)
    print("MOST COMMON LOCAL_TYPES:")
    print("="*50)
    for local_type, count in sorted(local_types.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"{local_type}: {count:,}")
    
    print("\n" + "="*50)
    print("MOST COMMON TYPE values:")
    print("="*50)
    for feature_type, count in sorted(feature_types.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"{feature_type}: {count:,}")
    
    print("\n" + "="*50)
    print("SAMPLE DATA:")
    print("="*50)
    for i, sample in enumerate(sample_data[:10]):
        print(f"{i+1}. {sample['NAME1']} ({sample['LOCAL_TYPE']}) - {sample['POPULATED_PLACE']}")

if __name__ == "__main__":
    analyze_feature_types()
