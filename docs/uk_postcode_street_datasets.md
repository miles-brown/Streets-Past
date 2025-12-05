# UK Postal Address and Street Datasets with Complete SE London (SE1–SE18) Coverage: A Practical Guide

## Executive summary: What’s available for SE London and what to use when

This report evaluates the practical options to obtain comprehensive, operationally reliable address and street data for South-East London postcode districts SE1–SE18. The core finding is that there is no single, completely free, open dataset that reliably delivers full, property‑level addresses across SE London at postal delivery precision. Instead, the viable path to complete, authoritative coverage is to combine open data for orientation and search, with licensed data for validation and delivery‑grade completeness.

- Royal Mail’s Postcode Address File (PAF) remains the definitive source of UK delivery points and is widely licensed through third‑party APIs and platforms. It includes the Delivery Point Suffix (DPS) that distinguishes individual dwellings within a postcode unit. Licensing is commercial; a 2024 factsheet outlines price changes and structures, with public sector access agreed to 31 March 2028. PAF’s strengths are delivery precision and coverage of Northern Ireland; its principal constraint for many users is licensing cost and terms.[^22][^23][^24][^25]
- For the public sector, Ordnance Survey’s AddressBase products—free at the point of use under the Public Sector Geospatial Agreement (PSGA)—provide property‑level coverage across Great Britain (England, Scotland, Wales). AddressBase introduces the Unique Property Reference Number (UPRN) for cross‑dataset linking, includes coordinates, and is updated on a frequent cadence. AddressBase Core is the primary product, with Islands and Plus/Premium options for specific needs.[^1][^2]
- As open, no‑cost complements, the Office for National Statistics (ONS) Postcode Directory (ONSPD) and National Statistics Postcode Lookup (NSPL) map postcodes to geographies and are released quarterly; Ordnance Survey’s Code‑Point Open provides point geometries for all current postcode units in Great Britain; OS Open Names offers street names and place names; and OpenStreetMap (OSM) contributes volunteered geographic information and is often strong in urban areas like London. These open datasets are valuable for geocoding, list generation by outward code (e.g., “SE1”), and mapping, but do not guarantee full, property‑level, delivery‑grade address completeness.[^8][^7][^9][^4][^12][^13][^14]
- Practical APIs for development: Postcodes.io provides a free, well‑documented postcode lookup and reverse geocoding API powered by ONS/OS data; getAddress.io and Ideal Postcodes deliver richer, property‑level results and add features like UPRN and rooftop geocodes under commercial terms; OS Places API offers a UK address search service with geosearch; Google Address Validation is supported in the UK and can standardize addresses but does not replace authoritative UK address databases.[^3][^15][^16][^20][^17][^19]

To anchor these choices in operational needs, Table 1 summarises the best‑fit dataset for common scenarios across SE London. The central insight is straightforward: use open datasets to discover and navigate, and use licensed datasets to validate and deliver.

To illustrate the decision points succinctly, the following matrix compares options by use case, with notes on coverage and constraints for SE London.

Table 1. At‑a‑glance matrix of recommended datasets by use case

| Use case | Best‑fit option(s) | Why this fit | Coverage notes | Key constraint(s) |
|---|---|---|---|---|
| Property‑level address capture/validation (web forms) | AddressBase (PSGA), or getAddress.io / Ideal Postcodes; optionally Google Address Validation for standardization | Delivery‑grade completeness (PAF‑derived in AddressBase), UPRN for linking; commercial APIs add usability and support | Great Britain for AddressBase; UK for commercial APIs; UK support for Google | Licensed data (fees/terms) for AddressBase and APIs; Google is complementary, not a PAF replacement[^1][^2][^15][^16][^17] |
| Street‑level mapping by outward code (SE1–SE18) | OS Open Names + Code‑Point Open + ONSPD; OSM for enrichment | Street names, place names, postcode points, and postcode‑to‑admin linkages; strong for London in OSM | Great Britain for OS Open Names/Code‑Point; UK for ONSPD; global for OSM | OS Open and ONSPD are open but do not guarantee full property lists; OSM completeness varies[^4][^9][^8][^12][^13][^14] |
| Bulk postcode‑to‑admin area lookups | ONSPD/NSPL | Official quarterly mappings; best‑fit geographies | UK coverage | Not property‑level; CSV/TXT formats require integration work[^8][^7] |
| Quick prototyping / low‑volume postcode geocoding | Postcodes.io | Free, open API with comprehensive postcode data | UK postcodes | Not property‑level; dependent on ONS/OS refresh cadence[^3] |
| Emergency services or public sector operational use | AddressBase (PSGA) + OS Places | UPRN linking, frequent updates, geosearch for closest properties | Great Britain | Requires PSGA membership; OS Places is a paid API[^1][^2][^20] |
| Research or public‑facing mapping (no property‑level requirements) | OS Open Names + Code‑Point Open + ONSPD (+ OSM) | Open, no‑cost combination for visualization and analysis | Great Britain/UK per dataset | Variable completeness vs licensed sources; ODbL considerations for OSM derivatives[^4][^9][^8][^12][^13] |

