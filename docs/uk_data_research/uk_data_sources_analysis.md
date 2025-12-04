# UK Official Data Sources for Postcodes, Administrative Geographies, and Street Names: A Definitive Acquisition and Licensing Guide

## Executive Summary

This guide identifies and explains how to acquire the official United Kingdom (UK) datasets needed to underpin robust address, postcode, street, and administrative geography capabilities. It brings together the core products from the Office for National Statistics (ONS), Ordnance Survey (OS), Royal Mail’s Postcode Address File (PAF), and related authoritative sources, and sets out formats, access methods, licensing models, and coverage differences that matter to technical and programme leads. The emphasis is on building production-grade pipelines that remain compliant and sustainable.

For postcodes and their linkages to administrative geographies, the ONS Postcode Directory (ONSPD) and the National Statistics Postcode Lookup (NSPL) remain the definitive public products. Both are updated quarterly, provide UK-wide coverage, and are provided in CSV and ASCII TXT formats. ONSPD uses point-in-polygon allocation to assign postcodes to the geographies where the mean grid reference of all addresses falls; NSPL uses a best-fit methodology from Output Areas, a distinction that matters when interpreting assignations and performing analysis. ONS publishes these via its Open Geography Portal under OGL for boundary data, with ONSPD itself subject to a custom licence due to embedded third-party IP. Together with NSPL, they answer “SE2 Abbey Wood” style queries by linking the postcode to its post town and a wide array of statistical and administrative geographies for analysis and reporting[^1][^3][^4][^6].

For the most complete address backbone, AddressBase products from Ordnance Survey match Royal Mail postal addresses to Unique Property Reference Numbers (UPRNs) and provide property-level coordinates and lifecycle attributes. AddressBase (core) covers Great Britain (GB), includes UDPRN, and is released every six weeks in CSV and GML. AddressBase Premium extends coverage and depth, with over 40 million addresses, 100 million cross-references, and richer lifecycle information; Premium is also updated every six weeks and is available in CSV, GML, and GeoPackage[^13][^14][^15][^16][^17].

For authoritative street naming and network context, GeoPlace’s National Street Gazetteer (NSG) for England and Wales is the authoritative source of official street names and responsibilities, exposed via services such as FindMyStreet and the DataVia API. OS Open Names provides a comprehensive open gazetteer of place names, road numbers, and postcodes across GB, updated quarterly and exposed both as download and via the OS Names API; it is ideal for discovery, labelling, and light-weight name/road matching. OS Open Roads offers a mid-scale, topologically connected road network for GB and is published twice a year; it is suited to routing, proximity, and network-level analysis rather than official street naming[^24][^18][^19][^20][^22][^23].

Licensing and access vary by product and plan. ONS boundary datasets are generally under the Open Government Licence (OGL v3.0). ONSPD is under a custom licence. AddressBase is available under OS plans (OpenData, Public Sector, Premium) and is free at point of use to Public Sector Geospatial Agreement (PSGA) members; trial options include a Data Exploration Licence. PAF is a Royal Mail commercial product accessed via licensed solutions providers and subject to a Code of Practice; public sector arrangements exist and should be confirmed directly[^2][^31][^35][^36][^37][^30].

The right combination depends on coverage, compliance, and budget. For a UK-wide open solution, ONSPD + NSPL for postcode linkage, OS Open Names for names and labelling, and ONS boundaries under OGL provide a robust baseline with GB network context from OS Open Roads. For full property-level addressing and lifecycle in GB, add AddressBase Premium (PSGA members can access at no direct cost; commercial otherwise). PAF is essential when you need the operational postal address backbone used by Royal Mail and prefer to source directly from its ecosystem; Public sector licensing routes exist and should be validated[^10][^24][^30][^37].


## Scope and Definitions

This guide covers three data domains:

- Postcodes and post towns: structured identifiers used by Royal Mail for mail delivery. In the ONS postcode products, postcodes are linked to administrative and statistical geographies, enabling analyses that need to aggregate or attribute postcode-level events to areas such as local authority districts, wards, and regions[^1][^6][^7].

- Administrative geographies: UK countries and sub-national divisions including counties, local authority districts (LADs), unitary authorities (UAs), and electoral or health boundaries. ONS publishes digital boundaries, names and codes, and lookups that allow consistent joins and time-series analysis[^3][^5][^10][^11][^12].

