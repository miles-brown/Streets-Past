# SE London Street Data Sources: A Borough-by-Borough Access Blueprint

## Executive Summary: What exists today for SE London streets

Across South East (SE) London, each borough’s approach to publishing street-related data is shaped by its digital maturity, statutory obligations, and available platforms. In practice, analysts can assemble a working street dataset for most SE postcodes by combining three types of sources: borough-level street or road registers; borough and Greater LondonAuthority (GLA) geospatial portals; and Transport for London (TfL) datasets for the parts of the network where TfL is the highway authority. 

- Southwark provides a modern data portal built on Esri technology, a council spectrum spatial mapping interface that explicitly exposes the Local Street Gazetteer (LSG), and a robust set of planning and environment datasets available under the Open Government Licence (OGL). Street centerline or gazetteer extraction will typically be done through the Spectrum Spatial interface or via direct engagement for data extracts. [^1][^5][^6][^8][^9][^10]
- Lewisham publishes an open-data site backed by SQLite databases and Datasette, exposing API endpoints and downloadable CSV/JSON. Street-related infrastructure such as electric vehicle (EV) chargepoints is accessible, and the full highway authority street inventory should be requested as the Local Street Gazetteer is not surfaced publicly. Supplementary traffic context is available from the Department for Transport (DfT). [^11][^12][^14][^15]
- Greenwich offers the most complete, ready-to-use borough street inventory for this study: a Road Register available in both PDF and CSV, covering SE7, SE8, SE9, and SE18. Additional transport-related documents and roadworks data are also published. [^16][^17][^18][^19][^20]
- Westminster maintains a central data hub and a Digital Planning data page aligned to national planning data standards. Street centerline or highway extent data were not explicitly surfaced; requests via the data team are the likely path, with planning data providing useful spatial context, especially for SE11. [^21][^22][^23]
- Bexley’s highway authority records provide a street list by maintenance responsibility with clear coding and last-updated dates. A dedicated enquiry process yields extent plans and finer detail for a fee; the Local Plan Policies Map on ArcGIS Online offers a policy context layer. [^24][^25][^26][^27]

Regional backbones and cross-cutting datasets are essential to a complete picture: TfL’s GIS Open Data Hub for the TLRN and other transport assets; the GLA’s London Datastore for GeoJSON and other citywide layers; and the Office for National Statistics (ONS) Open Geography portal for consistent boundaries to clip and aggregate results. [^2][^3][^4]

Immediate outcomes:
- A CSV street list can be downloaded for Greenwich now.
- EV chargepoints and ward/boundary layers can be extracted programmatically for Lewisham now.
- Southwark and Bexley provide authoritative street listings via interactive tools and highway records, respectively, with practical routes to extract or request geospatial versions.
- Westminster, Southwark (for centerlines), and Lewisham’s gazetteer require engagement or structured API/data requests for full street network layers.

To ground the above in a single view, the matrix below summarizes what is available today by borough and how to get it.

Table 1. Borough-to-dataset availability matrix for SE postcodes

| Borough      | SE postcodes (focus) | Street dataset/availability                               | Formats                         | Portal/Tool                                | Access method                              | License/Notes (summary)                                  | Update signal/status                         |
|--------------|-----------------------|------------------------------------------------------------|----------------------------------|---------------------------------------------|---------------------------------------------|-----------------------------------------------------------|-----------------------------------------------|
| Southwark    | SE1, SE14, SE15, SE16, SE17 | Local Street Gazetteer (LSG) via Spectrum Spatial; planning/environment geospatial layers | Interactive (Spectrum); GeoJSON/other for planning items | Southwark Data; Spectrum Spatial; Open Data page | Spectrum UI for LSG; open downloads for planning datasets; request LSG export | OGL for planning datasets; confirm LSG licensing on request | Spectrum Spatial live; planning datasets updated on portal |
| Lewisham     | SE3, SE4, SE12, SE13  | LSG not surfaced publicly; EV chargepoints; boundaries and lookups; FixMyStreet history | CSV/JSON (Datasette APIs); GIS map | Open Data Lewisham; Lewisham Observatory     | Datasette queries/API; Observatory for context; request LSG | Site terms not specified here; confirm on use            | Datasette-backed datasets; last-updated signals on site   |
| Greenwich    | SE7, SE8, SE9, SE18   | Road Register (street list) ready now                      | PDF; CSV                         | Greenwich Data Observatory; Road Register page | Direct download                             | Not specified here; confirm on download                   | Road register published in PDF/CSV               |
| Westminster  | SE11                  | Planning-related geospatial datasets via Digital Planning  | Spatial data per dataset         | Data hub; Digital Planning                   | Browse/download; request street layer if not present | Not specified here; confirm on dataset pages              | Active Digital Planning programme               |
| Bexley       | SE2                   | Publicly maintained highway list (status by street)        | Web page; documents; enquiry     | Highway records; Local Plan Policies Map     | Direct download (lists); paid extent enquiry; ArcGIS map | Not specified here; confirm on use                         | Last-updated dates on highway records page       |
| Regional     | All SE                | TfL network and assets; GLA/ONS boundaries                 | ArcGIS Hub layers; GeoJSON; GIS  | TfL GIS Hub; London Datastore; ONS Open Geography | Open downloads/APIs                          | OGL for TfL and GLA; ONS open geography                   | TfL catalog updates via RSS/DCAT/OGC Records     |

