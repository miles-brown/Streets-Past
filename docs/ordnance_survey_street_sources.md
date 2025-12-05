# Ordnance Survey Open & Commercial Street Data for London: Complete SE (SE1–SE18) Street Extraction Playbook

## Executive Summary

This playbook provides a practical, authoritative route to compile street names for the SE postcode area districts of London (SE1–SE18). It explains what Ordnance Survey (OS) open and premium products can be used, how to access them (downloads and APIs), and how to combine datasets to generate SE-focused street lists with quality controls. It also clarifies licensing and costs, particularly for open products under the Open Government Licence (OGL) and premium offerings available via the OS Data Hub.

Three OS OpenData products are central to a robust, no-cost solution for street extraction across Great Britain, including London:

- OS Open Names provides authoritative names and numbers for roads, settlements, and postcodes, with quarterly updates and flexible formats (CSV, GML, GeoPackage). It includes over 870,000 named and numbered roads and is the most straightforward source of street names from open data[^3].
- OS Open UPRN provides Unique Property Reference Numbers (UPRNs), the persistent identifiers for addressable locations, enabling linkage of street information to addresses for validation and enrichment. It is updated every six weeks and is free to use under OGL[^6].
- Code-Point Open provides postcode unit locations (1.7 million postcodes), updated quarterly, and is designed for linking statistical or operational datasets to geographic locations[^1].

Commercially, AddressBase Core (and the broader AddressBase family) offers address records referenced by UPRN, USRN (Unique Street Reference Number), and TOID (Topographic Identifier), with weekly updates. AddressBase is essential when full address attribution, lifecycle detail, or comprehensive linking identifiers are required; however, it is not free unless your organisation is covered by the Public Sector Geospatial Agreement (PSGA)[^4][^9]. For programmatic queries, the OS Places API provides address lookup and postcode search at scale; pricing depends on your plan and is not detailed here[^8].

OS Open Roads provides a high-level view of the road network (motorways to country lanes) and is useful for network context and naming confirmation; however, it is simplified and not the authoritative source of street names[^7]. Legacy products such as Meridian 2 have been superseded or discontinued; OS Open Roads is the modern open network dataset[^7].

To extract street names specifically for SE1–SE18, the recommended approach is:

- Use OS Open Names to retrieve road features across Great Britain and filter to SE districts via postcode attributes or bounding geometries.
- Optionally, validate and enrich using Code-Point Open postcode points (filter to SE prefixes) and OS Open UPRN to link addresses for cross-checking.
- If needed, use the OS Places API to search by postcode and retrieve associated addresses and road references for verification.

Deliverables include a deduplicated, authoritative list of street names for SE1–SE18 with identifiers (UPRN/USRN where available), attributes (road number/name, locality), and metadata for reproducibility. The approach is scalable, leverages open data where possible, and provides a premium pathway for higher assurance where required.

Information gaps to be aware of include pricing specifics for premium datasets accessed via the OS Data Hub, dynamic content on the OS Data Hub Open Data Downloads pages that may require browsing, current operational status of certain legacy products like Meridian 2, granular boundaries for SE districts, and endpoint-specific parameters beyond what is summarised in OS Names and OS Places documentation[^1][^3][^6][^7][^8][^9].

## Scope and Definitions

The goal is a comprehensive list of street names for the SE London postcode districts (SE1–SE18) derived from authoritative OS sources. OS Open Names includes both named and numbered roads, settlements, and postcodes mapped to the British National Grid, making it the principal open dataset for street names. It offers coverage across Great Britain and is updated quarterly, with publication months in January, April, July, and October[^3]. OS Open Roads provides the connected road network but at a higher level and with simplified geometry; it is not intended as the authoritative source for street names[^7].

Key terms used throughout:

- Unique Property Reference Number (UPRN): a persistent identifier for every addressable location in Great Britain, allocated primarily by local authorities, and present across OS addressing products[^6][^9].
- Unique Street Reference Number (USRN): the persistent identifier for streets, used for linking street records across OS products; present in AddressBase Core[^4].
- Topographic Identifier (TOID): an identifier used in OS MasterMap products; included in AddressBase for cross-referencing[^4].
- AddressBase Core: an OS addressing product with over 33 million addresses, referenced by UPRN and USRN, updated weekly[^4].
- OS Open Names: OS OpenData product providing road names/numbers, settlements, and postcodes, updated quarterly[^3].
- OS Open UPRN: OS OpenData product with UPRNs (without full address detail), updated every six weeks[^6].
- Code-Point Open: OS OpenData product providing postcode unit locations (1.7 million postcodes), updated quarterly[^1].

