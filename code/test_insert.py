#!/usr/bin/env python3

from supabase import create_client

url = "https://nadbmxfqknnnyuadhdtk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

supabase = create_client(url, key)

# Test 1: Get count
try:
    response = supabase.table('streets').select('id', count='exact').execute()
    print(f"Current count: {response.count}")
except Exception as e:
    print(f"Count error: {e}")

# Test 2: Insert one record
try:
    test_record = {
        'street_name': 'Oxford Street',
        'street_type': 'primary'
    }
    
    result = supabase.table('streets').insert(test_record).execute()
    print("✅ Test insert successful!")
    print(f"Inserted record: {result.data}")
    
except Exception as e:
    print(f"❌ Test insert failed: {e}")

# Test 3: Get count again
try:
    response = supabase.table('streets').select('id', count='exact').execute()
    print(f"New count: {response.count}")
except Exception as e:
    print(f"Second count error: {e}")

# Test 4: Get sample records
try:
    response = supabase.table('streets').select('*').limit(3).execute()
    print(f"Sample records:")
    for i, record in enumerate(response.data, 1):
        print(f"{i}. {record}")
        
except Exception as e:
    print(f"Sample error: {e}")