- Street names and networks: official street naming and identification (USRN) from the National Street Gazetteer for England and Wales; open gazetteer naming from OS Open Names and network geometry from OS Open Roads for GB[^24][^18][^22].

The geographic scope typically splits between Great Britain (England, Wales, Scotland) and the full UK (which includes Northern Ireland). ONS products usually cover the UK; OS open products commonly cover GB only. PAF covers the UK. These differences drive how you scope coverage, choose identifiers (UPRN/USRN), and architect integrations[^1][^3][^7][^24].


## Methodology and Source Vetting

Only official and authoritative sources have been used: ONS (including the Open Geography Portal), Ordnance Survey, GeoPlace, Royal Mail (PAF), and central government portals such as data.gov.uk and planning.data.gov.uk. For each dataset, the guide checks coverage (UK vs GB vs England), update frequency, file formats, access methods, licensing, and identifiers. Where appropriate, ONS licences and the Open Government Licence v3.0 are taken as the baseline for open boundary and code sets; OS plans and PSGA terms define access to OS address and street products[^2][^3][^31].


## UK Postcodes and Post Town Mappings

ONS provides two principal postcode products that answer different analytical needs and are widely used across government and industry.

- ONS Postcode Directory (ONSPD). ONSPD links all current and terminated UK postcodes to a wide range of administrative, electoral, health, and other geographic areas. It uses 1-metre resolution grid references and assigns postcodes to the area where the mean grid reference of all addresses falls. It draws on inputs from Royal Mail, OS, National Records of Scotland, Land & Property Services (Northern Ireland), and ONS. Files are released quarterly and are provided in ZIP bundles containing multi-CSVs and ASCII TXT, with a comprehensive user guide. ONSPD is free to download, but licensing reflects third-party IP embedded in the product[^1][^4][^5].

- National Statistics Postcode Lookup (NSPL). NSPL allocates postcodes to 2021 Census Output Areas using the same methodology as ONSPD and then references these to higher geographies using a best-fit approach based on census population weights. It is designed to support the production of area-based statistics from postcode-level data. NSPL is UK-wide, released quarterly, and available as CSV and TXT[^1][^6][^9].

ONS also publishes an “Online ONS Postcode Directory (Live)” as centroid lookups for current postcodes. This is useful for fast lookup and mapping use-cases where full linkage to all geographies is not required[^8].

Royal Mail’s Postcode Address File (PAF) is the UK’s operational address backbone, covering more than 32 million postal delivery points and 1.8 million postcodes, with thousands of changes each week. It is a commercial dataset licensed through Royal Mail’s solutions provider ecosystem and governed by a Code of Practice. PAF is the source of record for postal addressing and includes sub-datasets such as Multiple Residence, Not Yet Built, BFPO, and Alias. While ONS products link postcodes to geographies, PAF provides the authoritative postal address components used in real-world addressing and logistics[^7][^29].

To illustrate the differences between the ONS products and PAF, Table 1 compares coverage, purpose, methodology, formats, and licensing.

Table 1. ONS postcode products and PAF: key differences

| Dataset | Coverage | Purpose | Update frequency | Formats | Access | Licence |
|---|---|---|---|---|---|---|
| ONSPD (ONS Postcode Directory) | UK | Link current and terminated postcodes to administrative, electoral, health, and statistical geographies using point-in-polygon (mean grid reference) | Quarterly (Feb, May, Aug, Nov) | ZIP containing multi-CSV and ASCII TXT + user guide | Open Geography Portal | Custom licence due to third-party IP |
| NSPL (National Statistics Postcode Lookup) | UK | Allocate postcodes to 2021 Output Areas and best-fit to higher geographies for statistics | Quarterly | CSV and TXT | data.gov.uk and Open Geography Portal | Open (see dataset entry; OGL applies to related ONS materials) |
| Online ONSPD (Live) | UK (live postcodes) | Digital vector centroids for live postcodes for mapping/lookup | As per release schedule | Downloadable data (see dataset) | ArcGIS Hub | As per ONS dataset entry |
| PAF (Postcode Address File) | UK | Authoritative Royal Mail postal address backbone for delivery, includes business names, MR, NYB, BFPO, Alias | Continuous (weekly stats published) | Multiple formats via licensed providers | Solutions providers; public sector licence routes exist | Royal Mail commercial; Code of Practice; public sector arrangements |