This report provides detail on data sources, licensing, APIs, and a practical workflow for SE London, along with documented limitations. The practical recommendation is a hybrid stack: start with open data to build functionality and coverage quickly, then integrate licensed sources—AddressBase for public sector use, PAF‑based APIs (getAddress.io, Ideal Postcodes) for commercial delivery—to achieve full, delivery‑grade precision across SE1–SE18.

---

## Scope, definitions, and how UK addressing works

Addressing data in the UK is shaped by two overlapping systems: the postal delivery ecosystem and the geospatial addressing system. Understanding their identifiers, coverage, and licensing is essential for building reliable services in SE London.

Postal delivery and PAF. Royal Mail’s Postcode Address File (PAF) is a database of “delivery points”—addresses that receive mail. PAF includes the standard address elements (building name/number, street, locality, town, county, postcode) and a Delivery Point Suffix (DPS) that uniquely identifies each delivery point within a postcode unit. The Postcode Address File is the operational backbone for mail delivery and is widely licensed to third‑party providers. PAF covers all four nations of the UK, including Northern Ireland. It is not open data; licensing fees and terms apply, with a Code of Practice governing usage. Royal Mail has actively defended its database rights, and public sector access to PAF has been agreed to 31 March 2028.[^22][^25][^26]

Geospatial addressing and AddressBase. Ordnance Survey’s AddressBase products are the authoritative geospatial complement. AddressBase assigns a Unique Property Reference Number (UPRN) to every addressable location in Great Britain, enabling robust cross‑dataset linking and geographic location. AddressBase is available free to eligible public sector bodies under the Public Sector Geospatial Agreement (PSGA). AddressBase products are updated frequently and include coordinates and rich metadata; AddressBase Core is the primary product for operational use, with Islands (for Northern Ireland and Crown Dependencies), Plus, and Premium variants for advanced requirements. GeoPlace—formed by local government associations and Ordnance Survey—provides related guidance and the UPRN standard.[^1][^2][^10][^11]

Postcodes and open datasets. UK postcodes are units used for postal routing. The ONS Postcode Directory (ONSPD) and National Statistics Postcode Lookup (NSPL) map current and terminated postcodes to administrative and health geographies using best‑fit methodologies; they are updated quarterly and released under the Open Government Licence. Code‑Point Open provides point geometries for all current postcode units in Great Britain, and OS Open Names offers street names and place names. These open datasets are ideal for geocoding, analysis, and mapping, but are not substitutes for delivery‑grade address lists.[^8][^7][^9][^4]

Voluntary contributions and OSM. OpenStreetMap is a global, community‑maintained map dataset licensed under the Open Database License (ODbL). Postal code features and address points are mapped by contributors, and OSM coverage in London is generally strong. However, OSM is not guaranteed to be complete or uniform, and address tagging practices vary.[^12][^13]

Implications for SE London. SE London has active development and dense urban fabric, and both PAF and AddressBase reflect frequent updates. Open datasets (ONSPD, Code‑Point Open, OS Open Names, OSM) are excellent for building street lists by outward code, for postcode‑to‑admin mappings, and for mapping layers. For capture and validation of individual addresses, however, licensed data—AddressBase for public sector and PAF‑sourced APIs for commercial use—are necessary to achieve completeness and delivery precision, particularly for multi‑occupancy buildings and new developments.

To clarify the terminology and constraints across datasets, Table 2 presents a concise glossary.

Table 2. Glossary of key terms

| Term | Definition | Typical use | Notes |
|---|---|---|---|
| Postcode Address File (PAF) | Royal Mail database of delivery points (mail‑receiving addresses) | Postal validation, address capture | Includes DPS; licensed; UK coverage including Northern Ireland[^22][^25] |
| Delivery Point Suffix (DPS) | A suffix that uniquely identifies a delivery point within a postcode | Precise address differentiation | Enables unique property identification within a postcode unit[^22] |
| Unique Property Reference Number (UPRN) | Persistent identifier for every addressable location in Great Britain | Cross‑dataset linking, geospatial joins | Mandated in public sector geospatial standards[^11][^10] |
| ONSPD | ONS Postcode Directory—postcodes linked to administrative geographies | Analysis, joins to admin statistics | Quarterly; UK coverage; OGL[^8][^7] |
| NSPL | National Statistics Postcode Lookup—best‑fit allocation of postcodes to geographies | Statistical allocation and reporting | Quarterly; methodology differs from ONSPD in places[^8] |
| Code‑Point Open | Point geometries for current postcode units in Great Britain | Mapping, geocoding | Open data; Great Britain coverage[^9] |
| OS Open Names | Street names and place names for Great Britain | Street lists, labeling maps | Open data; quarterly updates[^4] |
| OpenStreetMap (OSM) | Community‑maintained global map data | Mapping, enrichment | Coverage varies; ODbL license[^12][^13] |

---

## Royal Mail Postcode Address File (PAF): Coverage, access, and licensing

PAF is the UK’s definitive list of addresses that receive mail. For SE London, PAF completeness and delivery precision are essential for any service that must identify every dwelling or business delivery point—critical for logistics, emergency response, and customer onboarding.