In short, the Greenwich Road Register is the quickest path to a borough-wide street list among the councils reviewed. Lewisham and Southwark require either API/UI workflows (Lewisham) or UI-to-request paths (Southwark’s LSG via Spectrum Spatial). Bexley provides an authoritative street register by maintenance responsibility and a paid route to detailed extents. Westminster exposes rich planning and corporate data; street centerlines or official highway extents are not immediately obvious and likely require direct request.

[^1]: Southwark Data portal.  
[^2]: TfL GIS Open Data Hub.  
[^3]: London Datastore – GeoJSON format datasets.  
[^4]: ONS Open Geography Portal.  
[^5]: Spectrum Spatial – Southwark Council.  
[^6]: Article 4 areas dataset (Southwark).  
[^8]: Tree dataset (Southwark).  
[^9]: Open data – Southwark Council.  
[^10]: Southwark Interactive Map.  
[^11]: Open Data Lewisham portal.  
[^12]: Lewisham Observatory.  
[^14]: Datasette JSON API documentation.  
[^15]: DfT Road Traffic – Lewisham.  
[^16]: Royal Greenwich Data Observatory.  
[^17]: Royal Borough of Greenwich Road Register page.  
[^18]: Greenwich Road Register (PDF).  
[^19]: Greenwich Road Register (CSV).  
[^20]: Greenwich public transport downloads.  
[^21]: Data – Westminster City Council.  
[^22]: Digital Planning Data – Westminster.  
[^23]: Westminster City Council: Digital planning improvement (case study).  
[^24]: Publicly maintained highway – London Borough of Bexley.  
[^25]: Bexley Data Hub overview.  
[^26]: Highways extent enquiry form – Bexley.  
[^27]: Bexley Local Plan Policies Map (ArcGIS Online item).  
[^28]: TfL Unified API documentation.  
[^29]: GeoPlace: National Street Gazetteer overview.  
[^30]: GeoPlace DataVia API (street data services).

---

## How to Use This Guide and Methodology

This guide is structured for analysts who need to assemble authoritative street datasets for SE postcode areas across Southwark, Lewisham, Greenwich, Westminster, and Bexley. It proceeds borough-by-borough, detailing what is available, how to access it (including direct downloads, APIs, or enquiry routes), and what licensing or update signals apply. To ensure reproducible workflows, we anchor each step to public portals and documented APIs, and we provide a consolidated access playbook that covers both self-serve and request-based routes.

Methodologically, the report synthesizes:
- Borough open data portals, mapping interfaces, and document repositories.
- Regional backbones, including TfL’s GIS Hub for network and assets, the London Datastore for citywide layers, and the ONS Open Geography portal for boundaries.
- Transport and street-related APIs and standards to enable programmatic discovery and retrieval.

Where boroughs do not publish a specific street layer, we identify the statutory context and the standard custodians for street data in England and Wales. In particular, the National Street Gazetteer (NSG) maintained under the GeoPlace programme underpins streetworks, highway, and planning workflows. While this report identifies practical routes to obtain or approximate borough street layers, analysts should engage borough custodians for definitive LSG/NSG extracts and any licensing details not specified in public materials. [^2][^3][^4][^29]

