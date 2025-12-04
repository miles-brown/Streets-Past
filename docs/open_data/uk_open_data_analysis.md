# UK Open Data for Street Names and Historical Information: Sources, Formats, Updates, and Licensing for Commercial Use

## Executive Summary

This guide maps the principal United Kingdom open data sources for street names and historical information, and sets out the practical and legal requirements for using them in commercial products. It focuses on authoritative geospatial datasets (Ordnance Survey), national heritage designations (Historic England), postcode datasets, local government portals, historical maps (British Library), and genealogy resources that provide street‑level context. For each source, it explains formats, coverage, update cycles, download or API access, licensing, and the attribution and compliance obligations that matter to product, data, and legal teams.

Key findings:

- Ordnance Survey (OS) OpenNames is the principal open dataset for street names and place names across Great Britain. It is published in CSV, GML, and GeoPackage; updated quarterly; and distributed via the OS Data Hub and associated product documentation. OS OpenNames is free to use under the OS OpenData terms and is suitable for commercial reuse when attribution and other licence conditions are met.[^2][^1][^3][^18]

- Historic England’s National Heritage List for England (NHLE) is the official register of designated historic assets in England. Data is distributed via the Historic England Open Data Hub as GIS layers (points and polygons) and is generally updated on a frequent cadence, with the heritage-at-risk dataset updated annually. Licensing is under the Open Government Licence (OGL) v3.0; attribution must include Historic England and, for spatial data, Ordnance Survey Crown rights.[^5][^4][^7][^16]

- Code-Point Open provides Great Britain postcode units with grid references and is published in CSV and GeoPackage. It is updated quarterly and available through OS Data Hub and data.gov.uk. Licensing is OGL v3.0, but product pages and ONS guidance require specific attributions acknowledging OS, Royal Mail, and National Statistics rights; Northern Ireland postcodes are excluded and have separate licensing.[^9][^10][^12][^20]

- Boundary-Line maps administrative and electoral boundaries for Great Britain and is updated twice yearly. It is accessible via OS Data Hub under OGL terms and should be used alongside the Office for National Statistics (ONS) Open Geography Portal for definitive boundary products across the UK.[^14][^13][^15][^23][^24]

- Local authority open data portals commonly publish street and address-related datasets. The Department for Transport (DfT) guidance recommends publishing under OGL with rich metadata and the use of open formats (CSV, JSON, XML). When publishing datasets that contain OS data, local authorities must follow OS criteria and provide appropriate attribution.[^25][^26]

- The British Library’s collections include extensive historical maps; access to items varies by copyright and format. While many digitised images are available, this report did not confirm dataset-level bulk download licensing for map images; usage depends on item-specific rights and terms.[^27]

- Genealogy sources, including Free UK Genealogy (CC0), The National Archives (TNA) census guides (historic access terms), and the UK Data Service (censuses under OGL), provide street-level historical context. For commercial reuse, check per-dataset licensing and any third‑party rights; Free UK Genealogy’s CC0 licensing is broadly permissive.[^28][^29][^30]

Commercial use is generally permitted under OGL for OS open products, Historic England datasets, Code-Point Open, and ONS boundaries, subject to attribution and to respecting non-OGL elements such as logos and third-party data (e.g., Royal Mail). Northern Ireland postcode data and certain NI boundary components require separate licences. This guide provides concrete attribution templates and a compliance checklist to support safe productisation.[^12][^21][^4][^25]



## Methodology and Scope

This report prioritises official sources from Ordnance Survey, Historic England, the Office for National Statistics (ONS), the Department for Transport (DfT), The National Archives (TNA), and the UK Data Service, supplemented by recognised portals such as data.gov.uk and the British Library. Where data portals or product pages describe licensing, update cycles, formats, and access mechanisms, those details are taken as authoritative. When terms differ across sources or include exceptions (e.g., Northern Ireland), we highlight the divergence and its operational implications.

Scope:

- Geospatial baselines for contemporary street names and places (OS OpenNames), administrative boundaries (OS Boundary-Line; ONS Open Geography), and postcode geographies (Code-Point Open; ONS Postcode Directory). 
- National heritage designations and historic environment layers in England (Historic England NHLE and related datasets).
- Local authority open data practice relevant to streets and addresses (DfT guidance).
- Historical map holdings and access (British Library).
- Genealogical datasets and historical street-level records (Free UK Genealogy, TNA census guides, UK Data Service).

