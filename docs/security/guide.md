# Streets Past — Security & Privacy Guide

**Document date:** 2026-03-04
**Project:** Streets Past (https://streetetymology.co.uk/)
**Stack:** React SPA + Supabase (PostgreSQL, Auth, Storage, Edge Functions) + MiniMax/Cloudflare hosting

---

## Table of Contents

1. [Authentication & Authorization](#1-authentication--authorization)
2. [Row Level Security (RLS)](#2-row-level-security-rls)
3. [Input Validation & Injection Prevention](#3-input-validation--injection-prevention)
4. [CORS Configuration](#4-cors-configuration)
5. [Data Privacy & GDPR](#5-data-privacy--gdpr)
6. [Security Hardening Checklist](#6-security-hardening-checklist)
7. [Incident Response](#7-incident-response)

---

## 1. Authentication & Authorization

### Auth Flow

Streets Past uses Supabase Auth for all authentication. The flow is:

1. User submits email and password on `/register` or `/login`.
2. Supabase issues a JWT (access token + refresh token) stored in `localStorage` via the Supabase JS SDK.
3. On returning visits, `supabase.auth.onAuthStateChange()` in `AuthContext.tsx` restores the session automatically.
4. OAuth providers (if configured) redirect back to `/auth/callback`, which is handled by the `HomePage` component after Supabase exchanges the authorization code for a session.
5. Tokens are included automatically as `Authorization: Bearer <jwt>` on all Supabase SDK requests.

**Key file:** `street-etymology/src/contexts/AuthContext.tsx`

### Role-Based Access Control

Roles are stored in the `profiles.role` column. There are three levels:

| Role | Permissions |
|------|-------------|
| `user` | Read public data, submit contributions, manage own profile |
| `moderator` | All `user` permissions + approve/reject contributions via `/admin` |
| `admin` | All `moderator` permissions + write to `streets` table, read all profiles |

The `isAdmin` helper in `AuthContext` evaluates to `true` for both `moderator` and `admin` roles:

```typescript
isAdmin: profile?.role === 'admin' || profile?.role === 'moderator'
```

The `/admin` route should enforce this client-side check, but enforcement must also be backed by RLS policies on the database (see Section 2).

### Session Management

- Sessions are managed via `supabase.auth.onAuthStateChange()`, which fires on sign-in, sign-out, token refresh, and tab focus.
- The Supabase JS SDK handles JWT refresh automatically before expiry.
- On `signOut()`, the SDK clears the local session and the `AuthContext` state resets to `null`.
- There is no server-side session store; the JWT is the single source of truth.

### Password Requirements

Supabase Auth defaults apply unless overridden in the Supabase dashboard:

- Minimum length: 6 characters (Supabase default).
- **Recommendation:** Raise the minimum to 8 or 12 characters in the Supabase Auth settings (Authentication > Providers > Email).
- **Recommendation:** Enable email confirmation so that unverified accounts cannot submit contributions or access protected resources.

---

## 2. Row Level Security (RLS)

RLS must be enabled on every table that holds user data or moderated content. Supabase disables RLS by default; it must be explicitly turned on per table.

### `streets` Table

This table holds the canonical UK street data (sourced from OS OpenNames) and verified etymologies.

| Operation | Who | Policy |
|-----------|-----|--------|
| SELECT | Everyone (anonymous + authenticated) | `true` |
| INSERT | Admin only | `auth.jwt() ->> 'role' = 'admin'` |
| UPDATE | Admin only | `auth.jwt() ->> 'role' = 'admin'` |
| DELETE | Admin only | `auth.jwt() ->> 'role' = 'admin'` |

Street name data is public information; no restriction on reads is needed or desirable.

### `contributions` Table

Contributions are user-submitted etymology suggestions that go through a moderation workflow.

| Operation | Who | Policy |
|-----------|-----|--------|
| SELECT | Everyone, but filtered by status | `status = 'approved'` for anonymous; all statuses for authenticated owner or admin |
| INSERT | Authenticated users only | `auth.uid() IS NOT NULL` |
| UPDATE | Admin/moderator only (to change `status`) | `auth.jwt() ->> 'role' IN ('admin', 'moderator')` |
| DELETE | Admin only | `auth.jwt() ->> 'role' = 'admin'` |

An owner should also be able to delete their own unmoderated contribution:

```sql
-- Owner can delete their own pending contributions
DELETE: auth.uid() = user_id AND status = 'pending'
```

### `profiles` Table

Profiles hold personally identifiable information (email, full name, role).

| Operation | Who | Policy |
|-----------|-----|--------|
| SELECT | Own profile only | `auth.uid() = user_id` |
| SELECT | Admin: all profiles | `auth.jwt() ->> 'role' IN ('admin', 'moderator')` |
| INSERT | Authenticated users (own row only) | `auth.uid() = user_id` |
| UPDATE | Own profile only | `auth.uid() = user_id` |
| UPDATE | Admin: role field only | `auth.jwt() ->> 'role' = 'admin'` |
| DELETE | Own profile (via account deletion flow) | `auth.uid() = user_id` |

Prevent users from escalating their own role by restricting `UPDATE` on the `role` column to admins only, using a column-level check or a separate policy.

### `newsletter_subscribers` Table

| Operation | Who | Policy |
|-----------|-----|--------|
| SELECT | Admin only | `auth.jwt() ->> 'role' = 'admin'` |
| INSERT | Anyone (anonymous subscription) | `true` — but enforce email format validation at application level |
| DELETE | Admin only, or matching email via secure token | Admin RLS + unsubscribe token flow |

### Storage: `historical-maps` Bucket

**Current state (too permissive):** The bucket has public policies allowing SELECT, INSERT, UPDATE, and DELETE for all users including anonymous.

**Required changes:**

| Operation | Who | Recommended Policy |
|-----------|-----|--------------------|
| SELECT | Everyone | Public read is acceptable for map images |
| INSERT | Authenticated users only | `auth.uid() IS NOT NULL` |
| UPDATE | Admin/moderator only | `auth.jwt() ->> 'role' IN ('admin', 'moderator')` |
| DELETE | Admin only | `auth.jwt() ->> 'role' = 'admin'` |

Public DELETE is a critical misconfiguration. An anonymous user could delete all uploaded historical map images. This must be corrected before the storage bucket is used in production.

To apply this in the Supabase Storage policy editor, remove the existing public DELETE and UPDATE policies and create authenticated-only replacements.

---

## 3. Input Validation & Injection Prevention

### SQL Injection

The Supabase JS SDK uses parameterized queries for all operations. Direct string interpolation into SQL is not possible through the SDK's standard methods (`.select()`, `.insert()`, `.ilike()`, etc.). SQL injection via the application layer is not a practical risk under normal usage.

The `SearchBar` component uses `.ilike('name', \`%${query}%\`)`. This is parameterized by the SDK and is safe.

**Recommendation:** Do not use raw SQL via `.rpc()` with user-controlled input unless the stored procedure is explicitly hardened.

### XSS (Cross-Site Scripting)

React automatically escapes content rendered in JSX. However, one confirmed XSS risk exists:

**MapView popup (`street-etymology/src/components/MapView.tsx`):**

The MapLibre GL JS popup accepts HTML. If street names or etymology text are rendered using string interpolation into `.setHTML()` (e.g., `` popup.setHTML(`<b>${street.name}</b>`) ``), and that data originates from user contributions, an attacker could inject `<script>` tags or event handlers via a crafted contribution.

**Remediation — use the DOM API instead of string interpolation:**

```typescript
// Unsafe (current pattern):
popup.setHTML(`<h3>${street.name}</h3><p>${street.etymology_suggestion}</p>`);

// Safe alternative:
const container = document.createElement('div');
const heading = document.createElement('h3');
heading.textContent = street.name;
const para = document.createElement('p');
para.textContent = street.etymology_suggestion ?? '';
container.appendChild(heading);
container.appendChild(para);
popup.setDOMContent(container);
```

MapLibre GL JS provides `popup.setDOMContent(element)` precisely for this purpose.

### CSRF (Cross-Site Request Forgery)

The application is a SPA using JWT-based authentication (Bearer tokens in `Authorization` headers). Browser-native CSRF attacks rely on cookies being sent automatically; they do not apply to header-based token auth. CSRF is not a material risk for this architecture.

### ContributionForm Input Validation

The `ContributionForm` collects free-text etymology and source URLs from users. The following server-side or Edge Function validations should be enforced:

- **`etymology_text`**: Maximum length 5,000 characters. No HTML permitted (strip or reject tags).
- **`sources`**: Validate as a list of URLs if structured as URLs; apply maximum item count (e.g., 10 sources).
- **Email fields**: Validate format with a regex or zod schema before insertion.
- **Rate limiting**: Limit contribution submissions to a reasonable rate per authenticated user (e.g., 5 per hour) to prevent spam. This is best implemented in a Supabase Edge Function acting as a submission proxy, using the user's JWT to identify and throttle.

---

## 4. CORS Configuration

### Edge Functions

All Supabase Edge Functions currently return:

```
Access-Control-Allow-Origin: *
```

This is acceptable for the `suggest-etymology` function because:

- It accepts only `streetName` (public data, no credentials).
- It performs no write operations to the database.
- The function is effectively a public utility API.

**However**, if Edge Functions are added in future that perform authenticated operations (e.g., moderate contributions, delete records), the CORS policy must be tightened:

```typescript
// Restrict to the canonical origin for sensitive functions
const allowedOrigin = 'https://streetetymology.co.uk';
headers.set('Access-Control-Allow-Origin', allowedOrigin);
headers.set('Vary', 'Origin');
```

### Supabase Anon Key

The `VITE_SUPABASE_ANON_KEY` is exposed in the frontend bundle. This is expected and intentional by design — Supabase's security model assumes the anon key is public. Access control is enforced entirely through RLS policies on the database, not by keeping the key secret.

**Actions to take:**

- Audit which operations the anon key can perform. In the Supabase dashboard, review the `anon` role's permissions.
- Ensure no table has permissive policies that allow anonymous writes where they are not intended.
- Never expose the `service_role` key in the frontend. It bypasses RLS entirely.

---

## 5. Data Privacy & GDPR

### Personal Data Collected

| Data Item | Location | Purpose | Retention |
|-----------|----------|---------|-----------|
| Email address | `profiles.email`, `newsletter_subscribers.email` | Authentication, contact, newsletter | Until account/subscription deletion |
| Full name | `profiles.full_name` | Display name on contributions | Until account deletion |
| User ID (UUID) | `profiles.user_id`, `contributions.user_id` | Linking contributions to accounts | Until account deletion |
| IP address (implicit) | Supabase/Cloudflare logs | Security, rate limiting | Per provider policy (typically 30–90 days) |

### Data Storage Region

By default, Supabase projects are created in the region selected at project creation time. For UK/EU GDPR compliance, the Supabase project should be hosted in an EU region (e.g., `eu-west-1` or `eu-central-1`). Confirm the region in the Supabase dashboard under Project Settings > General.

If the project is hosted outside the EU, a Data Transfer Impact Assessment (DTIA) may be required, or standard contractual clauses (SCCs) must be in place with Supabase.

### Right to Erasure (Right to be Forgotten)

Users have the right to request deletion of all personal data. The deletion flow must:

1. Delete or anonymize all rows in `contributions` where `user_id` matches the requesting user.
   - Option A: Hard delete contributions.
   - Option B: Null out `user_id` to preserve the etymology content as an anonymous contribution (preferred if the content has value to the community).
2. Delete the `profiles` row for the user.
3. Delete the Supabase Auth user record via `supabase.auth.admin.deleteUser(userId)` (requires `service_role` key; call from a secure Edge Function).
4. Remove the user from `newsletter_subscribers` if they subscribed with the same email.

This flow should be accessible from the user's profile page (`/profile`) and must be documented in the Privacy Policy at `/privacy`.

### Newsletter Subscribers

- Email addresses collected for the newsletter require explicit, freely given consent (GDPR Article 7).
- The consent mechanism must clearly state what the subscriber will receive and how often.
- Each newsletter email must include an unsubscribe link.
- The unsubscribe action must remove the row from `newsletter_subscribers` without requiring the user to log in.
- A double opt-in flow (confirmation email before adding to the list) is recommended.

### Privacy Policy

A Privacy Policy is served at the `/privacy` route (`PrivacyPage.tsx`). It must cover:

- What data is collected and why
- How long data is retained
- Who data is shared with (Supabase, Cloudflare, any analytics providers)
- User rights: access, rectification, erasure, portability, objection
- Contact details for the data controller
- Cookie usage (if any analytics or tracking cookies are set)

### Cookies

Supabase stores the JWT session in `localStorage`, not cookies, by default. If no third-party analytics or tracking scripts are present, the site may not require a cookie consent banner. Confirm this by auditing the deployed bundle for any cookie-setting scripts.

---

## 6. Security Hardening Checklist

Items marked with a priority level: **[Critical]**, **[High]**, **[Medium]**, **[Low]**.

### Storage

- [ ] **[Critical]** Restrict the `historical-maps` bucket DELETE policy to admin only. Anonymous DELETE is currently permitted and must be closed immediately.
- [ ] **[High]** Restrict the `historical-maps` bucket INSERT policy to authenticated users only.
- [ ] **[High]** Restrict the `historical-maps` bucket UPDATE policy to admin/moderator only.

### Authentication

- [ ] **[High]** Enable email confirmation in Supabase Auth (Authentication > Providers > Email > "Confirm email"). Unconfirmed accounts should not be able to submit contributions.
- [ ] **[Medium]** Raise minimum password length to 12 characters in Supabase Auth settings.
- [ ] **[Medium]** Configure account lockout after repeated failed login attempts (available in Supabase Auth settings under "Rate Limits").

### XSS / Content Security

- [ ] **[High]** Sanitize MapView popup HTML. Replace `.setHTML()` string interpolation with `.setDOMContent()` using `textContent` assignments to prevent XSS via street name or etymology data.
- [ ] **[High]** Add a `Content-Security-Policy` (CSP) HTTP response header. A suitable starting policy for a React SPA with MapLibre and Supabase:

  ```
  Content-Security-Policy:
    default-src 'self';
    script-src 'self';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: blob: https://*.tile.openstreetmap.org https://*.supabase.co;
    connect-src 'self' https://*.supabase.co https://nadbmxfqknnnyuadhdtk.supabase.co;
    font-src 'self';
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
  ```

  Configure this header in the MiniMax/Cloudflare hosting layer or via a `_headers` file if supported.

- [ ] **[Medium]** Add `X-Content-Type-Options: nosniff` and `X-Frame-Options: DENY` headers at the hosting layer.
- [ ] **[Medium]** Add `Referrer-Policy: strict-origin-when-cross-origin`.

### Input Validation

- [ ] **[High]** Enforce server-side maximum length validation on `contributions.etymology_text` (suggested: 5,000 characters).
- [ ] **[High]** Validate and sanitize the `sources` field in `ContributionForm` to prevent injection of malicious URLs.
- [ ] **[Medium]** Rate limit contribution submissions per authenticated user using a Supabase Edge Function proxy (suggested: 5 per hour).

### Database

- [ ] **[High]** Verify that RLS is enabled on all tables: `streets`, `contributions`, `profiles`, `newsletter_subscribers`, `historical_maps`.
- [ ] **[High]** Audit all RLS policies against the recommended policies in Section 2.
- [ ] **[Medium]** Enable automated Supabase database backups (available on paid plans). On the free plan, manually export using `pg_dump` on a scheduled basis.
- [ ] **[Medium]** Restrict the `role` column in `profiles` from self-modification. Add a check that only admins can set `role` values other than `'user'`.

### Supabase Configuration

- [ ] **[High]** Audit the `anon` role permissions in Supabase. Remove any table grants that should require authentication.
- [ ] **[High]** Confirm the `service_role` key is never committed to the repository or exposed in frontend code. It should only appear in server-side Edge Function environment variables.
- [ ] **[Medium]** Rotate the `service_role` key if there is any suspicion it has been exposed.
- [ ] **[Low]** Review Supabase project member access. Remove any project members who no longer require access.

### Network & Hosting

- [ ] **[Medium]** Consider enabling a Web Application Firewall (WAF) via Cloudflare if the site is proxied through Cloudflare. A basic WAF rule set can block common attack patterns and bot traffic.
- [ ] **[Low]** Enable Cloudflare Bot Fight Mode or equivalent to reduce automated abuse.
- [ ] **[Low]** Review CORS policy on Edge Functions annually or after any new function is added.

---

## 7. Incident Response

### General Principles

1. **Contain first**: Disable the affected system or revoke credentials before investigating.
2. **Document**: Record timestamps, observed behavior, affected data, and actions taken.
3. **Notify**: Inform affected users within 72 hours if personal data is involved (GDPR Article 33 requirement for controllers).
4. **Post-mortem**: After resolution, document the root cause and preventive measures.

---

### Scenario 1: Database Breach

**Indicators:** Unexpected data access patterns in Supabase logs, evidence of bulk data export, reports of user data appearing externally.

**Response steps:**

1. Immediately rotate the Supabase `service_role` key and `anon` key in the Supabase dashboard (Settings > API).
2. Update the deployed frontend environment variables with the new `anon` key.
3. Revoke all active sessions via Supabase Auth (Auth > Users > "Log out all users" if available, or use the Admin API).
4. Audit Supabase access logs for the affected time period (Logs > API Logs, Logs > Database Logs).
5. Identify the affected rows and assess which user data was exposed.
6. If personal data (email, name) was exposed, notify affected users within 72 hours per GDPR Article 33.
7. File a breach notification with the relevant supervisory authority (ICO in the UK) if required.
8. **Contact:** Supabase support at https://supabase.com/support

---

### Scenario 2: Authentication Compromise

**Indicators:** Reports of unauthorized account access, unexpected admin actions, suspicious activity in contribution moderation logs.

**Response steps:**

1. Identify the compromised account(s) from Supabase Auth logs.
2. Disable the affected account(s) via Supabase dashboard (Auth > Users > Disable user) or Admin API.
3. Rotate the Supabase JWT secret if there is evidence of token forgery (this will invalidate all active sessions — communicate this to users).
4. Review and revert any unauthorized changes to the `streets` table, contribution statuses, or user roles.
5. If an admin account was compromised, audit all admin actions since the compromise date.
6. Force password reset for the affected user(s).
7. Communicate to affected users: confirm what actions were taken on their account, advise password change.

---

### Scenario 3: Storage Abuse

**Indicators:** Unexpected files in the `historical-maps` bucket, high storage usage, reports of inappropriate content uploads.

**Response steps:**

1. Immediately apply the corrected storage RLS policies (see Section 2 and the hardening checklist) if the public DELETE/INSERT misconfiguration has not yet been fixed.
2. Delete the offending files via the Supabase Storage dashboard.
3. Review storage access logs (Supabase Logs > Storage Logs) to identify the source IP and any authenticated user associated with the uploads.
4. If the uploads violate the Terms of Service, disable the associated account.
5. If files were CSAM or otherwise illegal, preserve evidence, do not delete, and contact the relevant authorities.
6. **Contact:** Supabase support at https://supabase.com/support for storage-level intervention.

---

### Scenario 4: DDoS / High Traffic Abuse

**Indicators:** Site unresponsive, Supabase API rate limit errors appearing in frontend, abnormal traffic volumes in hosting dashboard.

**Response steps:**

1. Check Cloudflare or MiniMax hosting analytics for traffic source patterns.
2. Enable Cloudflare's "I'm Under Attack" mode (Under Attack Mode) if available, which adds a JavaScript challenge to all visitors.
3. If the Supabase API is being targeted directly, contact Supabase support to apply IP-level rate limiting or temporary blocks.
4. Review which API endpoints are being targeted. If it is the `suggest-etymology` Edge Function, consider adding a per-IP rate limit within the function using a Supabase KV store or Upstash Redis.
5. If it is the search endpoint, consider caching common search responses in a CDN layer to reduce direct database load.
6. **Contact:** MiniMax support for hosting-level mitigation; Supabase support for API/database-level mitigation.

---

### Key Contacts

| Service | Support URL | Notes |
|---------|-------------|-------|
| Supabase | https://supabase.com/support | For database, auth, storage, and Edge Function issues |
| Cloudflare | https://support.cloudflare.com | For CDN, WAF, and DDoS mitigation |
| MiniMax Hosting | Platform dashboard | For deployment and hosting issues |
| ICO (UK data regulator) | https://ico.org.uk/make-a-complaint/ | For GDPR breach notifications |

---

*Last updated: 2026-03-04. Review this document after any significant infrastructure change or security incident.*
