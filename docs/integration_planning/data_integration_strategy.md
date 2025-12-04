# UK Postcode, County, Local Authority, and Street Name Integration into Supabase: Technical Implementation Strategy

## Executive Summary and Objectives

This strategy sets out an authoritative, production-grade approach to integrating United Kingdom postcode, county, local authority, and street name data into Supabase (PostgreSQL) for search, address/autocomplete, analytics, and heritage enrichment. It builds on the principal open datasets available from Ordnance Survey (OS), the Office for National Statistics (ONS), and Historic England, and aligns refresh schedules and licensing across sources to ensure compliance and operational resilience. The plan prioritises a tabular, relational model that is index-first, with PostGIS enabled for spatial functionality. British National Grid (EPSG:27700) is retained as the analytical standard; WGS84 (EPSG:4326) is provided as a service layer for web mapping. The design deliberately supports incremental updates, robust validation, and auditability.

The primary sources are OS OpenNames (street backbone) for Great Britain; Code-Point Open (GB postcode units) and the ONS Postcode Directory (UK-wide lookups) for postcode enrichment and roll-ups; Boundary-Line (GB) and ONS Open Geography (UK-wide boundaries) for administrative context; and the National Heritage List for England (NHLE) and related Historic England layers for heritage overlays[^1][^2][^10][^13][^14][^15][^5][^7][^21]. Together they offer predictable refresh cycles, open licensing under OS Open Data and Open Government Licence (OGL) v3.0, and sufficient geometry and attributes to support robust address geocoding, spatial joins, and heritage enrichment.

Success will be measured by production-grade query performance for common workloads (e.g., prefix search, locality roll-ups), validated spatial integrity (correct projections, SRID handling, bbox checks), end-to-end data quality (non-nullable constraints, referential lookups, coordinate range checks), reliable and repeatable batch imports aligned to source cadence, and comprehensive licence attribution persisted in metadata.

To frame the integration challenge at a glance, Table 1 summarises the source landscape across coverage, formats, and update cycles.

Table 1. Source landscape overview (formats, coverage, update cycles, licences)

| Dataset | Coverage | Formats | Update frequency | Licence | Primary attribution |
|---|---|---|---|---|---|
| OS OpenNames | Great Britain | CSV, GML, GeoPackage | Quarterly (Jan/Apr/Jul/Oct) | OS Open Data Licence | OS attribution; GB focus[^1][^2][^3][^18] |
| Code-Point Open | Great Britain | CSV, GeoPackage | Quarterly | OGL v3.0 | OGL; OS; Royal Mail; National Statistics[^9][^10][^11][^20][^12] |
| ONS Postcode Directory (ONSPD) | United Kingdom | Multi-CSV; GIS-ready | Regular releases | OGL v3.0 | OGL; ONS/OS rights; NI may need extra terms[^13][^12] |
| Boundary-Line | Great Britain | Vector GIS | Twice yearly (May/Oct) | OGL v3.0 | OGL; OS rights[^14][^15] |
| ONS Open Geography | United Kingdom | GIS (full/generalised/clipped) | Per ONS schedule | OGL v3.0 | OGL; ONS/OS rights[^21][^24] |
| Historic England NHLE | England | GIS (points/polygons); spreadsheets (some) | Frequent; Heritage at Risk annual | OGL v3.0 | © Historic England [year]; OS data attribution[^5][^7][^4][^16] |

Information gaps are explicitly acknowledged, including dynamic OS Data Hub pages, item-level rights for British Library map images, separate Northern Ireland licences, dataset-level schemas, and heterogeneous local authority data standards. These do not prevent implementation but require validation during ingestion[^15][^27][^12][^3][^25].

### Scope

This strategy covers five technical domains: data transformation and model design, indexing for performance, spatial handling and coordinate systems, data validation and quality controls, and batch import with monitoring and rollback. It defines the ingestion and harmonisation of postcodes, administrative geographies (counties, local authorities), street names and street segments, and optional heritage overlays in England. Northern Ireland datasets are included conceptually with an explicit licensing caveat and are treated as out-of-scope for initial ingestion pending confirmation[^12].

### Success Metrics

