# Contributing to Streets Past

Thank you for your interest in contributing to Streets Past — a project exploring the etymological origins and histories of UK street names.

This document covers everything you need to get started, from setting up a local environment to submitting a pull request.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Code Style](#code-style)
4. [Adding New Pages](#adding-new-pages)
5. [Adding New Components](#adding-new-components)
6. [Edge Functions](#edge-functions)
7. [Running Checks](#running-checks)
8. [Etymology Contributions](#etymology-contributions)
9. [Documentation](#documentation)
10. [Code of Conduct](#code-of-conduct)

---

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) 18 or later
- [pnpm](https://pnpm.io/) — this project uses pnpm exclusively, not npm or yarn
- A Supabase account (or access to the project credentials) for backend features

### Setup

1. Fork the repository on GitHub and clone your fork:

   ```bash
   git clone https://github.com/<your-username>/Streets-Past.git
   cd Streets-Past
   ```

2. Move into the frontend application directory:

   ```bash
   cd street-etymology
   ```

3. Install dependencies:

   ```bash
   pnpm install
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env.local
   ```

   Open `.env.local` and fill in your Supabase credentials:

   ```
   VITE_SUPABASE_URL=<your_supabase_project_url>
   VITE_SUPABASE_ANON_KEY=<your_supabase_anon_key>
   ```

5. Start the development server:

   ```bash
   pnpm dev
   ```

   The app will be available at `http://localhost:5173`.

---

## Development Workflow

### Branching

Create a new branch from `main` for every change. Use the following prefixes:

| Type | Prefix | Example |
|------|--------|---------|
| New feature | `feature/` | `feature/add-county-filter` |
| Bug fix | `fix/` | `fix/map-marker-popup-overflow` |
| Documentation | `docs/` | `docs/update-contributing-guide` |
| Refactor | `refactor/` | `refactor/search-bar-hooks` |
| Chore / tooling | `chore/` | `chore/update-dependencies` |

```bash
git checkout -b feature/your-feature-name
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) style:

```
<type>(<scope>): <short description>
```

Common types: `feat`, `fix`, `docs`, `style`, `refactor`, `chore`

Examples:

```
feat(map): add postcode boundary overlay
fix(search): prevent duplicate results on rapid input
docs(edge-functions): clarify CORS header requirements
chore(deps): upgrade maplibre-gl to v5.2
```

Keep the subject line under 72 characters. Use the body for additional context if needed.

### Pull Request Process

1. Make sure your branch is up to date with `main`:

   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. Run lint and build checks before pushing (see [Running Checks](#running-checks)).

3. Push your branch and open a pull request against `main`.

4. In the PR description, briefly explain:
   - What the change does
   - Why it is needed
   - Any manual testing steps a reviewer should follow

5. A maintainer will review your PR. Be prepared to make small adjustments based on feedback.

---

## Code Style

### TypeScript

- Strict mode is **off** — you do not need to satisfy strict null checks, but well-typed code is still preferred.
- Use **named exports** for all components and utilities. Default exports are only used for the root `App` component.
- Write **functional components** with hooks. Class components are not used in this project.
- Define prop interfaces inline or immediately above the component they belong to.
- The path alias `@/` maps to `./src/` — use it for all internal imports:

  ```ts
  import { supabase } from '@/lib/supabase'
  import { SearchBar } from '@/components/SearchBar'
  ```

- Fetch Supabase data inside `useEffect` hooks. Keep side effects out of render logic.
- Place reusable custom hooks in `src/hooks/`.

### Tailwind and Styling

- Use Tailwind utility classes for all styling. Avoid inline `style` props unless absolutely necessary.
- Stick to the project's heritage/amber design tokens:
  - Primary amber: `#b45309` (exposed as `heritage.gold` in the Tailwind config)
  - Secondary stone: `#57534e` (`heritage.brown`)
  - Accent parchment: `heritage.parchment`, `heritage.ink`
- Use `amber-*` and `stone-*` Tailwind scale classes where custom tokens are not needed.
- Headings use Georgia/serif (`font-serif`). Body text uses Inter/sans-serif (`font-sans`).
- shadcn/ui components follow the **new-york** style. If you add a new shadcn component, run the CLI from within `street-etymology/`:

  ```bash
  pnpm dlx shadcn@latest add <component-name>
  ```

### Component Structure

A typical component file looks like this:

```tsx
import { useState } from 'react'
import { supabase, type Street } from '@/lib/supabase'

interface MyComponentProps {
  streetId: string
}

export function MyComponent({ streetId }: MyComponentProps) {
  const [data, setData] = useState<Street | null>(null)

  // fetch, handlers, effects...

  return (
    <div className="rounded-lg bg-amber-50 p-4 text-stone-800">
      {/* markup */}
    </div>
  )
}
```

---

## Adding New Pages

1. Create a new file in `street-etymology/src/pages/`:

   ```
   src/pages/NewPage.tsx
   ```

   Use a named export:

   ```tsx
   export function NewPage() {
     return <main>...</main>
   }
   ```

2. Register the route in `street-etymology/src/App.tsx`. Most pages use `MainLayout` (header + footer). Full-screen pages (like the map) use `FullScreenLayout`. Auth pages have no layout wrapper:

   ```tsx
   <Route
     path="/new-page"
     element={
       <MainLayout>
         <NewPage />
       </MainLayout>
     }
   />
   ```

3. If the page should appear in the site navigation, add a link to `street-etymology/src/components/Header.tsx`.

---

## Adding New Components

1. Create the file in `street-etymology/src/components/`:

   ```
   src/components/ComponentName.tsx
   ```

2. Use the heritage amber/stone colour palette so the component fits the visual style of the site.

3. If the component needs database types, import them from `@/lib/supabase`:

   ```ts
   import { type Street, type Contribution } from '@/lib/supabase'
   ```

4. Export the component by name (no default export).

---

## Edge Functions

Edge Functions live under `supabase/functions/<function-name>/index.ts` and run on the **Deno** runtime.

### Rules for all Edge Functions

- Use `Deno.serve()` as the entry point — not a Node-style `http` server.
- Include CORS headers on every response. Handle `OPTIONS` preflight requests explicitly:

  ```ts
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  }

  Deno.serve(async (req) => {
    if (req.method === 'OPTIONS') {
      return new Response('ok', { headers: corsHeaders })
    }

    // ... handler logic

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  })
  ```

- Use the auto-provided `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` environment variables when you need elevated database access. Do not hard-code credentials.

### Creating a New Edge Function

1. Create the directory and entry file:

   ```
   supabase/functions/<function-name>/index.ts
   ```

2. Follow the `Deno.serve()` + CORS pattern above.

3. Document the function's input/output shape in a comment at the top of the file.

---

## Running Checks

All commands run from the `street-etymology/` directory.

### Lint

```bash
pnpm lint
```

This runs ESLint with the flat config (`eslint.config.js`), including `react-hooks` and `react-refresh` rules. Fix any reported issues before opening a PR.

### Type Check and Build

```bash
pnpm build
```

This runs `tsc` followed by a Vite production build. If the TypeScript compiler reports errors, the build will fail. Resolve all type errors before submitting a PR.

### Preview the Production Build

```bash
pnpm preview
```

Serves the compiled output locally so you can verify the production bundle before pushing.

There is no automated test framework configured at this time. Manual testing against a local Supabase instance is the current practice.

---

## Etymology Contributions

The etymology suggestion engine is a rule-based pattern matcher in:

```
supabase/functions/suggest-etymology/index.ts
```

It currently has **57 suffix patterns** (road types, geographic features, settlement elements) and **34 prefix patterns** (descriptive, directional, colour, nobility, landmarks).

### Adding a Suffix Pattern

Suffix patterns match the end of a street name (e.g., `gate`, `wick`, `thorpe`). Each entry follows this shape:

```ts
{
  pattern: /gate$/i,
  element: 'gate',
  meaning: 'street or way',
  origin: 'Old Norse',
  period: 'Viking Age (c.850–1100)',
}
```

Add new entries to the suffix patterns array and include:
- A clear `meaning` (what the element means in plain English)
- An accurate `origin` (language or culture of origin)
- An approximate historical `period`

### Adding a Prefix Pattern

Prefix patterns match the start of a street name (e.g., `high`, `royal`, `fleet`):

```ts
{
  pattern: /^high/i,
  element: 'high',
  meaning: 'important or main route',
  origin: 'Old English',
  period: 'Anglo-Saxon',
}
```

### Sources and Confidence

If you add patterns, please reference a credible source in a comment — for example, the English Place-Name Society, the Oxford Dictionary of English Place-Names, or equivalent regional reference works. Patterns with no backing source will not be merged.

The confidence field is computed automatically (`"medium"` when patterns match, `"low"` when none do) and does not need manual adjustment.

---

## Documentation

Research and technical documentation lives in the `docs/` directory, organised by topic:

```
docs/
  ai_ml/        AI/ML etymology analysis
  auth/         Authentication and community design
  database/     Database solution analysis
  domain/       Domain and SSL research
  hosting/      Hosting platform comparison
  mapping/      Mapping service analysis
  open_data/    UK open data sources
  storage/      Storage cost analysis
```

If you add a significant new feature or make a technical decision that future contributors should understand, add a brief Markdown document to the appropriate subdirectory. Keep documentation factual and focused — link to external references rather than reproducing them in full.

---

## Code of Conduct

Streets Past is a small, friendly open-source project. A few expectations:

- Be respectful and considerate in all interactions — issues, pull requests, and discussion threads.
- Assume good faith. If something is unclear, ask before escalating.
- Stay on topic. This project is about UK street etymology and history; keep contributions relevant.
- Attribution matters — if you draw on external research or data sources, cite them.
- Discriminatory language or personal attacks of any kind will not be tolerated and will result in removal from the project.

If you have concerns about someone's behaviour, open a private issue or contact a maintainer directly.

---

We appreciate every contribution, whether it is a typo fix, a new etymology pattern, or a major feature. Thank you for helping build Streets Past.
