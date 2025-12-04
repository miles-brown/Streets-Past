# UK Street Name Mapping Solutions: Cost, Performance, and Integration Blueprint

## Executive Summary

Engineering teams building UK street name visualization and search face three recurring constraints: basemap tile capacity and policy, geocoding throughput and storage rights, and client rendering performance at scale. The OpenStreetMap Foundation’s “standard” raster tiles are not designed for commercial-grade reliability and come with strict usage policies; they must not be used for production traffic without dedicated hosting or a commercial provider. For geocoding, the OSMF public instance of Nominatim allows only occasional use (about 1 request per second) and explicitly cautions against relying on it for paid applications; persistent storage and bulk autocomplete require either a commercial API or self-hosting. On the client side, MapLibre GL JS (WebGL) is better suited than Leaflet (DOM) for large point datasets and dynamic vector styling, especially when performance patterns such as clustering, tiling, and attribute reduction are applied.

Top-line recommendations are as follows. For basemaps, adopt a commercial tile provider. MapTiler and Stadia Maps both offer straightforward pricing, generous quotas, and soft-limit overage mechanics that support production scale and cost predictability; MapTiler provides explicit per-request accounting and transparent overage rates, while Stadia’s credit system covers tiles, geocoding, and routing with low overage costs and a sizable non-commercial free tier.[^11][^14] For geocoding, LocationIQ offers a generous free plan and soft daily limits suitable for early-stage and medium scale; OpenCage provides clear daily quotas, soft limits on subscriptions, and permissive storage rights; Nominatim should be self-hosted for any sustained or commercial workload given its public API policy and limits.[^7][^5][^3] For rendering, choose MapLibre GL JS as the default when plotting 1M+ points or dynamically restyling vector layers; reserve Leaflet for simpler maps or raster tile overlays.[^15][^16][^17][^18][^19]

At-a-glance limits and pricing highlights:
- OSM tiles: No numeric rate limits are published; policy prohibits heavy uses (pre-seeding, high-zoom scraping, offline caching). Commercial users are advised to use third-party providers; service is best-effort without SLA.[^1]
- Nominatim: Public usage about 1 request per second; bulk geocoding discouraged; self-hosting recommended for larger or critical workloads.[^3][^4]
- OpenCage: Free trial 2,500 requests/day at 1 rps; subscriptions with daily quotas (10k/day, 30k/day, 125k/day, 300k/day), soft limits on paid tiers, and storage allowed; paid tiers have typical rate limits up to 40 rps.[^5]
- LocationIQ: Free plan 5,000 requests/day, 2 rps, 60 rpm; paid plans include soft daily limits (up to +100%) and soft monthly limits on higher tiers; caching and storage vary by plan.[^7][^8]
- MapTiler: Free 5,000 sessions and 100,000 requests/month (pauses when exceeded); Flex $25 for 25k sessions and 500k requests with $0.10/1k overage; Unlimited $295 for 300k sessions and 5M requests with $0.08/1k overage; Custom contract available.[^11][^12][^13]
- Stadia Maps: Free 200k credits/month (non-commercial), Starter $20 for 1M credits with $0.03/1k overage, Standard $80 for 7.5M credits with $0.02/1k overage, Professional $250 for 25M credits with $0.015/1k overage.[^14]

To illustrate these constraints and options concisely, Table 1 summarizes the core tile and geocoding policies and pricing.

### Table 1. Constraints at a glance: OSM tiles policy and Nominatim limits; MapTiler vs Stadia pricing; geocoding free tiers

| Topic | Key Policy/Limit | Notes | Source |
|---|---|---|---|
| OSM tiles | Best-effort; no numeric rate limits | Prohibits heavy uses; caching headers must be honored; commercial users advised to use third-party providers | [^1] |
| Nominatim (public) | ~1 request/second; bulk discouraged | Caching required; self-hosting recommended for larger or critical workloads | [^3][^4] |
| MapTiler | Free 5k sessions + 100k req; Flex 25k + 500k at $25; Unlimited 300k + 5M at $295 | Overage $0.10/1k (Flex) and $0.08/1k (Unlimited); pausing on Free when exceeded | [^11][^12][^13] |
| Stadia Maps | Free 200k credits; Starter 1M at $20; Standard 7.5M at $80; Professional 25M at $250 | Overage $0.03/1k, $0.02/1k, $0.015/1k respectively | [^14] |
| OpenCage | Free 2,500/day at 1 rps; paid daily quotas (10k to 300k/day) | Soft limits on subscriptions; permanent storage allowed; priority support on paid | [^5] |
| LocationIQ | Free 5,000/day at 2 rps, 60 rpm; paid soft daily/monthly limits | Free plan requires prominent link-back; caching rules differ by plan | [^7][^8] |

