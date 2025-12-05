#!/usr/bin/env python3
"""
Supabase Database Read-Only Diagnostics
This script examines the database structure without performing any write operations.
"""
import json
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def main():
    print("=== Supabase Database Read-Only Diagnostics ===\n")
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("✓ Supabase client initialized successfully")
        
        # Step 1: Try to find the streets table
        print("\n1. Looking for streets table...")
        
        # Try common table names
        possible_table_names = ['streets', 'london_streets', 'postcodes', 'se_streets']
        found_table = None
        
        for table_name in possible_table_names:
            try:
                print(f"   Testing table: {table_name}")
                result = supabase.table(table_name).select("*").limit(1).execute()
                print(f"   ✓ Table '{table_name}' found and accessible")
                found_table = table_name
                break
            except Exception as e:
                print(f"   ✗ Table '{table_name}' not found: {str(e)}")
                continue
        
        if not found_table:
            print("\n❌ No accessible streets table found!")
            # Let's try to see what tables exist by making a raw query
            print("\n   Attempting to query table schema...")
            try:
                # This will fail but might show us available tables
                result = supabase.table("information_schema.tables").select("*").eq("table_schema", "public").execute()
                print("   Table listing successful!")
                if result.data:
                    table_names = [t['table_name'] for t in result.data]
                    print(f"   Available tables: {table_names}")
                else:
                    print("   No tables found in public schema")
            except Exception as e:
                print(f"   Schema query failed: {str(e)}")
            return
        
        print(f"\n2. Examining table structure for '{found_table}'...")
        
        # Step 2: Get table schema information
        try:
            # Try to get schema information
            schema_result = supabase.table("information_schema.columns").select("*").eq("table_name", found_table).eq("table_schema", "public").execute()
            
            if schema_result.data:
                print("   ✓ Column schema retrieved successfully:")
                for col in schema_result.data:
                    print(f"     - {col['column_name']}: {col['data_type']}")
                    if col.get('is_nullable') == 'NO':
                        print(f"       (NOT NULL)")
                    if col.get('column_default'):
                        print(f"       (DEFAULT: {col['column_default']})")
            else:
                print("   ❌ No schema information available")
        except Exception as e:
            print(f"   ❌ Schema query failed: {str(e)}")
            print("   Let's try to infer structure from sample data...")
        
        # Step 3: Get record count
        print(f"\n3. Counting records in '{found_table}'...")
        try:
            # Count records
            count_result = supabase.table(found_table).select("id", count="exact").execute()
            if hasattr(count_result, 'count') and count_result.count is not None:
                record_count = count_result.count
                print(f"   ✓ Found {record_count} records in the table")
            else:
                print("   ❌ Could not get exact count")
                
                # Try alternative counting method
                count_result = supabase.table(found_table).select("*").execute()
                if count_result.data:
                    print(f"   ✓ Table contains {len(count_result.data)} records (based on sample query)")
                else:
                    print("   ❌ No records found or error occurred")
        except Exception as e:
            print(f"   ❌ Count query failed: {str(e)}")
        
        # Step 4: Get sample records to understand data structure
        print(f"\n4. Getting sample records from '{found_table}'...")
        try:
            sample_result = supabase.table(found_table).select("*").limit(5).execute()
            if sample_result.data:
                print(f"   ✓ Successfully retrieved {len(sample_result.data)} sample records:")
                print("\n   Sample Data Structure:")
                for i, record in enumerate(sample_result.data, 1):
                    print(f"   Record {i}:")
                    for key, value in record.items():
                        if isinstance(value, str) and len(value) > 50:
                            print(f"     {key}: {value[:47]}...")
                        else:
                            print(f"     {key}: {value}")
                    print()
            else:
                print("   ❌ No sample records available")
        except Exception as e:
            print(f"   ❌ Sample query failed: {str(e)}")
        
        print("\n=== Diagnostics Complete ===")
        print("Now we understand the database structure and can fix the write operations!")
        
    except Exception as e:
        print(f"\n❌ Critical error during diagnostics: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()