Temporal baseline: current as of December 2024, acknowledging that update cadence and publication schedules can change and must be verified at the time of download or integration.



## OS OpenNames Dataset: Formats, Updates, Licensing, Coverage

OS OpenNames provides a comprehensive gazetteer of place names, road numbers and names, and postcodes for Great Britain, with features positioned using British National Grid. It is designed for address and location enrichment, place search, and routing applications. The dataset includes alternative names in Welsh, Scots, and Gaelic alongside English, and spans hundreds of thousands of named and numbered roads, tens of thousands of settlements, and over 1.6 million postcodes.[^2]

From a technical perspective, OS OpenNames is published in CSV, GML, and GeoPackage formats, suitable for direct loading into GIS, databases, and analytical pipelines. Coverage is Great Britain. OS documents indicate a quarterly release cadence with publication windows in January, April, July, and October. Distribution is via the OS Data Hub downloads site and the OS OpenData plan (free).[^2][^1][^3][^18]

Licensing and commercial use. OS OpenNames is provided under OS OpenData terms. Commercial reuse is permitted subject to attribution and other licence conditions. Teams should treat the dataset as open data under the OS Open Data Licence (compatible with OGL-style attribution) and include appropriate acknowledgements in downstream products.[^18][^3]

Integration tips. Because OS OpenNames uses British National Grid (EPSG:27700), downstream systems often reproject to WGS84 (EPSG:4326) for web mapping while retaining grid coordinates for analytics. The CSV and GeoPackage options provide flexible entry points for both relational and GIS workflows.[^3][^2][^1]

To make these details operational, Table 1 summarises the key specifications and access points.

Table 1. OS OpenNames specifications and access

| Element | Detail |
|---|---|
| Purpose and content | Gazetteer of place names, road numbers/names, and postcodes; includes Welsh/Scots/Gaelic alternatives |
| Formats | CSV, GML, GeoPackage |
| Coordinate system | British National Grid (EPSG:27700) |
| Coverage | Great Britain |
| Update frequency | Quarterly (Jan/Apr/Jul/Oct) |
| Download access | OS Data Hub – Open Data Downloads; OS OpenNames product page |
| Licensing model | OS Open Data Licence; commercial reuse permitted with attribution |
| Example counts | 870k+ named/numbered roads; ~44k settlements; 1.6M+ postcodes |

As shown in Table 1, OS OpenNames is a high-coverage, regularly refreshed gazetteer that fits naturally into address normalisation and place search workflows. The quarterly cycle enables a predictable refresh schedule in data pipelines. The availability of both CSV (for tabular joins) and GeoPackage (for geospatial workflows) helps unify ETL across teams using different toolchains.[^2][^1][^3][^18]



## UK Postcodes Data: Code-Point Open and ONS Postcode Directory

Code-Point Open is Ordnance Survey’s open dataset of postcode units for Great Britain, each with a grid reference and supporting attributes such as administrative and NHS codes. It covers approximately 1.7 million postcode units and is published in CSV and GeoPackage formats. The dataset is updated quarterly and is widely used for geocoding enrichment, customer analytics, and route planning.[^9][^10][^11][^20]

Access and formats. Code-Point Open can be obtained via data.gov.uk and OS Data Hub. CSV supports lightweight integration into data warehouses and analytics stacks; GeoPackage supports spatial joins and map visualisation alongside other GIS layers.[^9][^10][^11]

Licensing and attribution. Code-Point Open is licensed under OGL v3.0. In practice, attribution must also acknowledge the rights of Ordnance Survey (Crown copyright and database rights), Royal Mail (postcode rights), and National Statistics (where applicable). Northern Ireland postcodes are not included in Code-Point Open, and their reuse is governed by separate terms (see Northern Ireland notes below).[^9][^12][^21]

ONS Postcode Directory (ONSPD). The ONSPD is a comprehensive UK-wide postcode directory with lookups across multiple geographies (e.g., LSOA, MSOA, region, local authority). It is useful for analytical joins and roll-ups in the UK context. ONSPD access and documentation are available via the ONS GeoPortal and related ONS resources. Licensing and attribution follow OGL v3.0 plus third‑party rights as described above; Northern Ireland usage may require additional permissions.[^13][^12]

Table 2 contrasts Code-Point Open and the ONS Postcode Directory in practical terms.

Table 2. Code-Point Open vs ONS Postcode Directory