---

## Regional Backbones and Cross-Cutting Datasets

No single borough portal provides full coverage of every SE street with associated attributes. A robust approach layers borough registers and planning/geospatial data with TfL’s network and citywide boundaries.

First, TfL’s GIS Open Data Hub centralizes London-wide geospatial layers for roads, buses, rail, cycle infrastructure, river services, assets, boundaries, and environmental themes. The site supports programmatic discovery via RSS feeds, DCAT feeds, and OGC API – Records, and datasets are typically published under OGL or TfL transport data terms. This is the primary source forTfL-managed streets and associated assets, such as traffic signals, which are essential in areas where TfL is the highway authority. [^2]

Second, the London Datastore complements borough data by hosting a broad set of citywide datasets, including many in GeoJSON. For SE-focused analysts, this is an efficient route to obtain standardized spatial layers and cross-borough indicators for analysis and visualization. [^3]

Third, the ONS Open Geography portal provides authoritative boundary datasets—borough, ward, Lower-layer Super Output Areas (LSOA), and Middle-layer Super Output Areas (MSOA)—that enable consistent clipping, aggregation, and spatial joins of borough data to standardized geographies. [^4]

Table 2. Regional sources for streets and context

| Source                         | Coverage focus                                  | Formats and access                         | License/terms                  | Typical uses                                                  |
|--------------------------------|--------------------------------------------------|--------------------------------------------|--------------------------------|---------------------------------------------------------------|
| TfL GIS Open Data Hub          | London-wide transport networks and assets       | ArcGIS Hub layers; API discovery (RSS/DCAT/OGC Records) | OGL/TfL terms                  | TLRN streets, assets, bus/rail/cycle layers, boundaries       |
| London Datastore               | Citywide datasets incl. GeoJSON                 | CSV/GeoJSON and others                     | Varies by dataset (often OGL)  | Discovery of borough layers, citywide context, backups        |
| ONS Open Geography             | Administrative and statistical boundaries        | GIS boundary downloads                      | Open geography (ONS)           | Clipping, aggregation, joins, standard geographies            |

Analysts should combine these regional backbones with borough-level registers to produce a complete street layer for SE areas. This approach also mitigates gaps where boroughs do not publish street centerline datasets or where access requires an enquiry or registration. [^2][^3][^4]

---

## Borough Findings: Southwark (SE1, SE14, SE15, SE16, SE17)

Southwark publishes a modern data portal with Esri-backed mapping, robust planning and environmental datasets, and an interactive Spectrum Spatial interface that explicitly references the Local Street Gazetteer (LSG). Together, these routes support both thematic geospatial analysis and the extraction of authoritative street data.

Data portals and tools. Southwark Data provides themed datasets across children and young people, community safety, deprivation, economy and employment, environment, health and social care, housing, and population and equalities. The site enables downloads as reports, maps, and tables and supports postcode/ward search for quick profiles. Spectrum Spatial exposes council GIS layers directly to end users, including LSG-derived “A Roads,” “B Roads,” “C Roads,” and “Principal streets” layers. The council’s open data page confirms that datasets are published for reuse, with planning items such as Article 4 areas explicitly licensed under OGL. [^1][^5][^6][^9]

Street datasets and access. The fastest path to a street inventory is through Spectrum Spatial, where analysts can interact with LSG-derived layers and export or request data as appropriate. For spatial context layers—such as trees, Article 4 areas, and conservation boundaries—Southwark publishes downloadable datasets (e.g., GeoJSON for Article 4 areas) that can be used to enrich street-level analysis or to cross-reference planning constraints within SE postcode streets. The council also provides an interactive mapping interface for address and postcode searches that can assist with validation. [^5][^6][^8][^10]

Table 3. Southwark: street and street-related datasets

| Dataset/tool                         | What it covers                                      | Access method                         | Formats/notes                       | Update cadence (if known) |
|--------------------------------------|------------------------------------------------------|---------------------------------------|-------------------------------------|---------------------------|
| Local Street Gazetteer (via Spectrum) | Borough street network (A/B/C/Principal roads)       | Spectrum Spatial UI; request export   | Interactive; export by arrangement   | Not stated                |
| Article 4 areas                      | Planning constraint polygons                         | Open data page                        | GeoJSON; OGL                        | Not stated                |
| Tree dataset                         | Tree locations/attributes                             | Planning datasets page                | Data page indicates availability     | Not stated                |
| Interactive map (Southwark Maps)     | Address/postcode search and mapping                   | Interactive web map                   | UI-assisted validation               | Ongoing                   |