Structure and identifiers. A PAF record comprises the standard address elements plus the Delivery Point Suffix (DPS), which differentiates delivery points sharing the same postcode. Together, postcode plus DPS form a unique identifier for a delivery point. PAF includes both residential and business addresses and covers all UK nations, including Northern Ireland. As a managed operational dataset, PAF is updated frequently to reflect new builds, changes, and cancellations.[^22][^25]

Access models. Direct licensing from Royal Mail is available to organizations for internal use, solution provider licensing enables vendors to build products and services, and corporate licensing covers parent‑subsidiary structures. Many organizations access PAF indirectly through licensed APIs and platforms operated by third parties (e.g., getAddress.io, Ideal Postcodes, Loqate, Melissa). For public sector bodies, separate agreements govern access to PAF; these have been agreed to 31 March 2028.[^24][^25]

Licensing and price signals. PAF licensing is commercial and tiered. Royal Mail’s pricing factsheet (2024) and updates provide structure and price changes. Microbusinesses and charities may be eligible for limited free use in specific circumstances; ongoing or commercial use requires fees. Solution providers and direct end‑user pricing differ, and corporate licensing options cover multi‑entity use. For budgeting, organizations should review the factsheet and engage with Royal Mail or solution providers for current rates and terms.[^23][^24]

Compliance and governance. Royal Mail’s Code of Practice sets standards for data use, including appropriate application and handling of PAF. Enforcement and legal protections around PAF database rights have been reinforced in recent cases, underscoring the need for compliant licensing.[^25][^26]

Pros and cons. PAF delivers delivery‑grade completeness across the UK and is the appropriate choice for mail‑related operations. However, licensing cost and terms can be prohibitive for some use cases, particularly where open data alternatives suffice for mapping and analysis.

To support procurement and compliance planning, Table 3 summarises PAF access routes, and Table 4 outlines licensing categories and eligibility.

Table 3. PAF access routes and typical use cases

| Access route | How it works | Typical use cases | Notes |
|---|---|---|---|
| Direct licensing (Royal Mail) | License PAF directly for internal use or solutions | Enterprise systems; mail operations; compliance‑critical workflows | Pricing and terms vary by volume and application[^24] |
| Solution provider / reseller | Use APIs or datasets from licensed providers | Web forms, CRM integrations, address capture tools | Simplifies integration; cost embedded in service fees[^15][^16] |
| Corporate license | Parent‑subsidiary coverage under one license | Multi‑entity organizations | Centralized compliance and governance[^24] |
| Public sector access | Agreements for public bodies to access PAF | Local authorities, NHS, emergency services | Access term agreed to 31 March 2028[^23] |

Table 4. Licensing categories and eligibility

| Category | Eligibility | Permitted uses | Constraints |
|---|---|---|---|
| Direct End User | Organizations using PAF internally | Internal use within licensed entity | Fees, audit, and compliance obligations[^24] |
| Solution Provider | Organizations building products/services on PAF | Provide APIs/solutions to end users | Must be licensed; additional terms apply[^24] |
| Corporate | Parent company and subsidiaries | Group‑wide usage under one license | Centralized management; fees vary[^24] |
| Microbusiness | <9 employees, turnover <£2m | Development use for one year free | Conditions apply; fees for continued or other uses[^24] |
| Charities | UK charities/CICs with income <£10m | Non‑commercial use free | Commercial use or other data products require fees[^24] |
| Public sector | Public bodies under agreed access | Operational use | Access term to 31 March 2028[^23] |

---

## Ordnance Survey and ONS open datasets: What you can legally use for free

Open datasets enable robust, no‑cost geospatial functionality for SE London. While they do not replace licensed, property‑level address products, they are foundational for street lists, postcode mapping, and administrative linkages.

ONS Postcode Directory (ONSPD) and NSPL. ONSPD links all current and terminated UK postcodes to administrative, health, and other geographies via a point‑in‑polygon methodology; NSPL provides best‑fit allocation to geographies for statistical production. Both are released quarterly and are available under the Open Government Licence. They are ideal for joining postcode data to administrative statistics and for geodemographic analysis.[^8][^7]

Code‑Point Open. Ordnance Survey’s Code‑Point Open provides point locations for all current postcode units in Great Britain, suitable for mapping, proximity operations, and basic geocoding. It is open and free to use.[^9]

OS Open Names. OS Open Names includes street names and place names for Great Britain, updated quarterly, and can be used to compile authoritative street lists and labeling layers. It complements Code‑Point Open by focusing on named features rather than postal points.[^4]

OS Places API. OS Places offers a UK‑wide address search service with geosearch capabilities, supporting use cases like identifying closest properties for emergency services. OS Places is a paid API, typically used where robust commercial support and service levels are required.[^20]

Public sector AddressBase. For eligible public sector organizations, AddressBase products are free at the point of use under the PSGA and are the preferred source for property‑level addressing across Great Britain, with UPRN linking and frequent updates.[^1][^2]

To clarify update cadence and format, Table 5 summarises these open datasets and their operational characteristics.

Table 5. Open dataset comparison

