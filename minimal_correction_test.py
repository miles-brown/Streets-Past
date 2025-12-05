#!/usr/bin/env python3
"""
Minimal Test for Postal Code Correction
=======================================

Test the basic correction logic with just a few streets
"""

import os
import requests
import json
from datetime import datetime

def test_basic_correction():
    """Test basic correction with a few streets"""
    
    print('🧪 MINIMAL POSTAL CODE CORRECTION TEST')
    print('=' * 50)
    
    # Load environment
    with open('/workspace/.env', 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    print(f'✅ Environment loaded')
    print(f'🌐 Supabase: {supabase_url}')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # Test with a few specific streets from SE areas
    test_streets = [
        ('High Street', 'SE1'),
        ('Church Lane', 'SE5'),
        ('Victoria Road', 'SE10'),
        ('Main Street', 'SE15')
    ]
    
    print('\\n🔧 Testing corrections for sample streets:')
    
    success_count = 0
    error_count = 0
    
    for street_name, correct_postcode in test_streets:
        print(f'\\n   Testing {street_name} -> {correct_postcode}')
        
        try:
            # Find street
            get_url = f'{supabase_url}/rest/v1/streets?street_name=eq.{street_name}&select=id,postcode'
            get_response = requests.get(get_url, headers=headers)
            
            if get_response.status_code == 200:
                data = get_response.json()
                if data:
                    street_id = data[0]['id']
                    current_postcode = data[0].get('postcode', 'None')
                    print(f'     Found: Current postcode = {current_postcode}')
                    
                    # Update if needed
                    if current_postcode != correct_postcode:
                        update_url = f'{supabase_url}/rest/v1/streets?id=eq.{street_id}'
                        update_data = {
                            'postcode': correct_postcode,
                            'post_town': 'London'
                        }
                        
                        update_response = requests.patch(update_url, headers=headers, json=update_data)
                        
                        if update_response.status_code in [200, 204]:
                            print(f'     ✅ Updated successfully to {correct_postcode}')
                            success_count += 1
                        else:
                            print(f'     ❌ Update failed: {update_response.status_code}')
                            error_count += 1
                    else:
                        print(f'     ✅ Already correct ({correct_postcode})')
                else:
                    print(f'     ⚠️  Street not found in database')
                    error_count += 1
            else:
                print(f'     ❌ Find failed: {get_response.status_code}')
                error_count += 1
                
        except Exception as e:
            print(f'     ❌ Exception: {str(e)[:50]}')
            error_count += 1
    
    # Summary
    print('\\n' + '=' * 50)
    print(f'📊 Test Results:')
    print(f'   ✅ Successful corrections: {success_count}')
    print(f'   ❌ Errors: {error_count}')
    print(f'   📈 Test success rate: {success_count/(success_count+error_count)*100:.1f}%')
    
    if success_count > 0:
        print('\\n🎉 BASIC CORRECTION TEST PASSED!')
        print('💡 Ready to scale to full correction process.')
    else:
        print('\\n⚠️  Basic test failed - check errors above')
    
    return success_count, error_count

if __name__ == '__main__':
    test_basic_correction()