Together, these products support different aspects of street data capture and validation. OS Open Names is the primary source of street names, Code-Point Open supports spatial filtering by postcode and validation against geographic distributions, OS Open UPRN provides identifiers for linking and cross-referencing, and AddressBase Core adds comprehensive address attribution and lifecycle detail when required.

## OS Data Access & Licensing Overview

Access to OS data is mediated through the OS Data Hub, where users sign up, create projects, and obtain API keys for programmatic access. For downloads, the OS Data Hub provides open data packages and premium products, depending on your plan[^10][^11]. Licensing is straightforward for open products and more complex for premium offerings.

OS OpenData products are made available under the Open Government Licence (OGL) v3.0, which permits free use, modification, and redistribution with attribution. The attribution statement should include “Contains OS data © Crown copyright and database right [Year]”[^12]. For premium products, OS offers plans through the OS Data Hub, and PSGA members can access certain address products (including AddressBase Core) at no cost; commercial licensing and partner channels are available for businesses[^4][^11]. OS Data Hub plan FAQs indicate that users may benefit from up to £1,000 of premium data each month, subject to terms; OS Places API usage and costs should be checked directly with OS[^11].

To illustrate access pathways and licensing, Table 1 summarises the relevant products and options. This sets expectations for what can be done with open data and when premium access is appropriate.

### Table 1: OS Access Pathways and Licensing

| Product/Service | Access Method | Licence | Cost Status | Update Frequency | Notes |
|---|---|---|---|---|---|
| OS Open Names | OS Data Hub download | OGL v3.0 | Free | Quarterly (Jan, Apr, Jul, Oct) | Primary open source of road names/numbers, settlements, postcodes[^3] |
| OS Open UPRN | OS Data Hub download | OGL v3.0 | Free | Every six weeks | UPRNs for ~40M addressable locations; identifiers for linking[^6] |
| Code-Point Open | OS Data Hub download | OGL v3.0 | Free | Quarterly (Feb, May, Aug, Nov) | Postcode unit locations for linking and spatial filters[^1] |
| OS Open Roads | OS Data Hub download | OGL v3.0 | Free | Twice a year (Apr, Nov) | High-level road network; simplified geometry; not authoritative for street names[^7] |
| AddressBase Core | OS Data Hub (PSGA/Premium), sample data, exploration licence | Premium (PSGA free for members) | Premium (PSGA free for eligible public sector) | Weekly | Addresses with UPRN/USRN/TOID; full lifecycle detail in premium tiers[^4][^9] |
| OS Places API | API via OS Data Hub | Premium plan (PSGA free for members) | Premium (PSGA free for members) | Frequently updated | Programmatic address lookup and postcode search; pricing not detailed here[^8][^11] |

The implication is clear: use OS Open Names as the core source for street names, augment with OS Open UPRN and Code-Point Open for identifiers and spatial filtering, and add AddressBase Core and OS Places API for comprehensive addressing and programmatic access when premium entitlements apply.

## Product Deep Dives: OpenData and Premium

### OS Open Names

OS Open Names is the authoritative open dataset for street names in Great Britain. It includes over 870,000 named and numbered roads, nearly 44,000 settlements, and over 1.6 million postcodes, all mapped to the British National Grid. It is updated quarterly, with publication months in January, April, July, and October. Formats include CSV, GML, and GeoPackage[^3]. From a workflow perspective, OS Open Names supplies the road name and number fields required for SE street extraction, with the settlement and postcode attributes supporting geographic filtering and validation.

### OS Open UPRN

OS Open UPRN provides UPRNs—the persistent identifiers for addressable locations across Great Britain—covering approximately 40 million locations. UPRNs are primarily allocated by local authorities and never reused, making them reliable keys for linking street and address information across datasets. OS Open UPRN is free under OGL and updated every six weeks, with formats including CSV and GeoPackage[^6]. While it does not include full address text, it enables robust linkage to addresses when premium products are available and supports cross-referencing across operational systems.

### Code-Point Open

