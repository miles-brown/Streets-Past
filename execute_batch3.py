#!/usr/bin/env python3
import re

# Read the batch3_final.sql file
with open('/workspace/batch3_final.sql', 'r') as f:
    content = f.read()

# Extract the INSERT statement (skip the header and comments)
lines = content.strip().split('\n')

# Find the INSERT statement
insert_lines = []
in_insert = False
for line in lines:
    if line.strip().startswith('INSERT INTO'):
        in_insert = True
        insert_lines.append(line)
    elif in_insert and line.strip() == 'ON CONFLICT (postal_district) DO NOTHING;':
        insert_lines.append(line)
        break
    elif in_insert:
        insert_lines.append(line)

# Join all lines into one SQL statement
sql_statement = ' '.join(insert_lines)

print(f"Total SQL statement length: {len(sql_statement)} characters")
print("First 200 characters:")
print(sql_statement[:200])
print("...")
print("Last 100 characters:")
print(sql_statement[-100:])

# Count the number of records
values_match = re.findall(r"\('.*?'\)", sql_statement)
print(f"Number of value tuples found: {len(values_match)}")

# Execute the SQL using curl (since we don't have direct DB access)
import subprocess
import os

# Set up Supabase credentials
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

# Execute via REST API
headers = {
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'apikey': SUPABASE_KEY
}

# For large SQL, we'll execute smaller chunks
chunk_size = 50
values_tuples = re.findall(r"\('[^']*'\)", sql_statement)

# Reconstruct SQL with smaller chunks
for i in range(0, len(values_tuples), chunk_size):
    chunk = values_tuples[i:i + chunk_size]
    chunk_sql = f"INSERT INTO postal_districts (postal_area, postal_district, post_town, region, country) VALUES {', '.join(chunk)} ON CONFLICT (postal_district) DO NOTHING;"
    
    print(f"\nExecuting chunk {i//chunk_size + 1}: records {i+1} to {min(i+chunk_size, len(values_tuples))}")
    
    # For now, just print the chunk SQL
    print(f"Chunk SQL length: {len(chunk_sql)}")
    if i == 0:  # Only print the first chunk
        print("First 200 chars of chunk:")
        print(chunk_sql[:200])

print(f"\nTotal chunks to execute: {(len(values_tuples) + chunk_size - 1) // chunk_size}")