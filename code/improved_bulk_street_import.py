#!/usr/bin/env python3
"""
Improved OS Open Names CSV Bulk Import Script
More inclusive approach - imports all populated places and geographic features
that could have street names associated with them.
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
LOG_FILE = "/workspace/code/improved_street_import_log.txt"

# We want to include all geographic features since they can have street names
INCLUDED_LOCAL_TYPES = {
    'populatedPlace', 'hamlet', 'village', 'town', 'city', 'suburbanArea', 'otherSettlement',
    'street', 'road', 'namedRoad', 'footpath', 'track', 'route', 'terrace', 'row', 'close', 
    'alley', 'way', 'place', 'square', 'court', 'grove', 'crescent', 'avenue', 'lane', 'park',
    'estate', 'farm', 'farmstead', 'locality', 'district', 'area', 'neighbourhood', 'zone',
    'forest', 'wood', 'moor', 'heath', 'common', 'green', 'field', 'meadow', 'hill', 'mountain',
    'mount', 'headland', 'point', 'bay', 'harbour', 'quay', 'pier', 'dock', 'canal', 'river',
    'stream', 'brook', 'lake', 'pond', 'reservoir', 'beach', 'cliff', 'rock', 'cave'
}

# Names that indicate street/road features
STREET_INDICATORS = [
    'street', 'road', 'lane', 'avenue', 'close', 'way', 'row', 'drive', 'place', 'square', 
    'court', 'grove', 'park', 'crescent', 'terrace', 'gardens', 'mews', 'walk', 'view', 
    'heights', 'bridge', 'wharf', 'pier', 'quay', 'strand', 'highway', 'motorway', 'bypass',
    'approach', 'service', 'link', 'arcade', 'centre', 'center', 'mall', 'precinct', 
    'walkway', 'passage', 'alley', 'path', 'trail', 'route', 'track', 'tracklet', 'private'
]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class ImprovedStreetImport:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        self.total_processed = 0
        self.total_imported = 0
        self.errors = 0
        self.skipped = 0
        self.current_batch = []
        
    def osgb36_to_wgs84(self, easting: float, northing: float) -> Tuple[float, float]:
        """
        Simple OSGB36 to WGS84 conversion (approximate).
        """
        lat = (northing - 100000) * 0.000009 + 49.5
        lon = (easting - 400000) * 0.000014 + 0.5
        return lat, lon
    
    def validate_and_clean_record(self, row: Dict) -> Optional[Dict]:
        """Clean and validate a single record - much more inclusive"""
        try:
            # Core fields - we need at least a name
            name1 = str(row.get('NAME1', '')).strip()
            name2 = str(row.get('NAME2', '')).strip() if row.get('NAME2') else ''
            
            if not name1:
                return None  # Skip records without a name
            
            # Combine names if both exist
            full_name = f"{name1} {name2}".strip() if name2 else name1
            
            # Get feature types
            local_type = str(row.get('LOCAL_TYPE', '')).lower().strip()
            feature_type = str(row.get('TYPE', '')).lower().strip()
            
            # Check if this is a feature we want to include
            should_include = False
            
            # Include if it's explicitly one of our target types
            if local_type in INCLUDED_LOCAL_TYPES:
                should_include = True
            
            # Include if TYPE field indicates it's a street/road
            if 'road' in feature_type or 'street' in feature_type:
                should_include = True
            
            # Include if the name contains street indicators
            if any(indicator in full_name.lower() for indicator in STREET_INDICATORS):
                should_include = True
            
            # If not explicitly excluded and has reasonable characteristics, include it
            # This catches many populated places that might have street names associated
            if not should_include and len(full_name) > 1 and len(full_name) < 100:
                # Include it anyway since populated places can have street names
                should_include = True
            
            if not should_include:
                return None
            
            # Clean and prepare the record
            cleaned_record = {
                'street_name': full_name,
                'street_type': local_type if local_type else feature_type,
                'county': str(row.get('COUNTY_UNITARY', '')).strip() if row.get('COUNTY_UNITARY') else None,
                'local_authority_area': str(row.get('DISTRICT_BOROUGH', '')).strip() if row.get('DISTRICT_BOROUGH') else None,
                'post_town': str(row.get('POPULATED_PLACE', '')).strip() if row.get('POPULATED_PLACE') else None,
                'postcode': str(row.get('POSTCODE_DISTRICT', '')).strip() if row.get('POSTCODE_DISTRICT') else None,
                'region': str(row.get('REGION', '')).strip() if row.get('REGION') else None,
                'street_name_language': str(row.get('NAME1_LANG', 'en')).strip() if row.get('NAME1_LANG') else 'en',
                'country': str(row.get('COUNTRY', 'England')).strip() if row.get('COUNTRY') else 'England'
            }
            
            # Coordinates conversion
            x_coord = row.get('GEOMETRY_X')
            y_coord = row.get('GEOMETRY_Y')
            
            if x_coord and y_coord:
                try:
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
            cleaned_record['osm_id'] = None
            cleaned_record['etymology'] = None
            cleaned_record['historical_origins'] = None
            cleaned_record['cultural_significance'] = None
            cleaned_record['notable_people'] = None
            cleaned_record['fun_facts'] = None
            
            return cleaned_record
            
        except Exception as e:
            logging.warning(f"Error cleaning record: {e}")
            return None
    
    def insert_batch(self):
        """Insert current batch to database"""
        if not self.current_batch:
            return
        
        try:
            result = self.supabase.table('streets').insert(self.current_batch).execute()
            
            if result.data:
                self.total_imported += len(result.data)
                logging.info(f"Inserted batch of {len(result.data)} records. Total imported: {self.total_imported:,}")
            else:
                self.skipped += len(self.current_batch)
                logging.warning(f"Batch was empty or skipped: {len(self.current_batch)} records")
                
        except Exception as e:
            self.errors += len(self.current_batch)
            logging.error(f"Error inserting batch of {len(self.current_batch)} records: {e}")
            # Log examples of failed records
            for record in self.current_batch[:3]:
                logging.error(f"Problem record: {record}")
        
        self.current_batch = []
    
    def process_csv_file(self, csv_file: str):
        """Process a single CSV file"""
        try:
            df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)
            
            for _, row in df.iterrows():
                cleaned_record = self.validate_and_clean_record(row.to_dict())
                
                if cleaned_record:
                    self.current_batch.append(cleaned_record)
                    self.total_processed += 1
                    
                    # Progress tracking
                    if self.total_processed % PROGRESS_INTERVAL == 0:
                        logging.info(f"Progress: {self.total_processed:,} records processed, {self.total_imported:,} imported")
                    
                    # Insert batch when full
                    if len(self.current_batch) >= BATCH_SIZE:
                        self.insert_batch()
                else:
                    self.skipped += 1
                    
        except Exception as e:
            logging.error(f"Error processing {csv_file}: {e}")
    
    def import_all_data(self):
        """Import all CSV files"""
        logging.info("Starting improved bulk import of OS Open Names data...")
        logging.info(f"Processing files from: {DATA_DIR}")
        
        csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
        csv_files.sort()
        
        logging.info(f"Found {len(csv_files)} CSV files to process")
        
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
            logging.info(f"Import success rate: {success_rate:.1f}%")
        
        logging.info(f"Log file: {LOG_FILE}")
        logging.info("="*60)

if __name__ == "__main__":
    print("🚀 Starting Improved UK Street Etymology Database Import")
    print("📊 Importing populated places and geographic features...")
    
    importer = ImprovedStreetImport()
    
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
