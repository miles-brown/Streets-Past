# Monitoring and Observability Guide — Streets Past

**Last updated:** 2026-03-04
**Project:** Streets Past (streetetymology.co.uk)
**Deployment:** MiniMax hosting (6fv9t1y43vab.space.minimax.io), Supabase project `nadbmxfqknnnyuadhdtk`
**Audience:** Solo developer / small team

---

## Overview

This document establishes the monitoring strategy for Streets Past at MVP stage. The approach prioritises free-tier and low-cost tools with minimal maintenance overhead. The goal is to know when something breaks before users report it, understand usage trends, and stay within Supabase free-tier limits.

**Stack at a glance:**

| Layer | Technology | Monitoring approach |
|---|---|---|
| Frontend SPA | React 18 + Vite, hosted on MiniMax | Sentry error tracking, UptimeRobot |
| Backend | Supabase (PostgreSQL, Auth, Storage, Edge Functions) | Supabase dashboard + usage alerts |
| Map tiles | OSM raster tiles (tile.openstreetmap.org) | Browser network analysis, tile request estimation |
| AI etymology | `suggest-etymology` Edge Function | Edge Function logs in Supabase dashboard |

---

## 1. Uptime Monitoring

### Tool: UptimeRobot (free tier)

The free UptimeRobot plan provides:
- Up to 50 HTTP(S) monitors
- 5-minute check intervals
- Email alerts on downtime
- Public status pages (1 included)
- 90-day log history

Sign up at https://uptimerobot.com — no credit card required for the free tier.

### Recommended monitors

Set up the following monitors in UptimeRobot. All use HTTP(S) monitor type unless noted.

| Monitor name | URL | Keyword check | Alert threshold |
|---|---|---|---|
| Homepage | `https://streetetymology.co.uk/` | `Streets Past` | 2 failures (10 min down) |
| Canonical redirect | `https://streetetymology.co.uk` | — | 2 failures |
| Supabase API health | `https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/` | — | 1 failure |
| Edge Function: suggest-etymology | `https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/suggest-etymology` | — | 2 failures |
| MiniMax deployment | `https://6fv9t1y43vab.space.minimax.io/` | `Streets Past` | 2 failures |

**Notes on monitor configuration:**

The Supabase REST API endpoint returns a 200 with the OpenAPI schema when the `apikey` header is omitted, which is sufficient for a liveness check. The Edge Function monitor will return a 400 (missing body) but the important thing is that it does not return a 5xx — adjust UptimeRobot to treat any non-5xx response as "up" using the "Status code" check option.

For the Edge Function monitor, use a POST request with body `{"streetName":"test"}` and the `Content-Type: application/json` header. This confirms the function is actually executing, not just responding to a preflight.

### Alert contacts

Configure at least two notification channels in UptimeRobot:
1. Email (primary) — the developer's email address
2. Telegram or Slack webhook (optional, free) — for faster mobile notification

---

## 2. Error Tracking

### Tool: Sentry (free tier)

The Sentry free tier provides:
- 5,000 error events per month
- 14-day data retention
- Source map support for readable stack traces
- Performance monitoring (limited on free tier)
- One team member seat

Sign up at https://sentry.io. Create a project of type **React**.

### Integrating Sentry with the React app

The existing `ErrorBoundary` component at `street-etymology/src/components/ErrorBoundary.tsx` catches uncaught React render errors. Sentry should be integrated both at the SDK level (for all JS errors) and inside the ErrorBoundary (for React-specific component tree errors).

**Step 1 — Install the Sentry SDK:**

```bash
cd street-etymology
pnpm add @sentry/react
```

**Step 2 — Initialise Sentry in `src/main.tsx`:**

```typescript
import * as Sentry from '@sentry/react'

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE, // 'development' | 'production'
  enabled: import.meta.env.PROD,     // only active in production builds
  tracesSampleRate: 0.1,             // 10% of transactions for performance
  replaysOnErrorSampleRate: 0.0,     // disable session replay (not on free tier)
  integrations: [
    Sentry.browserTracingIntegration(),
  ],
  // Ignore noisy non-actionable errors
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection captured',
  ],
  // Scrub PII from breadcrumbs
  beforeBreadcrumb(breadcrumb) {
    if (breadcrumb.category === 'xhr' || breadcrumb.category === 'fetch') {
      // Strip auth tokens from request URLs logged as breadcrumbs
      if (breadcrumb.data?.url?.includes('apikey=')) {
        breadcrumb.data.url = breadcrumb.data.url.replace(/apikey=[^&]+/, 'apikey=REDACTED')
      }
    }
    return breadcrumb
  },
})
```