Practical access steps. Start with Spectrum Spatial to navigate LSG-derived layers for Southwark; where export options are not self-serve, contact the council to obtain LSG extracts or suitable centerline data for the SE postcodes of interest. Use the open data pages to download thematic planning and environment datasets to provide context on streets, particularly where planning constraints intersect street segments. For address-level validation, the interactive map provides a quick check. Confirm any reuse licensing on a per-dataset basis; planning datasets such as Article 4 areas are explicitly under OGL. [^1][^5][^6][^9][^10]

---

## Borough Findings: Lewisham (SE3, SE4, SE12, SE13)

Lewisham operates an open-data portal powered by SQLite databases and Datasette, exposing data via human-friendly interfaces and machine-readable JSON APIs. The Observatory provides ward profiles and thematic context, while the open-data site itself focuses on structured, queryable datasets.

Open Data Lewisham. The portal provides several street- or transport-relevant datasets. EV chargepoints are mapped and exposed with coordinates. Ward boundaries and statistical boundaries are available, and “Lookups” provide ONS codes for postcodes, output areas (OA), LSOA/MSOA, and wards. FixMyStreet issue history offers a long-run dataset of maintenance-related issues, which can enrich street segment analysis. Crucially, the site offers “APIs” and read-only databases queryable via SQL, with CSV/JSON exports supported through Datasette’s JSON API. [^11][^14]

Street-related data. The full Local Street Gazetteer is not surfaced publicly on the portal; analysts should request LSG/NSG extracts from the council for complete street coverage. EV chargepoints are accessible, and boundaries and lookup tables can be used to standardise geographies and joins. To understand flows and traffic context, the DfT Road Traffic website provides local authority statistics, including recent vehicle miles and count point information for Lewisham. [^11][^12][^15]

Table 4. Lewisham: street/transport-relevant datasets

| Dataset                               | Content                                  | Access method                   | Formats               | Notes/licensing                      |
|---------------------------------------|-------------------------------------------|---------------------------------|-----------------------|--------------------------------------|
| EV chargepoints                       | Mapped locations of chargepoints          | Portal; GIS map                 | CSV/JSON via Datasette | Confirm licensing on use             |
| Ward/statistical boundaries           | Boundary polygons and centroids           | Portal                          | Various               | For clipping and aggregation         |
| ONS lookups (postcode/OA/LSOA/MSOA)   | Code lists and mappings                    | Portal                          | Various               | Supports joins and standardisation   |
| FixMyStreet history                   | Issue history since 2007                  | Portal (Datasette)              | CSV/JSON via API      | Useful proxy for street maintenance  |
| Highway authority street gazetteer    | Official street list (LSG)                | Request from council            | CSV/GeoJSON (typical) | Not published on portal              |

Practical access steps. Use Datasette’s documented JSON API to query and export relevant tables in CSV/JSON for SE postcode coverage. Combine boundaries from the portal with ONS Open Geography layers for consistent spatial joins. Request LSG/NSG street data from the council for authoritative coverage. Optionally, layer DfT traffic statistics for context. [^11][^12][^14][^15][^4]

---

## Borough Findings: Greenwich (SE7, SE8, SE9, SE18)

Greenwich’s Data Observatory provides a hub for borough intelligence, while the council’s document repository offers a ready-to-use Road Register in both PDF and CSV. The site also publishes transport- and traffic-related downloads to support local analysis.

Data Observatory. The Observatory provides interactive ward profiles and thematic datasets across population, children and young people, health, housing, crime, deprivation, economy, and environment. Mapping is powered by Esri, indicating that geospatial layers underpin many Observatory tools. [^16]

Road Register. Greenwich’s Road Register is a list of all streets in the borough and can be downloaded immediately in PDF or CSV. The CSV is the most operationally useful for programmatic analysis and mapping and covers the SE7, SE8, SE9, and SE18 postcodes within Greenwich. [^17][^18][^19]

Supplementary transport downloads. The council publishes public transport documents and roadworks and traffic materials that can provide additional operational detail on streets, schemes, and temporary restrictions. [^20]