Known information gaps relevant to planning: Mapbox’s current pricing and limits; Thunderforest and Carto quotas; MapTiler’s complete free-tier session definitions beyond headline numbers; official Leaflet benchmarks at 1M+ points; UK-specific accuracy metrics for OpenCage/LocationIQ; and granular UK government OS Places pricing and quotas beyond high-level summaries.[^27][^22][^11][^18][^26][^28][^29]

### Key Takeaways

Do not use OSMF’s public standard tile servers for production or commercial traffic. Their purpose and capacity are not SLA-backed; violations can lead to blocking without notice, and heavy uses such as pre-seeding or high-zoom scraping are prohibited.[^1]

For geocoding, self-host Nominatim or choose a commercial API if you need reliable throughput, persistent storage, autocomplete, or batch processing. The OSMF public instance enforces strict rate limits and discourages heavy uses.[^3][^4]

Prefer MapLibre GL JS for rendering UK street name overlays and large point datasets. It leverages WebGL for high-performance vector rendering and offers mature patterns for large-data optimization (clustering, tiling, attribute reduction).[^15][^16]

### Recommendations Snapshot

Use MapTiler or Stadia for basemaps. MapTiler provides straightforward monthly request quotas and transparent per-1,000 overage pricing; Stadia offers broad API coverage and generous credits across maps, geocoding, and routing with low overage rates.[^11][^14]

Combine MapLibre GL JS with PostGIS-backed queries. Tiles and vector layers should be sourced from a commercial provider; client-side rendering should use clustering and zoom-bound rendering for scalability; backend spatial search should rely on index-aware predicates such as ST_Intersects and ST_DWithin.[^16][^20][^21]

Select geocoding by scale and use-case. LocationIQ’s free plan and soft daily limits support early-stage builds; OpenCage offers permissive storage and predictable daily quotas; for postal-grade UK address validation with Unique Property Reference Numbers (UPRN), use OS Places or UK PAF-backed providers.[^7][^5][^26]

## Scope, Assumptions, and Success Criteria

This blueprint targets interactive visualization of UK street names at city to national scale, supporting search, hover tooltips, and click-to-identify flows. We assume a client web application with a backend database and APIs, targeting modern browsers, with potential for server-side prerender of tiles or vector layers. The goal is to balance cost-efficiency and performance while respecting licensing terms and usage policies for tiles and geocoding.

Success is defined as consistent map interactivity at UK national scale, compliant tiling and geocoding, predictable monthly costs, and client frame rates sufficient for smooth pan and zoom with clustering and symbol overlays. Data attribution must follow the Open Database License (ODbL) and provider guidelines.[^2]

## Foundations: UK Street Data and Search Semantics

Street name visualization relies on retrieving named linear features from OpenStreetMap (OSM) and related datasets. The semantic distinction matters: searching for a street name differs from geocoding a fully specified address. Nominatim, OSM’s geocoding software, can resolve place names and addresses and supports forward and reverse geocoding endpoints; however, it is not intended as a high-throughput, persistent store for autocomplete or large-scale batch processing on its public instance.[^4]

In the UK, postal-grade address validation is typically handled via the Postcode Address File (PAF) and AddressBase, with Unique Property Reference Numbers (UPRN) enabling persistent linkage across government and commercial datasets. Ordnance Survey (OS) Places API provides gold-standard address coverage with UPRN and is frequently accessed by the public sector via the Public Sector Geospatial Agreement (PSGA). Private-sector applications often use PAF-backed providers (for example, Ideal Postcodes, getAddress.io, Loqate) for capture and validation workflows. These UK-specific sources achieve rooftop-level precision and daily updates, supporting address resolution workflows where the cost of misclassification is high (new builds, rural addresses, flats).[^26][^28][^29]

OpenStreetMap data under ODbL is free to use, with attribution and share-alike obligations for derived databases. Teams should ensure visible attribution (“© OpenStreetMap contributors”) and track data provenance when mixing OSM and commercial sources.[^2]

### Data Model & Indexing Basics

Street geometries are typically modeled as linestrings with names and metadata. Efficient queries depend on spatial indexes and index-aware predicates. In PostGIS, spatial GiST indexes accelerate bounding box operators such as && and distance operators like <-> for nearest-neighbor, while predicates such as ST_Intersects, ST_Contains, and ST_DWithin are index-aware when used correctly. Avoid non-index-aware functions like raw ST_Distance in WHERE clauses on large tables; instead, use ST_DWithin to constrain the search radius, which internally leverages bounding box prefiltering to use the spatial index effectively.[^20][^21]

## OpenStreetMap Tiles: Policy, Costs, and Operational Reality

