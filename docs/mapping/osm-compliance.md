# OSM Tile Usage Compliance Checklist — Streets Past

**Document scope:** OpenStreetMap standard raster tile usage as implemented in
`street-etymology/src/components/MapView.tsx`.

**Policy source:** https://operations.osmfoundation.org/policies/tiles/
**ODbL license:** https://www.openstreetmap.org/copyright
**Last reviewed:** 2026-03-04

---

## 1. Current Compliance Status

### What the project currently does right

| Requirement | Implementation | Status |
|---|---|---|
| Visible attribution text | `attribution` field set in the MapLibre raster source with link to `https://www.openstreetmap.org/copyright` | Pass |
| Attribution rendered by MapLibre | MapLibre GL JS renders the attribution control automatically from the source definition | Pass |
| Geographic bounds enforced | `maxBounds` set to UK only: SW `[-12, 49]`, NE `[3, 61]` — limits the tile footprint to a small region | Pass |
| Single-page interactive use | Tiles are loaded on-demand as the user pans and zooms; no batch loading logic is present | Pass |
| No offline download feature | No "save for offline" or tile pre-seeding logic exists anywhere in the codebase | Pass |
| HTTPS tile URLs | All three subdomain URLs use `https://` | Pass |

### What needs attention

| Issue | Severity | Detail |
|---|---|---|
| Generic browser User-Agent | High | Tile requests are made by the browser with a default browser User-Agent string. OSM policy requires a descriptive, app-identifying User-Agent. Browsers cannot set the `User-Agent` header on image requests, but a tile proxy can. Without this, the project is at risk of being blocked without notice. |
| Subdomain rotation (`a/b/c`) | Medium | The subdomain URLs (`a.tile.openstreetmap.org`, `b.tile.openstreetmap.org`, `c.tile.openstreetmap.org`) are legacy load-balancing aliases. OSM policy specifies the canonical URL as `https://tile.openstreetmap.org/{z}/{x}/{y}.png`. The subdomains still function but should be consolidated to the canonical single endpoint. |
| No tile caching layer | High | Browser cache is controlled by the HTTP response headers from OSM's servers. There is no application-level caching proxy ensuring a minimum 7-day cache lifetime. If OSM servers return short or no-cache headers, tiles will be re-fetched on every page load, increasing request volume and violating the policy's caching requirement. |
| No request volume monitoring | Medium | There is no instrumentation tracking how many tile requests are made per day. Without this it is impossible to know whether usage falls within OSM's acceptable-use expectations. |
| Referrer policy not explicitly set | Low | The site does not set a restrictive `Referrer-Policy` header (which would strip the `Referer` header from tile requests). Current browser defaults send the origin as a Referer, which satisfies OSM policy. This should be confirmed and locked in as a project-wide header policy. |

---

## 2. Attribution Requirements

### License

OpenStreetMap data is published under the **Open Database Licence (ODbL) 1.0**. Any use of OSM-derived map tiles requires credit to OpenStreetMap and its contributors. Attribution is not optional — it is a licence condition.

Full attribution guidelines: https://wiki.osmfoundation.org/wiki/Licence/Attribution_Guidelines

### Required attribution text

The minimum required text is:

```
© OpenStreetMap contributors
```

The word "OpenStreetMap" must link to `https://www.openstreetmap.org/copyright`.

### Current implementation in MapView.tsx

```typescript
attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
```

This satisfies the minimum requirement. MapLibre GL JS renders this string in the bottom-right attribution control by default.

### Additional attribution placement recommendations

- The attribution control must remain **visible** — do not hide it with CSS, do not position it off-screen, and do not reduce its opacity below readable contrast.
- On the `MapPage` (full-screen layout with no header/footer), the MapLibre attribution control is the only attribution present. Confirm it is never obscured by the legend overlay that sits in `bottom-4 right-4`.
- If the map is ever embedded in a screenshot, export, or social share image, the attribution must be included in that image too.
- Do not use a "credits" modal or collapsed tooltip as the sole attribution — the text must be persistently visible on the map canvas.

---

## 3. Technical Requirements Checklist

### 3.1 Tile URL