| Dimension | Code-Point Open | ONS Postcode Directory (ONSPD) |
|---|---|---|
| Purpose | Open unit-level postcodes with grid references | UK-wide directory enabling joins to statistical and administrative geographies |
| Coverage | Great Britain (excl. Northern Ireland) | United Kingdom (including Northern Ireland) |
| Formats | CSV, GeoPackage | Multi-CSV, supporting Excel and GIS ingestion (as provided on the ONS GeoPortal) |
| Update frequency | Quarterly | Regular releases; see ONS GeoPortal for current cadence |
| Access | OS Data Hub; data.gov.uk | ONS GeoPortal (and related ONS resources) |
| Licensing | OGL v3.0; attribution to OS, Royal Mail, National Statistics | OGL v3.0; attribution to ONS/OS/Royal Mail as applicable; NI may need extra terms |
| Northern Ireland | Not included | Included; separate licensing may apply for certain uses |

The main takeaway from Table 2 is that Code-Point Open is optimal for spatial positioning and lightweight geocoding in Great Britain, while ONSPD is the right companion for UK-wide analytical joins across statistical geographies. Combined, they support both mapping and analytics with a single postcode-to-geography mapping framework.[^9][^10][^11][^13][^12]



## Boundary Data: OS Boundary-Line and ONS Open Geography

Boundary-Line is Ordnance Survey’s map of administrative and electoral boundaries for Great Britain, updated twice a year (May and October). It provides vector geometries at 1:10,000 scale and is available through OS Data Hub under the OGL. Common uses include electoral analysis, service planning, and boundary overlays for addresses and neighbourhoods.[^14][^15][^24]

ONS Open Geography Portal is the definitive source for UK boundary products, including full extent, generalised, and clipped variants designed for GIS. It supplies statistical and administrative geographies for the whole UK and is the recommended source for harmonised boundary datasets across England, Wales, Scotland, and Northern Ireland.[^23][^24]

Table 3 helps teams decide when to use Boundary-Line versus ONS Open Geography products.

Table 3. Boundary-Line vs ONS Open Geography

| Dimension | OS Boundary-Line | ONS Open Geography Portal |
|---|---|---|
| Scope | Great Britain | United Kingdom (definitive statistical/administrative geographies) |
| Update frequency | Twice yearly (May, October) | As per ONS release schedule |
| Format | Vector GIS data; see OS documentation | Full, generalised, and clipped boundary products in GIS formats |
| Licensing | OGL v3.0 | OGL v3.0 |
| Use cases | Electoral and administrative analysis; council wards; parishes; constituencies | Statistical joins; UK-wide comparability; consistent cross-border analysis |

When covering Great Britain only, Boundary-Line provides an immediately usable, familiar administrative layer. For UK‑wide projects, ONS Open Geography ensures consistent coding and coverage, including Northern Ireland geometries and statistical units that align with census and other national statistics.[^14][^24][^23][^15]



## Historic England Listed Building Records and the National Heritage List for England (NHLE)

NHLE is the official, up-to-date register of nationally protected historic buildings and sites in England. Historic England disseminates NHLE and related historic environment datasets via its Open Data Hub in GIS formats (points and polygons), including Listed Buildings, Scheduled Monuments, Registered Parks and Gardens, Battlefields, Protected Wrecks, and more. Management datasets (e.g., Heritage at Risk) and thematic layers (e.g., Conservation Areas, Archaeological Priority Areas) are also available. The Open Data Hub and dataset pages indicate frequent updates, and the Heritage at Risk register is updated annually.[^5][^7][^16]

Licensing. Historic England’s open data is licensed under OGL v3.0. Attribution should take the form “© Historic England [year]”, and for spatial data should also state “Contains Ordnance Survey data © Crown copyright and database right [year]”. Historic England’s terms emphasise that data is provided “as is”, and users must not misrepresent the data or suggest endorsement. They also highlight data protection obligations and the exclusion of trademarked logos from the open licence.[^4]

Downloading and APIs. Historic England’s Open Data Hub provides downloads and access to services/APIs for direct integration into GIS and data platforms. Teams should avoid scraping the public website and instead rely on the Open Data Hub for reliable, licenced access. Dataset documentation clarifies content and update status; for example, the Heritage at Risk register is annual, while many NHLE layers are updated frequently.[^5][^4][^7]

