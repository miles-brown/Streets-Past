#!/usr/bin/env python3

import re
import subprocess
import json

# Read the batch3_final.sql file
with open('/workspace/batch3_final.sql', 'r') as f:
    content = f.read()

# Extract all the value tuples
pattern = r"\('[^']*'\)"
matches = re.findall(pattern, content)

print(f"Found {len(matches)} records in batch 3")

# Group them into chunks of 50 records each
chunk_size = 50
chunks = []

for i in range(0, len(matches), chunk_size):
    chunk = matches[i:i + chunk_size]
    chunks.append(chunk)

print(f"Created {len(chunks)} chunks")

# Let's focus on processing chunks systematically
# Since we've already inserted some records, let's process the remaining

# Create a list of all the postal_districts we've already processed
processed_records = [
    'GL8', 'GL9', 'GL10', 'GL11', 'GL12', 'GL13', 'GL14', 'GL15', 'GL16', 'GL17',
    'GL18', 'GL19', 'GL20', 'GL50', 'GL51', 'GL52', 'GL53', 'GL54', 'GL55', 'GL56',
    'GU1', 'GU2', 'GU3', 'GU4', 'GU5', 'GU6', 'GU7', 'GU8', 'GU9', 'GU10',
    'GU11', 'GU12', 'GU13', 'GU14', 'GU15', 'GU16', 'GU17', 'GU18', 'GU19', 'GU20',
    'GU21', 'GU22', 'GU23', 'GU24', 'GU25', 'GU26', 'GU27', 'GU28', 'GU29', 'GU30',
    'GU31', 'GU32', 'GU33', 'GU34', 'GU35', 'GU46', 'GU47', 'GU51', 'GU52', 'GU95',
    'GY1', 'GY2', 'GY3', 'GY4', 'GY5', 'GY6', 'GY7', 'GY8', 'GY9', 'GY10',
    'HA0', 'HA1', 'HA2', 'HA3', 'HA4', 'HA5', 'HA6', 'HA7', 'HA8', 'HA9',
    'HD1', 'HD2'
]

print(f"Already processed {len(processed_records)} records")

# Find remaining records
remaining_records = []
for match in matches:
    # Extract the postal_district (second field)
    parts = match.split(', ')
    if len(parts) >= 2:
        district = parts[1].strip("'()")
        if district not in processed_records:
            remaining_records.append(match)

print(f"Remaining records to process: {len(remaining_records)}")

# Group remaining records into chunks
remaining_chunks = []
for i in range(0, len(remaining_records), chunk_size):
    chunk = remaining_records[i:i + chunk_size]
    remaining_chunks.append(chunk)

print(f"Remaining chunks to process: {len(remaining_chunks)}")

# Print the first chunk as an example
if remaining_chunks:
    first_chunk = remaining_chunks[0]
    print(f"\nFirst chunk contains {len(first_chunk)} records:")
    for record in first_chunk[:5]:  # Show first 5
        print(f"  {record}")
    if len(first_chunk) > 5:
        print(f"  ... and {len(first_chunk) - 5} more")

# Generate SQL for the first remaining chunk
if remaining_chunks:
    chunk_sql = f"INSERT INTO postal_districts (postal_area, postal_district, post_town, region, country) VALUES {', '.join(remaining_chunks[0])} ON CONFLICT (postal_district) DO NOTHING;"
    
    print(f"\nFirst chunk SQL length: {len(chunk_sql)}")
    print("First 200 characters:")
    print(chunk_sql[:200])
    print("...")
    print("Last 100 characters:")
    print(chunk_sql[-100:])

# Save the remaining records to a file for further processing
with open('/workspace/remaining_batch3_records.txt', 'w') as f:
    for chunk in remaining_chunks:
        for record in chunk:
            f.write(record + '\n')

print(f"\nSaved remaining records to /workspace/remaining_batch3_records.txt")