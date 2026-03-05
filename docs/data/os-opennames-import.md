# OS OpenNames ETL Guide: Loading into Streets Past (Supabase/PostGIS)

## Overview

This guide covers the complete extract-transform-load (ETL) pipeline for importing OS OpenNames data into the Streets Past Supabase PostgreSQL database. OS OpenNames is the principal open dataset for street names across Great Britain, published by Ordnance Survey and covering approximately 870,000 named and numbered roads (plus 1.6 million postcodes and ~44,000 settlements). For Streets Past, only the road-related subset of ~790,000 records is loaded into the `streets` table.

**License**: OS OpenData Licence (compatible with OGL v3.0). Commercial use is permitted with attribution. See [Section 11](#11-attribution-and-license-compliance) for required attribution text.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Download](#2-download)
3. [Data Structure](#3-data-structure)
4. [Coordinate Conversion](#4-coordinate-conversion)
5. [Filtering](#5-filtering)
6. [CSV Preprocessing Script](#6-csv-preprocessing-script)
7. [Database Loading](#7-database-loading)
8. [Post-Load Indexing](#8-post-load-indexing)
9. [Quarterly Refresh Workflow](#9-quarterly-refresh-workflow)
10. [Data Validation](#10-data-validation)
11. [Attribution and License Compliance](#11-attribution-and-license-compliance)

---

## 1. Prerequisites

### Required Tools

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.10+ | Preprocessing and coordinate conversion | `apt install python3` / pyenv |
| `pyproj` | OSGB36 → WGS84 coordinate conversion | `pip install pyproj` |
| `pandas` | CSV filtering and transformation | `pip install pandas` |
| `psql` | Bulk loading via `\copy` | `apt install postgresql-client` |
| Supabase CLI | Schema migrations, edge function deploys | [supabase.com/docs/guides/cli](https://supabase.com/docs/guides/cli) |

### Python Environment Setup

```bash
# Create a dedicated virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all required packages
pip install pyproj pandas psycopg2-binary tqdm
```

### Database Access

You need the Supabase direct connection string (not the pooler) for bulk `\copy` operations. Find it in the Supabase dashboard under **Project Settings > Database > Connection string** — use the **Direct connection** URI, not the Session/Transaction pooler.

```bash
# Set as environment variable to avoid hardcoding credentials
export SUPABASE_DB_URL="postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres"
```

For the Streets Past project the Supabase project ID is `nadbmxfqknnnyuadhdtk`.

---

## 2. Download

### Source

OS OpenNames is available from the **OS Data Hub** open downloads page (free, no API key required):

```
https://osdatahub.os.uk/downloads/open/OpenNames
```

An account is required to download. Registration is free.

### Which Format to Use

**Use CSV**. All three formats (CSV, GML, GeoPackage) contain the same data, but CSV is the most practical for this pipeline:

- No specialist GIS software required
- Directly loadable with pandas and psql `\copy`
- Smallest file size
- Easiest to inspect and debug

GeoPackage is preferable if you are working inside QGIS or another GIS tool. GML is not recommended for bulk processing.

### Download Steps

1. Go to `https://osdatahub.os.uk/downloads/open/OpenNames`
2. Select **Download** for the CSV format
3. The download is a ZIP archive, approximately 600–800 MB compressed
4. Extract to a working directory:

```bash
mkdir -p ~/os-opennames-data
cd ~/os-opennames-data
unzip opname_csv_gb.zip
```

After extraction you will have a directory named `DATA/` containing approximately 214 individual CSV files, one per OS grid square (e.g., `HP.csv`, `HT.csv`, `HU.csv`, ..., `SV.csv`, `SW.csv`).

### Update Schedule

OS OpenNames is updated quarterly:

| Release Month | Approximate Availability |
|--------------|--------------------------|
| January | Mid-January |
| April | Mid-April |
| July | Mid-July |
| October | Mid-October |

Subscribe to OS Data Hub notifications to receive emails when new releases are published.

---

## 3. Data Structure

Each CSV file in the `DATA/` directory has the same column schema. There is a header row in each file.

### Column Reference

| Column | Type | Description |
|--------|------|-------------|
| `ID` | string | Unique identifier for the feature (UPRN-style OS reference) |
| `NAMES_URI` | string | Linked Data URI for the name entity |
| `NAME1` | string | Primary name (e.g., "High Street", "A303") |
| `NAME1_LANG` | string | Language of NAME1 (`eng`, `cym`, `gla`, `sco`, empty) |
| `NAME2` | string | Secondary/alternative name (e.g., Welsh equivalent) |
| `NAME2_LANG` | string | Language of NAME2 |
| `TYPE` | string | Feature class (e.g., `transportNetwork`, `populatedPlace`) |
| `LOCAL_TYPE` | string | Specific feature type (see filtering section below) |
| `GEOMETRY_X` | float | Easting in OSGB36 British National Grid (EPSG:27700) |
| `GEOMETRY_Y` | float | Northing in OSGB36 British National Grid (EPSG:27700) |
| `MOST_DETAIL_VIEW_RES` | integer | Scale denominator for most detailed view |
| `LEAST_DETAIL_VIEW_RES` | integer | Scale denominator for least detailed view |
| `MBR_XMIN` | float | Minimum bounding rectangle, min easting |
| `MBR_YMIN` | float | Minimum bounding rectangle, min northing |
| `MBR_XMAX` | float | Minimum bounding rectangle, max easting |
| `MBR_YMAX` | float | Minimum bounding rectangle, max northing |
| `POSTCODE_DISTRICT` | string | Postcode district (e.g., "SW1A") |
| `POPULATED_PLACE` | string | Associated settlement name |
| `POPULATED_PLACE_URI` | string | Linked Data URI for the settlement |
| `POPULATED_PLACE_TYPE` | string | Settlement type |
| `DISTRICT_BOROUGH` | string | District or borough name |
| `DISTRICT_BOROUGH_URI` | string | Linked Data URI |
| `DISTRICT_BOROUGH_TYPE` | string | District/borough type |
| `COUNTY_UNITARY` | string | County or unitary authority name |
| `COUNTY_UNITARY_URI` | string | Linked Data URI |
| `COUNTY_UNITARY_TYPE` | string | County/unitary type |
| `REGION` | string | OS region name (e.g., "South East") |
| `REGION_URI` | string | Linked Data URI |
| `COUNTRY` | string | Country (`England`, `Wales`, `Scotland`) |
| `RELATED_SPATIAL_OBJECT` | string | Reference to related spatial objects |
| `SAME_AS_DBPEDIA` | string | DBpedia linked data reference |
| `SAME_AS_GEONAMES` | string | GeoNames linked data reference |

### Key Fields for Streets Past

The Streets Past `streets` table primarily uses:

- `ID` → `id` (source reference)
- `NAME1` → `name`
- `POPULATED_PLACE` → `city`
- `COUNTY_UNITARY` → `county`
- `POSTCODE_DISTRICT` → `postcode_area`
- `GEOMETRY_X`, `GEOMETRY_Y` → converted to `longitude`, `latitude`
- `LOCAL_TYPE` → used for filtering (not stored directly)
- `NAME2` → stored as `name_alt` if available (Welsh/Gaelic names)
- `COUNTRY` → used for regional grouping

---

## 4. Coordinate Conversion

OS OpenNames stores coordinates in **OSGB36 British National Grid (EPSG:27700)** — eastings and northings in metres. Web mapping (MapLibre GL JS, Leaflet, OpenStreetMap tiles) requires **WGS84 geographic coordinates (EPSG:4326)** — decimal degrees longitude and latitude.

### Why Conversion is Necessary

- GEOMETRY_X values are eastings like `530000` (metres from the false origin)
- GEOMETRY_Y values are northings like `180000` (metres from the false origin)
- MapLibre expects longitude/latitude like `-0.1278`, `51.5074`

Without conversion, markers appear in the South Atlantic Ocean.

### Option A: Python with pyproj (Recommended for Preprocessing)

```python
from pyproj import Transformer

# Create a reusable transformer: EPSG:27700 (BNG) → EPSG:4326 (WGS84)
# always_xy=True ensures output is (longitude, latitude) order
transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

def bng_to_wgs84(easting: float, northing: float) -> tuple[float, float]:
    """
    Convert British National Grid (OSGB36) coordinates to WGS84.

    Args:
        easting:  GEOMETRY_X value from OS OpenNames
        northing: GEOMETRY_Y value from OS OpenNames

    Returns:
        (longitude, latitude) in decimal degrees (WGS84)
    """
    longitude, latitude = transformer.transform(easting, northing)
    return longitude, latitude

# Example
lon, lat = bng_to_wgs84(530000, 180000)
print(f"{lon:.6f}, {lat:.6f}")  # → -0.127758, 51.507268  (central London)
```

### Option B: PostGIS ST_Transform (In-Database Conversion)

If you load raw BNG coordinates into a staging table first, PostGIS can handle the conversion directly in SQL. This is slower than Python preprocessing but avoids the need for pyproj.

```sql
-- Enable PostGIS extension (already enabled in Supabase by default)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create a staging table with native BNG geometry
CREATE TEMP TABLE streets_staging_bng (
    os_id           TEXT,
    name1           TEXT,
    geometry_x      FLOAT,
    geometry_y      FLOAT,
    local_type      TEXT,
    populated_place TEXT,
    county_unitary  TEXT,
    postcode_district TEXT,
    country         TEXT
);

-- After loading staging data, convert and insert into the target table
INSERT INTO streets (id, name, latitude, longitude, city, county, postcode_area)
SELECT
    os_id,
    name1,
    ST_Y(ST_Transform(ST_SetSRID(ST_MakePoint(geometry_x, geometry_y), 27700), 4326)) AS latitude,
    ST_X(ST_Transform(ST_SetSRID(ST_MakePoint(geometry_x, geometry_y), 27700), 4326)) AS longitude,
    populated_place,
    county_unitary,
    postcode_district
FROM streets_staging_bng;
```

### Coordinate Sanity Check

After conversion, valid UK WGS84 coordinates must fall within:

| Bound | Longitude | Latitude |
|-------|-----------|---------|
| Southwest | -8.65 | 49.86 |
| Northeast | 1.77 | 60.86 |

Any row outside these bounds indicates a conversion error or a data quality issue.

---

## 5. Filtering

The full OS OpenNames dataset contains multiple feature types. Streets Past only needs road features.

### TYPE Filter

Only include rows where `TYPE = 'transportNetwork'`.

This excludes populated places, postcodes, administrative units, and other non-road features.

### LOCAL_TYPE Filter

Within `transportNetwork`, include only road-type entries:

| LOCAL_TYPE Value | Description | Include |
|-----------------|-------------|---------|
| `Named Road` | A road with an official name (e.g., "High Street") | Yes |
| `Numbered Road` | A numbered route without a local name (e.g., "A303") | Yes |
| `Section Of Named Road` | A named section or alias of a road | Yes |
| `Motorway` | Motorway designations (M1, M25, etc.) | Optional |
| `Ferry Route` | Ferry crossings | No |
| `Ferry Terminal` | Ferry terminal points | No |
| `Road Junction` | Junction reference points | No |
| `Postcode` | Postcode centroids (even if in transportNetwork) | No |

For Streets Past, the recommended filter is:

```python
ROAD_LOCAL_TYPES = {
    "Named Road",
    "Numbered Road",
    "Section Of Named Road",
    "Motorway",
}
```

Motorways are optional. They add approximately 8,000 records and are useful for completeness, but many carry no street-etymology value. Include them unless storage is a concern.

### Approximate Record Counts After Filtering

| Filter Applied | Approximate Count |
|---------------|-------------------|
| All records | ~1,900,000 |
| TYPE = transportNetwork | ~870,000 |
| + Named Road only | ~610,000 |
| + Named Road + Numbered Road | ~790,000 |
| + Named Road + Numbered Road + Motorway | ~798,000 |

---

## 6. CSV Preprocessing Script

This script reads all CSV files in the OS OpenNames `DATA/` directory, filters for road features, converts coordinates, and outputs a single clean CSV ready for database loading.

```python
#!/usr/bin/env python3
"""
preprocess_os_opennames.py

Preprocesses OS OpenNames CSV data for import into the Streets Past Supabase database.

Usage:
    python preprocess_os_opennames.py \
        --input-dir /path/to/opname_csv_gb/DATA \
        --output /path/to/streets_clean.csv

Requirements:
    pip install pyproj pandas tqdm
"""

import argparse
import csv
import logging
import os
import sys
from pathlib import Path

import pandas as pd
from pyproj import Transformer
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── Configuration ────────────────────────────────────────────────────────────

# Only rows with these LOCAL_TYPE values are imported
ROAD_LOCAL_TYPES = {
    "Named Road",
    "Numbered Road",
    "Section Of Named Road",
    "Motorway",
}

# Column mapping: OS OpenNames → Streets Past database columns
# Keys are OS column names, values are target column names
COLUMN_MAP = {
    "ID":                   "os_id",
    "NAME1":                "name",
    "NAME2":                "name_alt",
    "LOCAL_TYPE":           "local_type",
    "POPULATED_PLACE":      "city",
    "COUNTY_UNITARY":       "county",
    "POSTCODE_DISTRICT":    "postcode_area",
    "COUNTRY":              "country",
    "REGION":               "region",
    "DISTRICT_BOROUGH":     "district",
}

# Expected WGS84 bounding box for Great Britain
WGS84_BOUNDS = {
    "lon_min": -8.65,
    "lon_max":  1.77,
    "lat_min": 49.86,
    "lat_max": 60.86,
}

# ─── Coordinate Transformer ───────────────────────────────────────────────────

# Build once; reuse for every row (significant performance gain)
BNG_TO_WGS84 = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)


def convert_coords(easting: float, northing: float) -> tuple[float, float] | tuple[None, None]:
    """Convert OSGB36 BNG eastings/northings to WGS84 lon/lat."""
    try:
        lon, lat = BNG_TO_WGS84.transform(float(easting), float(northing))
        # Reject coordinates outside Great Britain bounding box
        if not (WGS84_BOUNDS["lon_min"] <= lon <= WGS84_BOUNDS["lon_max"]):
            return None, None
        if not (WGS84_BOUNDS["lat_min"] <= lat <= WGS84_BOUNDS["lat_max"]):
            return None, None
        return round(lon, 7), round(lat, 7)
    except (ValueError, TypeError):
        return None, None


# ─── Processing ───────────────────────────────────────────────────────────────

def process_csv_file(filepath: Path, transformer: Transformer) -> list[dict]:
    """
    Read a single OS OpenNames CSV file and return filtered, cleaned rows.
    """
    rows = []

    try:
        df = pd.read_csv(
            filepath,
            dtype=str,          # Read everything as string; we parse manually
            keep_default_na=False,
            low_memory=False,
        )
    except Exception as exc:
        log.warning(f"Failed to read {filepath.name}: {exc}")
        return rows

    # Normalise column names (strip whitespace)
    df.columns = df.columns.str.strip()

    # Check required columns are present
    required = {"TYPE", "LOCAL_TYPE", "NAME1", "GEOMETRY_X", "GEOMETRY_Y"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        log.warning(f"{filepath.name}: missing columns {missing}, skipping")
        return rows

    # Filter: transport network and road local types only
    mask = (
        (df["TYPE"] == "transportNetwork") &
        (df["LOCAL_TYPE"].isin(ROAD_LOCAL_TYPES)) &
        (df["NAME1"].str.strip() != "")
    )
    df = df[mask].copy()

    if df.empty:
        return rows

    for _, row in df.iterrows():
        # Convert coordinates
        try:
            easting  = float(row.get("GEOMETRY_X", ""))
            northing = float(row.get("GEOMETRY_Y", ""))
        except (ValueError, TypeError):
            continue

        lon, lat = convert_coords(easting, northing)
        if lon is None:
            continue  # Skip rows with invalid coordinates

        # Build output record
        record = {
            "longitude": lon,
            "latitude":  lat,
        }

        for os_col, db_col in COLUMN_MAP.items():
            record[db_col] = row.get(os_col, "").strip() or None

        # Clean up name: strip leading/trailing whitespace, collapse internal spaces
        if record.get("name"):
            record["name"] = " ".join(record["name"].split())

        rows.append(record)

    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess OS OpenNames CSV files for Supabase import"
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Path to the OS OpenNames DATA/ directory (contains per-grid-square CSVs)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the output cleaned CSV file",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional: limit total rows written (useful for testing)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_path = Path(args.output)

    if not input_dir.is_dir():
        log.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)

    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        log.error(f"No CSV files found in {input_dir}")
        sys.exit(1)

    log.info(f"Found {len(csv_files)} CSV files in {input_dir}")

    all_rows = []
    skipped_coords = 0

    for csv_file in tqdm(csv_files, desc="Processing grid squares"):
        file_rows = process_csv_file(csv_file, BNG_TO_WGS84)
        all_rows.extend(file_rows)

        if args.limit and len(all_rows) >= args.limit:
            all_rows = all_rows[:args.limit]
            log.info(f"Reached row limit of {args.limit}")
            break

    log.info(f"Total road records after filtering: {len(all_rows):,}")

    if not all_rows:
        log.error("No records to write. Check filter settings.")
        sys.exit(1)

    # Define output column order
    fieldnames = [
        "os_id", "name", "name_alt", "local_type",
        "city", "county", "postcode_area", "district", "region", "country",
        "latitude", "longitude",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        writer.writerows(all_rows)

    log.info(f"Output written to: {output_path}")
    log.info(f"Total rows: {len(all_rows):,}")


if __name__ == "__main__":
    main()
```

### Running the Script

```bash
# Basic run
python preprocess_os_opennames.py \
    --input-dir ~/os-opennames-data/DATA \
    --output ~/os-opennames-data/streets_clean.csv

# Test run with row limit (useful for sanity-checking the output)
python preprocess_os_opennames.py \
    --input-dir ~/os-opennames-data/DATA \
    --output ~/os-opennames-data/streets_test.csv \
    --limit 10000
```

### Expected Output

The output CSV will have these columns:

```
os_id, name, name_alt, local_type, city, county, postcode_area, district, region, country, latitude, longitude
```

Example rows:

```csv
os_id,name,name_alt,local_type,city,county,postcode_area,district,region,country,latitude,longitude
osgb4000000074569285,High Street,,Named Road,Oxford,Oxfordshire,OX1,Oxford,South East,England,51.7519674,-1.2577899
osgb4000000074219073,Castle Street,,Named Road,Edinburgh,City of Edinburgh,EH1,Edinburgh,Scotland,Scotland,55.9494178,-3.1973882
```

Processing time for the full dataset is approximately 8–15 minutes on a standard laptop.

---

## 7. Database Loading

### 7.1 Prepare the Target Table

Before loading, ensure the `streets` table exists with the correct schema. Run this migration if starting fresh:

```sql
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create the streets table
CREATE TABLE IF NOT EXISTS streets (
    id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    os_id                 TEXT UNIQUE,           -- OS OpenNames ID for upsert deduplication
    name                  TEXT NOT NULL,
    name_alt              TEXT,                  -- Welsh/Gaelic alternative name
    local_type            TEXT,                  -- Named Road / Numbered Road / etc.
    city                  TEXT,
    county                TEXT,
    postcode_area         TEXT,                  -- Postcode district, e.g. "SW1A"
    district              TEXT,
    region                TEXT,
    country               TEXT,
    latitude              DOUBLE PRECISION,
    longitude             DOUBLE PRECISION,
    geom                  GEOMETRY(POINT, 4326), -- PostGIS geometry column
    etymology_suggestion  TEXT,
    etymology_verified    BOOLEAN DEFAULT FALSE,
    historical_period     TEXT,
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ DEFAULT NOW()
);
```

### 7.2 Option A: psql \copy (Recommended for Bulk Load)

`\copy` streams data directly through the client connection and is the fastest method for large datasets. It does not require superuser privileges, unlike the server-side `COPY` command.

```bash
psql "$SUPABASE_DB_URL" <<'SQL'
\copy streets (os_id, name, name_alt, local_type, city, county, postcode_area, district, region, country, latitude, longitude)
FROM '/path/to/streets_clean.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');
SQL
```

After the initial load, populate the PostGIS geometry column:

```sql
UPDATE streets
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE geom IS NULL
  AND latitude IS NOT NULL
  AND longitude IS NOT NULL;
```

Estimated load time: 3–7 minutes for ~790,000 rows depending on network latency to Supabase.

### 7.3 Option B: Supabase Dashboard CSV Import

The Supabase Table Editor supports CSV import for smaller datasets (up to ~50,000 rows reliably). For the full ~790,000 row dataset, use the `psql \copy` method instead.

Steps for smaller batches:
1. Go to **Table Editor** in the Supabase dashboard
2. Select the `streets` table
3. Click **Import Data** (top right)
4. Upload the CSV file
5. Map columns to table columns
6. Click **Import**

### 7.4 Option C: Supabase JS SDK Batch Insert

Use this approach if loading from a Node.js script or when adding incremental records programmatically. The Supabase SDK supports upsert operations for quarterly refreshes.

```typescript
import { createClient } from "@supabase/supabase-js";
import fs from "fs";
import Papa from "papaparse";

const supabase = createClient(
  process.env.VITE_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY! // Use service role key for bulk writes
);

const BATCH_SIZE = 1000; // Supabase recommends batches of 500–2000 rows

interface StreetRow {
  os_id: string;
  name: string;
  name_alt: string | null;
  local_type: string | null;
  city: string | null;
  county: string | null;
  postcode_area: string | null;
  latitude: number;
  longitude: number;
}

async function loadStreets(csvPath: string) {
  const content = fs.readFileSync(csvPath, "utf-8");
  const { data } = Papa.parse<StreetRow>(content, {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
  });

  console.log(`Loaded ${data.length} rows from CSV`);

  let inserted = 0;
  let errors = 0;

  for (let i = 0; i < data.length; i += BATCH_SIZE) {
    const batch = data.slice(i, i + BATCH_SIZE);

    const { error } = await supabase
      .from("streets")
      .upsert(batch, {
        onConflict: "os_id",        // Use os_id as the unique key for upserts
        ignoreDuplicates: false,    // Update existing rows on conflict
      });

    if (error) {
      console.error(`Batch ${i / BATCH_SIZE + 1} error:`, error.message);
      errors++;
    } else {
      inserted += batch.length;
      if (i % 50000 === 0) {
        console.log(`Progress: ${inserted.toLocaleString()} / ${data.length.toLocaleString()}`);
      }
    }
  }

  console.log(`Done. Inserted/updated: ${inserted.toLocaleString()}, Errors: ${errors}`);
}

loadStreets("streets_clean.csv").catch(console.error);
```

Note: The SDK method is significantly slower than `psql \copy` for large datasets (~790,000 rows). Expect 30–90 minutes depending on network latency and batch size. Use `psql \copy` for the initial full load and the SDK for incremental updates.

---

## 8. Post-Load Indexing

Create these indexes immediately after the bulk load. Do not create them before loading — it is much faster to index after the data is in place.

```sql
-- ─── B-tree index for name search (case-insensitive prefix matching) ───────
CREATE INDEX IF NOT EXISTS idx_streets_name
    ON streets (name);

-- ─── B-tree index for lowercase name (used by ilike queries in SearchBar) ──
CREATE INDEX IF NOT EXISTS idx_streets_name_lower
    ON streets (lower(name));

-- ─── GiST index for spatial queries (bbox, nearest-neighbour) ──────────────
CREATE INDEX IF NOT EXISTS idx_streets_geom
    ON streets USING GIST (geom);

-- ─── B-tree index for coordinate lookups (map viewport filtering) ───────────
CREATE INDEX IF NOT EXISTS idx_streets_lat_lon
    ON streets (latitude, longitude);

-- ─── B-tree index for postcode_area prefix search ───────────────────────────
CREATE INDEX IF NOT EXISTS idx_streets_postcode_area
    ON streets (postcode_area);

-- ─── B-tree index for county-based filtering ────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_streets_county
    ON streets (county);

-- ─── B-tree index for OS ID (upsert deduplication key) ──────────────────────
-- This index is created automatically by the UNIQUE constraint on os_id.
-- If not, create it explicitly:
CREATE UNIQUE INDEX IF NOT EXISTS idx_streets_os_id
    ON streets (os_id);

-- ─── Full-text search index (optional: for future full-text search feature) ─
CREATE INDEX IF NOT EXISTS idx_streets_name_fts
    ON streets USING GIN (to_tsvector('english', name));
```

### Verify Indexes

```sql
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'streets'
ORDER BY indexname;
```

### Analyze the Table

After creating indexes, update the query planner statistics:

```sql
ANALYZE streets;
```

---

## 9. Quarterly Refresh Workflow

OS OpenNames is updated in January, April, July, and October. Use this workflow each quarter to keep the Streets Past database current.

### 9.1 Refresh Process Overview

```
1. Download new OS OpenNames release
2. Run preprocessing script → new streets_clean_YYYY_QN.csv
3. Load into a staging table
4. Diff against production: find new, changed, and deleted records
5. Upsert new and changed records into streets table
6. (Optional) Flag or remove deleted records
7. Validate row counts and coordinate sanity
8. Update the last_updated metadata record
```

### 9.2 Staging Table for Diff

```sql
-- Create a temporary staging table for the new release
CREATE TEMP TABLE streets_staging (LIKE streets INCLUDING ALL);

-- Load the new CSV into staging
\copy streets_staging (os_id, name, name_alt, local_type, city, county, postcode_area, district, region, country, latitude, longitude)
FROM '/path/to/streets_clean_2026_Q2.csv'
WITH (FORMAT CSV, HEADER TRUE, NULL '');

-- Update geom column in staging
UPDATE streets_staging
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
```

### 9.3 Upsert Changed and New Records

```sql
-- Upsert: insert new records, update changed records
-- Keyed on os_id (the OS OpenNames unique identifier)
INSERT INTO streets (
    os_id, name, name_alt, local_type,
    city, county, postcode_area, district, region, country,
    latitude, longitude, geom, updated_at
)
SELECT
    s.os_id, s.name, s.name_alt, s.local_type,
    s.city, s.county, s.postcode_area, s.district, s.region, s.country,
    s.latitude, s.longitude, s.geom, NOW()
FROM streets_staging s
ON CONFLICT (os_id) DO UPDATE SET
    name           = EXCLUDED.name,
    name_alt       = EXCLUDED.name_alt,
    local_type     = EXCLUDED.local_type,
    city           = EXCLUDED.city,
    county         = EXCLUDED.county,
    postcode_area  = EXCLUDED.postcode_area,
    district       = EXCLUDED.district,
    region         = EXCLUDED.region,
    country        = EXCLUDED.country,
    latitude       = EXCLUDED.latitude,
    longitude      = EXCLUDED.longitude,
    geom           = EXCLUDED.geom,
    updated_at     = NOW()
-- Only update if something actually changed (avoids unnecessary writes)
WHERE
    streets.name           IS DISTINCT FROM EXCLUDED.name OR
    streets.latitude       IS DISTINCT FROM EXCLUDED.latitude OR
    streets.longitude      IS DISTINCT FROM EXCLUDED.longitude OR
    streets.city           IS DISTINCT FROM EXCLUDED.city OR
    streets.county         IS DISTINCT FROM EXCLUDED.county OR
    streets.postcode_area  IS DISTINCT FROM EXCLUDED.postcode_area;
```

### 9.4 Identify Deleted Records (Optional)

OS OpenNames occasionally removes or merges road entries. If referential integrity matters (e.g., contributions reference a deleted street), mark them rather than hard-deleting:

```sql
-- Add a soft-delete column if not already present
ALTER TABLE streets ADD COLUMN IF NOT EXISTS os_deleted BOOLEAN DEFAULT FALSE;

-- Flag streets in the production table that no longer appear in the new release
UPDATE streets
SET os_deleted = TRUE
WHERE os_id NOT IN (SELECT os_id FROM streets_staging)
  AND os_deleted = FALSE;

-- Count affected rows
SELECT COUNT(*) FROM streets WHERE os_deleted = TRUE;
```

### 9.5 Refresh Checklist

```
[ ] Download new OS OpenNames CSV ZIP from OS Data Hub
[ ] Extract to working directory
[ ] Run preprocess_os_opennames.py with --output including the release quarter
[ ] Inspect output: check row count is within ±5% of previous release
[ ] Load into streets_staging table
[ ] Run upsert query
[ ] Run validation queries (see Section 10)
[ ] Update changelog / metadata table with release date and row count
[ ] Drop streets_staging temp table
[ ] Run ANALYZE streets;
```

---

## 10. Data Validation

Run these checks after every load (initial and quarterly refresh).

### 10.1 Row Count Check

```sql
-- Total rows in the streets table
SELECT COUNT(*) AS total_streets FROM streets;

-- Breakdown by local_type
SELECT
    local_type,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
FROM streets
GROUP BY local_type
ORDER BY count DESC;

-- Breakdown by country
SELECT
    country,
    COUNT(*) AS count
FROM streets
GROUP BY country
ORDER BY count DESC;
```

Expected results (approximate):

| country | count |
|---------|-------|
| England | ~680,000 |
| Scotland | ~75,000 |
| Wales | ~35,000 |

### 10.2 Coordinate Sanity Checks

```sql
-- Check for NULL coordinates
SELECT COUNT(*) AS null_coords
FROM streets
WHERE latitude IS NULL OR longitude IS NULL;

-- Check for out-of-bounds coordinates (should return 0)
SELECT COUNT(*) AS out_of_bounds
FROM streets
WHERE latitude  < 49.86 OR latitude  > 60.86
   OR longitude < -8.65 OR longitude > 1.77;

-- Check coordinate ranges (min/max should be within UK bounds)
SELECT
    MIN(latitude)   AS min_lat,
    MAX(latitude)   AS max_lat,
    MIN(longitude)  AS min_lon,
    MAX(longitude)  AS max_lon
FROM streets;

-- Check PostGIS geometry is populated
SELECT
    COUNT(*) FILTER (WHERE geom IS NOT NULL) AS has_geom,
    COUNT(*) FILTER (WHERE geom IS NULL)     AS missing_geom,
    COUNT(*) AS total
FROM streets;
```

### 10.3 Null Detection on Key Fields

```sql
-- Check for null or empty values in critical columns
SELECT
    COUNT(*) FILTER (WHERE name IS NULL OR name = '')      AS null_name,
    COUNT(*) FILTER (WHERE os_id IS NULL OR os_id = '')    AS null_os_id,
    COUNT(*) FILTER (WHERE county IS NULL)                 AS null_county,
    COUNT(*) FILTER (WHERE city IS NULL)                   AS null_city,
    COUNT(*) FILTER (WHERE postcode_area IS NULL)          AS null_postcode_area,
    COUNT(*) AS total
FROM streets;
```

Note: `county` and `city` nulls are expected for some records in remote areas or where OS OpenNames does not populate these fields. `name` and `os_id` nulls should be zero.

### 10.4 Duplicate Detection

```sql
-- Check for duplicate os_id values (should return 0 if UNIQUE constraint is working)
SELECT os_id, COUNT(*) AS cnt
FROM streets
GROUP BY os_id
HAVING COUNT(*) > 1
LIMIT 20;

-- Check for exact duplicate name+county combinations
SELECT name, county, COUNT(*) AS cnt
FROM streets
GROUP BY name, county
HAVING COUNT(*) > 5
ORDER BY cnt DESC
LIMIT 20;
```

High counts for name+county (e.g., "High Street, Yorkshire" appearing 40+ times) are expected and correct — there are genuinely many streets with the same name in the same county.

### 10.5 Spatial Query Smoke Test

```sql
-- Find streets within 1km of central London (Trafalgar Square)
-- lon: -0.1281, lat: 51.5081
SELECT name, city, county, postcode_area,
       ST_Distance(
           geom::geography,
           ST_SetSRID(ST_MakePoint(-0.1281, 51.5081), 4326)::geography
       ) AS distance_metres
FROM streets
WHERE ST_DWithin(
    geom::geography,
    ST_SetSRID(ST_MakePoint(-0.1281, 51.5081), 4326)::geography,
    1000  -- 1000 metres
)
ORDER BY distance_metres
LIMIT 10;
```

This query should return results in under 100ms with the GiST index in place.

---

## 11. Attribution and License Compliance

### License

OS OpenNames is provided under the **OS OpenData Licence**, which is compatible with the Open Government Licence (OGL) v3.0. Commercial use is permitted. The full licence text is at:

```
https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
```

### Required Attribution

Every product, page, or API response that uses data derived from OS OpenNames **must** include the following attribution:

```
Contains OS data © Crown copyright and database right 2026.
```

Update the year each time you refresh from a new OS OpenNames release.

### Where to Display Attribution

For Streets Past, attribution must appear in:

1. **Footer** (`street-etymology/src/components/Footer.tsx`) — on every page
2. **About page** (`street-etymology/src/pages/AboutPage.tsx`) — with a dedicated data sources section
3. **Map page** (`street-etymology/src/pages/MapPage.tsx`) — as a map attribution overlay (MapLibre attribution control)
4. **API responses** — if any public API endpoints return street data, include attribution in the response metadata or documentation
5. **README / documentation** — any developer-facing documentation

### MapLibre Attribution Control

Add the OS attribution to the MapLibre map in `MapView.tsx`:

```typescript
const map = new maplibregl.Map({
  container: mapContainer.current,
  style: { /* ... */ },
  attributionControl: true,
  customAttribution: "Contains OS data © Crown copyright and database right 2026",
});
```

### What You Must Not Do

- Do not remove or obscure the attribution
- Do not claim that the data is your own original work
- Do not suggest that Ordnance Survey endorses Streets Past
- Do not use the OS logo without a separate agreement

### Attribution for Combined Datasets

If postcode data (Code-Point Open) is also loaded, use the combined attribution:

```
Contains OS data © Crown copyright and database right 2026.
Contains Royal Mail data © Royal Mail copyright and database right 2026.
Licensed under the Open Government Licence v3.0.
```

---

## Appendix A: Quick Reference — Column Mapping

| OS OpenNames Column | Streets Past Column | Notes |
|--------------------|---------------------|-------|
| `ID` | `os_id` | Unique identifier; used as upsert key |
| `NAME1` | `name` | Primary street name |
| `NAME2` | `name_alt` | Welsh/Gaelic alternative (nullable) |
| `LOCAL_TYPE` | `local_type` | Road classification |
| `POPULATED_PLACE` | `city` | Town/village name |
| `COUNTY_UNITARY` | `county` | County or unitary authority |
| `POSTCODE_DISTRICT` | `postcode_area` | e.g., "SW1A" |
| `DISTRICT_BOROUGH` | `district` | District or borough name |
| `REGION` | `region` | OS region |
| `COUNTRY` | `country` | England / Wales / Scotland |
| `GEOMETRY_X` | *(converted)* | Easting → `longitude` (WGS84) |
| `GEOMETRY_Y` | *(converted)* | Northing → `latitude` (WGS84) |
| *(derived)* | `geom` | PostGIS POINT(longitude, latitude) |

---

## Appendix B: Troubleshooting

### "No module named pyproj"

```bash
pip install pyproj
# or with conda:
conda install -c conda-forge pyproj
```

### Coordinates converting to wrong location

Verify the input is genuinely OSGB36 (EPSG:27700). Valid BNG eastings for Great Britain are in the range 0–700,000 and northings 0–1,300,000. If values are outside this range, they may already be in WGS84 or another CRS.

```python
# Quick sanity check
print(f"Easting range: {df['GEOMETRY_X'].astype(float).min():.0f} – {df['GEOMETRY_X'].astype(float).max():.0f}")
print(f"Northing range: {df['GEOMETRY_Y'].astype(float).min():.0f} – {df['GEOMETRY_Y'].astype(float).max():.0f}")
```

### psql \copy permission denied

The `\copy` command (client-side) does not require database superuser access. If you are using the server-side `COPY` command instead, you will need superuser. Always use `\copy` (lowercase, with backslash) in the psql client.

### Upsert failing with "duplicate key value violates unique constraint"

This happens if `os_id` is not set as UNIQUE. Ensure the column has a UNIQUE constraint:

```sql
ALTER TABLE streets ADD CONSTRAINT streets_os_id_key UNIQUE (os_id);
```

### Supabase free tier storage limit

The Supabase free tier includes 500 MB of database storage. The full `streets` table with ~790,000 rows and indexes is approximately 300–450 MB depending on the average column lengths. This fits within the free tier, but leaves limited headroom for contributions, profiles, and other tables. Monitor storage in the Supabase dashboard and upgrade to Pro ($25/month, 8 GB included) before hitting the limit.