ONS methodology matters for analytics. The distinction between point-in-polygon assignment to the mean address location (ONSPD) and best-fit allocation from Output Areas (NSPL) influences how postcodes are associated with administrative areas, especially near boundaries. Analysts should choose ONSPD when they need the canonical linkage used across official statistics and NSPL when constructing area-based estimates that explicitly rely on census best-fit weights[^1][^6].

Access and integration are straightforward. Both ONSPD and NSPL are provided in CSV/TXT, often within a single ZIP per release, with a user guide detailing field definitions and code sets. When you need to link post towns to postcodes, PAF’s address lines and post town fields are the authoritative source, while ONSPD/NSPL support the administrative geography linkages needed for analysis and aggregation[^1][^4][^6][^7].


## Administrative Geography: Counties and Local Authorities

The definitive lists of counties and local authority areas (including LADs and UAs) come from ONS names and codes and the Open Geography Portal. ONS maintains current names and Government Statistical Service (GSS) nine-character codes for administrative geographies across the UK, published as CSV and Excel. The Register of Geographic Codes and Code History Database support time-series and reclassification tracking as boundaries and codes evolve[^12][^3].

For boundaries, ONS publishes full-resolution and generalised vector boundary datasets for counties and unitary authorities and for local authority districts, along with several resolutions and coastal clipping options. The open naming and boundary data are generally available under OGL v3.0, with standard attribution statements required. ONS provides guidance on selecting the appropriate boundary resolution (BFE, BFC, BGC, BUC) for different analytical tasks[^3][^10][^11][^31].

OS Boundary-Line is an open dataset covering every administrative boundary in Great Britain—parliamentary constituencies, council wards, counties, and more. It is published twice a year (May and October) and is available in ESRI Shapefile, GeoPackage, GML, MapInfo TAB, and Vector Tiles. Boundary-Line is free to use under the OS Open Data terms, making it useful for map display and analysis alongside ONS boundaries[^25][^26][^27].

A central task for many analysts is connecting LADs to counties/UAs. ONS publishes a canonical lookup for this relationship (e.g., LAD to County and Unitary Authority, April 2025, England and Wales). This dataset provides fields such as LAD25CD/LAD25NM and CTYUA25CD/CTYUA25NM and is available via the Open Geography Portal in multiple formats including CSV, KML, GeoJSON, and Shapefile, as well as REST services for programmatic access[^11].

To orient implementers quickly, Table 2 lists the core administrative geography resources and their characteristics.

Table 2. Administrative geography datasets overview

| Dataset | Coverage | Formats | Update frequency | Access | Licence |
|---|---|---|---|---|---|
| ONS Names and Codes for Administrative Geographies (including Counties) | UK | CSV, Excel | As updated | Open Geography Portal | OGL v3.0 (with attribution to ONS/OS) |
| Counties and Unitary Authorities Boundaries (Dec 2024, BGC) | UK | Multiple (Shapefile/GeoJSON/KML/CSV) + services | Annual release | Open Geography Portal | Custom licence details on page; attribution required |
| Local Authority Districts Boundaries (May 2024, BFE) | UK | Multiple + services | Annual release | Open Geography Portal | As above |
| LAD to County/UA Lookup (Apr 2025, EW) | England and Wales | CSV, KML, GeoJSON, Shapefile + REST | Annual | Open Geography Portal | As above |
| OS Boundary-Line | Great Britain | Shapefile, GeoPackage, GML, MapInfo TAB, Vector Tiles | Twice yearly (May, Oct) | OS Data Hub | OS OpenData (free) |

Choice of boundary resolution should reflect intended use. Table 3 summarises the ONS boundary resolution codes and their typical applications.

Table 3. ONS boundary resolution codes and typical uses

| Code | Description | Typical use |
|---|---|---|
| BFE | Full resolution; extent of the realm | Detailed analysis, cartography at large scales; preserves full detail including offshore islands |
| BFC | Full resolution; clipped to coastline | Analytic work where coastline clipping (Mean High Water) is appropriate |
| BGC | Generalised (20m); clipped to coastline | Balanced performance and cartography for web maps and regional analysis |
| BUC | Ultra-generalised (500m); clipped to coastline | Small-scale national maps, rapid rendering, rough spatial overlay |


## Official UK Street Names and Network Datasets