| Dataset | Coverage | Update frequency | Formats | License | Primary fields/geometry | Notes |
|---|---|---|---|---|---|---|
| ONSPD | UK (current and terminated postcodes) | Quarterly | CSV, TXT | Open Government Licence | Postcode, admin/health geographies | Best‑fit for higher geographies[^8][^7] |
| NSPL | UK postcodes (best‑fit allocation) | Quarterly | CSV, TXT | Open Government Licence | Postcode to Output Areas and higher geographies | Methodology differs from ONSPD[^8] |
| Code‑Point Open | Great Britain (current postcode units) | As per OS release cycle | CSV/GIS formats | Open (OS OpenData) | Point geometry for postcode units | Postcode centroids[^9] |
| OS Open Names | Great Britain | Quarterly | CSV, GML, GeoPackage | Open (OS OpenData) | Street names, place names | Useful for street lists[^4] |
| OS Places API | UK | Commercial service | API | Paid API | Address search, geosearch | Complementary to AddressBase[^20] |

---

## Third‑party UK address APIs and databases: How they extend open data

Open datasets provide essential building blocks, but property‑level completeness and usability often require third‑party APIs and platforms that license PAF or draw on AddressBase.

Postcodes.io. Postcodes.io is a free, open‑source API maintained by Ideal Postcodes. It provides postcode validation, lookup, reverse geocoding, and autocomplete, drawing on ONS and Ordnance Survey datasets. It is ideal for quick prototyping, low‑volume geocoding, and building postcode‑centric features. It is not property‑level and is updated when ONS/OS data is refreshed.[^3]

getAddress.io. getAddress.io offers autocomplete, postcode lookup, typeahead, location, and distance features, with flexible subscriptions and daily updates. The service claims near‑complete UK address coverage by aggregating multiple sources including Ordnance Survey’s Code‑Point Open and other registers, and provides easy‑to‑use client libraries. It is suited to commercial web forms and CRM integrations that need richer address functionality.[^15][^16]

Ideal Postcodes. Ideal Postcodes provides a commercial address validation service, including UPRN and rooftop geocodes in the UK at no extra charge on lookups, with pay‑as‑you‑go and enterprise plans. It is designed for production use with support and service‑level commitments, and offers 240+ international coverage as well as UK datasets. This is suitable where property‑level precision, UPRN linkage, and operational support are required.[^20]

OS Places API. OS Places offers a paid, secure, and resilient UK address search service with geosearch, including features to identify closest properties—useful for emergency services or operational field use. It complements open datasets and AddressBase by providing a robust API layer.[^20]

Google Address Validation API. Google provides address validation for the UK, with address metadata and standardization. This can be helpful for front‑end forms and data hygiene, but does not replace UK‑specific authoritative address sources like AddressBase or PAF‑based services. Billing is per‑call under Google Maps Platform pricing, with coverage details published by Google.[^17][^19]

To aid selection, Table 6 compares these APIs by core features and integration.

Table 6. API feature comparison

| API | Coverage | Property‑level | UPRN | Rate limits | Pricing signal | Best‑fit use cases |
|---|---|---|---|---|---|---|
| Postcodes.io | UK postcodes | No | No | Public API | Free | Prototyping; low‑volume geocoding; postcode‑centric features[^3] |
| getAddress.io | UK addresses | Yes (via aggregated sources) | Not specified | Subscription‑based | Paid (tiered) | Commercial web forms; CRM integrations; autocomplete[^15][^16] |
| Ideal Postcodes | UK (+ international) | Yes | Yes | Commercial | Paid (PAYG/enterprise) | Production address validation; UPRN; rooftop geocodes[^20] |
| OS Places API | UK addresses | Yes | Not the focus | Commercial | Paid | Enterprise geosearch; operational field scenarios[^20] |
| Google Address Validation | UK supported | Standardization only | No | Per‑call | Paid (Maps Platform) | Complementary validation and standardization[^17][^19] |

---

## OpenStreetMap for SE London: Extracts, tools, and Overpass patterns

OpenStreetMap (OSM) is a flexible, open data source for streets and address points in London. The Overpass API allows targeted extraction of features, which can be filtered by area, tags, and geometry.

Query strategies with Overpass. Overpass functions as a database‑over‑the‑web, accepting declarative queries and returning OSM elements (nodes, ways, relations). For SE London, common patterns include selecting ways tagged with highway names and retrieving associated address nodes or building footprints. Queries can be constrained by bounding boxes or by administrative areas, enabling focused extracts for each outward code (e.g., SE1).[^12]

Postal code features. While OSM includes postal code tags (e.g., “postal_code=SE1 1AA”), completeness and consistency are not guaranteed. For practical work, use OSM features for street names, locality names, and building footprints, and rely on ONSPD or Code‑Point Open for authoritative postcodes and centroids. Where OSM address nodes exist, they can augment property‑level coverage, but variability should be expected.[^13][^14]

Exporting and tooling. Overpass turbo provides a web IDE to build queries and export data; programmatic access is possible via the Overpass REST API. Exports can be filtered for SE districts and converted into GIS or relational formats for analysis. London‑specific references—such as OSM’s London page and community data portals—can help orient the mapper to coverage and resources.[^12][^37]

To make this practical, Table 7 proposes a query recipe plan for SE outward codes.

Table 7. Overpass query recipe plan for SE outward codes

