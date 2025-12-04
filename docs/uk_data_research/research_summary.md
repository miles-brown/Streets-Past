# Official UK Government Data Sources for Postcodes, Administrative Geographies, and Street Names: Acquisition, Formats, Licensing, and Coverage

## Executive Summary

Reliable access to postcodes, administrative geographies, and street names is foundational to UK geospatial operations. This report identifies the official sources—Office for National Statistics (ONS), Ordnance Survey (OS), Royal Mail’s Postcode Address File (PAF), and GeoPlace—and explains how to acquire and use them in production. It clarifies coverage (UK vs Great Britain), update cycles, data formats, access methods, and licensing frameworks so that GIS analysts, data engineers, address and street authorities, and public sector analysts can assemble compliant, resilient data pipelines.

ONS products are the definitive bridge between postcodes and statistical/administrative geographies. The ONS Postcode Directory (ONSPD) and National Statistics Postcode Lookup (NSPL) link current and terminated postcodes to counties, local authority districts (LADs), regions, health geographies, and statistical units. ONSPD uses point-in-polygon allocation with 1-metre grid references and is released quarterly in CSV/TXT. NSPL aligns postcodes to Output Areas then applies best-fit allocation to higher geographies and is also quarterly. The Open Geography Portal is the primary distribution channel and the hub for boundaries, centroids, names and codes, and lookup tables[^1][^3][^4][^5][^6][^9][^12].

For addressing, Royal Mail’s PAF is the UK’s operational address backbone, containing tens of millions of delivery points and postcodes, continuously updated and governed by a Code of Practice. It is accessed via licensed solutions providers under commercial terms, with public sector licensing arrangements available. OS AddressBase products augment PAF by adding Unique Property Reference Numbers (UPRNs), coordinates, classification, and lifecycle attributes. AddressBase core and AddressBase Premium are updated every six weeks and distributed in CSV/GML (Premium also in GeoPackage). AddressBase Premium provides full lifecycle coverage across England, Scotland, and Wales[^7][^13][^14][^15][^16][^29].

For street names, GeoPlace’s National Street Gazetteer (NSG) for England and Wales is authoritative, assigning Unique Street Reference Numbers (USRNs) and providing official street names and maintenance responsibilities via services such as DataVia API and FindMyStreet. OS Open Names offers a free, comprehensive gazetteer of place names, road numbers, and postcodes across Great Britain with quarterly updates, available as downloads and via the OS Names API. OS Open Roads provides a mid-scale, topologically connected road network suited to routing and network analysis, updated twice a year[^24][^18][^19][^20][^22][^23].

Licensing and access vary by product. ONS boundary and names/codes datasets are generally available under the Open Government Licence (OGL v3.0). ONSPD carries a custom licence reflecting embedded third-party IP. OS open products (e.g., OS Open Names, OS Open Roads, Boundary-Line) are free under OS OpenData terms. AddressBase products are available under OS’s plans (OpenData, Public Sector, Premium), with free access for PSGA members; trials can use the Data Exploration Licence. PAF licensing is commercial through Royal Mail solutions providers, with public sector arrangements to be confirmed[^31][^2][^35][^36][^37][^30][^29].

In practice, teams should select combinations that align to their coverage (UK vs GB), their need for postal addressing vs geographic analysis, and their licensing constraints. The common stacks include an ONS-led open analytical stack, a PSGA-led public sector stack, a commercial GB stack, and a PAF-led operational addressing stack. All require careful attention to coverage boundaries (especially Northern Ireland vs Great Britain), identifier adoption (UPRN/USRN), and release cadence.

Table 1 summarises the key dataset attributes discussed in this report.

Table 1. Key dataset attributes and access summary