Code-Point Open contains the locations of all current postcode units in Great Britain—around 1.7 million postcodes—and is updated quarterly. It is designed for linking datasets to geographic locations and includes administrative and health authority code attributes for analytical use. Formats include CSV and GeoPackage[^1]. In SE street extraction, Code-Point Open helps validate that a road appears in the expected SE districts and provides a spatial anchor point to confirm coverage.

### OS Open Roads

OS Open Roads offers a high-level view of the road network across Great Britain, from motorways to country lanes, with links representing an approximate central alignment of the carriageway. It includes roads classified by national or local highway authorities and is updated twice a year (April and November). It is available in ESRI Shapefile, GeoPackage, GML, and vector tiles[^7]. OS Open Roads is useful for network analysis, proximity queries, and context, but its simplified nature means it is not the definitive source for street names; OS Open Names remains preferable for naming.

### AddressBase Family (Core/Plus/Premium)

AddressBase products match Royal Mail postal addresses to UPRNs and provide property-level coordinates and classification. AddressBase Core includes over 33 million unique addresses, each referenced by UPRN and USRN (and TOID), and is updated weekly. It is available in CSV and GeoPackage, with ordering by area or tiles[^4]. AddressBase Plus and Premium add lifecycle information, multi-occupancy details, historical and pre-build addresses, and additional cross-references (e.g., OS MasterMap Topography Layer TOIDs)[^4]. Access routes include OS Data Hub for PSGA members and commercial licensing for businesses via OS partners. The GOV.UK guidance emphasises the UPRN standard and sets out weekly updates for the full dataset, with underlying data updated continuously[^9]. For the SE street use case, AddressBase is critical when address-level attribution or authoritative street identifiers are required.

### Meridian 2 (Legacy)

Meridian 2 was a mid-scale transportation product historically available via OS OpenData. The modern replacement for open roads network data is OS Open Roads[^7]. While Meridian 2 documentation may still exist in第三方 repositories, it should not be considered current; OS Open Roads is the appropriate open product for road network context.

To consolidate product attributes and use in street extraction, Table 2 provides a comparative matrix.

### Table 2: Comparative Matrix of OS Products for Street Extraction

| Product | Coverage | Update Frequency | Formats | Licence | Use in Street Extraction | API Availability |
|---|---|---|---|---|---|---|
| OS Open Names | Great Britain | Quarterly (Jan, Apr, Jul, Oct) | CSV, GML, GeoPackage | OGL v3.0 | Primary source of road names/numbers; settlements; postcodes | Not specified[^3] |
| OS Open UPRN | Great Britain | Every six weeks | CSV, GeoPackage | OGL v3.0 | Identifiers (UPRN) for linking addresses; validation | Not specified[^6] |
| Code-Point Open | Great Britain | Quarterly (Feb, May, Aug, Nov) | CSV, GeoPackage | OGL v3.0 | Spatial filter by postcode; validation against geographic distribution | Not specified[^1] |
| OS Open Roads | Great Britain | Twice a year (Apr, Nov) | Shapefile, GeoPackage, GML, vector tiles | OGL v3.0 | Network context; proximity analysis; confirm road existence | Not specified[^7] |
| AddressBase Core | Great Britain | Weekly | CSV, GeoPackage | Premium (PSGA free for members) | Full address attribution; USRN/TOID linking; authoritative street references | Not applicable (download/API via OS Places for addresses)[^4][^8][^9] |
| AddressBase Plus/Premium | Great Britain | Six-weekly to weekly (varies) | GML (Premium), others | Premium | Lifecycle, historical/pre-build, alternative addresses; extended identifiers | Not applicable (download/API via OS Places for addresses)[^4][^9] |
| Meridian 2 (Legacy) | Great Britain | Historical | Various | Legacy open/licence | Superseded by OS Open Roads | Not applicable[^7] |

## Access & APIs: Endpoints, Parameters, and Usage

The OS Data Hub is the gateway to downloads and APIs. Create an account, set up a project, and obtain an API key for programmatic services[^10][^11]. The OS Names API is a free service for searching populated places, road names, road numbers, and postcodes. The base endpoint is documented on the API Catalogue, with an overview available on the OS Data Hub[^14][^15]. The OS Places API provides address lookup and postcode search; its base endpoint is also listed on the API Catalogue, and documentation is available via the OS Data Hub[^8][^16].

