# UK Government Open Data Street Sources for London SE Postcodes (SE1–SE18): Access, Datasets, and Download Methods

## Executive Summary

This guide sets out the authoritative, government-backed routes to assemble comprehensive street and address lists for the London SE postcode districts (SE1, SE2, SE3, SE4, SE5, SE7, SE8, SE9, SE11, SE12, SE13, SE14, SE15, SE16, SE17, SE18). It explains what to use, how to access it, how to filter by SE districts, and how to keep the data current.

Three strands of official data work together. First, Office for National Statistics (ONS) postcode products—particularly the ONS Postcode Directory (ONSPD) and the National Statistics Postcode Lookup (NSPL)—provide UK-wide postcode-to-geography linkages and centroids; these products are open and updated quarterly, and are the most practical starting point for postcode-led workflows and for filtering to SE districts.[^1][^3][^5][^6][^20][^21][^24] Second, Government Digital Service (GDS) guidance points public sector organisations to AddressBase products as the authoritative address and street dataset for Great Britain. Access is free for public sector bodies covered by the Public Sector Geospatial Agreement (PSGA), with AddressBase Core updated weekly and the broader family of products (Core, Plus, Premium, Islands) providing different levels of content and formats.[^9][^10][^12][^13][^14][^15][^16][^17][^27][^28] Third, open complementary datasets—OS Open Names for road names and place elements, and OS Open Greenspace for context—support enrichment and validation. These are available via the OS Data Hub under open licences and are updated regularly.[^25][^26][^29][^31][^30]

Two broad acquisition strategies work in practice. For a postcode-led approach, download the national ONSPD/NSPL CSV, load into a database, and filter by Postcode district (the outward code, e.g., “SE1”, “SE11”). Output streets by joining ONSPD/NSPL to authoritative street data via the Unique Street Reference Number (USRN) where available, or by deriving distinct thoroughfare names from address-level sources (see below). For an address-led approach, PSGA members can access AddressBase Core (and, where licensed, Plus/Premium) to retrieve addresses and street references by postcode, then derive a clean street list by grouping on USRN and street attributes. Non-PSGA users can validate outputs using the public FindMyStreet map for streets data and FindMyAddress for addresses and UPRNs (the latter limited to 10 free daily searches and for personal use).[^9][^18][^19]

Table 1 summarises the core sources, what they contain, access routes, licence, and update cadence.

Table 1. Summary matrix of core datasets for SE streets and addresses

| Dataset | Coverage | Granularity | Access method | Licence | Update frequency | Typical use |
|---|---|---|---|---|---|---|
| ONS Postcode Directory (ONSPD) | UK | Postcodes, centroids, geography linkages | Direct download (CSV/TXT/ZIP multi-CSV) | OGL/ONS terms | Quarterly | Postcode-to-area linkages; filtering by SE district; base reference[^3][^5][^6][^20] |
| National Statistics Postcode Lookup (NSPL) | UK | Postcodes, best-fit linkages, centroids | Direct download (CSV/TXT); interactive lookup | OGL/ONS terms | Quarterly | Alternative methodology to ONSPD; centroids; quick checks[^1][^4][^24] |
| AddressBase Core | Great Britain | Addresses, UPRN, coordinates | OS Data Hub for PSGA members; bulk weekly releases | PSGA terms | Weekly (full dataset publication) | Authoritative addresses; USRN linkage for streets[^9][^10][^13][^27] |
| AddressBase Plus | Great Britain | As Core + LA confirmations, multi-occupancy, TOIDs | OS Data Hub (PSGA) | PSGA terms | Six-weekly cadence (per product family) | Enhanced address detail and topographic links[^9][^14] |
| AddressBase Premium | Great Britain | Full GML with historic/alternative addresses, TOIDs | OS Data Hub (PSGA) | PSGA terms | Six-weekly cadence (per product family) | Deep address history and topology links[^9][^15] |
| AddressBase Islands | NI/IoM/Channel Islands | Addresses for Islands | OS Data Hub (PSGA) | PSGA terms | Product-specific | Coverage extension beyond GB[^9][^16] |
| OS Open Names | Great Britain | Road names, place names, postcode locations | OS Data Hub open downloads | Open (OS OpenData) | Quarterly | Lightweight street name and place enrichment[^25][^26] |
| OS Open Greenspace | Great Britain (open) | Greenspace extents | Data.gov.uk and OS Data Hub | Open (OS OpenData) | Periodic | Context and validation layers[^29][^30] |

