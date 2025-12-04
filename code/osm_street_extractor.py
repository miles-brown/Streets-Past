#!/usr/bin/env python3
"""
OpenStreetMap UK Street Data Extractor
Extracts street data from OSM using Overpass API for street etymology database
"""

import json
import requests
import time
import csv
import re
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/code/osm_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OSMStreetExtractor:
    """Extract UK street data from OpenStreetMap using Overpass API"""
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSM Street Etymology Database Extractor 1.0'
        })
        
        # Street highway types to include
        self.street_types = {
            'residential',      # Residential streets
            'unclassified',     # Minor roads
            'tertiary',         # Local connector roads
            'secondary',        # Secondary roads
            'primary',          # Primary roads
            'trunk',            # Major roads
            'motorway',         # Motorways
            'trunk_link',       # Motorway links
            'primary_link',     # Primary links
            'secondary_link',   # Secondary links
            'tertiary_link',    # Tertiary links
            'living_street',    # Pedestrian priority streets
            'service',          # Service roads (selective)
            'access',           # Access roads
            'track',            # Tracks (selective)
        }
        
        # Statistics
        self.stats = {
            'total_queries': 0,
            'total_streets_found': 0,
            'streets_with_names': 0,
            'streets_without_names': 0,
            'errors': 0
        }
    
    def create_uk_street_query(self) -> str:
        """Create Overpass QL query for UK streets"""
        query = """
        [out:json][timeout:180];
        (
          way["highway"]["name"]["name"!~"^(Unnamed|Unnamed Road)$"]
          ["highway"~"^(residential|unclassified|tertiary|secondary|primary|trunk|motorway|living_street|service)$"]
          ["name"!~"^[0-9]+$"]
          (gb);
        );
        out body;
        """
        return query.strip()
    
    def create_narrow_query(self, bbox: Tuple[float, float, float, float]) -> str:
        """Create query for a specific bounding box"""
        south, west, north, east = bbox
        query = f"""
        [out:json][timeout:60];
        (
          way["highway"]["name"]["name"!~"^(Unnamed|Unnamed Road)$"]
          ["highway"~"^(residential|unclassified|tertiary|secondary|primary|trunk|living_street)$"]
          ["name"!~"^[0-9]+$"]
          ({south},{west},{north},{east});
        );
        out body;
        """
        return query.strip()
    
    def test_small_area(self) -> Dict:
        """Test with a small area around London to validate approach"""
        logger.info("Testing with London area...")
        
        # Small bbox around central London
        bbox = (51.45, -0.15, 51.55, 0.05)  # South, West, North, East
        query = self.create_narrow_query(bbox)
        
        try:
            logger.info("Sending test query to Overpass API...")
            response = self.session.post(self.overpass_url, data=query, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Received {len(data.get('elements', []))} elements")
            
            # Analyze the response
            elements = data.get('elements', [])
            streets_with_names = 0
            street_types = {}
            
            for element in elements:
                if element.get('tags', {}).get('name'):
                    streets_with_names += 1
                    
                highway_type = element.get('tags', {}).get('highway', 'unknown')
                street_types[highway_type] = street_types.get(highway_type, 0) + 1
            
            test_result = {
                'total_elements': len(elements),
                'streets_with_names': streets_with_names,
                'street_types': street_types,
                'sample_streets': []
            }
            
            # Collect sample streets
            for element in elements[:10]:  # First 10 for sample
                if element.get('tags', {}).get('name'):
                    street_data = {
                        'name': element.get('tags', {}).get('name'),
                        'highway': element.get('tags', {}).get('highway'),
                        'id': element.get('id')
                    }
                    test_result['sample_streets'].append(street_data)
            
            logger.info(f"Test results: {test_result}")
            return test_result
            
        except Exception as e:
            logger.error(f"Test query failed: {e}")
            return {'error': str(e)}
    
    def extract_street_data(self, elements: List[Dict]) -> List[Dict]:
        """Extract and clean street data from OSM elements"""
        streets = []
        
        for element in elements:
            tags = element.get('tags', {})
            street_name = tags.get('name', '').strip()
            
            # Skip unnamed or invalid streets
            if not street_name or street_name in ['Unnamed', 'Unnamed Road', '']:
                self.stats['streets_without_names'] += 1
                continue
            
            # Skip numeric-only names
            if street_name.isdigit() or re.match(r'^[0-9]+$', street_name):
                self.stats['streets_without_names'] += 1
                continue
            
            # Clean street name
            street_name = self.clean_street_name(street_name)
            if not street_name:
                continue
            
            # Extract street data
            street_data = {
                'osm_id': element.get('id'),
                'street_name': street_name,
                'street_type': tags.get('highway', ''),
                'ref': tags.get('ref', ''),  # Street reference number
                'layer': tags.get('layer', ''),
                'bridge': tags.get('bridge', ''),
                'tunnel': tags.get('tunnel', ''),
                'oneway': tags.get('oneway', ''),
                'maxspeed': tags.get('maxspeed', ''),
                'surface': tags.get('surface', ''),
                'access': tags.get('access', ''),
                'created_at': datetime.now().isoformat(),
                'source': 'OpenStreetMap'
            }
            
            # Extract coordinates if available
            if 'geometry' in element:
                coords = element['geometry']
                if coords:
                    # Get center coordinates for the street segment
                    lats = [coord['lat'] for coord in coords if 'lat' in coord]
                    lons = [coord['lon'] for coord in coords if 'lon' in coord]
                    
                    if lats and lons:
                        street_data['latitude'] = sum(lats) / len(lats)
                        street_data['longitude'] = sum(lons) / len(lons)
            
            streets.append(street_data)
            self.stats['streets_with_names'] += 1
        
        return streets
    
    def clean_street_name(self, name: str) -> Optional[str]:
        """Clean and validate street name"""
        if not name:
            return None
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove common prefixes that aren't part of the name
        prefixes_to_remove = ['Street ', 'Road ', 'Avenue ', 'Lane ']
        for prefix in prefixes_to_remove:
            if name.startswith(prefix):
                return None  # Let the street_type handle these
        
        # Remove special characters and normalize
        name = re.sub(r'[^\w\s\-\']', '', name)
        
        # Must have at least 2 characters after cleaning
        if len(name.strip()) < 2:
            return None
        
        return name.strip()
    
    def save_sample_data(self, streets: List[Dict], filename: str = '/workspace/data/osm_sample_streets.json'):
        """Save sample data for inspection"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'extracted_at': datetime.now().isoformat(),
                    'total_streets': len(streets),
                    'statistics': self.stats
                },
                'streets': streets[:100]  # First 100 for inspection
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Sample data saved to {filename}")
    
    def run_test(self):
        """Run test to validate data extraction approach"""
        logger.info("=== Starting OSM Street Data Extraction Test ===")
        
        # Test with small area
        test_result = self.test_small_area()
        
        if 'error' in test_result:
            logger.error(f"Test failed: {test_result['error']}")
            return False
        
        # If test is successful, try full UK query
        if test_result.get('streets_with_names', 0) > 0:
            logger.info("Test successful! Proceeding with small extraction...")
            
            # Try full UK query
            logger.info("Testing full UK query...")
            query = self.create_uk_street_query()
            
            try:
                response = self.session.post(self.overpass_url, data=query, timeout=180)
                response.raise_for_status()
                
                data = response.json()
                elements = data.get('elements', [])
                
                logger.info(f"Found {len(elements)} total elements in UK")
                
                # Extract street data
                streets = self.extract_street_data(elements)
                
                logger.info(f"Extracted {len(streets)} valid streets with names")
                
                # Save sample data
                self.save_sample_data(streets)
                
                # Print statistics
                self.print_statistics()
                
                return True
                
            except Exception as e:
                logger.error(f"Full query failed: {e}")
                return False
        
        return False
    
    def print_statistics(self):
        """Print extraction statistics"""
        logger.info("=== EXTRACTION STATISTICS ===")
        logger.info(f"Total queries: {self.stats['total_queries']}")
        logger.info(f"Total streets found: {self.stats['total_streets_found']}")
        logger.info(f"Streets with names: {self.stats['streets_with_names']}")
        logger.info(f"Streets without names: {self.stats['streets_without_names']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("=" * 35)

def main():
    """Main execution function"""
    extractor = OSMStreetExtractor()
    
    try:
        success = extractor.run_test()
        if success:
            logger.info("✅ OSM extraction test completed successfully!")
        else:
            logger.error("❌ OSM extraction test failed!")
            
    except KeyboardInterrupt:
        logger.info("Extraction interrupted by user")
    except Exception as e:
        logger.error(f"Extraction failed with error: {e}")

if __name__ == "__main__":
    main()