Key Points:
- Base endpoint for OS Names API: api.os.uk/search/names/v1 (free)[^14][^15].
- Base endpoint for OS Places API: api.os.uk/search/places/v1 (premium/PSGA as applicable)[^8][^16].
- Documentation and overview: OS Names overview and OS Places overview are available through OS Data Hub docs[^15][^16].
- Terms and conditions apply to API usage and should be reviewed before production deployment[^11].

Table 3 summarises the API endpoints and typical query patterns relevant to postcode-to-street workflows. Parameter-level details vary by endpoint and should be confirmed in the technical specifications.

### Table 3: API Endpoint Summary

| API | Base Endpoint | Typical Query Pattern | Free/Paid | Typical Use | Documentation |
|---|---|---|---|---|---|
| OS Names API | api.os.uk/search/names/v1 | Search by road name/number or settlement; filter by type and bbox | Free | Discover and verify road names and postcodes | API Catalogue and OS Docs overview[^14][^15] |
| OS Places API | api.os.uk/search/places/v1 | Postcode lookup; address search; geosearch for nearest properties | Premium (PSGA free for members) | Retrieve addresses by postcode; verify street associations | API Catalogue and OS Docs overview[^8][^16] |

These APIs complement the download-based workflows: OS Names provides a lightweight way to discover or verify names, while OS Places enables postcode-to-address lookups and geosearch. Where premium data entitlements apply, programmatic access can substitute or augment downloads.

## SE London (SE1–SE18) Extraction Methodology

The SE postcode area spans districts SE1 through SE18 across parts of central, south, and southeast London. A practical method leverages OS Open Names as the primary source, with optional validation and enrichment from Code-Point Open and OS Open UPRN. If premium access is available, AddressBase Core and OS Places API can provide address-level verification and additional identifiers.

### Method A: OS Open Names Download

1. Register on the OS Data Hub and download OS Open Names in your preferred format (CSV, GeoPackage, or GML)[^3].
2. Parse the dataset to isolate records where the road feature type indicates streets and the associated postcode attributes fall within the SE1–SE18 districts. Use the postcode and settlement fields to identify SE coverage and apply bounding box filters if needed.
3. Extract the street names and road numbers, normalise the names (remove suffixes/prefixes consistently), and aggregate by street. Deduplicate variants that represent the same thoroughfare (e.g., “High Street” vs “High St”).
4. Validate against OS Open Roads for presence in the road network and, where appropriate, against Code-Point Open to confirm postcode distributions align with the extracted streets[^7][^1].

### Method B: Code-Point Open for Postcode Centroids

1. Register on the OS Data Hub and download Code-Point Open (CSV or GeoPackage)[^1].
2. Filter records by postcode prefix “SE1” through “SE18”.
3. Group the filtered postcodes by outward code (e.g., SE1, SE2, … SE18) and perform spatial join operations with OS Open Names to associate streets with the outward code clusters.
4. Generate the unique street list per SE district and review outliers (e.g., streets that appear outside expected borough boundaries or show anomalous distributions)[^1].

### Method C: OS Names API Discovery

1. Query the OS Names API using the base endpoint to search by road name or number across England, Scotland, and Wales[^14].
2. Filter results by local_type (e.g., road names and numbers) and use bounding boxes aligned to SE London to constrain the search to relevant districts.
3. Compile a street list from the API responses and deduplicate entries, standardising road type suffixes[^14][^15].

### Method D: OS Places API Postcode Lookup

1. If your plan allows, query the OS Places API by postcode to retrieve addresses and associated street references[^8][^16].
2. Group addresses by SE1–SE18 outward codes and extract unique street names.
3. Validate against OS Open Names for naming consistency and add identifiers (UPRN/USRN if available via AddressBase Core) to strengthen data integrity[^4][^8][^9].

Quality assurance should include:
- Deduplication of street names and normalisation of suffixes.
- Cross-validation against OS Open Roads to ensure the extracted streets exist in the contemporary network[^7].
- Checks against postcode distributions using Code-Point Open to confirm alignment with SE districts[^1].
- Optional verification using premium AddressBase Core identifiers (UPRN/USRN/TOID) when available[^4][^9].

To illustrate the choices, Table 4 compares the methods.

### Table 4: Method Comparison for SE Street Extraction