In short: use ONSPD/NSPL as your postcode backbone and to filter to SE districts; use AddressBase (PSGA) for authoritative streets and addresses; use OS Open Names and related open products to enrich and validate; and use GDS’s public tools for spot checks. The ONS Open Geography Portal also provides a convenient postcode lookup and CSV export for quick analyses.[^7][^8][^23]

## Scope, Definitions, and Methodology

This report focuses on the SE postcode districts of interest—SE1, SE2, SE3, SE4, SE5, SE7, SE8, SE9, SE11, SE12, SE13, SE14, SE15, SE16, SE17, SE18—and the practical steps to assemble authoritative street and address lists for these areas. The scope is Great Britain (GB) for addressing and street data, with UK-wide coverage for ONS postcode products.

We distinguish between three conceptual layers:

- Postcodes. These are identifiers for postal delivery routes, not administrative geographies. ONS maintains two national products: ONSPD and NSPL. Both provide linkages to statistical and administrative geographies and are updated quarterly. ONSPD uses a point-in-polygon methodology; NSPL uses a best-fit approach to allocate statistics to higher geographies.[^1][^21]
- Streets. Streets are modelled with a Unique Street Reference Number (USRN), the government standard identifier for streets. Streets data is maintained by Local Highway Authorities and distributed via GeoPlace and Ordnance Survey products (AddressBase family) under the PSGA.[^22]
- Addresses. Addresses are modelled with a Unique Property Reference Number (UPRN), the government standard identifier for addressable locations. AddressBase products provide authoritative address data, including coordinates and, depending on product, links to other identifiers and topographic features.[^9][^22]

Methodologically, there are two main acquisition routes:

- Postcode-led. Use ONSPD or NSPL to filter to the SE outward codes, then attach address/street identifiers and derive street lists by grouping on USRN or by extracting distinct thoroughfare names from address-level data.
- Address-led. For PSGA members, query or download AddressBase by postcode, then derive streets by grouping addresses on USRN and street attributes. For non-PSGA users, validate addresses via FindMyAddress and streets via FindMyStreet, noting the former’s daily search limit and personal-use restrictions.[^9][^18][^19]

To align analyses across datasets, use the government’s open standards for UPRN and USRN to ensure consistent joins and to interoperate with other government data holdings.[^22]

Table 2 maps key identifiers and standards to their purpose and where they appear.

Table 2. Identifier and standard mapping

| Identifier/Standard | Purpose | Primary dataset(s) | Where it appears |
|---|---|---|---|
| UPRN (Unique Property Reference Number) | Stable identifier for every addressable location in GB | AddressBase family (Core/Plus/Premium) | Address records; cross-government linking field[^9][^22] |
| USRN (Unique Street Reference Number) | Stable identifier for every street record in GB | AddressBase family; NSG/Highway Authority data | Street records; links to addresses and maintenance responsibility[^22] |
| ONSPD | Postcode-to-geography linkages and centroids | ONS Postcode Directory | Postcode records; linkage fields to OAs/LSOAs/MSOAs/LADs[^1][^5][^20] |
| NSPL | Best-fit postcode-to-geography lookups and centroids | National Statistics Postcode Lookup | Postcode records; best-fit area allocations[^1][^4][^24] |

## Authoritative UK Street and Address Ecosystem: Roles and Relationships

The ONS Open Geography Portal is the definitive source for geographic products and postcode datasets. It disseminates ONSPD and NSPL, as well as boundary and lookup products, under open licensing, with a consistent release schedule and user guides. The portal also provides interactive tools such as the ONS Postcode Directory Look-up Tool and Tabular/Spatial Extract Tool for ad hoc analysis and CSV export.[^2][^7][^8]

Ordnance Survey (OS), through the OS Data Hub, provides the AddressBase family of addressing products. AddressBase is the authoritative address and street dataset for Great Britain, created from local authority data and published under the PSGA. Public sector bodies can access AddressBase free of charge under the PSGA, with a weekly publication of the full dataset and product-specific updates thereafter.[^9][^10][^12][^27]

GeoPlace distributes streets and address data in collaboration with local authorities and OS, and provides public-facing tools—FindMyAddress and FindMyStreet—for searching official addresses (with UPRN) and streets (with USRN), respectively. While these are not bulk-download mechanisms, they are invaluable for validation and spot checks.[^18][^19]