| Target | Example pattern (pseudo‑query) | Expected features | Export format | Notes |
|---|---|---|---|---|
| Streets in SE1 | `way[highway][name](area:SE1);` | Highway ways with names | GeoJSON, OSM PBF | Add `out;` to return results; wrap with `(area:SE1);`[^12] |
| Address nodes in SE1 | `node[addr:housenumber][addr:street](area:SE1);` | Address points | GeoJSON | Completeness varies by mapping[^13] |
| Buildings in SE1 | `way[building](area:SE1);` | Building footprints | GeoJSON | Useful for footprint‑to‑postcode joins via centroids[^14] |

Operationally, OSM is most valuable in London for building street networks, enriching place names, and providing additional context. It should be used as a complement to ONSPD, Code‑Point Open, and OS Open Names for postcode‑aware applications.

---

## Free public APIs and datasets that list streets by postcode area

Generating a street list by outward code (e.g., “all streets in SE1”) can be approached in three legal ways without breaching licensing terms.

Approach A: Use ONSPD + Code‑Point Open. Extract all postcode units for the outward code (SE1) from ONSPD or Code‑Point Open, then join to OS Open Names by locality or street name to assemble a street list. This leverages official open datasets, producing a reproducible list of street names within the district.[^8][^9][^4]

Approach B: Use Postcodes.io to enumerate units and map to streets. Call Postcodes.io to retrieve postcodes for SE1, then join those records to OS Open Names or OSM features to derive streets. This method is practical for developers and avoids proprietary data, though it remains dependent on open data refresh cadence.[^3][^4]

Approach C: OSM‑centric extraction. Use Overpass to query highway ways within each outward code area, extract unique street names, and normalize. Postcodes can be attached where available via tags, and centroids can be snapped to ONSPD points for verification.[^12][^14]

To compare effort and reliability, Table 8 outlines these methods.

Table 8. Methods to compile street lists by outward code

| Method | Steps | Effort | Reliability | Pros | Cons |
|---|---|---|---|---|---|
| A: ONSPD + Code‑Point + OS Open Names | 1) Load ONSPD/Code‑Point for SEx; 2) Join to OS Open Names | Moderate | High (open data) | Official open data; reproducible | Not property‑level; manual joins[^8][^9][^4] |
| B: Postcodes.io + OS Open Names | 1) Query postcodes for SEx; 2) Join to OS Open Names | Low | High (open data) | Simple API; quick prototyping | Depends on ONS/OS cadence; not property‑level[^3][^4] |
| C: OSM Overpass | 1) Query highways by area; 2) Extract street names | Moderate | Variable | Rich context; flexible | Completeness varies; normalization needed[^12][^13][^14] |

---

## Data quality and completeness for SE1–SE18: What to expect by source

Quality expectations differ markedly between licensed and open sources, and across urban vs. rural contexts.

PAF and AddressBase. Both represent authoritative addressing at different levels. PAF is delivery‑point centric and includes the DPS, making it the definitive record for postal operations. AddressBase assigns a UPRN to every addressable location in Great Britain, enabling robust cross‑dataset linking and geospatial precision; it is the preferred choice for public sector bodies under the PSGA. AddressBase’s frequent updates and metadata make it ideal for operational systems that require both precision and inter‑operability.[^1][^2][^25]

Open sources. ONSPD and NSPL are robust for postcode‑to‑geography mapping. Code‑Point Open provides reliable postcode centroids for Great Britain. OS Open Names offers street and place names at authoritative quality, refreshed quarterly. OpenStreetMap’s coverage in London is often strong, but address and postal code tagging can be uneven and should be treated as supplementary rather than authoritative.[^8][^9][^4][^12][^13]

SE London specific considerations. Dense urban areas and active development in SE London mean that new addresses and conversions appear frequently. Open sources may lag operational changes, while AddressBase and PAF‑based products are refreshed more frequently, making them better suited for time‑sensitive operations and comprehensive coverage.

Validation strategies. The most practical approach is a triangulation method: use ONSPD to enumerate postcodes and geographies; verify centroids via Code‑Point Open; cross‑check streets using OS Open Names and OSM; and validate properties via AddressBase (PSGA) or PAF‑based APIs. UPRN should be used as the stable identifier for joins and inter‑operability in the public sector.[^1][^2][^11]

Table 9 summarises expected completeness by dataset type across SE1–SE18.

Table 9. Completeness matrix for SE1–SE18 by dataset type

| Dataset | Expected completeness | Strengths | Limitations | SE London notes |
|---|---|---|---|---|
| PAF | Very high | Delivery‑grade; DPS uniqueness | Licensing; access via fees | Strong for delivery precision[^25] |
| AddressBase (PSGA) | Very high | UPRN linking; coordinates; frequent updates | Great Britain only; PSGA eligibility | Preferred for public sector ops[^1][^2] |
| ONSPD | High (postcode coverage) | Official mappings; quarterly | Not property‑level | Good for enumeration[^8][^7] |
| Code‑Point Open | High (postcode centroids) | Open; stable | Great Britain only; centroid not polygon | Useful for proximity[^9] |
| OS Open Names | High (streets/places) | Authoritative street names | Not a property list | Good for street lists[^4] |
| OSM | Variable | Rich map context; flexibility | Inconsistent tagging | Strong in London; supplement only[^12][^13] |