| Theme | Dataset | Coverage | Update cycle | Formats | Access/licensing |
|---|---|---|---|---|---|
| Postcodes and linkage | ONSPD | UK | Quarterly | CSV, TXT (in ZIP) | Open download; custom licence due to third-party IP |
| Postcodes and linkage | NSPL | UK | Quarterly | CSV, TXT | Open download |
| Boundaries and lookups | ONS boundaries (e.g., Counties & UAs; LADs) | UK | Annual/periodic | Shapefile, GeoJSON, KML, CSV + services | OGL v3.0 |
| Administrative names/codes | ONS Names & Codes (GSS) | UK | Periodic | CSV, Excel | OGL v3.0 |
| Postal addressing | PAF (Royal Mail) | UK | Continuous | Multiple via providers | Commercial licence; public sector arrangements |
| Property-level addressing | AddressBase core | GB | Every six weeks | CSV, GML | OS plans |
| Property-level addressing | AddressBase Premium | GB | Every six weeks | CSV, GML, GeoPackage | OS plans; PSGA access |
| Street gazetteer | OS Open Names | GB | Quarterly | CSV, GML, GeoPackage; API | OS OpenData; API terms |
| Road network | OS Open Roads | GB | Twice yearly | Shapefile, GeoPackage, GML, Vector Tiles | OS OpenData |
| Administrative boundaries | OS Boundary-Line | GB | Twice yearly | Shapefile, GeoPackage, GML, MapInfo TAB, Vector Tiles | OS OpenData |
| Authoritative street data | NSG via GeoPlace services | England & Wales | Periodic via services | APIs/services | USRN open/royalty-free |


## Scope and Definitions

Postcodes and post towns. UK postcodes are alphanumeric identifiers used by Royal Mail to facilitate mail delivery. In this report, “post town” refers to the postal town component commonly used in addressing (for example, “Abbey Wood” in SE2 Abbey Wood). ONS products relate postcodes to a wide range of geographies for statistical production, and the distinction between ONSPD and NSPL matters when assigning postcodes to areas for analysis[^1][^6][^7].

Administrative geographies. The UK statistical geography hierarchy includes countries, regions, combined authorities, counties, local authority districts (LADs), unitary authorities (UAs), wards, and statistical units such as Output Areas (OAs), Lower-layer Super Output Areas (LSOAs), and Middle-layer Super Output Areas (MSOAs). ONS maintains names, codes, and boundaries for these geographies and distributes them openly via the Open Geography Portal[^3][^10][^12].

Street names and identifiers. In England and Wales, the National Street Gazetteer (NSG) is the authoritative register of streets, maintained by local authorities and coordinated by GeoPlace. It assigns a Unique Street Reference Number (USRN) to each street element and records responsibilities. OS Open Names provides a comprehensive gazetteer for Great Britain of named and numbered roads, settlements, and postcodes for discovery and labelling; OS Open Roads provides a connected road network suitable for routing and analysis[^24][^18][^22].


## Methodology and Source Vetting

This report relies exclusively on official and authoritative sources: ONS (including the Open Geography Portal), Ordnance Survey, GeoPlace, Royal Mail (PAF), and central government portals (e.g., planning.data.gov.uk). For each dataset, coverage, update frequency, formats, access methods, licensing, and identifiers were validated using product pages, technical documentation, and licences. The Open Geography Portal and OS Data Hub serve as the definitive entry points for ONS and OS products, respectively[^3][^35].


## UK Postcodes and Post Town Mappings

ONS Postcode Directory (ONSPD). ONSPD is the canonical product linking current and terminated UK postcodes to administrative, electoral, health, and statistical geographies. It uses point-in-polygon assignment to the area containing the mean grid reference of all addresses in the postcode and includes 1-metre resolution grid references. ONSPD is produced quarterly and distributed as ZIP files containing multi-CSVs and ASCII TXT, accompanied by a user guide. The product is free to download but uses a custom licence reflecting embedded IP from Royal Mail and other partners[^1][^4][^5].

National Statistics Postcode Lookup (NSPL). NSPL allocates postcodes to 2021 Census Output Areas and then applies best-fit allocation to higher geographies, making it particularly suitable for producing area-based statistics from postcode-level inputs. It is UK-wide, updated quarterly, and available in CSV and TXT. It is published on government data portals alongside the Open Geography Portal[^1][^6][^9].

ONS Online Postcode Directory (Live). The online, live version provides digital vector centroids for current postcodes and is suitable for mapping and quick lookup applications that do not require the full geographic linkage set in ONSPD/NSPL[^8].