Success is defined by:
- Query latency targets: prefix search returning top results within 50–150 ms p95 for typical filters; spatial joins completing within defined SLAs for production traffic.
- Data quality targets: 100% compliance with non-nullable and uniqueness constraints; valid SRID; coordinate ranges within GB/UK extents; referential integrity for administrative lookups.
- Operational metrics: reproducible batch imports aligned to source cadence; comprehensive attribution strings persisted in metadata; audit logs of lineage and transformations; deterministic, idempotent pipelines.

These metrics support predictable performance for web mapping and autocomplete, reliable analytics (e.g., postcode-to-LSOA/MSOA joins), and heritage overlays in England, using OS OpenNames, Code-Point Open, ONSPD, Boundary-Line, ONS Open Geography, and Historic England NHLE[^1][^10][^13][^14][^21][^7].

## Source Landscape and Licensing Foundations

The integration blueprint hinges on five cornerstone datasets and a licensing model that enables commercial reuse with attribution. OGL v3.0 underpins most sources, while OS OpenNames follows the OS Open Data Licence; third-party rights—especially Royal Mail for postcodes and OS Crown rights for geospatial data—must be acknowledged in attribution statements[^21][^12][^4][^18]. Boundary-Line and ONS Open Geography provide administrative and electoral boundary context; ONSPD extends postcode capabilities to the UK and supports statistical joins; Historic England datasets overlay heritage designations for England[^14][^24][^23][^13][^5][^7].

To consolidate the licensing and access picture, Table 2 details each source’s licence model and required attribution. These statements must be stored in metadata and surfaced in product documentation.

Table 2. Consolidated licensing and attribution matrix

| Source | Licence | Commercial use | Required attribution (examples) |
|---|---|---|---|
| OS OpenNames | OS OpenData Licence | Yes | “Contains OS data © Crown copyright and database right [year].”[^18] |
| Code-Point Open | OGL v3.0 | Yes | “Contains OS data © Crown copyright and database right [year]. Contains Royal Mail data © Royal Mail copyright and database right [year]. Contains National Statistics data © Crown copyright and database right [year]. Licensed under the Open Government Licence v3.0.”[^9][^10][^11][^12][^21] |
| Boundary-Line | OGL v3.0 | Yes | “Contains public sector information licensed under the Open Government Licence v3.0.” Add OS rights if spatial data includes OS geometry[^14][^15][^21]. |
| ONS Open Geography | OGL v3.0 | Yes | “Contains public sector information licensed under the Open Government Licence v3.0.” Add ONS/OS rights as applicable[^21][^24]. |
| ONSPD | OGL v3.0 | Yes | OGL statement; acknowledge ONS/OS rights; NI may require extra permissions[^13][^12]. |
| Historic England NHLE | OGL v3.0 | Yes | “© Historic England [year]. Contains Ordnance Survey data © Crown copyright and database right [year]. Licensed under the Open Government Licence v3.0.”[^7][^4][^21] |

Attribution templates (Table 3) should be persisted alongside dataset metadata and surfaced in “About”/legal pages.

Table 3. Attribution templates

| Scenario | Attribution text |
|---|---|
| OGL-only dataset | “Contains public sector information licensed under the Open Government Licence v3.0.”[^21] |
| OS geospatial (e.g., Boundary-Line, OpenNames) | “Contains OS data © Crown copyright and database right [year].”[^18][^15] |
| Code-Point Open | “Contains OS data © Crown copyright and database right [year]. Contains Royal Mail data © Royal Mail copyright and database right [year]. Contains National Statistics data © Crown copyright and database right [year]. Licensed under the Open Government Licence v3.0.”[^10][^12][^21] |
| Historic England spatial data | “© Historic England [year]. Contains Ordnance Survey data © Crown copyright and database right [year]. Licensed under the Open Government Licence v3.0.”[^7][^4] |
| Local authority dataset (OS present) | “Contains public sector information licensed under the Open Government Licence v3.0. Contains OS data © Crown copyright and database right [year].”[^25] |

### OS OpenNames

