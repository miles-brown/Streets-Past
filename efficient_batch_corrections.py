#!/usr/bin/env python3
"""
Efficient Batch Postal Code Correction
======================================

Process SE areas in parallel batches for maximum efficiency
"""

import os
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def load_environment():
    """Load environment variables"""
    with open('/workspace/.env', 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value
    return os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

def correct_area_batch(area_code, streets, supabase_url, supabase_key):
    """Correct postal codes for a single SE area"""
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    updated_count = 0
    error_count = 0
    errors = []
    
    print(f'🔧 Processing {area_code} ({len(streets)} streets)...')
    
    for i, street in enumerate(streets):
        try:
            street_name = street['name']
            
            # Find existing street
            get_url = f'{supabase_url}/rest/v1/streets?street_name=eq.{street_name}&select=id'
            get_response = requests.get(get_url, headers=headers)
            
            if get_response.status_code != 200:
                error_count += 1
                errors.append(f'{street_name}: GET failed ({get_response.status_code})')
                continue
            
            data = get_response.json()
            if not data:
                continue  # Street doesn't exist
            
            street_id = data[0]['id']
            
            # Update record
            update_url = f'{supabase_url}/rest/v1/streets?id=eq.{street_id}'
            update_data = {
                'postcode': area_code,
                'post_town': 'London',
                'latitude': street.get('latitude'),
                'longitude': street.get('longitude'),
                'current_status': 'Active',
                'verified_status': 'Verified'
            }
            
            update_response = requests.patch(update_url, headers=headers, json=update_data)
            
            if update_response.status_code in [200, 204]:
                updated_count += 1
            else:
                error_count += 1
                errors.append(f'{street_name}: UPDATE failed ({update_response.status_code})')
            
            # Progress update every 50 streets
            if (i + 1) % 50 == 0:
                print(f'   Progress: {i+1}/{len(streets)} ({updated_count} updated)')
            
        except Exception as e:
            error_count += 1
            errors.append(f'{street_name}: Exception {str(e)[:30]}')
    
    result = {
        'area': area_code,
        'total': len(streets),
        'updated': updated_count,
        'errors': error_count,
        'error_details': errors
    }
    
    print(f'   ✅ {area_code} complete: {updated_count} updated, {error_count} errors')
    return result

def main():
    """Main execution with parallel processing"""
    
    print('🚀 EFFICIENT PARALLEL POSTAL CODE CORRECTION')
    print('=' * 60)
    
    # Load environment and data
    supabase_url, supabase_key = load_environment()
    
    with open('/workspace/data/accurate_se_streets.json', 'r') as f:
        accurate_data = json.load(f)
    
    print(f'📁 Loaded {len(accurate_data)} SE areas')
    print(f'📅 Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Process areas in batches of 3 for efficiency
    area_items = list(accurate_data.items())
    batch_size = 3
    total_updated = 0
    total_errors = 0
    all_errors = []
    
    for batch_start in range(0, len(area_items), batch_size):
        batch_end = min(batch_start + batch_size, len(area_items))
        batch = area_items[batch_start:batch_end]
        
        print(f'\\n📦 Processing batch {batch_start//batch_size + 1}: {[area for area, _ in batch]}')
        
        # Process batch in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(correct_area_batch, area, streets, supabase_url, supabase_key)
                for area, streets in batch
            ]
            
            batch_results = []
            for future in as_completed(futures):
                result = future.result()
                batch_results.append(result)
                total_updated += result['updated']
                total_errors += result['errors']
                all_errors.extend(result['error_details'])
        
        # Batch summary
        batch_updated = sum(r['updated'] for r in batch_results)
        batch_errors = sum(r['errors'] for r in batch_results)
        print(f'📊 Batch summary: {batch_updated} updated, {batch_errors} errors')
    
    # Final summary
    total_streets = sum(len(streets) for streets in accurate_data.values())
    success_rate = (total_updated / total_streets * 100) if total_streets > 0 else 0
    
    print('\\n' + '=' * 60)
    print('📊 FINAL RESULTS:')
    print(f'   📋 Total streets: {total_streets}')
    print(f'   ✅ Successfully updated: {total_updated}')
    print(f'   ❌ Errors: {total_errors}')
    print(f'   📈 Success rate: {success_rate:.1f}%')
    
    if all_errors:
        print(f'\\n🚨 Sample errors (first 10):')
        for error in all_errors[:10]:
            print(f'   {error}')
    
    print(f'\\n🎯 COMPLETED: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    if total_updated > 0:
        print('🎉 SUCCESS! Significant postal code corrections completed!')
    else:
        print('⚠️  No updates - check errors above')

if __name__ == '__main__':
    main()