| Requirement | Current value | Required value | Action |
|---|---|---|---|
| Canonical URL | `https://a.tile.openstreetmap.org/{z}/{x}/{y}.png` (three subdomains) | `https://tile.openstreetmap.org/{z}/{x}/{y}.png` | Consolidate to single canonical URL |

**Code location:** `street-etymology/src/components/MapView.tsx`, lines 52-55.

Change from:
```typescript
tiles: [
  'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
  'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
  'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
],
```

Change to:
```typescript
tiles: [
  'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
],
```

### 3.2 HTTP User-Agent header

OSM policy requires a **valid, descriptive HTTP User-Agent** that identifies the application by name and provides a way to contact the operator.

**Problem:** Browsers do not allow JavaScript to set the `User-Agent` header on image tile requests (`fetch` requests to different origins also cannot override this header in modern browsers). The requests therefore arrive at OSM's servers with the generic browser User-Agent (e.g., `Mozilla/5.0 ...`). The OSM policy states explicitly: "Generic browser/language library User-Agents will be blocked without notice."

**Solution:** Route tile requests through a lightweight caching reverse proxy hosted on the same domain or a subdomain. The proxy adds the correct `User-Agent` header before forwarding to OSM, and also caches responses for the required minimum of 7 days.

Example User-Agent value to set on the proxy:
```
StreetsPast/1.0 (https://streetetymology.co.uk/; contact@streetetymology.co.uk)
```

### 3.3 HTTP Referer header

OSM policy requires that the `Referer` header is sent with tile requests from web applications.

- Standard browser behaviour is to send the page origin as `Referer` on cross-origin image requests, so this requirement is currently satisfied by default.
- Ensure the site never sets `<meta name="referrer" content="no-referrer">` or a `Referrer-Policy: no-referrer` HTTP response header, as either would strip the Referer from tile requests and result in blocking.

**Verification step:** Open DevTools > Network, filter by `tile.openstreetmap.org`, inspect a tile request, confirm the `Referer` request header is present and shows the site origin.

### 3.4 Tile caching (minimum 7 days)

| Requirement | Current status | Action required |
|---|---|---|
| Cache tiles locally for at least 7 days | Not enforced by the application — relies entirely on browser HTTP cache and OSM server cache headers | Implement a caching proxy that stores tile responses for a minimum of 7 days |
| No `no-cache` or `Cache-Control: no-store` headers on tile requests | Not set by the application code (pass) | Confirm CDN/hosting does not add these headers to outbound requests |
| Conditional requests when cache expires | Browser handles this automatically via `ETag`/`Last-Modified` if cached (pass for browser cache) | Proxy must also implement conditional request forwarding |

**Minimum cache TTL:** 7 days (604,800 seconds).

A Cloudflare Worker or a lightweight Deno/Node proxy deployed to the same hosting environment would satisfy both the User-Agent and caching requirements simultaneously.

### 3.5 No-cache header audit

Confirm the following are never set on outbound tile requests:
- `Cache-Control: no-cache`
- `Cache-Control: no-store`
- `Pragma: no-cache`

These can be introduced accidentally by fetch interceptors, service workers, or CDN rules. Audit any service workers registered by the application and any Cloudflare/CDN cache rules applied to the deployment.

---

## 4. Prohibited Actions

The following are explicitly prohibited by OSM tile usage policy. None are currently implemented, but each should be confirmed as out of scope before any future feature work.

| Prohibited action | Risk in Streets Past context | Verdict |
|---|---|---|
| Bulk downloading of tiles | No batch tile fetching code exists | Not present |
| Pre-seeding tile caches | No admin tool or script pre-loads tiles | Not present |
| Building offline tile archives | No "download for offline" feature | Not present |
| Automated scraping at high zoom (z14+) | No headless or bot tile-loading code | Not present |
| Masking or spoofing User-Agent | Not done intentionally; but default browser UA is effectively a generic UA that OSM treats similarly — see Section 3.2 | Needs remediation |
| Sending `no-cache` headers | Not set explicitly | Not present |
| Stripping the Referer header | Not done | Not present |
| Redistributing OSM tiles as a tile service | Streets Past uses tiles for its own map only | Not applicable |