The OSMF “standard” raster tile service is community-funded and designed for occasional use, not commercial-grade workloads. The policy emphasizes normal interactive viewing, strict adherence to caching headers, and avoidance of heavy uses. There are no published numeric rate limits; violations such as pre-seeding tiles, automated scraping at high zoom, or offline caching features trigger blocking without notice. The service does not provide an SLA, and commercial users are advised to use third-party providers or self-host tiles. The scope applies to the standard raster tiles at tile.openstreetmap.org, not vector tiles or other layers.[^1][^25]

### Table 2. OSM tile usage policy: permitted vs prohibited behaviors

| Behavior | Status | Notes | Source |
|---|---|---|---|
| Normal interactive viewing (viewport + modest look-ahead) | Permitted | Respect caching headers; conditional requests required | [^1] |
| Caching tiles locally | Permitted (with rules) | Honor Cache-Control; if headers unreadable, cache ≥7 days; no “no-cache” | [^1] |
| Pre-seeding large areas | Prohibited | Building tile archives or seeding is blocked | [^1] |
| High-zoom automated scans (z≥14) | Prohibited | Headless bots and forcing renders are blocked | [^1] |
| Offline use features | Prohibited | “Download city for offline use” disallowed | [^1] |
| Commercial usage | Not prohibited, but cautioned | Service not designed for reliability; commercial users should use third parties | [^1] |

### Production Readiness and Cost Implications

For production, plan for commercial tile hosting or self-hosting. MapTiler and Stadia Maps offer straightforward pricing, generous quotas, and soft-limit mechanics that mitigate surprise bills while enabling scale. MapTiler’s pricing converts API usage into explicit request units by service type (for example, vector tiles, raster tiles, static maps), with overage rates per 1,000 requests. Stadia uses a credit system covering maps, geocoding, routing, and data APIs, with per-1,000 overage rates decreasing at higher tiers.[^11][^14]

#### Table 3. Cost planning scenarios: MapTiler vs Stadia (illustrative monthly usage)

| Monthly Usage Scenario | MapTiler Plan Fit | MapTiler Overage Est. | Stadia Plan Fit | Stadia Overage Est. | Notes | Source |
|---|---|---|---|---|---|---|
| 500k map requests | Flex: 500k included | $0 (within 500k) | Starter: 1M credits | $0 (within 1M) | Raster/vector request accounting differs; MapTiler counts service units explicitly | [^11][^14] |
| 6M map requests | Unlimited: 5M included | ~$80 (1M overage × $0.08/1k) | Standard: 7.5M credits | $0 (within 7.5M) | Stadia’s credit pool may be more flexible for mixed APIs | [^11][^14] |
| 25M mixed API calls (tiles + geocoding + routing) | Unlimited: 5M requests | ~$1,600 (20M overage × $0.08/1k) | Professional: 25M credits | $0 (within 25M) | Stadia’s single credit simplifies accounting across products | [^11][^14] |
| 50M mixed API calls | Custom contract | Negotiated | Professional + overage | ~$375 (25M base + 25M overage × $0.015/1k) | At extreme scale, Custom contract or tier upgrade advised | [^11][^14] |

The OSM US tile service offers a free, low-volume non-commercial option that can support hobbyist usage; however, production-grade workloads should adopt paid providers for SLA, capacity, and compliance.[^24]

## Client-Side Mapping: MapLibre GL JS Integration

MapLibre GL JS is a TypeScript library that uses WebGL to render vector tiles and GeoJSON layers with dynamic styling. Integration patterns include adding vector or raster sources, custom layers, markers, and symbol layers for labels; clustering for dense points; and controls for navigation, fullscreen, geolocation, and scale. Performance guidance emphasizes making files smaller (reduce properties and coordinate precision), geometry simplification, chunking or streaming data, and converting large GeoJSON into vector tiles. For server-side vector tiling, Martin can expose PostGIS data as tiles, enabling efficient delivery to clients.[^15][^16][^30][^31]

### Table 4. MapLibre GL JS performance tactics: techniques and expected benefits

| Technique | Where to Apply | Expected Benefit | Notes | Source |
|---|---|---|---|---|
| Remove unused properties | Data prep | Lower payload and memory | Streamline features; reduce JSON size | [^16] |
| Reduce coordinate precision | Data prep | Smaller payloads without visible loss | ~6 decimal places is typically sufficient | [^16] |
| Simplify geometries | Data prep | Faster parse and render | Use Mapshaper or Turf for simplification | [^16] |
| Chunk large datasets | Loading | Lower main-thread blocking | Split by area or update cadence | [^16] |
| Stream on interaction | Loading | Reduced initial load | Load subsets as user pans/zooms | [^16] |
| Vector tiling (GeoJSON → MVT) | Data prep/Server | Efficient rendering at scale | Use Martin to tile PostGIS | [^16][^30][^31] |
| Clustering | Visualization | Fewer DOM/WebGL objects | Configure cluster radius and max zoom | [^16] |
| Disable overlap calculations | Visualization | Reduced compute | Icon/text layout allow-overlap | [^16] |
| Set min/max zoom on layers | Visualization | Constrain rendering cost | Avoid rendering at low zooms where dense | [^16] |

