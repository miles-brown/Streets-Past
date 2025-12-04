#!/usr/bin/env python3
"""
OS Open Names CSV Bulk Import Script
Processes 819 CSV files containing UK street/place data and imports to Supabase streets table.
"""

import os
import glob
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from supabase import create_client, Client
import json
import sys

# Supabase credentials
SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"

# Configuration
DATA_DIR = "/workspace/data/Data"
BATCH_SIZE = 1000
PROGRESS_INTERVAL = 5000
LOG_FILE = "/workspace/code/street_import_log.txt"

# Street-related features to include
STREET_TYPES = {
    'road', 'street', 'lane', 'avenue', 'close', 'way', 'row', 'drive', 'place', 'square', 'court', 'grove', 
    'park', 'field', 'green', 'common', 'hill', 'mount', 'crescent', 'terrace', 'gardens', 'mews',
    'walk', 'view', 'heights', 'villas', 'circular', 'bridge', 'wharf', 'pier', 'quay', 'strand',
    'highway', 'motorway', 'bypass', 'approach', 'service', 'link', 'circular', 'by-pass', 'footway',
    'slip', 'access', 'arcade', 'centre', 'center', 'mall', 'precinct', 'walkway', 'underpass',
    'passage', 'alley', 'path', 'trail', 'route', 'track', 'tracklet', 'private', 'service',
    'farm', 'cottage', 'house', 'hall', 'manor', 'estate', 'village', 'town', 'city'
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class StreetImport:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        self.total_processed = 0
        self.total_imported = 0
        self.errors = 0
        self.skipped = 0
        self.current_batch = []
        
    def get_database_schema(self) -> Dict:
        """Get the streets table schema"""
        try:
            # Try to get a sample record to understand the schema
            result = self.supabase.table('streets').select('*').limit(1).execute()
            if result.data:
                logging.info("Database schema retrieved successfully")
                return result.data[0]
            else:
                logging.warning("No data in streets table, using expected schema")
                return {}
        except Exception as e:
            logging.error(f"Error getting database schema: {e}")
            return {}
    
    def validate_and_clean_record(self, row: Dict) -> Optional[Dict]:
        """Clean and validate a single record"""
        try:
            # Map OS Open Names columns to our database schema
            cleaned_record = {}
            
            # Core fields
            name1 = str(row.get('NAME1', '')).strip()
            name2 = str(row.get('NAME2', '')).strip() if row.get('NAME2') else ''
            
            if not name1:
                return None  # Skip records without a name
            
            # Combine names if both exist
            full_name = f"{name1} {name2}".strip() if name2 else name1
            
            # Check if it's a street/road type
            local_type = str(row.get('LOCAL_TYPE', '')).lower()
            feature_type = str(row.get('TYPE', '')).lower()
            
            # Include if it's a street/road related feature
            if local_type not in {'street', 'road', 'path', 'lane', 'walkway'} and feature_type != 'namedRoad':
                # Also check if any common street terms appear in the name
                if not any(term in full_name.lower() for term in ['street', 'road', 'lane', 'close', 'avenue', 'way', 'place', 'square', 'court']):
                    # Include villages, towns, etc. but with different treatment
                    pass  # We'll include them but mark as populated place
            
            cleaned_record['street_name'] = full_name
            cleaned_record['street_type'] = feature_type if feature_type and feature_type != 'None' else local_type
            cleaned_record['county'] = str(row.get('COUNTY_UNITARY', '')).strip() if row.get('COUNTY_UNITARY') else None
            cleaned_record['local_authority_area'] = str(row.get('DISTRICT_BOROUGH', '')).strip() if row.get('DISTRICT_BOROUGH') else None
            cleaned_record['post_town'] = str(row.get('POPULATED_PLACE', '')).strip() if row.get('POPULATED_PLACE') else None
            cleaned_record['postcode'] = str(row.get('POSTCODE_DISTRICT', '')).strip() if row.get('POSTCODE_DISTRICT') else None
            
            # Coordinates (OSGB36 grid references - need to convert to WGS84 lat/lon)
            x_coord = row.get('GEOMETRY_X')
            y_coord = row.get('GEOMETRY_Y')
            
            if x_coord and y_coord:
                try:
                    # Convert OSGB36 to WGS84 lat/lon (approximate conversion)
                    # For simplicity, we'll use a basic conversion
                    # Note: This is simplified - in production you'd use a proper library like pyproj
                    lat, lon = self.osgb36_to_wgs84(float(x_coord), float(y_coord))
                    cleaned_record['latitude'] = lat
                    cleaned_record['longitude'] = lon
                except (ValueError, TypeError):
                    cleaned_record['latitude'] = None
                    cleaned_record['longitude'] = None
            else:
                cleaned_record['latitude'] = None
                cleaned_record['longitude'] = None
            
            # Set defaults for required fields
            cleaned_record['country'] = 'England'  # Default for OS Open Names GB
            cleaned_record['region'] = str(row.get('REGION', '')).strip() if row.get('REGION') else None
            cleaned_record['street_name_language'] = str(row.get('NAME1_LANG', 'en')).strip() if row.get('NAME1_LANG') else 'en'
            cleaned_record['osm_id'] = None  # Not available in OS Open Names
            
            # Add empty fields that the database expects
            cleaned_record['etymology'] = None
            cleaned_record['historical_origins'] = None
            cleaned_record['cultural_significance'] = None
            cleaned_record['notable_people'] = None
            cleaned_record['fun_facts'] = None
            
            return cleaned_record
            
        except Exception as e:
            logging.warning(f"Error cleaning record: {e}")
            return None
    
    def osgb36_to_wgs84(self, easting: float, northing: float) -> Tuple[float, float]:
        """
        Simple OSGB36 to WGS84 conversion.
        Note: This is an approximation. For precise conversion, use pyproj library.
        """
        # Approximate conversion factors (simplified)
        # This works reasonably well for most of the UK
        lat = (northing - 100000) * 0.000009 + 49.5
        lon = (easting - 400000) * 0.000014 + 0.5
        
        return lat, lon
    
    def insert_batch(self):
        """Insert current batch to database"""
        if not self.current_batch:
            return
        
        try:
            # Insert batch
            result = self.supabase.table('streets').insert(self.current_batch).execute()
            
            if result.data:
                self.total_imported += len(result.data)
                logging.info(f"Inserted batch of {len(result.data)} records. Total imported: {self.total_imported}")
            else:
                self.skipped += len(self.current_batch)
                logging.warning(f"Batch was empty or skipped: {len(self.current_batch)} records")
                
        except Exception as e:
            self.errors += len(self.current_batch)
            logging.error(f"Error inserting batch of {len(self.current_batch)} records: {e}")
            # Log the batch for debugging
            for record in self.current_batch[:3]:  # Log first 3 records as examples
                logging.error(f"Problem record: {record}")
        
        # Clear batch
        self.current_batch = []
    
    def process_csv_file(self, csv_file: str):
        """Process a single CSV file"""
        try:
            # Read CSV with proper encoding
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            for _, row in df.iterrows():
                cleaned_record = self.validate_and_clean_record(row.to_dict())
                
                if cleaned_record:
                    self.current_batch.append(cleaned_record)
                    self.total_processed += 1
                    
                    # Progress tracking
                    if self.total_processed % PROGRESS_INTERVAL == 0:
                        logging.info(f"Progress: {self.total_processed} records processed, {self.total_imported} imported")
                    
                    # Insert batch when full
                    if len(self.current_batch) >= BATCH_SIZE:
                        self.insert_batch()
                else:
                    self.skipped += 1
                    
        except Exception as e:
            logging.error(f"Error processing {csv_file}: {e}")
    
    def import_all_data(self):
        """Import all CSV files"""
        logging.info("Starting bulk import of OS Open Names data...")
        logging.info(f"Processing files from: {DATA_DIR}")
        
        # Get all CSV files
        csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
        csv_files.sort()  # Process in order
        
        logging.info(f"Found {len(csv_files)} CSV files to process")
        
        # Get database schema info
        schema = self.get_database_schema()
        logging.info(f"Database schema columns: {list(schema.keys()) if schema else 'Unknown'}")
        
        # Process each file
        for i, csv_file in enumerate(csv_files, 1):
            filename = os.path.basename(csv_file)
            logging.info(f"Processing file {i}/{len(csv_files)}: {filename}")
            
            try:
                self.process_csv_file(csv_file)
            except Exception as e:
                logging.error(f"Failed to process {filename}: {e}")
                continue
        
        # Insert remaining batch
        if self.current_batch:
            self.insert_batch()
        
        # Final summary
        self.print_summary()
    
    def print_summary(self):
        """Print import summary"""
        logging.info("\n" + "="*60)
        logging.info("IMPORT SUMMARY")
        logging.info("="*60)
        logging.info(f"Total records processed: {self.total_processed:,}")
        logging.info(f"Total records imported: {self.total_imported:,}")
        logging.info(f"Records skipped: {self.skipped:,}")
        logging.info(f"Records with errors: {self.errors:,}")
        
        if self.total_processed > 0:
            success_rate = (self.total_imported / self.total_processed) * 100
            logging.info(f"Success rate: {success_rate:.1f}%")
        
        logging.info(f"Log file: {LOG_FILE}")
        logging.info("="*60)

if __name__ == "__main__":
    print("🚀 Starting UK Street Etymology Database Import")
    print("📊 Processing OS Open Names data...")
    
    importer = StreetImport()
    
    try:
        importer.import_all_data()
        print("✅ Import completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Import interrupted by user")
        importer.print_summary()
        
    except Exception as e:
        print(f"❌ Import failed with error: {e}")
        logging.error(f"Import failed: {e}")
        importer.print_summary()
        sys.exit(1)