Table 5. Greenwich: Road Register download options

| Format | File size | Download reference | Notes                          |
|--------|-----------|--------------------|--------------------------------|
| PDF    | ~1.04 MB  | See reference [^18] | Human-readable register         |
| CSV    | ~294 KB   | See reference [^19] | Programmatically usable street list |

Practical access steps. Download the CSV Road Register to obtain an authoritative street list for Greenwich SE postcodes. Use the Data Observatory to enrich analysis with ward profiles and thematic context. Where geospatial centerlines are required, either integrate TfL layers or request an extract from the council as needed. [^16][^17][^18][^19][^20]

---

## Borough Findings: Westminster (SE11)

Westminster publishes a wide range of datasets via its corporate data hub and maintains a Digital Planning page aligned to national planning data standards. The council’s adoption of open digital planning has enhanced the automated publication of planning datasets.

Data hub and planning. The Data page aggregates links to facts and figures, ward profiles, census outputs, environmental measures, and air quality data. The Digital Planning Data page is a depositary for planning-related datasets consistent with national standards, including Article 4 areas, conservation areas, listed building datasets, and tree preservation orders. While these are not street centerlines per se, they provide critical spatial context for street segments in SE11 and across Westminster. [^21][^22][^23]

Street data availability. The reviewed materials do not explicitly list a street centerline or highway extent dataset for Westminster. Analysts should therefore either request the street gazetteer from the council or combine planning-related spatial data with regional backbones (TfL and GLA) for network coverage. The council’s active adoption of digital planning standards suggests a growing, more automated data publication environment. [^21][^22][^23]

Table 6. Westminster: relevant datasets for street-level analysis

| Dataset category                          | Relevance to streets                 | Access path                         |
|-------------------------------------------|--------------------------------------|-------------------------------------|
| Digital planning datasets (Article 4, conservation, listed buildings, TPOs) | Constraint and context along streets | Digital Planning page; per dataset  |
| Ward profiles and demographic/environmental indicators | Area-level context for SE11          | Data hub pages                      |
| Street centerline/highway extent          | Not explicitly listed                | Request via council data team        |

Practical access steps. Start with the Digital Planning data page to identify relevant planning layers for SE11. Use ward profiles and environmental data for area context. For the street network itself, contact the council to request the official gazetteer or suitable highway extent data. [^21][^22][^23]

---

## Borough Findings: Bexley (SE2)

Bexley publishes detailed highway authority records that classify streets by maintenance responsibility and provide status codes, last-updated dates, and supplementary scheme information. The borough also provides a one-stop Data Hub and an interactive Local Plan Policies Map, offering policy context for streets and development sites.

Highway authority records. The publicly maintained highway page defines and maintains lists of streets by responsibility: public (repairable), private, mixed, made-up, unmade, awaiting adoption, and TfL-maintained. Status codes (e.g., R, P, M, U, AA, TfL) and postal district codes (including SE2, SE9, SE18) support precise filtering and classification. The list of street names was last updated on 30 October 2023, with other lists updated on different dates. For detailed highway extent plans, the council offers a formal enquiry route with a published fee and typical response times. [^24][^26]

Data Hub and policy layers. The Data Hub centralises borough statistics and links to external sources for deeper analysis. The Local Plan Policies Map on ArcGIS Online provides a spatial representation of policy designations, which can be used alongside highway records to assess street segments in context of planning policies. [^25][^27]

Table 7. Bexley highway records: codes and coverage

| Code | Meaning                                             | SE areas (examples)                 | Last updated (examples)                 |
|------|-----------------------------------------------------|-------------------------------------|-----------------------------------------|
| R    | Repairable (maintained at public expense)           | SE2 (Abbey Wood), SE9 (Eltham), SE18 (Woolwich) | Street names list: 30 Oct 2023          |
| P    | Private (not maintained at public expense)          |覆盖 borough-wide                    |Street descriptions list: 9 July 2021     |
| M    | Made-up road (surfaced, suitable for vehicles)      |覆盖 borough-wide                    |Traffic schemes list: 29 Oct 2025         |
| U    | Unmade road (unsurfaced; may be unsuitable)         |覆盖 borough-wide                    |                                         |
| AA   | Awaiting Adoption (part or full)                    |覆盖 borough-wide                    |                                         |
| TfL  | Transport for London – highway authority            |TfL-controlled streets               |                                         |