#### Integration Patterns for UK Street Names

Render street name labels via a symbol layer backed by a vector tile source, with clustering enabled for point features and min/max zoom bounds to avoid rendering at low zooms where symbols would be unreadable. Apply layout properties such as icon-allow-overlap to reduce layout computation when collision checks are unnecessary. For search results and hover tooltips, use popups anchored to symbols; for click-to-identify flows, rely on query rendering callbacks and symbol filters to retrieve feature attributes. Client-side performance patterns (chunking, tiling) should be paired with backend filters that return only relevant features per viewport.[^16]

## Geocoding APIs: OpenCage, LocationIQ, and Nominatim

Geocoding selection hinges on rate limits, storage rights, autocomplete support, and commercial terms. OpenCage provides clear daily quotas on paid tiers, soft limits for subscriptions, and permissive storage; LocationIQ offers a generous free plan, soft daily limits, and tiered caching rules; Nominatim’s public API is appropriate only for occasional use, with bulk and autocomplete discouraged.

### Table 5. Geocoding free-tier comparison

| Provider | Free Tier Requests | Rate Limit | Caching/Storage | Commercial Use | Notable Notes | Source |
|---|---|---|---|---|---|---|
| OpenCage | 2,500/day | 1 rps | Permanent storage allowed | Testing only | Paid tiers have daily quotas and soft limits | [^5][^6] |
| LocationIQ | 5,000/day | 2 rps, 60 rpm | Free: cache up to 48 hours; Paid: store while customer | Free requires prominent link-back | Soft daily limits up to +100% on many paid plans | [^7][^8] |
| Nominatim (public) | ~1 rps (policy) | ~1 rps | Caching required; storage allowed under ODbL | Permitted but cautioned | Bulk/autocomplete discouraged; self-host for larger needs | [^3][^4][^2] |

#### OpenCage Details

OpenCage’s free trial allows 2,500 requests/day at 1 rps, intended for testing. Paid plans start at $50/month for 10,000 requests/day and 15 rps, rising to 300,000 requests/day and 40 rps at $1,000/month; all subscriptions use soft limits, and permanent storage is permitted. Enterprise options include dedicated instances and custom SLAs.[^5][^6]

#### LocationIQ Details

LocationIQ’s free plan provides 5,000 requests/day, 2 rps, and 60 rpm, with commercial use allowed if a prominent link-back is displayed. Paid plans expand daily/monthly quotas, often with soft limits permitting up to an additional 100% of the daily limit; caching and storage policies vary by plan, with paid plans allowing longer or permanent storage of geocode responses.[^7][^8][^9]

#### Nominatim Usage Limits and Self-Hosting

The OSMF public Nominatim instance limits usage to about 1 request per second and discourages bulk geocoding and autocomplete. Results must be cached, and applications should be able to switch services on request. For higher throughput or persistent autocomplete, self-hosting is recommended; Nominatim supports minutely updates and scales from city-sized imports to planet-wide deployments.[^3][^4]

## PostGIS Spatial Queries for Street Location Searches

Backend search should rely on proven spatial predicates. Use ST_Intersects for spatial joins and filtering by viewport or polygon; ST_Contains and ST_Within for containment; and ST_DWithin for radius-based searches with index awareness. Ensure GiST indexes on geometry columns and use bounding box operators for efficient filtering. Avoid non-index-aware predicates in WHERE clauses, and examine query plans to verify index usage.

### Table 6. PostGIS predicate cheat-sheet for street search

| Predicate | Typical Use | Index-Aware | Example Use Case | Source |
|---|---|---|---|---|
| ST_Intersects | Viewport or polygon filter | Yes | Return streets intersecting current map bounds | [^20] |
| ST_Contains | Containment (polygon contains geometry) | Yes | Find streets fully within a district polygon | [^20] |
| ST_Within | Containment (geometry within polygon) | Yes | Filter streets within a local authority boundary | [^20] |
| ST_DWithin | Radius search | Yes | Find streets within 200m of a point | [^20][^21] |
| ST_Covers / ST_CoveredBy | Coverage predicates | Yes | Alternative to contains/within with edge cases | [^20] |
| && (bounding box) | Prefilter | Yes | Fast bbox check before precise predicates | [^21] |
| <-> (distance operator) | Nearest neighbor | Yes | Locate nearest street segment to an address point | [^21] |