Table 4 summarises the principal NHLE and related datasets, their formats, and update patterns.

Table 4. NHLE and related Historic England datasets

| Dataset | Geometry | Update frequency | Access |
|---|---|---|---|
| Listed Buildings | Points and polygons | Frequent updates (see dataset page) | Historic England Open Data Hub |
| Scheduled Monuments | Points and polygons | Frequent updates | Historic England Open Data Hub |
| Registered Parks & Gardens | Polygons | Frequent updates | Historic England Open Data Hub |
| Battlefields | Polygons | Frequent updates | Historic England Open Data Hub |
| Protected Wrecks | Points/polygons | Frequent updates | Historic England Open Data Hub |
| World Heritage Sites | Polygons | Frequent updates | Historic England Open Data Hub |
| De-Designated Sites | Various | Updated as changes occur | Historic England Open Data Hub |
| Conservation Areas | Polygons | Regular updates | Historic England Open Data Hub |
| Heritage at Risk (register) | Annual spreadsheet + GIS | Annual | Historic England Open Data Hub |
| Greater London Archaeological Priority Areas | Polygons | Periodic updates | Historic England Open Data Hub |

For each dataset, Historic England provides dataset-level information on content and update cadence; teams should capture the “last updated” date at the time of download and reflect it in product metadata and user communications.[^5][^7][^4][^16]



## Local Council Open Data Portals: Discovery, Standards, Licensing

Local authorities publish a wide array of datasets relevant to streets and addresses—ranging from street naming and numbering to traffic signals, off-street parking, and public rights of way. The Department for Transport’s guidance sets out a practical framework: adopt open standards where they exist; publish in common open formats (CSV/JSON/XML); publish rich metadata in the same place as the data; and apply the Open Government Licence (OGL) by default, including an attribution statement.[^25]

The guidance also addresses the use of Ordnance Survey data by local authorities. If an authority’s dataset includes OS data, it must check OS criteria before publishing and include required OS attribution statements. The Public Sector Geospatial Agreement (PSGA) facilitates public-sector access and sharing of OS data for core business activity, and OS OpenData is already covered under OGL. Where authorities are not covered by the PSGA presumption-to-publish, OS provides a process to request publishing exemptions.[^25]

Platforms. Authorities commonly publish via local data portals, UTMC systems, or sub-national transport body (STB) platforms. Where UTMC infrastructure exists, DfT recommends leveraging its data publishing capabilities, ensuring data is available in open formats and that any constraints (e.g., rate limits) are documented. Publishing should anticipate user feedback and provide contact channels for error reporting and access requests.[^25]

Table 5 provides a concise metadata checklist for local authority datasets, and Table 6 offers common licensing and attribution patterns.

Table 5. Minimum metadata fields for local authority open data

| Field | Purpose |
|---|---|
| Title | Identify the dataset |
| Unique identifier | Support programmatic referencing |
| Website URL of the dataset | Direct access and provenance |
| What data is included | Clarify scope (e.g., “Street naming and numbering register”) |
| Location | Latitude/longitude in EPSG:4326, where applicable |
| Unit | Units of measurement where relevant |
| Origin date | When the dataset was generated |
| Last modified | Date of most recent update |
| Date range | Temporal coverage |
| Contact details | Support for queries and error reporting |

Table 6. Licensing patterns and examples for local authorities

| Scenario | Licence | Attribution example |
|---|---|---|
| Default open data | OGL v3.0 | “Contains public sector information licensed under the Open Government Licence v3.0.” |
| OS-containing dataset | OGL (OS OpenData) + OS attribution | “Contains OS data © Crown copyright and database right [year].” |
| Authority-specific policy | OGL with local statement | “Open data, [Council name], licensed under the Open Government Licence.” |

These practices ensure discoverability, interoperability, and lawful reuse. They also reduce friction downstream by signalling update cadence, formats, and licensing in machine-readable ways.[^25][^26]



## British Library Historical Maps: Access and Re‑use

The British Library holds over 170 million items, including extensive map collections. Access to digitised items is offered through various portals and services, but usage rights vary by item, copyright status, and intended use. Many images are available to view free of charge, while reproduction or high-resolution downloads may involve additional terms or fees. The Library’s operations may periodically experience service disruptions (e.g., planned catalogue updates or strike action), so teams should plan for access variability and monitor official notices.[^27]

