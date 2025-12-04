#!/usr/bin/env python3
"""
OpenStreetMap UK Street Data Extractor - Regional Approach
Extracts street data from OSM by dividing UK into smaller regions
"""

import json
import requests
import time
import csv
import re
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OSMRegionalExtractor:
    """Extract UK street data from OpenStreetMap using regional approach"""
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSM Street Etymology Database Extractor 1.0'
        })
        
        # Street highway types to include
        self.street_types = {
            'residential', 'unclassified', 'tertiary', 'secondary', 
            'primary', 'trunk', 'motorway', 'living_street', 'service'
        }
        
        # UK bounding box
        self.uk_bbox = {
            'south': 49.8,   # Southern tip of mainland UK
            'west': -8.0,    # Western coast
            'north': 60.9,   # Northern tip of Scotland
            'east': 2.0      # Eastern coast
        }
        
        # Statistics
        self.total_streets = 0
        self.processed_regions = 0
        
    def create_region_query(self, bbox: Dict[str, float]) -> str:
        """Create Overpass QL query for a specific region"""
        south, west, north, east = bbox['south'], bbox['west'], bbox['north'], bbox['east']
        query = f"""
        [out:json][timeout:90];
        (
          way["highway"]["name"]["name"!~"^(Unnamed|Unnamed Road)$"]
          ["highway"~"^(residential|unclassified|tertiary|secondary|primary|trunk|living_street)$"]
          ["name"!~"^[0-9]+$"]
          ({south},{west},{north},{east});
        );
        out body;
        """
        return query.strip()
    
    def create_test_query(self) -> str:
        """Create a small test query"""
        # Very small area around central London
        bbox = {'south': 51.48, 'west': -0.12, 'north': 51.52, 'east': 0.02}
        return self.create_region_query(bbox)
    
    def divide_uk_regions(self, grid_size: float = 2.0) -> List[Dict[str, float]]:
        """Divide UK into smaller regions for processing"""
        regions = []
        
        # Create grid covering UK
        lat_steps = math.ceil((self.uk_bbox['north'] - self.uk_bbox['south']) / grid_size)
        lon_steps = math.ceil((self.uk_bbox['east'] - self.uk_bbox['west']) / grid_size)
        
        for i in range(lat_steps):
            for j in range(lon_steps):
                south = self.uk_bbox['south'] + i * grid_size
                north = min(south + grid_size, self.uk_bbox['north'])
                west = self.uk_bbox['west'] + j * grid_size
                east = min(west + grid_size, self.uk_bbox['east'])
                
                # Skip if too small (edge case)
                if north - south < 0.1 or east - west < 0.1:
                    continue
                
                # Add small padding to ensure coverage
                padding = 0.01
                regions.append({
                    'south': max(south - padding, 49.0),
                    'west': max(west - padding, -9.0),
                    'north': min(north + padding, 61.0),
                    'east': min(east + padding, 3.0)
                })
        
        return regions
    
    def extract_streets_from_region(self, bbox: Dict[str, float]) -> List[Dict]:
        """Extract streets from a single region"""
        query = self.create_region_query(bbox)
        
        try:
            logger.info(f"Querying region {bbox}")
            response = self.session.post(self.overpass_url, data=query, timeout=90)
            response.raise_for_status()
            
            data = response.json()
            elements = data.get('elements', [])
            
            streets = []
            for element in elements:
                tags = element.get('tags', {})
                street_name = tags.get('name', '').strip()
                
                # Skip unnamed streets
                if not street_name or street_name in ['Unnamed', 'Unnamed Road', '']:
                    continue
                    
                # Skip numeric-only names
                if street_name.isdigit() or re.match(r'^[0-9]+$', street_name):
                    continue
                
                # Clean street name
                street_name = ' '.join(street_name.split())
                if len(street_name.strip()) < 2:
                    continue
                
                # Extract coordinates
                latitude = None
                longitude = None
                if 'geometry' in element and element['geometry']:
                    coords = element['geometry']
                    lats = [coord['lat'] for coord in coords if 'lat' in coord]
                    lons = [coord['lon'] for coord in coords if 'lon' in coord]
                    
                    if lats and lons:
                        latitude = round(sum(lats) / len(lats), 6)
                        longitude = round(sum(lons) / len(lons), 6)
                
                # Create street record
                street_data = {
                    'street_name': street_name,
                    'street_type': tags.get('highway', ''),
                    'latitude': latitude,
                    'longitude': longitude,
                    'osm_id': element.get('id'),
                    'region_bbox': bbox,
                    'created_at': datetime.now().isoformat(),
                    'source': 'OpenStreetMap'
                }
                
                streets.append(street_data)
            
            return streets
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error for region {bbox}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing region {bbox}: {e}")
            return []
    
    def test_small_area(self):
        """Test with very small area first"""
        logger.info("Testing with small London area...")
        
        query = self.create_test_query()
        try:
            response = self.session.post(self.overpass_url, data=query, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            elements = data.get('elements', [])
            
            logger.info(f"Found {len(elements)} elements in test area")
            
            # Sample first few streets
            sample_streets = []
            for element in elements[:5]:
                if element.get('tags', {}).get('name'):
                    sample_streets.append({
                        'name': element['tags']['name'],
                        'highway': element['tags'].get('highway', 'unknown')
                    })
            
            logger.info("Sample streets:")
            for street in sample_streets:
                logger.info(f"  - {street['name']} ({street['highway']})")
            
            return len(elements) > 0
            
        except Exception as e:
            logger.error(f"Test query failed: {e}")
            return False
    
    def process_all_regions(self):
        """Process all UK regions"""
        logger.info("Dividing UK into regions...")
        regions = self.divide_uk_regions(grid_size=1.5)  # Smaller regions
        
        logger.info(f"Created {len(regions)} regions to process")
        
        all_streets = []
        successful_regions = 0
        
        # Process first 5 regions as test
        test_regions = regions[:5]
        
        for i, region in enumerate(test_regions, 1):
            logger.info(f"Processing region {i}/{len(test_regions)}")
            
            streets = self.extract_streets_from_region(region)
            all_streets.extend(streets)
            
            if streets:
                successful_regions += 1
            
            # Rate limiting
            time.sleep(1)
            
            logger.info(f"Region {i}: {len(streets)} streets found")
            
            # Save progress every region
            if i % 2 == 0:
                self.save_progress(all_streets, f"/workspace/data/osm_progress_{i}.json")
        
        self.total_streets = len(all_streets)
        self.processed_regions = successful_regions
        
        # Save final results
        self.save_final_results(all_streets)
        
        logger.info(f"Processing complete!")
        logger.info(f"Total regions processed: {successful_regions}/{len(test_regions)}")
        logger.info(f"Total streets extracted: {self.total_streets}")
        
        return all_streets
    
    def save_progress(self, streets: List[Dict], filename: str):
        """Save progress to file"""
        data = {
            'metadata': {
                'extracted_at': datetime.now().isoformat(),
                'total_streets_so_far': len(streets),
                'processing_status': 'in_progress'
            },
            'streets': streets
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save_final_results(self, streets: List[Dict]):
        """Save final results"""
        filename = '/workspace/data/osm_uk_streets.json'
        
        data = {
            'metadata': {
                'extracted_at': datetime.now().isoformat(),
                'total_streets': len(streets),
                'regions_processed': self.processed_regions,
                'extraction_method': 'Regional Overpass API queries'
            },
            'streets': streets
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Final results saved to {filename}")
        
        # Also save as CSV for easy inspection
        csv_filename = '/workspace/data/osm_uk_streets.csv'
        if streets:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['street_name', 'street_type', 'latitude', 'longitude', 'osm_id', 'created_at', 'source']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(streets)
            
            logger.info(f"CSV results saved to {csv_filename}")

def main():
    """Main execution function"""
    extractor = OSMRegionalExtractor()
    
    # Test small area first
    if not extractor.test_small_area():
        logger.error("❌ Test failed!")
        return
    
    logger.info("✅ Test successful! Starting full extraction...")
    
    # Process regions
    streets = extractor.process_all_regions()
    
    if streets:
        logger.info(f"✅ Successfully extracted {len(streets)} street records!")
        
        # Show sample
        logger.info("Sample extracted streets:")
        for i, street in enumerate(streets[:5], 1):
            logger.info(f"{i:2d}. {street['street_name']} ({street['street_type']})")
    else:
        logger.error("❌ No streets extracted!")

if __name__ == "__main__":
    main()