#### Optimization Patterns

Combine bounding box operators with precise predicates to reduce scanned rows, then apply ST_DWithin to leverage indexes for distance queries. Use materialized views for common search areas (for example, city or local authority extents) to avoid recomputing heavy filters. Always verify index usage via EXPLAIN and tune thresholds for clustering and min/max zoom rendering on the client to minimize server response sizes.[^21][^20]

## Performance at Scale: Leaflet vs MapLibre GL JS with 1M+ Street Markers

At scale, rendering technology determines user experience. Leaflet uses HTML/CSS/JS and is ideal for simpler maps and raster overlays, but its DOM-based markers struggle as feature counts climb into the hundreds of thousands to millions. MapLibre GL JS leverages GPU acceleration and is designed for dynamic vector styling, large datasets, and smooth animations. While there is no single official benchmark across both libraries at exactly 1M points, community guidance and performance analysis consistently show MapLibre’s superiority for data-heavy visualizations.[^17][^18][^19]

### Table 7. Leaflet vs MapLibre GL JS: capability comparison

| Criterion | Leaflet | MapLibre GL JS | Implications | Source |
|---|---|---|---|---|
| Rendering | DOM-based | WebGL/GPU | MapLibre scales better with large point sets | [^17][^18][^19] |
| Data format | Raster tiles + GeoJSON | Vector tiles + GeoJSON | Vector allows dynamic styling and efficient payloads | [^15][^16] |
| Performance | Lightweight but limited at high counts | High performance for large datasets | Prefer MapLibre for 1M+ markers | [^17][^18][^19] |
| Clustering | Plugins | Native clustering options | Both support clustering; MapLibre scales further | [^16][^17] |
| Learning curve | Simpler | Steeper | Leaflet easier for basic needs | [^17] |

#### Optimization Strategies for 1M+ Markers

Use clustering to reduce the number of rendered objects; set cluster radius and max zoom to align with readability. Convert large datasets into vector tiles and serve them via a tile server (for example, Martin) to avoid shipping monolithic GeoJSON payloads. Apply attribute reduction and coordinate simplification, and stream subsets on pan/zoom interactions to keep payloads and memory footprints manageable.[^16]

## Tile Server Alternatives: MapTiler and Stadia Maps

MapTiler and Stadia Maps both deliver reliable production hosting and predictable billing, with integration paths for MapLibre GL JS and raster tiles in Leaflet.

### Table 8. Side-by-side pricing and quotas

| Provider | Plan | Monthly Cost | Included Requests/Credits | Overage Rate | Commercial Use | SLA | Source |
|---|---|---|---|---|---|---|---|
| MapTiler | Free | $0 | 5,000 sessions + 100,000 requests | N/A (pauses) | No | None | [^11][^12][^13] |
| MapTiler | Flex | $25 | 25,000 sessions + 500,000 requests | $0.10 per 1,000 requests | Yes | None | [^11][^12][^13] |
| MapTiler | Unlimited | $295 | 300,000 sessions + 5,000,000 requests | $0.08 per 1,000 requests | Yes | 99.9% | [^11][^13] |
| MapTiler | Custom | Contract | Custom | No automatic overage bills | Yes | Custom | [^11][^13] |
| Stadia Maps | Free | $0 | 200,000 credits | N/A | No (non-commercial) | None | [^14] |
| Stadia Maps | Starter | $20 | 1,000,000 credits | $0.03 per 1,000 credits | Yes | None | [^14] |
| Stadia Maps | Standard | $80 | 7,500,000 credits | $0.02 per 1,000 credits | Yes | None | [^14] |
| Stadia Maps | Professional | $250 | 25,000,000 credits | $0.015 per 1,000 credits | Yes | None | [^14] |

### Table 9. Credit/request cost mapping examples

| Usage Pattern | MapTiler Request Accounting | Stadia Credit Cost | Notes | Source |
|---|---|---|---|---|
| Vector tile | 1 request per tile | 1 credit per tile | MapTiler lists explicit request conversions by service | [^11][^14] |
| Raster tile (256) | 1 request per tile | 1 credit per tile | Retina/HiDPI variants count more in MapTiler | [^11][^14] |
| Static map image | ~15 requests per image | 20 credits per request | Accounting differs by provider | [^11][^14] |
| Geocoding call | 1 request | 20 credits (typical forward/reverse) | Stadia’s credits unify maps + geocoding + routing | [^14] |

#### Cost Scenarios and Break-Even Planning

To plan budgets, map typical monthly usage to plans and overage. For mixed workloads (tiles, geocoding, routing), Stadia’s unified credits simplify accounting; MapTiler’s explicit service-unit pricing aids granular cost control. Enable spending limits and alerts to avoid surprise bills, and consider a Custom contract for extreme volumes.[^11][^14]

