# CLAUDE.md - Streets Past Project Guide

## Project Overview

**Streets Past** is a full-stack web application for exploring the etymological origins and histories of UK street names. Users can search streets, explore an interactive map, view etymologies, and contribute their own research. The project targets the UK market with data sourced from OS OpenNames (~790,000 street records).

**Live deployment:** https://6fv9t1y43vab.space.minimax.io
**Canonical domain:** https://streetetymology.co.uk/

## Repository Structure

```
Streets-Past/
├── street-etymology/          # Main frontend application (React + Vite + TypeScript)
│   ├── src/
│   │   ├── App.tsx            # Root component with routing (react-router-dom v6)
│   │   ├── main.tsx           # Entry point with ErrorBoundary + StrictMode
│   │   ├── index.css          # Global styles (Tailwind + CSS variables)
│   │   ├── components/        # Reusable UI components
│   │   │   ├── Header.tsx     # Sticky nav with auth-aware menu
│   │   │   ├── Footer.tsx     # Site footer
│   │   │   ├── SearchBar.tsx  # Autocomplete search with debounced Supabase queries
│   │   │   ├── MapView.tsx    # MapLibre GL JS interactive map component
│   │   │   ├── ContributionForm.tsx  # User etymology submission form
│   │   │   ├── NewsletterSignup.tsx  # Email subscription component
│   │   │   └── ErrorBoundary.tsx     # React error boundary wrapper
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx # Auth provider using Supabase Auth
│   │   ├── hooks/
│   │   │   └── use-mobile.tsx # Mobile detection hook
│   │   ├── pages/             # Route-level page components
│   │   │   ├── HomePage.tsx
│   │   │   ├── SearchPage.tsx
│   │   │   ├── MapPage.tsx    # Full-screen map (no header/footer layout)
│   │   │   ├── StreetDetailPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   ├── AdminPage.tsx  # Moderation dashboard (admin/moderator roles)
│   │   │   ├── AboutPage.tsx
│   │   │   ├── PrivacyPage.tsx
│   │   │   └── TermsPage.tsx
│   │   └── lib/
│   │       └── supabase.ts    # Supabase client + type definitions (Street, Profile, Contribution)
│   ├── package.json           # pnpm project config
│   ├── vite.config.ts         # Vite config with path aliases (@/ -> ./src/)
│   ├── tailwind.config.js     # Tailwind v3 with custom heritage/amber theme
│   ├── tsconfig.json          # TypeScript project references
│   ├── tsconfig.app.json      # App TS config (strict: false)
│   ├── eslint.config.js       # Flat ESLint config with React hooks/refresh
│   ├── postcss.config.js      # PostCSS with Tailwind + Autoprefixer
│   ├── components.json        # shadcn/ui config (new-york style, lucide icons)
│   └── index.html             # SPA entry with SEO meta tags + structured data
│
├── supabase/                  # Supabase Edge Functions (Deno runtime)
│   └── functions/
│       ├── suggest-etymology/ # AI etymology suggestion via pattern matching
│       │   └── index.ts       # Deno.serve() - linguistic rule-based analysis
│       └── create-bucket-historical-maps-temp/
│           └── index.ts       # Storage bucket creation with RLS policies
│
├── external_api/              # Python API proxy layer
│   ├── __init__.py            # Auto-loads function proxies from JSON
│   ├── function_utils.py      # FunctionProxy class + ToolResult model (Pydantic)
│   ├── data_sources/          # Data source integrations (various web APIs)
│   └── mcp_function_list.json # MCP function registry
│
├── browser/                   # Browser automation utilities
│   ├── global_browser.py      # Playwright browser management
│   ├── browser_extension/     # Error capture extension
│   ├── extracted_content/     # Scraped content (e.g., OSM tile usage policy)
│   ├── screenshots/           # Browser screenshots
│   └── user_data/             # Browser profile data
│
├── docs/                      # Research documentation
│   ├── ai_ml/                 # AI/ML etymology analysis research
│   ├── auth/                  # Authentication & community analysis
│   ├── database/              # Database solution analysis
│   ├── domain/                # Domain & SSL cost analysis
│   ├── hosting/               # Hosting platform comparison
│   ├── mapping/               # Mapping service analysis
│   ├── open_data/             # UK open data research
│   └── storage/               # Storage cost analysis & calculations
│
├── .memory/                   # Internal metadata (todo tracking, URL sources)
├── memories/                  # Build progress notes
├── memory/                    # Research history records
├── pyproject.toml             # Python 3.12.5 project config (hatchling build)
└── .gitignore                 # Comprehensive multi-language gitignore
```