PAF (Postcode Address File). PAF is Royal Mail’s operational address database, covering over 32 million delivery points and more than 1.8 million postcodes. It is updated continuously—thousands of changes each week—and is distributed via licensed solutions providers under a Code of Practice. PAF is the authoritative source for postal addressing and includes specialized datasets such as Multiple Residence, Not Yet Built, BFPO, and Alias. Public sector licensing routes exist and should be confirmed directly[^7][^29].

To illustrate the different strengths and characteristics, Table 2 compares ONSPD, NSPL, and PAF.

Table 2. ONSPD vs NSPL vs PAF

| Attribute | ONSPD | NSPL | PAF |
|---|---|---|---|
| Primary use | Link postcodes to statistical/administrative geographies for analysis | Best-fit allocation from Output Areas to higher geographies for statistics | Operational postal addressing for delivery |
| Methodology | Point-in-polygon (mean grid reference) | Best-fit from 2021 Output Areas | Postal address management by Royal Mail |
| Coverage | UK | UK | UK |
| Update cadence | Quarterly | Quarterly | Continuous |
| Formats | ZIP with multi-CSVs and ASCII TXT | CSV and TXT | Multiple via licensed providers |
| Licensing | Custom (third-party IP) | Open (per dataset) | Commercial; public sector arrangements |
| Access | Open Geography Portal | data.gov.uk/Open Geography Portal | Solutions providers |

When you need to relate “SE2 Abbey Wood” style entries to post towns and to administrative geographies for analysis, ONSPD/NSPL provide the geography linkage and PAF provides the operational addressing. The OGL applies to most ONS boundary and names/codes products, whereas ONSPD’s custom licence and PAF’s commercial terms require specific attention[^1][^5][^6][^7][^31].


## Administrative Geography: Counties and Local Authorities

ONS Names and Codes. ONS maintains authoritative names and GSS nine-character codes for administrative geographies across the UK, including counties, regions, LADs/UAs, and wards. These are published in CSV and Excel and are essential for consistent joins across ONS products and other government datasets[^12].

ONS Boundaries. ONS publishes digital boundary datasets across a range of resolutions, from full extent to generalised and clipped variants. These are available via the Open Geography Portal, typically in Shapefile, GeoJSON, KML, and CSV formats, and are covered by the Open Government Licence v3.0. Datasets such as Counties and Unitary Authorities (December 2024, BGC) and Local Authority Districts (May 2024, BFE) are provided with accompanying services and metadata[^10][^11][^3][^31].

OS Boundary-Line. OS Boundary-Line is a free, open dataset mapping every administrative boundary in Great Britain—counties, LADs/UAs, wards, parliamentary constituencies—and is updated twice a year (May and October). It supports analysis and visualization and is available in ESRI Shapefile, GeoPackage, GML, MapInfo TAB, and Vector Tiles[^25][^26][^27].

Table 3 consolidates administrative geography resources.

Table 3. Administrative geography datasets: coverage and formats

| Dataset | Coverage | Formats | Update frequency | Access | Licence |
|---|---|---|---|---|---|
| ONS Names & Codes (Administrative Geographies) | UK | CSV, Excel | Periodic | Open Geography Portal | OGL v3.0 |
| Counties & Unitary Authorities Boundaries (Dec 2024, BGC) | UK | Multiple + services | Annual | Open Geography Portal | OGL (with attribution) |
| LAD Boundaries (May 2024, BFE) | UK | Multiple + services | Annual | Open Geography Portal | OGL (with attribution) |
| LAD to County/UA Lookup (Apr 2025, EW) | England & Wales | CSV, KML, GeoJSON, Shapefile | Annual | Open Geography Portal | OGL (with attribution) |
| OS Boundary-Line | Great Britain | Shapefile, GeoPackage, GML, MapInfo TAB, Vector Tiles | Twice yearly | OS Data Hub | OS OpenData (free) |


## Official UK Street Names and Network Datasets