Practical access steps. Use the highway records page to retrieve the current street list by responsibility and status, filtering by SE postal districts as needed. For detailed extent plans or specific highway geometry, submit a highways extent enquiry (fee applies) and expect a typical 5–7 working day response. For policy context, consult the Local Plan Policies Map. [^24][^26][^27]

---

## Access Playbook: Downloads, APIs, and Enquiry Routes

Street data access across SE London spans three archetypes: direct downloads, API-driven extraction, and request-based channels. The consolidated playbook below aligns channels to boroughs and indicates licensing terms where publicly stated.

- Direct downloads. Greenwich’s Road Register is available immediately in PDF and CSV. Southwark’s planning datasets (e.g., Article 4 areas) can be downloaded in standard spatial formats and are explicitly under OGL. [^17][^18][^19][^6]
- API-driven access. Lewisham’s portal uses Datasette atop SQLite, exposing read-only databases with a documented JSON API for querying and CSV/JSON exports. TfL’s GIS Hub provides open geospatial layers with programmatic discovery (RSS, DCAT, OGC API – Records), and the TfL Unified API offers access to real-time transport status across modes. [^11][^14][^2][^28]
- Request/enquiry-based channels. Southwark’s LSG and planning/geospatial items may require request for full gazetteer exports via Spectrum Spatial. Westminster does not surface street centerlines in reviewed materials; analysts should request the gazetteer from the council. Bexley provides a formal highways extent enquiry for detailed plans and specific geometry. [^5][^21][^26]

Licensing and reuse. Many TfL and GLA datasets are published under the Open Government Licence (OGL). Borough pages explicitly note OGL for certain planning items (e.g., Southwark Article 4). Where licensing is not stated, analysts should confirm on the dataset page or with the data owner before reuse. [^2][^3][^6]

Table 8. Access methods by borough and dataset

| Borough      | Dataset/collection                         | Method (download/API/UI/request) | Endpoint/tool reference         | Format(s)                | Notes/licensing                     |
|--------------|--------------------------------------------|----------------------------------|----------------------------------|--------------------------|-------------------------------------|
| Southwark    | Article 4 areas; trees; other planning     | Download                         | Open data pages                  | GeoJSON/other (per item) | OGL noted for planning items        |
| Southwark    | Local Street Gazetteer (LSG)               | UI + request                     | Spectrum Spatial                 | UI export/request        | Confirm LSG licensing on request    |
| Lewisham     | EV chargepoints; boundaries; lookups; FixMyStreet | API + download               | Open Data Lewisham (Datasette)   | CSV/JSON                 | Read-only DB; confirm terms         |
| Greenwich    | Road Register                              | Download                         | Road Register page               | PDF; CSV                 | Not specified here; confirm         |
| Westminster  | Digital planning datasets                  | Download                         | Digital Planning page            | Per dataset              | Not specified here; confirm         |
| Westminster  | Street centerline/highway extent           | Request                          | Council data team                | Per response             | Not listed; likely request          |
| Bexley       | Highway authority lists                    | Download + enquiry               | Highway records page; enquiry form | Web list; paid plans     | Confirm terms; fee for extent plans |
| Regional     | TfL GIS Hub (roads/assets/boundaries)      | Download/API                     | TfL GIS Hub                      | GIS layers; APIs         | OGL/TfL terms                       |
| Regional     | London Datastore (GeoJSON, etc.)           | Download                         | London Datastore                 | GeoJSON/other            | OGL (varies by dataset)             |
| Boundaries   | ONS Open Geography                         | Download                         | ONS portal                       | GIS boundary files       | Open geography                      |

This playbook emphasises speed where possible (Greenwich CSV), automation where supported (Lewisham APIs), and pragmatism where engagement is required (Southwark LSG, Westminster street layer, Bexley extent plans). [^17][^6][^11][^14][^21][^26][^2][^3][^4]

---

## Data Quality, Coverage, and Update Signals

Street datasets differ across boroughs in both structure and recency. Recognising these differences is key to producing reliable analysis.