| Method | Steps | Inputs | Effort | Pros | Cons |
|---|---|---|---|---|---|
| A: OS Open Names download | Download, filter SE postcodes, extract and deduplicate streets | OS Open Names CSV/GeoPackage/GML | Moderate | Authoritative open street names; quarterly updates; no cost | Requires GIS/ETL; manual validation of outliers[^3] |
| B: Code-Point Open | Filter SE postcodes, spatial join to OS Open Names | Code-Point Open + OS Open Names | Higher | Confirms postcode-street alignment; supports district grouping | Additional processing; outliers require review[^1] |
| C: OS Names API | Query road names/numbers, bbox filter, compile list | OS Names API | Low–Moderate | Quick discovery; free service | Parameter details vary; may require pagination/testing[^14][^15] |
| D: OS Places API | Postcode lookup, group addresses, extract streets | OS Places API | Moderate | Address-level verification; supports geosearch | Premium unless PSGA; pricing not specified[^8][^11][^16] |

A consistent output schema ensures comparability and downstream usability. Table 5 proposes a schema for the SE street dataset.

### Table 5: Proposed Output Schema

| Field | Description | Source Product | Validation Rule | Mandatory |
|---|---|---|---|---|
| street_name | Canonical street name (e.g., “High Street”) | OS Open Names / OS Places | Must match name in OS Open Names; deduplicate variants | Yes |
| road_number | Numeric or letter road designation (e.g., “A2”) | OS Open Names | Must match OS Open Names; null if not applicable | No |
| district | SE outward code (SE1–SE18) | Code-Point Open / OS Open Names | Must be one of SE1–SE18 | Yes |
| locality | Settlement or locality name | OS Open Names | Cross-check against OS Open Names settlement fields | No |
| easting | British National Grid easting | Code-Point Open / OS Open Names | Must be within SE district bounding box | No |
| northing | British National Grid northing | Code-Point Open / OS Open Names | Must be within SE district bounding box | No |
| uprn | Unique Property Reference Number | OS Open UPRN / AddressBase Core | Must be a valid UPRN; persistent identifier | No |
| usrn | Unique Street Reference Number | AddressBase Core | Must be a valid USRN; available in premium products | No |
| toid | Topographic Identifier | AddressBase Core | Must be a valid TOID; cross-reference mapping | No |
| source_dataset | Product used to derive record | N/A | Must be one of: OS Open Names, Code-Point Open, OS Places, AddressBase Core | Yes |
| source_date | Dataset publication date | N/A | Must match the product’s documented schedule | Yes |

## Licensing, Attribution, and Compliance

OS OpenData products are licensed under OGL v3.0. Derived datasets can be published and shared under OGL, provided the attribution “Contains OS data © Crown copyright and database right [Year]” is included in all copies and derivative works[^12]. Public sector organisations covered by the PSGA can access certain addressing products free of charge (e.g., AddressBase Core) and should follow the UPRN standard for consistent address referencing across systems[^9].

Premium access is administered via the OS Data Hub. Plan-specific conditions, including any free allowances, should be verified in OS Data Hub FAQs; in particular, the OS Places API is excluded from the general “up to £1,000 free premium data per month” guidance and has separate terms[^11]. For businesses, OS licensed partners and commercial channels govern pricing and usage. Attribution and data sharing should follow OS terms and conditions and be documented for audit and reproducibility[^11][^12].

Table 6 summarises licensing and attribution requirements.

### Table 6: Licensing and Attribution Matrix

| Product/Service | Licence | Cost | Attribution Requirements | Redistribution Conditions |
|---|---|---|---|---|
| OS Open Names | OGL v3.0 | Free | “Contains OS data © Crown copyright and database right [Year]” | Allowed under OGL with attribution[^12] |
| OS Open UPRN | OGL v3.0 | Free | As above | Allowed under OGL with attribution[^12] |
| Code-Point Open | OGL v3.0 | Free | As above | Allowed under OGL with attribution[^12] |
| OS Open Roads | OGL v3.0 | Free | As above | Allowed under OGL with attribution[^12] |
| AddressBase Core (PSGA) | PSGA terms | Free for eligible public sector | PSGA attribution; follow OS terms | Governed by PSGA; publication terms apply[^9][^11] |
| AddressBase (commercial) | Premium terms | Paid | Commercial attribution; follow OS terms | Governed by licence; partner terms may apply[^4][^11] |
| OS Places API | Premium/PSGA | Premium (PSGA free for members) | Follow OS terms | Governed by OS Data Hub terms[^8][^11][^16] |