National Street Gazetteer (NSG) and GeoPlace services. The NSG is the authoritative register of streets in England and Wales. It assigns USRNs and records official names, responsibilities, and street features. GeoPlace provides APIs and services—including FindMyStreet and DataVia—that expose this information for public use. USRNs are open and royalty-free, aligning with government policy to standardize property and street identifiers across the public sector[^24][^17].

OS Open Names. OS Open Names is a comprehensive, open gazetteer of place names, road numbers, and postcodes across Great Britain, with National Grid coordinates. It contains over 870,000 named and numbered roads, nearly 44,000 settlements, and more than 1.6 million postcodes, and is updated quarterly. It is available for download in CSV, GML, and GeoPackage, and as a RESTful API via the OS Names API[^18][^19][^20][^21].

OS Open Roads. OS Open Roads offers a mid-scale, topologically connected road network for Great Britain from motorways to country lanes, representing an approximate central alignment of the carriageway. It is updated twice a year (April and November) and is suited to routing, proximity analysis, and network-level statistics. It is available in Shapefile, GeoPackage, GML, and Vector Tiles[^22][^23].

Table 4 summarizes the principal street and network datasets.

Table 4. Street and network datasets

| Dataset | Coverage | Content | Update cadence | Formats | Access/licensing |
|---|---|---|---|---|---|
| NSG via GeoPlace services | England & Wales | Official street names, USRN, responsibilities | Periodic via services | APIs/services | USRN open/royalty-free |
| OS Open Names | Great Britain | Gazetteer of roads, settlements, postcodes | Quarterly | CSV, GML, GeoPackage; API | OS OpenData; API terms |
| OS Open Roads | Great Britain | Connected road network | Twice yearly | Shapefile, GeoPackage, GML, Vector Tiles | OS OpenData |


## Licensing and Access Frameworks

Open Government Licence (OGL v3.0). OGL is the standard licence for most ONS boundary and names/codes data. It requires attribution and allows free use, including commercial, subject to the licence terms. The OGL user guidance provides recommended attribution statements and clarifies conditions for re-use[^31].

ONS licences. ONS geography products are provided under OGL unless otherwise stated. ONSPD is subject to a custom licence due to third-party IP embedded in the product. Teams should consult ONS licensing pages when planning redistribution or commercial use of ONSPD-derived outputs[^2][^5].

Ordnance Survey plans and PSGA. OS distributes data through the OS Data Hub under three plans: OpenData (free), Public Sector (for eligible bodies under the Public Sector Geospatial Agreement), and Premium (commercial). AddressBase products are available via these plans; public sector access is free at point of use under PSGA. A Data Exploration Licence is available for trials. API usage is governed by OS Data Hub API terms[^35][^36][^13][^15][^21][^30][^37].

PAF licensing. PAF is a Royal Mail commercial product accessed via licensed solutions providers and governed by a Code of Practice. Public sector licensing arrangements exist. Pricing is outside the scope of this guide and must be confirmed directly[^7][^29].

Table 5 consolidates licensing and access.

Table 5. Licensing and access by dataset

| Dataset | Licence | Access model | Notes |
|---|---|---|---|
| ONS boundaries and names/codes | OGL v3.0 | Open download | Attribution required |
| ONSPD | Custom | Open download | Third-party IP embedded |
| NSPL | Open (per dataset) | Open download | Best-fit methodology |
| OS Open Names | OS OpenData | Open download + API | Quarterly updates |
| OS Open Roads | OS OpenData | Open download | Twice-yearly updates |
| AddressBase core | OS plans | OS Data Hub | Six-week cadence |
| AddressBase Premium | OS plans (PSGA/Premium) | OS Data Hub | PSGA access free at point of use |
| OS Names API | OS OpenData/API terms | OS Data Hub API | API-specific terms |
| Boundary-Line | OS OpenData | OS Data Hub | Twice-yearly updates |
| PAF | Royal Mail commercial | Solutions providers | Code of Practice; public sector arrangements |


## Integration and Identifier Strategy

UPRN and USRN. The Unique Property Reference Number (UPRN) and the Unique Street Reference Number (USRN) are the backbone identifiers for addresses and streets across the public sector. Adoption of UPRN/USRN standardizes joins across datasets, enables lifecycle tracking, and reduces ambiguity in address/street resolution. GOV.UK guidance promotes their use for identifying property and street information[^17].