## Tech Stack

### Frontend (street-etymology/)
- **React 18** with TypeScript
- **Vite 6** as build tool (with `@vitejs/plugin-react`)
- **React Router DOM v6** for client-side routing
- **Tailwind CSS v3.4** with `tailwindcss-animate` plugin
- **shadcn/ui** components (new-york style, Radix UI primitives)
- **MapLibre GL JS v5** for interactive mapping (OpenStreetMap tiles)
- **Supabase JS SDK v2** for database, auth, and storage
- **lucide-react** for icons
- **react-hot-toast** / **sonner** for notifications
- **zod** + **react-hook-form** for form validation
- **recharts** for data visualization
- **pnpm** as package manager

### Backend
- **Supabase** (PostgreSQL + PostGIS + Auth + Storage + Edge Functions)
- **Deno** runtime for Supabase Edge Functions
- **Python 3.12.5** for external API layer and data processing

### Database (Supabase)
- **PostgreSQL** with **PostGIS** spatial extension
- **Row Level Security (RLS)** for data access control
- Core tables: `streets`, `contributions`, `profiles`, `newsletter_subscribers`, `historical_maps`
- Supabase project ID: `nadbmxfqknnnyuadhdtk`

## Development Commands

All commands run from the `street-etymology/` directory:

```bash
# Install dependencies
pnpm install

# Start dev server
pnpm dev

# Build for production (includes TypeScript check)
pnpm build

# Build for production deployment (no source identifiers)
pnpm build:prod

# Run ESLint
pnpm lint

# Preview production build
pnpm preview

# Clean install (nuclear option)
pnpm run clean
```

**Note:** The `dev`, `build`, `lint`, and `preview` scripts all auto-run `pnpm install --prefer-offline` first. The pnpm store is configured via `.npmrc` to use `/tmp/.pnpm-store`.

## Architecture & Patterns

### Routing
Two layout patterns in `App.tsx`:
- **MainLayout**: Header + content + Footer (most pages)
- **FullScreenLayout**: No chrome, used for `/map`
- Auth pages (`/login`, `/register`) have no layout wrapper

All routes:
| Path | Component | Layout | Notes |
|------|-----------|--------|-------|
| `/` | `HomePage` | MainLayout | Landing page |
| `/search` | `SearchPage` | MainLayout | Street search with autocomplete |
| `/street/:id` | `StreetDetailPage` | MainLayout | Individual street etymology |
| `/map` | `MapPage` | FullScreenLayout | Interactive UK map |
| `/contribute` | `SearchPage` | MainLayout | Contribution entry point (reuses SearchPage) |
| `/profile` | `ProfilePage` | MainLayout | User profile |
| `/admin` | `AdminPage` | MainLayout | Moderation dashboard |
| `/about` | `AboutPage` | MainLayout | About the project |
| `/privacy` | `PrivacyPage` | MainLayout | Privacy policy |
| `/terms` | `TermsPage` | MainLayout | Terms of service |
| `/login` | `LoginPage` | None | Auth page |
| `/register` | `RegisterPage` | None | Auth page |
| `/auth/callback` | `HomePage` | MainLayout | OAuth callback handler |

### Authentication
- `AuthContext` provides `user`, `session`, `profile`, `loading`, `signIn`, `signUp`, `signOut`, `isAdmin`
- Roles: `user`, `moderator`, `admin` (stored in `profiles.role`)
- `isAdmin` check: `profile?.role === 'admin' || profile?.role === 'moderator'`
- Auth state listener via `supabase.auth.onAuthStateChange()`

### Data Access
- All database access goes through the Supabase JS client (`src/lib/supabase.ts`)
- Type exports: `Street`, `Profile`, `Contribution`
- Spatial queries use PostGIS for map-related features
- Search uses debounced Supabase `.ilike()` queries

### Map
- MapLibre GL JS with OpenStreetMap raster tiles (no API key needed)
- Map centered on UK: `[-2.5, 54.0]`, zoom `5.5`
- Bounded to UK: SW `[-12, 49]` to NE `[3, 61]`
- Custom amber/brown gradient markers with popups

### Edge Functions (Deno)
- `create-bucket-historical-maps-temp`: One-time storage setup function (public bucket, 10MB limit, `image/*` + `application/pdf`)
- All functions include CORS headers for cross-origin access

#### `suggest-etymology` Algorithm

The etymology engine (`supabase/functions/suggest-etymology/index.ts`) uses a rule-based pattern matching approach:

