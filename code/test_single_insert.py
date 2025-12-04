#!/usr/bin/env python3
"""
Single record test to identify exact required fields
"""
import requests
from datetime import datetime

def test_single_insert():
    """Test inserting a single record to identify required fields"""
    
    headers = {
        'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo',
        'Content-Type': 'application/json'
    }
    
    print("Testing single record insertion...")
    
    # Test 1: Minimal fields (street_name only)
    test1 = {
        'street_name': 'Test Street 1'
    }
    
    try:
        response = requests.post(
            "https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/streets",
            headers=headers,
            json=test1
        )
        print(f"Test 1 (street_name only): {response.status_code}")
        if response.status_code != 201:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Test 1 exception: {e}")
    
    # Test 2: Include county field
    test2 = {
        'street_name': 'Test Street 2',
        'county': 'United Kingdom'
    }
    
    try:
        response = requests.post(
            "https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/streets",
            headers=headers,
            json=test2
        )
        print(f"Test 2 (street_name + county): {response.status_code}")
        if response.status_code != 201:
            print(f"  Error: {response.text}")
        else:
            print("  ✅ SUCCESS! This combination works!")
    except Exception as e:
        print(f"Test 2 exception: {e}")
    
    # Test 3: Get current count
    try:
        response = requests.get(
            "https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/streets?select=street_name",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"\nCurrent database count: {len(data)} streets")
    except Exception as e:
        print(f"Count check exception: {e}")

if __name__ == "__main__":
    test_single_insert()