GDS sets the standards—UPRN for properties and USRN for streets—and provides guidance that underpins consistent linking of address and street data across government datasets.[^22]

Table 3 summarises the ecosystem roles.

Table 3. Ecosystem role map

| Organisation | Dataset/Tool | Role | Access | Licence |
|---|---|---|---|---|
| ONS | ONSPD, NSPL, boundaries, lookups, interactive tools | National statistical geography; postcodes; centroids | Open downloads via Open Geography Portal | OGL and ONS terms[^2][^7][^8][^20][^24] |
| Ordnance Survey | AddressBase (Core/Plus/Premium/Islands), OS Open Names, OS Open Greenspace | Authoritative addressing and open geospatial datasets | OS Data Hub (PSGA for AddressBase; open downloads for OS OpenData) | PSGA; OS OpenData terms[^9][^10][^12][^13][^14][^15][^16][^25][^26][^29][^30] |
| GeoPlace | FindMyAddress, FindMyStreet | Public search tools for addresses (UPRN) and streets (USRN) | Public web tools | Public-use terms; tool-specific constraints[^18][^19] |
| GDS | UPRN/USRN standards guidance | Standards and interoperability | Guidance on GOV.UK | Open guidance[^22] |

## ONS Postcode Products (ONSPD and NSPL): Access and SE Filtering

ONS produces two key postcode products. The ONS Postcode Directory (ONSPD) links current and terminated UK postcodes to administrative, health, and statistical geographies using a point-in-polygon methodology; postcodes that straddle boundaries are assigned to the area containing the mean grid reference of all addresses in that postcode. The National Statistics Postcode Lookup (NSPL) provides postcode-to-area linkages using a best-fit approach primarily designed for the allocation of statistical data. Both datasets include 1-metre resolution grid references and are updated quarterly (February, May, August, November).[^1][^21]

Access is available from the ONS Open Geography Portal as CSV and TXT (and multi-CSV ZIPs). The portal includes interactive tools that allow postcode search and CSV export for quick looks and checks. For programmatic needs, the portal exposes catalog feeds and APIs for metadata discovery (e.g., DCAT, OGC Records), rather than for direct filtering of the postcode files themselves.[^2][^5][^6][^7][^8][^20][^24]

SE filtering is straightforward once the national file is loaded into a database or analytics tool: filter records by the Postcode district (outward code) such as “SE1”, “SE2”, through “SE18”. When constructing a street list, join ONSPD/NSPL to AddressBase by postcode to bring in USRN (for streets) and UPRN (for addresses), then derive the distinct street set. ONS also publishes “postcode to OA/LSOA/MSOA/LAD” lookups that can be used to validate administrative geographies relevant to the SE area and to support area-based aggregation or confirmation.[^11]

Table 4 compares ONSPD and NSPL features.

Table 4. ONSPD vs NSPL feature comparison

| Feature | ONSPD | NSPL |
|---|---|---|
| Coverage | UK | UK |
| Linkage methodology | Point-in-polygon | Best-fit for statistical allocation |
| Grid reference resolution | 1-metre | 1-metre (centroids provided) |
| Formats | CSV, TXT, multi-CSV ZIP | CSV, TXT |
| Update frequency | Quarterly | Quarterly |
| Primary use cases | Geography joins; analysis; filtering by district | Best-fit area allocation; validation; quick lookups |
| Interactive tools | Postcode lookup; extract tools | Postcode lookup; extract tools |

### Direct Download and Data Formats

ONS distributes ONSPD and NSPL via the Open Geography Portal. Files are provided as CSV and TXT; for ONSPD, multi-CSV ZIPs are also available. Recent releases include February 2025 and May 2025, among others. The OGL context and ONS guidance apply to reuse.[^5][^6][^20][^24]

### Interactive Lookups and Extracts

The ONS Postcode Directory Look-up Tool allows postcode search on a map and export of the resulting postcode record to CSV. The Tabular/Spatial Extract Tool can generate targeted extracts. These tools are useful for ad hoc validation and spot checks rather than bulk SE extraction; for bulk work, download the national file and filter offline.[^7][^8]

### Filtering to London SE Districts

