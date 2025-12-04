#!/usr/bin/env python3
"""
Proper UK Postcode Generation for Import Script
Generates realistic UK postcode formats
"""

import random
import string

def generate_realistic_postcode():
    """Generate a proper UK postcode format"""
    
    # Define postcode areas and their valid districts
    postcode_areas = {
        'BR6': ['BR6'],  # Orpington
        'BR7': ['BR7'],  # Chislehurst  
        'IG1': ['IG1'],  # Ilford
        'E17': ['E17'],  # Walthamstow
        'IG11': ['IG11'], # Barking
        'SE10': ['SE10'], # Greenwich
        'E8': ['E8'],    # Hackney
        'NW1': ['NW1'],  # Camden
        'N1': ['N1'],    # Islington
        'M1': ['M1']     # Manchester
    }
    
    # Choose random area and district
    area = random.choice(list(postcode_areas.keys()))
    
    # Generate proper inward code format
    # UK inward codes follow patterns like: 1AA, 1AB, 1AE, 1BB, etc.
    first_digit = random.randint(1, 9)
    letters = 'ABDEFGHJLNPQRSTUWXYZ'  # Valid letters in UK postcodes
    
    # Build inward code (format: [1-9][A-Z][A-Z])
    inward_code = f"{first_digit}{random.choice(letters)}{random.choice(letters)}"
    
    # Full postcode
    postcode = f"{area} {inward_code}"
    
    return postcode

# Test the function
print("=== PROPER UK POSTCODE EXAMPLES ===")
print("Generated realistic postcodes:")
for i in range(10):
    postcode = generate_realistic_postcode()
    area, inward = postcode.split(' ')
    print(f"{i+1:2d}. {postcode} = {area} (area/district) + {inward} (delivery point)")

print(f"\n=== STREET NAME + POSTCODE COMBINATIONS ===")
print("These are UNIQUE identifiers for streets:")
streets = ["High Street", "Church Road", "London Road", "Victoria Street"]
for street in streets:
    postcode = generate_realistic_postcode()
    print(f"✅ {street}, {postcode} = UNIQUE street location")
    
print(f"\n✅ This solves your original question:")
print("'High Street, Orpington' vs 'High Street, Chislehurst'")
print("Even if they had the same street name (HIGH STREET), they would")
print("have different postcodes (BR6 vs BR7), making them separate entries!")