OS OpenNames provides road numbers/names, place names, and postcodes across Great Britain. It is delivered as CSV, GML, and GeoPackage; coordinates are in British National Grid (EPSG:27700); the release cadence is quarterly. The dataset includes alternative name forms in Welsh, Scots, and Gaelic, and is covered by OS OpenData terms that permit commercial reuse with attribution[^1][^2][^3][^18].

### Code-Point Open

Code-Point Open provides unit-level postcodes for Great Britain with grid references and administrative codes. It is distributed as CSV and GeoPackage, updated quarterly, and available via OS Data Hub and data.gov.uk. It is licensed under OGL v3.0, and the attribution should acknowledge OS, Royal Mail, and National Statistics rights; Northern Ireland postcodes are excluded from this product[^9][^10][^11][^20][^12].

### ONSPD (ONS Postcode Directory)

ONSPD is a UK-wide directory that enables postcode lookups across statistical and administrative geographies (e.g., LSOA, MSOA, local authority, region). It is accessed via ONS GeoPortal, uses OGL v3.0, and requires attention to third-party rights; Northern Ireland inclusion may be subject to additional licensing in some contexts[^13][^12][^24].

### Boundary-Line

Boundary-Line maps administrative and electoral boundaries for Great Britain, with vector GIS data updated twice yearly (May and October). It is accessed via OS Data Hub, and licensing follows OGL v3.0 with OS attribution as applicable[^14][^15][^24].

### ONS Open Geography

ONS Open Geography provides definitive UK boundary products across England, Wales, Scotland, and Northern Ireland, including full, generalised, and clipped variants designed for GIS. Licensing is OGL v3.0[^21][^24].

### Historic England NHLE

Historic England distributes NHLE and related datasets (e.g., Listed Buildings, Scheduled Monuments, Registered Parks and Gardens, Battlefields) via its Open Data Hub, typically as points and polygons in GIS formats. Many layers update frequently; the Heritage at Risk register is annual. Licensing is OGL v3.0, with required attributions to Historic England and OS, and explicit exclusions of logos and trademarks under open terms[^5][^7][^4][^16].

### Local Authority Open Data

DfT guidance recommends publishing in open formats (CSV/JSON/XML), adopting open standards, providing rich metadata, and applying OGL by default. Where OS data is present, authorities must meet OS attribution requirements[^25].

## Target Data Model in Supabase (Conceptual Schema)

The integration relies on a relational, factorised schema that separates street entities from postcodes and administrative hierarchies. PostGIS is enabled for spatial functionality. Canonical identifiers and deterministic keys ensure deduplication across sources. The design deliberately avoids proprietary geospatial dependencies while supporting efficient spatial queries.

The factorised design comprises: streets, postcodes, counties, local_authorities, and boundaries geometries. Administrative codes (e.g., GSS codes) are anchored to authoritative lookups and boundaries; ONSPD provides the glue for UK-wide joins across geographies[^13][^24].

Table 4 details the core entity dictionary.

Table 4. Core entity dictionary

| Entity | Description | Primary key | Key attributes |
|---|---|---|---|
| counties | Administrative counties (lookup) | county_id (UUID) | county_name (text), country (text: England/Wales/Scotland/NI), gss_county_code (text, unique nullable) |
| local_authorities | Local authority districts/unitary authorities (lookup) | la_id (UUID) | la_name (text), authority_type (text), gss_la_code (text, unique), county_id (UUID, nullable), country (text) |
| postcodes | Postcode units with attributes | postcode_id (UUID) | postcode_text (text, unique), postcode_area (text), postcode_district (text), grid_easting (int), grid_northing (int), wgs84_lat (numeric), wgs84_lon (numeric), admin_codes (JSONB) |
| streets | Street backbone (OpenNames) | street_id (UUID) | street_name (text), street_type (text), locality (text), alternative_names (JSONB), county_id (UUID), la_id (UUID), geometry_bng (geometry, SRID 27700), geometry_wgs84 (geometry, SRID 4326), source_refs (JSONB) |
| boundaries_uk | Boundary geometries | boundary_id (UUID) | gss_code (text), boundary_name (text), boundary_type (text), geometry (geometry, SRID 27700), country (text), version_tag (text) |

### Normalization Principles