For product teams, the implication is clear: item-by-item due diligence is required before bulk reuse of map images. Unlike geospatial open data under OGL, digitised historical map images often carry specific rights statements, even when the underlying item is out of copyright. This report did not identify a definitive, dataset-level bulk download licence for British Library map images; confirmation is required from the Library’s rights statements and licences on a per-item basis.[^27]



## Genealogy Datasets with Street Information

Free UK Genealogy provides free access to family history databases under a Creative Commons CC0 Public Domain Dedication, which permits commercial reuse subject only to attribution and link-back where practicable. Projects include FreeBMD (civil registration indexes), FreeCEN (nineteenth-century census transcripts), and FreeREG (parish registers). While these resources offer rich address and street context, licensing is per project and dataset; any commercial application should confirm the applicable licence at the point of use.[^28]

The National Archives (TNA) publish authoritative guides to historic census records from 1841 to 1921. Address capture improved over time: from 1851 onward, schedules generally required exact address (house name or number), and 1911 Enumerators’ Summary Books list every address, including uninhabited buildings. Street indexes exist for larger towns and have been archived. These guides are essential for interpreting historical address data and for integrating genealogical street context into historical products.[^29]

The UK Data Service provides access to census aggregate, flow, boundary, and microdata, much of it under OGL. Boundary datasets and geographic look-up tables are available in common GIS formats for multiple census years and support spatial analysis and time-series comparability.[^30]

Table 7 compares these genealogy and census resources for commercial use and street-level coverage.

Table 7. Genealogy and census resources: scope, formats, licensing

| Resource | Scope | Formats | Licensing | Street-level utility |
|---|---|---|---|---|
| Free UK Genealogy | Birth/marriage/death indexes; census transcripts; parish registers | Web datasets; downloadable data varies | CC0 (per project/dataset) | High for 19th-century address and street context |
| The National Archives (TNA) | Historical census guides (1841–1921) | Guides, references, archival catalogues | Not a data licence; research guidance | High for interpreting addresses, street indexes |
| UK Data Service | Census aggregates, flows, boundaries, microdata | GIS formats; CSV; online explorers | OGL for many datasets | High for boundary joins and historical geographies |

In practice, Free UK Genealogy offers permissive, CC0-licensed content for enrichment, while TNA and UK Data Service resources enable rigorous historical interpretation and spatial joins under OGL. As always, confirm exact licence terms for each dataset at the time of use.[^28][^29][^30]



## Licensing and Attribution for Commercial Use

Open Government Licence (OGL) v3.0. The OGL is the standard licence for UK public sector information. It grants a worldwide, royalty-free, perpetual, non-exclusive right to copy, publish, distribute, adapt, and exploit information commercially and non-commercially, provided attribution is given and certain restrictions are respected (e.g., no endorsement, no use of logos, no warranty, exclusion of personal data and unlicensed third-party rights). OGL is compatible with Creative Commons Attribution (CC BY) and Open Data Commons Attribution Licence.[^21]

ONS and third-party rights. The ONS guidance for geographical products emphasises that OGL applies to many postcode and boundary datasets, but downstream users must also respect third-party rights—most notably Royal Mail’s interest in postcodes and OS Crown rights in geospatial data. Attribution statements should therefore include both the OGL statement and specific acknowledgements of OS and Royal Mail where applicable.[^12]

Historic England. Historic England’s open data is licensed under OGL v3.0 with specific attribution expectations: “© Historic England [year]” and, for spatial data, “Contains Ordnance Survey data © Crown copyright and database right [year]”. Historic England excludes logos and other marks from the open licence, and disclaims liability, requiring users to avoid misrepresentation and to comply with data protection and other laws.[^4]

OS OpenData. OS OpenNames (and other OS OpenData products) are free to use for commercial and non-commercial purposes under OS OpenData terms; attribution is required. Teams should follow OS’s suggested attribution language and ensure that any derived products that include OS data meet OS OpenData conditions and PSGA-related guidance where relevant.[^18][^25]

Local authorities. DfT’s guidance sets OGL as the default licence and provides suggested attribution statements. When OS data is present, authorities must include OS attribution. Authorities can publish their own attribution statements consistent with OGL and their open data policies.[^25]

Table 8 distils licensing and attribution requirements across the main sources in scope.

Table 8. Consolidated licensing and attribution matrix

