#!/usr/bin/env python3
"""
Minimal OSM Street Import Script
Only uses basic columns that are likely to exist
"""

import json
import csv
import logging
from datetime import datetime
from supabase import create_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinimalOSMImporter:
    def __init__(self):
        SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
        SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"
        
        self.supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        self.csv_file = "/workspace/data/osm_sample_uk_streets.csv"
    
    def get_existing_names(self):
        """Get existing street names to avoid duplicates"""
        try:
            response = self.supabase.table('streets').select('street_name').execute()
            existing = {record['street_name'].lower() for record in response.data}
            logger.info(f"Found {len(existing)} existing street names")
            return existing
        except Exception as e:
            logger.error(f"Error getting existing names: {e}")
            return set()
    
    def test_insert(self):
        """Test inserting a simple record"""
        test_record = {
            'street_name': 'Test Street',
            'street_type': 'residential',
            'source': 'OpenStreetMap Test'
        }
        
        try:
            response = self.supabase.table('streets').insert(test_record).execute()
            logger.info("Test insert successful!")
            return True
        except Exception as e:
            logger.error(f"Test insert failed: {e}")
            return False
    
    def minimal_import(self):
        """Try minimal import with only essential fields"""
        logger.info("Starting minimal import...")
        
        # Get existing names
        existing_names = self.get_existing_names()
        
        # Load CSV data
        streets = []
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    if i >= 100:  # Limit to first 100 for testing
                        break
                        
                    street_name = row.get('street_name', '').strip()
                    if not street_name or len(street_name) < 2:
                        continue
                    
                    # Check for duplicates
                    if street_name.lower() in existing_names:
                        continue
                    
                    # Create minimal record
                    street_record = {
                        'street_name': street_name,
                        'street_type': row.get('street_type', '').strip() or 'residential',
                        'source': 'OpenStreetMap'
                    }
                    
                    streets.append(street_record)
                    existing_names.add(street_name.lower())
                    
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return
        
        logger.info(f"Prepared {len(streets)} streets for import")
        
        # Try to insert in small batches
        batch_size = 10
        for i in range(0, len(streets), batch_size):
            batch = streets[i:i + batch_size]
            
            try:
                response = self.supabase.table('streets').insert(batch).execute()
                logger.info(f"Imported batch {i//batch_size + 1}: {len(batch)} streets")
                
            except Exception as e:
                logger.error(f"Batch {i//batch_size + 1} failed: {e}")
                continue
    
    def check_final_count(self):
        """Check how many records are now in the database"""
        try:
            response = self.supabase.table('streets').select('*', count='exact').execute()
            count = response.count if hasattr(response, 'count') else 0
            logger.info(f"Final database count: {count}")
            
            # Get some OSM records
            osm_response = self.supabase.table('streets').select('street_name', 'street_type', 'source').execute()
            osm_streets = [r for r in osm_response.data if r.get('source') == 'OpenStreetMap']
            logger.info(f"OSM streets imported: {len(osm_streets)}")
            
            # Show sample
            logger.info("Sample imported streets:")
            for i, street in enumerate(osm_streets[:10], 1):
                logger.info(f"  {i}. {street['street_name']} ({street['street_type']})")
                
        except Exception as e:
            logger.error(f"Error checking count: {e}")

def main():
    importer = MinimalOSMImporter()
    
    # Test basic insert first
    if not importer.test_insert():
        logger.error("Basic test failed!")
        return
    
    # Do minimal import
    importer.minimal_import()
    
    # Check results
    importer.check_final_count()

if __name__ == "__main__":
    main()