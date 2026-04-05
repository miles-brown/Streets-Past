# Next.js + Supabase (SSR)

Next.js 15 App Router with `@supabase/supabase-js`, `@supabase/ssr`, and middleware that refreshes auth cookies (`updateSession`). Use this for experiments or SSR patterns alongside the main Vite app in `../street-etymology/`.

## Prerequisites

- Node 18+ (Node 20+ recommended)
- npm (or use pnpm with your own lockfile)

## Setup

```bash
cd next
npm install
cp .env.example .env.local
# Edit .env.local: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
```

`.env.local` is gitignored. Do not commit API keys.

## Scripts

| Command       | Description                    |
|---------------|--------------------------------|
| `npm run dev` | Dev server (http://localhost:3000) |
| `npm run build` | Production build           |
| `npm run start` | Run production build locally |
| `npm run lint`  | ESLint (Next + TypeScript) |

## Layout

| Path | Role |
|------|------|
| `app/page.tsx` | Server Component sample: reads `streets` |
| `app/layout.tsx` | Root layout |
| `middleware.ts` | Calls `updateSession` on each matched request |
| `utils/supabase/server.ts` | `createClient()` for Server Components / Route Handlers |
| `utils/supabase/client.ts` | Browser `createClient()` |
| `utils/supabase/middleware.ts` | `updateSession(request)` for cookie refresh |

## Agent skills

Supabase skills are installed at the **repository root** (`.agents/skills/`, gitignored), not inside `next/`. To reinstall:

```bash
cd ..   # repo root
npm_config_cache=/tmp/npm-cache-npx npx skills add supabase/agent-skills -y
```

## ESLint

Config: `.eslintrc.json` extends `next/core-web-vitals` and `next/typescript`. Next.js 15 still ships `next lint`; Next 16 may move to the ESLint CLI only.
