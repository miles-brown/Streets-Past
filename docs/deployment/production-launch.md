# Streets Past — Production Deployment Runbook

**Application:** Streets Past (https://streetetymology.co.uk/)
**Current live deployment:** https://6fv9t1y43vab.space.minimax.io
**Backend:** Supabase project `nadbmxfqknnnyuadhdtk` (https://nadbmxfqknnnyuadhdtk.supabase.co)
**Last updated:** 2026-03-04

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Supabase Project Setup](#2-supabase-project-setup)
3. [Edge Function Deployment](#3-edge-function-deployment)
4. [Frontend Build](#4-frontend-build)
5. [Hosting Deployment](#5-hosting-deployment)
6. [DNS and SSL Setup](#6-dns-and-ssl-setup)
7. [Post-Deployment Verification](#7-post-deployment-verification)
8. [Environment Management](#8-environment-management)
9. [Rollback Procedure](#9-rollback-procedure)

---

## 1. Prerequisites

### Accounts Required

| Service | Purpose | URL |
|---------|---------|-----|
| Supabase | Database, Auth, Storage, Edge Functions | https://supabase.com |
| Hosting provider | Static asset delivery (see Section 5) | see below |
| Domain registrar | `streetetymology.co.uk` | Namecheap or equivalent |
| Cloudflare (recommended) | DNS management + free SSL | https://cloudflare.com |

### Tools Required

Install the following on the machine performing the deployment:

```bash
# Node.js 18 or higher
node --version   # must be >= 18.0.0

# pnpm (install via npm if not present)
npm install -g pnpm
pnpm --version   # confirm installation

# Supabase CLI (used for edge function deployment and DB migrations)
npm install -g supabase
supabase --version   # confirm installation

# Git
git --version
```

The Supabase CLI requires Docker to be running on the local machine only for commands that start a local development instance (`supabase start`). Deploying to the hosted Supabase project via `supabase functions deploy` does not require Docker.

### Repository Access

```bash
git clone <repository-url> Streets-Past
cd Streets-Past
```

---

## 2. Supabase Project Setup

This section covers creating a fresh Supabase project. If deploying to the existing project (`nadbmxfqknnnyuadhdtk`), skip to Section 2.4 to verify extensions and run any pending migrations.

### 2.1 Create the Project

1. Log in to https://supabase.com/dashboard
2. Click **New project**
3. Set:
   - **Name:** `streets-past` (or preferred name)
   - **Database password:** generate a strong password and store it securely
   - **Region:** `eu-west-2` (London) — recommended for UK traffic
   - **Pricing plan:** Free tier is sufficient for MVP; upgrade to Pro ($25/month) when approaching 500 MB database storage or 50,000 MAU
4. Wait for provisioning (approximately 2 minutes)
5. Note the **Project URL** and **anon public key** from **Settings > API**

### 2.2 Enable PostGIS

PostGIS is required for spatial queries (latitude/longitude bounding boxes, proximity searches).

In the Supabase Dashboard, navigate to **Database > Extensions** and enable:

- `postgis` — spatial data types and operators

Alternatively, run in the **SQL Editor**:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 2.3 Create Core Tables

Run the following SQL in **Database > SQL Editor**. This creates the four core tables and the storage metadata table.

```sql
-- Profiles table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'moderator', 'admin')),
    contribution_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Streets table (~790k OS OpenNames records)
CREATE TABLE IF NOT EXISTS public.streets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    city TEXT,
    county TEXT,
    postcode TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    etymology_suggestion TEXT,
    etymology_verified BOOLEAN NOT NULL DEFAULT FALSE,
    historical_period TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Spatial index for map queries
CREATE INDEX IF NOT EXISTS streets_location_idx
    ON public.streets (latitude, longitude)
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- Full-text search index
CREATE INDEX IF NOT EXISTS streets_name_idx ON public.streets USING gin(to_tsvector('english', name));

-- Contributions table (user-submitted etymologies)
CREATE TABLE IF NOT EXISTS public.contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    street_id UUID NOT NULL REFERENCES public.streets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    etymology_text TEXT NOT NULL,
    sources TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Newsletter subscribers
CREATE TABLE IF NOT EXISTS public.newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    subscribed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Historical maps metadata
CREATE TABLE IF NOT EXISTS public.historical_maps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    street_id UUID REFERENCES public.streets(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    storage_path TEXT NOT NULL,
    uploaded_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2.4 Enable Row Level Security

```sql
-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.streets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.newsletter_subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.historical_maps ENABLE ROW LEVEL SECURITY;

-- Profiles: users can read all profiles, edit only their own
CREATE POLICY "Public profiles are viewable by everyone"
    ON public.profiles FOR SELECT USING (true);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Streets: publicly readable, only admins/moderators can write
CREATE POLICY "Streets are publicly readable"
    ON public.streets FOR SELECT USING (true);

CREATE POLICY "Admins and moderators can modify streets"
    ON public.streets FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE user_id = auth.uid()
            AND role IN ('admin', 'moderator')
        )
    );

-- Contributions: authenticated users can create; users see their own, admins see all
CREATE POLICY "Users can submit contributions"
    ON public.contributions FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own contributions"
    ON public.contributions FOR SELECT USING (
        auth.uid() = user_id OR
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE user_id = auth.uid()
            AND role IN ('admin', 'moderator')
        )
    );

CREATE POLICY "Admins can update contribution status"
    ON public.contributions FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE user_id = auth.uid()
            AND role IN ('admin', 'moderator')
        )
    );

-- Newsletter: anyone can subscribe
CREATE POLICY "Anyone can subscribe to newsletter"
    ON public.newsletter_subscribers FOR INSERT WITH CHECK (true);

-- Historical maps: publicly readable
CREATE POLICY "Historical maps are publicly readable"
    ON public.historical_maps FOR SELECT USING (true);
```

### 2.5 Create Profile Trigger

This trigger automatically creates a profile row when a new user registers via Supabase Auth:

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (user_id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name'
    )
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### 2.6 Link Supabase CLI to the Project

```bash
# Log in to Supabase CLI
supabase login

# Link CLI to the production project
# Run from the repository root (Streets-Past/)
supabase link --project-ref nadbmxfqknnnyuadhdtk
```

You will be prompted for the database password set during project creation.

---

## 3. Edge Function Deployment

Streets Past has two Supabase Edge Functions, both located in `supabase/functions/`. Edge Functions run on Deno and are deployed via the Supabase CLI.

### 3.1 Deploy suggest-etymology

This function accepts a POST request with `{ "streetName": string }` and returns an etymology suggestion using rule-based pattern matching (57 suffix patterns + 34 prefix patterns). It has no external dependencies and no environment variables beyond those auto-provided by Supabase.

```bash
# From the repository root (Streets-Past/)
supabase functions deploy suggest-etymology --project-ref nadbmxfqknnnyuadhdtk
```

Expected output: `Deployed Function suggest-etymology`

Test the deployed function:

```bash
curl -X POST \
  'https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/suggest-etymology' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <SUPABASE_ANON_KEY>' \
  -d '{"streetName": "Kirkgate"}'
```

A successful response looks like:

```json
{
  "data": {
    "streetName": "Kirkgate",
    "etymology": "\"Gate\" derives from Old Norse, meaning \"road, way, or street (from \"gata\")\" (Viking Age (793-1066)). \"Kirk\" derives from Old Norse, meaning \"church (Scottish/Northern)\" (Viking Age)...",
    "elements": [...],
    "confidence": "medium",
    "sources": [...]
  }
}
```

### 3.2 Deploy create-bucket-historical-maps-temp

This function creates the `historical-maps` storage bucket (public, 10 MB file limit, accepts `image/*` and `application/pdf`) and applies RLS policies. It is a one-time setup function.

```bash
supabase functions deploy create-bucket-historical-maps-temp --project-ref nadbmxfqknnnyuadhdtk
```

### 3.3 Invoke create-bucket-historical-maps-temp (One Time)

After deploying, invoke the function once to create the storage bucket:

```bash
curl -X POST \
  'https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/create-bucket-historical-maps-temp' \
  -H 'Authorization: Bearer <SUPABASE_ANON_KEY>'
```

A successful response:

```json
{
  "success": true,
  "message": "Bucket created successfully with public access policies",
  "bucket": {
    "name": "historical-maps",
    "public": true,
    "allowed_mime_types": ["image/*", "application/pdf"],
    "file_size_limit": 10485760,
    "policies": [...]
  }
}
```

If the bucket already exists, the function returns a `BUCKET_CREATION_FAILED` error with status 409 — this is expected and can be ignored on subsequent runs.

Confirm the bucket exists in the Supabase Dashboard under **Storage**.

---

## 4. Frontend Build

All commands run from the `street-etymology/` directory unless otherwise stated.

### 4.1 Clone and Navigate

```bash
git clone <repository-url> Streets-Past
cd Streets-Past/street-etymology
```

### 4.2 Configure Environment Variables

The environment template is at `street-etymology/.env.example`:

```
VITE_SUPABASE_URL=https://<project-id>.supabase.co
VITE_SUPABASE_ANON_KEY=<your-supabase-anon-key>
```

Copy it and fill in real values:

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```
VITE_SUPABASE_URL=https://nadbmxfqknnnyuadhdtk.supabase.co
VITE_SUPABASE_ANON_KEY=<anon_key_from_supabase_dashboard>
```

Retrieve the anon key from **Supabase Dashboard > Settings > API > Project API keys > anon public**.

**Important:** Never commit `.env.local` to version control. It is listed in `.gitignore`.

### 4.3 Install Dependencies

The `.npmrc` file redirects the pnpm store to `/tmp/.pnpm-store` — this is intentional for the deployment environment and must not be changed:

```
store-dir=/tmp/.pnpm-store
virtual-store-dir=/tmp/street-etymology/.pnpm
```

```bash
pnpm install
```

Note: the `build:prod` script runs `pnpm install --prefer-offline` automatically, so a separate install step is not strictly required before building.

### 4.4 Production Build

Use `build:prod`, not `build`, for all production deployments. The `build:prod` script sets `BUILD_MODE=prod`, which disables the `vite-plugin-source-identifier` plugin that injects `data-matrix` debug attributes into the DOM:

```bash
pnpm build:prod
```

This command:
1. Runs `pnpm install --prefer-offline`
2. Removes the Vite temp cache (`rm -rf node_modules/.vite-temp`)
3. Runs TypeScript type checking (`tsc -b`)
4. Runs `vite build` with `BUILD_MODE=prod`

Output is written to `street-etymology/dist/`.

### 4.5 Verify the Build

```bash
# Preview the production build locally
pnpm preview
```

Open http://localhost:4173 and confirm the home page loads. Then proceed to upload `dist/` to the hosting provider.

---

## 5. Hosting Deployment

The build output is the `street-etymology/dist/` directory (a standard single-page application). Because this is a React Router SPA, all hosting providers must be configured to serve `index.html` for all routes (the "rewrite all to index.html" pattern).

### 5.1 Cloudflare Pages (Recommended)

Cloudflare Pages is the recommended platform based on project research. Static asset delivery is unlimited, global CDN is included, free SSL is automatic, and up to 100 custom domains are supported per project.

**Limits to be aware of:**
- 20,000 files per deployment
- 25 MiB per file
- 500 builds/month on the free plan

**Deploy via Git integration (recommended):**

1. Log in to https://dash.cloudflare.com and go to **Workers & Pages > Create > Pages**
2. Connect your Git provider and select the `Streets-Past` repository
3. Set the build configuration:
   - **Framework preset:** None (custom)
   - **Build command:** `cd street-etymology && pnpm build:prod`
   - **Build output directory:** `street-etymology/dist`
   - **Root directory:** `/` (repository root)
4. Add environment variables:
   - `VITE_SUPABASE_URL` = `https://nadbmxfqknnnyuadhdtk.supabase.co`
   - `VITE_SUPABASE_ANON_KEY` = `<anon key>`
5. Click **Save and Deploy**

**Configure SPA routing** — create `street-etymology/public/_redirects`:

```
/*  /index.html  200
```

This file is automatically copied into `dist/` by Vite if placed in `public/`. Cloudflare Pages respects the Netlify-compatible `_redirects` syntax.

**Deploy via direct upload (manual):**

```bash
# Install Wrangler CLI
npm install -g wrangler

# Authenticate
wrangler login

# Deploy dist directory directly
wrangler pages deploy street-etymology/dist --project-name=streets-past
```

### 5.2 Netlify

1. Install the Netlify CLI:
   ```bash
   npm install -g netlify-cli
   netlify login
   ```

2. From the repository root, initialise and deploy:
   ```bash
   netlify init
   netlify deploy --dir=street-etymology/dist --prod
   ```

3. Or connect via the Netlify Dashboard (https://app.netlify.com):
   - **Base directory:** `street-etymology`
   - **Build command:** `pnpm build:prod`
   - **Publish directory:** `street-etymology/dist`

4. Add environment variables in **Site settings > Environment variables**.

5. Create `street-etymology/public/_redirects` for SPA routing:
   ```
   /*  /index.html  200
   ```

6. Alternatively, create `street-etymology/public/netlify.toml` at the repository root:
   ```toml
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

### 5.3 Vercel

Note: the Vercel Hobby plan restricts commercial use. If the site generates revenue, a Pro plan is required.

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   vercel login
   ```

2. From `street-etymology/`:
   ```bash
   vercel --prod
   ```

3. Or connect via https://vercel.com/new:
   - **Framework preset:** Vite
   - **Root directory:** `street-etymology`
   - **Build command:** `pnpm build:prod`
   - **Output directory:** `dist`

4. Add environment variables in **Project Settings > Environment Variables**.

5. Create `street-etymology/vercel.json` for SPA routing:
   ```json
   {
     "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
   }
   ```

### 5.4 MiniMax (Current Host)

The application is currently live on MiniMax at https://6fv9t1y43vab.space.minimax.io.

To deploy an updated build to MiniMax:

1. Build the production artifact:
   ```bash
   cd street-etymology
   pnpm build:prod
   ```

2. Upload the contents of `street-etymology/dist/` via the MiniMax hosting dashboard or CLI following MiniMax platform documentation.

3. Ensure the MiniMax project is configured to serve `index.html` for all unmatched routes (SPA mode).

---

## 6. DNS and SSL Setup

### 6.1 Cloudflare DNS Setup (Recommended)

Cloudflare provides free SSL via its proxy and is the recommended DNS provider.

1. Log in to https://dash.cloudflare.com, click **Add a Site**, enter `streetetymology.co.uk`
2. Select the **Free plan**
3. Cloudflare scans existing DNS records — review and confirm
4. At your domain registrar (e.g., Namecheap), update the nameservers to the two Cloudflare nameservers shown (e.g., `alice.ns.cloudflare.com`, `bob.ns.cloudflare.com`)
5. DNS propagation takes up to 48 hours, but typically resolves within 1 hour

**Add DNS records** in Cloudflare:

For Cloudflare Pages:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `@` | `<project>.pages.dev` | Proxied (orange cloud) |
| CNAME | `www` | `<project>.pages.dev` | Proxied (orange cloud) |

For Netlify:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `@` | `<project>.netlify.app` | Proxied |
| CNAME | `www` | `<project>.netlify.app` | Proxied |

**SSL settings** in Cloudflare under **SSL/TLS**:
- Set encryption mode to **Full (strict)**
- Enable **Always Use HTTPS**
- Enable **Automatic HTTPS Rewrites**

### 6.2 Without Cloudflare (Let's Encrypt via Hosting Provider)

All four hosting providers (Cloudflare Pages, Netlify, Vercel, MiniMax) provision free TLS certificates automatically via Let's Encrypt when a custom domain is added through their dashboards. No manual certificate management is required.

To add the custom domain:

- **Cloudflare Pages:** Pages dashboard > Custom domains > Add custom domain > `streetetymology.co.uk`
- **Netlify:** Site settings > Domain management > Add custom domain
- **Vercel:** Project settings > Domains > Add

After adding the domain, update your domain registrar's DNS to point to the provider:

- For Netlify, add a CNAME record pointing `www` to `<project>.netlify.app` and an ALIAS/ANAME for the apex (`@`)
- For Vercel, follow the CNAME or A record instructions shown in the Vercel dashboard

---

## 7. Post-Deployment Verification

Run through this checklist after every production deployment. Check both the canonical domain (`streetetymology.co.uk`) and the MiniMax URL (`6fv9t1y43vab.space.minimax.io`) during transition.

### 7.1 Core Pages

- [ ] **Homepage** (`/`) loads without console errors; amber/heritage colour scheme renders correctly
- [ ] **About page** (`/about`) loads
- [ ] **Privacy page** (`/privacy`) loads
- [ ] **Terms page** (`/terms`) loads
- [ ] **404 handling** — navigate to a non-existent path (e.g., `/does-not-exist`); confirm the SPA handles it gracefully rather than serving an HTML 404 from the host

### 7.2 Search

- [ ] Navigate to `/search`
- [ ] Type a partial street name (e.g., "Kirk") — autocomplete results appear within ~500ms
- [ ] Selecting a result navigates to `/street/:id`
- [ ] The street detail page displays name, etymology suggestion, and location information
- [ ] Navigating to `/contribute` also loads the search interface (it reuses `SearchPage`)

### 7.3 Interactive Map

- [ ] Navigate to `/map`
- [ ] MapLibre GL JS renders (no blank canvas, no WebGL errors in console)
- [ ] OpenStreetMap raster tiles load and display
- [ ] Map is centred on the UK (`[-2.5, 54.0]`, zoom ~5.5)
- [ ] Street markers appear (amber gradient style) for streets with coordinates
- [ ] Clicking a marker opens a popup with street name and etymology snippet

### 7.4 Authentication Flow

- [ ] Navigate to `/register` — form renders with no layout chrome (no Header/Footer)
- [ ] Register a new test account with a real email
- [ ] Check email for Supabase confirmation link; click it
- [ ] After confirmation, `/auth/callback` redirects to the homepage
- [ ] Navigate to `/login` and sign in with the new account
- [ ] User avatar or name appears in the Header
- [ ] Navigate to `/profile` — profile page loads for the authenticated user
- [ ] Sign out — unauthenticated state restored

### 7.5 Edge Function (suggest-etymology)

- [ ] Visit a street detail page at `/street/:id`
- [ ] Confirm that the etymology suggestion section is populated (sourced from the `suggest-etymology` Edge Function or from the `etymology_suggestion` column)
- [ ] Alternatively, test directly:
  ```bash
  curl -X POST \
    'https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/suggest-etymology' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer <SUPABASE_ANON_KEY>' \
    -d '{"streetName": "High Street"}'
  ```
  Expected: 200 response with `confidence: "medium"` and element matches for "high" and "street"

### 7.6 Admin Dashboard

- [ ] Using an account with `role = 'admin'` or `role = 'moderator'` in the `profiles` table, navigate to `/admin`
- [ ] Dashboard loads and displays pending contributions
- [ ] Approve or reject a test contribution to confirm the status update writes to Supabase

To grant admin role to a user (run in Supabase SQL Editor):

```sql
UPDATE public.profiles
SET role = 'admin'
WHERE email = 'your-admin-email@example.com';
```

### 7.7 SSL and Performance

- [ ] `https://streetetymology.co.uk/` redirects correctly (no HTTP, no mixed content warnings)
- [ ] Browser shows padlock / secure connection
- [ ] Open DevTools Network tab — no requests to HTTP endpoints
- [ ] Check `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are not accidentally exposed in `dist/index.html` as plaintext (they will appear in the bundled JS, which is expected, but should not appear in `<meta>` tags or similar)

---

## 8. Environment Management

### 8.1 Environment Variables

The frontend uses two Vite environment variables, both prefixed with `VITE_` (required for Vite to expose them to the browser bundle):

| Variable | Description | Where to find |
|----------|-------------|---------------|
| `VITE_SUPABASE_URL` | Supabase project REST endpoint | Dashboard > Settings > API > Project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous/public key | Dashboard > Settings > API > anon public |

Edge Functions (`suggest-etymology`, `create-bucket-historical-maps-temp`) use:

| Variable | Description | Provided by |
|----------|-------------|-------------|
| `SUPABASE_URL` | Supabase project URL | Auto-injected by Supabase runtime |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (admin access) | Auto-injected by Supabase runtime |

The service role key is never needed in the frontend and must never be exposed in client-side code or `dist/`.

### 8.2 Staging vs Production

Maintain two separate Supabase projects for staging and production:

| Environment | Supabase Project | Frontend URL | `.env` file |
|-------------|-----------------|--------------|-------------|
| Production | `nadbmxfqknnnyuadhdtk` | `streetetymology.co.uk` | `.env.local` (gitignored) |
| Staging | `<staging-project-ref>` | staging branch preview URL | `.env.staging` (gitignored) |

To build against the staging Supabase project:

```bash
VITE_SUPABASE_URL=https://<staging-ref>.supabase.co \
VITE_SUPABASE_ANON_KEY=<staging-anon-key> \
BUILD_MODE=prod \
pnpm build:prod
```

On Cloudflare Pages, create a separate Pages project connected to a `staging` branch and configure the staging environment variables there. Preview deployments on every pull request automatically use the preview environment.

### 8.3 Managing Environment Variables in Hosting Providers

Never store environment variable values in the repository. Set them in the hosting provider dashboard:

- **Cloudflare Pages:** Pages project > Settings > Environment variables
  - Add variables for both Production and Preview environments separately
- **Netlify:** Site settings > Build & deploy > Environment variables
- **Vercel:** Project settings > Environment variables (scope to Production / Preview / Development)

To rotate the Supabase anon key:

1. Generate a new key in **Supabase Dashboard > Settings > API**
2. Update the environment variable in the hosting provider dashboard
3. Trigger a new deployment to rebuild and re-bundle the updated key

---

## 9. Rollback Procedure

### 9.1 Rollback a Frontend Deployment

**Cloudflare Pages:**

Cloudflare Pages retains all historical deployments. To revert:

1. Go to **Workers & Pages > streets-past > Deployments**
2. Find the last known-good deployment
3. Click the three-dot menu > **Rollback to this deployment**

The rollback is instant (switching traffic to the previous build artifact).

**Netlify:**

1. Go to **Deploys** in the Netlify dashboard
2. Find the last known-good deploy
3. Click **Publish deploy**

**Vercel:**

1. Go to **Deployments** in the Vercel dashboard
2. Find the last known-good deployment
3. Click the three-dot menu > **Promote to Production**

**MiniMax:**

Re-upload the previous `dist/` artifact via the MiniMax dashboard. Keep a local archive of each production build:

```bash
# Archive before each deployment
tar -czf dist-$(date +%Y%m%d-%H%M%S).tar.gz street-etymology/dist/
```

### 9.2 Rollback a Bad Database Migration

If a schema migration breaks the application:

1. **Identify the migration** causing the issue in Supabase SQL history (**Database > Backups** or via `supabase migration list`)

2. **Revert the migration** by running the inverse SQL in the SQL Editor. For example, if you added a column:
   ```sql
   ALTER TABLE public.streets DROP COLUMN IF EXISTS new_column;
   ```

3. **Point-in-time restore** (Supabase Pro plan): If the migration caused data loss and you are on the Pro plan, use **Database > Backups** to restore to a specific timestamp. Note that this overwrites all data written since the restore point.

### 9.3 Rollback an Edge Function

Supabase does not retain previous versions of Edge Functions. To roll back:

1. Check out the previous version of the function from Git:
   ```bash
   git log supabase/functions/suggest-etymology/index.ts   # find last good commit
   git checkout <commit-hash> -- supabase/functions/suggest-etymology/index.ts
   ```

2. Redeploy:
   ```bash
   supabase functions deploy suggest-etymology --project-ref nadbmxfqknnnyuadhdtk
   ```

3. Commit the revert if it needs to be permanent:
   ```bash
   git add supabase/functions/suggest-etymology/index.ts
   git commit -m "revert suggest-etymology to <commit-hash>"
   ```

### 9.4 Emergency Contacts and Resources

| Resource | URL |
|----------|-----|
| Supabase status | https://status.supabase.com |
| Cloudflare status | https://www.cloudflarestatus.com |
| Supabase Dashboard | https://supabase.com/dashboard/project/nadbmxfqknnnyuadhdtk |
| MiniMax deployment | https://6fv9t1y43vab.space.minimax.io |
| Canonical domain | https://streetetymology.co.uk |
