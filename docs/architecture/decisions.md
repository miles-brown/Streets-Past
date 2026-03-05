# Architecture Decision Records — Streets Past

This document consolidates the architecture decision records (ADRs) for the Streets Past project. Each decision is drawn from the research documentation in `docs/` and the technical choices reflected in the codebase. Decisions follow the format: Context → Options Considered → Decision → Rationale → Consequences.

---

## ADR-001: Frontend Framework — React + Vite + TypeScript

**Status:** Accepted
**Date:** 2025-12
**Research source:** `complete_street_etymology_website_setup.md`, codebase

### Context

Streets Past requires a frontend capable of rendering an interactive map, an autocomplete search bar, user authentication flows, a moderation dashboard, and etymology detail pages. The application serves read-heavy traffic from UK users and must integrate tightly with Supabase for database queries, authentication, and storage. Build tooling needed to be fast in development and produce a compact, optimised bundle for deployment.

### Options Considered

| Framework | Rendering | Notes |
|---|---|---|
| React 18 + Vite 6 | SPA (client-side) | Widely adopted, large ecosystem, fast HMR |
| Next.js | SSR / SSG / SPA | SSR adds complexity; Vercel-optimised; larger cold-start overhead |
| SvelteKit | SSR / SPA | Smaller bundle size; smaller ecosystem; fewer Supabase community examples |
| Astro | Content-site / islands | Excellent for static content; limited for interactive map/auth flows |

### Decision

React 18 as the component model, Vite 6 as the build tool, TypeScript (strict mode off) as the language, deployed as a single-page application (SPA).

### Rationale

- A SPA is sufficient for the application's needs. The primary pages are either highly interactive (map, search) or lightly trafficked (about, terms), so server-side rendering provides minimal SEO benefit over a well-structured SPA with meta tags.
- React's ecosystem provides ready-made solutions for every required integration: MapLibre GL JS bindings, Supabase JS SDK v2, shadcn/ui component library, react-hook-form, and react-router-dom v6.
- Vite 6 offers sub-second hot-module replacement during development and a production build pipeline with tree-shaking and source-map control (`vite-plugin-source-identifier` disabled in prod via `BUILD_MODE=prod`).
- The team can follow well-documented Supabase + React patterns for auth, RLS-aware queries, and Edge Function calls.
- `strict: false` in `tsconfig.app.json` reduces friction during rapid development without sacrificing the core benefit of typed interfaces for Supabase data shapes.

### Consequences

- Positive: Fast development iteration, large community, strong Supabase integration examples.
- Positive: Vite path aliases (`@/ → ./src/`) keep imports clean across a growing component tree.
- Negative: No server-side rendering means initial page load depends on the client executing JavaScript; mitigated by Cloudflare Pages CDN edge caching of the static bundle.
- Negative: SPA requires manual SEO meta management (handled via structured data in `index.html`).
- Watch: If the project scales to require server-rendered etymology pages for SEO (e.g., individual street pages indexed by Google), a migration to Next.js or Astro for the detail pages would be the most natural upgrade path.

---

## ADR-002: Database — Supabase PostgreSQL + PostGIS

**Status:** Accepted
**Date:** 2025-12
**Research source:** `docs/database/database_analysis.md`

### Context

The primary dataset is approximately 790,000 street records from OS OpenNames, growing toward 1M+. The application requires full-text search on street names, spatial queries for map viewport filtering (bounding box, nearest-neighbour), community contribution tracking, and user authentication with row-level security. The database must integrate with the auth and storage layer without additional infrastructure.

### Options Considered

| Platform | Storage (free) | PostGIS | Auth integration | Notes |
|---|---|---|---|---|
| **Supabase (PostgreSQL)** | 500 MB | Yes (extension) | Native | Integrated auth, storage, edge functions; Pro $25/month |
| Neon (serverless PostgreSQL) | 0.5 GB | Yes (extension) | None (external) | Serverless autoscaling; Launch $19/month; no built-in auth |
| PlanetScale (MySQL/Postgres) | No free tier | MySQL: No; Postgres: Yes | None (external) | Starts at $5/month single-node; no free tier |
| Railway (PostgreSQL) | 30-day trial + $5 credits | Likely (unconfirmed) | None (external) | Per-second usage billing; PostGIS support unconfirmed |
| SQLite | File-based | Via SpatiaLite | None | Development only; serialised writes; no production HA |

### Decision

Supabase with PostgreSQL and the PostGIS extension enabled. Supabase project ID: `nadbmxfqknnnyuadhdtk`.

### Rationale