Coverage and formats. Greenwich publishes a straightforward street list in both PDF and CSV, which is well-suited to immediate analysis and joining with other tabular or spatial data. Southwark prioritises a mapping-first approach via Spectrum Spatial for LSG-derived layers and uses open data pages for planning and environment layers that often provide rich spatial attributes. Lewisham’s data is delivered through APIs backed by SQLite, enabling robust programmatic workflows and repeatable extracts; however, the absence of a public LSG requires an alternative path for the official gazetteer. Bexley provides a coded list of streets by maintenance responsibility and a paid route to detailed extents, which is especially valuable for asset management and legal queries. Westminster’s planning datasets are mature and standardised, but the lack of an obvious street centerline dataset in the reviewed materials suggests an additional request will be needed for network geometry. [^17][^18][^19][^5][^11][^24][^22]

Update signals and cadence. Greenwich’s Road Register includes explicit publication metadata, with PDF and CSV sizes provided on the download page. Bexley’s highway records page displays last-updated dates for each list (e.g., street names updated 30 October 2023; traffic schemes updated 29 October 2025), offering clear signals for refresh. Southwark’s Spectrum Spatial is a live mapping environment; analysts should record the date of any extract and confirm currency with the data owner if precise timestamps are critical. Lewisham’s Datasette-backed site provides a modern publication model, but specific update frequencies vary by dataset. Westminster’s Digital Planning page reflects an active programme aligned to national standards, but street-layer update cadence is not stated in the reviewed materials and should be clarified. [^17][^18][^19][^24][^5][^11][^22]

Table 9. Update and versioning signals (where available)

| Borough      | Dataset                          | Last updated/published (signals)        | Format(s)         | Versioning notes                   |
|--------------|----------------------------------|-----------------------------------------|-------------------|------------------------------------|
| Greenwich    | Road Register                    | Publication metadata on download page   | PDF; CSV          | CSV recommended for programmatic use |
| Bexley       | Highway records (lists)          | Street names: 30 Oct 2023; traffic schemes: 29 Oct 2025 | Web list/documents | Multiple lists with different dates |
| Southwark    | LSG via Spectrum Spatial         | Live mapping interface (no explicit date) | UI export         | Confirm currency with data owner    |
| Lewisham     | Datasette-backed datasets        | Site-level signals vary per dataset     | CSV/JSON          | Read-only DB; note query limits     |
| Westminster  | Digital planning datasets        | Active programme (no street-layer cadence stated) | Per dataset       | Request street layer cadence         |

Finally, to interpret street datasets and align them to national conventions, it is helpful to understand the National Street Gazetteer (NSG) context. The NSG underpins streetworks, maintenance, and planning data sharing across England and Wales. Where borough portals do not expose LSG/NSG directly, analysts should engage custodians for authoritative coverage and for confirmation of licensing, update cadence, and any applicable fees. [^29][^30]

---

## Appendix: National Street Data Context and APIs

The National Street Gazetteer (NSG), provided through GeoPlace, is the definitive database of streets in England and Wales used for streetworks coordination, highway maintenance, and planning. Boroughs maintain their Local Street Gazetteers (LSG) in line with national conventions, and these datasets feed the NSG. When borough portals do not expose LSG/NSG data directly, analysts should expect to request extracts and to agree licensing and usage terms with the council or its appointed custodian. [^29]

GeoPlace also offers services such as DataVia, which provide programmatic access to street and address data, potentially useful when local portals are incomplete or lack particular attributes. DataVia represents an alternative route to obtain authoritative street data and related identifiers when council-provided open data is not immediately available. [^30]

Complementary APIs. For operational and network context, TfL’s Unified API provides real-time status across modes and can be used alongside the TfL GIS Open Data Hub for authoritative geometry. The ONS Open Geography portal provides the consistent boundary framework needed for robust spatial joins and area-based summaries. Together, these resources enable analysts to enrich borough street datasets with network, asset, and geographic context. [^28][^2][^4]

---

## References