### Table 10. Example monthly budgets (illustrative)

| Scenario | MapTiler Fit and Overage | Stadia Fit and Overage | Commentary | Source |
|---|---|---|---|---|
| 3M tile requests (vector) + 300k geocodes | Flex/ Unlimited mix → ~$240–$320 | Standard → within 7.5M credits | Stadia likely simpler; MapTiler transparent per-service | [^11][^14] |
| 10M mixed API calls | Unlimited + overage → ~$800+ | Professional + overage → ~$150–$200 | Stadia overage cheaper at high scale | [^11][^14] |
| 50M mixed API calls | Custom contract | Professional + overage → ~$375 | Negotiate MapTiler; confirm SLA needs | [^11][^14] |

## Implementation Blueprint: UK Street Names Visualization and Search

The end-to-end architecture comprises client rendering with MapLibre GL JS, a PostGIS-backed query API, and commercial tile hosting, with geocoding selected per workload and compliance requirements. Attribution must be visible and persistent per ODbL and provider guidelines. Operational concerns include rate limiting, caching, observability, and cost controls.

### Table 11. Implementation checklist

| Area | Checklist Item | Purpose | Source |
|---|---|---|---|
| Tiles | Select provider (MapTiler/Stadia) | SLA-backed capacity, predictable billing | [^11][^14] |
| Tiles | Configure TileJSON/Style JSON | Basemap and vector style integration | [^30][^23] |
| Client | Add MapLibre map, sources, layers | Vector rendering with symbols | [^15][^16] |
| Client | Enable clustering and zoom bounds | Scalability for 1M+ markers | [^16] |
| Data | Prepare vector tiles (Martin) | Efficient large-data delivery | [^30][^31] |
| Backend | Index geometry (GiST) | Fast spatial queries | [^20][^21] |
| Backend | Implement ST_Intersects/ST_DWithin | Viewport and radius search | [^20] |
| Geocoding | Choose provider (OpenCage/LocationIQ/Nominatim self-host) | Throughput and storage compliance | [^5][^7][^3][^4] |
| Compliance | Implement attribution and caching headers | ODbL and provider policy adherence | [^2][^1] |
| Operations | Set rate limits and backoff | API resilience | [^7][^5] |
| Operations | Observability: logs, metrics, traces | Reliability and cost control | N/A |
| Cost | Spending limits and alerts | Avoid surprise bills | [^11][^14] |

### Minimal Viable Stack

A pragmatic MVP for UK street visualization uses MapTiler Flex or Stadia Starter for basemaps, MapLibre GL JS for client rendering, and LocationIQ’s free plan for geocoding. This combination provides capacity for moderate traffic, soft-limit headroom for spikes, and permissive caching/storage on paid geocoding tiers as the application grows.[^11][^14][^7]

### Production-Ready Stack

For production-grade workloads, adopt MapTiler Unlimited or Stadia Standard/Professional, combine OpenCage paid tiers or LocationIQ’s higher plans for geocoding with soft-limit protections, and self-host Nominatim if persistent autocomplete or bulk geocoding is required. On the backend, use PostGIS with index-aware predicates and materialized views. Operationally, implement rate limiting, robust caching, observability, and budget controls with alerts.[^11][^14][^5][^3][^20]

## Risk, Compliance, and Licensing

Compliance spans tile policies, geocoding terms, and ODbL attribution. OSMF’s tile service is not SLA-backed and can block violating clients without notice; production traffic should use commercial providers or self-host tiles. Geocoding providers enforce rate limits and storage terms; OpenCage allows permanent storage on paid tiers, LocationIQ differentiates caching durations by plan, and Nominatim’s public instance requires caching and disallows heavy uses. Under ODbL, visible attribution is mandatory and derivative data obligations apply.[^1][^5][^7][^3][^2]

### Table 12. Compliance matrix

| Component | Policy | Key Limits | Required Actions | Risk if Violated | Source |
|---|---|---|---|---|---|
| OSM tiles | Tile usage policy | Heavy uses prohibited; caching rules | Honor headers; visible attribution | Blocking without notice; unreliability | [^1] |
| Nominatim (public) | Usage policy | ~1 rps; bulk discouraged | Cache results; able to switch services | Access withdrawn; unstable for paid use | [^3] |
| OpenCage | Pricing/ToS | Daily quotas; soft limits on paid | Permanent storage allowed on paid; respect rps | Throttling; account review | [^5][^6] |
| LocationIQ | Pricing/ToS | Free plan link-back; soft daily limits | Follow caching/storage per plan | 429 rate limiting; account review | [^7][^8] |
| ODbL | Licensing | Attribution; share-alike | Display “© OpenstreetMap contributors” | Legal exposure | [^2] |