- **Integrated platform:** Supabase bundles PostgreSQL, Auth, Storage, and Edge Functions under a single project with a unified SDK. Using Neon or Railway for the database would require a separate auth provider (Firebase Auth, Auth0, Clerk), adding cost and integration complexity at every query boundary.
- **PostGIS:** PostGIS spatial extensions (ST_Intersects, ST_DWithin, ST_Contains, `&&` bounding box, `<->` nearest-neighbour) are essential for map viewport queries over ~790k street coordinate records. Supabase documents and supports PostGIS via extension enablement.
- **Row Level Security:** Supabase's RLS policies enforce data access at the database level, meaning the frontend Supabase client can make queries directly without a custom API proxy layer, while security is guaranteed by policy.
- **Free tier adequacy at MVP:** 500 MB storage, 50,000 MAUs, 5 GB egress, and shared compute cover the MVP stage. The OS OpenNames dataset can be selectively loaded (name, city, county, lat/lng, etymology fields) to fit within the free-tier storage limit.
- **Cost projection:** Pro tier at $25/month unlocks 8 GB disk and 100,000 MAUs when growth demands it, representing a clear and predictable upgrade path.
- SQLite was appropriate for local schema prototyping but is unsuitable for production due to serialised writes, no HA, and no PostGIS support.

### Consequences

- Positive: Single SDK (`@supabase/supabase-js` v2) handles auth, database, storage, and edge function invocation.
- Positive: Spatial queries supported via GiST-indexed geometry columns.
- Positive: RLS policies remove the need for a custom API layer for most read operations.
- Negative: Free-tier storage limit (500 MB) means the full 790k-record OS OpenNames dataset must be selectively imported; high-resolution or full-geometry imports require the Pro plan.
- Negative: Free-tier projects pause after one week of inactivity; the production deployment on `space.minimax.io` must be kept active or migrated to a paid plan.
- Watch: Connection limits on the free tier (60 direct, 200 pooler) become relevant under concurrent map viewport queries. Implement connection pooling discipline and consider lazy loading of map markers.

---

## ADR-003: Mapping — MapLibre GL JS + OpenStreetMap Raster Tiles

**Status:** Accepted
**Date:** 2025-12
**Research source:** `docs/mapping/mapping_analysis.md`

### Context

The application requires an interactive map of the UK displaying street markers with click-to-popup etymology details. The map must handle potentially large numbers of markers (sourced from ~790k street records), support pan and zoom, and render within a single-page application without requiring a paid API key for development or low-traffic production use.

### Options Considered

**Map rendering libraries:**

| Library | Rendering | Performance at scale | Notes |
|---|---|---|---|
| **MapLibre GL JS v5** | WebGL / GPU | High (vector tiles, clustering, GPU-accelerated) | Open-source Mapbox fork; no API key for rendering |
| Leaflet | DOM-based | Limited at high marker counts | Simpler API; suitable for basic maps only |
| Google Maps JS API | WebGL | High | Per-use billing; API key required |
| Mapbox GL JS | WebGL | High | Commercial licence; API key required |

**Tile providers evaluated:**

| Provider | Free tier | Notes |
|---|---|---|
| **OSM direct raster tiles** | Unlimited (with policy compliance) | Usage policy prohibits pre-seeding, scraping; no SLA; suitable for low-traffic production |
| MapTiler Cloud | 5,000 sessions / 100,000 req/month | Service pauses on free tier; Flex $25/month |
| Stadia Maps | 200,000 credits/month (non-commercial) | Starter $20/month; credit-based unified model |
| Mapbox | Usage-based | Paid; proprietary Mapbox GL JS |
| Self-hosted vector tiles | Unlimited | High operational cost; requires Martin + PostGIS pipeline |

### Decision

MapLibre GL JS v5 for client-side rendering, with direct OpenStreetMap raster tiles for the basemap. Map centred on UK: `[-2.5, 54.0]`, zoom `5.5`, bounded to UK SW `[-12, 49]` to NE `[3, 61]`.

### Rationale

- **MapLibre GL JS:** The WebGL-based rendering model scales to large datasets where Leaflet's DOM-based approach degrades. MapLibre supports clustering, symbol layers, zoom-bound rendering, and custom amber/brown gradient markers consistent with the heritage theme. It is the natural open-source successor to Mapbox GL JS and requires no API key for the rendering library itself.
- **OSM raster tiles:** For a UK-focused application with modest initial traffic, OSM tiles are acceptable under the [OSM Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/). Traffic is bounded by UK scope and a street detail use-case. The policy prohibits pre-seeding and high-zoom scraping; the MapView component only requests tiles for the current viewport, which is compliant.
- **No tile API key:** Removing API key dependency simplifies local development and eliminates per-tile billing during the MVP phase. OSM raster tiles carry ODbL attribution requirements, handled by the visible "© OpenStreetMap contributors" attribution in the map component.
- **Geocoding:** The research evaluated LocationIQ (5,000 req/day free, 2 rps, commercial use with link-back) and OpenCage (2,500 req/day free) as geocoding providers for future autocomplete enhancement. Neither is used in the current MVP, which relies on Supabase `.ilike()` queries for search.

