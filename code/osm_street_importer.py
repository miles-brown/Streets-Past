#!/usr/bin/env python3
"""
OSM Street Data Import Script
Imports extracted OpenStreetMap street data into Supabase database
"""

import json
import csv
import logging
from datetime import datetime
from supabase import create_client, Client
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OSMStreetImporter:
    """Import OpenStreetMap street data into Supabase"""
    
    def __init__(self):
        # Supabase configuration
        SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
        SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Data source
        self.csv_file = "/workspace/data/osm_sample_uk_streets.csv"
        self.json_file = "/workspace/data/osm_sample_uk_streets.json"
        
        # Import statistics
        self.stats = {
            'total_records': 0,
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'duplicates': 0
        }
    
    def load_existing_streets(self) -> set:
        """Load existing street names from database for duplicate detection"""
        logger.info("Loading existing streets from database...")
        
        try:
            response = self.supabase.table('streets').select('street_name').execute()
            existing_names = {record['street_name'].lower() for record in response.data}
            logger.info(f"Found {len(existing_names)} existing street names")
            return existing_names
        except Exception as e:
            logger.error(f"Failed to load existing streets: {e}")
            return set()
    
    def load_osm_data(self) -> list:
        """Load OSM street data from CSV file"""
        logger.info("Loading OSM street data...")
        
        streets = []
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    street_name = row.get('street_name', '').strip()
                    
                    if not street_name:
                        continue
                    
                    # Skip if too short or invalid
                    if len(street_name) < 2:
                        continue
                    
                    street_data = {
                        'street_name': street_name,
                        'street_type': row.get('street_type', '').strip(),
                        'latitude': float(row.get('latitude')) if row.get('latitude') and row.get('latitude') != '' else None,
                        'longitude': float(row.get('longitude')) if row.get('longitude') and row.get('longitude') != '' else None,
                        'osm_id': int(row.get('osm_id')) if row.get('osm_id') else None,
                        'created_at': datetime.now().isoformat(),
                        'source': 'OpenStreetMap'
                    }
                    
                    streets.append(street_data)
            
            self.stats['total_records'] = len(streets)
            logger.info(f"Loaded {len(streets)} streets from OSM data")
            return streets
            
        except Exception as e:
            logger.error(f"Failed to load OSM data: {e}")
            return []
    
    def clean_street_data(self, street: dict) -> dict:
        """Clean and validate street data for database"""
        cleaned = {}
        
        # Clean street name
        street_name = street.get('street_name', '').strip()
        if len(street_name) < 2:
            return None
        
        cleaned['street_name'] = street_name
        
        # Street type mapping
        street_type = street.get('street_type', '').lower()
        if street_type in ['residential', 'unclassified', 'tertiary', 'secondary', 'primary', 'trunk']:
            cleaned['street_type'] = street_type
        elif street_type == 'motorway':
            cleaned['street_type'] = 'motorway' 
        elif street_type == 'living_street':
            cleaned['street_type'] = 'living_street'
        elif street_type == 'service':
            cleaned['street_type'] = 'service'
        else:
            cleaned['street_type'] = 'road'  # Default
        
        # Coordinates
        cleaned['latitude'] = street.get('latitude')
        cleaned['longitude'] = street.get('longitude')
        
        # Additional metadata
        cleaned['osm_id'] = street.get('osm_id')
        cleaned['source'] = street.get('source', 'OpenStreetMap')
        cleaned['created_at'] = street.get('created_at', datetime.now().isoformat())
        
        # Default values for missing fields (to match database schema)
        cleaned['postcode'] = None
        cleaned['county'] = 'United Kingdom'  # Default county for OSM data
        cleaned['local_authority_area'] = None
        cleaned['post_town'] = None
        cleaned['historical_context'] = None
        cleaned['etymology'] = None
        cleaned['origin_language'] = None
        cleaned['meaning'] = None
        cleaned['historical_period'] = None
        cleaned['notable_people'] = None
        cleaned['historical_events'] = None
        cleaned['related_streets'] = None
        cleaned['external_references'] = None
        cleaned['last_updated'] = datetime.now().isoformat()
        
        return cleaned
    
    def batch_import_streets(self, streets: list, existing_names: set, batch_size: int = 500):
        """Import streets in batches"""
        logger.info(f"Starting import of {len(streets)} streets...")
        
        # Process in batches
        for i in range(0, len(streets), batch_size):
            batch = streets[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(streets) + batch_size - 1)//batch_size} ({len(batch)} streets)")
            
            # Clean and filter the batch
            cleaned_batch = []
            skipped_count = 0
            
            for street in batch:
                cleaned = self.clean_street_data(street)
                if not cleaned:
                    skipped_count += 1
                    continue
                
                # Check for duplicates (case insensitive)
                if cleaned['street_name'].lower() in existing_names:
                    self.stats['duplicates'] += 1
                    skipped_count += 1
                    continue
                
                cleaned_batch.append(cleaned)
            
            if not cleaned_batch:
                logger.info(f"Batch {i//batch_size + 1}: No valid streets to import (skipped {skipped_count})")
                self.stats['skipped'] += skipped_count
                continue
            
            try:
                # Insert batch
                result = self.supabase.table('streets').insert(cleaned_batch).execute()
                
                imported_count = len(cleaned_batch)
                self.stats['imported'] += imported_count
                self.stats['skipped'] += skipped_count
                
                logger.info(f"Batch {i//batch_size + 1}: Imported {imported_count} streets, skipped {skipped_count}")
                
                # Add imported names to existing set to avoid duplicates in next batches
                for street in cleaned_batch:
                    existing_names.add(street['street_name'].lower())
                
            except Exception as e:
                self.stats['errors'] += len(cleaned_batch) + skipped_count
                logger.error(f"Batch {i//batch_size + 1} failed: {e}")
                continue
        
        logger.info(f"Import complete! Summary:")
        logger.info(f"  Total processed: {self.stats['total_records']}")
        logger.info(f"  Successfully imported: {self.stats['imported']}")
        logger.info(f"  Skipped (invalid/duplicates): {self.stats['skipped']}")
        logger.info(f"  Errors: {self.stats['errors']}")
    
    def verify_import(self):
        """Verify the import by checking database"""
        try:
            response = self.supabase.table('streets').select('street_name', 'source').execute()
            
            osm_streets = [record for record in response.data if record.get('source') == 'OpenStreetMap']
            total_streets = len(response.data)
            
            logger.info(f"=== VERIFICATION RESULTS ===")
            logger.info(f"Total streets in database: {total_streets}")
            logger.info(f"OSM streets imported: {len(osm_streets)}")
            logger.info(f"Original manual streets: {total_streets - len(osm_streets)}")
            
            # Show sample OSM streets
            logger.info(f"\nSample imported OSM streets:")
            for i, street in enumerate(osm_streets[:10], 1):
                logger.info(f"{i:2d}. {street['street_name']}")
            
            return len(osm_streets) > 0
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False

def main():
    """Main import function"""
    logger.info("=== OSM Street Data Import Starting ===")
    
    importer = OSMStreetImporter()
    
    try:
        # Load existing streets to avoid duplicates
        existing_names = importer.load_existing_streets()
        
        # Load OSM data
        osm_streets = importer.load_osm_data()
        
        if not osm_streets:
            logger.error("No OSM street data found!")
            return
        
        # Start import
        logger.info(f"Starting import of {len(osm_streets)} streets...")
        importer.batch_import_streets(osm_streets, existing_names)
        
        # Verify import
        logger.info("\nVerifying import...")
        success = importer.verify_import()
        
        if success:
            logger.info("✅ Import completed successfully!")
        else:
            logger.error("❌ Import verification failed!")
    
    except Exception as e:
        logger.error(f"Import failed with error: {e}")

if __name__ == "__main__":
    main()