### Future features that would require migration to a commercial provider

Any of the following, if implemented, would exceed what is permitted on OSM standard tiles:

- A "download this area for offline use" feature for mobile users.
- Automated screenshot or PDF generation of map views at scale.
- A tile endpoint shared with third-party sites or embed codes.
- Background data pipelines that iterate over a bounding box requesting tiles at any zoom.
- Any admin tooling that pre-renders tiles across the UK at launch.

---

## 5. Risk Assessment

### Consequence of non-compliance

OSM tile policy enforcement is **immediate and without prior notice**. There is no warning period, no grace period, and no SLA. The OSM Operations Working Group monitors usage patterns and blocks IP addresses or User-Agent strings automatically.

| Risk event | Probability | Impact | Notes |
|---|---|---|---|
| Blocked due to generic browser User-Agent | Medium — low traffic now, higher risk as user numbers grow | High — map page goes blank for all users | Mitigated only by adding a proxy; cannot be fixed in browser-side code |
| Blocked due to insufficient caching | Low at current traffic levels | High — redundant tile requests accelerate blocking | Mitigated by proxy with 7-day cache |
| Policy change that removes free access | Low | Very High — entire map feature breaks | Mitigated by having a commercial provider migration plan ready |
| Service outage (OSM has no SLA) | Low | Medium — degraded map experience during outage | Mitigated by commercial fallback |

### Current risk level

With low traffic (early-stage deployment), the immediate blocking risk is low. However, the User-Agent and caching gaps are **structural non-compliance issues** — they are not conditional on traffic volume. OSM can block at any traffic level if requests are non-compliant.

**Recommendation:** Treat the User-Agent proxy as a prerequisite before any public launch or marketing effort that would drive significant traffic.

---

## 6. Migration Plan

### When to migrate to a commercial tile provider

Migrate away from OSM standard tiles when any of the following conditions are met:

| Trigger | Recommended action |
|---|---|
| More than approximately 500 unique map sessions per day | Switch to MapTiler Free tier (5,000 sessions/month included) |
| Any requirement to set a custom User-Agent without operating a proxy | Switch to MapTiler or Stadia Maps (requests go through their infrastructure) |
| Any offline or pre-seeding feature requirement | Switch to a provider that explicitly permits this |
| OSM announces a policy change restricting access | Immediate migration to commercial provider |
| Map availability becomes a business-critical requirement (SLA needed) | MapTiler Flex ($25/month) or Stadia Starter ($20/month) both offer SLA-backed service |

### How to migrate

Migration requires changing only the `tiles` array and the `attribution` string in `MapView.tsx`. No other part of the codebase references tile URLs. The change is confined to approximately 10 lines of code.

**MapTiler migration example:**
```typescript
// Replace the OSM source block with:
sources: {
  basemap: {
    type: 'raster',
    tiles: [
      'https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png?key=YOUR_API_KEY',
    ],
    tileSize: 256,
    attribution:
      '&copy; <a href="https://www.maptiler.com/copyright/">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
},
```

**Stadia Maps migration example:**
```typescript
// Replace the OSM source block with:
sources: {
  basemap: {
    type: 'raster',
    tiles: [
      'https://tiles.stadiamaps.com/tiles/osm_bright/{z}/{x}/{y}.png?api_key=YOUR_API_KEY',
    ],
    tileSize: 256,
    attribution:
      '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
},
```

The API key should be stored in `.env.local` as `VITE_MAPTILER_API_KEY` or `VITE_STADIA_API_KEY` and referenced in `MapView.tsx` via `import.meta.env.VITE_MAPTILER_API_KEY`. Add the variable to `.env.example` with a placeholder value.

---

## 7. Implementation Tasks

Ordered by priority. All code changes are in `street-etymology/src/components/MapView.tsx` unless otherwise noted.

### Priority 1 — Required before significant traffic

**Task 1.1: Consolidate tile URLs to canonical OSM endpoint**

File: `street-etymology/src/components/MapView.tsx`, lines 52-55.

Remove the three subdomain URLs and replace with the single canonical URL:
```typescript
tiles: [
  'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
],
```

**Task 1.2: Add a tile caching proxy with a correct User-Agent**