### Consequences

- Positive: No API key required for map rendering; zero tile cost at MVP traffic levels.
- Positive: WebGL rendering supports future expansion to dense marker datasets with clustering.
- Positive: MapLibre's clustering API and zoom-bound rendering are already available for future performance optimisation.
- Negative: OSM tiles carry no SLA; high-traffic production deployment should migrate to MapTiler Flex ($25/month) or Stadia Maps Starter ($20/month).
- Negative: Direct OSM tile usage must comply with caching headers and the tile usage policy. A CDN in front of the app (Cloudflare) does not cache tile requests to OSM servers.
- Watch: If marker density grows beyond the current viewport-loading approach, convert to vector tiles served via a Martin + PostGIS pipeline, as documented in the MapLibre performance guidance.

---

## ADR-004: Authentication — Supabase Auth

**Status:** Accepted
**Date:** 2025-12
**Research source:** `docs/auth/auth_community_analysis.md`

### Context

The application requires user registration, login, and session management to support community contributions and moderation. Roles include `user`, `moderator`, and `admin`. Authentication must integrate with the database layer to enforce Row Level Security policies without a custom API proxy. Social login (OAuth) is desirable for reduced registration friction.

### Options Considered

| Provider | Free MAUs | RLS integration | Social OAuth | Notes |
|---|---|---|---|---|
| **Supabase Auth** | 50,000 | Native (same project) | Yes | Integrated with Supabase DB/RLS/Storage |
| Firebase Auth / GIP | 50,000 | External (requires custom claims + Edge Function) | Yes | Requires separate auth project; JWT bridge to Supabase RLS |
| Auth0 | 7,500 MAUs free | External | Yes | Expensive at scale; complex integration with Supabase |
| Clerk | 10,000 MAUs free | External | Yes | Developer-friendly; requires JWT bridge to Supabase |
| Custom JWT | Unlimited | Manual | Manual | Significant engineering effort; no social login out of the box |
| X / Twitter OAuth | Paid API required ($200+/month) | External | N/A | Effectively not viable for production login |

### Decision

Supabase Auth, accessed via the `AuthContext` provider in `src/contexts/AuthContext.tsx`. The context exposes `user`, `session`, `profile`, `loading`, `signIn`, `signUp`, `signOut`, and `isAdmin`. Roles are stored in the `profiles.role` column.

### Rationale

- **Zero integration friction:** Supabase Auth operates within the same Supabase project as the database. RLS policies can reference `auth.uid()` and `auth.role()` directly, without a JWT bridge or custom claims function.
- **50,000 MAU free tier:** At MVP and early growth stages, 50,000 monthly active users on the free plan is more than sufficient. The research modelled this against Firebase Auth (also 50,000 free) and found parity, but Supabase's flat-rate Pro plan ($25/month, 100,000 MAUs) is simpler to budget than Google Identity Platform's per-MAU tiered pricing beyond 50,000.
- **Social OAuth included:** Google, GitHub, and other OAuth providers are configured directly in the Supabase dashboard with no additional cost.
- **Audit log retention:** Free-tier audit logs retain for approximately one hour. This is acceptable at MVP; the Pro plan extends retention to 7 days.
- **Session management and RLS:** `supabase.auth.onAuthStateChange()` handles token refresh automatically. The `isAdmin` check (`profile?.role === 'admin' || profile?.role === 'moderator'`) gates the AdminPage component without requiring a server-side call.

### Consequences

- Positive: RLS policies enforce data access at the database level using `auth.uid()`, eliminating the need for a custom API gateway.
- Positive: Auth state is globally available via React context with no additional state management library.
- Positive: No additional monthly cost at MVP; Supabase Auth is included in the Supabase free plan.
- Negative: Free-tier session controls (single session per user, configurable timeouts) are not available; these require the Pro plan.
- Negative: Free-tier projects pause after one week of inactivity, which can interrupt active user sessions.
- Watch: Phone-based MFA (via Supabase Auth add-on at $75/month for the first project) is not enabled. If MFA becomes a requirement, this cost must be budgeted separately.

---

## ADR-005: Etymology Engine — Rule-Based Pattern Matching (Hybrid Architecture)

**Status:** Accepted
**Date:** 2025-12
**Research source:** `docs/ai_ml/ai_ml_analysis.md`, `docs/ai_ml/suggest_etymology_algorithm.md`, `supabase/functions/suggest-etymology/index.ts`

### Context

The application needs to generate etymology suggestions for ~790,000 UK street names. The suggestions must be deterministic and explainable, available at zero marginal cost for common patterns, and consistent with academic sources. An optional LLM layer was evaluated for complex or ambiguous names.

### Options Considered