| Source | Licence | Commercial use | Required attribution |
|---|---|---|---|
| OS OpenNames | OS OpenData Licence | Yes | OS attribution; follow OS OpenData terms |
| Code-Point Open | OGL v3.0 | Yes | OGL statement; OS; Royal Mail; National Statistics |
| OS Boundary-Line | OGL v3.0 | Yes | OGL statement; OS Crown rights |
| ONS Open Geography | OGL v3.0 | Yes | OGL statement; ONS and OS rights |
| Historic England (NHLE, etc.) | OGL v3.0 | Yes | © Historic England [year]; OS data © Crown copyright and database right [year] |
| UK Data Service census data (where OGL) | OGL v3.0 | Yes | OGL statement; source acknowledgement |
| Free UK Genealogy | CC0 | Yes | Attribution and link-back encouraged; not required by licence |
| British Library map images | Varies by item | Case-by-case | Item-specific rights statements and terms |

Finally, for attribution templates that meet OGL and related requirements, Table 9 provides working examples.

Table 9. Attribution templates

| Scenario | Attribution text |
|---|---|
| OGL-only dataset | “Contains public sector information licensed under the Open Government Licence v3.0.” |
| OS geospatial data (e.g., Boundary-Line, OS OpenNames) | “Contains OS data © Crown copyright and database right [year].” |
| Code-Point Open | “Contains OS data © Crown copyright and database right [year]. Contains Royal Mail data © Royal Mail copyright and database right [year]. Contains National Statistics data © Crown copyright and database right [year]. Licensed under the Open Government Licence v3.0.” |
| Historic England spatial data | “© Historic England [year]. Contains Ordnance Survey data © Crown copyright and database right [year]. Licensed under the Open Government Licence v3.0.” |
| Free UK Genealogy | “Contains data from Free UK Genealogy, licensed under CC0 (attribution and link-back encouraged).” |
| Local authority dataset (OS present) | “Contains public sector information licensed under the Open Government Licence v3.0. Contains OS data © Crown copyright and database right [year].” |

These templates should be included in product documentation, dataset metadata, and any end-user licence notices, alongside version and date-of-data statements to support audits and reproducibility.[^21][^12][^4][^25][^28]



## Integration Playbook: Combining Street Names, Postcodes, Boundaries, and Heritage

A practical integration strategy brings together authoritative, open datasets to form a coherent model for search, navigation, analytics, and heritage enrichment. Below is a step-by-step approach.

1) Establish the street backbone with OS OpenNames. Ingest OS OpenNames in GeoPackage or CSV and normalise key fields such as road names, road numbers, locality, and alternative name forms. Retain British National Grid geometry for analytics, and create a derived WGS84 layer for web mapping. The quarterly cadence makes it straightforward to schedule a repeatable refresh.[^1][^2][^3]

2) Enrich with postcodes using Code-Point Open and ONSPD. Use Code-Point Open to position postcode units in Great Britain; for UK‑wide joins to statistical geographies (e.g., LSOA/MSOA), integrate the ONS Postcode Directory. For Northern Ireland, confirm separate licensing terms before combining with GB-only open datasets.[^9][^10][^11][^13][^12]

3) Add administrative context via Boundary-Line and ONS boundaries. For Great Britain coverage, Boundary-Line offers a standard administrative baseline; for UK‑wide comparability and NI coverage, source boundary geometries from the ONS Open Geography Portal. Harmonise administrative codes and naming conventions to enable robust reporting and aggregation.[^14][^24][^23][^15]

4) Overlay heritage designations from Historic England. Consume NHLE and related datasets through the Historic England Open Data Hub, selecting the appropriate geometry type (points/polygons) by use case. Record the “last updated” date of each dataset and store it in your metadata store to support provenance, reproducibility, and risk reporting.[^5][^7][^16]

5) Validate licensing and attribution throughout the pipeline. For every ingest or refresh, embed attribution strings in your product’s “About”/legal pages, dataset metadata, and internal runbooks. Ensure non-OGL elements (e.g., logos) are excluded, and confirm any third‑party rights that may be embedded in the data (e.g., Royal Mail). For Northern Ireland datasets, verify that the appropriate licence is in place before commercial use.[^21][^12][^4]

6) Manage updates on a cadence and publish transparency artefacts. Align refreshes to the datasets’ official cycles: quarterly for OpenNames and Code-Point Open; twice yearly for Boundary-Line; frequent for most NHLE layers; annual for Heritage at Risk. Maintain a register of dataset versions, last-updated dates, and attribution statements. Where your product exposes derived outputs, include a “data obtained on [date]” statement for transparency.[^2][^10][^14][^5][^7]

