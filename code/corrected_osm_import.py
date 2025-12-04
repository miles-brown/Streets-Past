#!/usr/bin/env python3
"""
Corrected OSM Street Importer - Uses only columns confirmed to exist
Based on database schema analysis, only street_name and street_type are confirmed to exist
"""
import csv
import logging
from datetime import datetime
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_supabase_client():
    """Create Supabase client"""
    SUPABASE_URL = "https://nadbmxfqknnnyuadhdtk.supabase.co"
    SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZGJteGZxa25ubnl1YWRoZHRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgyNjE5OSwiZXhwIjoyMDgwNDAyMTk5fQ.WhPS8SCqOfur1wPa5ONRbHeetkyT9cMQH-G-ald4Hzo"
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_existing_street_names(supabase: Client) -> set:
    """Get existing street names to avoid duplicates"""
    try:
        response = supabase.table('streets').select('street_name').execute()
        names = {record['street_name'].lower() for record in response.data}
        logger.info(f"Found {len(names)} existing street names")
        return names
    except Exception as e:
        logger.error(f"Failed to get existing streets: {e}")
        return set()

def create_corrected_street_data(csv_row: dict) -> dict:
    """Create street data using only confirmed existing columns"""
    street_name = csv_row.get('street_name', '').strip()
    
    if len(street_name) < 2:
        return None
    
    # Map street types
    street_type = csv_row.get('street_type', '').lower()
    if street_type in ['residential', 'unclassified', 'tertiary', 'secondary', 'primary', 'trunk']:
        mapped_type = street_type
    elif street_type == 'motorway':
        mapped_type = 'motorway' 
    elif street_type == 'living_street':
        mapped_type = 'living_street'
    else:
        mapped_type = 'road'  # Default
    
    # Return ONLY the columns that exist: street_name and street_type
    return {
        'street_name': street_name,
        'street_type': mapped_type
    }

def main():
    """Main import function with corrected column set"""
    logger.info("=== Starting Corrected OSM Street Import ===")
    logger.info("Using only confirmed existing columns: street_name, street_type")
    
    # Create client
    supabase = create_supabase_client()
    
    # Get existing street names
    existing_names = get_existing_street_names(supabase)
    
    # Read CSV data
    streets_to_import = []
    skipped = 0
    
    try:
        with open('/workspace/data/osm_sample_uk_streets.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                street_data = create_corrected_street_data(row)
                
                if not street_data:
                    skipped += 1
                    continue
                
                # Check for duplicates
                if street_data['street_name'].lower() in existing_names:
                    skipped += 1
                    continue
                
                streets_to_import.append(street_data)
                existing_names.add(street_data['street_name'].lower())
    
        logger.info(f"Prepared {len(streets_to_import)} streets for import ({skipped} skipped)")
        
        if not streets_to_import:
            logger.info("No streets to import")
            return
        
        # Import in small batches
        batch_size = 100
        total_imported = 0
        
        for i in range(0, len(streets_to_import), batch_size):
            batch = streets_to_import[i:i + batch_size]
            
            try:
                result = supabase.table('streets').insert(batch).execute()
                imported_count = len(result.data) if result.data else len(batch)
                total_imported += imported_count
                logger.info(f"Batch {i//batch_size + 1}: Imported {imported_count} streets")
                
            except Exception as e:
                logger.error(f"Batch {i//batch_size + 1} failed: {e}")
                continue
        
        logger.info(f"=== IMPORT COMPLETE ===")
        logger.info(f"Total imported: {total_imported}")
        logger.info(f"Total skipped: {skipped}")
        
        # Verify final count
        try:
            verify_response = supabase.table('streets').select('street_name', 'street_type').execute()
            total_count = len(verify_response.data)
            
            logger.info(f"=== VERIFICATION ===")
            logger.info(f"Total streets in DB: {total_count}")
            logger.info(f"Import result: +{total_imported} new OSM streets")
            logger.info(f"Total database size: {total_count} streets")
            
            # Show sample of imported streets
            if verify_response.data:
                logger.info("\nSample streets in database:")
                for i, street in enumerate(verify_response.data[:10], 1):
                    logger.info(f"{i:2d}. {street['street_name']} ({street['street_type']})")
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
    
    except Exception as e:
        logger.error(f"Import failed: {e}")

if __name__ == "__main__":
    main()