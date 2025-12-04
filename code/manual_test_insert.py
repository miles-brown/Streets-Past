import csv
import subprocess
import json

# Read first few street names from CSV
streets_to_add = []

try:
    with open('/workspace/data/osm_sample_uk_streets.csv', 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i < 5:  # Get first 5 streets
                street_name = row.get('street_name', '').strip()
                street_type = row.get('street_type', 'residential').strip()
                
                if street_name and len(street_name) > 2:
                    streets_to_add.append({
                        'street_name': street_name,
                        'street_type': street_type
                    })
                    print(f"Street {i+1}: {street_name} ({street_type})")
                    
    print(f"\nPrepared {len(streets_to_add)} streets for testing")
    
    # Try to insert first street using curl
    if streets_to_add:
        first_street = streets_to_add[0]
        print(f"\nTrying to insert: {first_street}")
        
        # Create JSON payload
        payload = json.dumps(first_street)
        print(f"Payload: {payload}")
        
        # Use curl to insert
        curl_cmd = [
            'curl', '-X', 'POST',
            'https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/streets',
            '-H', 'apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ4MjYxOTksImV4cCI6MjA4MDQwMjE5OX0.gI7-b8DxjBTMlRLqerkCKUP2DuGK2YVhEozYx-M7gGE',
            '-H', 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo',
            '-H', 'Content-Type: application/json',
            '-H', 'Prefer: return=representation',
            '-d', payload
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        print(f"Curl result: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()