| Approach | Cost (100k req/month) | Determinism | Explainability | Notes |
|---|---|---|---|---|
| **Rule-based pattern matching (local)** | ~$0 | Fully deterministic | Full (explicit element citations) | 57 suffix + 34 prefix patterns; implemented in Edge Function |
| GPT-4o mini API only | ~$6–$95 (conservative–aggressive token budgets) | Non-deterministic | Partial | Hallucination risk; external dependency |
| GPT-4o mini hybrid (25% routed) | ~$1.5–$24 (conservative–aggressive) | Partial | Partial | Best cost–coverage trade-off for complex names |
| spaCy + etymology-db (local NLP) | ~$0 (compute) | Deterministic | High | Requires ML infrastructure; Wiktionary-derived dataset (last updated 2023-12-05) |
| Wiktionary API / etymology-db | ~$0 | Deterministic | High | Component-level only; proper nouns not headwords |
| Wordnik API | Free tier (rate-limited) | Deterministic | Partial | General lexical; not toponym-specific |

### Decision

A rule-based pattern matching engine implemented as a Supabase Edge Function (Deno runtime) at `supabase/functions/suggest-etymology/index.ts`. The engine matches 57 suffix/word patterns and 34 prefix/word patterns against the street name and returns structured elements with origin language, meaning, and historical period. No external API calls are made for standard suggestions.

The architecture is designed to be hybrid-ready: the local engine handles the majority of cases, and an optional LLM layer (GPT-4o mini) can be added for ambiguous or multi-component names in a future iteration.

**Pattern categories implemented:**
- Road types: gate (ON), street (Latin/OE), lane (OE), way (OE), road (OE), close (OF), court (OF), place (OF), row (OE), plus 10 further variants
- Geographic: hill, green, field, ford, bridge, heath, moor, meadow, grove, wood
- Settlement: bury (OE "burh"), ton (OE "tun"), ham (OE), stead (OE), worth (OE), wick (OE)
- Norse: gate ("gata"), kirk, toft, thorpe, by, beck, thwaite
- Religious/civic: church, abbey, priory, castle, mill, market, cheap, shambles
- Modern (17th–19th c.): parade, terrace, crescent, square, circus, avenue, boulevard, mews, yard, alley, passage, walk, drive, gardens, park
- Descriptive prefixes: high, low, old, new, great, little, long, broad
- Directional: north, south, east, west, upper, lower
- Colours: white, black, green, red, golden, silver
- Noble: royal, king, queen, prince, duke, lord
- Landmarks: abbey, church, mill, cross, fleet, well, spring

### Rationale

- **Zero marginal API cost:** The rule-based engine runs entirely within the Deno Edge Function with no external API calls. For 100,000 monthly etymology requests with only local processing, cost is effectively $0 in API fees.
- **Deterministic and explainable:** Each matched element returns its origin language, meaning, and historical period, supporting academic citations (English Place-Name Society, Oxford Dictionary of English Place-Names, University of Nottingham). This aligns with the project's mission to present credible, sourced etymologies.
- **Handles the majority of cases:** UK street names follow predictable morphological patterns. Suffixes like `-street`, `-gate`, `-lane`, `-wick`, `-ton`, `-ham`, `-thorpe` and prefixes like `high-`, `old-`, `king-` cover a large proportion of the 790k records.
- **Hybrid-ready:** The AI/ML research showed that a hybrid pipeline (local-first, LLM for complex cases) reduces monthly API cost by 75–85% versus an all-API approach. The Edge Function's response includes a `confidence` field (`"medium"` for matched elements, `"low"` for no matches), providing a natural routing signal for future LLM escalation.
- **LLM costs at 25% routing, moderate token budget:** ~$5–$9/month for 100,000 requests. This is budgetable when community demand justifies it.

### Consequences

- Positive: No external API dependency; etymology suggestions work offline and have zero variable cost.
- Positive: Structured element output (`elements[]` with `origin`, `meaning`, `period`) supports future UI enhancements (etymology timeline, origin language filtering).
- Positive: Confidence scoring provides a hook for future quality improvement without breaking changes.
- Negative: The rule-based approach cannot handle commemorative names (person names, event names) or highly localised dialect forms. These return `confidence: "low"` with a generic fallback message.
- Negative: Patterns are manually maintained; adding new patterns requires a code change and Edge Function deployment.
- Watch: If the LLM hybrid layer is added, token budget discipline and Batch API usage (50% discount for asynchronous processing) are the primary cost levers. Web search tool calls (~$10–$25 per 1,000 calls) must remain disabled for routine requests.

---

## ADR-006: Hosting — MiniMax (Current) with Cloudflare Pages (Recommended Production Target)

**Status:** Partially accepted; production migration pending
**Date:** 2025-12
**Research source:** `docs/hosting/hosting_analysis.md`, `memories/street_etymology_report_completion.md`

