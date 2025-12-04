#!/usr/bin/env python3

import re

# Read the main SQL file
with open('/workspace/insert_districts_fixed.sql', 'r') as f:
    content = f.read()

# Find all INSERT statements
insert_pattern = r"INSERT INTO postal_districts.*?ON CONFLICT.*?DO NOTHING;"
inserts = re.findall(insert_pattern, content, re.DOTALL)

print(f"Found {len(inserts)} INSERT statements in the SQL file")

# Let's get the remaining INSERT statements starting from where we left off
# We need to continue from approximately where we've processed so far
# Current count is 911, target is 2997, so we need ~2086 more records

total_values = 0
remaining_inserts = []

for i, insert in enumerate(inserts):
    # Count values in this INSERT statement
    values = re.findall(r"\('.*?'\)", insert)
    total_values += len(values)
    
    # If we haven't reached close to 2997 records yet, include this insert
    if total_values < 2997:
        remaining_inserts.append(insert)
    else:
        break

print(f"Total values so far: {total_values}")
print(f"Remaining INSERT statements to process: {len(remaining_inserts)}")

# Process the remaining inserts in chunks
chunk_size = 1  # Process one INSERT statement at a time for reliability
processed_count = 0

for i in range(0, len(remaining_inserts), chunk_size):
    chunk = remaining_inserts[i:i + chunk_size]
    
    # Combine chunk into single SQL statement
    combined_sql = '\n'.join(chunk)
    
    # Count records in this chunk
    values = re.findall(r"\('.*?'\)", combined_sql)
    processed_count += len(values)
    
    print(f"Chunk {i//chunk_size + 1}: {len(values)} records (Total: {processed_count})")
    
    # For debugging, show first few records
    if i == 0:  # First chunk
        print("First chunk SQL:")
        print(combined_sql[:500])
        print("...")
        print(combined_sql[-200:])
    
    # Write chunk to file for manual execution
    filename = f"/workspace/remaining_chunk_{i//chunk_size + 1}.sql"
    with open(filename, 'w') as f:
        f.write(combined_sql)
    
    print(f"Saved chunk to {filename}")
    
    # Stop after a few chunks for now
    if i >= 2:  # Process first 3 chunks
        break

print(f"\nGenerated {min(3, len(remaining_inserts))} chunks for manual execution")