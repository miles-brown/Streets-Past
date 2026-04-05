#!/usr/bin/env bash
# Read-only check: saved_streets is exposed to PostgREST after migration.
# Uses anon key from street-etymology/.env (same as the browser client).
#
# Expected before migration: HTTP 404 + PGRST205 (table not in schema cache).
# Expected after migration: not PGRST205 — often 401/403 (no anon grant) or 200 with [].
#
# RLS and grants: confirm in Dashboard → Authentication / Table Editor is not enough;
# use Table Editor → saved_streets → Policies (select/insert/delete for authenticated).

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/street-etymology/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE (need VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY)"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

if [[ -z "${VITE_SUPABASE_URL:-}" || -z "${VITE_SUPABASE_ANON_KEY:-}" ]]; then
  echo "VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be set in $ENV_FILE"
  exit 1
fi

URL="${VITE_SUPABASE_URL%/}/rest/v1/saved_streets?select=id&limit=1"
BODY=$(curl -sS "$URL" \
  -H "apikey: ${VITE_SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${VITE_SUPABASE_ANON_KEY}" \
  -H "Accept: application/json")
CODE=$(curl -sS -o /dev/null -w "%{http_code}" "$URL" \
  -H "apikey: ${VITE_SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${VITE_SUPABASE_ANON_KEY}")

echo "HTTP status: $CODE"
echo "Body: $BODY"

if echo "$BODY" | grep -q 'PGRST205'; then
  echo ""
  echo "RESULT: saved_streets is NOT visible to the API (migration likely not applied yet)."
  exit 1
fi

echo ""
echo "RESULT: Table exists in PostgREST schema cache (migration applied at least once)."
echo "Dashboard: verify RLS enabled on public.saved_streets and policies for authenticated."
exit 0
