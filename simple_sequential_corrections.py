#!/usr/bin/env python3
"""
Simple Sequential Postal Code Correction
========================================

Process SE areas one by one with clear progress tracking
"""

import os
import requests
import json
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

def correct_single_street(supabase_url, supabase_key, street_name, area_code, street_data):
    """Correct a single street's postal code"""
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Find existing street
        get_url = f'{supabase_url}/rest/v1/streets?street_name=eq.{street_name}&select=id'
        get_response = requests.get(get_url, headers=headers)
        
        if get_response.status_code != 200:
            return False, f'GET failed ({get_response.status_code})'
        
        data = get_response.json()
        if not data:
            return False, 'Street not found'
        
        street_id = data[0]['id']
        
        # Update record
        update_url = f'{supabase_url}/rest/v1/streets?id=eq.{street_id}'
        update_data = {
            'postcode': area_code,
            'post_town': 'London',
            'latitude': street_data.get('latitude'),
            'longitude': street_data.get('longitude'),
            'current_status': 'Active',
            'verified_status': 'Verified'
        }
        
        update_response = requests.patch(update_url, headers=headers, json=update_data)
        
        if update_response.status_code in [200, 204]:
            return True, 'Success'
        else:
            return False, f'UPDATE failed ({update_response.status_code})'
            
    except Exception as e:
        return False, f'Exception: {str(e)[:50]}'

def main():
    """Main sequential processing"""
    
    print('🔄 SEQUENTIAL POSTAL CODE CORRECTION')
    print('=' * 50)
    
    # Load environment and data
    supabase_url, supabase_key = load_environment()
    
    with open('/workspace/data/accurate_se_streets.json', 'r') as f:
        accurate_data = json.load(f)
    
    print(f'📁 Loaded {len(accurate_data)} SE areas')
    print(f'📅 Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Process areas one by one
    total_processed = 0
    total_updated = 0
    total_errors = 0
    all_errors = []
    
    for area_code, streets in accurate_data.items():
        print(f'\\n🔧 Processing {area_code} ({len(streets)} streets)...')
        
        area_updated = 0
        area_errors = 0
        
        # Process each street
        for i, street in enumerate(streets):
            total_processed += 1
            street_name = street['name']
            
            # Update progress every 25 streets
            if (i + 1) % 25 == 0:
                print(f'   Progress: {i+1}/{len(streets)} (Total: {total_processed})')
            
            success, error = correct_single_street(supabase_url, supabase_key, street_name, area_code, street)
            
            if success:
                area_updated += 1
                total_updated += 1
            else:
                area_errors += 1
                total_errors += 1
                all_errors.append(f'{area_code}-{street_name}: {error}')
        
        print(f'   ✅ {area_code} complete: {area_updated} updated, {area_errors} errors')
    
    # Final summary
    total_streets = sum(len(streets) for streets in accurate_data.values())
    success_rate = (total_updated / total_streets * 100) if total_streets > 0 else 0
    
    print('\\n' + '=' * 50)
    print('📊 FINAL SUMMARY:')
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
        print('🎉 SUCCESS! Postal code corrections completed!')
    else:
        print('⚠️  No updates - check errors above')

if __name__ == '__main__':
    main()