### Context

The frontend SPA (React + Vite) requires a hosting platform that can serve the compiled static bundle and a single `index.html` with client-side routing. The application is read-heavy, with occasional bursts from social traffic. The hosting platform must support custom domains, HTTPS, and CI/CD from the repository. Cost must be minimised at MVP stage.

### Options Considered

| Platform | Static bandwidth | Build limits | Commercial use | Notes |
|---|---|---|---|---|
| **Cloudflare Pages** | Unlimited (static) | 500 builds/month; 20-min timeout | Not restricted | Recommended; Workers Functions metered at 100k req/day free |
| Netlify Starter | ~100 GB/month | ~300 build-minutes | Not restricted | Overage soft-metered; functions limits unconfirmed |
| Vercel Hobby | 100 GB fast transfer | 100 deployments/day | Non-commercial only | Hobby plan prohibits commercial use |
| GitHub Pages | 100 GB/month (soft) | 10 builds/hour (soft) | Permitted | 1 GB site size limit; no server-side features |
| **MiniMax** (`space.minimax.io`) | Unknown | N/A | Development environment | Current deployment; development/demo use |

### Decision

**Current deployment:** MiniMax (`space.minimax.io`) — the development and demo environment used during build. Live at `https://6fv9t1y43vab.space.minimax.io`.

**Recommended production target:** Cloudflare Pages, with deployment to the canonical domain `https://streetetymology.co.uk/`.

### Rationale

- **Why Cloudflare Pages for production:** Cloudflare Pages serves static assets as "free and unlimited" per its Pages Functions pricing documentation. The application's SPA architecture (single `index.html`, hashed JS/CSS bundles) is ideal for CDN-edge delivery. Static asset bandwidth carries no billing risk regardless of viral traffic spikes, unlike Vercel (100 GB cap) and Netlify (~100 GB cap).
- **Vercel Hobby excluded:** The Hobby plan explicitly restricts commercial use. Streets Past is a public commercial-grade production site, making Vercel Hobby non-compliant.
- **GitHub Pages excluded:** The 1 GB published-site limit and 100 GB/month soft cap are manageable for the current bundle but leave no headroom for future growth or the potential inclusion of pre-rendered static street pages.
- **Cloudflare Pages limits:** 20,000 files per deployment and 25 MiB per file are well within the Vite build output. 500 builds/month accommodates continuous deployment from the main branch.
- **MiniMax as current host:** The `space.minimax.io` deployment served as the development and demonstration environment. Its platform metadata (1,022 files, ~47 MB workspace) suggests it is adequate for demonstration but not intended as the long-term production host.

### Consequences

- Positive: Cloudflare Pages provides global edge delivery from 300+ PoPs with zero static bandwidth cost.
- Positive: Cloudflare's free SSL is provisioned automatically and auto-renews, integrating with the domain SSL decision (ADR-010).
- Negative: Production migration from MiniMax to Cloudflare Pages requires DNS transfer and CI/CD reconfiguration (a one-time task).
- Negative: Cloudflare Pages Functions (used for any dynamic route handling) are subject to the Workers free quota: 100,000 requests/day with 10 ms CPU time per invocation. The SPA architecture avoids invoking Functions for static delivery.
- Watch: If server-side rendering or ISR (incremental static regeneration) is added for SEO of individual street pages, evaluate Cloudflare Workers for SSR rather than migrating the entire application to Next.js.

---

## ADR-007: Storage — Supabase Storage

**Status:** Accepted
**Date:** 2025-12
**Research source:** `docs/storage/storage_analysis.md`

### Context

The application allows users and moderators to upload historical map images and street photographs as supporting evidence for etymology contributions. Images need to be stored durably, served via CDN, and subject to the same RLS access controls as the database. File types include images (`image/*`) and PDFs (`application/pdf`) with a maximum upload size of 10 MB per file.

### Options Considered

| Platform | Free storage | Per-upload limit | RLS integration | CDN | Optimisation |
|---|---|---|---|---|---|
| **Supabase Storage** | 1 GB | 50 MB | Native (same project) | Basic CDN | None (free); origin transforms (Pro) |
| Cloudinary | DAM Free: 25 GB | Not specified | External | Global CDN | Extensive (transformations, responsive) |
| AWS S3 | Credits-based | N/A | External (custom IAM) | Via CloudFront | None native; external pipeline needed |
| GitHub LFS | 10 GiB storage / 10 GiB bandwidth | N/A | Not applicable | Not a CDN | None |

### Decision

Supabase Storage with a dedicated `historical-maps` bucket (10 MB file size limit, `image/*` and `application/pdf` MIME types). The bucket creation and RLS policy setup is handled by the `create-bucket-historical-maps-temp` Edge Function.

### Rationale