**Step 3 — Wrap the app with Sentry's error boundary in `src/main.tsx`:**

```typescript
import * as Sentry from '@sentry/react'
import { ErrorBoundary } from './components/ErrorBoundary.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Sentry.ErrorBoundary
      fallback={({ error, resetError }) => (
        <ErrorBoundary>
          {/* ErrorBoundary's own render fallback is used; Sentry captures the event */}
          {null}
        </ErrorBoundary>
      )}
      onError={(error, componentStack) => {
        // Error is already captured by Sentry.ErrorBoundary automatically
        console.error('React render error:', error)
      }}
    >
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </Sentry.ErrorBoundary>
  </StrictMode>
)
```

Alternatively, replace the existing `ErrorBoundary` wrapper in `main.tsx` with `Sentry.ErrorBoundary` directly and update `ErrorBoundary.tsx` to call `Sentry.captureException` in `componentDidCatch`:

```typescript
// In ErrorBoundary.tsx — add Sentry capture
import * as Sentry from '@sentry/react'

componentDidCatch(error: any, errorInfo: any) {
  Sentry.captureException(error, { extra: errorInfo })
}
```

**Step 4 — Add the environment variable:**

Add to `street-etymology/.env.local`:
```
VITE_SENTRY_DSN=https://<key>@<org>.ingest.sentry.io/<project-id>
```

Add to `.env.example`:
```
VITE_SENTRY_DSN=                 # Sentry DSN (from sentry.io project settings)
```

### Source maps for production debugging

Without source maps, Sentry stack traces show minified bundle code, which is unusable for debugging.

**Option A — Upload source maps during build (recommended):**

```bash
pnpm add -D @sentry/vite-plugin
```

In `vite.config.ts`:

```typescript
import { sentryVitePlugin } from '@sentry/vite-plugin'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import sourceIdentifierPlugin from 'vite-plugin-source-identifier'

const isProd = process.env.BUILD_MODE === 'prod'

export default defineConfig({
  plugins: [
    react(),
    sourceIdentifierPlugin({
      enabled: !isProd,
      attributePrefix: 'data-matrix',
      includeProps: true,
    }),
    // Only upload source maps in production builds
    isProd && sentryVitePlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
      sourcemaps: {
        assets: './dist/**',
        deleteFilesAfterUpload: './dist/**/*.map', // do not serve maps publicly
      },
    }),
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    sourcemap: isProd ? 'hidden' : true, // hidden = maps generated but not referenced in bundles
  },
})
```

The `hidden` sourcemap mode generates `.map` files (uploaded to Sentry) without adding `//# sourceMappingURL` comments to production bundles. This means source maps are never publicly accessible but Sentry can use them to de-minify stack traces.

**Option B — Manual upload (simpler, no Vite plugin):**

After each production build, run:
```bash
npx @sentry/cli releases files <release-version> upload-sourcemaps ./dist
```