Administrative geographies are modelled as explicit lookups. Names may vary by source or time (e.g., re-organisations), and historical versions are preserved using version_tag on boundaries and source_refs across tables. Canonical codes (e.g., GSS) are the stable pivot for joins, reducing reliance on name-only matches[^24].

### Keys and Deduplication

Deterministic keys are generated from source values, e.g., normalized postcode_text for postcodes and a composite hash of street_name, locality, county, and geometry proximity for streets. External identifiers (e.g., OS feature IDs, ONSPD codes) are captured in source_refs JSONB to anchor lineage[^10][^13].

### Metadata and Provenance

For each table, persist source_name, source_url (as a metadata reference), licence, attribution_text, obtained_at (timestamp), last_updated_at (source), and version_tag. These fields enable auditability and compliance and are essential for regulated operations[^21][^4].

## Data Transformation Requirements

Transformation begins with ingest staging tables for OS OpenNames, Code-Point Open, ONSPD, Boundary-Line, and ONS boundaries. Data is then normalised and conformed to canonical codes and SRIDs. The schema harmonisation maps source columns to internal fields, with transformations recorded in a runbook.

OS OpenNames uses EPSG:27700; derived WGS84 geometries (EPSG:4326) are produced for web clients. Both are persisted. ONSPD provides many-to-one postcode-to-geography joins, including LSOA/MSOA and local authority codes[^3][^11][^13][^15].

Table 5 summarises per-source transformation notes.

Table 5. Per-source transformation notes (formats, coordinate systems, key mappings)

| Source | Ingest format | Coordinate system | Key transformations |
|---|---|---|---|
| OS OpenNames | CSV/GeoPackage/GML | EPSG:27700 | Normalise street_name, street_type, locality, alternative names; derive WGS84 geometry; map to counties/local_authorities lookups; preserve source IDs in source_refs[^3]. |
| Code-Point Open | CSV/GeoPackage | EPSG:27700 | Parse postcode_text; derive postcode_area/district; convert BNG to lat/lon (EPSG:4326); capture admin_codes (LA, NHS, etc.); dedupe by postcode_text[^11][^20]. |
| ONSPD | Multi-CSV | N/A tabular; geometry via boundaries | Join postcodes to LSOA/MSOA/local authority/region; harmonise GSS codes; flag NI datasets for licensing checks; store lookup attributes in postcodes.admin_codes[^13][^24]. |
| Boundary-Line | Vector GIS | EPSG:27700 | Ingest multipolygons; harmonise codes/names; label administrative levels; persist boundary geometry; store version_tag and obtained_at[^15][^14]. |
| ONS Open Geography | GIS | EPSG:27700 (typical) | Ingest full/generalised/clipped variants; select generalised for web; harmonise GSS codes; tag country; preserve version; store geometry with SRID 27700[^24][^21]. |
| Historic England NHLE | GIS (points/polygons) | EPSG:27700 (typical) | Retain geometry SRID; normalise heritage attributes; persist dataset name, obtained_at, last_updated_at; link spatially to streets/postcodes where appropriate[^5][^7]. |

Table 6 provides a field-level mapping checklist.

Table 6. Field-level mapping checklist (source → internal field, transforms, constraints)

| Source field | Internal field | Transform | Constraint |
|---|---|---|---|
| OpenNames.road_number/name | streets.street_name | Upper/trim, Unicode normalisation | Not null |
| OpenNames.locality | streets.locality | Upper/trim, canonicalisation via lookup | Not null (for street backbone) |
| OpenNames.geometry (BNG) | streets.geometry_bng | None; SRID=27700 | Valid SRID; bbox within GB extent |
| OpenNames.alt_names | streets.alternative_names | JSONB array; language tags | Optional |
| Code-Point.postcode | postcodes.postcode_text | Normalise (uppercase, strip spaces) | Unique; not null |
| Code-Point.easting/northing | postcodes.grid_easting/grid_northing | None | Within GB BNG range |
| Derived lat/lon | postcodes.wgs84_lat/lon | ST_Transform from 27700 | Range checks [-90,90]/[-180,180] |
| ONSPD.lsoa_code | postcodes.admin_codes.lsoa | JSONB set | Optional (UK-wide coverage) |
| Boundary-Line.code/name | boundaries_uk.gss_code/name | Trim/canonicalise | Not null; unique per version_tag |
| ONS boundary.gss_code | boundaries_uk.gss_code | Trim/canonicalise | Not null; unique per version_tag |
| NHLE.dataset_name | metadata.dataset_name | Set from dataset | Not null |
| NHLE.geometry (BNG) | street/buildings geometry | Preserve SRID; optional reproject | Valid SRID; bbox checks |