Coordinate systems and names. OS Open Names provides British National Grid coordinates and multi-lingual naming for settlements, enabling consistent geocoding and labelling across Great Britain. When integrating with ONSPD/NSPL or ONS boundaries, plan for coordinate transformations if you adopt WGS84 for web mapping, and use GSS codes for administrative geographies. The OS Names API offers find and nearest functions to support geocoding and proximity searches[^18][^19][^20].

Lookups and codes. The LAD to County/UA lookup and ONS Names & Codes tables enable many-to-one joins from districts to counties/UAs and provide consistent code sets for cross-dataset linkage. These are essential for analytical rollups and time-series comparability[^11][^12].


## Implementation Scenarios and Recommendations

Public Sector Geospatial Agreement (PSGA) pipeline (recommended for eligible bodies). Use ONSPD and NSPL for postcode-to-geography linkage and ONS boundary/name/code datasets under OGL. For full addressing in GB, include AddressBase Premium via PSGA. For network context, add OS Open Roads; for discovery and labelling, use OS Open Names; for authoritative street names and responsibilities in England and Wales, use GeoPlace services. This stack provides comprehensive coverage with minimal licensing friction for public sector members[^3][^10][^24][^30][^37].

Commercial GB addressing stack. Combine ONSPD/NSPL for UK-wide analysis with OS Open Names for GB-wide naming and OS Open Roads for routing. Add AddressBase Premium (commercial) for property-level addressing and lifecycle. Confirm licensing and costs with OS partners[^3][^18][^22][^15].

Cost-conscious open analytical stack. For UK-wide analysis without property-level addressing, use ONSPD/NSPL and ONS boundaries/names/codes (OGL), plus OS Open Roads and OS Open Names for GB network context and labelling. Where you need authoritative street names/responsibilities (England and Wales), consider GeoPlace services for targeted queries[^10][^24].

PAF-led operational addressing stack. If your core need is operational postal addressing, PAF (via licensed providers) can serve as the backbone, joined to ONSPD/NSPL for geography linkage and to AddressBase where UDPRN/UPRN mapping is available. Validate public sector licensing and redistribution constraints before deployment[^7][^13].

Table 6 compares the scenarios.

Table 6. Scenario comparison

| Scenario | Coverage | Cost | Update cadence | Strengths | Considerations |
|---|---|---|---|---|---|
| PSGA-led | UK (boundaries/postcodes), GB (AddressBase, OS Open) | Low direct cost (membership) | Quarterly (ONSPD/NSPL), six-weekly (AddressBase), biannual (Open Roads) | Full property-level via PSGA; open boundaries | PSGA eligibility; licence compliance |
| Commercial GB stack | UK (ONSPD/NSPL), GB (OS Open, AddressBase Premium) | Commercial | As above | Full addressing/lifecycle | Commercial licensing and budgeting |
| Open analytical stack | UK | Free | Quarterly/biannual | Broad analytical capability | No property-level addressing; limited street responsibilities |
| PAF-led | UK | Commercial | Continuous updates | Operational addressing | No built-in geography linkage; manage licensing |


## Data Formats and Download Access Matrix

ONS products. ONSPD is distributed as a ZIP file containing multi-CSVs and ASCII TXT files with a user guide. NSPL is available in CSV and TXT via data portals. ONS boundary datasets are provided in multiple formats (Shapefile, GeoJSON, KML, CSV) and exposed via OGC services. Names & Codes are provided in CSV and Excel[^4][^6][^3][^12].

Ordnance Survey products. AddressBase core and Premium are available in CSV and GML (Premium also in GeoPackage). OS Open Names is available in CSV, GML, and GeoPackage and is accessible via the OS Names API. OS Open Roads is provided in Shapefile, GeoPackage, GML, and Vector Tiles. Boundary-Line is available in Shapefile, GeoPackage, GML, MapInfo TAB, and Vector Tiles[^13][^15][^18][^22][^25][^26][^27].