## Free vs Paid: Which to Choose and When

For street name extraction in SE London, OS Open Names is the default choice because it is free, authoritative, and updated quarterly. It supplies the road names and numbers needed to compile the SE street list with minimal friction[^3]. OS Open UPRN and Code-Point Open add value by enabling linkage, validation, and spatial filtering without cost[^6][^1]. OS Open Roads complements the process by confirming that streets exist in the contemporary road network, though it is simplified and not the definitive source of names[^7].

Premium products are justified when:
- Full address attribution is required (e.g., property-level detail, lifecycle status).
- USRN and TOID are needed for cross-referencing across authoritative datasets.
- Programmatic address search and postcode lookup at scale is essential to the solution (OS Places API).
- Data must be tied to weekly updates and integrated into enterprise systems where identifiers like UPRN/USRN are mandatory.

Table 7 provides a concise decision matrix.

### Table 7: Decision Matrix for SE Street Extraction

| Use Case | Recommended Dataset/Service | Reason | Cost Implication |
|---|---|---|---|
| Compile SE street names quickly and at no cost | OS Open Names | Authoritative open dataset for road names/numbers; quarterly updates | Free (OGL)[^3] |
| Validate street presence and distribution | OS Open Roads + Code-Point Open | Confirms network presence and aligns streets to SE postcodes | Free (OGL)[^7][^1] |
| Link streets to addresses for QA | OS Open UPRN | Adds UPRNs for persistent identifier linkage | Free (OGL)[^6] |
| Full address attribution and identifiers | AddressBase Core | Weekly updates; UPRN/USRN/TOID; enterprise-ready | Free for PSGA; paid otherwise[^4][^9] |
| Programmatic postcode-to-address lookup | OS Places API | Scalable address lookup and geosearch | Premium (PSGA free for members)[^8][^11][^16] |

## Implementation Checklist and Next Steps

A disciplined implementation will reduce risk and accelerate delivery. The checklist below organises actions from setup to QA and delivery.

### Table 8: Implementation Checklist

| Step | Action | Owner | Inputs | Outputs |
|---|---|---|---|---|
| 1 | Create OS Data Hub account and project; obtain API key | Data engineer | OS Data Hub access | Project configured; API credentials[^10][^11] |
| 2 | Download OS Open Names and Code-Point Open | Data engineer | OS Data Hub downloads | OS Open Names files; Code-Point Open files[^3][^1] |
| 3 | Build SE filters (postcode prefixes SE1–SE18; bbox) | Data engineer | SE district definitions; Code-Point Open | Filter criteria; bounding boxes[^1] |
| 4 | Extract and normalise street names | Data analyst | OS Open Names | Deduplicated street list per SE district[^3] |
| 5 | Validate with OS Open Roads and Code-Point Open | GIS analyst | OS Open Roads; Code-Point Open | QA report; outliers flagged[^7][^1] |
| 6 | Optionally add UPRNs and address links | Data engineer | OS Open UPRN; AddressBase Core (if PSGA/commercial) | Linked identifiers (UPRN/USRN/TOID)[^6][^4][^9] |
| 7 | If using APIs, document endpoints and usage patterns | Data engineer | OS Names API; OS Places API | API call logs; usage notes[^14][^8][^15][^16] |
| 8 | Apply attribution and compliance | Project manager | OGL attribution text | Attribution included in outputs; licence notes[^12][^11] |
| 9 | QA and sign-off | Project manager | Full dataset; QA reports | Approved SE street list; metadata and reproducibility notes |

## Appendices

### Appendix A: Key OS Docs and API Catalogue Links

The following list consolidates official documentation and catalogues for quick reference. URLs are provided in the References section.

- OS Data Hub (account and project setup)[^10]
- OS Data Hub plans and FAQs (including premium allowances and API terms)[^11]
- Code-Point Open product page and technical documentation[^1][^13]
- OS Open Names product page and technical documentation[^3][^17]
- OS Open UPRN product page and technical documentation[^5][^18]
- OS Open Roads product page and technical documentation[^7][^19]
- AddressBase and AddressBase Core product pages and technical documentation[^2][^4][^20]
- OS Places API (product page, API Catalogue entry, OS Docs overview)[^8][^16][^21]
- OS Names API (API Catalogue entry and OS Docs overview)[^14][^15]
- GOV.UK guidance on accessing free address data via AddressBase and PSGA[^9]

