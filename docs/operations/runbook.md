# Streets Past - Operations Runbook

**Project:** Streets Past (streetetymology.co.uk)
**Supabase Project ID:** nadbmxfqknnnyuadhdtk
**Hosting:** MiniMax (https://6fv9t1y43vab.space.minimax.io)
**Canonical Domain:** https://streetetymology.co.uk/
**Last Updated:** 2026-03-04

---

## Table of Contents

1. [Common Operations](#1-common-operations)
2. [Troubleshooting Guide](#2-troubleshooting-guide)
3. [Scaling Triggers and Actions](#3-scaling-triggers-and-actions)
4. [Data Management](#4-data-management)
5. [Incident Response](#5-incident-response)
6. [Backup and Recovery](#6-backup-and-recovery)
7. [Maintenance Schedule](#7-maintenance-schedule)

---

## 1. Common Operations

### 1.1 Deploying a Frontend Update

1. Ensure all changes are committed to Git.
2. From the `street-etymology/` directory, install dependencies and build:
   ```bash
   cd street-etymology/
   pnpm install
   pnpm build:prod
   ```
   The `build:prod` script sets `BUILD_MODE=prod`, which disables the `vite-plugin-source-identifier` debug plugin. The compiled output lands in `street-etymology/dist/`.

3. Upload the contents of `dist/` to the MiniMax hosting platform via the MiniMax dashboard or CLI. The deployment target is:
   - Live URL: https://6fv9t1y43vab.space.minimax.io
   - Canonical: https://streetetymology.co.uk/ (DNS CNAME to the MiniMax URL)

4. After deployment, open https://streetetymology.co.uk/ in an incognito window and verify:
   - The homepage loads without console errors.
   - The search bar returns results.
   - The `/map` route renders the MapLibre map.
   - Authentication (login/register) completes successfully.

**Rollback:** Re-upload the previous `dist/` build. The Git history is the source of truth; check out the previous tag or commit and rebuild.

---

### 1.2 Deploying an Edge Function Update

Prerequisites: Supabase CLI authenticated (`supabase login`).

**Deploy a single function:**
```bash
supabase functions deploy suggest-etymology --project-ref nadbmxfqknnnyuadhdtk
```

**Deploy all functions:**
```bash
supabase functions deploy --project-ref nadbmxfqknnnyuadhdtk
```

**Verify deployment:**
1. Open Supabase dashboard → Edge Functions → `suggest-etymology` → Logs.
2. Send a test POST request:
   ```bash
   curl -X POST \
     https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/suggest-etymology \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <SUPABASE_ANON_KEY>" \
     -d '{"streetName": "High Street"}'
   ```
   Expected response: JSON with `etymology`, `elements`, `confidence`, and `sources` fields.

**Notes:**
- The `create-bucket-historical-maps-temp` function is a one-time setup utility. Do not redeploy it unless recreating the storage bucket.
- All Edge Functions use Deno runtime. Verify `index.ts` uses `Deno.serve()` and includes CORS headers before deploying.

---

### 1.3 Adding a New Admin or Moderator

Connect to the Supabase database via the SQL Editor (Supabase dashboard → SQL Editor) and run:

```sql
-- Grant admin role
UPDATE profiles
SET role = 'admin'
WHERE email = 'user@example.com';

-- Grant moderator role
UPDATE profiles
SET role = 'moderator'
WHERE email = 'user@example.com';

-- Verify the change
SELECT user_id, email, full_name, role
FROM profiles
WHERE email = 'user@example.com';
```

The user must already have a registered account. The `isAdmin` check in `AuthContext.tsx` accepts both `'admin'` and `'moderator'` roles, granting access to the `/admin` moderation dashboard.

**To revoke admin/moderator access:**
```sql
UPDATE profiles
SET role = 'user'
WHERE email = 'user@example.com';
```

---

### 1.4 Checking Database Size

**Via Supabase Dashboard:**
1. Open https://supabase.com/dashboard/project/nadbmxfqknnnyuadhdtk
2. Navigate to Database → Usage (or Settings → Usage).
3. Check the "Database size" metric against the free-tier limit (500MB).

**Via SQL Editor:**
```sql
-- Total database size
SELECT pg_size_pretty(pg_database_size(current_database())) AS db_size;

-- Per-table sizes (largest first)
SELECT
  relname AS table_name,
  pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
  pg_size_pretty(pg_relation_size(relid)) AS data_size,
  pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

The `streets` table (~790k records) will be the largest. Monitor it when loading new OS OpenNames data.

---

### 1.5 Manual Database Backup

**CSV export via Supabase Dashboard:**
1. Open Supabase dashboard → Table Editor.
2. For each critical table (`streets`, `contributions`, `profiles`, `newsletter_subscribers`), open the table and use the Export → CSV option.
3. Store exported CSVs in a secure, off-platform location (e.g., encrypted local storage or a private Git repository).

**Via SQL Editor (for targeted exports):**
```sql
-- Export approved contributions with street names
SELECT c.id, s.name, s.city, c.etymology_text, c.sources, c.status, c.created_at
FROM contributions c
JOIN streets s ON c.street_id = s.id
WHERE c.status = 'approved';
```
Copy the result set from the dashboard to save as CSV.

**Note:** Automated daily backups are only available on Supabase Pro ($25/month). On the free tier, perform manual exports weekly (see Section 7: Maintenance Schedule).

---

## 2. Troubleshooting Guide

### 2.1 Site Not Loading

**Symptoms:** Browser shows connection timeout, DNS error, or blank page.

**Diagnosis steps:**

1. **Check MiniMax hosting status.**
   Open https://6fv9t1y43vab.space.minimax.io directly. If this also fails, the issue is with MiniMax hosting, not DNS.

2. **Check DNS resolution.**
   ```bash
   dig streetetymology.co.uk
   nslookup streetetymology.co.uk
   ```
   The CNAME should resolve to the MiniMax hosting URL. If DNS has not propagated or the CNAME record is missing, check the domain registrar settings.

3. **Check SSL certificate.**
   ```bash
   curl -vI https://streetetymology.co.uk 2>&1 | grep -E "SSL|certificate|expire"
   ```
   SSL is provisioned via Cloudflare (free tier). If the certificate has expired or the Cloudflare proxy is misconfigured, the site will show a security warning.

4. **Check browser console.**
   Open DevTools → Console. Look for:
   - 404 errors on JS/CSS bundles (deploy may be incomplete).
   - CSP (Content Security Policy) violations blocking scripts.
   - Mixed content warnings (HTTP resources on HTTPS page).

**Resolution:**
- MiniMax hosting outage: Wait for platform resolution; no self-hosted fallback exists.
- DNS issue: Update CNAME record at domain registrar; allow up to 48 hours for propagation.
- SSL issue: Re-verify Cloudflare SSL/TLS mode is set to "Full" or "Full (strict)".
- Incomplete deploy: Re-run `pnpm build:prod` and re-upload `dist/`.

---

### 2.2 Search Returning No Results

**Symptoms:** Search bar returns empty results for common street names (e.g., "High Street").

**Diagnosis steps:**

1. **Check Supabase connectivity.** Open the browser DevTools → Network tab. Search for a term and look for requests to `nadbmxfqknnnyuadhdtk.supabase.co`. If requests are failing (401, 403, or network error), the anon key may be invalid or the Supabase project is paused.

2. **Check if the Supabase project is paused.** On the free tier, Supabase pauses inactive projects after 1 week of inactivity. Open the Supabase dashboard. If the project shows "Paused", click "Restore".

3. **Verify the anon key.** In `street-etymology/.env.local`, confirm `VITE_SUPABASE_ANON_KEY` matches the key in Supabase dashboard → Settings → API → Project API keys → `anon public`.

4. **Verify streets table has data.**
   ```sql
   SELECT COUNT(*) FROM streets;
   SELECT * FROM streets LIMIT 5;
   ```
   If the table is empty, the OS OpenNames import may not have run. See Section 4.1.

5. **Test the query directly.**
   ```sql
   SELECT id, name, city, county
   FROM streets
   WHERE name ILIKE '%high street%'
   LIMIT 10;
   ```

6. **Check RLS policies.**
   ```sql
   SELECT tablename, policyname, cmd, qual
   FROM pg_policies
   WHERE tablename = 'streets';
   ```
   The `streets` table should have a SELECT policy allowing public (anon) reads.

**Resolution:**
- Paused project: Restore via Supabase dashboard. Consider setting up a simple cron ping to prevent pausing.
- Invalid anon key: Update `.env.local`, rebuild, and redeploy.
- Empty table: Follow the OS OpenNames import procedure (Section 4.1).
- Missing RLS policy: Add a policy permitting anon SELECT on `streets`.

---

### 2.3 Map Not Rendering

**Symptoms:** The `/map` page shows a blank area or spinner instead of the interactive map.

**Diagnosis steps:**

1. **Check OSM tile server status.**
   Open https://tile.openstreetmap.org in a browser. If tiles do not load, the OSM tile CDN may be degraded. Check the OSM community wiki or https://operations.osmfoundation.org/ for status.

2. **Check browser console for errors.**
   - `Failed to fetch` on tile requests: Network or CORS issue. OSM tiles should not have CORS restrictions.
   - `MapLibre GL: ...` errors: Library initialisation failure, possibly due to WebGL unavailability.
   - Content Security Policy (CSP) blocking tile requests: The `connect-src` or `img-src` CSP directives may not include `tile.openstreetmap.org`.

3. **Test WebGL availability.**
   In the browser console: `!!window.WebGLRenderingContext`. If `false`, the user's browser or device does not support WebGL and the map cannot render.

4. **Verify MapLibre initialisation in `MapView.tsx`.**
   The map is centered on `[-2.5, 54.0]` with zoom `5.5`. If the container element is not in the DOM when `new Map()` is called, MapLibre will fail silently.

**Resolution:**
- OSM tile outage: This is outside your control. Consider documenting a fallback tile provider (e.g., MapTiler free tier or Stadia Maps). See Section 3.4.
- WebGL issue: Display a message to the user directing them to update their browser.
- CSP issue: Update the Content Security Policy headers to allow `tile.openstreetmap.org`.

---

### 2.4 Auth Not Working

**Symptoms:** Login or registration fails, users are not redirected after OAuth, or sessions expire unexpectedly.

**Diagnosis steps:**

1. **Check Supabase Auth settings.**
   Supabase dashboard → Authentication → Settings. Verify:
   - Email confirmations: If "Enable email confirmations" is on, new users must confirm their email before they can log in.
   - Site URL: Must be set to `https://streetetymology.co.uk`.
   - Redirect URLs (allowed list): Must include `https://streetetymology.co.uk/auth/callback` and `https://6fv9t1y43vab.space.minimax.io/auth/callback`.

2. **Check for email delivery issues.**
   Supabase free tier uses a shared SMTP server with rate limits. For production, configure a custom SMTP provider (e.g., Resend, Sendgrid) in Supabase → Authentication → SMTP Settings.

3. **Check browser console for auth errors.**
   Look for `AuthApiError` messages. Common errors:
   - `Invalid login credentials`: Wrong password or unconfirmed email.
   - `User already registered`: Attempt to register with an existing email.
   - `Email not confirmed`: User has not clicked the confirmation link.

4. **Verify the `profiles` table trigger.**
   A database trigger should create a row in `profiles` when a new user is created in `auth.users`. Verify:
   ```sql
   SELECT trigger_name, event_manipulation, action_statement
   FROM information_schema.triggers
   WHERE event_object_table = 'users'
     AND trigger_schema = 'auth';
   ```

**Resolution:**
- Add missing redirect URLs in Supabase Auth settings.
- Disable email confirmation for low-friction onboarding (or configure a reliable SMTP provider).
- Manually confirm a user's email via Supabase dashboard → Authentication → Users → confirm email.
- Repair missing profile rows:
  ```sql
  INSERT INTO profiles (user_id, email)
  SELECT id, email FROM auth.users
  WHERE id NOT IN (SELECT user_id FROM profiles);
  ```

---

### 2.5 Edge Function Errors

**Symptoms:** Etymology suggestions fail, the contribution form shows an error, or API calls to Edge Functions return 500 or 4xx responses.

**Diagnosis steps:**

1. **Check Edge Function logs.**
   Supabase dashboard → Edge Functions → `suggest-etymology` → Logs. Look for runtime errors, unhandled exceptions, or timeout messages.

2. **Test the function directly** (see Section 1.2 for the curl command).

3. **Common error causes:**
   - `CORS error` in browser: The function's CORS headers may not include the request origin. Verify the function returns `Access-Control-Allow-Origin: *` (or the specific domain).
   - `401 Unauthorized`: The request is missing the `Authorization: Bearer <anon_key>` header.
   - Cold start timeout: Edge Functions may take 1-2 seconds on first invocation after a period of inactivity.

4. **Check Deno runtime compatibility.**
   If a function was recently updated, ensure it uses `Deno.serve()` and not the deprecated `serve()` from `std/http`.

**Resolution:**
- CORS: Ensure the OPTIONS preflight handler returns the correct headers.
- Auth: Confirm the frontend is sending the Supabase anon key in the `Authorization` header.
- Code error: Fix the bug in `supabase/functions/<name>/index.ts` and redeploy (Section 1.2).

---

### 2.6 "Access Denied" on Admin Page

**Symptoms:** A user navigates to `/admin` and sees an access denied message or is redirected away.

**Diagnosis steps:**

1. **Verify the user's role in the database.**
   ```sql
   SELECT user_id, email, role
   FROM profiles
   WHERE email = 'admin@example.com';
   ```
   The `role` must be `'admin'` or `'moderator'`. Any other value (including `NULL` or `'user'`) will fail the `isAdmin` check.

2. **Check for session issues.**
   The user may be logged in but their profile has not loaded. Ask them to sign out and sign back in to force a profile refresh via `onAuthStateChange`.

3. **Verify `AuthContext` is loading correctly.**
   In the browser, open DevTools → Application → Local Storage. Check for a Supabase session token under `nadbmxfqknnnyuadhdtk`. If absent, the user is not authenticated.

**Resolution:**
- Update the role via SQL (Section 1.3).
- Ask the user to clear browser storage and log in again.

---

## 3. Scaling Triggers and Actions

Monitor usage monthly. The following thresholds indicate when free-tier limits are approaching and what action to take.

### 3.1 Database Approaching 500MB

**Trigger:** Database size exceeds ~400MB (80% of 500MB free-tier limit).

**Immediate actions:**
- Run the size query from Section 1.4 to identify the largest tables and indexes.
- Review the `streets` table for duplicate or low-quality records that can be pruned.
- Delete rejected contributions that are more than 90 days old:
  ```sql
  DELETE FROM contributions
  WHERE status = 'rejected'
    AND created_at < NOW() - INTERVAL '90 days';
  ```
- VACUUM the database to reclaim space:
  ```sql
  VACUUM ANALYZE streets;
  VACUUM ANALYZE contributions;
  ```

**If space cannot be recovered:**
- Upgrade to Supabase Pro ($25/month), which provides 8GB database storage.
- Alternatively, archive older or lower-priority `streets` records to a separate table or external CSV store, keeping only the records actively queried.

---

### 3.2 Auth Approaching 50k MAU

**Trigger:** Monthly Active Users in Supabase Auth dashboard approaches 40k (80% of 50k free-tier limit).

**Actions:**
- Review authentication usage in Supabase dashboard → Authentication → Users. Identify bot accounts or unused accounts.
- Purge accounts that have never contributed and have not logged in within 12 months (with appropriate GDPR notices — see Section 4.4).
- If legitimate user growth is driving the increase, upgrade to Supabase Pro ($25/month, which includes higher MAU limits).

---

### 3.3 Storage Approaching 1GB

**Trigger:** Supabase Storage usage approaches 800MB (80% of 1GB free-tier limit).

**Immediate actions:**
- Review the `historical-maps` bucket for duplicate or oversized files.
- Implement image compression on upload: enforce a maximum file size in the `ContributionForm` frontend and reject uploads exceeding the Edge Function's configured 10MB limit.
- Re-compress existing images using a script or the Supabase Storage API.

**If storage needs persist:**
- Evaluate Cloudinary (free tier: 25GB storage, 25GB monthly bandwidth). Cloudinary provides automatic image optimisation and a CDN, reducing storage and improving load times.
- Update the `historical_maps` table to store Cloudinary URLs instead of Supabase Storage paths.
- Research reference: `docs/storage/storage_analysis.md`

---

### 3.4 Map Tiles Causing OSM Policy Concerns

**Trigger:** OSM Foundation contacts the project regarding tile usage policy violations (heavy traffic without a valid use case declaration), or tile.openstreetmap.org degrades or blocks requests.

**OSM tile usage policy:** Bulk/heavy usage requires caching, rate-limiting, or migration to a commercial tile provider. Self-hosting a tile server is an option for large-scale deployments.

**Migration options (in order of cost):**

| Provider | Free Tier | Estimated Cost at 1M tiles/month |
|---|---|---|
| MapTiler Cloud | 100k tiles/month | ~$25/month |
| Stadia Maps | 200k tiles/month | ~$10/month |
| Protomaps (self-hosted PMTiles) | Free (storage costs only) | ~$1-2/month on Cloudflare R2 |

**Migration steps:**
1. Register for a MapTiler or Stadia Maps account and obtain an API key.
2. Update the tile URL in `MapView.tsx`:
   ```typescript
   // Replace:
   'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
   // With (MapTiler example):
   `https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png?key=${MAPTILER_API_KEY}`
   ```
3. Add the API key to `.env.local` as `VITE_MAPTILER_API_KEY`.
4. Update the attribution string to reflect the new provider.
5. Research reference: `docs/mapping/mapping_analysis.md`

---

### 3.5 AI Etymology Costs Rising

**Trigger:** Monthly Supabase Edge Function invocation costs or downstream AI API costs (if GPT-4o mini is integrated) exceed budget targets.

**Current state:** The `suggest-etymology` function uses purely rule-based pattern matching with no external AI API calls. There is no per-request API cost.

**If GPT-4o mini or similar is integrated in future:**
- Implement a caching layer: Store etymology suggestions in the `streets.etymology_suggestion` column. On request, return the cached value if present rather than calling the AI API.
- Batch process streets in bulk during off-peak hours rather than on-demand.
- Rate-limit etymology requests per user per day (e.g., 10 AI suggestions/day for unauthenticated users).
- Use GPT-4o mini only as a fallback when rule-based matching returns `confidence: "low"`.
- Research reference: `docs/ai_ml/ai_ml_analysis.md` (hybrid local + GPT-4o mini, $6-$95 per 100k requests).

---

## 4. Data Management

### 4.1 Quarterly OS OpenNames Data Refresh

OS OpenNames is updated periodically by Ordnance Survey under the Open Government Licence v3.0. A data refresh imports updated or new street records into the `streets` table.

**Full procedure:** See `docs/data/os-opennames-import.md`.

**Summary of steps:**
1. Download the latest OS OpenNames dataset from the OS Data Hub (https://osdatahub.os.uk/downloads/open/OpenNames).
2. Unzip and locate the CSV files for England, Scotland, and Wales.
3. Parse and filter for `TYPE = 'streetDescriptiveIdentifier'` records (approximately 790k records).
4. Load into a staging table in Supabase:
   ```sql
   CREATE TABLE streets_staging (LIKE streets INCLUDING ALL);
   ```
5. Use `COPY` or the Supabase data import tool to load CSV data into `streets_staging`.
6. Upsert new/updated records into `streets`:
   ```sql
   INSERT INTO streets (id, name, city, county, postcode, latitude, longitude)
   SELECT id, name, city, county, postcode, latitude, longitude
   FROM streets_staging
   ON CONFLICT (id) DO UPDATE SET
     name = EXCLUDED.name,
     city = EXCLUDED.city,
     county = EXCLUDED.county,
     postcode = EXCLUDED.postcode,
     latitude = EXCLUDED.latitude,
     longitude = EXCLUDED.longitude;
   ```
7. Drop the staging table:
   ```sql
   DROP TABLE streets_staging;
   ```
8. Run `VACUUM ANALYZE streets;` to update statistics.

**Note:** Preserve `etymology_suggestion`, `etymology_verified`, and `historical_period` columns for existing records — these contain community-contributed data.

---

### 4.2 Cleaning Up Rejected Contributions

Rejected contributions older than 90 days can be deleted to reduce database clutter:

```sql
-- Preview records to be deleted
SELECT COUNT(*)
FROM contributions
WHERE status = 'rejected'
  AND created_at < NOW() - INTERVAL '90 days';

-- Delete rejected contributions older than 90 days
DELETE FROM contributions
WHERE status = 'rejected'
  AND created_at < NOW() - INTERVAL '90 days';
```

**Bulk reject pending contributions via SQL (if admin page is unavailable):**
```sql
-- Reject all pending contributions older than 30 days with no activity
UPDATE contributions
SET status = 'rejected'
WHERE status = 'pending'
  AND created_at < NOW() - INTERVAL '30 days';
```

Run these cleanup queries quarterly (see Section 7: Maintenance Schedule).

---

### 4.3 Archiving Old Newsletter Subscriber Data

To comply with data minimisation principles, remove subscribers who have been unsubscribed or inactive for more than 12 months:

```sql
-- View unsubscribed or stale entries (adjust column names to match schema)
SELECT id, email, subscribed_at, unsubscribed_at
FROM newsletter_subscribers
WHERE unsubscribed_at IS NOT NULL
  AND unsubscribed_at < NOW() - INTERVAL '12 months';

-- Delete stale unsubscribed entries
DELETE FROM newsletter_subscribers
WHERE unsubscribed_at IS NOT NULL
  AND unsubscribed_at < NOW() - INTERVAL '12 months';
```

Before deleting, export the data as a CSV backup (Section 1.5) in case it is needed for compliance audits.

---

### 4.4 GDPR Deletion Requests

When a user submits a Subject Access Request (SAR) or Right to Erasure request under UK GDPR:

**Step 1: Identify the user**
```sql
SELECT user_id, email, full_name, created_at
FROM profiles
WHERE email = 'user@example.com';
```

**Step 2: Export their data (for SAR)**
```sql
SELECT * FROM profiles WHERE email = 'user@example.com';
SELECT * FROM contributions WHERE user_id = '<user_id>';
SELECT * FROM newsletter_subscribers WHERE email = 'user@example.com';
```

**Step 3: Delete their data (for erasure request)**
```sql
-- Delete contributions
DELETE FROM contributions WHERE user_id = '<user_id>';

-- Delete profile
DELETE FROM profiles WHERE user_id = '<user_id>';

-- Delete newsletter subscription
DELETE FROM newsletter_subscribers WHERE email = 'user@example.com';
```

**Step 4: Delete auth record**
In Supabase dashboard → Authentication → Users, find the user by email and click "Delete user". This removes the record from `auth.users`.

Alternatively, via the Supabase Admin API:
```bash
curl -X DELETE \
  https://nadbmxfqknnnyuadhdtk.supabase.co/auth/v1/admin/users/<user_id> \
  -H "Authorization: Bearer <SERVICE_ROLE_KEY>"
```

**Timeframe:** UK GDPR requires responding to erasure requests within 30 days. Log the request date and completion date for compliance records.

**Note:** Approved contributions attributed to the user may be anonymised rather than deleted if they constitute part of the site's public data (legitimate interest basis). Consult the Privacy Policy for the applicable retention basis.

---

## 5. Incident Response

### 5.1 Database Outage

**Symptoms:** All database-dependent features fail (search, map markers, auth, contributions). Error messages reference Supabase connection failures.

**Response:**
1. Check the Supabase status page: https://status.supabase.com
   Look for incidents affecting the `ap-southeast-1` region (or whichever region the project is hosted in).
2. Check the Supabase dashboard. If the project is paused (free-tier inactivity), click "Restore". Restoration typically takes 1-3 minutes.
3. If Supabase reports no incident and the project is not paused, check the Supabase Discord or GitHub Issues for reports from other users.
4. There is no self-hosted database fallback. The site will be degraded until Supabase resolves the issue.

**Communication:** If the outage lasts more than 30 minutes during business hours, consider posting a brief status note on social media or via the site's static content.

**Post-incident:** After resolution, verify all features are functioning (search, map, auth, contributions). Check for any data integrity issues in the Supabase logs.

---

### 5.2 Site Defacement or Compromise

**Symptoms:** Unauthorised content appears on the site, unusual API activity in logs, unexpected user account changes.

**Immediate response:**
1. **Take the site offline** by removing the deployment from MiniMax hosting or pointing the DNS CNAME to a maintenance page.
2. **Rotate all Supabase keys immediately.**
   - Supabase dashboard → Settings → API → Regenerate anon key and service role key.
   - Update `.env.local` with the new keys.
3. **Review Supabase Auth logs.**
   Supabase dashboard → Authentication → Logs. Look for unexpected sign-ins, password resets, or admin actions.
4. **Review database changes.**
   Run queries to identify recent unexpected modifications:
   ```sql
   -- Check for recent profile role escalations
   SELECT user_id, email, role, updated_at
   FROM profiles
   WHERE role IN ('admin', 'moderator')
   ORDER BY updated_at DESC;
   ```
5. **Identify the attack vector** (compromised credentials, leaked anon key, XSS, etc.).
6. **Redeploy from a clean Git state.**
   Check out a known-good commit, rebuild with the new Supabase keys, and redeploy.
7. **Re-enable the site** once the attack vector is closed.

**Post-incident:**
- Document the incident, timeline, and resolution.
- Review and tighten RLS policies if data was accessed inappropriately.
- Implement additional monitoring (e.g., Supabase Webhooks for profile role changes).

---

### 5.3 Spam Contributions

**Symptoms:** Large volume of low-quality, nonsense, or promotional `contributions` records with `status = 'pending'`.

**Immediate response:**
1. **Use the admin dashboard** (`/admin`) to bulk-review and reject spam contributions.
2. **Bulk reject via SQL** if the volume is too large for the UI:
   ```sql
   -- Review pending contributions from suspicious users
   SELECT c.id, c.user_id, c.etymology_text, c.created_at, p.email
   FROM contributions c
   JOIN profiles p ON c.user_id = p.user_id
   WHERE c.status = 'pending'
     AND c.created_at > NOW() - INTERVAL '24 hours'
   ORDER BY c.created_at DESC;

   -- Bulk reject from a specific user
   UPDATE contributions
   SET status = 'rejected'
   WHERE user_id = '<spammer_user_id>'
     AND status = 'pending';
   ```
3. **Ban the spammer's account** by deleting it (Section 4.4) or setting a `banned` flag on their profile.

**Preventive measures:**
- **Rate limiting:** Add a database-level constraint or Edge Function logic to limit contributions per user per hour.
- **CAPTCHA:** Integrate hCaptcha or Cloudflare Turnstile on the `ContributionForm` component. Both have free tiers.
- **Email verification:** Require confirmed email addresses before allowing contributions (Supabase Auth setting).
- **Honeypot field:** Add a hidden form field to the contribution form that bots will fill in; reject submissions where this field is populated.

---

### 5.4 Cost Overrun

**Symptoms:** Supabase billing alert, unexpected invoice, or usage metrics exceeding free-tier limits.

**Response:**
1. **Check Supabase billing dashboard.**
   Supabase dashboard → Settings → Billing. Identify which resource is over limit: database storage, egress, Edge Function invocations, Auth MAU, or Storage.

2. **Identify the cause by resource type:**

   | Resource | Investigation query or location |
   |---|---|
   | Database storage | Run size queries from Section 1.4 |
   | Egress | Check which tables have the highest read throughput; large file downloads |
   | Edge Function invocations | Check Supabase → Edge Functions → usage metrics |
   | Auth MAU | Check Supabase → Authentication → Users count |
   | Storage | Check Supabase → Storage → `historical-maps` bucket size |

3. **Apply targeted fixes** (see Section 3 for scaling actions per resource type).

4. **Set spending alerts** in the Supabase billing dashboard to receive email notifications before limits are exceeded.

5. **Year 1 budget target:** Less than £20/month total. If costs exceed this consistently:
   - Evaluate whether Supabase Pro ($25/month) is more cost-effective than piecemeal overages.
   - Review the cost breakdown in `complete_street_etymology_website_setup.md` (MVP: £8-£44/yr, Growth: £44-£164/yr).

---

## 6. Backup and Recovery

### 6.1 Backup Strategy

| Tier | Backup Type | Frequency | Retention | Action Required |
|---|---|---|---|---|
| Free (current) | Manual CSV export | Weekly | Indefinite (operator managed) | Manual (see Section 1.5) |
| Pro ($25/month) | Automated daily backup | Daily | 7 days (point-in-time recovery) | None (automatic) |
| Code | Git repository | On every commit | Full history | Push to GitHub after each feature |

**Priority tables for manual backup:**
1. `profiles` — user account data (GDPR sensitive)
2. `contributions` — community-contributed content
3. `streets` — core dataset (can be re-imported from OS OpenNames if lost, but slower to recover)
4. `newsletter_subscribers` — email list (GDPR sensitive)

---

### 6.2 Recovery Procedure

**Scenario: Complete data loss (Supabase project deleted or corrupted)**

1. **Create a new Supabase project** at https://supabase.com. Note the new project ID and API keys.

2. **Recreate the database schema.** Apply the schema migrations from the `supabase/migrations/` directory (if present) or recreate tables manually based on the schema in CLAUDE.md (Section: Database Schema).

3. **Enable PostGIS extension:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

4. **Import backed-up data.**
   Use the Supabase CSV import tool or `COPY` statements to restore `streets`, `contributions`, `profiles`, and `newsletter_subscribers` from the most recent CSV backups.

5. **Re-import OS OpenNames data** if the streets table backup is unavailable (Section 4.1).

6. **Recreate RLS policies** for all tables (reference the original migration files).

7. **Redeploy Edge Functions:**
   ```bash
   supabase functions deploy --project-ref <new_project_id>
   ```

8. **Recreate the storage bucket** by invoking the `create-bucket-historical-maps-temp` Edge Function (or manually create the `historical-maps` bucket in the Supabase Storage dashboard with public access and a 10MB file size limit).

9. **Update environment variables.**
   Replace the old Supabase URL and anon key with the new values in `street-etymology/.env.local`. Rebuild and redeploy the frontend.

10. **Update Supabase Auth redirect URLs** for the new project (Section 2.4).

**Expected recovery time:** 2-4 hours with full backups available; 4-8 hours if the OS OpenNames data must be re-imported.

---

## 7. Maintenance Schedule

### Weekly Tasks

- **Check Supabase usage dashboard.**
  Review database size, storage usage, Edge Function invocations, and Auth MAU against free-tier limits.

- **Review pending contributions.**
  Open `/admin` and process any contributions awaiting moderation (approve or reject). Aim to clear the queue within 7 days to maintain contributor trust.

- **Manual database backup.**
  Export `profiles`, `contributions`, `newsletter_subscribers`, and (monthly) `streets` to CSV (Section 1.5). Store securely off-platform.

---

### Monthly Tasks

- **Run a Lighthouse audit.**
  Open Chrome DevTools → Lighthouse and audit https://streetetymology.co.uk/ on:
  - Performance (target: 90+)
  - Accessibility (target: 95+)
  - SEO (target: 90+)
  Address any regressions identified.

- **Check dependency updates.**
  From `street-etymology/`:
  ```bash
  pnpm outdated
  ```
  Review and apply non-breaking updates. Pay particular attention to security advisories for `supabase-js`, `maplibre-gl`, and Vite.

- **Review error logs.**
  Check Supabase Edge Function logs (Section 2.5) for recurring errors. Review the browser console on the live site for any new JavaScript errors.

- **Review costs.**
  Check Supabase billing dashboard. Confirm total spend is within the Year 1 target of less than £20/month.

---

### Quarterly Tasks

- **OS OpenNames data refresh.**
  Download and import the latest OS OpenNames dataset to keep street records current (Section 4.1, full procedure in `docs/data/os-opennames-import.md`).

- **Database cleanup.**
  Delete rejected contributions older than 90 days (Section 4.2). Archive stale newsletter subscriber records (Section 4.3).

- **Review and update documentation.**
  Update this runbook, CLAUDE.md, and any relevant files in `docs/` to reflect changes in architecture, costs, or procedures.

- **Security review.**
  - Rotate the Supabase service role key if it has been shared with any third party.
  - Review RLS policies for the `streets`, `contributions`, and `profiles` tables.
  - Check for unused admin/moderator accounts and revoke access where appropriate.
  - Review the list of allowed redirect URLs in Supabase Auth settings.

- **Cost projection review.**
  Re-evaluate the MVP vs. Growth cost projections against actual usage. Reference `complete_street_etymology_website_setup.md` for Year 1/Year 2 cost breakdowns. Decide whether to upgrade Supabase plan or migrate any services.

---

*End of runbook. For architecture decisions and research background, see the `docs/` directory. For codebase guidance, see `CLAUDE.md`.*