Deploy a lightweight proxy (Cloudflare Worker, Deno Deploy function, or Supabase Edge Function) that:
1. Accepts tile requests at a path such as `/tiles/osm/{z}/{x}/{y}.png`
2. Sets `User-Agent: StreetsPast/1.0 (https://streetetymology.co.uk/; contact@streetetymology.co.uk)` on the upstream request to OSM
3. Caches the tile response for a minimum of 7 days using `Cache-Control: max-age=604800`
4. Forwards the `Referer` header from the incoming browser request to OSM

Update the tile URL in `MapView.tsx` to point to the proxy:
```typescript
tiles: [
  'https://streetetymology.co.uk/tiles/osm/{z}/{x}/{y}.png',
],
```

**Task 1.3: Confirm Referer header is being sent**

Open browser DevTools on the `/map` page. Filter network requests by `tile.openstreetmap.org` (or the proxy URL after Task 1.2). Confirm that the `Referer` request header is present and contains the site origin. Document the result.

### Priority 2 — Recommended housekeeping

**Task 2.1: Verify attribution control is always visible**

On the MapPage (full-screen layout), visually confirm that the MapLibre attribution text is not obscured by the legend overlay in `bottom-4 right-4`. If overlap occurs, adjust the legend position or increase the bottom padding of the attribution control.

**Task 2.2: Add the tile provider API key to .env.example**

When a commercial tile provider is adopted (Section 6), add the API key variable to `street-etymology/.env.example` with a placeholder value, so that new developers know to supply it.

**Task 2.3: Document the proxy User-Agent string**

Record the exact User-Agent string in use in this document and in `CLAUDE.md` under the "Map" section. If the contact email changes, both must be updated.

### Priority 3 — Monitoring (see Section 9)

**Task 3.1: Instrument tile request counts**

Add logging to the proxy (Task 1.2) to count tile requests per day. Export the count to a monitoring dashboard or log aggregator. Set an alert threshold (e.g., 50,000 tile requests per day) that triggers a review of whether migration to a commercial provider is warranted.

---

## 8. Alternative Tile Providers

If OSM standard tiles are not suitable — whether due to compliance requirements, traffic growth, or SLA needs — the following providers are available. All support MapLibre GL JS and require only a URL change in `MapView.tsx`.

### MapTiler Cloud

- **Free tier:** 5,000 map sessions and 100,000 tile requests per month. Service pauses (not billed) when the limit is exceeded. The MapTiler logo is required on the free tier.
- **Flex:** $25/month — 25,000 sessions, 500,000 requests, $0.10 per 1,000 additional requests. Commercial use permitted. No MapTiler logo required.
- **Unlimited:** $295/month — 300,000 sessions, 5,000,000 requests, 99.9% SLA.
- **Tile URL format:** `https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png?key=API_KEY`
- **Attribution required:** "Map tiles by MapTiler" + "© OpenStreetMap contributors"
- **Pricing page:** https://www.maptiler.com/cloud/pricing/
- **Suitability:** Best fit for Streets Past once daily sessions exceed approximately 150/day.

### Stadia Maps

- **Free tier:** 200,000 credits per month. Non-commercial use only. A 14-day full-feature trial is available.
- **Starter:** $20/month — 1,000,000 credits, $0.03 per 1,000 additional credits. Commercial use permitted.
- **Standard:** $80/month — 7,500,000 credits.
- **Credits per operation:** 1 credit per raster or vector tile, 20 per static map request.
- **Tile URL format:** `https://tiles.stadiamaps.com/tiles/osm_bright/{z}/{x}/{y}.png?api_key=API_KEY`
- **Attribution required:** "© Stadia Maps" + "© OpenStreetMap contributors"
- **Pricing page:** https://stadiamaps.com/pricing/
- **Suitability:** Starter tier at $20/month gives 1,000,000 credits — adequate for early production. Preferred choice if geocoding APIs (Stadia uses a unified credit system) are also needed.

### LocationIQ

- **Free tier:** 5,000 geocoding requests per day. Tile hosting is not the primary LocationIQ offering; it focuses on geocoding. Mention here is for completeness as it was identified in the research phase.
- **Geocoding only** — not a suitable tile provider for Streets Past map tiles.