### Coordinates and SRIDs

British National Grid (EPSG:27700) is the storage standard for analytical accuracy. WGS84 (EPSG:4326) is derived and stored for web mapping clients. Where geometry is missing, records are flagged and excluded from map layers, while retaining tabular joins. Transformations use ST_Transform and ST_SetSRID; bbox checks confirm coordinate ranges for GB/UK[^3][^11].

### Code Harmonisation

Canonical codes (e.g., GSS for local authorities and statistical units) are the primary join keys, preventing fragile name-only matches. ONSPD provides the mapping from postcode to LSOA/MSOA and local authority/region codes. Boundary datasets are normalised to these codes and country tags[^24][^13].

## Spatial Data Handling (Coordinates and Boundaries)

Spatial handling must address SRIDs, boundary simplification, and geometry types. The default storage is EPSG:27700; derived service layers in EPSG:4326 support web clients. For boundaries, generalised geometries are preferred for performance while clipped geometries are used when precise spatial overlays are required. Geometry storage is multipolygon for boundaries and point or linestring for streets and postcodes, reflecting source nature and intended usage[^15][^24].

Table 7 summarises SRID and geometry choices.

Table 7. SRID and geometry choices (storage vs service layers)

| Layer | Storage SRID | Geometry type | Service layer SRID | Notes |
|---|---|---|---|---|
| streets | 27700 | Point or linestring | 4326 | Derived service layer for web; bbox checks; SRID tags |
| postcodes | 27700 | Point (unit) | 4326 | Derived lat/lon persisted; used for geocoding and joins |
| boundaries_uk | 27700 | Multipolygon | 4326 (derived) | Generalised for display; clipped for precise overlays |
| heritage_overlays | 27700 | Point or polygon | 4326 (derived) | Used for spatial joins to streets/postcodes |

### Indexing Strategy

An index-first design underpins query performance. B-tree indexes cover exact and range lookups on canonical fields (postcodes, local authority IDs, GSS codes). GiST indexes cover spatial predicates (KNN, ST_DWithin, ST_Intersects). GIN/tsvector indexes support full-text search on street_name, locality, and alternative names. Covering indexes (with INCLUDE) and partial indexes are used where cardinality and workload warrant.

Table 8 maps indexes to queries.

Table 8. Index design matrix (tables × indexes × query patterns)

| Table | Index type | Columns | Query patterns | Expected selectivity |
|---|---|---|---|---|
| postcodes | B-tree | postcode_text UNIQUE | Exact postcode lookup | Very high |
| postcodes | B-tree | postcode_area, postcode_district | Prefix/area filters | Medium |
| postcodes | GiST | geometry (SRID 27700/4326) | ST_DWithin, KNN by distance | Spatial |
| streets | B-tree | county_id, la_id | Administrative filters | Medium |
| streets | GIN/tsvector | search_vector (name + locality) | Prefix/ftsearch autocomplete | High |
| streets | GiST | geometry_bng (27700), geometry_wgs84 (4326) | ST_Intersects, KNN | Spatial |
| boundaries_uk | B-tree | gss_code, boundary_type, country | Administrative joins | High |
| boundaries_uk | GiST | geometry (27700) | ST_Intersects (overlay) | Spatial |
| lookups | B-tree | gss_la_code, gss_county_code | Joins to postcodes/streets | High |

### Precision and Accuracy

BNG coordinates are retained for analytics; WGS84 service layers use derived lat/lon. Bounding box tests validate coordinates against GB/UK extents. For distances, prefer BNG for analytical precision; when using WGS84, document metre-to-degree conversion caveats and perform distance-based predicates accordingly[^3].

## Data Validation and Quality Control