### Appendix B: Sample API Request Patterns

These examples illustrate typical query structures. Endpoint paths are provided; base hostnames and full URLs are in the References.

- OS Names API: search for road names/numbers within an SE bounding box.
  - Path: /search/names/v1/find
  - Typical parameters: query (road name/number), bbox (SE bounding box), local_type (road)
  - Purpose: discover and verify street names for SE districts[^14][^15]
- OS Places API: postcode lookup for SE districts.
  - Path: /search/places/v1/postcode
  - Typical parameters: postcode (e.g., “SE1 2AA”)
  - Purpose: retrieve addresses and street references grouped by outward code[^8][^16][^21]

Parameter names and payloads should be verified against the OS Docs technical specifications for each API.

### Appendix C: Reproducibility Notes

- Record source dataset names, publication months, and versions for every input (e.g., OS Open Names: Jan/Apr/Jul/Oct; Code-Point Open: Feb/May/Aug/Nov; OS Open Roads: Apr/Nov; AddressBase Core: weekly).
- Store bounding boxes used for SE filtering and any postcode prefix lists (SE1–SE18).
- Preserve attribution statements in outputs and documentation.
- If premium data is used, record plan identifiers, entitlements (e.g., PSGA membership), and any usage constraints as per OS Data Hub terms[^11][^12].

### Appendix D: Known Limitations and Data Quality Considerations

- OS Open Roads is a simplified, high-level network and should not be used as the primary source for street names. Use OS Open Names for authoritative naming and OS Open Roads for context and validation[^7].
- Meridian 2 is legacy; OS Open Roads supersedes it for open road network data[^7].
- Dynamic content on OS Data Hub Open Data Downloads pages may require browsing to view current package details and file listings[^10].
- Pricing for AddressBase and OS Places API varies by plan and is not detailed in the sources; confirm with OS directly[^11].
- API-specific query parameters and example payloads should be validated against OS Docs technical pages prior to production use[^15][^21].
- Granular geographic boundaries for SE districts require external GIS layers (e.g., postcode district boundaries) not included in the datasets discussed.

## References

[^1]: Code-Point Open | Data Products | OS - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/code-point-open

[^2]: AddressBase | Data Products | OS - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/addressbase

[^3]: OS Open Names | Data Products - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-open-names

[^4]: AddressBase Core | Data Products | OS - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/addressbase-core

[^5]: OS Open UPRN | Data Products - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-open-uprn

[^6]: OS Open UPRN technical documentation - OS Docs. https://docs.os.uk/os-downloads/identifiers/os-open-uprn

[^7]: OS Open Roads | Data Products - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-open-roads

[^8]: OS Places API | Data Products - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-places-api

[^9]: Access free address data using AddressBase - GOV.UK. https://www.gov.uk/guidance/access-free-address-data-using-addressbase

[^10]: OS Data Hub - Ordnance Survey. https://osdatahub.os.uk/

[^11]: Plans | FAQs | Support - OS Data Hub. https://osdatahub.os.uk/support/faqs/plans

[^12]: Open Government Licence v3.0 - The National Archives. https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/

[^13]: Code-Point Open technical documentation - OS Docs. https://docs.os.uk/os-downloads/addressing-and-location/code-point-open

[^14]: OS Names API - API Catalogue. https://www.api.gov.uk/os/os-names-api/

[^15]: OS Names API overview - OS Docs. https://osdatahub.os.uk/docs/names/overview

[^16]: OS Places API - API Catalogue. https://www.api.gov.uk/os/os-places-api/

[^17]: OS Open Names technical documentation - OS Docs. https://docs.os.uk/os-downloads/addressing-and-location/os-open-names

[^18]: Download OS Open UPRN - OS Data Hub. https://osdatahub.os.uk/downloads/open/OpenUPRN

[^19]: Download OS Open Roads - OS Data Hub. https://osdatahub.os.uk/downloads/open/OpenRoads

[^20]: AddressBase products' documentation - OS Docs. https://docs.os.uk/os-downloads/addressing-and-location/addressbase

[^21]: OS Places API overview - OS Docs. https://osdatahub.os.uk/docs/places/overview