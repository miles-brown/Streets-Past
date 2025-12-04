# UK Counties and Local Authorities Import Documentation

## Overview

This documentation describes the processed UK administrative geography datasets ready for Supabase import, derived from official Office for National Statistics (ONS) Names & Codes datasets.

## Data Sources

### Counties Dataset
- **Source**: County and Unitary Authority (December 2024) Names and Codes in the UK
- **URL**: https://www.data.gov.uk/dataset/79b1ab91-4fb9-4a66-abc7-ddfba7027c73/county-and-unitary-authority-december-2024-names-and-codes-in-the-uk
- **Original File**: `county_unitary_authority_december_2024.csv`
- **Records**: 218 administrative units

### Local Authorities Dataset
- **Source**: Local Authority Districts (April 2025) Names and Codes in the UK (V2)
- **URL**: https://www.data.gov.uk/dataset/b2c91962-58e7-40f1-ad56-7aa2473a93fd/local-authority-districts-april-2025-names-and-codes-in-the-uk-v21
- **Original File**: `local_authority_districts_april_2025.csv`
- **Records**: 361 local authority districts and unitary authorities

## File Structure

### Counties Import File: `counties_import_supabase.csv`

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `county_id` | UUID | Primary key | Generated unique identifier |
| `county_name` | Text | Primary name in English | Not null |
| `county_name_welsh` | Text | Welsh language name | Nullable (196 of 218 missing) |
| `gss_county_code` | Text | Government Statistical Service 9-character code | Unique, not null |
| `country` | Text | Country name (England/Wales/Scotland/Northern Ireland) | Not null |
| `authority_type` | Text | Type of administrative unit | Not null |
| `source_reference` | Text | Source dataset reference | Not null |

### Local Authorities Import File: `local_authorities_import_supabase.csv`

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `la_id` | UUID | Primary key | Generated unique identifier |
| `la_name` | Text | Primary name in English | Not null |
| `la_name_welsh` | Text | Welsh language name | Nullable (339 of 361 missing) |
| `gss_la_code` | Text | Government Statistical Service 9-character code | Unique, not null |
| `country` | Text | Country name (England/Wales/Scotland/Northern Ireland) | Not null |
| `authority_type` | Text | Type of administrative unit | Not null |
| `source_reference` | Text | Source dataset reference | Not null |

## Data Distribution

### Counties by Country and Type
- **England**: 153 units (21 Counties, 132 Unitary Authorities)
- **Scotland**: 32 Council Areas
- **Wales**: 22 Unitary Authorities
- **Northern Ireland**: 11 District Councils

### Local Authorities by Country and Type
- **England**: 296 units
  - 164 Districts
  - 33 London Boroughs
  - 36 Metropolitan Districts
  - 63 Unitary Authorities
- **Scotland**: 32 Unitary Authorities
- **Wales**: 22 Unitary Authorities
- **Northern Ireland**: 11 Unitary Authorities

## GSS Code Structure

All codes follow the Government Statistical Service 9-character format:
- **First Character**: Country prefix (E=England, W=Wales, S=Scotland, N=Northern Ireland)
- **Next 2-3 Characters**: Administrative level indicator
- **Remaining Characters**: Unique identifier within the level

Examples:
- `E10000003`: Cambridgeshire (County)
- `E06000001`: Hartlepool (Unitary Authority)
- `E09000001`: City of London (London Borough)
- `S12000006`: Dumfries and Galloway (Scottish Council Area)

## Data Quality Validation

✅ **Passed Validations**:
- No duplicate GSS codes within each dataset
- All GSS codes match expected 9-character pattern
- No missing primary names or GSS codes
- Consistent country classification
- UUID primary keys properly generated

⚠️ **Data Gaps**:
- Welsh language names missing for most entries (90% of counties, 94% of local authorities)
- Some administrative reorganization tracking may require additional temporal data

## Import Instructions for Supabase

### 1. Create Database Tables

```sql
-- Create counties table
CREATE TABLE IF NOT EXISTS counties (
    county_id UUID PRIMARY KEY,
    county_name TEXT NOT NULL,
    county_name_welsh TEXT,
    gss_county_code TEXT UNIQUE NOT NULL,
    country TEXT NOT NULL,
    authority_type TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create local_authorities table  
CREATE TABLE IF NOT EXISTS local_authorities (
    la_id UUID PRIMARY KEY,
    la_name TEXT NOT NULL,
    la_name_welsh TEXT,
    gss_la_code TEXT UNIQUE NOT NULL,
    country TEXT NOT NULL,
    authority_type TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_counties_gss_code ON counties(gss_county_code);
CREATE INDEX idx_counties_country ON counties(country);
CREATE INDEX idx_counties_type ON counties(authority_type);

CREATE INDEX idx_local_authorities_gss_code ON local_authorities(gss_la_code);
CREATE INDEX idx_local_authorities_country ON local_authorities(country);
CREATE INDEX idx_local_authorities_type ON local_authorities(authority_type);
```

### 2. Import Data

Import the CSV files using Supabase's CSV import functionality or SQL COPY commands:

```sql
-- Import counties data
\copy counties FROM 'data/import/counties/counties_import_supabase.csv' WITH (FORMAT csv, HEADER true);

-- Import local authorities data  
\copy local_authorities FROM 'data/import/local_authorities/local_authorities_import_supabase.csv' WITH (FORMAT csv, HEADER true);
```

### 3. Verify Import

```sql
-- Check record counts
SELECT 'Counties' as table_name, COUNT(*) as record_count FROM counties
UNION ALL
SELECT 'Local Authorities' as table_name, COUNT(*) as record_count FROM local_authorities;

-- Sample data verification
SELECT country, authority_type, COUNT(*) as count
FROM counties 
GROUP BY country, authority_type
ORDER BY country, authority_type;
```

## Licensing and Attribution

The source datasets are licensed under the Open Government Licence v3.0. Attribution requirements:

- Contains public sector information licensed under the Open Government Licence v3.0
- Contains ONS data © Crown copyright and database right
- Data as at December 2024 (counties) and April 2025 (local authorities)

## Update Schedule

These datasets should be refreshed according to ONS release schedules:
- **Counties/Unitary Authorities**: Updated annually in December
- **Local Authority Districts**: Updated annually in April

## Related Datasets

For comprehensive UK administrative geography coverage, consider also integrating:
- Local Authority District to County/Unitary Authority lookups
- Boundary data for spatial analysis
- Statistical geography data (wards, parishes, etc.)
- Postcode to administrative area mappings

## Contact and Support

For questions about the data structure or import process, refer to:
- ONS Geography Portal: https://geoportal.statistics.gov.uk/
- Technical documentation in the integration strategy document
- Supabase documentation for import procedures

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-04  
**Author**: MiniMax Agent