Information gaps. Current, provider‑specific SE London completeness metrics per dataset are not publicly documented; Postcodes.io coverage does not enumerate SE districts; OSM completeness in SE London requires empirical sampling; pricing for PAF is not fully enumerated publicly; Code‑Point Open page content was not fully extracted here; public availability of street‑list APIs at zero cost is limited; and OSM does not guarantee postal code tagging completeness. These gaps inform the recommended validation approach and reliance on licensed sources for production completeness.

---

## Access and integration: APIs, endpoints, and ingestion patterns

For teams integrating datasets into applications and data pipelines, clear patterns and schema awareness are essential.

Key endpoints. Postcodes.io supports lookup by postcode (`/postcodes/:postcode`) and reverse geocoding, plus bulk operations and autocomplete; it provides administrative and geospatial fields in responses. getAddress.io exposes endpoints for autocomplete, find (postcode lookup), typeahead, location, and distance, with client libraries and rate‑limited subscription tiers. OS Places API offers a search places endpoint for UK addresses and geosearch. Google’s Address Validation API provides UK coverage for address standardization.[^3][^16][^20][^17]

Response schemas. Postcodes.io returns fields for postcode, admin geographies, and coordinates, enabling joins to ONSPD and OS Open Names. getAddress.io’s endpoints return structured addresses and related metadata suitable for form capture. OS Places returns address features and supports geosearch. Google Address Validation returns standardized components and metadata.

UPRN usage. For the public sector, UPRN is the recommended stable identifier to link addresses across datasets and systems. Incorporating UPRN in data models enables consistent joins and interoperability.[^11]

Caching, rate limiting, and monitoring. Production systems should cache results, implement backoff for rate limits, and monitor API health and data freshness. Postcodes.io and getAddress.io provide documentation and status resources to guide integration and reliability planning.[^3][^16]

To make the integration landscape concrete, Table 10 summarises endpoint patterns and authentication considerations.

Table 10. Endpoint cheat‑sheet

| API | Base | Key endpoints | Auth | Typical responses | Notes |
|---|---|---|---|---|---|
| Postcodes.io | Public | `/postcodes/:postcode`; reverse geocode; bulk; autocomplete | Public | Postcode fields, admin geographies, coordinates | Free, open‑source API[^3] |
| getAddress.io | Public | Autocomplete; Find; Typeahead; Location; Distance | API key / subscription | Structured addresses; metadata | Client libraries; tiered plans[^16] |
| OS Places API | OS Data Hub | Search places; geosearch | API key / license | Address features; geosearch results | Paid service; UK coverage[^20] |
| Google Address Validation | Google Maps Platform | Address Validation | API key / billing | Standardized address components; metadata | UK supported; per‑call billing[^17][^19] |

---

## Licensing, legal, and compliance considerations

Compliance should be embedded from design through deployment.

OGL and ODbL. ONSPD/NSPL are released under the Open Government Licence (OGL), enabling free use for most purposes with attribution. OpenStreetMap data is licensed under ODbL; derivative databases and public use require attribution and share‑alike provisions. OS Open Names and Code‑Point Open are open under OS OpenData terms. Organizations must ensure correct attribution and understand share‑alike implications when distributing derived datasets.[^7][^12][^4][^9]

PSGA and AddressBase. Public sector access to AddressBase is enabled through the PSGA. AddressBase products are free at the point of use for eligible bodies and updated frequently, with weekly full dataset versions and continuous core updates. Using AddressBase ensures alignment with the UPRN standard and the UK Geospatial Strategy.[^1][^2]

PAF licensing. PAF is a licensed dataset with commercial terms. Microbusinesses and charities may qualify for limited free use; otherwise, fees apply for continued or commercial use. Solution providers must be licensed to integrate PAF into products and services. Audit and compliance obligations are part of the licensing agreements, and Royal Mail has actively protected its database rights.[^24][^23][^25][^26]

Operational guidance. Maintain audit trails for address data ingestion and use; implement clear attribution and license notices for open datasets; align public sector workflows with UPRN and PSGA guidance; and segregate responsibilities when mixing open and licensed data to avoid license contamination.

Table 11 provides a licensing summary.

Table 11. Licensing summary

| Dataset/API | License | Cost signal | Key obligations |
|---|---|---|---|
| ONSPD/NSPL | OGL | Free | Attribution; follow OGL terms[^7] |
| Code‑Point Open | OS OpenData | Free | Attribution per OS terms[^9] |
| OS Open Names | OS OpenData | Free | Attribution per OS terms[^4] |
| OpenStreetMap | ODbL | Free | Attribution; share‑alike for derivatives[^12] |
| AddressBase (PSGA) | PSGA | Free for eligible public sector | Eligibility; UPRN usage; PSGA terms[^1][^2] |
| PAF | Royal Mail licence | Commercial fees | Eligibility; compliance; audit; usage constraints[^24][^25][^26] |
| OS Places API | OS license | Paid API | Terms per OS Data Hub[^20] |
| getAddress.io / Ideal Postcodes | Commercial | Paid | Subscription terms; permitted uses[^15][^16] |
| Google Address Validation | Google Maps Platform | Paid | Billing; service‑specific terms[^19] |