7) Handle coordinate systems and projections explicitly. Continue to store OS OpenNames and other OS products in EPSG:27700 for analytical precision, and create service layers in EPSG:4326 for web clients. Document coordinate systems in your data dictionaries and metadata.[^3]

This playbook helps teams avoid the common pitfalls—unclear licensing, mixed coordinate systems, and ad hoc refreshes—by sequencing the work in the order that best mirrors the datasets’ semantics and update rhythms.



## Risks, Restrictions, and Compliance Checklist

The main risks arise from three areas: licensing and attribution, personal data, and third‑party rights. Historic England explicitly disclaims endorsement and liability; OGL disclaims warranty; ONS highlights third‑party rights in postcode products; and the British Library’s map images require item‑specific rights clearance. Northern Ireland datasets often require separate licences.

Table 10 consolidates the core compliance items.

Table 10. Compliance checklist for open geospatial and heritage data

| Check | What to verify |
|---|---|
| Licence model and scope | Confirm OGL or other licence; check dataset-specific conditions (e.g., OS OpenData terms) |
| Attribution | Prepare correct attribution statement(s); include OS, Royal Mail, and National Statistics where applicable |
| Third‑party rights | Confirm rights for Royal Mail, OS, and any other embedded rights holders |
| Personal data | Ensure no personal data is present unless explicitly permitted; respect data protection laws |
| Endorsement | Do not suggest official endorsement; avoid use of logos and trademarks unless covered |
| Accuracy and currency | Record “last updated” date; include “data obtained on [date]” in product materials |
| Northern Ireland | Check separate licences for NI postcodes/boundaries before use |
| British Library images | Confirm item-level rights and permitted uses; do not assume dataset-level blanket open licence |

Teams should maintain an internal register of attributions, last-updated dates, and data lineage for each dataset. This register is invaluable for compliance audits, customer due diligence, and ongoing maintenance.[^21][^4][^12][^27]



## Appendix: Data Access, Formats, and Update Frequencies

The appendix summarises the principal datasets covered in this guide. Where OS Data Hub pages load dynamically, consult the OS product pages and technical documentation to confirm the latest file formats, schema notes, and download endpoints.

Table 11. Quick-reference summary

| Dataset | Provider | Coverage | Formats | Update frequency | Licence | Attribution | Download/API |
|---|---|---|---|---|---|---|---|
| OS OpenNames | Ordnance Survey | Great Britain | CSV, GML, GeoPackage | Quarterly (Jan/Apr/Jul/Oct) | OS OpenData | OS attribution | OS Data Hub; product page |
| Code-Point Open | Ordnance Survey | Great Britain | CSV, GeoPackage | Quarterly | OGL v3.0 | OGL; OS; Royal Mail; National Statistics | OS Data Hub; data.gov.uk |
| Boundary-Line | Ordnance Survey | Great Britain | Vector GIS | Twice yearly (May/Oct) | OGL v3.0 | OGL; OS rights | OS Data Hub; OS docs |
| ONS Open Geography | ONS | UK | GIS (full/generalised/clipped) | Per ONS schedule | OGL v3.0 | OGL; ONS/OS rights | ONS GeoPortal |
| ONSPD (Postcode Directory) | ONS | UK | Multi-CSV; GIS-ready | Regular releases | OGL v3.0 | OGL; OS/Royal Mail/NS where applicable | ONS GeoPortal |
| NHLE (Listed Buildings, etc.) | Historic England | England | GIS (points/polygons); spreadsheets (some) | Frequent; annual for Heritage at Risk | OGL v3.0 | © Historic England; OS Crown rights | Historic England Open Data Hub |
| Local authority datasets | Local authorities | Varies | CSV, JSON, XML; GIS | Varies by dataset | OGL by default | OGL; OS if present | Local portals; UTMC/STB platforms |
| British Library historical maps | British Library | Varies | Digitised images | N/A (item access varies) | Item-specific | Item-level rights statements | British Library portals |
| Free UK Genealogy | Free UK Genealogy | UK | Web/download | Ongoing | CC0 | Attribution/link-back encouraged | Free UK Genealogy site |
| UK Data Service census data | UK Data Service | UK | GIS; CSV; explorers | Varies | OGL (many datasets) | OGL; source acknowledgement | UK Data Service portals |