PAF. PAF is delivered via licensed solutions providers in multiple formats; specific schemas and costs should be confirmed directly with providers[^7][^29].

Table 7 summarises formats and access.

Table 7. Formats and access matrix

| Dataset | Formats | Access | Update frequency |
|---|---|---|---|
| ONSPD | ZIP (multi-CSV, TXT) | Open Geography Portal | Quarterly |
| NSPL | CSV, TXT | data.gov.uk/Open Geography Portal | Quarterly |
| ONS Names & Codes | CSV, Excel | Open Geography Portal | Periodic |
| ONS boundaries (e.g., Counties & UAs; LADs) | Shapefile, GeoJSON, KML, CSV + services | Open Geography Portal | Annual/periodic |
| AddressBase core | CSV, GML | OS Data Hub | Every six weeks |
| AddressBase Premium | CSV, GML, GeoPackage | OS Data Hub | Every six weeks |
| OS Open Names | CSV, GML, GeoPackage; API | OS Data Hub + OS Names API | Quarterly |
| OS Open Roads | Shapefile, GeoPackage, GML, Vector Tiles | OS Data Hub | Twice yearly |
| Boundary-Line | Shapefile, GeoPackage, GML, MapInfo TAB, Vector Tiles | OS Data Hub | Twice yearly |
| PAF | Multiple via providers | Solutions providers | Continuous |


## Known Gaps and Next Steps

- PAF schema and pricing. PAF is distributed via licensed solutions providers, and schema details, pricing tiers, and redistribution terms vary. Confirm with Royal Mail or your chosen provider and ensure alignment with the Code of Practice[^7][^29].

- NSG full dataset access and licensing. GeoPlace exposes NSG via services; direct bulk download availability and licensing terms should be clarified for your use case[^24].

- Northern Ireland street data. Confirm authoritative sources for street naming and USRN coverage in Northern Ireland (e.g., OSNI/NI local authorities) to complement GB coverage.

- AddressBase linkage specifics. Cross-references between UDPRN, UPRN, and USRN can vary by edition. Consult the AddressBase technical specification and release notes to confirm linkage fields and lifecycle attributes for your target edition[^14][^16][^17].

- ONSPD custom licence edge-cases. Review ONS licensing pages for constraints on redistribution and commercial use when combining ONSPD with third-party IP or using it in derivative works[^2][^5].

- Post town presence in ONSPD/NSPL. While post towns are intrinsic to postal addressing, explicit availability of “post town” fields in ONSPD/NSPL should be verified against the product documentation before building dependencies[^1][^4].


## Appendix: Reference Index and Field Spec Snippets

Reference index. The following datasets and services are cited in this report. See the numbered References section for the authoritative URLs and more details.

- Postcode products (ONSPD, NSPL) and methodology.
- ONSPD release and data access.
- NSPL dataset entry and formats.
- Open Geography Portal and boundary datasets.
- Names & Codes (GSS codes).
- AddressBase core and Premium.
- OS Open Names and OS Names API.
- OS Open Roads and Boundary-Line.
- GeoPlace street data services (NSG, DataVia API, FindMyStreet).
- PAF overview, Code of Practice, and public sector licensing.
- OGL and OS/PSGA licensing frameworks.

ONS boundary dataset field examples ( Counties & UAs, Dec 2024 BGC). Typical fields include CTYUA24CD (code), CTYUA24NM (name), BNG_E/BNG_N (British National Grid coordinates), LONG/LAT, and geometry area/length metadata. Use these to join to Names & Codes and to aggregate analyses by county/UA[^10][^12].

LAD to County/UA lookup fields. Typical fields include LAD25CD/LAD25NM and CTYUA25CD/CTYUA25NM (with Welsh variants), enabling many-to-one joins for rollups from districts to counties/UAs[^11].


## References