---

## Recommendations and implementation plan for SE London use cases

The overarching recommendation is a hybrid stack: combine open datasets for discovery, mapping, and enumeration, and integrate licensed datasets for property‑level completeness and operational validation.

Recommended hybrid stacks.

- Public sector operations. Use AddressBase (PSGA) as the primary source for property‑level addressing and UPRN linkage, with OS Open Names for street lists and Code‑Point Open for postcode centroids. Add OS Places API for geosearch where necessary.[^1][^2][^4][^9][^20]
- Commercial web forms and CRM. Use a PAF‑based API such as getAddress.io or Ideal Postcodes for address capture and validation, with Postcodes.io for auxiliary postcode geocoding and ONSPD for postcode‑to‑admin joins.[^15][^16][^3][^8]
- Research and public‑facing maps. Use OS Open Names + Code‑Point Open + ONSPD, with OSM enrichment for contextual detail. This stack is cost‑free and robust for mapping, but should be validated against licensed sources where precision matters.[^4][^9][^8][^12]

SE London workflow. To compile street lists by outward code, follow the “ONSPD + Code‑Point + OS Open Names” method: enumerate postcodes for the target outward code (SE1–SE18), join to OS Open Names for street names, and validate using OSM overlays. For property‑level validation, ingest AddressBase (PSGA) or PAF‑based APIs. Use UPRN as the key identifier wherever possible to maintain inter‑operability.

Roadmap. Start with a proof of concept using open datasets (ONSPD, Code‑Point Open, OS Open Names, Postcodes.io), then integrate licensed APIs (getAddress.io, Ideal Postcodes) for production. If public sector eligibility exists, onboard AddressBase via PSGA and align internal data models to UPRN. Establish continuous data refresh processes tied to quarterly releases and provider update cadences.

To ground these recommendations, Table 12 presents a decision matrix by use case.

Table 12. Decision matrix

| Requirement | Preferred dataset/API | Rationale | Expected coverage | Integration effort |
|---|---|---|---|---|
| Property‑level validation in commercial apps | getAddress.io or Ideal Postcodes | Delivery‑grade completeness; support | UK coverage | Moderate (API integration, caching)[^15][^16][^20] |
| Public sector property‑level operations | AddressBase (PSGA) | UPRN; frequent updates; free | Great Britain | Moderate (PSGA onboarding; UPRN adoption)[^1][^2][^11] |
| Street‑level listing by outward code | OS Open Names + Code‑Point Open + ONSPD | Authoritative street/postcode data | Great Britain/UK | Low‑moderate (joins; data cleaning)[^4][^9][^8] |
| Prototyping postcode geocoding | Postcodes.io | Free, simple API | UK | Low (HTTP calls; schema mapping)[^3] |
| Complementary address standardization | Google Address Validation | Standardize addresses; UK supported | UK | Low (billing; front‑end integration)[^17][^19] |

---

## Appendices

### A. Quick‑reference dataset catalogue

Table 13. Dataset catalogue

| Name | Provider | Coverage | Update frequency | License | URL | Notes |
|---|---|---|---|---|---|---|
| ONS Postcode Directory (ONSPD) | ONS | UK | Quarterly | OGL | See [^8], [^7] | Current and terminated postcodes |
| National Statistics Postcode Lookup (NSPL) | ONS | UK | Quarterly | OGL | See [^8] | Best‑fit methodology |
| Code‑Point Open | Ordnance Survey | Great Britain | Per release | OS OpenData | See [^9] | Postcode unit points |
| OS Open Names | Ordnance Survey | Great Britain | Quarterly | OS OpenData | See [^4] | Street and place names |
| AddressBase (Core/Islands/Plus/Premium) | Ordnance Survey (PSGA) | Great Britain (+ Islands) | Frequent (weekly full versions) | PSGA | See [^1], [^2] | UPRN; property‑level |
| OS Places API | Ordnance Survey | UK | Service cadence | Paid API | See [^20] | Address search; geosearch |
| Postcodes.io | Ideal Postcodes (open‑source) | UK | Per ONS/OS refresh | MIT | See [^3] | Postcode API |
| getAddress.io | getAddress.io | UK | Daily | Commercial | See [^15], [^16] | Autocomplete; find; tiers |
| Ideal Postcodes | Ideal Postcodes | UK (+ international) | Commercial cadence | Commercial | See [^20] | UPRN; rooftop geocodes |
| OpenStreetMap | OSM Foundation | Global | Continuous | ODbL | See [^12], [^37] | Community data |
| Google Address Validation | Google | UK supported | Continuous | Paid | See [^17], [^19] | Complementary validation |

### B. API quick‑reference endpoints

Table 14. API quick‑reference

| API | Base | Endpoint pattern | Auth | Example response fields | Rate limit notes |
|---|---|---|---|---|---|
| Postcodes.io | Public | `/postcodes/{postcode}` | Public | postcode, admin areas, latitude, longitude | Public API; follow docs[^3] |
| getAddress.io | Public | Autocomplete; Find; Typeahead; Location; Distance | API key | formatted address, ids, metadata | Tiered limits per plan[^16] |
| OS Places API | OS Data Hub | Search places v1 | API key | address features, geosearch | Commercial service terms[^20] |
| Google Address Validation | Google Maps Platform | Address Validation | API key | standardized address components, metadata | Per‑call billing; UK supported[^17][^19] |