- **Integrated auth and RLS:** Supabase Storage shares the Auth session and can enforce RLS policies consistent with the database. This means the same `auth.uid()` check that gates `contributions` table inserts can gate storage bucket uploads, without a custom pre-signed URL server.
- **MVP adequacy:** The 1 GB free storage tier and 5 GB egress (plus 5 GB cached egress) are sufficient for MVP. The 50 MB per-file upload limit at the platform level is reduced to 10 MB per file via bucket policy, which is appropriate for web-optimised historical map images and photo uploads.
- **Cost structure at scale:** At 10,000 images averaging 10 MB each (100 GB storage), Supabase costs approximately $16/month. At this scale, Cloudinary Plus ($99/month) and AWS S3 + CloudFront ($8–$10/month) become the competitive alternatives. The decision to use Supabase Storage is explicitly tied to the MVP phase; a migration to S3 + Cloudflare CDN or Cloudinary is the documented upgrade path.
- **Cloudinary deferred:** Cloudinary's DAM Free plan (25 GB) and transformation pipeline are compelling for production image delivery but add a second vendor SDK, additional credentials management, and a more complex upload flow. Deferred to a future iteration when image optimisation and responsive delivery become requirements.
- **GitHub LFS excluded:** LFS is not a content delivery network and incurs per-GiB bandwidth billing. It is unsuitable as the primary storage and delivery layer for user-uploaded images.

### Consequences

- Positive: Single Supabase SDK handles database, auth, and storage operations.
- Positive: RLS policies can restrict uploads to authenticated users and restrict reads to approved-contribution images.
- Negative: 50 MB platform-level file size cap restricts high-resolution master image uploads. Workaround is documented: store originals externally and use Supabase Storage for delivery-optimised web variants only.
- Negative: Supabase Storage provides basic CDN on the free tier; Cloudinary's transformation pipeline would be needed for responsive image variants.
- Watch: If the `historical_maps` table grows beyond the 1 GB free tier, evaluate either the Supabase Pro plan (larger storage quotas) or migration to S3 + Cloudflare CDN, which the cost analysis shows as the lowest-cost option at 50k+ image scale.

---

## ADR-008: Data Source — OS OpenNames

**Status:** Accepted
**Date:** 2025-12
**Research source:** `docs/open_data/uk_open_data_analysis.md`

### Context

Streets Past requires a comprehensive, authoritative, and commercially licensable dataset of UK street names to populate the `streets` table. The dataset must provide names, geographic coordinates, and administrative context (city, county, postcode) for approximately 790,000 records. The dataset must be legally usable in a publicly accessible commercial web application.

### Options Considered

| Dataset | Records | Format | Update cadence | Licence | Coverage |
|---|---|---|---|---|---|
| **OS OpenNames** | ~870k roads; 1.6M postcodes | CSV, GML, GeoPackage | Quarterly (Jan/Apr/Jul/Oct) | OS OpenData (commercial use permitted) | Great Britain |
| Code-Point Open | ~1.7M postcode units | CSV, GeoPackage | Quarterly | OGL v3.0 | Great Britain (excl. NI) |
| Custom web scraping | Variable | Unstructured | Manual | Unclear / restricted | Variable |
| Community-only | 0 at launch | N/A | User-contributed | N/A | UK-wide in theory |
| Historic England NHLE | ~400k designated assets | GIS (points/polygons) | Frequent | OGL v3.0 | England only |
| ONS Open Geography | Statistical boundaries | GIS | Per ONS schedule | OGL v3.0 | UK |

### Decision

OS OpenNames as the primary street dataset (~870k named/numbered roads across Great Britain). Code-Point Open and ONS datasets are available as supplementary sources for postcode and boundary enrichment.

### Rationale

- **Coverage:** OS OpenNames provides the most comprehensive single dataset for street names across Great Britain, with approximately 870,000 named and numbered roads, 44,000 settlements, and 1.6M postcodes. No alternative free dataset offers equivalent coverage.
- **Licence:** OS OpenData permits commercial reuse with attribution. The required attribution is: "Contains OS data © Crown copyright and database right [year]." This is compatible with a public web application.
- **Coordinate system:** OS OpenNames uses British National Grid (EPSG:27700). Web mapping requires WGS84 (EPSG:4326). The import pipeline reprojects coordinates for storage in the `streets` table (`latitude`, `longitude` columns). British National Grid coordinates are retained for analytical precision where needed.
- **Update cadence:** Quarterly releases (January, April, July, October) allow a predictable refresh pipeline. Data ages by at most three months between refreshes.
- **Custom scraping excluded:** Web scraping of street name data from third-party sites would carry unclear licensing, inconsistent data quality, and ongoing maintenance overhead.
- **Community-only excluded:** Launching with zero seed data would provide no value to early users. Community contributions are additive to the OS OpenNames baseline.

### Consequences