[^1]: Postcode products — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/postcodeproducts  
[^2]: Licences — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/licences  
[^3]: Open Geography Portal. https://geoportal.statistics.gov.uk/  
[^4]: ONS Postcode Directory (February 2024) for the UK — ArcGIS Hub. https://geoportal.statistics.gov.uk/datasets/e14b1475ecf74b58804cf667b6740706  
[^5]: ONS Postcode Directory (February 2024) — Data download. https://www.arcgis.com/sharing/rest/content/items/e14b1475ecf74b58804cf667b6740706/data  
[^6]: National Statistics Postcode Lookup (NSPL) — data.gov.uk. https://www.data.gov.uk/dataset/7ec10db7-c8f4-4a40-8d82-8921935b4865/national-statistics-postcode-lookup-uk  
[^7]: Powered by PAF. https://www.poweredbypaf.com/  
[^8]: Online ONS Postcode Directory (Live) — ArcGIS Hub. https://hub.arcgis.com/datasets/3be72478d8454b59bb86ba97b4ee325b  
[^9]: National Statistics Postcode Lookup (May 2025) — ArcGIS Hub. https://hub.arcgis.com/datasets/077631e063eb4e1ab43575d01381ec33  
[^10]: Counties and Unitary Authorities (December 2024) Boundaries UK BGC — Open Geography Portal. https://geoportal.statistics.gov.uk/datasets/ons::counties-and-unitary-authorities-december-2024-boundaries-uk-bgc-1/about  
[^11]: Local Authority District to County and Unitary Authority (April 2025) Lookup in EW (V2) — data.gov.uk. https://www.data.gov.uk/dataset/a76a9de2-d0f4-4fd7-bcc9-e63bbf28bbb5/local-authority-district-to-county-and-unitary-authority-april-2025-lookup-in-ew-v21  
[^12]: Names and codes listings — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/namescodesandlookups/namesandcodeslistings  
[^13]: AddressBase — Ordnance Survey. https://www.ordnancesurvey.co.uk/products/addressbase  
[^14]: AddressBase — OS Downloads Documentation. https://docs.os.uk/os-downloads/addressing-and-location/addressbase  
[^15]: AddressBase Premium — Ordnance Survey. https://www.ordnancesurvey.co.uk/products/addressbase-premium  
[^16]: AddressBase Premium — OS Downloads Documentation. https://docs.os.uk/os-downloads/addressing-and-location/addressbase-premium  
[^17]: Access free address data using AddressBase — GOV.UK. https://www.gov.uk/guidance/access-free-address-data-using-addressbase  
[^18]: OS Open Names — Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-open-names  
[^19]: OS Open Names — OS Downloads Documentation. https://docs.os.uk/os-downloads/addressing-and-location/os-open-names  
[^20]: OS Names API — Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-names-api  
[^21]: OS Names API — API Catalogue. https://www.api.gov.uk/os/os-names-api/  
[^22]: OS Open Roads — Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-open-roads  
[^23]: OS Open Roads — OS Downloads Documentation. https://docs.os.uk/os-downloads/networks/os-open-roads  
[^24]: Access street data and services — GeoPlace LLP. https://www.geoplace.co.uk/addresses-streets/street-data-and-services  
[^25]: Boundary-Line — Ordnance Survey. https://www.ordnancesurvey.co.uk/products/boundary-line  
[^26]: Boundary-Line — OS Downloads Documentation. https://docs.os.uk/os-downloads/addressing-and-location/boundary-line  
[^27]: Boundary-Line Open Data Downloads — OS Data Hub. https://osdatahub.os.uk/downloads/open/BoundaryLine  
[^29]: PAF Public Sector Licence — OS Licensing. https://www.ordnancesurvey.co.uk/licensing/paf-licence  
[^30]: The PSGA — Ordnance Survey. https://www.ordnancesurvey.co.uk/customers/public-sector/public-sector-geospatial-agreement  
[^31]: Open Government Licence v3.0 — The National Archives. https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/  
[^35]: Plans — OS Data Hub. https://osdatahub.os.uk/plans  
[^36]: Helpful licensing terms — Public Sector licensing guide — OS. https://www.ordnancesurvey.co.uk/customers/public-sector/public-sector-licensing/licensing-terms  
[^37]: PSGA questions and answers — Ordnance Survey. https://www.ordnancesurvey.co.uk/customers/public-sector/public-sector-geospatial-agreement/psga-questions-answers