1. **Input**: `{ streetName: string }` via POST
2. **Normalize**: Lowercase + trim, split into words
3. **Suffix/word matching** against 57 etymology patterns (road types, geographic features, settlement elements)
4. **Prefix/word matching** against 34 prefix patterns (descriptive, color, nobility, landmark)
5. **Deduplicate** matched elements by name
6. **Generate suggestion** combining element meanings, origins, and historical periods
7. **Output**: `{ streetName, etymology, elements[], confidence, sources[] }`

**Pattern categories (57 suffix patterns)**:
- Road types: gate (ON), street (Latin/OE), lane (OE), way (OE), road (OE), close (OF), court (OF), place (OF), row (OE)
- Geographic: hill, green, field, ford, bridge, heath, moor, meadow, grove, wood
- Settlement: bury (OE "burh"), ton (OE "tun"), ham (OE), stead (OE), worth (OE), wick (OE)
- Norse: gate ("gata"), kirk, toft, thorpe, by, beck, thwaite
- Religious: church, abbey, priory, castle
- Commerce: mill, market, cheap ("ceap"), shambles ("scamel")
- Modern (17th-19th c.): parade, terrace, crescent, square, circus, avenue, boulevard, mews

**Prefix categories (34 prefix patterns)**:
- Descriptive: high, low, old, new, great, little, long, broad
- Directional: north, south, east, west, upper, lower
- Colors: white, black, green, red, golden, silver
- Nobility: royal, king, queen, prince, duke, lord
- Landmarks: abbey, church, mill, cross, fleet, well, spring

**Confidence levels**: `"medium"` (elements found) or `"low"` (no recognized elements)
**Sources**: English Place-Name Society, Oxford Dictionary of English Place-Names, University of Nottingham

## Code Conventions

### TypeScript
- Strict mode is **off** (`strict: false` in tsconfig.app.json)
- `@typescript-eslint/no-unused-vars` and `@typescript-eslint/no-explicit-any` are **off**
- Path alias: `@/` maps to `./src/`
- Target: ES2020, module: ESNext, JSX: react-jsx

### Styling
- Tailwind CSS with custom design tokens via CSS variables
- Heritage/academic theme: amber primary (`#b45309`), stone secondary (`#57534e`), parchment accents
- Custom color palette: `heritage.gold`, `heritage.brown`, `heritage.parchment`, `heritage.ink`
- Fonts: Georgia/serif for headings, Inter/sans-serif for body
- Dark mode support via `class` strategy (configured but not fully implemented)
- Container: centered, `2rem` padding, max `1400px`

### Component Patterns
- Named exports for all components (not default exports, except `App`)
- Functional components with hooks
- Props interfaces defined inline or near component
- Supabase data fetching in `useEffect` hooks
- Custom hooks in `src/hooks/`

### ESLint
- Flat config format (`eslint.config.js`)
- `react-hooks` and `react-refresh` plugins enabled
- `react-refresh/only-export-components: warn` with `allowConstantExport: true`

## Environment Variables

A template is provided at `street-etymology/.env.example`. Copy it to `.env.local` and fill in values:

```bash
cp street-etymology/.env.example street-etymology/.env.local
```

Required in `.env.local` for the frontend:
```
VITE_SUPABASE_URL=<supabase_project_url>
VITE_SUPABASE_ANON_KEY=<supabase_anon_key>
```

Supabase Edge Functions use:
```
SUPABASE_URL        # Auto-provided by Supabase
SUPABASE_SERVICE_ROLE_KEY  # Auto-provided by Supabase
```

## Key Files to Know

| File | Purpose |
|------|---------|
| `street-etymology/src/lib/supabase.ts` | Supabase client init + shared types |
| `street-etymology/src/contexts/AuthContext.tsx` | Global auth state management |
| `street-etymology/src/App.tsx` | All route definitions (13 routes) |
| `street-etymology/src/components/MapView.tsx` | MapLibre map with street markers |
| `street-etymology/src/components/SearchBar.tsx` | Debounced autocomplete search |
| `street-etymology/tailwind.config.js` | Custom theme (colors, fonts, animations) |
| `street-etymology/vite.config.ts` | Build config with path aliases |
| `street-etymology/.env.example` | Environment variable template |
| `supabase/functions/suggest-etymology/index.ts` | Etymology pattern matching engine (57 suffix + 34 prefix patterns) |
| `docs/ai_ml/suggest_etymology_algorithm.md` | Full algorithm documentation for etymology engine |
| `complete_street_etymology_website_setup.md` | 390+ line production setup guide with cost breakdowns |
| `memory/research_history_record.json` | 8 completed research initiatives tracking |
| `docs/` | Extensive research docs for all technical decisions |