### C. Sample queries and patterns

- Overpass API example: retrieve all highway ways named within an SE outward code area and export as GeoJSON for street list compilation (see Overpass documentation and examples).[^12]
- Postcodes.io lookup: call `/postcodes/{postcode}` to retrieve admin geographies and coordinates for a given postcode unit; use bulk or autocomplete methods for list generation and form capture.[^3]

---

## References

[^1]: Access free address data using AddressBase - GOV.UK. https://www.gov.uk/guidance/access-free-address-data-using-addressbase  
[^2]: AddressBase | Data Products | Ordnance Survey. https://www.ordnancesurvey.co.uk/products/addressbase  
[^3]: Postcodes.io: Postcode & Geolocation API for the UK. https://postcodes.io/  
[^4]: OS Open Names | Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-open-names  
[^5]: OS Open Names - Data.gov.uk. https://www.data.gov.uk/dataset/4949c88e-89b7-49b5-a0cf-8a3a2a4dac9d/os-open-names1  
[^6]: Open Data Downloads | OS Data Hub. https://osdatahub.os.uk/data/downloads/open  
[^7]: Postcode products - Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/postcodeproducts  
[^8]: ONS Postcode Directory (ONSPD) for the UK - Geoportal. https://geoportal.statistics.gov.uk/datasets/b54177d3d7264cd6ad89e74dd9c1391d  
[^9]: Code-Point Open | Ordnance Survey. https://www.ordnancesurvey.co.uk/products/code-point-open  
[^10]: Addressing the UK - GeoPlace (PDF). https://static.geoplace.co.uk/downloads/Addressing-the-UK.pdf  
[^11]: The UPRN - GeoPlace. https://www.geoplace.co.uk/addresses-streets/location-data/the-uprn  
[^12]: Overpass API - OpenStreetMap Wiki. https://wiki.openstreetmap.org/wiki/Overpass_API  
[^13]: Postal codes in the United Kingdom - OpenStreetMap Wiki. https://wiki.openstreetmap.org/wiki/Postal_codes_in_the_United_Kingdom  
[^14]: London - OpenStreetMap. https://www.openstreetmap.org/relation/65606  
[^15]: getAddress() - Simple APIs for UK Addresses. https://getaddress.io/  
[^16]: getAddress.io Documentation. https://documentation.getaddress.io/  
[^17]: Address Validation API coverage details - Google Developers. https://developers.google.com/maps/documentation/address-validation/coverage  
[^18]: Address Validation API overview - Google Developers. https://developers.google.com/maps/documentation/address-validation/overview  
[^19]: Google Maps Platform Pricing. https://mapsplatform.google.com/pricing/  
[^20]: OS Places API - API Catalogue. https://www.api.gov.uk/os/os-places-api/  
[^21]: UK Address and Postal Data FAQ: AddressBase, UPRN, PAF, and ... https://coordable.co/blog/uk-address-postal-data-faq/  
[^22]: Postcode Address File - Wikipedia. https://en.wikipedia.org/wiki/Postcode_Address_File  
[^23]: Public sector access to Royal Mail Postcode Address File agreed to 2028 - GOV.UK. https://www.gov.uk/government/news/public-sector-access-to-royal-mail-postcode-address-file-agreed-to-2028  
[^24]: PAF Pricing Factsheet (2024). https://www.poweredbypaf.com/wp-content/uploads/2024/11/20240618-2024-Pricing-Factsheet.pdf  
[^25]: PAF Code of Practice - Royal Mail (PDF). https://www.royalmail.com/sites/default/files/PAF-Code-of-Practice-211118.pdf  
[^26]: Royal Mail successfully protects rights in its Postcode Address File - Bird & Bird. https://www.twobirds.com/en/insights/2025/uk/addressing-database-rights-royal-mail-successfully-protects-rights-in-its-postcode-address-file  
[^37]: London - OpenStreetMap Wiki. https://wiki.openstreetmap.org/wiki/London  
[^38]: GLA Postcode Districts within Greater London (Map 1) - GLA (PDF). https://www.london.gov.uk/sites/default/files/gla_postcode_map_a3_map1.pdf

---

### Acknowledged information gaps

- Current, quantified completeness metrics per provider for SE1–SE18 are not published in the referenced sources.  
- Postcodes.io documentation confirms UK coverage but does not enumerate district‑level completeness for SE London.  
- Empirical sampling of OSM address/postal code completeness for SE London was not performed in this review and remains a known gap.  
- PAF pricing for non‑public‑sector, high‑volume usage is not fully enumerated publicly; only structures and eligibility signals are available.  
- The Code‑Point Open product page content could not be fully extracted here; details are corroborated via data.gov.uk and product context.  
- There are no free, public APIs that reliably return complete, authoritative street lists by postcode area; available APIs are either postcode‑centric (not street‑list APIs) or licensed address products.  
- OSM postal code features are inconsistent and should not be treated as authoritative without cross‑validation.