To isolate SE districts, filter ONSPD/NSPL by the outward code—SE1, SE2, SE3, SE4, SE5, SE7, SE8, SE9, SE11, SE12, SE13, SE14, SE15, SE16, SE17, SE18. If you plan to derive streets, join the filtered set to AddressBase (USRN for streets; UPRN for addresses), then group by USRN and street attributes to produce a clean SE street list. Use ONS lookups (OA/LSOA/MSOA/LAD) to validate that your extracted records fall within expected London geographies for quality assurance.[^5][^11]

## Government Digital Service (GDS) and AddressBase: Authoritative Address and Street Data

GDS guidance explains how public sector organisations can access AddressBase products free of charge under the PSGA. AddressBase Core is the source of truth for addresses in Great Britain, with Ordnance Survey publishing a new version of the whole dataset weekly. The family includes AddressBase Plus and AddressBase Premium (with richer attributes and GML), and AddressBase Islands for Northern Ireland and the Crown Dependencies.[^9][^10][^13][^14][^15][^16]

The practical distinction for most teams is:

- AddressBase Core (bulk weekly). Authoritative addresses with UPRN and coordinates; excludes properties not yet built or demolished. Suitable for extracting addresses by postcode and for joining to USRN to derive streets.[^13]
- AddressBase Plus. Adds multi-occupancy handling, local authority confirmations, and OS MasterMap Topographic Identifier (TOID) references.[^14]
- AddressBase Premium. Offers a comprehensive GML data model, including historic/alternative addresses and additional topographic and transport identifiers; appropriate where richer history or topology is required.[^15]
- OS Places API. A PSGA-covered API that supports postcode search and other geospatial operations; useful for dynamic queries and integrations.[^17]

Table 5 compares AddressBase product capabilities at a glance.

Table 5. AddressBase products comparison

| Product | Coverage | Core fields | Format | Update frequency | Access |
|---|---|---|---|---|---|
| Core | Great Britain | UPRN, address text, coordinates | CSV (product-specific formats) | Weekly publication of full dataset | PSGA via OS Data Hub[^9][^13] |
| Plus | Great Britain | As Core + LA confirmations, multi-occupancy, TOIDs | CSV (product-specific) | Product-specific cadence | PSGA via OS Data Hub[^9][^14] |
| Premium | Great Britain | Full GML with historic/alternative addresses, TOIDs | GML | Product-specific cadence | PSGA via OS Data Hub[^9][^15] |
| Islands | NI/IoM/Channel Islands | Addresses for Islands | Product-specific | Product-specific | PSGA via OS Data Hub[^9][^16] |
| OS Places API | Great Britain | Postcode and address search, geospatial ops | API | Ongoing | PSGA (API access)[^17] |

### PSGA Access and Eligibility

Public sector access is free at point of use for organisations covered by the PSGA. Teams should verify eligibility and register through the OS Data Hub, which provides access channels and documentation. The PSGA also covers use of the OS Places API for address and postcode queries.[^9][^27][^28]

### Deriving Street Lists from AddressBase

To derive streets for SE districts using AddressBase, query or download address records where the postcode outward code matches the SE districts of interest. Join to the streets component via the USRN, then group by USRN and street attributes (e.g., street name, locality, town) to produce a distinct street list. Validate using ONS products for completeness and geographic coherence, and use public tools such as FindMyStreet to spot-check USRN-linked street facts and maintenance responsibility where needed.[^9][^18][^22]

## Complementary Open Datasets for Street Names and Local Context

OS Open Names is a free, quarterly-updated dataset containing place names, road numbers, and postcodes for Great Britain. It is available in CSV, GML, and GeoPackage formats and is useful for enriching address or street lists with standardized road names and locate-by-name features. OS Open Greenspace provides open greenspace geometry useful for context and validation checks. Both are available from the OS Data Hub under open terms.[^25][^26][^29][^30][^31]

Table 6 provides a snapshot.

Table 6. Complementary open datasets snapshot

| Dataset | Content | Format(s) | Update frequency | Download | Licence |
|---|---|---|---|---|---|
| OS Open Names | Road names, place names, road numbers, postcodes | CSV, GML, GeoPackage | Quarterly | OS Data Hub (Open) | Open (OS OpenData)[^25][^26] |
| OS Open Greenspace | Greenspace extents (parks, pitches, etc.) | Product-specific | Periodic | Data.gov.uk; OS Data Hub | Open (OS OpenData)[^29][^30] |

Use these open datasets to cross-check naming consistency, add locality context, and ensure your derived SE street list is broadly consistent with the national mapping baseline.

## How to Assemble a Complete Street List for SE1–SE18