## Database Schema (Core Tables)

- **streets**: `id`, `name`, `city`, `county`, `postcode`, `latitude`, `longitude`, `etymology_suggestion`, `etymology_verified`, `historical_period`, metadata
- **contributions**: `id`, `street_id`, `user_id`, `etymology_text`, `sources`, `status` (pending/approved/rejected)
- **profiles**: `user_id`, `email`, `full_name`, `role` (user/moderator/admin), `contribution_count`
- **newsletter_subscribers**: email subscription management
- **historical_maps**: map image metadata linked to streets

## Common Tasks

### Adding a new page
1. Create component in `src/pages/NewPage.tsx` (named export)
2. Add route in `src/App.tsx` within appropriate layout
3. Add nav link in `src/components/Header.tsx` if needed

### Adding a new component
1. Create in `src/components/ComponentName.tsx`
2. Use Tailwind classes with the project's amber/stone color palette
3. Import Supabase types from `../lib/supabase` if needed

### Working with the map
- MapView component handles initialization, marker management, and fly-to animations
- Street data loaded from Supabase with spatial filtering
- Markers use amber gradient styling consistent with the heritage theme

### Adding a Supabase Edge Function
1. Create directory under `supabase/functions/<function-name>/`
2. Add `index.ts` using `Deno.serve()` pattern
3. Include CORS headers for all responses
4. Handle OPTIONS preflight requests

## Project History & Research Records

The project was built starting 2025-12-04 and deployed to MiniMax hosting (`space.minimax.io`). Several metadata files track the build and research process:

### Build Completion (`memories/street_etymology_report_completion.md`)
Full build progress log with completion checklist. All items completed: database setup, edge functions, storage buckets, auth system, all pages, build, deploy, and testing.

### Research History (`memory/research_history_record.json`)
Tracks 8 completed research initiatives that informed every technical decision:

| Research Task | Deliverable | Key Decision |
|---------------|-------------|--------------|
| Domain & SSL costs | `docs/domain/domain_ssl_costs.md` | Namecheap .org (~£8/yr) + free Cloudflare SSL |
| Authentication & community | `docs/auth/auth_community_analysis.md` | Supabase Auth (50k MAU free) |
| Database solutions | `docs/database/database_analysis.md` | Supabase PostgreSQL + PostGIS |
| Storage solutions | `docs/storage/storage_analysis.md` | Supabase Storage (1GB free), Cloudinary alt |
| UK open data | `docs/open_data/uk_open_data_analysis.md` | OS OpenNames (~790k streets, OGL v3.0) |
| AI/ML etymology | `docs/ai_ml/ai_ml_analysis.md` | Hybrid local + GPT-4o mini ($6-$95/100k req) |
| Hosting options | `docs/hosting/hosting_analysis.md` | Cloudflare Pages (unlimited bandwidth) |
| Mapping solutions | `docs/mapping/mapping_analysis.md` | MapLibre GL JS + LocationIQ/OpenCage |

### Source Tracking (`.memory/url_source_meta.json`)
Tracks 51 research topics with 46+ source URLs across all research areas. Each source includes publisher, title, URL, and a summary of key information extracted.

### Production Setup Guide (`complete_street_etymology_website_setup.md`)
390+ line comprehensive guide covering:
- Executive summary with cost projections
- Technical architecture (serverless Jamstack)
- Storage solutions comparison (Supabase vs Cloudinary vs AWS S3)
- Detailed Year 1/Year 2 cost breakdowns (MVP: £8-£44/yr, Growth: £44-£164/yr)
- Weekend MVP setup guide (48-hour plan)
- Scalability roadmap (MVP to 50k+ users)
- Data strategy (OS OpenNames + community contributions)
- Backup, monitoring, and risk mitigation

### Workspace Metadata (`workspace.json`)
MiniMax platform metadata: 1,022 files, ~47MB workspace size. The hosting platform is MiniMax (`space.minimax.io`), not Netlify/Vercel/Cloudflare despite research docs covering those options.

## Notes

- The project uses `vite-plugin-source-identifier` for dev debugging (disabled in prod builds via `BUILD_MODE=prod`)
- The `.npmrc` file redirects pnpm store to `/tmp` paths - this is intentional for the deployment environment
- Research documentation in `docs/` is extensive and covers all technical decisions made during planning
- The `external_api/` Python layer is a supporting service, not the primary backend
- The `browser/` directory contains research/scraping utilities, not part of the main application