[^1]: Southwark Data portal. https://data.southwark.gov.uk/  
[^2]: TfL GIS Open Data Hub. https://gis-tfl.opendata.arcgis.com/  
[^3]: London Datastore – GeoJSON format datasets. https://data.london.gov.uk/dataset/?format=geojson  
[^4]: ONS Open Geography Portal. https://geoportal.statistics.gov.uk/  
[^5]: Spectrum Spatial – Southwark Council. https://geomap.southwark.gov.uk/connect/analyst/mobile/  
[^6]: Article 4 areas dataset | Southwark Council. https://www.southwark.gov.uk/download-our-planning-datasets/article-4-areas-dataset  
[^8]: Tree dataset | Southwark Council. https://www.southwark.gov.uk/download-our-planning-datasets/tree-dataset  
[^9]: Open data | Southwark Council. https://www.southwark.gov.uk/about-council/transparency/freedom-information-data-protection-and-open-data/open-data  
[^10]: Interactive map | Southwark Council. https://www.southwark.gov.uk/interactive-map  
[^11]: Open Data Lewisham portal. https://lb-lewisham.github.io/open-data-lewisham/  
[^12]: Lewisham Observatory. https://www.observatory.lewisham.gov.uk/  
[^14]: Datasette JSON API documentation. https://docs.datasette.io/en/stable/json_api.html  
[^15]: DfT Road Traffic – Lewisham local authority. https://roadtraffic.dft.gov.uk/local-authorities/E09000023  
[^16]: Royal Greenwich Data Observatory. https://dataobservatory.royalgreenwich.gov.uk/  
[^17]: Road register | Royal Borough of Greenwich. https://www.royalgreenwich.gov.uk/downloads/download/861/road_register  
[^18]: Royal Borough of Greenwich road register (PDF). https://www.royalgreenwich.gov.uk/download/downloads/id/3575/royal_borough_of_greenwich_road_register.pdf  
[^19]: Royal Borough of Greenwich road register (CSV). https://www.royalgreenwich.gov.uk/download/downloads/id/3576/royal_borough_of_greenwich_road_register_csv.csv  
[^20]: Public transport downloads – Royal Borough of Greenwich. https://www.royalgreenwich.gov.uk/downloads/200260/public_transport  
[^21]: Data | Westminster City Council. https://www.westminster.gov.uk/about-council/data  
[^22]: Digital Planning Data | Westminster City Council. https://www.westminster.gov.uk/planning-building-control-and-environmental-regulations/digital-planning-data  
[^23]: Westminster City Council – Digital planning improvement (case study). https://opendigitalplanning.org/insights/case-study/westminster-city-council-digital-planning-improvement  
[^24]: Publicly maintained highway – London Borough of Bexley. https://www.bexley.gov.uk/services/parking-transport-and-streets/highway-records/publicly-maintained-highway  
[^25]: Bexley Data Hub overview. https://www.bexley.gov.uk/discover-bexley/bexley-data-hub/what-data-hub  
[^26]: Highways extent enquiry form – London Borough of Bexley. https://www.bexley.gov.uk/services/parking-transport-and-streets/highways-extent-enquiry-form  
[^27]: Bexley Local Plan Policies Map (ArcGIS Online item). https://www.arcgis.com/home/item.html?id=47d8febb1093429f964cf6500d0c691e  
[^28]: TfL Unified API documentation. https://tfl.gov.uk/info-for/open-data-users/api-documentation  
[^29]: GeoPlace: National Street Gazetteer overview. https://www.geoplace.co.uk/addresses-streets/street-data-and-services/national-street-gazetteer  
[^30]: GeoPlace DataVia API (street data services). https://www.geoplace.co.uk/addresses-streets/street-data-and-services/datavia-api

---

## Information gaps to address

- Southwark: explicit, self-serve download links for a full Local Street Gazetteer or street centerline layer via the public portal were not identified; extraction via Spectrum Spatial or request is likely. [^5]
- Lewisham: official Local Street Gazetteer access via an open, documented endpoint is not surfaced; dataset appears SQLite/Datasette-based with various geodata, but public LSG/NSG extraction is unclear. [^11]
- Westminster: no explicit street dataset download found; planning and transport data are present, but street centerline or highway extent data are not listed in reviewed materials. [^21][^22]
- Greenwich: Road Register is well-documented (PDF/CSV); whether an OpenGIS-ready street centerline file is provided remains unclear. [^17][^18][^19]
- Licensing specifics: Southwark planning datasets indicate OGL; other borough licensing statements for street/highway datasets were not explicitly stated in the reviewed materials. [^6]
- Update cadences: Greenwich provides clear download pages, but update frequency for the Road Register is not explicitly stated; Westminster and Southwark do not state update cadences for street layers in reviewed materials. [^17][^18][^19][^21][^22][^5]