Teams can choose between two main approaches, with hybrid variations depending on licensing and system constraints.

Table 7 summarises the workflow options.

Table 7. Workflow options matrix

| Approach | Steps | Tools | Outputs | Pros | Cons |
|---|---|---|---|---|---|
| A. Postcode-led (ONSPD/NSPL + AddressBase) | 1) Download ONSPD/NSPL (CSV/TXT/ZIP); 2) Filter to SE outward codes; 3) Join to AddressBase by postcode to bring in USRN; 4) Group by USRN and street attributes; 5) QA against ONS lookups and open datasets | ONS portal; OS Data Hub (PSGA) | SE street list (unique streets), optionally with UPRNs | Simple filtering; consistent geography; authoritative addresses | Requires PSGA for AddressBase; bulk handling of national files[^5][^11][^9] |
| B. Address-led (PSGA AddressBase) | 1) Query/download AddressBase (Core/Plus/Premium) by SE postcodes; 2) Group address records by USRN and street fields; 3) Export unique streets; 4) Validate with FindMyStreet and ONS | OS Data Hub (PSGA); FindMyStreet; ONS tools | SE street list tied to UPRN/USRN | Authoritative, granular; integrated addresses and streets | Requires PSGA; data model understanding[^9][^18][^22] |
| Non-PSGA validation path | 1) Derive candidate street list via A or B with available access; 2) Spot-check via FindMyStreet and FindMyAddress (10 searches/day; personal use) | FindMyStreet; FindMyAddress | Validated subset, not bulk | Zero-cost verification | Strict limits; not a bulk source[^18][^19] |

### Approach A: Postcode-led (ONSPD/NSPL + AddressBase)

- Download ONSPD or NSPL and filter by the SE outward codes listed above.[^5][^24]
- Join to AddressBase by postcode to obtain USRN for streets and UPRN for addresses.[^9]
- Derive unique streets by grouping on USRN and street descriptors.
- Validate using ONS lookups (postcode-to-OA/LSOA/MSOA/LAD) and visual checks in ONS tools; enrich with OS Open Names as needed.[^11][^7][^8][^25]

### Approach B: Address-led (PSGA AddressBase access)

- Query or download AddressBase Core/Plus/Premium for SE postcodes.[^9][^13][^14][^15]
- Group by USRN and street attributes to compile a unique street list.
- Cross-verify with FindMyStreet and ONS postcode products for completeness and naming consistency.[^18][^22]

### Non-PSGA Validation Path (Public Tools)

- Use FindMyStreet to verify streets, highway authority, and USRN-linked details.[^18]
- Use FindMyAddress to confirm addresses and UPRNs, noting the 10 free daily searches limit and personal-use restriction.[^19]
- Treat these as validation aids, not bulk sources.

## Access Methods and Step-by-Step Downloads

This section consolidates concrete download and access routes, formats, authentication requirements, and update cadence. Where relevant, examples refer to SE filtering.

Table 8 provides a quick-reference view of access methods.

Table 8. Access method quick reference

| Dataset | Direct URL reference | Portal | Format(s) | Authentication | Update cadence | Example SE filtering step |
|---|---|---|---|---|---|---|
| ONSPD | See Ref [5], [6], [20] | ONS Open Geography Portal | CSV, TXT, ZIP (multi-CSV) | None for downloads | Quarterly | Download CSV/TXT; filter WHERE Postcode district LIKE ‘SE%’ |
| NSPL | See Ref [4], [24] | ONS Open Geography Portal | CSV, TXT | None for downloads | Quarterly | As above |
| AddressBase Core | See Ref [13] | OS Data Hub (PSGA) | Product-specific | PSGA login required | Weekly (full publication) | Query by SE postcodes; derive streets via USRN |
| AddressBase Plus | See Ref [14] | OS Data Hub (PSGA) | Product-specific | PSGA | Product-specific | As above |
| AddressBase Premium | See Ref [15] | OS Data Hub (PSGA) | GML | PSGA | Product-specific | As above |
| AddressBase Islands | See Ref [16] | OS Data Hub (PSGA) | Product-specific | PSGA | Product-specific | As above |
| OS Places API | See Ref [17] | OS Data Hub | API | PSGA | Ongoing | Postcode search endpoints |
| OS Open Names | See Ref [26] | OS Data Hub (Open) | CSV, GML, GeoPackage | None | Quarterly | Download GB; filter to SE via bounding box or joins |
| OS Open Greenspace | See Ref [29], [30] | Data.gov.uk; OS Data Hub | Product-specific | None | Periodic | Use for context checks in SE area |
| ONS interactive tools | See Ref [7], [8] | ONS | CSV (export) | None | Rolling | Postcode search and export; not for bulk SE extraction |

