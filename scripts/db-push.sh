#!/usr/bin/env bash
# Push pending SQL migrations to the linked Supabase project.
# Requires: Supabase CLI (supabase link already run) + database password.
#
#   export SUPABASE_DB_PASSWORD='your-database-password'
#   ./scripts/db-push.sh
#
# Password: Supabase Dashboard → Project Settings → Database → Database password

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Load repo-root secrets (gitignored), e.g. .env.local with SUPABASE_DB_PASSWORD
if [[ -f "$ROOT/.env.local" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env.local"
  set +a
fi

if ! command -v supabase >/dev/null 2>&1; then
  echo "Install Supabase CLI: https://supabase.com/docs/guides/cli/getting-started"
  exit 1
fi

if [[ -z "${SUPABASE_DB_PASSWORD:-}" ]]; then
  echo "Set SUPABASE_DB_PASSWORD to your Postgres database password, then re-run."
  echo "Dashboard: Project Settings → Database"
  echo ""
  echo "If the CLI login-role path fails on your project, or you prefer the dashboard:"
  echo "  Supabase → SQL Editor → paste scripts/apply-saved-streets.sql → Run"
  echo "After deploy, verify: ./scripts/verify-saved-streets-migration.sh"
  exit 1
fi

exec supabase db push --yes -p "$SUPABASE_DB_PASSWORD"