England and Wales have an authoritative street register—the National Street Gazetteer (NSG)—maintained by local authorities and coordinated by GeoPlace. The NSG provides official street names and the Unique Street Reference Number (USRN), and it records responsibilities and lifecycle details. GeoPlace exposes this information through services such as FindMyStreet (for discovery and responsibility lookup) and the DataVia API (for programmatic access). The USRN is the standard identifier for streets, complementing the UPRN for properties; both are now open and royalty-free, enabling consistent cross-referencing across datasets[^24].

For Great Britain-wide naming and labelling, OS Open Names is the definitive open gazetteer for settlements, road numbers, and postcodes. It contains over 870,000 named/numbered roads, nearly 44,000 settlements, and over 1.6 million postcodes. OS Open Names is updated quarterly and is available for download as CSV, GML, and GeoPackage. For lightweight integration and search, the OS Names API provides a REST interface, supporting both string-based lookup and “nearest” queries in British National Grid. Note that the OS Names API does not return detailed addresses and is not intended for bulk address matching; use AddressBase or OS Places for those tasks[^18][^19][^20][^21].

For network geometry and connectivity, OS Open Roads provides a mid-scale, topologically connected road network for GB, including motorways to country lanes. It is updated twice a year (April and November) and is suitable for proximity analyses, drive-time estimation, and high-level routing. It does not substitute for the NSG where official street names and responsibilities are needed[^22][^23].

Table 4 compares the principal street-focused datasets and services.

Table 4. Street and network datasets: scope, access, and use

| Dataset/Service | Coverage | Purpose and content | Update frequency | Access | Licence/Notes |
|---|---|---|---|---|---|
| National Street Gazetteer (NSG) via GeoPlace services (DataVia API, FindMyStreet) | England and Wales (streets) | Official street names, USRN, responsibilities, lifecycle | As maintained by authorities and published by GeoPlace | APIs and web services | Authoritative street data; USRN open/royalty-free |
| OS Open Names (download) | Great Britain | Gazetteer of settlements, road numbers, postcodes (with National Grid coordinates) | Quarterly | OS Data Hub (CSV/GML/GeoPackage) | OS OpenData (free) |
| OS Names API | Great Britain | REST API for find/nearest lookups of places, roads, postcodes | Quarterly | OS Data Hub API | Free under OS OpenData; not for bulk address matching |
| OS Open Roads | Great Britain | Mid-scale, connected road network; centrline geometry | Twice yearly (Apr, Nov) | OS Data Hub (Shapefile/GeoPackage/GML/Vector Tiles) | OS OpenData (free) |


## Licensing and Access Frameworks

Licensing shapes what you can do with each dataset and how you may redistribute derivatives. The Open Government Licence v3.0 (OGL) is the default for most ONS boundary, names, and codes data, requiring attribution and, where applicable, inclusion of OS crown copyright. ONSPD has custom licensing due to embedded IP, and redistributions should follow the specific terms published by ONS[^31][^2][^5].

Ordnance Survey offers several plans through the OS Data Hub: OpenData (free), Public Sector (for eligible public bodies under PSGA), and Premium (commercial). AddressBase products are available via these plans; public sector access is free at point of use under the PSGA. OS also offers a Data Exploration Licence for trials. API usage terms apply when consuming OS APIs (e.g., OS Names API), including conditions on caching, throughput, and display. PSGA membership is free at point of use to eligible public sector bodies and unlocks access to OS premium datasets[^35][^36][^13][^30][^21][^37].

PAF is a Royal Mail commercial product distributed via licensed solutions providers. A Code of Practice governs usage, and public sector licensing routes exist. Pricing is outside the scope of this guide and should be obtained directly from Royal Mail or its authorized partners[^7][^29].

Table 5 summarises licensing and access by dataset.

Table 5. Licensing and access by dataset

| Dataset/Service | Licence | Access model | Notes |
|---|---|---|---|
| ONS boundaries, names and codes (Open Geography Portal) | OGL v3.0 | Open download | Attribution required; ONSPD has custom licence |
| ONSPD | Custom | Open download | Contains third-party IP; follow ONS licence terms |
| NSPL | Open (see dataset) | Open download | Used for best-fit allocations to geographies |
| OS Open Names | OS OpenData | Open download + API | Free; quarterly updates |
| OS Open Roads | OS OpenData | Open download | Free; twice-yearly updates |
| AddressBase (core) | OS plans | OS Data Hub | Updates every six weeks; CSV/GML |
| AddressBase Premium | OS plans (PSGA, Premium) | OS Data Hub | Updates every six weeks; CSV/GML/GeoPackage; PSGA free for members |
| OS Names API | OS OpenData/API terms | OS Data Hub API | API-specific terms apply |
| Boundary-Line | OS OpenData | OS Data Hub | Free; twice-yearly updates |
| PAF (Royal Mail) | Commercial | Licensed providers | Code of Practice; public sector licensing routes exist |