For the most current release dates and file-level schema notes, consult the provider pages at the time of download. When integrating into a data platform, preserve the provenance (source, version, last-updated date) alongside the data itself.[^2][^11][^15][^24][^13][^5][^25][^27][^28][^30]



## Information Gaps and Caveats

- OS Data Hub download pages for some products may render dynamically; use the OS product pages and technical documentation for definitive formats, schemas, and endpoints.
- British Library digitised map images: item-level copyright and reuse terms vary, and no blanket dataset-level open licence was confirmed in this report.
- Northern Ireland postcode and boundary licensing often requires separate licences; verify with the appropriate Northern Ireland authority before commercial use.
- The precise dataset-level schema for OS OpenNames (field-by-field) should be taken from OS technical documentation when implementing ingestion pipelines.
- Local authority portals are heterogeneous; the examples referenced represent common practices rather than a comprehensive survey.



## References

[^1]: OS Open Names | Data Products - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-open-names  
[^2]: Download OS Open Names - OS Data Hub. https://osdatahub.os.uk/downloads/open/OpenNames  
[^3]: OS Open Names technical documentation. https://docs.os.uk/os-downloads/addressing-and-location/os-open-names  
[^4]: Historic England Open Data Hub Terms and Conditions. https://historicengland.org.uk/terms/website-terms-conditions/open-data-hub/  
[^5]: Historic England Open Data Hub. https://opendata-historicengland.hub.arcgis.com/  
[^6]: Download Listing Data - Historic England. https://historicengland.org.uk/listing/the-list/data-downloads/  
[^7]: National Heritage List for England (NHLE) - API Catalogue. https://www.api.gov.uk/he/national-heritage-list-for-england-nhle/  
[^8]: Search the List – Historic England. https://historicengland.org.uk/listing/the-list/  
[^9]: Code-Point Open - Data.gov.uk. https://www.data.gov.uk/dataset/c1e0176d-59fb-4a8c-92c9-c8b376a80687/code-point-open2  
[^10]: Download Code-Point Open - OS Data Hub. https://osdatahub.os.uk/downloads/open/CodePointOpen  
[^11]: Code-Point Open technical documentation. https://docs.os.uk/os-downloads/addressing-and-location/code-point-open  
[^12]: Licences - Office for National Statistics (ONS). https://www.ons.gov.uk/methodology/geography/licences  
[^13]: ONS Postcode Directory (UK) - Geoportal. https://geoportal.statistics.gov.uk/datasets/b54177d3d7264cd6ad89e74dd9c1391d  
[^14]: Boundary-Line | Data Products - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/boundary-line  
[^15]: Boundary-Line technical documentation. https://docs.os.uk/os-downloads/addressing-and-location/boundary-line  
[^16]: Historic England listed building points dataset. https://opendata-historicengland.hub.arcgis.com/datasets/historicengland::listed-building-points/explore  
[^17]: OS Names API - API Catalogue. https://www.api.gov.uk/os/os-names-api/  
[^18]: OS Open Data Licence (summary PDF). https://www.rowmaps.com/datasets/SU/OS-opendata-licence.pdf  
[^19]: Open Data Downloads | OS Data Hub. https://osdatahub.os.uk/data/downloads/open  
[^20]: Code-Point Open product page - Ordnance Survey. https://os.uk/products/code-point-open  
[^21]: Open Government Licence v3.0 - The National Archives. https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/  
[^22]: Code-Point Open - London Datastore. https://data.london.gov.uk/dataset/ordnance-survey-code-point-open-epr1g  
[^23]: Open Geography Portal - ONS. https://geoportal.statistics.gov.uk/  
[^24]: Digital boundaries - ONS. https://www.ons.gov.uk/methodology/geography/geographicalproducts/digitalboundaries  
[^25]: Local authority transport: how to publish your data - GOV.UK. https://www.gov.uk/guidance/local-authority-transport-how-to-publish-your-data  
[^26]: Find open data - data.gov.uk. https://www.data.gov.uk/  
[^27]: British Library: Our collections. https://www.bl.uk/collection  
[^28]: Free UK Genealogy. https://www.freeukgenealogy.org.uk/  
[^29]: Census records - The National Archives. https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/census-records/  
[^30]: UK Data Service: Census data. https://ukdataservice.ac.uk/help/data-types/census-data/