### ONS ONSPD/NSPL

- Download the latest ONSPD/NSPL from the ONS Open Geography Portal. Files are provided in CSV and TXT; ONSPD also offers multi-CSV ZIPs. Updates are quarterly.[^1][^5][^6][^20][^24]
- For quick checks, use the ONS Postcode Directory Look-up Tool and the Tabular/Spatial Extract Tool. These return CSV exports suitable for spot verification.[^7][^8]
- Programmatic discovery is supported via catalog/record APIs; however, bulk filtering is performed locally after download.[^2]

### AddressBase via OS Data Hub (PSGA)

- Confirm PSGA eligibility and register as required.[^27][^28]
- Access AddressBase Core (and, where licensed, Plus and Premium) through the OS Data Hub. The full AddressBase dataset is published weekly, with product-specific cadence thereafter.[^9][^10][^12][^13][^14][^15]
- Derive SE streets by querying by postcode outward code (“SE1”–“SE18”) and grouping on USRN.

### Open Complementary Datasets

- Download OS Open Names (CSV/GML/GeoPackage) via the OS Data Hub; updates are quarterly.[^25][^26]
- Access OS Open Greenspace via Data.gov.uk and OS Data Hub for contextual validation.[^29][^30][^31]

### Public Tools for Verification

- Use FindMyStreet to verify street existence, USRN, and maintenance responsibility; useful for sanity checks and issue discovery.[^18]
- Use FindMyAddress to verify addresses and UPRNs, subject to a 10-search-per-day limit and personal-use constraints.[^19]

## Licensing, Attribution, and Compliance

Most ONS geographic products are available under the Open Government Licence (OGL), with ONS-specific terms and attribution requirements. Always consult the product pages for precise licence wording and attribution demands.[^2][^5][^20]

For addressing data, PSGA membership governs use. AddressBase is free at point of use for public sector bodies covered by the PSGA; specific redistribution and derivative use conditions apply, including attribution to Ordnance Survey and, where relevant, to local authorities and GeoPlace. GDS guidance also describes permitted uses such as sharing data with emergency responders and publishing derived datasets under appropriate terms.[^9][^27][^28]

OS OpenData products (e.g., OS Open Names, OS Open Greenspace) are supplied under open terms via the OS Data Hub. Ensure you follow OS OpenData licence conditions and attribution requirements when reusing or redistributing these datasets.[^25][^29][^31]

Table 9 summarises licensing and attribution at a glance.

Table 9. Licence and attribution summary

| Dataset | Licence | Attribution text (indicative) | Redistribution notes |
|---|---|---|---|
| ONSPD/NSPL | OGL (ONS terms apply) | Contains public sector information licensed under the Open Government Licence v3.0; © ONS and third-party rights | Follow OGL attribution; check product page for ONS terms[^2][^5][^20] |
| AddressBase Core/Plus/Premium/Islands | PSGA | © Ordnance Survey and/or local authority/GeoPlace (as applicable) | PSGA governs use; redistribution subject to PSGA terms[^9][^27][^28] |
| OS Open Names | OS OpenData | © Ordnance Survey and database rights | Open reuse under OS OpenData terms; attribution required[^25][^31] |
| OS Open Greenspace | OS OpenData | © Ordnance Survey and database rights | Open reuse under OS OpenData terms; attribution required[^29][^30][^31] |

Note: Always verify the exact licence and attribution wording on the product pages before publication or redistribution.

## Update Strategy and Data Quality

ONS releases ONSPD and NSPL quarterly (February, May, August, November). Plan refresh cycles in line with these releases and validate that SE district coverage remains stable across cycles. Monitor ONS announcements for methodological changes that could affect linkage best-fits or boundary handling.[^1][^2][^5][^24]

AddressBase is updated on a six-week cycle across the product family, with AddressBase Core having a weekly publication of the full dataset. Incorporate weekly or six-weekly refreshes depending on the products used, and track epoch/version notes in OS documentation.[^9][^10][^12][^13][^14][^15]