Quality controls ensure referential integrity, uniqueness, and spatial validity. Range checks validate coordinate bounds; deduplication is applied using deterministic keys on postcodes and streets. Licensing checks confirm attribution strings per dataset; provenance metadata is persisted.

Table 9 summarises rule-to-field mapping.

Table 9. Validation rule matrix (rule → table → field → check SQL sketch)

| Rule | Table | Field | Check |
|---|---|---|---|
| Unique postcode | postcodes | postcode_text | UNIQUE constraint |
| Valid SRID | all spatial | geometry | ST_SRID(geometry) IN (27700, 4326) |
| Coordinate range (GB) | postcodes/streets | geometry | ST_MinX/MaxX/Y within GB extents |
| Non-nullable name | streets | street_name | CHECK (street_name IS NOT NULL) |
| Admin lookup integrity | streets | county_id, la_id | FK-like check to lookups (no FK) |
| Deduplication | postcodes | postcode_text | ON CONFLICT DO NOTHING (staging) |
| Deduplication | streets | composite hash | Hash on name+locality+county+geom |
| Attribution persistence | metadata | attribution_text | NOT NULL; linked to dataset |

### Automated QA

SQL-based schema checks confirm nullability, uniqueness, SRID, and geometry validity. Spatial predicates validate bbox containment, and KNN sanity checks confirm realistic coordinate clustering for streets and postcodes. These tests run in the pipeline’s QA stage to block ingestion when thresholds are not met.

## Batch Import Procedures

The pipeline supports staging tables, deterministic upserts, idempotent runs, and checkpointing. It is aligned to official release cadence: quarterly (OpenNames, Code-Point Open), twice yearly (Boundary-Line), and frequent (NHLE). Full refreshes are used when schemas change or code harmonisation requires rebuilds; otherwise, incremental delta loads are applied using checksums or last-modified markers where available[^2][^10][^15][^5].

Table 10 provides a cadence plan.

Table 10. Cadence plan (dataset → frequency → window → checkpoint)

| Dataset | Frequency | Target window | Checkpoint |
|---|---|---|---|
| OS OpenNames | Quarterly | Jan/Apr/Jul/Oct | Persist dataset_version, obtained_at |
| Code-Point Open | Quarterly | Jan/Apr/Jul/Oct | Persist dataset_version, obtained_at |
| ONSPD | Regular releases | As per ONS | Persist release tag, obtained_at |
| Boundary-Line | Twice yearly | May/Oct | Persist version_tag, obtained_at |
| ONS Open Geography | Per ONS schedule | As announced | Persist product version, obtained_at |
| Historic England NHLE | Frequent; HAR annual | Rolling | Persist last_updated_at per dataset |

Table 11 outlines the operational runbook.

Table 11. Operational runbook (step → command/stage → rollback)

| Step | Stage | Rollback |
|---|---|---|
| Download | Pull dataset artifacts from OS Data Hub/ONS GeoPortal/Historic England | Revert to prior version in metadata; do not overwrite |
| Verify checksum | Confirm dataset integrity | Abort pipeline; raise incident |
| Validate schema | Check required fields present | Halt ingest; update mapping |
| Transform | Normalise, harmonise codes, derive SRIDs | Log transformation lineage; abort on fatal errors |
| Load staging | Insert into staging tables | TRUNCATE staging on failure |
| Deduplicate | Deterministic keys and checksums | Keep prior canonical records |
| Upsert to prod | Idempotent upserts using unique constraints | Rollback to prior snapshot |
| Publish metrics | Latency, row counts, error rates | Investigate breaches; roll forward after fix |

### Logging and Audit

All transformations are logged with lineage: source name, dataset version, obtained_at, attribution_text, and mapping version. Monitoring covers row counts, duplicate rates, spatial validation failures, and attribution compliance checks. These artifacts underpin traceability and compliance for audits[^4][^21].

## Estimated Data Volumes and Processing Requirements

The integration involves substantial tabular and spatial datasets. Code-Point Open includes approximately 1.7 million postcode units; OS OpenNames covers in the order of 870,000+ named/numbered roads, ~44,000 settlements, and 1.6M+ postcodes. Boundary datasets have high vertex counts across administrative units; NHLE layers include tens of thousands of designated heritage features, with many updated frequently[^20][^2][^14][^7].

