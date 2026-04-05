# Streets Past — Database Schema

**Supabase project ID:** `nadbmxfqknnnyuadhdtk`
**Runtime:** PostgreSQL 15 with PostGIS extension
**Derived from:** Source code audit of `street-etymology/src/` (all pages, components, and contexts), plus `supabase/functions/` edge function code.
**Date documented:** 2026-04-05

---

## Table of Contents

1. [Extension Setup](#1-extension-setup)
2. [Table: streets](#2-table-streets)
3. [Table: contributions](#3-table-contributions)
4. [Table: profiles](#4-table-profiles)
5. [Table: newsletter_subscribers](#5-table-newsletter_subscribers)
6. [Table: historical_maps](#6-table-historical_maps)
7. [Table: saved_streets](#7-table-saved_streets)
8. [Indexes](#8-indexes)
9. [Row Level Security Policies](#9-row-level-security-policies)
10. [Storage Bucket: historical-maps](#10-storage-bucket-historical-maps)
11. [Source Confidence Notes](#11-source-confidence-notes)

---

## 1. Extension Setup

```sql
-- Required for spatial queries (latitude/longitude filtering and future geometry columns)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Required for UUID generation (used as primary keys by Supabase Auth and profile tables)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## 2. Table: streets

The primary data table. Sourced from OS OpenNames (~790,000 street records under OGL v3.0). All columns confirmed by direct inspection of `SearchBar.tsx`, `MapView.tsx`, `StreetDetailPage.tsx`, `SearchPage.tsx`, `AdminPage.tsx`, and `HomePage.tsx`.

```sql
CREATE TABLE streets (
    -- Primary key: referenced as street.id throughout the codebase.
    -- Type is text (not uuid) because OS OpenNames identifiers are alphanumeric strings.
    -- Confirmed: .eq('id', id) where id comes from useParams<{ id: string }>()
    id                  TEXT PRIMARY KEY,

    -- Street name. Required. Used in .ilike('name', ...) for search.
    name                TEXT NOT NULL,

    -- Settlement / postal town. Nullable. Used in display and filter dropdowns.
    -- Confirmed: .not('city', 'is', null), s.city filter in SearchPage.
    city                TEXT,

    -- Administrative county. Nullable. Used in filter dropdowns.
    -- Confirmed: s.county filter in SearchPage.
    county              TEXT,

    -- Postcode district prefix (e.g. "SW1", "M1"). Nullable.
    -- IMPORTANT: The column is named postcode_area, NOT postcode.
    -- Confirmed by: street.postcode_area in SearchBar.tsx line 137,
    --               StreetDetailPage.tsx line 113, SearchPage.tsx line 294.
    postcode_area       TEXT,

    -- WGS-84 decimal degrees latitude. Nullable.
    -- Confirmed: .not('latitude', 'is', null) in MapView.tsx.
    -- Used with street.latitude.toFixed(4) so must be numeric, not text.
    latitude            DOUBLE PRECISION,

    -- WGS-84 decimal degrees longitude. Nullable.
    -- Confirmed: .not('longitude', 'is', null) in MapView.tsx.
    longitude           DOUBLE PRECISION,

    -- AI-generated or human-authored etymology text. Nullable.
    -- Written by: AdminPage.tsx approve handler (copies from contribution).
    -- Read by: SearchBar, SearchPage, MapView popup, StreetDetailPage, HomePage.
    etymology_suggestion TEXT,

    -- Whether the etymology has been verified by a moderator/admin. Nullable (treated as falsy when null).
    -- Confirmed: .eq('etymology_verified', true) in HomePage; street.etymology_verified boolean checks throughout.
    etymology_verified  BOOLEAN DEFAULT FALSE,

    -- Citation or reference for the etymology text. Nullable.
    -- Confirmed: street.etymology_source rendered in StreetDetailPage.tsx line 265.
    etymology_source    TEXT,

    -- Free-text date or date range for first recorded use of the street name. Nullable.
    -- Stored as text because historical dates are often imprecise (e.g. "circa 1350", "13th century").
    -- Confirmed: street.first_recorded_date in StreetDetailPage.tsx line 121,
    --            SearchPage.tsx sort by 'date' uses first_recorded_date.localeCompare().
    first_recorded_date TEXT,

    -- Supplementary historical context. Nullable.
    -- Confirmed: street.historical_notes in StreetDetailPage.tsx line 291.
    historical_notes    TEXT,

    -- Broad historical era label (e.g. "Medieval", "Victorian", "Roman"). Nullable.
    -- Confirmed: Street type and StreetDetailPage.tsx render when non-null.
    historical_period   TEXT,

    -- Audit timestamps.
    -- updated_at confirmed: AdminPage.tsx line 102 sets updated_at: new Date().toISOString()
    --                        ProfilePage.tsx line 89 sets updated_at: new Date().toISOString()
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Trigger: auto-update updated_at

```sql
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER streets_set_updated_at
    BEFORE UPDATE ON streets
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
```

---

## 3. Table: contributions

Community-submitted etymology suggestions awaiting moderator review. All columns confirmed by direct inspection of `ContributionForm.tsx`, `AdminPage.tsx`, `StreetDetailPage.tsx`, and `ProfilePage.tsx`.

```sql
CREATE TABLE contributions (
    -- Primary key. UUID generated by Supabase.
    -- Confirmed: contribution.id used as React key and in .eq('id', contribution.id).
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign key to streets. Required for every contribution.
    -- Confirmed: ContributionForm.tsx inserts street_id: streetId (a string prop).
    --            AdminPage.tsx uses c.street_id in .in('id', streetIds).
    street_id           TEXT NOT NULL REFERENCES streets(id) ON DELETE CASCADE,

    -- Supabase Auth user UUID. Nullable — anonymous submissions are allowed.
    -- Confirmed: ContributionForm.tsx inserts user_id: user?.id || null
    user_id             UUID REFERENCES auth.users(id) ON DELETE SET NULL,

    -- Submitter email. Always populated (from logged-in user or manual entry).
    -- Confirmed: ContributionForm.tsx inserts user_email: submitterEmail.
    --            AdminPage.tsx displays contribution.user_email.
    --            ProfilePage.tsx queries .eq('user_email', user.email).
    user_email          TEXT NOT NULL,

    -- The contributed etymology text. Required.
    -- Confirmed: ContributionForm.tsx inserts etymology_suggestion: etymology.trim()
    --            AdminPage.tsx copies this value to streets.etymology_suggestion on approve.
    etymology_suggestion TEXT NOT NULL,

    -- Optional citations. Nullable when not provided.
    -- Confirmed: ContributionForm.tsx inserts sources: sources.trim() || null
    --            AdminPage.tsx renders contribution.sources.
    sources             TEXT,

    -- Moderation status. One of: 'pending', 'approved', 'rejected'.
    -- Confirmed: ContributionForm.tsx inserts status: 'pending'.
    --            AdminPage.tsx updates to 'approved' or 'rejected'.
    --            StreetDetailPage.tsx queries .eq('status', 'approved').
    --            AdminPage.tsx filter uses all three values.
    status              TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'approved', 'rejected')),

    -- Timestamp set when a moderator approves or rejects the contribution. Nullable until reviewed.
    -- Confirmed: AdminPage.tsx sets reviewed_at: new Date().toISOString() on both approve and reject.
    reviewed_at         TIMESTAMPTZ,

    -- Submission timestamp. Used for ordering.
    -- Confirmed: .order('created_at', { ascending: false }) in StreetDetailPage and AdminPage.
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 4. Table: profiles

One profile row per registered user. Created synchronously during `signUp()` in `AuthContext.tsx`. Looked up by `user_id` on every auth state change.

```sql
CREATE TABLE profiles (
    -- Primary key is the Supabase Auth user UUID, not a separate serial/uuid column.
    -- Confirmed: .eq('user_id', user.id) in AuthContext.tsx; insert uses user_id: data.user.id.
    user_id             UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- User's email address, denormalised from auth.users for convenience.
    -- Confirmed: AuthContext.tsx inserts email: email.
    email               TEXT NOT NULL,

    -- Display name. Optional at registration.
    -- Confirmed: AuthContext.tsx inserts full_name: fullName || null.
    --            ProfilePage.tsx updates full_name and reads profile?.full_name.
    full_name           TEXT,

    -- Access control role. One of: 'user', 'moderator', 'admin'.
    -- Confirmed: AuthContext.tsx inserts role: 'user'; isAdmin checks role === 'admin' || 'moderator'.
    role                TEXT NOT NULL DEFAULT 'user'
                        CHECK (role IN ('user', 'moderator', 'admin')),

    -- Running count of accepted contributions. Default 0 at registration.
    -- Confirmed: AuthContext.tsx inserts contribution_count: 0.
    -- Note: incrementing this counter is not performed in the current frontend code;
    -- it is likely updated by a database trigger or manually by admins.
    contribution_count  INTEGER NOT NULL DEFAULT 0,

    -- Audit timestamp. Updated when user edits their profile.
    -- Confirmed: ProfilePage.tsx sets updated_at: new Date().toISOString() on profile save.
    -- created_at is not directly written by frontend code but is implied by the insert pattern.
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER profiles_set_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
```

### Trigger: auto-create profile on user sign-up (alternative to application-level insert)

The current implementation creates the profile in `AuthContext.tsx` at the application layer. A database trigger is an alternative / fallback approach that makes profile creation atomic:

```sql
-- OPTIONAL: server-side fallback trigger (supplement to app-level insert in AuthContext.tsx)
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (user_id, email, full_name, role, contribution_count)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data ->> 'full_name',
        'user',
        0
    )
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

---

## 5. Table: newsletter_subscribers

Minimal subscription table. Only `email` is inserted from `NewsletterSignup.tsx`. The duplicate-key error code `23505` is explicitly handled in the component, confirming the unique constraint on `email`.

```sql
CREATE TABLE newsletter_subscribers (
    -- Surrogate primary key.
    id          BIGSERIAL PRIMARY KEY,

    -- Subscriber email address. Must be unique.
    -- Confirmed: NewsletterSignup.tsx inserts { email: email.trim().toLowerCase() }.
    --            Error code 23505 (unique_violation) is handled explicitly.
    email       TEXT NOT NULL UNIQUE,

    -- Subscription timestamp.
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 6. Table: historical_maps

Mentioned in CLAUDE.md as a core table. Not accessed by any frontend component code found in the repository (no Supabase query targeting `historical_maps` exists in `src/`). The storage bucket `historical-maps` holds the actual image/PDF files; this table stores associated metadata.

```sql
-- INFERRED schema — no frontend column references found in source code.
-- Column names and types are derived from the CLAUDE.md description only.
-- Treat every column except id and created_at as unconfirmed.
CREATE TABLE historical_maps (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- The street this historical map depicts. Nullable — a map may cover a wider area.
    street_id   TEXT REFERENCES streets(id) ON DELETE SET NULL,

    -- Storage object path within the historical-maps bucket.
    storage_path TEXT NOT NULL,

    -- Human-readable title or description of the map image.
    title       TEXT,

    -- Approximate year or date range the map depicts (free text).
    map_date    TEXT,

    -- MIME type of the file (image/* or application/pdf per bucket config).
    mime_type   TEXT,

    -- File size in bytes.
    file_size   INTEGER,

    -- Who uploaded the map.
    uploaded_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,

    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 7. Table: saved_streets

User-specific bookmarks for “My atlas”. Authenticated users insert/delete their own rows; each user can only `SELECT` their own saves. Schema matches [`supabase/migrations/20260405120000_saved_streets.sql`](../../supabase/migrations/20260405120000_saved_streets.sql) (duplicate for manual runs: [`scripts/apply-saved-streets.sql`](../../scripts/apply-saved-streets.sql)).

`street_id` is **TEXT** and references `streets(id)` (OS OpenNames-style string identifiers).

```sql
CREATE TABLE saved_streets (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    street_id   TEXT NOT NULL REFERENCES streets(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, street_id)
);

CREATE INDEX saved_streets_user_id_idx ON saved_streets (user_id);
CREATE INDEX saved_streets_street_id_idx ON saved_streets (street_id);
```

### Row Level Security (summary)

- RLS enabled on `saved_streets`.
- Policies: authenticated users may `SELECT`, `INSERT`, and `DELETE` only where `auth.uid() = user_id`.
- `GRANT SELECT, INSERT, DELETE ON saved_streets TO authenticated`.

---

## 8. Indexes

### streets

```sql
-- Full-text / pattern search on street name (used by SearchBar ilike query and SearchPage filter).
-- A GIN trig index accelerates ILIKE '%query%' patterns on PostgreSQL.
CREATE INDEX idx_streets_name_trgm
    ON streets USING GIN (name gin_trgm_ops);
-- Requires: CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Simple B-tree for equality / ordering on name (used by .order('name')).
CREATE INDEX idx_streets_name ON streets (name);

-- Filter indexes for SearchPage dropdowns.
CREATE INDEX idx_streets_city    ON streets (city)    WHERE city IS NOT NULL;
CREATE INDEX idx_streets_county  ON streets (county)  WHERE county IS NOT NULL;
CREATE INDEX idx_streets_postcode_area ON streets (postcode_area) WHERE postcode_area IS NOT NULL;

-- Filter index for verified etymology (used in HomePage featured streets query).
CREATE INDEX idx_streets_etymology_verified
    ON streets (etymology_verified)
    WHERE etymology_verified = TRUE;

-- Spatial index for map queries (latitude/longitude not-null filter in MapView).
-- If a PostGIS geometry column is added in future, replace with GIST index.
CREATE INDEX idx_streets_latitude  ON streets (latitude)  WHERE latitude  IS NOT NULL;
CREATE INDEX idx_streets_longitude ON streets (longitude) WHERE longitude IS NOT NULL;
```

### contributions

```sql
-- Most common query pattern: filter by street_id, then by status.
CREATE INDEX idx_contributions_street_id ON contributions (street_id);
CREATE INDEX idx_contributions_status    ON contributions (status);

-- AdminPage and StreetDetailPage both order by created_at DESC.
CREATE INDEX idx_contributions_created_at ON contributions (created_at DESC);

-- ProfilePage queries by user_email.
CREATE INDEX idx_contributions_user_email ON contributions (user_email);

-- Optional: composite index for the approved contributions query on StreetDetailPage.
-- .eq('street_id', id).eq('status', 'approved').order('created_at', { ascending: false })
CREATE INDEX idx_contributions_street_status_date
    ON contributions (street_id, status, created_at DESC);
```

### profiles

```sql
-- Primary key user_id is already indexed. Email lookup for uniqueness checks.
CREATE INDEX idx_profiles_email ON profiles (email);
```

### newsletter_subscribers

```sql
-- email has a UNIQUE constraint which creates an implicit index; no additional index needed.
```

### historical_maps

```sql
CREATE INDEX idx_historical_maps_street_id ON historical_maps (street_id)
    WHERE street_id IS NOT NULL;
```

### saved_streets

```sql
CREATE INDEX saved_streets_user_id_idx ON saved_streets (user_id);
CREATE INDEX saved_streets_street_id_idx ON saved_streets (street_id);
```

---

## 9. Row Level Security Policies

All tables use Supabase's built-in RLS. The auth patterns are confirmed from `AuthContext.tsx` (role check: `profile.role === 'admin' || 'moderator'`), `ContributionForm.tsx` (anonymous insert allowed), and `StreetDetailPage.tsx` (public read).

### Enable RLS

```sql
ALTER TABLE streets               ENABLE ROW LEVEL SECURITY;
ALTER TABLE contributions         ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles              ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE historical_maps       ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_streets         ENABLE ROW LEVEL SECURITY;
```

### streets policies

```sql
-- Anyone (including unauthenticated visitors) can read streets.
CREATE POLICY "streets_public_read"
    ON streets FOR SELECT
    USING (true);

-- Only admins and moderators can insert, update, or delete street records.
-- Role is stored in the profiles table, joined via auth.uid().
CREATE POLICY "streets_admin_insert"
    ON streets FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role IN ('admin', 'moderator')
        )
    );

CREATE POLICY "streets_admin_update"
    ON streets FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role IN ('admin', 'moderator')
        )
    );

CREATE POLICY "streets_admin_delete"
    ON streets FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role IN ('admin', 'moderator')
        )
    );
```

### contributions policies

```sql
-- Admins and moderators can read all contributions regardless of status.
CREATE POLICY "contributions_admin_read_all"
    ON contributions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role IN ('admin', 'moderator')
        )
    );

-- Authenticated users can read their own contributions (any status).
CREATE POLICY "contributions_owner_read"
    ON contributions FOR SELECT
    USING (
        auth.uid() IS NOT NULL
        AND user_id = auth.uid()
    );

-- Anyone can read approved contributions (displayed publicly on StreetDetailPage).
CREATE POLICY "contributions_public_read_approved"
    ON contributions FOR SELECT
    USING (status = 'approved');

-- Anyone (authenticated or anonymous) can insert a contribution.
-- This is confirmed by ContributionForm.tsx: user_id is null for anonymous users,
-- but the insert is still performed without an auth check.
CREATE POLICY "contributions_public_insert"
    ON contributions FOR INSERT
    WITH CHECK (true);

-- Only admins and moderators can update contributions (approve / reject workflow).
CREATE POLICY "contributions_admin_update"
    ON contributions FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role IN ('admin', 'moderator')
        )
    );

-- Only admins can delete contributions.
CREATE POLICY "contributions_admin_delete"
    ON contributions FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role = 'admin'
        )
    );
```

### profiles policies

```sql
-- Authenticated users can read their own profile.
-- AuthContext.tsx fetches profile with .eq('user_id', user.id).
CREATE POLICY "profiles_owner_read"
    ON profiles FOR SELECT
    USING (auth.uid() = user_id);

-- Admins can read all profiles.
CREATE POLICY "profiles_admin_read_all"
    ON profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles p2
            WHERE p2.user_id = auth.uid()
              AND p2.role = 'admin'
        )
    );

-- Authenticated users can insert their own profile only.
-- AuthContext.tsx calls .insert({ user_id: data.user.id, ... }) immediately after signUp.
CREATE POLICY "profiles_owner_insert"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Authenticated users can update their own profile (full_name, updated_at).
-- Confirmed: ProfilePage.tsx calls .update({ full_name, updated_at }).eq('user_id', user.id).
CREATE POLICY "profiles_owner_update"
    ON profiles FOR UPDATE
    USING (auth.uid() = user_id);

-- Only admins can change roles or delete profiles.
CREATE POLICY "profiles_admin_update"
    ON profiles FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles p2
            WHERE p2.user_id = auth.uid()
              AND p2.role = 'admin'
        )
    );

CREATE POLICY "profiles_admin_delete"
    ON profiles FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM profiles p2
            WHERE p2.user_id = auth.uid()
              AND p2.role = 'admin'
        )
    );
```

### newsletter_subscribers policies

```sql
-- Anyone can subscribe (insert their email).
-- Confirmed: NewsletterSignup.tsx inserts without auth check.
CREATE POLICY "newsletter_public_insert"
    ON newsletter_subscribers FOR INSERT
    WITH CHECK (true);

-- Only admins can read the subscriber list.
CREATE POLICY "newsletter_admin_read"
    ON newsletter_subscribers FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role = 'admin'
        )
    );

-- Only admins can delete subscribers (unsubscribe management).
CREATE POLICY "newsletter_admin_delete"
    ON newsletter_subscribers FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role = 'admin'
        )
    );
```

### historical_maps policies

```sql
-- Public read (maps are display assets).
CREATE POLICY "historical_maps_public_read"
    ON historical_maps FOR SELECT
    USING (true);

-- Authenticated users can upload maps (insert metadata).
CREATE POLICY "historical_maps_auth_insert"
    ON historical_maps FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

-- Admins and moderators can update or delete map metadata.
CREATE POLICY "historical_maps_admin_update"
    ON historical_maps FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role IN ('admin', 'moderator')
        )
    );

CREATE POLICY "historical_maps_admin_delete"
    ON historical_maps FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role IN ('admin', 'moderator')
        )
    );
```

### saved_streets policies

```sql
CREATE POLICY "saved_streets_select_own"
    ON saved_streets FOR SELECT
    TO authenticated
    USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "saved_streets_insert_own"
    ON saved_streets FOR INSERT
    TO authenticated
    WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "saved_streets_delete_own"
    ON saved_streets FOR DELETE
    TO authenticated
    USING ((SELECT auth.uid()) = user_id);

GRANT SELECT, INSERT, DELETE ON TABLE saved_streets TO authenticated;
```

---

## 10. Storage Bucket: historical-maps

Configuration confirmed from `supabase/functions/create-bucket-historical-maps-temp/index.ts`.

| Property | Value |
|---|---|
| Bucket ID | `historical-maps` |
| Bucket name | `historical-maps` |
| Public | `true` |
| Allowed MIME types | `image/*`, `application/pdf` |
| File size limit | `10485760` bytes (10 MB) |

The edge function (`create-bucket-historical-maps-temp`) creates this bucket programmatically via the Supabase Storage REST API and attempts to apply four storage object policies (SELECT, INSERT, UPDATE, DELETE) scoped to `bucket_id = 'historical-maps'`. Because the function uses fully open policies (no auth check), the production deployment should replace these with appropriately restricted policies:

```sql
-- Recommended production storage policies (replacing the open policies created by the edge function)

-- Public can view any file in the bucket (bucket is public).
CREATE POLICY "historical_maps_storage_public_read"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'historical-maps');

-- Authenticated users can upload files.
CREATE POLICY "historical_maps_storage_auth_insert"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'historical-maps'
        AND auth.uid() IS NOT NULL
    );

-- Admins and moderators can replace or delete files.
CREATE POLICY "historical_maps_storage_admin_update"
    ON storage.objects FOR UPDATE
    USING (
        bucket_id = 'historical-maps'
        AND EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role IN ('admin', 'moderator')
        )
    );

CREATE POLICY "historical_maps_storage_admin_delete"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'historical-maps'
        AND EXISTS (
            SELECT 1 FROM profiles
            WHERE user_id = auth.uid()
              AND role IN ('admin', 'moderator')
        )
    );
```

---

## 11. Source Confidence Notes

The schema above was derived entirely from reading the frontend TypeScript source code. This section records where each design decision comes from and what level of confidence to assign.

### Confirmed from code (high confidence)

| Column | Evidence location |
|---|---|
| `streets.id` (text PK) | `useParams<{ id: string }>()` → `.eq('id', id)` in StreetDetailPage.tsx |
| `streets.name` | `.ilike('name', ...)` in SearchBar.tsx; `.order('name')` in SearchPage.tsx |
| `streets.city` | displayed and filtered in SearchBar.tsx:137, SearchPage.tsx:43-44 |
| `streets.county` | displayed and filtered in SearchPage.tsx:43-44, StreetDetailPage.tsx |
| `streets.postcode_area` (not `postcode`) | `street.postcode_area` in SearchBar.tsx:137, StreetDetailPage.tsx:113, SearchPage.tsx:294 |
| `streets.latitude` / `streets.longitude` | `.not('latitude', 'is', null)` in MapView.tsx; `.toFixed(4)` implies numeric |
| `streets.etymology_suggestion` | read in 5+ files; written by AdminPage.tsx approve handler |
| `streets.etymology_verified` | `.eq('etymology_verified', true)` in HomePage.tsx; boolean checks throughout |
| `streets.etymology_source` | `street.etymology_source` in StreetDetailPage.tsx:265 |
| `streets.first_recorded_date` (text) | `street.first_recorded_date` in StreetDetailPage.tsx:121; sort in SearchPage.tsx:94 |
| `streets.historical_notes` | `street.historical_notes` in StreetDetailPage.tsx |
| `streets.historical_period` (nullable text) | `Street` in `supabase.ts`; rendered on StreetDetailPage when non-null |
| `streets.created_at` | returned by `.select('*')` on streets; on `Street` in `supabase.ts` |
| `streets.updated_at` | AdminPage.tsx approve handler; ProfilePage profile update |
| `contributions.id` (uuid) | `.eq('id', contribution.id)` in AdminPage.tsx |
| `contributions.street_id` | ContributionForm.tsx insert; AdminPage.tsx join logic |
| `contributions.user_id` (nullable uuid) | `user?.id \|\| null` in ContributionForm.tsx |
| `contributions.user_email` | displayed in AdminPage.tsx; queried in ProfilePage.tsx |
| `contributions.etymology_suggestion` | ContributionForm.tsx insert; rendered everywhere |
| `contributions.sources` (nullable) | `sources.trim() \|\| null` in ContributionForm.tsx |
| `contributions.status` ('pending'\|'approved'\|'rejected') | all three values used in AdminPage.tsx; filter and insert |
| `contributions.reviewed_at` (nullable) | set on approve/reject in AdminPage.tsx |
| `contributions.created_at` | `.order('created_at', ...)` in multiple pages |
| `profiles.user_id` (uuid PK) | `.eq('user_id', user.id)` in AuthContext.tsx |
| `profiles.email` | inserted in AuthContext.tsx signUp |
| `profiles.full_name` (nullable) | inserted and updated in AuthContext / ProfilePage |
| `profiles.role` ('user'\|'moderator'\|'admin') | `role: 'user'` on insert; isAdmin check in AuthContext.tsx:107 |
| `profiles.contribution_count` (integer) | `contribution_count: 0` inserted in AuthContext.tsx |
| `profiles.updated_at` | `updated_at: new Date().toISOString()` in ProfilePage.tsx:89 |
| `newsletter_subscribers.email` (unique) | insert in NewsletterSignup.tsx; error code 23505 handled |
| `historical-maps` bucket config | create-bucket-historical-maps-temp/index.ts: public, 10MB, image/*, application/pdf |
| `saved_streets` (id, user_id, street_id, created_at) | StreetDetailPage.tsx (save/remove); ProfilePage.tsx (“My atlas” list); types in `supabase.ts` (`SavedStreet`) |

### Inferred from CLAUDE.md only (medium confidence)

| Item | Note |
|---|---|
| `historical_maps` table schema | CLAUDE.md lists the table name only. No frontend component queries it. Columns are speculative. |
| `streets.id` being OS OpenNames identifier | CLAUDE.md states data is sourced from OS OpenNames. The id type (text) matches `Street.id` and `saved_streets.street_id`. |

Canonical TypeScript types for `Street`, `Profile`, `Contribution`, and `SavedStreet` live in `street-etymology/src/lib/supabase.ts`; keep them aligned with live Postgres after schema changes.