Data quality controls are essential. Maintain crosswalk tables that link UPRN and USRN consistently across releases. Reconcile street name variants using OS Open Names and perform ad hoc verification via FindMyStreet and ONS interactive tools. Use ONS lookups (postcode to OA/LSOA/MSOA/LAD) to detect anomalous records or boundary-edge effects during each refresh.[^7][^8][^11][^18][^22][^25]

Table 10 proposes a pragmatic refresh plan.

Table 10. Release cycle and refresh plan

| Dataset | Provider | Cadence | Next expected refresh window | QA checklist |
|---|---|---|---|---|
| ONSPD | ONS | Quarterly (Feb/May/Aug/Nov) | Align to ONS release announcements | Verify SE district counts; sample street joins; cross-check with lookups[^1][^5] |
| NSPL | ONS | Quarterly | As above | Compare with ONSPD; validate best-fit allocations[^1][^24] |
| AddressBase Core | OS | Weekly publication of full dataset | Weekly | Verify USRN/UPRN joins; compare SE street count trends[^9][^13] |
| AddressBase Plus/Premium | OS | Product-specific (around six-weekly) | As per OS release notes | Check added fields (TOIDs, multi-occupancy) consistency[^9][^14][^15] |
| OS Open Names | OS | Quarterly | Jan/Apr/Jul/Oct cadence | Reconcile street naming variants; align locality names[^25][^26] |
| OS Open Greenspace | OS | Periodic | As per dataset page | Ensure contextual layers align with street set[^29][^30] |

## Appendix: Direct URLs and Verification Resources

Table 11 lists the key resources for download, access, and verification. Use the Reference IDs to locate the URLs in the References section.

Table 11. Reference index (by Reference ID; see References for URLs)

| Dataset/Resource | Reference ID | Purpose | Notes |
|---|---|---|---|
| ONS Postcode products (overview) | [1] | Product definitions and methodology | ONSPD vs NSPL |
| ONS Open Geography Portal | [2] | Home for ONSPD/NSPL and boundaries | Downloads, tools, APIs |
| ONSPD February 2025 dataset | [5] | Direct dataset access | CSV/TXT/ZIP multi-CSV |
| ONSPD direct ZIP download | [6] | Bulk download | Multi-CSV ZIP |
| ONS Postcode Directory Look-up Tool | [7] | Interactive postcode lookup and CSV export | Quick checks only |
| ONS Tabular/Spatial Extract Tool | [8] | Extract by geography | Not bulk SE filter |
| GDS guidance: AddressBase free access | [9] | PSGA access and product overview | Weekly publication detail |
| AddressBase product landing | [10] | Product overview | Feature highlights |
| OS AddressBase Core | [13] | Product details | CSV-based Core |
| OS AddressBase Plus | [14] | Product details | Enriched attributes |
| OS AddressBase Premium | [15] | Product details | GML format |
| OS AddressBase Islands | [16] | Product details | Coverage beyond GB |
| OS Places API: Postcode | [17] | API specification | Postcode search |
| FindMyStreet | [18] | Public street verification | USRN checks |
| FindMyAddress | [19] | Public address/UPRN verification | 10/day, personal use |
| ONS Postcode Directory (landing) | [20] | Dataset landing | ONSPD |
| NSPL dataset | [24] | NSPL download | CSV/TXT |
| OS Open Names | [25] | Product page | Dataset description |
| OS Open Names download | [26] | Direct open download | CSV/GML/GeoPackage |
| OS Data Hub | [27] | Authentication and access | PSGA, open downloads |
| PSGA Member Finder | [28] | Eligibility | Public sector members |
| OS Open Greenspace (Data.gov.uk) | [29] | Dataset page | Open dataset |
| OS Open Greenspace product page | [30] | Overview | Coverage and use |
| OS OpenData portal | [31] | Open data landing | Licences and downloads |
| ONS Postcode to OA… lookup | [11] | Administrative linkages | Validation |
| GDS open standards (UPRN/USRN) | [22] | Standards | Identifier usage |

## Information Gaps and Practical Notes

- The London Datastore page for a “Postcode Directory for London” could not be verified during this research because access was blocked by a security challenge. Its relationship to ONSPD for London-specific extracts is therefore unconfirmed here.
- The OS Data Hub “Open Data Downloads” page loads dynamically, preventing capture of precise file listings; however, OS Open Names and related products are publicly documented and downloadable (see references).
- AddressBase access is governed by the PSGA. Concrete SE-area extraction workflows via the OS Data Hub will depend on your organisation’s PSGA status, authentication, and product licensing.
- FindMyAddress and FindMyStreet are public search tools; bulk or automated extraction methods are not documented here and are likely restricted by terms of use.