Table 12 provides a volumetric summary.

Table 12. Volumetric summary (dataset → estimated count → file sizes → geometry type)

| Dataset | Estimated count | File sizes (indicative) | Geometry type |
|---|---|---|---|
| OS OpenNames | 870k+ roads; ~44k settlements; 1.6M+ postcodes | Varies by format | Points/lines |
| Code-Point Open | ~1.7M postcode units | CSV/GeoPackage | Points |
| ONSPD | UK postcodes with geography joins | Multi-CSV | N/A (tabular) |
| Boundary-Line | Administrative/electoral units | Vector GIS | Multipolygons |
| ONS Open Geography | UK-wide statistical/administrative | GIS (full/generalised/clipped) | Multipolygons |
| NHLE | Listed Buildings; Scheduled Monuments; etc. | GIS layers | Points/polygons |

### Compute and I/O Estimates

Spatial joins and index builds are the dominant workloads. Memory sizing should accommodate bulk inserts and spatial index creation; batching reduces I/O amplification. Staging and production tables require separate temp tablespaces where possible. Derived SRID transformations (27700 → 4326) are performed once and persisted to avoid runtime overhead.

## Operational Monitoring, Metadata, and Compliance

Operational resilience depends on persisted metadata, compliance checks, and transparent publication. Dataset version tags, last_updated_at, source_url (as metadata), and attribution_text must be stored and displayed. Audit logs track ingestion, transformations, and failures. Compliance spans licence conformance (OGL, OS OpenData), third-party rights acknowledgements (OS, Royal Mail, National Statistics), data protection (no personal data), and Northern Ireland licensing caveats[^12][^21][^4].

Table 13 provides a compliance checklist.

Table 13. Compliance checklist (item → source → status → owner)

| Item | Source | Status | Owner |
|---|---|---|---|
| OGL attribution present | All OGL datasets | Pending/Complete | Data Governance |
| OS attribution present | OS OpenData products | Pending/Complete | Data Governance |
| Royal Mail acknowledgement | Code-Point Open | Pending/Complete | Legal |
| NI licensing verified | ONSPD/NI boundaries | Pending/Complete | Legal |
| Dataset last_updated_at persisted | All | Pending/Complete | Data Ops |
| Data protection review | All | Pending/Complete | Compliance |
| Endorsement avoidance | All | Pending/Complete | Product |
| Item-level rights review | British Library maps | Pending/Complete | Legal |

### Publication Artefacts

Product “About”/legal pages include dataset attribution and date-of-data statements. Endpoints expose metadata for dataset versions and licences. User-facing components avoid implying endorsement and exclude logos and trademarks consistent with open terms[^21][^4].

## Appendices

### Appendix A: API and Endpoint Quick-Reference

- OS Open Data Downloads: OS Data Hub (open data downloads)[^19].
- OS OpenNames product page and downloads[^1][^2][^3].
- Code-Point Open product page, OS Data Hub downloads, and data.gov.uk[^20][^10][^9].
- Historic England Open Data Hub and dataset downloads; NHLE API catalogue[^5][^7][^8].
- ONS GeoPortal (ONSPD, Open Geography)[^13][^21].

### Appendix B: Glossary of Terms and Codes

- GSS code: Government Statistical Service code used to uniquely identify statistical and administrative geographies in the UK.
- LSOA/MSOA: Lower Layer Super Output Areas and Middle Layer Super Output Areas, statistical geography units used for census and other data.
- BNG: British National Grid (EPSG:27700), the projected coordinate system used for analytical precision across Great Britain.
- WGS84: World Geodetic System (EPSG:4326), a global latitude/longitude coordinate system used by web mapping clients.
- OGL: Open Government Licence v3.0, a permissive licence for public sector information.
- PSGA: Public Sector Geospatial Agreement, the framework enabling public sector access to OS data.

### Appendix C: Attribution Text Templates

Table 14. Attribution templates catalogue