## Integration and Identifier Strategy

Two identifiers make cross-dataset joins reliable and sustainable:

- Unique Property Reference Number (UPRN). Assigned to addressable locations, the UPRN provides a persistent key across datasets and lifecycle events. It is the cornerstone for property-level linking in AddressBase, enabling you to combine postal attributes, lifecycle changes, and geolocation consistently[^15][^17].

- Unique Street Reference Number (USRN). The USRN identifies streets and their segments. When combined with UPRN, it allows you to link properties to the streets on which they front and to authoritative responsibility and network attributes maintained by local authorities in England and Wales[^24].

OS Open Names and the OS Names API use British National Grid coordinates for features and support multi-lingual naming where applicable. When integrating OS Open Names with ONSPD/NSPL, decide early whether to work in British National Grid (EPSG:27700) or WGS84 (EPSG:4326) and set consistent transformation parameters. For ONSPD/NSPL linkage, use the GSS codes for geographies to join to ONS boundary polygons and names/codes lookups; the LAD to County/UA lookup provides a ready-made bridge for many analyses[^12][^18][^19][^20].

For authoritative street responsibilities and official names in England and Wales, link via USRN from NSG. For GB-wide naming and labelling, use OS Open Names. For property-level postal and lifecycle detail, adopt AddressBase Premium (GB) and join on UPRN[^24][^15][^18].


## Implementation Scenarios and Recommendations

Public sector (PSGA) pipeline. If you are an eligible public sector body, the most complete stack with minimal licensing friction is: ONSPD and NSPL for postcode-to-geography linkages; ONS boundary and names/codes datasets under OGL; AddressBase Premium via PSGA for property-level addressing and lifecycle; OS Open Roads for network context; and OS Open Names for labelling and discovery. GeoPlace services can fill the authoritative street name and responsibility requirements in England and Wales[^3][^10][^24][^30][^37].

Commercial stack (GB focus). For commercial implementations in GB, a practical combination is ONSPD/NSPL for geography linkages, OS Open Names for names/labelling, OS Open Roads for network work, and AddressBase Premium (commercial) for full addressing and lifecycle. Confirm AddressBase licensing and area pricing with OS or licensed partners[^3][^18][^22][^15].

Cost-conscious open stack. For UK-wide coverage with minimal cost, use ONSPD/NSPL plus ONS boundaries and names/codes (OGL). Add OS Open Names and OS Open Roads for GB network and labelling. Where you need official street responsibilities (England and Wales), consider programmatic access to GeoPlace services for specific queries rather than full NSG acquisition if licensing or budget constraints apply[^10][^24].

PAF-dependent scenarios. If your primary need is postal addressing fidelity and you operate within Royal Mail’s licensing framework, PAF (via licensed providers) can serve as your address backbone. Join to ONSPD/NSPL for geography linkage and to AddressBase where UDPRN/UPRN bridging is available. Validate public sector licensing and any redistribution constraints before deployment[^7][^29][^13].

Table 6 summarises the trade-offs.

Table 6. Scenario comparison

| Scenario | Coverage | Licence fit | Cost profile | Update cadence | Strengths | Considerations |
|---|---|---|---|---|---|---|
| PSGA Public Sector | UK (boundaries/postcodes), GB (AddressBase, OS Open products) | OGL + PSGA | Low direct cost (membership) | Quarterly (ONSPD/NSPL), 6-weekly (AddressBase), biannual (Open Roads) | Full property-level via PSGA; minimal licensing friction | PSGA eligibility; ensure attribution and terms compliance |
| Commercial (GB) | UK (ONSPD/NSPL), GB (OS Open, AddressBase) | OS Premium + dataset licences | Commercial | As above | Full addressing and lifecycle; robust APIs | Commercial licensing; plan budgeting |
| Cost-conscious open | UK | OGL | Free | As above | Broad analytical capability at low cost | No property-level unless you augment; limited street responsibilities |
| PAF-led | UK | Royal Mail commercial | Commercial | Continuous updates | Authoritative postal addressing | No built-in geography linkages; manage redistribution and licensing |