## References

[^1]: Postcode products - Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/postcodeproducts  
[^2]: Open Geography Portal. https://geoportal.statistics.gov.uk/  
[^3]: ONS Postcode Directory (February 2025) for the UK. https://geoportal.statistics.gov.uk/datasets/6fb8941d58e54d949f521c92dfb92f2a  
[^4]: National Statistics Postcode Lookup (May 2025) User Guide. https://hub.arcgis.com/datasets/1320d98561d44fd98da21b9962e84396  
[^5]: ONSPD direct ZIP download (February 2025). https://www.arcgis.com/sharing/rest/content/items/6fb8941d58e54d949f521c92dfb92f2a/data  
[^6]: ONS Postcode Directory (May 2025) for the UK - ArcGIS Hub. https://hub.arcgis.com/datasets/3be72478d8454b59bb86ba97b4ee325b  
[^7]: ONS Postcode Directory Look-up Tool. https://ons.maps.arcgis.com/apps/webappviewer/index.html?id=374d26ccc6244bf594465a3a4ab3ac19  
[^8]: ONS Postcode Directory Tabular and Spatial Extract Tool. https://geoportal.statistics.gov.uk/apps/ons-postcode-directory-extract-tool  
[^9]: Access free address data using AddressBase - GOV.UK. https://www.gov.uk/guidance/access-free-address-data-using-addressbase  
[^10]: AddressBase | Data Products | Ordnance Survey. https://www.ordnancesurvey.co.uk/products/addressbase  
[^11]: Postcode to OA (2021) to LSOA to MSOA to LAD lookup. https://geoportal.statistics.gov.uk/search?tags=LUP_PCD_OA_LSOA_MSOA_LAD  
[^12]: AddressBase - OS Downloads Documentation. https://docs.os.uk/os-downloads/addressing-and-location/addressbase  
[^13]: AddressBase Core | Ordnance Survey. https://www.ordnancesurvey.co.uk/products/addressbase-core  
[^14]: AddressBase Plus | Ordnance Survey. https://www.ordnancesurvey.co.uk/products/addressbase-plus  
[^15]: AddressBase Premium | Ordnance Survey. https://www.ordnancesurvey.co.uk/products/addressbase-premium  
[^16]: AddressBase Islands | Ordnance Survey. https://www.ordnancesurvey.co.uk/products/addressbase-islands  
[^17]: Postcode | OS Places API - Technical Specification. https://docs.os.uk/os-apis/accessing-os-apis/os-places-api/technical-specification/postcode  
[^18]: FindMyStreet. https://www.findmystreet.co.uk/map  
[^19]: FindMyAddress. https://www.findmyaddress.co.uk/  
[^20]: ONS Postcode Directory (ONSPD) - Open Geography Portal. https://geoportal.statistics.gov.uk/search?q=PRD_ONSPD  
[^21]: A Guide to ONS Geography Postcode Products. https://geoportal.statistics.gov.uk/search?collection=Document&sort=name&tags=DOC_UG_PCD  
[^22]: Identifying property and street information - GOV.UK. https://www.gov.uk/government/publications/open-standards-for-government/identifying-property-and-street-information  
[^23]: Find open data - data.gov.uk. https://www.data.gov.uk/  
[^24]: National Statistics Postcode Lookup (NSPL) - Open Geography Portal. https://geoportal.statistics.gov.uk/search?q=PRD_NSPL  
[^25]: OS Open Names | Data Products - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-open-names  
[^26]: Download OS Open Names - OS Data Hub. https://osdatahub.os.uk/downloads/open/OpenNames  
[^27]: OS Data Hub. https://osdatahub.os.uk/  
[^28]: PSGA Member Finder - Ordnance Survey. https://www.ordnancesurvey.co.uk/business-government/partner-member/member  
[^29]: OS Open Greenspace - Data.gov.uk. https://www.data.gov.uk/dataset/4c1fe120-a920-4f6d-bc41-8fd4586bd662/os-open-greenspace1  
[^30]: OS Open Greenspace | Data Products - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-open-greenspace  
[^31]: Open Data Downloads | OS Data Hub. https://osdatahub.os.uk/data/downloads/open