| Dataset | Text |
|---|---|
| OGL | “Contains public sector information licensed under the Open Government Licence v3.0.”[^21] |
| OS OpenNames | “Contains OS data © Crown copyright and database right [year].”[^18] |
| Code-Point Open | “Contains OS data © Crown copyright and database right [year]. Contains Royal Mail data © Royal Mail copyright and database right [year]. Contains National Statistics data © Crown copyright and database right [year]. Licensed under the Open Government Licence v3.0.”[^10][^12][^21] |
| Boundary-Line | “Contains public sector information licensed under the Open Government Licence v3.0.” Add OS rights where spatial data includes OS geometry[^14][^15]. |
| ONSPD | “Contains public sector information licensed under the Open Government Licence v3.0.” Add ONS/OS rights; check NI permissions[^13][^12]. |
| Historic England NHLE | “© Historic England [year]. Contains Ordnance Survey data © Crown copyright and database right [year]. Licensed under the Open Government Licence v3.0.”[^7][^4] |
| Local authority datasets | “Contains public sector information licensed under the Open Government Licence v3.0. Contains OS data © Crown copyright and database right [year].”[^25] |

## Information Gaps

- OS Data Hub download pages are dynamic; product pages and technical documentation should be consulted for definitive formats, schemas, and endpoints[^15][^3].
- British Library digitised map images are subject to item-level copyright; dataset-level bulk download licensing is not confirmed in this report[^27].
- Northern Ireland postcode and boundary licensing often requires separate permissions; verify with the appropriate NI authority before commercial use[^12].
- Exact dataset-level schema for OS OpenNames should be taken from OS technical documentation when implementing ingestion pipelines[^3].
- Local authority portals are heterogeneous; only representative examples and common practices are referenced here[^25].

---

## References

[^1]: OS Open Names | Data Products - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-open-names  
[^2]: Download OS Open Names - OS Data Hub. https://osdatahub.os.uk/downloads/open/OpenNames  
[^3]: OS Open Names technical documentation. https://docs.os.uk/os-downloads/addressing-and-location/os-open-names  
[^4]: Historic England Open Data Hub Terms and Conditions. https://historicengland.org.uk/terms/website-terms-conditions/open-data-hub/  
[^5]: Historic England Open Data Hub. https://opendata-historicengland.hub.arcgis.com/  
[^7]: National Heritage List for England (NHLE) - API Catalogue. https://www.api.gov.uk/he/national-heritage-list-for-england-nhle/  
[^8]: Download Listing Data - Historic England. https://historicengland.org.uk/listing/the-list/data-downloads/  
[^9]: Code-Point Open - Data.gov.uk. https://www.data.gov.uk/dataset/c1e0176d-59fb-4a8c-92c9-c8b376a80687/code-point-open2  
[^10]: Download Code-Point Open - OS Data Hub. https://osdatahub.os.uk/downloads/open/CodePointOpen  
[^11]: Code-Point Open technical documentation. https://docs.os.uk/os-downloads/addressing-and-location/code-point-open  
[^12]: Licences - Office for National Statistics (ONS). https://www.ons.gov.uk/methodology/geography/licences  
[^13]: ONS Postcode Directory (UK) - Geoportal. https://geoportal.statistics.gov.uk/datasets/b54177d3d7264cd6ad89e74dd9c1391d  
[^14]: Boundary-Line | Data Products - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/boundary-line  
[^15]: Boundary-Line technical documentation. https://docs.os.uk/os-downloads/addressing-and-location/boundary-line  
[^16]: Historic England listed building points dataset. https://opendata-historicengland.hub.arcgis.com/datasets/historicengland::listed-building-points/explore  
[^18]: OS Open Data Licence (summary PDF). https://www.rowmaps.com/datasets/SU/OS-opendata-licence.pdf  
[^19]: Open Data Downloads | OS Data Hub. https://osdatahub.os.uk/data/downloads/open  
[^20]: Code-Point Open product page - Ordnance Survey. https://os.uk/products/code-point-open  
[^21]: Open Government Licence v3.0 - The National Archives. https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/  
[^24]: Digital boundaries - ONS. https://www.ons.gov.uk/methodology/geography/geographicalproducts/digitalboundaries  
[^25]: Local authority transport: how to publish your data - GOV.UK. https://www.gov.uk/guidance/local-authority-transport-how-to-publish-your-data  
[^27]: British Library: Our collections. https://www.bl.uk/collection