# Streets Past (worktree)

UK street etymology: main product is the **Vite + React** app; an optional **Next.js** sample uses Supabase cookie sessions (`@supabase/ssr`).

## Quick start — main app (Vite)

```bash
cd street-etymology
cp .env.example .env.local   # set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
pnpm install
pnpm dev
```

Build: `pnpm run build` · Lint: `pnpm run lint`

## Optional — Next.js + Supabase SSR

```bash
cd next
cp .env.example .env.local   # use NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY
npm install
npm run dev
```

Build / lint: `npm run build` · `npm run lint`

See [`next/README.md`](next/README.md) for details.

## Supabase agent skills (local agents)

Skills install under `.agents/skills/` (gitignored). Reinstall anytime:

```bash
npm_config_cache=/tmp/npm-cache-npx npx skills add supabase/agent-skills -y
```

## Supabase CLI (migrations / functions)

From the repo root, with the [Supabase CLI](https://supabase.com/docs/guides/cli) installed and the project linked (`supabase link`):

```bash
export SUPABASE_DB_PASSWORD='your-database-password'   # Dashboard → Settings → Database
./scripts/db-push.sh
```

Or paste `scripts/apply-saved-streets.sql` (or `supabase/migrations/20260405120000_saved_streets.sql`) into the Supabase SQL Editor. Migration files live in `supabase/migrations/`.

After applying, run `scripts/verify-saved-streets.sql` in the SQL Editor (read-only checks: table columns, RLS, policies, grants, indexes) or confirm the same in **Dashboard → Table Editor / Authentication policies** for `saved_streets`.
