#!/usr/bin/env bash
# Read-only check: does public.saved_streets exist in the linked Supabase project?
# Uses the anon REST API (same as the browser). No database password required.
#
# Usage:
#   ./scripts/verify-saved-streets-migration.sh
# Expects street-etymology/.env with VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY,
# or those variables already exported.
#
# Exit codes: 0 = table exists (migration applied); 1 = table missing; 2 = error

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/street-etymology/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi

if [[ -z "${VITE_SUPABASE_URL:-}" || -z "${VITE_SUPABASE_ANON_KEY:-}" ]]; then
  echo "Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY (e.g. street-etymology/.env)." >&2
  exit 2
fi

BODY="$(curl -sS \
  "${VITE_SUPABASE_URL}/rest/v1/saved_streets?select=id&limit=1" \
  -H "apikey: ${VITE_SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${VITE_SUPABASE_ANON_KEY}" \
  -H "Accept: application/json")"

if echo "$BODY" | grep -q '"code":"PGRST205"'; then
  echo "saved_streets: not found (migration not applied or not yet visible in API)." >&2
  exit 1
fi

if echo "$BODY" | grep -q '"code":"PGRST"'; then
  echo "Unexpected PostgREST error:" >&2
  echo "$BODY" >&2
  exit 2
fi

echo "saved_streets: table is reachable via PostgREST (migration applied)."
echo "Next: verify in Dashboard → Authentication → Policies → saved_streets (RLS enabled; select/insert/delete for authenticated)."
exit 0