## Recommendations and Phased Rollout

For a proof of concept, use the OSM US tile service (low-volume, non-commercial) alongside MapLibre GL JS and LocationIQ’s free tier to validate UX and query patterns. For minimum viable production, adopt MapTiler Flex or Stadia Starter for tiles and a geocoding paid plan for soft-limit headroom and storage rights. For full-scale production, select MapTiler Unlimited or Stadia Professional, implement PostGIS spatial indexing and materialized views, and consider self-hosting Nominatim for autocomplete and bulk processing. Set monthly budget thresholds and enable alerts to cap overage exposure.[^24][^11][^14][^5][^3]

### Table 13. Phased rollout plan

| Phase | Goals | Providers | Monthly Budget Target | Scale Tests | Compliance Checks | Source |
|---|---|---|---|---|---|---|
| POC | Validate UX, labels, search | OSM US tiles; MapLibre; LocationIQ Free | $0–$50 | Pan/zoom with clustering; 100k markers | Attribution; geocoding rate limits | [^24][^7] |
| MVP | Production pilot | MapTiler Flex or Stadia Starter; LocationIQ Paid | $50–$150 | 500k markers; soft-limit spikes | Caching/storage terms; spending limits | [^11][^14][^7] |
| Production | National scale | MapTiler Unlimited or Stadia Professional; OpenCage/LocationIQ Paid; Self-host Nominatim | $300–$800+ | 1M+ markers; vector tiles; backend filters | ODbL attribution; tile policy; geocoding ToS | [^11][^14][^5][^3][^2] |

## Appendices

### Appendix A: MapTiler request accounting table (selected)

| Service | Request Count | Notes | Source |
|---|---|---|---|
| TileJSONs / Style JSONs / Fonts / Viewers / XMLs | Free | Metadata endpoints | [^11] |
| Vector tile | 1 | Core vector request unit | [^11] |
| Raster tile 512×512 (HiDPI) | 4 | Retina accounting | [^11] |
| Raster tile 256×256 | 1 | Standard raster tile | [^11] |
| Static maps API image | 15 | Billed as composite | [^11] |
| Vector data (GeoJSON) | 1 | Data API unit | [^11] |
| Search & Geocoding | 1 | Per call | [^11] |
| Elevation | 1 | Per call | [^11] |
| Coordinates API | 1 | Per call | [^11] |
| Export | 50× | Heavy export unit | [^11] |

### Appendix B: Stadia Maps credit costs (selected)

| API | Credit Cost | Notes | Source |
|---|---|---|---|
| Standard Vector/Raster basemaps | 1 per tile | Core map rendering | [^14] |
| Satellite imagery | 4 per tile | Higher-resolution raster | [^14] |
| Static maps | 20 per request | Additional for cacheable variant | [^14] |
| Autocomplete v2 | 1 per request | Cost-efficient newer version | [^14] |
| Forward/Reverse geocoding | 20 per request | Per call | [^14] |
| Routing (standard) | 20 per request | Core routing | [^14] |
| Time zones / Elevation | 5 per request | Data APIs | [^14] |

### Appendix C: Geocoding request allowance and rate limits (selected)

| Provider | Free Requests | Paid Quotas | Rate Limits | Storage/Caching | Source |
|---|---|---|---|---|---|
| OpenCage | 2,500/day (free) | 10k–300k/day (paid) | Up to ~40 rps | Permanent storage (paid) | [^5][^6] |
| LocationIQ | 5,000/day (free) | 25k/day to millions/month (paid) | ~2–40 rps by tier | Free: cache ≤48h; Paid: store while customer | [^7][^8] |
| Nominatim (public) | ~1 rps | Self-host for more | ~1 rps | Caching required; ODbL storage allowed | [^3][^4][^2] |

### Appendix D: PostGIS example queries for street search

- Streets intersecting viewport polygon:
  - SELECT name FROM streets WHERE ST_Intersects(geom, ST_MakeEnvelope(xmin, ymin, xmax, ymax, 4326));
- Streets within 200 meters of a point:
  - SELECT name FROM streets WHERE ST_DWithin(geom::geography, ST_Point(lon, lat)::geography, 200) ORDER BY geom <-> ST_Point(lon, lat) LIMIT 50;
- Nearest street segment:
  - SELECT name FROM streets ORDER BY geom <-> ST_Point(lon, lat) LIMIT 1;

These examples should be adapted with proper indexes and SRID handling, and verified via EXPLAIN to ensure index-aware execution.[^20][^21]

## Information Gaps