### Comparison summary

| Provider | Free monthly tile allowance | First paid tier | SLA on paid | Suitable phase |
|---|---|---|---|---|
| OSM Standard Tiles | Unlimited (acceptable use only) | N/A | None | Prototype / very low traffic with proxy |
| MapTiler | 5,000 sessions / 100,000 requests | $25/month (Flex) | Not specified for Flex | Early production |
| Stadia Maps | 200,000 credits (non-commercial) | $20/month (Starter) | Implied | Early production |

---

## 9. Monitoring Tile Request Volume

Without monitoring it is impossible to verify compliance or anticipate when a commercial provider becomes necessary.

### Recommended approach

**Option A — Proxy-level logging (recommended when the caching proxy from Task 1.2 is deployed)**

Log each cache miss (upstream request to OSM) and cache hit in the proxy. Aggregate daily:
- Total tile requests served to the browser
- Cache hit rate
- Upstream requests forwarded to OSM

Store daily aggregates in a simple log file or, if using Supabase, a lightweight analytics table.

**Option B — Browser-side tile event counting (no proxy required, limited)**

MapLibre GL JS fires a `data` event with `dataType: 'tile'` when a tile is requested. This can be used to count tile loads in the browser:

```typescript
map.current.on('data', (e) => {
  if (e.dataType === 'tile' && e.isSourceLoaded === false) {
    // increment a session-local counter
  }
});
```

This counts tile requests per user session only. It does not give server-side visibility into total daily request volume. Useful as a rough indicator during development; not a substitute for proxy-level monitoring in production.

### Alert thresholds

| Daily tile request count | Recommended action |
|---|---|
| Under 10,000 | No action — well within acceptable use |
| 10,000 to 50,000 | Review growth trend; plan commercial migration |
| Over 50,000 | Migrate to MapTiler Flex or Stadia Starter immediately |
| Over 100,000 | Already at a level that could trigger OSM blocking; commercial provider is mandatory |

Note: OSM does not publish a numeric threshold for "acceptable use." The figures above are conservative estimates based on the policy's framing around community-funded capacity and the prohibition of "heavy use." Any sustained high-zoom, high-session usage pattern is at risk of enforcement action regardless of absolute request count.

---

## Summary Checklist

Quick-reference for the development team:

- [ ] **Attribution** — `"© OpenStreetMap contributors"` with link to `/copyright` is present and visible in the MapLibre attribution control
- [ ] **Canonical URL** — Tile source uses `https://tile.openstreetmap.org/{z}/{x}/{y}.png` (single URL, not three subdomains)
- [ ] **User-Agent proxy** — A caching proxy sets a descriptive `User-Agent` header on all upstream tile requests to OSM
- [ ] **7-day cache** — Proxy caches tile responses for at least 7 days (604,800 seconds)
- [ ] **No no-cache headers** — Confirmed that no CDN rule, service worker, or fetch interceptor adds `Cache-Control: no-cache` to tile requests
- [ ] **Referer header present** — Verified in DevTools that tile requests carry the site origin as `Referer`
- [ ] **No bulk download features** — No offline, pre-seeding, or tile archive functionality exists or is planned without first migrating to a permitting provider
- [ ] **Request monitoring in place** — Daily tile request counts are logged and an alert threshold is configured
- [ ] **Migration plan documented** — Team knows which commercial provider to switch to and has a tested migration procedure ready

---

*Sources:*
- *OSM Tile Usage Policy: https://operations.osmfoundation.org/policies/tiles/*
- *OSM Attribution Guidelines: https://wiki.osmfoundation.org/wiki/Licence/Attribution_Guidelines*
- *ODbL 1.0: https://www.openstreetmap.org/copyright*
- *MapTiler Pricing: https://www.maptiler.com/cloud/pricing/*
- *Stadia Maps Pricing: https://stadiamaps.com/pricing/*
- *Raster Tile Providers (OSM Wiki): https://wiki.openstreetmap.org/wiki/Raster_tile_providers*
- *Streets Past mapping analysis: docs/mapping/mapping_analysis.md*