## Data Formats and Download Access Matrix

To speed procurement and integration, Table 7 consolidates formats, portals, and update cadences for key datasets.

Table 7. Formats and access matrix

| Dataset | Formats | Access methods | Update frequency |
|---|---|---|---|
| ONSPD | ZIP containing multi-CSV and ASCII TXT | Open Geography Portal | Quarterly |
| NSPL | CSV, TXT | data.gov.uk/Open Geography Portal | Quarterly |
| Online ONSPD (Live) | Downloadable centroid data | ArcGIS Hub | As released |
| ONS Names and Codes | CSV, Excel | Open Geography Portal | As updated |
| Counties & UA Boundaries (Dec 2024, BGC) | Shapefile, GeoJSON, KML, CSV + services | Open Geography Portal | Annual |
| LAD Boundaries (May 2024, BFE) | Multiple + services | Open Geography Portal | Annual |
| LAD to County/UA Lookup (Apr 2025, EW) | CSV, KML, GeoJSON, Shapefile + REST | Open Geography Portal | Annual |
| OS Boundary-Line | Shapefile, GeoPackage, GML, MapInfo TAB, Vector Tiles | OS Data Hub | Twice yearly |
| OS Open Names | CSV, GML, GeoPackage; API | OS Data Hub + OS Names API | Quarterly |
| OS Open Roads | Shapefile, GeoPackage, GML, Vector Tiles | OS Data Hub | Twice yearly |
| AddressBase (core) | CSV, GML | OS Data Hub | Every six weeks |
| AddressBase Premium | CSV, GML, GeoPackage | OS Data Hub (PSGA/Premium) | Every six weeks |
| PAF | Multiple via providers | Solutions providers (Royal Mail) | Continuous |


## Known Gaps and How to Proceed

- PAF detailed schema and pricing. PAF is licensed via solutions providers and pricing is negotiated; public sector licence terms may vary. Confirm specific field-level schema, pricing, and redistribution terms with Royal Mail or your chosen provider[^7][^29].

- National Street Gazetteer full download. GeoPlace exposes NSG content primarily through services (e.g., DataVia API, FindMyStreet). Direct full dataset download availability and any associated licensing should be clarified with GeoPlace for your use-case[^24].

- Northern Ireland street data. Authoritative NI street naming and USRN coverage via OSNI/Local Government channels is not detailed in the sources provided. Engage OSNI and NI local authorities for definitive routes.

- AddressBase core/USRN/UDPRN linkage specifics. Detailed cross-reference fields can vary by AddressBase edition and over time; consult the AddressBase technical specification for definitive linkage guidance between UDPRN, UPRN, and USRN in your target edition[^14][^16][^17].

- OGL vs custom licence edge-cases. ONSPD carries custom licence terms. For derivative works or publication, check ONS licensing pages for the exact constraints before redistribution[^2][^5].

- Post town as a field. While the post town concept is authoritative within PAF, whether it is exposed explicitly in ONSPD/NSPL should be verified in the ONSPD user guide and release documentation before building dependencies[^1][^4][^5].

- ONS boundary datasets for Northern Ireland. Confirm latest NI-specific boundary packs and names/codes where UK-wide completeness is required, as ONS resources sometimes split England & Wales vs Northern Ireland coverage[^3][^10].


## Appendix: Reference Index and Field Spec Snippets

This appendix provides a quick-reference index of the datasets cited and highlights key fields from boundary and lookup resources. For full technical specifications, refer to the linked documentation.

Table 8. Reference index (see numbered references)