The following gaps may affect detailed capacity planning and comparative assessments and should be validated prior to procurement or implementation:

- Mapbox current pricing and limits for tiles and geocoding in 2025.
- Thunderforest and Carto explicit free-tier quotas and rate limits.
- MapTiler exact definitions of “sessions” vs “requests” beyond headline free-tier numbers.
- Official Leaflet benchmarks at 1M+ markers ( FPS/memory) under clustering.
- UK-specific accuracy metrics for OpenCage and LocationIQ.
- OS Places full pricing and quotas beyond high-level PSGA mentions.[^27][^22][^11][^18][^26][^28][^29]

## References

[^1]: Tile Usage Policy - OpenStreetMap Foundation. https://operations.osmfoundation.org/policies/tiles/
[^2]: Open Database License (ODbL) 1.0 - OpenStreetMap. https://www.openstreetmap.org/copyright
[^3]: Nominatim Usage Policy - OpenStreetMap Foundation. https://operations.osmfoundation.org/policies/nominatim/
[^4]: Nominatim - OpenStreetMap Geocoding. https://nominatim.org/
[^5]: OpenCage Pricing - Geocoding API and Geosearch. https://opencagedata.com/pricing
[^6]: OpenCage Geocoding API Documentation. https://opencagedata.com/api
[^7]: Pricing - LocationIQ. https://locationiq.com/pricing
[^8]: Geocoding and Reverse Geocoding APIs - LocationIQ. https://locationiq.com/geocoding
[^9]: LocationIQ API Client for Dart (Free tier summary). https://pub.dev/documentation/location_iq/latest/
[^10]: Geocoding APIs compared: Pricing, free tiers & terms of use. https://www.bitoff.org/geocoding-apis-comparison/
[^11]: Flexible pricing for online mapping - MapTiler Cloud. https://www.maptiler.com/cloud/pricing/
[^12]: Map usage: Sessions vs requests | MapTiler documentation. https://docs.maptiler.com/guides/maps-apis/maps-platform/tile-requests-and-map-sessions-compared/
[^13]: Manage Your Costs with MapTiler Cloud. https://www.maptiler.com/news/2019/11/manage-your-costs-with-maptiler-cloud/
[^14]: Scalable Pricing & Plans for Map & Location APIs - Stadia Maps. https://stadiamaps.com/pricing/
[^15]: MapLibre GL JS Documentation. https://www.maplibre.org/maplibre-gl-js/docs/
[^16]: Optimising MapLibre Performance: Large GeoJSON Datasets. https://www.maplibre.org/maplibre-gl-js/docs/guides/large-data/
[^17]: MapLibre GL JS vs. Leaflet: Choosing the right tool for your interactive map. https://blog.jawg.io/maplibre-gl-vs-leaflet-choosing-the-right-tool-for-your-interactive-map/
[^18]: Vector Data Rendering Performance Analysis of Open-Source Web Mapping Libraries. https://www.researchgate.net/publication/395183209_Vector_Data_Rendering_Performance_Analysis_of_Open-Source_Web_Mapping_Libraries
[^19]: Leaflet versus Mapbox GL performance. http://kuanbutts.com/2019/08/31/mbgl-vs-leaflet/
[^20]: Chapter 5. Spatial Queries - PostGIS. https://postgis.net/docs/using_postgis_query.html
[^21]: PostGIS Performance: Indexing and EXPLAIN - Crunchy Data Blog. https://www.crunchydata.com/blog/postgis-performance-indexing-and-explain
[^22]: Raster tile providers - OpenStreetMap Wiki. https://wiki.openstreetmap.org/wiki/Raster_tile_providers
[^23]: Quickstart: MapLibre GL JS - Stadia Maps Documentation. https://docs.stadiamaps.com/tutorials/vector-maps-with-maplibre-gl-js/
[^24]: The OSM US Tileservice is now Generally Available. https://openstreetmap.us/news/2025/09/tileservice-general-availability/
[^25]: Servers/Tile Rendering - OpenStreetMap Wiki. https://wiki.openstreetmap.org/wiki/Servers/Tile_Rendering
[^26]: Best Geocoding Providers for the United Kingdom - Coordable. https://coordable.co/blog/country-analysis/best-geocoding-providers-united-kingdom/
[^27]: Mapbox Pricing. https://www.mapbox.com/pricing/
[^28]: OS Places API - Ordnance Survey. https://www.ordnancesurvey.co.uk/products/os-places-api
[^29]: OS Data Hub Plans - Ordnance Survey. https://osdatahub.os.uk/plans
[^30]: Martin - PostgreSQL to Vector Tiles. https://martin.maplibre.org/
[^31]: Martin (GitHub) - Postgres/PostGIS vector tiles server. https://github.com/maplibre/martin