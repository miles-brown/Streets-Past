# Streets Past - API Reference

This document covers the complete API surface of the Streets Past application:
Supabase Edge Functions (Deno runtime) and the client-side Supabase PostgREST
queries used across the frontend.

Supabase project ID: `nadbmxfqknnnyuadhdtk`
Base Edge Function URL: `https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1`

---

## Table of Contents

1. [Edge Functions](#edge-functions)
   - [suggest-etymology](#1-suggest-etymology)
   - [create-bucket-historical-maps-temp](#2-create-bucket-historical-maps-temp)
2. [Client-Side Database Queries](#client-side-database-queries)
   - [Street Search](#street-search)
   - [Street Detail](#street-detail)
   - [Map Streets](#map-streets)
   - [Contributions (Public View)](#contributions-public-view)
   - [Submit Contribution](#submit-contribution)
   - [Load Contributions (Admin)](#load-contributions-admin)
   - [Approve / Reject Contribution](#approve--reject-contribution)
   - [Load Profile](#load-profile)
   - [Create Profile on Signup](#create-profile-on-signup)
3. [Error Handling Patterns](#error-handling-patterns)
4. [CORS Reference](#cors-reference)

---

## Edge Functions

Edge Functions run in the Deno runtime on Supabase infrastructure. Both
functions include CORS preflight handling via `OPTIONS` responses.

---

### 1. suggest-etymology

Analyses a UK street name using rule-based linguistic pattern matching and
returns an etymology suggestion. No authentication is required.

**Source:** `supabase/functions/suggest-etymology/index.ts`
**Algorithm docs:** `docs/ai_ml/suggest_etymology_algorithm.md`

#### Endpoint

```
POST https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/suggest-etymology
```

#### CORS

| Header | Value |
|---|---|
| `Access-Control-Allow-Origin` | `*` |
| `Access-Control-Allow-Headers` | `authorization, x-client-info, apikey, content-type` |
| `Access-Control-Allow-Methods` | `POST, GET, OPTIONS` |
| `Access-Control-Max-Age` | `86400` |

An `OPTIONS` preflight request returns `HTTP 200` with no body and the headers
above.

#### Authentication

None. This is a public endpoint.

#### Request

**Content-Type:** `application/json`

| Field | Type | Required | Description |
|---|---|---|---|
| `streetName` | `string` | Yes | The street name to analyse (e.g. `"High Street"`) |

```json
{
  "streetName": "High Street"
}
```

#### Success Response — HTTP 200

**Content-Type:** `application/json`

```json
{
  "data": {
    "streetName": "High Street",
    "etymology": "\"High\" derives from Old English \"heah\", meaning \"principal or main\" (Various). \"Street\" derives from Latin via Old English, meaning \"paved road (from 'strata via' - layered way)\" (Roman/Early Medieval).\n\nThis street name contains elements from: Various, Roman/Early Medieval.\n\nFor definitive etymology, consult: local county archives, Ordnance Survey historical maps, and publications by the English Place-Name Society or relevant regional societies.",
    "elements": [
      {
        "element": "high",
        "info": {
          "meaning": "principal or main",
          "origin": "Old English \"heah\"",
          "period": "Various"
        }
      },
      {
        "element": "street",
        "info": {
          "origin": "Latin via Old English",
          "meaning": "paved road (from \"strata via\" - layered way)",
          "period": "Roman/Early Medieval"
        }
      }
    ],
    "confidence": "medium",
    "sources": [
      "English Place-Name Society publications",
      "Oxford Dictionary of English Place-Names",
      "Institute of Name-Studies, University of Nottingham"
    ]
  }
}
```

**Response fields:**

| Field | Type | Description |
|---|---|---|
| `data.streetName` | `string` | The street name as submitted |
| `data.etymology` | `string` | Human-readable etymology text (newline-separated paragraphs) |
| `data.elements` | `array` | Matched linguistic elements (may be empty) |
| `data.elements[].element` | `string` | The matched pattern word (e.g. `"gate"`, `"high"`) |
| `data.elements[].info.origin` | `string` | Language of origin |
| `data.elements[].info.meaning` | `string` | Meaning of the element |
| `data.elements[].info.period` | `string` | Historical period |
| `data.confidence` | `string` | `"medium"` when elements are found, `"low"` when none are recognised |
| `data.sources` | `string[]` | Fixed list of reference sources |

**Confidence values:**

| Value | Condition |
|---|---|
| `"medium"` | One or more recognised linguistic elements found |
| `"low"` | No recognised elements; generic guidance text is returned |

#### Error Response — HTTP 500

```json
{
  "error": {
    "code": "ETYMOLOGY_ERROR",
    "message": "Street name is required"
  }
}
```

| Field | Type | Description |
|---|---|---|
| `error.code` | `string` | Always `"ETYMOLOGY_ERROR"` |
| `error.message` | `string` | Human-readable description of the error |

Common trigger: omitting the `streetName` field entirely (message: `"Street name is required"`).

#### Algorithm Summary

The function applies two passes over the normalised street name (lowercased,
trimmed, split on whitespace):

1. **Suffix / word matching** — checks whether the full name ends with or
   contains any of 57 patterns covering road types (gate, street, lane, way,
   road, close, court, place, row), geographic features (hill, green, field,
   ford, bridge, heath, moor, meadow, grove, wood), settlement elements (bury,
   ton, ham, stead, worth, wick), Old Norse elements (kirk, toft, thorpe, by,
   beck, thwaite), religious buildings (church, abbey, priory, castle),
   commerce (mill, market, cheap, shambles), and Georgian/Victorian forms
   (parade, terrace, crescent, square, circus, avenue, boulevard, mews,
   gardens, park, yard, alley, passage, walk, drive).

2. **Prefix / word matching** — checks whether the full name begins with or
   contains any of 34 patterns covering descriptive qualifiers (high, low, old,
   new, great, little, long, broad), cardinal directions (north, south, east,
   west, upper, lower), colours (white, black, green, red, golden, silver),
   nobility (royal, king, queen, prince, duke, lord), and landmarks (abbey,
   church, mill, cross, fleet, well, spring).

Matched elements are deduplicated by element name before output.

#### curl Example

```bash
curl -X POST \
  https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/suggest-etymology \
  -H 'Content-Type: application/json' \
  -d '{"streetName": "Kirkgate"}'
```

#### TypeScript Example (direct fetch)

```typescript
const response = await fetch(
  'https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/suggest-etymology',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ streetName: 'Kirkgate' }),
  }
);

if (!response.ok) {
  const { error } = await response.json();
  console.error(`[${error.code}] ${error.message}`);
} else {
  const { data } = await response.json();
  console.log(data.etymology);
  console.log('Confidence:', data.confidence);
  console.log('Elements:', data.elements);
}
```

#### TypeScript Example (Supabase SDK — actual frontend usage)

This is how `StreetDetailPage.tsx` invokes the function:

```typescript
import { supabase } from '@/lib/supabase';

const { data, error } = await supabase.functions.invoke('suggest-etymology', {
  body: { streetName: street.name },
});

if (error) {
  console.error('Edge function error:', error);
} else if (data?.data?.etymology) {
  console.log(data.data.etymology);   // note the nested data.data shape
}
```

Note the double `data.data` nesting: the Supabase SDK unwraps the HTTP
response body into its own `data` field, and the function itself returns a
`{ data: { ... } }` envelope.

---

### 2. create-bucket-historical-maps-temp

A one-time administrative setup function that creates the `historical-maps`
Supabase Storage bucket and attaches four public RLS policies to it. It is not
part of normal application traffic and should only be called once per
environment.

**Source:** `supabase/functions/create-bucket-historical-maps-temp/index.ts`

#### Endpoint

```
POST https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/create-bucket-historical-maps-temp
```

#### CORS

| Header | Value |
|---|---|
| `Access-Control-Allow-Origin` | `*` |
| `Access-Control-Allow-Headers` | `authorization, x-client-info, apikey, content-type` |
| `Access-Control-Allow-Methods` | `POST, GET, OPTIONS, PUT, DELETE` |

An `OPTIONS` preflight request returns `HTTP 200` with the string body `"ok"`
and the headers above.

#### Authentication

The function uses environment variables injected automatically by Supabase:

| Variable | Source |
|---|---|
| `SUPABASE_SERVICE_ROLE_KEY` | Auto-provided by Supabase runtime |
| `SUPABASE_URL` | Auto-provided by Supabase runtime |

No caller-supplied token is required, but the function must be invoked via a
Supabase context that provides those variables. Call it with the service role
key in the `Authorization` header when testing outside the Supabase dashboard.

#### Request

No request body is required.

#### What the Function Does

1. Reads `SUPABASE_SERVICE_ROLE_KEY` and `SUPABASE_URL` from the Deno
   environment. Returns `CONFIG_ERROR` (500) if either is missing.
2. Calls `POST {SUPABASE_URL}/storage/v1/bucket` to create a bucket named
   `historical-maps` with:
   - `public: true`
   - `allowed_mime_types: ["image/*", "application/pdf"]`
   - `file_size_limit: 10485760` (10 MB)
3. If bucket creation fails, returns `BUCKET_CREATION_FAILED` with the
   upstream status code.
4. Executes four `CREATE POLICY` SQL statements via
   `POST {SUPABASE_URL}/rest/v1/rpc/exec_sql` (SELECT, INSERT, UPDATE, DELETE
   on `storage.objects` where `bucket_id = 'historical-maps'`). Policy errors
   are captured per-policy and included in the response rather than aborting.

#### Success Response — HTTP 200

```json
{
  "success": true,
  "message": "Bucket created successfully with public access policies",
  "bucket": {
    "name": "historical-maps",
    "public": true,
    "allowed_mime_types": ["image/*", "application/pdf"],
    "file_size_limit": 10485760,
    "policies": [
      "Policy created: \"Public",
      "Policy created: \"Public",
      "Policy created: \"Public",
      "Policy created: \"Public"
    ]
  }
}
```

| Field | Type | Description |
|---|---|---|
| `success` | `boolean` | Always `true` on success |
| `message` | `string` | Confirmation message |
| `bucket.name` | `string` | `"historical-maps"` |
| `bucket.public` | `boolean` | `true` |
| `bucket.allowed_mime_types` | `string[]` | `["image/*", "application/pdf"]` |
| `bucket.file_size_limit` | `number` | `10485760` (bytes = 10 MB) |
| `bucket.policies` | `string[]` | Per-policy creation result messages |

#### Error Responses

**HTTP 500 — CONFIG_ERROR**
```json
{
  "error": {
    "code": "CONFIG_ERROR",
    "message": "Missing Supabase configuration"
  }
}
```
Returned when `SUPABASE_SERVICE_ROLE_KEY` or `SUPABASE_URL` environment
variables are absent.

**HTTP (upstream status) — BUCKET_CREATION_FAILED**
```json
{
  "error": {
    "code": "BUCKET_CREATION_FAILED",
    "message": "The resource already exists",
    "status": 409
  }
}
```
Returned when the Supabase Storage API rejects bucket creation (e.g. bucket
already exists). The `status` field mirrors the upstream HTTP status code.

**HTTP 500 — FUNCTION_ERROR**
```json
{
  "error": {
    "code": "FUNCTION_ERROR",
    "message": "fetch failed"
  }
}
```
Returned on any unhandled exception (e.g. network failure inside the Deno
function).

#### curl Example

```bash
curl -X POST \
  https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/create-bucket-historical-maps-temp \
  -H 'Authorization: Bearer YOUR_SERVICE_ROLE_KEY' \
  -H 'Content-Type: application/json'
```

#### TypeScript Example (Supabase SDK)

```typescript
import { supabase } from '@/lib/supabase';

const { data, error } = await supabase.functions.invoke(
  'create-bucket-historical-maps-temp'
);

if (error) {
  console.error('Function error:', error);
} else if (data?.success) {
  console.log('Bucket created:', data.bucket.name);
  console.log('Policy results:', data.bucket.policies);
}
```

#### RLS Policies Created

| Policy Name | Operation | Condition |
|---|---|---|
| `Public Access for historical-maps` | `SELECT` | `bucket_id = 'historical-maps'` |
| `Public Upload for historical-maps` | `INSERT` | `bucket_id = 'historical-maps'` |
| `Public Update for historical-maps` | `UPDATE` | `bucket_id = 'historical-maps'` |
| `Public Delete for historical-maps` | `DELETE` | `bucket_id = 'historical-maps'` |

All policies apply to `storage.objects`. These are fully public policies — no
user authentication is enforced at the storage layer. Access control for
uploads and deletions should be handled at the application layer if needed.

---

## Client-Side Database Queries

These queries are executed via the Supabase JS SDK (`@supabase/supabase-js`
v2) in the browser. All queries communicate over PostgREST using the
project's anon key for public operations and the authenticated session token
for user-specific operations.

The Supabase client is initialised in `street-etymology/src/lib/supabase.ts`
and imported as `supabase` throughout the frontend.

---

### Street Search

**Used in:** `src/components/SearchBar.tsx`
**Trigger:** Debounced 300 ms after user input; fires when query length >= 2

```typescript
const { data, error } = await supabase
  .from('streets')
  .select('*')
  .ilike('name', `%${query}%`)
  .order('name')
  .limit(10);
```

| Parameter | Value | Notes |
|---|---|---|
| Table | `streets` | |
| Filter | `.ilike('name', '%query%')` | Case-insensitive substring match |
| Order | `.order('name')` | Ascending alphabetical |
| Limit | `.limit(10)` | Maximum 10 autocomplete suggestions |

**Returns:** `Street[]` — array of matching street records (empty array when
none found).

**TypeScript example:**

```typescript
import { supabase, Street } from '@/lib/supabase';

async function searchStreets(query: string): Promise<Street[]> {
  if (query.length < 2) return [];

  const { data, error } = await supabase
    .from('streets')
    .select('*')
    .ilike('name', `%${query}%`)
    .order('name')
    .limit(10);

  if (error) {
    console.error('Search error:', error);
    return [];
  }

  return data ?? [];
}
```

**curl equivalent:**

```bash
curl 'https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/streets?name=ilike.*high*&order=name&limit=10' \
  -H 'apikey: YOUR_ANON_KEY' \
  -H 'Authorization: Bearer YOUR_ANON_KEY'
```

---

### Street Detail

**Used in:** `src/pages/StreetDetailPage.tsx`
**Trigger:** On mount, using the `id` route parameter

```typescript
const { data: streetData, error: streetError } = await supabase
  .from('streets')
  .select('*')
  .eq('id', id)
  .maybeSingle();
```

| Parameter | Value | Notes |
|---|---|---|
| Table | `streets` | |
| Filter | `.eq('id', id)` | Exact match on primary key |
| Cardinality | `.maybeSingle()` | Returns `null` if not found (no error) |

**Returns:** `Street | null`

**TypeScript example:**

```typescript
import { supabase, Street } from '@/lib/supabase';

async function fetchStreet(id: string): Promise<Street | null> {
  const { data, error } = await supabase
    .from('streets')
    .select('*')
    .eq('id', id)
    .maybeSingle();

  if (error) throw error;
  return data;
}
```

**curl equivalent:**

```bash
curl 'https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/streets?id=eq.STREET_UUID&limit=1' \
  -H 'apikey: YOUR_ANON_KEY' \
  -H 'Authorization: Bearer YOUR_ANON_KEY'
```

---

### Map Streets

**Used in:** `src/components/MapView.tsx`
**Trigger:** On component mount; loads all streets with valid coordinates

```typescript
const { data, error } = await supabase
  .from('streets')
  .select('*')
  .not('latitude', 'is', null)
  .not('longitude', 'is', null);
```

| Parameter | Value | Notes |
|---|---|---|
| Table | `streets` | |
| Filter | `.not('latitude', 'is', null)` | Excludes streets with no coordinates |
| Filter | `.not('longitude', 'is', null)` | Excludes streets with no coordinates |
| Limit | None | Returns all mappable streets |

**Returns:** `Street[]` — all streets that have both latitude and longitude set.

Note: No server-side limit is applied. For large datasets consider adding
spatial bounding-box filters (PostGIS `ST_Within`) to restrict results to the
current map viewport.

**TypeScript example:**

```typescript
import { supabase, Street } from '@/lib/supabase';

async function fetchMappableStreets(): Promise<Street[]> {
  const { data, error } = await supabase
    .from('streets')
    .select('*')
    .not('latitude', 'is', null)
    .not('longitude', 'is', null);

  if (error) throw error;
  return data ?? [];
}
```

**curl equivalent:**

```bash
curl 'https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/streets?latitude=not.is.null&longitude=not.is.null' \
  -H 'apikey: YOUR_ANON_KEY' \
  -H 'Authorization: Bearer YOUR_ANON_KEY'
```

---

### Contributions (Public View)

**Used in:** `src/pages/StreetDetailPage.tsx`
**Trigger:** On mount, after fetching the street record

Returns only approved contributions for display to all visitors.

```typescript
const { data: contributionsData } = await supabase
  .from('contributions')
  .select('*')
  .eq('street_id', id)
  .eq('status', 'approved')
  .order('created_at', { ascending: false });
```

| Parameter | Value | Notes |
|---|---|---|
| Table | `contributions` | |
| Filter | `.eq('street_id', id)` | Scoped to the current street |
| Filter | `.eq('status', 'approved')` | Public view: approved only |
| Order | `.order('created_at', { ascending: false })` | Newest first |

**Returns:** `Contribution[]`

**TypeScript example:**

```typescript
import { supabase, Contribution } from '@/lib/supabase';

async function fetchApprovedContributions(streetId: string): Promise<Contribution[]> {
  const { data } = await supabase
    .from('contributions')
    .select('*')
    .eq('street_id', streetId)
    .eq('status', 'approved')
    .order('created_at', { ascending: false });

  return data ?? [];
}
```

---

### Submit Contribution

**Used in:** `src/components/ContributionForm.tsx`
**Trigger:** Form submission by any visitor (authenticated or anonymous)

```typescript
const { error } = await supabase.from('contributions').insert({
  street_id: streetId,
  user_id: user?.id || null,       // null for anonymous submissions
  user_email: submitterEmail,
  etymology_suggestion: etymology.trim(),
  sources: sources.trim() || null,
  status: 'pending',
});
```

**Insert payload:**

| Field | Type | Notes |
|---|---|---|
| `street_id` | `string` (UUID) | Foreign key to `streets.id` |
| `user_id` | `string \| null` | Supabase Auth user ID; `null` for anonymous |
| `user_email` | `string` | From authenticated user or manually entered |
| `etymology_suggestion` | `string` | The contributor's etymology text |
| `sources` | `string \| null` | Optional reference list |
| `status` | `string` | Always `"pending"` on creation |

**Returns:** No data on success; `error` is non-null on failure.

**TypeScript example:**

```typescript
import { supabase } from '@/lib/supabase';

async function submitContribution(params: {
  streetId: string;
  userId: string | null;
  userEmail: string;
  etymology: string;
  sources?: string;
}): Promise<void> {
  const { error } = await supabase.from('contributions').insert({
    street_id: params.streetId,
    user_id: params.userId,
    user_email: params.userEmail,
    etymology_suggestion: params.etymology.trim(),
    sources: params.sources?.trim() || null,
    status: 'pending',
  });

  if (error) throw error;
}
```

**curl equivalent:**

```bash
curl -X POST \
  'https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/contributions' \
  -H 'apikey: YOUR_ANON_KEY' \
  -H 'Authorization: Bearer YOUR_ANON_KEY' \
  -H 'Content-Type: application/json' \
  -H 'Prefer: return=minimal' \
  -d '{
    "street_id": "STREET_UUID",
    "user_id": null,
    "user_email": "contributor@example.com",
    "etymology_suggestion": "This street was named after...",
    "sources": "Local history archive, 1843",
    "status": "pending"
  }'
```

---

### Load Contributions (Admin)

**Used in:** `src/pages/AdminPage.tsx`
**Trigger:** On mount and whenever the status filter changes
**Required role:** `admin` or `moderator`

```typescript
// With status filter
let query = supabase
  .from('contributions')
  .select('*')
  .order('created_at', { ascending: false });

if (filter !== 'all') {
  query = query.eq('status', filter);
}

const { data: contributionsData, error } = await query;
```

After fetching contributions, the admin page makes a second query to resolve
street names:

```typescript
const streetIds = [...new Set(contributionsData.map(c => c.street_id))];

const { data: streets } = await supabase
  .from('streets')
  .select('id, name, city, county')
  .in('id', streetIds);
```

**Filter values:**

| `filter` | Effect |
|---|---|
| `"pending"` | Returns only unreviewed submissions |
| `"approved"` | Returns approved submissions |
| `"rejected"` | Returns rejected submissions |
| `"all"` | Returns all submissions regardless of status |

**Returns:** `Contribution[]` (enriched with a `street` property via
client-side join)

**TypeScript example:**

```typescript
import { supabase, Contribution } from '@/lib/supabase';

type StatusFilter = 'pending' | 'approved' | 'rejected' | 'all';

async function loadAdminContributions(filter: StatusFilter): Promise<Contribution[]> {
  let query = supabase
    .from('contributions')
    .select('*')
    .order('created_at', { ascending: false });

  if (filter !== 'all') {
    query = query.eq('status', filter);
  }

  const { data, error } = await query;
  if (error) throw error;
  return data ?? [];
}
```

---

### Approve / Reject Contribution

**Used in:** `src/pages/AdminPage.tsx`
**Required role:** `admin` or `moderator`

**Approve:**

```typescript
const { error: updateError } = await supabase
  .from('contributions')
  .update({
    status: 'approved',
    reviewed_at: new Date().toISOString(),
  })
  .eq('id', contribution.id);

// On approval, optionally propagate to the street record
await supabase
  .from('streets')
  .update({
    etymology_suggestion: contribution.etymology_suggestion,
    updated_at: new Date().toISOString(),
  })
  .eq('id', contribution.street_id);
```

**Reject:**

```typescript
const { error } = await supabase
  .from('contributions')
  .update({
    status: 'rejected',
    reviewed_at: new Date().toISOString(),
  })
  .eq('id', contribution.id);
```

**Update payload:**

| Field | Type | Notes |
|---|---|---|
| `status` | `string` | `"approved"` or `"rejected"` |
| `reviewed_at` | `string` | ISO 8601 timestamp set at review time |

**TypeScript example:**

```typescript
import { supabase } from '@/lib/supabase';

async function reviewContribution(
  contributionId: string,
  decision: 'approved' | 'rejected',
  streetId?: string,
  etymologySuggestion?: string
): Promise<void> {
  const { error } = await supabase
    .from('contributions')
    .update({
      status: decision,
      reviewed_at: new Date().toISOString(),
    })
    .eq('id', contributionId);

  if (error) throw error;

  // Propagate to street record only when approving
  if (decision === 'approved' && streetId && etymologySuggestion) {
    await supabase
      .from('streets')
      .update({
        etymology_suggestion: etymologySuggestion,
        updated_at: new Date().toISOString(),
      })
      .eq('id', streetId);
  }
}
```

**curl equivalent (approve):**

```bash
curl -X PATCH \
  'https://nadbmxfqknnnyuadhdtk.supabase.co/rest/v1/contributions?id=eq.CONTRIBUTION_UUID' \
  -H 'apikey: YOUR_ANON_KEY' \
  -H 'Authorization: Bearer YOUR_SESSION_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'Prefer: return=minimal' \
  -d '{"status": "approved", "reviewed_at": "2026-03-04T12:00:00.000Z"}'
```

---

### Load Profile

**Used in:** `src/contexts/AuthContext.tsx`
**Trigger:** On auth state change when a user session is present

```typescript
const { data: profileData } = await supabase
  .from('profiles')
  .select('*')
  .eq('user_id', user.id)
  .maybeSingle();
```

| Parameter | Value | Notes |
|---|---|---|
| Table | `profiles` | |
| Filter | `.eq('user_id', user.id)` | Scoped to the authenticated user |
| Cardinality | `.maybeSingle()` | Returns `null` if profile not yet created |

**Returns:** `Profile | null`

The profile record drives the `isAdmin` flag in `AuthContext`:
```typescript
const isAdmin = profile?.role === 'admin' || profile?.role === 'moderator';
```

**TypeScript example:**

```typescript
import { supabase, Profile } from '@/lib/supabase';

async function loadProfile(userId: string): Promise<Profile | null> {
  const { data } = await supabase
    .from('profiles')
    .select('*')
    .eq('user_id', userId)
    .maybeSingle();

  return data;
}
```

---

### Create Profile on Signup

**Used in:** `src/contexts/AuthContext.tsx` — inside the `signUp` function
**Trigger:** Immediately after a successful `supabase.auth.signUp()` call

```typescript
await supabase.from('profiles').insert({
  user_id: data.user.id,
  email,
  full_name: fullName || null,
  role: 'user',
  contribution_count: 0,
});
```

**Insert payload:**

| Field | Type | Notes |
|---|---|---|
| `user_id` | `string` (UUID) | Supabase Auth user ID |
| `email` | `string` | User's email address |
| `full_name` | `string \| null` | Optional display name |
| `role` | `string` | Always `"user"` on self-registration |
| `contribution_count` | `number` | Initialised to `0` |

All new self-registered users receive the `"user"` role. The `"moderator"` and
`"admin"` roles must be granted manually via direct database update.

**TypeScript example:**

```typescript
import { supabase } from '@/lib/supabase';

async function createProfile(params: {
  userId: string;
  email: string;
  fullName?: string;
}): Promise<void> {
  const { error } = await supabase.from('profiles').insert({
    user_id: params.userId,
    email: params.email,
    full_name: params.fullName ?? null,
    role: 'user',
    contribution_count: 0,
  });

  if (error) {
    console.error('Profile creation failed:', error);
  }
}
```

---

## Error Handling Patterns

### Edge Function errors

The Supabase JS SDK wraps edge function errors in an `error` object. Check
both the SDK-level `error` and the response body `error` field:

```typescript
const { data, error } = await supabase.functions.invoke('suggest-etymology', {
  body: { streetName },
});

if (error) {
  // SDK-level error (network failure, non-2xx response the SDK captured)
  console.error('Invocation error:', error.message);
  return;
}

if (data?.error) {
  // Application-level error returned in the response body
  console.error(`[${data.error.code}] ${data.error.message}`);
  return;
}

// Happy path
console.log(data.data.etymology);
```

### PostgREST query errors

All Supabase client queries return `{ data, error }`. Always check `error`
before using `data`:

```typescript
const { data, error } = await supabase
  .from('streets')
  .select('*')
  .eq('id', id)
  .maybeSingle();

if (error) {
  // PostgREST error: { message, details, hint, code }
  console.error('Database error:', error.message, error.code);
  throw error;
}

if (!data) {
  // maybeSingle() returns null when no row matched — not an error
  console.warn('Street not found');
}
```

Common PostgREST error codes:

| Code | Meaning |
|---|---|
| `PGRST116` | `.single()` found zero or more than one row |
| `42501` | RLS policy denied the operation |
| `23505` | Unique constraint violation |
| `23503` | Foreign key constraint violation |

### Authentication errors

```typescript
const { error } = await supabase.auth.signInWithPassword({ email, password });

if (error) {
  // error.message describes the failure (e.g. "Invalid login credentials")
  console.error('Auth error:', error.message);
}
```

---

## CORS Reference

Both Edge Functions share the same allowed headers. When invoking from a
browser outside the Supabase dashboard (e.g. during local development against
the production project), include the `apikey` header:

```typescript
const response = await fetch(
  'https://nadbmxfqknnnyuadhdtk.supabase.co/functions/v1/suggest-etymology',
  {
    method: 'POST',
    headers: {
      'apikey': import.meta.env.VITE_SUPABASE_ANON_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ streetName: 'Abbey Road' }),
  }
);
```

The Supabase JS SDK (`supabase.functions.invoke`) handles this automatically
using the anon key supplied at client initialisation.