- Positive: 790,000+ records provide immediate value at launch without community bootstrapping.
- Positive: Quarterly updates and a structured CSV/GeoPackage format support automated ingestion pipelines.
- Positive: Permissive commercial licence eliminates IP risk for the public application.
- Negative: Coverage is Great Britain only; Northern Ireland street data requires a separate dataset with different licensing terms.
- Negative: OS OpenNames provides street names and coordinates but not etymology data. Etymology must be generated by the `suggest-etymology` engine (ADR-005) or contributed by users.
- Negative: The full dataset (870k roads + 1.6M postcodes) exceeds the Supabase free-tier 500 MB storage limit if imported with full geometry. A selective import (name, city, county, lat/lng) is required for the free tier.
- Watch: Attribution ("Contains OS data © Crown copyright and database right") must be displayed on the site's About and legal pages, and in dataset metadata.

---

## ADR-009: CSS Framework — Tailwind CSS + shadcn/ui

**Status:** Accepted
**Date:** 2025-12
**Research source:** `street-etymology/tailwind.config.js`, `street-etymology/components.json`, codebase

### Context

The application requires a consistent visual identity (heritage/academic theme), accessible interactive components (modals, dropdowns, form controls, toasts), and a responsive layout that works across desktop and mobile. The team needed to move quickly without designing bespoke components from scratch.

### Options Considered

| Approach | Notes |
|---|---|
| **Tailwind CSS v3.4 + shadcn/ui** | Utility-first; Radix UI primitives; accessible; copy-paste components; no runtime CSS-in-JS |
| Material UI (MUI) | Opinionated styling; React only; difficult to customise away from Material Design |
| Chakra UI | Component library; reasonable customisation; larger bundle size |
| Plain CSS / CSS modules | Maximum control; slower to build; no accessibility primitives |
| Bootstrap | Legacy design language; jQuery-adjacent; poor Tailwind compatibility |

### Decision

Tailwind CSS v3.4 with the `tailwindcss-animate` plugin, `shadcn/ui` (new-york style) backed by 27 Radix UI primitives, and `lucide-react` for icons. Custom design tokens define the heritage/academic colour palette.

**Custom colour palette:**

| Token | Value | Usage |
|---|---|---|
| `heritage.gold` | `#b45309` | Primary actions, headings |
| `heritage.brown` | Stone tones | Secondary surfaces |
| `heritage.parchment` | Warm off-white | Background accents |
| `heritage.ink` | Near-black | Body text |

**Typography:** Georgia/serif for headings; Inter/sans-serif for body text.

### Rationale

- **Tailwind utility-first:** Utility classes applied directly in JSX components keep styles co-located with markup and eliminate the specificity conflicts common in global CSS. The `@/` alias and Tailwind's tree-shaking ensure unused styles are excluded from the production bundle.
- **shadcn/ui:** Rather than a traditional component library dependency, shadcn/ui copies component source files into the project (`src/components/`). This gives full ownership of component code while providing accessible, Radix UI-backed implementations for dialogs, dropdowns, toasts, and form primitives. Components adopt the project's CSS variable tokens automatically.
- **Accessibility:** Radix UI primitives implement WAI-ARIA patterns (focus management, keyboard navigation, screen reader labels) without custom implementation.
- **Heritage theme fit:** Tailwind's arbitrary-value syntax and CSS variable strategy allow the amber/stone palette to propagate consistently across all components, map markers, and form elements without per-component overrides.
- **Dark mode:** Configured via the `class` strategy in `tailwind.config.js`. Not fully implemented but ready to activate by toggling the `dark` class on the root element.

### Consequences

- Positive: Fast UI iteration; accessible components out of the box; consistent amber/stone design language.
- Positive: No runtime styling overhead; Tailwind generates static CSS at build time.
- Positive: shadcn/ui components are fully owned and customisable without upstream dependency constraints.
- Negative: Utility-class markup can be verbose; long `className` strings are unavoidable in complex components.
- Negative: Dark mode is configured but not fully implemented. Completing dark mode requires auditing colour variables across all components.
- Watch: Tailwind v4 introduced significant configuration changes. The project uses v3.4; any upgrade to v4 will require `tailwind.config.js` migration.

---

## ADR-010: Domain and SSL — Namecheap .org + Cloudflare SSL

**Status:** Accepted
**Date:** 2025-12
**Research source:** `docs/domain/domain_ssl_costs.md`

### Context

The project requires a production domain and HTTPS for the canonical URL `https://streetetymology.co.uk/`. The domain must be professionally credible for a UK heritage/academic audience, affordably priced, and paired with free, automatically renewing SSL.

### Options Considered

**TLD options:**

