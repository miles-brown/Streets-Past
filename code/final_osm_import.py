#!/usr/bin/env python3
"""
Final Corrected OSM Street Importer - includes ALL required database fields
Based on error analysis, county is a required NOT NULL field
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

def create_complete_street_data(csv_row: dict) -> dict:
    """Create complete street data with ALL required database fields"""
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
    
    # Return data with ALL required fields based on database schema analysis
    return {
        'street_name': street_name,
        'street_type': mapped_type,
        'county': 'United Kingdom',  # Required field - default for OSM UK streets
        'country': 'United Kingdom',  # Add country for context
    }

def main():
    """Main import function with complete field mapping"""
    logger.info("=== Final Corrected OSM Street Import ===")
    logger.info("Including ALL required database fields: street_name, street_type, county, country")
    
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
                street_data = create_complete_street_data(row)
                
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
        
        # Import in larger batches for efficiency
        batch_size = 200
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
                # If batch fails, try smaller batches
                if len(batch) > 50:
                    for j in range(0, len(batch), 50):
                        small_batch = batch[j:j + 50]
                        try:
                            small_result = supabase.table('streets').insert(small_batch).execute()
                            small_imported = len(small_result.data) if small_result.data else len(small_batch)
                            total_imported += small_imported
                            logger.info(f"Small batch {j//50 + 1}: Imported {small_imported} streets")
                        except Exception as e2:
                            logger.error(f"Small batch {j//50 + 1} failed: {e2}")
                continue
        
        logger.info(f"=== IMPORT COMPLETE ===")
        logger.info(f"Total imported: {total_imported}")
        logger.info(f"Total skipped: {skipped}")
        
        # Verify final count
        try:
            verify_response = supabase.table('streets').select('street_name', 'street_type', 'county').execute()
            total_count = len(verify_response.data)
            
            logger.info(f"=== FINAL VERIFICATION ===")
            logger.info(f"Total streets in DB: {total_count}")
            logger.info(f"New OSM streets imported: {total_imported}")
            logger.info(f"Database growth: +{total_imported} streets (from 35 to {total_count})")
            
            # Show sample of imported streets with county
            if verify_response.data:
                logger.info(f"\nSample streets in database:")
                for i, street in enumerate(verify_response.data[:10], 1):
                    county = street.get('county', 'Unknown')
                    logger.info(f"{i:2d}. {street['street_name']} ({street['street_type']}) - {county}")
            
            if total_imported > 0:
                logger.info(f"\n🎉 SUCCESS! OpenStreetMap integration completed!")
                logger.info(f"📊 Database expanded from {35} to {total_count} streets")
                logger.info(f"🌍 Added {total_imported} new UK street names for etymological research")
            else:
                logger.info(f"\n⚠️  Import completed but no new streets were added")
                
        except Exception as e:
            logger.error(f"Verification failed: {e}")
    
    except Exception as e:
        logger.error(f"Import failed: {e}")

if __name__ == "__main__":
    main()