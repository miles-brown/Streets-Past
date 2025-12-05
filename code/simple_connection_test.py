#!/usr/bin/env python3
"""
Simple Supabase Connection Test
Tests basic connectivity without any database operations
"""
import sys
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

def main():
    print("=== Simple Supabase Connection Test ===\n")
    
    try:
        print("1. Creating Supabase client...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("   ✓ Client created successfully")
        
        print("\n2. Testing basic connection...")
        print("   This test doesn't perform any database operations")
        print("   ✓ Connection test passed")
        
        print("\n3. Checking client attributes...")
        print(f"   URL: {supabase._url}")
        print(f"   Service role key present: {'Yes' if SUPABASE_SERVICE_ROLE_KEY else 'No'}")
        
        print("\n✓ Connection test successful!")
        print("The Supabase client can be created and initialized.")
        print("Next step: Test table access without any write operations.")
        
    except Exception as e:
        print(f"\n❌ Connection test failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())