| TLD | First year | Renewal | Notes |
|---|---|---|---|
| `.org` (Namecheap) | $7.48 (promo) | $15.98 | Free privacy, DNSSEC included |
| `.org` (Gandi) | $7.99 (promo) | $39.98 | Free SSL, Anycast DNS; higher renewal |
| `.co.uk` (Hostinger) | ~$3.99 | ~$11.99 | Lower cost; UK-market-specific; free privacy + SSL |
| `.co.uk` (names.co.uk) | Free (promo) | £12.99 | UK-specific |
| `.uk` (names.co.uk) | £12.99 | £12.99 | Shorter; no promo |

**SSL options:**

| Provider | Cost | Validity | Automation |
|---|---|---|---|
| **Cloudflare Universal SSL** | $0 | Auto-renewing | Automatic (delegate DNS to Cloudflare) |
| Let's Encrypt | $0 | 90 days (reducing to 45 days from 2025-12-02) | ACME client required |
| Hosting provider SSL | $0 (bundled) | Varies | Varies |
| Paid certificates | $50–$300/year | 1–2 years | Manual |

### Decision

Namecheap `.org` domain registration (~£8/year first year) with Cloudflare Universal SSL (free, auto-renewing). The canonical domain is `https://streetetymology.co.uk/`. DNS is delegated to Cloudflare.

### Rationale

- **`.org` TLD:** The `.org` TLD communicates the project's heritage/community mission and is globally recognisable. It avoids the `.co.uk` cost-versus-credibility trade-off; while `.co.uk` is cheaper at renewal, `.org` signals a non-commercial, public-interest project more clearly.
- **Namecheap:** Lowest first-year cost ($7.48 USD) with WHOIS privacy and DNSSEC included at no extra charge. Standard renewal at $15.98 is manageable. Gandi's renewal ($39.98) is higher despite bundling SSL, because Cloudflare provides SSL at no cost anyway.
- **Cloudflare SSL:** Delegating DNS to Cloudflare gives Universal SSL (auto-renewing), DDoS mitigation, and CDN caching of the SPA static assets — all on the free plan. This also positions the project for Cloudflare Pages deployment (ADR-006) with no additional configuration.
- **Let's Encrypt deferred:** Let's Encrypt is an equally valid free SSL option, but its transition to 45-day certificate validity (effective 2025-12-02) increases operational overhead for certificate renewal automation. Cloudflare's managed SSL removes this entirely.
- **Cost summary (Year 1):** Domain ~£8 + SSL $0 + Cloudflare CDN $0 = approximately £8 total.
- **Cost summary (Year 2):** Domain ~£13 (standard renewal rate) + SSL $0 = approximately £13 total.

### Consequences

- Positive: Lowest two-year total cost among the evaluated options (~£21 over two years).
- Positive: Cloudflare auto-renewing SSL eliminates certificate expiry risk and the Let's Encrypt 45-day renewal cadence.
- Positive: DNS delegation to Cloudflare enables free CDN caching, DDoS protection, and easy Cloudflare Pages deployment integration.
- Negative: Cloudflare DNS delegation introduces a dependency on Cloudflare's infrastructure. If Cloudflare experiences an outage, DNS resolution fails even if the origin host is available.
- Negative: Namecheap's standard renewal is 113% higher than the first-year promo ($15.98 vs $7.48). Budget must account for this step-up in Year 2.
- Watch: Registry-driven `.org` price increases have occurred (October 2025 notifications observed). Monitor annual renewal invoices. Consider a multi-year registration at the standard rate to lock in current pricing.

---

## Summary Table

| ADR | Decision | Key Trade-off |
|---|---|---|
| ADR-001 | React 18 + Vite 6 + TypeScript (SPA) | No SSR; simple deployment vs potential SEO gap for street detail pages |
| ADR-002 | Supabase PostgreSQL + PostGIS | Integrated platform vs free-tier storage limit for full 790k records |
| ADR-003 | MapLibre GL JS + OSM raster tiles | No API key cost vs no SLA; production should migrate to MapTiler/Stadia |
| ADR-004 | Supabase Auth (50k MAU free) | Zero-cost native RLS integration vs limited session controls on free tier |
| ADR-005 | Rule-based etymology engine (hybrid-ready) | Zero variable cost + deterministic vs cannot handle commemorative names |
| ADR-006 | MiniMax now; Cloudflare Pages for production | Unlimited static bandwidth vs pending DNS migration |
| ADR-007 | Supabase Storage (1 GB free) | Integrated RLS vs 50 MB file cap; upgrade path to S3 + CDN at scale |
| ADR-008 | OS OpenNames (~790k records, OGL) | Most comprehensive free UK dataset vs Great Britain only, no etymology |
| ADR-009 | Tailwind CSS v3.4 + shadcn/ui | Utility-first speed + accessible components vs verbose class markup |
| ADR-010 | Namecheap .org + Cloudflare SSL | Lowest two-year cost vs Namecheap renewal step-up; Gandi bundles more |