Set `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, and `SENTRY_PROJECT` as environment variables during the build step.

### Event budget management

With 5,000 events/month on the free tier, avoid event floods from a single repeating error:

1. In Sentry project settings, enable **Error Grouping** (default on).
2. Set **Rate Limiting** to 100 events/hour per issue in project settings.
3. Use the `ignoreErrors` list in `Sentry.init()` to suppress known browser noise.
4. Monitor the Events quota usage under Settings > Usage & Billing.

---

## 3. Supabase Dashboard Monitoring

The Supabase dashboard provides built-in observability at https://supabase.com/dashboard/project/nadbmxfqknnnyuadhdtk. No additional tools are needed for backend monitoring at MVP scale.

### Where to find each metric

| Metric | Dashboard location | Notes |
|---|---|---|
| Database size | Reports > Database | Total size including indexes |
| Active connections | Reports > Database | Should stay well below 60 (free tier limit) |
| API request volume | Reports > API | Requests per day/hour with status codes |
| API response times | Reports > API | p50/p99 latency by endpoint |
| Auth users (MAU) | Authentication > Users | Monthly active users count |
| Auth sign-in errors | Authentication > Logs | Failed login attempts |
| Storage bucket usage | Storage > (each bucket) | Per-bucket size and object count |
| Edge Function invocations | Edge Functions > suggest-etymology | Invocation count, error rate, execution time |
| Edge Function logs | Edge Functions > suggest-etymology > Logs | Real-time and historical log stream |
| Postgres logs | Database > Logs | Slow queries, errors, connection issues |

### Thresholds to watch

These values apply to the Supabase free tier limits:

| Resource | Free tier limit | Watch threshold | Action |
|---|---|---|---|
| Database size | 500 MB | 400 MB (80%) | Archive old contributions, compress data, consider paid plan |
| Monthly active users | 50,000 MAU | 40,000 MAU (80%) | Evaluate Supabase Pro ($25/month) |
| Storage (all buckets) | 1 GB | 800 MB (80%) | Purge unused historical map uploads, set image size limits |
| Edge Function invocations | 500,000/month | 400,000/month (80%) | Implement client-side caching to reduce redundant calls |
| Egress bandwidth | 5 GB/month | 4 GB/month (80%) | Enable CDN caching, compress API responses |
| API requests | Unlimited on free tier | — | Monitor for abuse patterns |

### Checking free tier usage

Navigate to: Settings > Billing > Usage to see a consolidated view of all limits and current consumption. Supabase sends an automatic email warning when usage approaches limits.

### Useful Postgres queries for monitoring

Run these in the SQL Editor (Database > SQL Editor):

```sql
-- Database size breakdown by table
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS total_size,
  pg_size_pretty(pg_relation_size(schemaname || '.' || tablename)) AS data_size,
  pg_size_pretty(pg_indexes_size(schemaname || '.' || tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;

-- Row counts across core tables
SELECT
  'streets' AS table_name, COUNT(*) AS row_count FROM streets
UNION ALL SELECT 'contributions', COUNT(*) FROM contributions
UNION ALL SELECT 'profiles', COUNT(*) FROM profiles
UNION ALL SELECT 'newsletter_subscribers', COUNT(*) FROM newsletter_subscribers;

-- Pending contributions awaiting moderation
SELECT COUNT(*) AS pending_count FROM contributions WHERE status = 'pending';

-- Slowest recent queries (requires pg_stat_statements extension)
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 4. Performance Monitoring

### Core Web Vitals

Google's Core Web Vitals are the primary performance signals that affect search ranking and user experience:

| Metric | Meaning | Good threshold | Poor threshold |
|---|---|---|---|
| LCP (Largest Contentful Paint) | How quickly the main content loads | < 2.5 s | > 4.0 s |
| FID (First Input Delay) / INP | Responsiveness to first user interaction | < 100 ms | > 300 ms |
| CLS (Cumulative Layout Shift) | Visual stability during load | < 0.1 | > 0.25 |

**Measuring Core Web Vitals in production:**

Add the `web-vitals` library to report real-user metrics to Sentry or the browser console:

```bash
pnpm add web-vitals
```

Create `src/lib/vitals.ts`:

```typescript
import { onCLS, onFID, onLCP, onFCP, onTTFB, onINP } from 'web-vitals'
import * as Sentry from '@sentry/react'

type MetricName = 'CLS' | 'FID' | 'LCP' | 'FCP' | 'TTFB' | 'INP'

function reportToSentry(metric: { name: MetricName; value: number; rating: string }) {
  // Only report poor or needs-improvement ratings to conserve Sentry event quota
  if (metric.rating === 'poor') {
    Sentry.captureMessage(`Poor Core Web Vital: ${metric.name}`, {
      level: 'warning',
      extra: { value: metric.value, rating: metric.rating },
    })
  }
}

export function initVitals() {
  onCLS(reportToSentry)
  onFID(reportToSentry)
  onLCP(reportToSentry)
  onFCP(reportToSentry)
  onTTFB(reportToSentry)
  onINP(reportToSentry)
}
```

Call `initVitals()` in `src/main.tsx` after `Sentry.init()`.

### Lighthouse CI

Run Lighthouse manually for periodic checks rather than on every commit, to keep the process lightweight.

**Manual check via PageSpeed Insights:**

Visit https://pagespeed.web.dev/ and test:
- `https://streetetymology.co.uk/` (homepage)
- `https://streetetymology.co.uk/map` (map page — heaviest page due to MapLibre)
- `https://streetetymology.co.uk/search` (search page)

Run this check monthly or after any significant frontend change.

**Local Lighthouse check before deployment:**

```bash
# Install globally once
pnpm add -g lighthouse

# Run against preview server
pnpm preview &
lighthouse http://localhost:4173 --output html --output-path ./lighthouse-report.html
open ./lighthouse-report.html
```

**Key areas to optimise for Streets Past specifically:**

- Map page: MapLibre GL JS (~750 KB gzipped) is the dominant bundle cost. Use `import()` dynamic import to lazy-load `MapView.tsx` since the map is only needed on `/map`.
- Images: Ensure historical map images served from Supabase Storage include `Cache-Control: public, max-age=31536000` headers.
- Fonts: Georgia is a system font and requires no loading. Inter (if loaded from Google Fonts) should use `display=swap` and be preloaded.

---

## 5. Map Tile Usage Tracking

### OpenStreetMap tile usage policy

The OSM tile server at `tile.openstreetmap.org` is free but governed by an acceptable use policy. Key limits:

- Maximum 2 download threads per application
- No bulk downloading or crawling
- Tiles should be cached by the browser (they return `Cache-Control` headers)
- Heavy users (> ~100,000 tile requests/day sustained) should self-host tiles or use a commercial provider
- A `User-Agent` or `Referer` header identifying the application is required

MapLibre GL JS handles all of this correctly by default. The main risk is a viral traffic spike causing the OSM tile servers to rate-limit or block the deployment IP.

### Estimating tile request volume

Each map view at zoom level 5.5 (the UK overview) loads approximately 6–12 tiles. Zooming to street level (zoom 15–17) loads 16–64 tiles per viewport. Factor in:

- **Tile caching:** Browsers cache OSM tiles aggressively (they expire after 7 days). Repeat visitors cost very few tile requests.
- **Viewport size:** Mobile phones request fewer tiles than desktop.

**Rough formula:**

```
Monthly tile requests ≈ monthly_map_pageviews × avg_tiles_per_session
```

At MVP scale (< 5,000 monthly users), with an estimated 20% visiting the map page and loading 50 tiles per session:

```
5,000 × 0.20 × 50 = 50,000 tiles/month
```

This is well within acceptable limits. Monitor if monthly users exceed 20,000.

### Monitoring tile requests in the browser

Use Chrome DevTools to profile tile requests during development:

1. Open DevTools > Network tab
2. Filter by `tile.openstreetmap.org`
3. Navigate to `/map` and interact with the map
4. Note the number of requests and check that responses return `200` (not `429` rate-limited)

Check the `Age` response header on tile responses: a non-zero value means the browser is serving from cache, which is the desired behaviour.

### If tile usage becomes a concern

If the project grows beyond ~50,000 monthly map page views, migrate tiles to one of:

- **Protomaps** — self-hostable PMTiles format, one-time download of UK extract (~2 GB)
- **Stadia Maps** — free tier includes 200,000 tile requests/month with attribution
- **MapTiler** — free tier includes 100,000 tiles/month

The MapLibre GL JS `Map` style URL is currently configured in `MapView.tsx`. Switching providers requires only updating the tile URL string.

---

## 6. Cost Alerts

### Supabase usage alerts

Supabase sends automated email notifications when approaching free-tier limits. Verify these are enabled:

1. In the Supabase dashboard: Settings > Billing > Usage alerts
2. Confirm alerts are set for database size, MAU, and storage thresholds

Additionally, review the Usage page manually on the first of each month before potential carryover resets.

**Manual monthly check checklist:**

- [ ] Database size < 400 MB
- [ ] Monthly active users < 40,000
- [ ] Storage < 800 MB total across all buckets
- [ ] Edge Function invocations < 400,000
- [ ] Egress < 4 GB

### OpenAI API cost tracking (if integrated)

If OpenAI's API is added in the future for enhanced etymology generation (as outlined in `docs/ai_ml/ai_ml_analysis.md`):

1. Set a **hard budget limit** in the OpenAI dashboard: https://platform.openai.com/settings/organization/limits
2. Set soft alert at 50% of monthly budget, hard stop at 90%
3. Add a `MONTHLY_AI_BUDGET_USD` environment variable so the application can track cumulative spend independently
4. Use `gpt-4o-mini` (cheapest capable model) for all etymology requests — approximately $0.15 per million input tokens
5. Cache etymology results in the `streets.etymology_suggestion` database column to avoid re-querying OpenAI for the same street name

**Cost estimation for OpenAI:**

At MVP scale (500 etymology requests/month), at ~300 tokens per request:
```
500 requests × 300 tokens × ($0.15 / 1,000,000 tokens) = $0.02/month
```

Well within free credit allocation. Alert becomes relevant above 100,000 requests/month (~$4.50).

### MiniMax hosting costs

MiniMax hosting billing can be monitored at the MiniMax platform dashboard. As a static SPA deployment, the main cost drivers are bandwidth and build minutes. Review the billing page monthly.

---

## 7. Logging Strategy

### What to log and where

| Event type | Where logged | Format | Retention |
|---|---|---|---|
| Auth sign-in (success) | Supabase Auth logs | Automatic | 7 days (dashboard) |
| Auth sign-in (failure) | Supabase Auth logs | Automatic | 7 days (dashboard) |
| Auth sign-up | Supabase Auth logs | Automatic | 7 days (dashboard) |
| Contribution submission | Supabase DB + `console.info` | Structured | Permanent (DB) |
| Contribution approval/rejection | Supabase DB | Automatic | Permanent (DB) |
| Etymology Edge Function call | Supabase Edge Function logs | `console.log` | 7 days (dashboard) |
| Etymology Edge Function error | Supabase Edge Function logs | `console.error` | 7 days (dashboard) |
| Search queries | Browser only (dev), Sentry breadcrumb (prod) | String | Session only |
| React render errors | Sentry | Exception + stack trace | 14 days (Sentry) |
| JS runtime errors | Sentry | Exception + stack trace | 14 days (Sentry) |
| Map load failure | Sentry | Exception | 14 days (Sentry) |
| Supabase client errors | Sentry breadcrumbs | Error object | 14 days (Sentry) |

### Edge Function logging

The `suggest-etymology` Edge Function already logs errors with `console.error`. Add structured logging for successful calls to track usage patterns:

In `supabase/functions/suggest-etymology/index.ts`, add after a successful response is prepared:

```typescript
console.log(JSON.stringify({
  event: 'etymology_requested',
  streetName,
  confidence: foundElements.length > 0 ? 'medium' : 'low',
  elementsFound: foundElements.length,
  timestamp: new Date().toISOString(),
}))
```

Supabase stores Edge Function `console.log` output in the function's log stream (Edge Functions > suggest-etymology > Logs), viewable in real time and searchable for 7 days.

### Frontend logging conventions

Use a consistent approach in the React app:

```typescript
// Development: verbose, includes full objects
// Production: structured, Sentry-captured for errors only

// Good — structured error with context
try {
  const { data, error } = await supabase.from('contributions').insert(payload)
  if (error) {
    Sentry.captureException(error, { extra: { streetId: payload.street_id } })
    console.error('[ContributionForm] Supabase insert failed:', error.message)
  }
} catch (err) {
  Sentry.captureException(err)
}

// Avoid — noisy logs that survive into production
console.log('data:', data)
console.log('user:', user)
```

Establish the convention that `console.error` and `console.warn` are production-appropriate and `console.log` / `console.debug` are development-only. Use a `DEBUG` flag or ESLint rule to enforce this if needed.

### Search query logging

Do not log full search query strings to any persistent store without a privacy review. Search terms may contain personal information (e.g., a user's home street). For analytics purposes, log only:

- Search result count (0 results vs. results found)
- Whether the search originated from the homepage or search page
- Time to first result

Do not log the query text itself in Sentry or any third-party service.

---

## 8. Alerting Rules

The following alerts are recommended as the minimum viable alerting setup. All can be configured with free-tier UptimeRobot + Sentry notifications.

### Critical alerts (require immediate response)

| Condition | Detection method | Alert channel |
|---|---|---|
| Site down > 5 minutes | UptimeRobot: homepage monitor | Email + optional Telegram |
| Supabase API unreachable | UptimeRobot: Supabase API monitor | Email |
| Edge Function returning 500 | UptimeRobot: POST probe + keyword check | Email |
| Spike in JS errors (> 50 new Sentry issues/hour) | Sentry: alert rule | Email |

**UptimeRobot configuration for site down:**

In UptimeRobot > My Monitors > Homepage > Edit:
- Monitoring interval: 5 minutes
- Send alerts after: 2 failed checks (10 minutes of downtime before alert fires)
- Alert contacts: email + any webhook

**Sentry alert rule for error spike:**

In Sentry > Alerts > Create Alert Rule:
- Condition: "Number of events is greater than 50 in 1 hour"
- Filter: environment = production
- Action: Send email notification

### Warning alerts (review within 24 hours)

| Condition | Detection method | Response |
|---|---|---|
| Database > 400 MB | Supabase email notification | Review largest tables, plan cleanup |
| Auth failures > 20 in 1 hour | Supabase Auth logs (manual check) | Check for credential stuffing attempt |
| Storage > 800 MB | Supabase email notification | Audit historical map uploads |
| Edge Function avg response > 2 s | Supabase Edge Function metrics | Review pattern matching algorithm, optimise |
| MAU approaching 40,000 | Supabase email notification | Evaluate Supabase Pro upgrade |
| LCP > 4 s (PageSpeed) | Manual monthly Lighthouse run | Profile bundle size, optimise lazy loading |

### Setting up Sentry alert rules

Navigate to Sentry > Project > Alerts > Create Alert:

1. **Unhandled JS error alert:**
   - Trigger: issue is seen for the first time
   - Filter: `is:unresolved` + `level:error`
   - Action: email immediately

2. **High error volume alert:**
   - Trigger: number of events > 100 in 1 hour
   - Action: email

3. **Specific error type alerts (optional, for known critical paths):**
   - Trigger: issue title contains `MapView` or `Supabase`
   - Action: email immediately

---

## 9. Dashboard Setup

### Option A: UptimeRobot public status page (recommended, free)

UptimeRobot's free plan includes one public status page. This is the simplest option.

1. In UptimeRobot: go to Status Pages > Create Status Page
2. Add all monitors created in Section 1
3. Set the friendly name to "Streets Past Status"
4. Note the generated URL (e.g., `https://stats.uptimerobot.com/XXXXXXX`)
5. Optionally link it from the site footer under "System Status"

The status page shows the current state of all monitored endpoints, 7-day uptime history, and incident log. It updates every 5 minutes.

### Option B: GitHub Status Badge (minimal, no setup)

If the codebase is hosted on GitHub, add a simple README badge or footer link showing build status. This does not reflect runtime uptime, only CI build health.

```markdown
[![CI](https://github.com/org/streets-past/actions/workflows/build.yml/badge.svg)](https://github.com/org/streets-past/actions)
```

### Option C: Statuspage.io (free tier)

Statuspage.io (Atlassian) offers a free tier with:
- Up to 5 components
- Email and Slack subscriber notifications
- Custom subdomain (e.g., `status.streetetymology.co.uk` via CNAME)

This is more polished than UptimeRobot's status page and supports incident communication, but requires more setup. Recommended only if the user base is large enough to warrant proactive status communication.

Components to create if using Statuspage.io:
1. Website (streetetymology.co.uk)
2. Search & Database (Supabase API)
3. Map
4. Etymology Suggestions (Edge Function)
5. Authentication

### Linking the status page

Add a "Status" link to the site footer in `street-etymology/src/components/Footer.tsx`, pointing to whichever status page is created. A real-time status indicator (green dot = operational) can be implemented by polling the UptimeRobot API (JSON feed available on free tier) and rendering an inline badge.

---

## Monthly Monitoring Routine

Run through this checklist on the first day of each month:

1. **Supabase Usage** — Open Settings > Billing > Usage. Note current database size, MAU, storage, Edge Function invocations, and egress. Compare to previous month.
2. **Sentry issues** — Review any new unresolved issues. Triage and assign priorities.
3. **UptimeRobot** — Review the 30-day uptime report. Investigate any downtime incidents.
4. **PageSpeed Insights** — Run the homepage and map page through https://pagespeed.web.dev/. Note LCP, CLS, and INP scores.
5. **Error log review** — In Supabase: check Edge Function logs and Auth logs for unusual patterns.
6. **Contribution moderation queue** — Check the Admin page for pending contributions. Run the SQL query for pending count (see Section 3).
7. **Cost review** — Confirm no unexpected charges on Supabase, MiniMax, or OpenAI (if applicable).

This routine should take approximately 20–30 minutes per month at MVP scale.

---

## Escalation Reference

| Situation | First step | Second step |
|---|---|---|
| Site completely down | Check UptimeRobot for which component failed | Check MiniMax deployment status; re-deploy if needed |
| Supabase API down | Check https://status.supabase.com | Wait for Supabase incident resolution; no action needed |
| Database full (500 MB) | Run size query to identify largest tables | Archive old `contributions` with status `rejected` to cold storage |
| Sentry quota exhausted | Increase `ignoreErrors` list, reduce sample rate | Upgrade to Sentry Developer plan ($26/month) |
| OSM tile rate-limiting | Check browser Network tab for `429` responses | Switch tile provider to Stadia Maps or Protomaps (see Section 5) |
| Auth abuse (credential stuffing) | Check Supabase Auth logs for failed sign-in patterns | Enable Supabase Auth > Protection > Rate limiting |