| Ref | Title | Notes |
|---|---|---|
| [^1] | Postcode products — Office for National Statistics | ONSPD and NSPL overview and methodology |
| [^2] | Licences — Office for National Statistics | ONS licensing terms and attribution |
| [^3] | Open Geography Portal | ONS boundaries, names/codes, lookups, APIs |
| [^4] | ONS Postcode Directory (February 2024) for the UK | ONSPD release details and download |
| [^5] | ONS Postcode Directory (February 2024) — Data | ONSPD data download |
| [^6] | National Statistics Postcode Lookup (NSPL) — data.gov.uk | NSPL dataset entry and formats |
| [^7] | Powered by PAF | PAF overview, updates, usage, Code of Practice |
| [^8] | Online ONS Postcode Directory (Live) | Live centroids for current postcodes |
| [^9] | National Statistics Postcode Lookup (May 2025) — ArcGIS Hub | NSPL latest release context |
| [^10] | Counties and Unitary Authorities (December 2024) Boundaries UK BGC | Example boundary dataset with fields and services |
| [^11] | Local Authority District to County and Unitary Authority (April 2025) Lookup in EW | LAD to county/UA lookup fields and formats |
| [^12] | Names and codes listings — Office for National Statistics | GSS codes, CSV/Excel downloads |
| [^13] | AddressBase — Ordnance Survey | Product overview, coverage, formats |
| [^14] | AddressBase — OS Downloads Documentation | Technical spec, header files, release notes |
| [^15] | AddressBase Premium — Ordnance Survey | Product overview, scale, cadence |
| [^16] | AddressBase Premium — OS Downloads Documentation | Technical specification and integration details |
| [^17] | Access free address data using AddressBase — GOV.UK | UPRN guidance and free access context |
| [^18] | OS Open Names — Ordnance Survey | Product overview and statistics |
| [^19] | OS Open Names — OS Downloads Documentation | Technical documentation and schema |
| [^20] | OS Names API — Ordnance Survey | API capabilities and limits |
| [^21] | OS Names API — API Catalogue | Cross-government API listing |
| [^22] | OS Open Roads — Ordnance Survey | Product overview and use-cases |
| [^23] | OS Open Roads — OS Downloads Documentation | Technical documentation |
| [^24] | Access street data and services — GeoPlace LLP | NSG, FindMyStreet, DataVia API, USRN |
| [^25] | Boundary-Line — Ordnance Survey | Product overview and licensing |
| [^26] | Boundary-Line — OS Downloads Documentation | Technical docs and formats |
| [^27] | Boundary-Line Open Data Downloads — OS Data Hub | Direct download |
| [^31] | Open Government Licence v3.0 — The National Archives | Licence text and user guidance |
| [^35] | Plans — OS Data Hub | OS plans, including OpenData, Premium, Public Sector |
| [^36] | Helpful licensing terms — Public Sector licensing guide — OS | Public sector licensing guidance |
| [^37] | The PSGA — Ordnance Survey | PSGA scope and access |

ONS Counties & UA boundary example fields (December 2024 BGC). The dataset typically includes identifiers such as CTYUA24CD and CTYUA24NM (name and code), BNG_E/BNG_N (British National Grid coordinates), LONG/LAT, and shape area/length fields. Use these to join to names and codes tables via GSS codes and to aggregate or map statistics appropriately[^10].

ONS LAD to County/UA lookup example fields. The canonical lookup includes LAD25CD/LAD25NM and CTYUA25CD/CTYUA25NM (and Welsh equivalents), enabling many-to-one mapping from districts to counties/unitary authorities. This is particularly useful when analysing data published at LAD level but needing county/UAs rollups[^11].

ONS Names and Codes (Administrative Geographies). Provides GSS nine-character codes in CSV/Excel for administrative units, including counties, regions, and LADs. These code sets underpin consistent joins across ONS products and are essential for accurate data integration and time-series analysis[^12].


## References

[^1]: Postcode products — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/postcodeproducts
[^2]: Licences — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/licences
[^3]: Open Geography Portal. https://geoportal.statistics.gov.uk/
[^4]: ONS Postcode Directory (February 2024) for the UK. https://geoportal.statistics.gov.uk/datasets/e14b1475ecf74b58804cf667b6740706
[^5]: ONS Postcode Directory (February 2024) — Data. https://www.arcgis.com/sharing/rest/content/items/e14b1475ecf74b58804cf667b6740706/data
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
[^30]: The PSGA — Ordnance Survey. https://www.ordnancesurvey.co.uk/customers/public-sector/public-sector-geospatial-agreement
[^31]: Open Government Licence v3.0 — The National Archives. https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
[^35]: Plans — OS Data Hub. https://osdatahub.os.uk/plans
[^36]: Helpful licensing terms — Public Sector licensing guide — OS. https://www.ordnancesurvey.co.uk/customers/public-sector/public-sector-licensing/licensing-terms
[^37]: The PSGA | Government and public sector | OS. https://www.ordnancesurvey.co.uk/customers/public-sector/public-sector-geospatial-agreement