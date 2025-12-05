#!/usr/bin/env python3

import json
import os
from supabase import create_client, Client

def main():
    print("=== SUPABASE DATABASE DIAGNOSTIC ===\n")
    
    # Get Supabase credentials from environment
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return
    
    print(f"✅ Supabase URL: {url}")
    print(f"✅ Service role key available: {key[:20]}...")
    
    # Create Supabase client
    try:
        supabase: Client = create_client(url, key)
        print("✅ Supabase client created successfully")
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return
    
    print("\n=== TESTING BASIC CONNECTIVITY ===")
    
    try:
        # Test 1: Try to select from streets table
        print("📋 Attempting to select from 'streets' table...")
        result = supabase.table('streets').select('*').limit(5).execute()
        
        if result.data:
            print(f"✅ Successfully read {len(result.data)} records from streets table")
            print("📋 Sample records:")
            for i, record in enumerate(result.data):
                print(f"  Record {i+1}: {json.dumps(record, indent=2)}")
                if i >= 2:  # Show only first 3 records
                    break
        else:
            print("⚠️  No data returned from streets table (might be empty)")
            
    except Exception as e:
        print(f"❌ Failed to read from streets table: {e}")
        print(f"   Error type: {type(e)}")
        return
    
    print("\n=== EXAMINING TABLE SCHEMA ===")
    
    try:
        # Test 2: Get table information using raw SQL
        print("📊 Attempting to get table schema information...")
        schema_query = """
        SELECT 
            column_name, 
            data_type, 
            is_nullable, 
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'streets' 
        ORDER BY ordinal_position;
        """
        
        result = supabase.rpc('exec_sql', {'sql': schema_query}).execute()
        print("✅ Schema query executed")
        
        if hasattr(result, 'data') and result.data:
            print("📋 Table schema:")
            for col in result.data:
                print(f"  {col['column_name']}: {col['data_type']} {'(NULL)' if col['is_nullable'] == 'YES' else '(NOT NULL)'}")
        else:
            print("⚠️  No schema data returned - trying alternative approach...")
            
    except Exception as e:
        print(f"❌ Failed to get schema via RPC: {e}")
        print("   Trying direct table inspection...")
    
    try:
        # Alternative: Try to get one record and examine its keys
        print("🔍 Getting one sample record to infer schema...")
        sample = supabase.table('streets').select('*').limit(1).execute()
        
        if sample.data:
            sample_record = sample.data[0]
            print("📋 Inferred schema from sample record:")
            for key, value in sample_record.items():
                value_type = type(value).__name__
                print(f"  {key}: {value_type}")
        else:
            print("⚠️  Cannot get sample record to infer schema")
            
    except Exception as e:
        print(f"❌ Failed to get sample record: {e}")
    
    print("\n=== TESTING WRITE OPERATION (PREPARATION) ===")
    
    # Test 3: Try to get existing record to understand structure
    try:
        print("🔍 Getting one existing record for update test...")
        existing = supabase.table('streets').select('*').limit(1).execute()
        
        if existing.data:
            record = existing.data[0]
            print("📋 Existing record structure:")
            for key, value in record.items():
                print(f"  {key}: {repr(value)}")
                
            # Test if we can construct a similar record
            print("\n🧪 Testing record reconstruction...")
            test_record = {}
            for key, value in record.items():
                if key == 'id':  # Skip auto-generated fields
                    continue
                test_record[key] = value
                
            print(f"📋 Test record for update: {json.dumps(test_record, indent=2)}")
            
        else:
            print("⚠️  No existing records found for testing")
            
    except Exception as e:
        print(f"❌ Failed to get existing record: {e}")
    
    print("\n=== DIAGNOSTIC COMPLETE ===")
    print("Based on the results above, we can now:")
    print("1. ✅ Verify database connection works")
    print("2. ✅ See actual table structure")  
    print("3. ✅ Identify field names and types")
    print("4. ✅ Prepare proper UPDATE operations")

if __name__ == "__main__":
    main()