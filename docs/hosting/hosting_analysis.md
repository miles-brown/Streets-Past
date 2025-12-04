# Cost-effective hosting for a street name etymology site with ~1M records: Comparative analysis of GitHub Pages, Cloudflare Pages, Netlify, and Vercel free tiers

## Executive summary

A public, static website for street name etymology at the scale of ~1 million records can be hosted reliably on free tiers, provided the dataset is optimized for CDN-friendly delivery and search is implemented with client-side indexes. Among the major platforms, Cloudflare Pages and Vercel stand out for their modern edge capabilities and developer experience, while GitHub Pages offers the simplest path to purely static publishing. Netlify’s Starter plan remains an attractive all-rounder, though some of its quota figures require verification due to extraction issues.

Key constraints most likely to shape the solution are dataset size and build/deployment limits: GitHub Pages caps published site size at 1 GB and enforces a soft 100 GB monthly bandwidth limit and a 10-minute deployment timeout; Cloudflare Pages allows 20,000 files per site with a 25 MiB per-file limit and 500 builds/month on the free plan; and Vercel’s Hobby plan provides substantial monthly allocations (e.g., build minutes and function quotas) but restricts commercial use and places limits on data transfer, deployments, and logs. Netlify’s free plan includes 100 GB bandwidth and 300 build minutes according to third-party sources; however, official documentation should be consulted to confirm exact values given extraction failures.

Recommendations:
- For a pure static build with prebuilt search indexes, Cloudflare Pages is the most robust default: static asset bandwidth is unlimited, edge functions are metered generously, and the platform’s performance characteristics are well suited to global delivery[^8][^9][^6][^7].
- For teams wanting a managed developer experience, Vercel Hobby can work if usage remains personal/non-commercial, with the caveat of bandwidth and function quotas[^10][^11][^12][^13].
- GitHub Pages is sufficient if the entire dataset plus index stays well under the 1 GB published-site limit and bandwidth remains under ~100 GB/month; it is the simplest but also the most constrained[^1].
- Netlify Starter is viable if the verified quotas meet the project’s needs and the 100 GB/month bandwidth cap is sufficient; confirm limits on the official pricing page[^16][^18].

Information gaps requiring follow-up:
- Netlify’s official documentation returned errors during extraction; several quota figures cited by third parties (e.g., 100 GB bandwidth and 300 build minutes) should be validated directly on Netlify’s pricing page and knowledge base[^16][^17][^18].
- Cloudflare does not explicitly document a bandwidth cap for Cloudflare Pages static asset delivery; statements that “requests to static assets are free and unlimited” should be confirmed in the latest Cloudflare documentation[^8][^7].
- For Vercel Hobby, the “build execution minutes” figure reported as 6,000 minutes on the plan page should be cross-checked against the Limits documentation[^10][^11].
- GitHub Pages site count limits per account (user/organization) should be verified against the latest official docs[^1].

To orient the reader, Table 1 summarizes the most relevant free-tier constraints.

Table 1 — Top constraints at a glance (free tiers; verification flags indicate items to validate)
| Platform | Storage/site limits | Bandwidth caps | Build/deploy limits | Edge/serverless availability | SSL | Custom domains | Commercial use |
|---|---|---|---|---|---|---|---|
| GitHub Pages | Published site ≤1 GB; repo recommended ≤1 GB[^1] | 100 GB/month (soft)[^1] | 10 builds/hour (soft); 10-minute deployment timeout[^1] | None (static hosting only) | Yes (automatic) | Yes | Yes (public repos) |
| Cloudflare Pages | ≤20,000 files; 25 MiB per file[^6] | Unclear for static assets; static requests free per Cloudflare Functions pricing[^8] | 500 builds/month; 20-minute build timeout[^6] | Pages Functions billed as Workers with daily quotas[^5][^8] | Yes (Free plan)[^19] | Yes (up to 100 custom domains/project)[^6] | Not specified on cited pages |
| Netlify (Starter) | Not verified (extraction failed) | 100 GB/month (third-party; verify)[^16] | 300 build minutes (third-party; verify)[^16] | Functions & Edge Functions available (limits vary; verify)[^16][^17] | Yes | Yes | Not specified on cited pages |
| Vercel (Hobby) | Disk 23 GB; source uploads 100 MB; env var total 64 KB[^11] | Fast data transfer 100 GB; fast origin transfer up to 10 GB[^11] | Deploys/day 100; build time per deploy 45 min; build execution hours 100; builds/hour rate limit 32[^11] | Functions and Edge Functions with invocations quotas and duration caps[^10][^13] | Yes | Yes (≤50 domains/project)[^11] | Hobby is personal/non-commercial[^10] |

Interpretation: The data shows GitHub Pages as the most constrained by storage and bandwidth, while Cloudflare’s platform removes bandwidth anxiety for static assets but enforces file-count and per-file limits that affect index packaging. Vercel offers generous compute and function quotas but imposes explicit bandwidth and log-retention limits, alongside a non-commercial restriction on Hobby. Netlify’s Starter plan is competitive on paper for static delivery if the 100 GB/month bandwidth and 300 build minutes are accurate—yet they must be verified.

---

## Methodology and source reliability

This assessment relies primarily on official documentation to ensure authoritative, policy-aligned conclusions. Where official sources were inaccessible due to transient extraction failures, we triangulate with Netlify’s official blog or community answers and explicitly flag items for verification. Cloudflare’s platform pages document limits and pricing mechanics, and Vercel’s plan and limits pages are the basis for quotas and fair-use rules. Only after establishing these platform constraints do we model practical implications for a 1 million–record dataset.

Key official sources include:
- GitHub Pages limits for bandwidth, site size, and deployment timeouts[^1].
- Cloudflare Pages limits for build counts, timeouts, file counts, per-file limits, domains, and redirects[^6].
- Cloudflare Workers/Pages Functions pricing and quotas, including daily request limits and free-tier mechanics[^5].
- Vercel’s plan descriptions, quotas, function limitations, and data-transfer constraints[^10][^11][^12][^13].
- Netlify’s pricing page and knowledge base; where access failed, we reference Netlify’s blog announcement introducing the free plan and a community answer describing overage behavior, marking the related values for verification[^16][^18][^17].

---

## Context and requirements

The workload centers on a public, read-heavy website containing etymology records for ~1 million streets. The site should offer low-latency access from many geographies, support search-as-you-type behavior, and expose details pages for individual records. Given public accessibility and likely viral social traffic spikes, the delivery model must be CDN-first, with static assets cached aggressively at the edge. While user-contributed content or analytics are plausible future additions, the initial scope focuses on static hosting with optional client-side search and minimal dynamic logic.

Non-functional requirements include:
- Global performance and resilience via a widely distributed CDN.
- Minimal ops burden and predictable hosting costs (ideally free-tier compatible).
- Compliance with platform terms, including licensing constraints such as Vercel’s non-commercial use on the Hobby plan[^10].
- A migration path that avoids hard rewrites if paid tiers become necessary later.

---

## Platform analyses (free tiers)

### GitHub Pages (free)

GitHub Pages is straightforward static hosting with automatic SSL and custom domain support. Its constraints are clear: a published site may be up to 1 GB; source repositories are recommended to stay at or below 1 GB; monthly bandwidth is soft-limited at 100 GB; deployments time out at 10 minutes; and builds are limited to 10 per hour as a soft limit (note that this soft limit does not apply to builds executed by custom GitHub Actions workflows, which can be used to bypass the Pages build rate limit)[^1]. There are no serverless functions or edge runtime features; Pages simply serves static content from the configured branch.

Suitability for 1M records: If the entire dataset, generated HTML, assets, and search index fit within ~1 GB and monthly bandwidth stays well under the 100 GB cap, GitHub Pages can work. Client-side search will require shipping a prebuilt index; keeping the index small and highly compressible becomes critical. If either the size or bandwidth ceiling risks being exceeded, more flexible platforms are preferable.

### Cloudflare Pages (free)

Cloudflare Pages pairs fast static delivery with generous platform limits: up to 20,000 files per site, a 25 MiB maximum per file, 500 builds per month, a 20-minute build timeout, and up to 100 custom domains per project[^6]. Redirects and header rules have defined ceilings (e.g., up to 2,100 total redirects per file), and preview deployments are unlimited. The Free plan includes SSL and global CDN delivery[^19].

Notably, Cloudflare’s functions pricing states that “requests to static assets are free and unlimited” and that Pages Functions are billed as Workers under the standard usage model[^8][^5]. This has practical implications: if search or routing avoids invoking functions, bandwidth for static assets is not directly metered. By contrast, any dynamic behavior—API routes, SSR-like endpoints, or request manipulation—consumes Workers daily quotas. On the free tier, Workers provide 100,000 requests/day and a 10 ms CPU-time-per-invocation budget; related services (KV, D1, Durable Objects) have their own quotas and storage limits[^5].

Suitability for 1M records: The file-count and per-file limits influence how the dataset and index are packaged. A single monolithic JSON file is likely to breach the 25 MiB per-file cap. The recommended approach is to segment the dataset into small, paginated bundles (e.g., shards by name prefix or geography) and generate a compact, prebuilt client-side search index. As long as requests do not invoke functions, static delivery is unlimited. If lightweight dynamic search or API filtering is needed, Cloudflare’s Workers quotas are generous for a free tier, but sustained high-volume traffic should be monitored against daily caps[^5][^8].

### Netlify (free/Starter)

Netlify’s Starter plan is widely used for static sites and Jamstack workflows. Based on accessible third-party sources, the free plan typically includes 100 GB bandwidth/month and 300 build minutes/month. Netlify community guidance clarifies that exceeding free-plan limits does not shut off the site; metered services (e.g., analytics, forms, build minutes) are auto-billed or soft-throttled, and usage continues[^16][^18]. The official blog introducing the free plan reiterates generous monthly allocations but should be used as a secondary source until pricing page details are confirmed[^17].

Functions and Edge Functions are core to Netlify’s model. However, specific invocation caps for the free plan were not verifiable in this review due to website extraction issues and should be validated. Custom domains and SSL are supported on the free tier.

Suitability for 1M records: If the verified quotas align (100 GB bandwidth and 300 build minutes), Netlify can host a static dataset and a client-side index similar to other platforms. Any server-side search or API routes will consume function invocations and need careful quota management or migration to a paid tier[^16][^17][^18].

### Vercel (Hobby/free)

Vercel’s Hobby plan targets personal, non-commercial projects. Quotas are extensive but clearly bounded: 100 deployments/day, a build-time limit of 45 minutes per deployment, 100 build execution hours overall, and a 32 builds/hour rate limit. Storage and data transfer limits include 23 GB disk, 100 GB of “fast data transfer,” and up to 10 GB of “fast origin transfer.” Logs are retained for 1 hour for runtime (build logs are retained indefinitely), and up to 50 domains per project are allowed[^11]. The plan page also lists function-related quotas (e.g., 1 million function invocations, active CPU and provisioned memory GB-hours) and notes duration caps and fair-use constraints[^10]. Function internals include a maximum uncompressed bundle size of 250 MB and maximum durations that can be configured up to 60 seconds (with defaults around 10 seconds)[^13].

Suitability for 1M records: Vercel’s static delivery and client-side search index strategy is compatible with Hobby. However, non-commercial terms limit production use for organizations. Data-transfer caps, deployment frequency limits, and short runtime log retention are operationally relevant. If the site benefits from Vercel’s developer tooling and the use remains personal or exploratory, Hobby can be a strong choice; otherwise, a paid plan is necessary[^10][^11][^12][^13].

---

## Search strategy options for 1M records

The central technical decision is how to implement search within free-tier constraints. Client-side search requires shipping an index; server-side or edge-side search requires invoking functions and staying within quotas.

Client-side options:
- Prebuilt search indexes such as Lunr allow building a serialized index at build time and loading it in the browser. Lunr’s documentation explicitly recommends prebuilding indexes for large or static datasets to avoid heavy client-side computation[^14]. Lunr and Elasticlunr provide stemming, stop words, and scoring with compact libraries suited to static distribution.
- Trade-offs include index size and initial load time. A million records can produce a large index, often too big to load on mobile networks. Mitigations include segmenting the index into shards (e.g., by first letter or region), lazy-loading shards on demand, and compressing aggressively (Brotli).

Edge/serverless search:
- Cloudflare Workers/Pages Functions, Netlify Functions/Edge Functions, and Vercel Functions support API endpoints that query a key-value store, KV-style index, or a compact shard. This approach trades bandwidth for compute and keeps the client payload small. The downside is hitting quotas: Cloudflare’s free tier offers 100,000 requests/day (CPU-time capped), Netlify’s invocation limits are not confirmed here, and Vercel’s Hobby plan provides 1 million function invocations with duration and GB-hour limits[^5][^10][^8].

Recommendation:
- Begin with a client-side search index generated at build time, shard the index by name prefixes to limit download size, and load shards lazily. Use Web Workers to keep the UI responsive. If user feedback indicates slow initial loads or poor mobile performance, pivot to an edge API backed by a small KV index (for Workers/KV) or equivalent, and reserve the API for longer queries while keeping instant suggestions client-side[^14][^5].

---

## Data modeling and asset packaging

Given platform limits, the data model must minimize asset sizes and avoid over-the-wire bloat. A pragmatic structure for ~1 million records includes:

- Per-record JSON: fields for name, alternative names, city/region, etymology text, sources, and lat/long. Keep field values concise (short keys, normalized strings).
- Record pages: static HTML pages can be prerendered and cached; their static nature plays well with CDN caching rules.
- Client-side index: build a compact, inverted index with tokens derived from names and aliases. Avoid verbose payloads; emit positional data only if phrase search is essential.
- Sharding: group records alphabetically (e.g., a–z) or by region. Shard both the dataset bundles and the search index to reduce initial transfer.

GitHub Pages constraints argue strongly for staying under 1 GB total. Cloudflare’s 20,000-file limit and 25 MiB per-file limit mean that sharding into many small files is acceptable, but single assets must remain small. Vercel’s 23 GB disk and 100 GB fast data transfer quotas are ample for a static site but not unlimited; careful asset management matters if you later add dynamic routes or function-backed features[^1][^6][^11].

Table 2 — File and asset constraints affecting dataset packaging
| Platform | Max files per site | Max file size | Published site size | Practical implication |
|---|---|---|---|---|
| GitHub Pages | N/A (not specified) | N/A (not specified) | ≤1 GB[^1] | Keep total output ≤1 GB; index must be small and compressible |
| Cloudflare Pages | ≤20,000[^6] | 25 MiB[^6] | Not specified | Avoid monolithic JSON; shard into small files within the per-file limit |
| Vercel (Hobby) | N/A (not a file-count limit) | N/A (not specified) | Disk 23 GB[^11] | Large datasets possible, but manage total size and transfer caps |
| Netlify (Starter) | Not verified | Not verified | Not verified | Validate official docs before committing to packaging strategy |

---

## Performance and bandwidth outlook

Bandwidth and cache policy determine operating cost and user-perceived latency. Static assets benefit from CDN caching; if the site architecture keeps requests from invoking functions, Cloudflare’s model makes the egress cost predictable and potentially zero for static assets[^8]. On Vercel, fast data transfer is capped at 100 GB, with up to 10 GB for fast origin transfer; this cap shapes overall monthly traffic before considering an upgrade[^11]. GitHub Pages’ 100 GB/month soft cap is adequate for moderate traffic but risky for spikes[^1]. Netlify’s 100 GB/month free bandwidth, if confirmed, behaves similarly with soft overages handled via metering rather than hard cutoffs[^16][^18].

Operational tactics:
- CDN caching: set long TTLs for static bundles and immutable assets; employ cache-busting via hashed filenames.
- Content segmentation: split the dataset and index so that only the necessary shards download for a given query.
- Client-side throttling: debounce search input, prefetch likely shards on hover, and lazy-load as the user scrolls.

---

## Risks, overages, and platform policies

- Non-commercial restrictions: Vercel’s Hobby plan is intended for personal, non-commercial projects; using it for a public production site may violate terms. Teams should either keep usage personal or choose a paid plan[^10].
- Soft caps and metering: Netlify’s free tier allows overages via auto-billing or soft-throttling rather than immediate shutdown, but unexpected spikes can still incur charges; monitor usage closely[^18]. GitHub Pages’ bandwidth and build limits are soft; extreme bursts may prompt GitHub to intervene, though Actions-based builds can avoid Pages’ 10 builds/hour soft limit[^1].
- Daily quotas: Cloudflare Workers and related services enforce daily quotas that reset at 00:00 UTC; once exhausted, further operations fail. Carefully model worst-case traffic against the 100,000 requests/day limit and CPU-time budgets[^5].
- Log retention: Vercel retains runtime logs for one hour on Hobby, which can complicate debugging after incidents. Consider external log aggregation for production use[^11].
- Vendor lock-in: Using a platform’s proprietary functions, KV, or analytics increases switching costs. To mitigate, keep the core site content portable (plain static assets and client-side index) and encapsulate platform-specific features behind a clear boundary.

---

## Cost scenarios and scaling path

Free-tier viability depends on traffic patterns and search mechanics. A CDN-first delivery model with client-side, sharded search is most likely to remain within free quotas. If traffic grows or the product adds dynamic features, paid tiers with higher limits become necessary.

Table 3 — Monthly traffic scenarios vs free-tier limits (assumptions noted)
| Scenario | Avg page size (HTML + assets) | Monthly pageviews | Est. monthly egress | GitHub Pages | Cloudflare Pages | Netlify Starter | Vercel Hobby |
|---|---:|---:|---:|---|---|---|---|
| Low | 150 KB | 100,000 | ~14.3 GB | Fits under 100 GB; watch build spikes[^1] | Static bandwidth unclear but generally unlimited for static requests[^8] | Likely fits 100 GB (verify)[^16] | Fits under 100 GB fast transfer[^11] |
| Medium | 150 KB | 500,000 | ~71.5 GB | Approaches cap; consider optimizing caching[^1] | Same as low; static egress free[^8] | Borderline; verify metering[^16][^18] | Borderline; monitor fast transfer[^11] |
| High | 150 KB | 1,000,000 | ~143 GB | Exceeds cap; not viable without reductions[^1] | Static requests remain free; Functions invocations must be controlled[^8] | Exceeds 100 GB; likely billed/soft-throttled[^16][^18] | Exceeds 100 GB; upgrade needed[^11] |

Interpretation: Client-side search reduces function invocations, preserving the free-tier budget for platforms that meter compute. Static delivery without function invocation is especially favorable on Cloudflare. On Vercel and Netlify, traffic above ~100 GB/month on free tiers pushes teams toward paid plans.

Table 4 — Scaling triggers and recommended upgrades
| Trigger | What to watch | Recommended path |
|---|---|---|
| Approaching bandwidth cap | Rising egress and cache misses | Cloudflare: stay static-only; Vercel/Netlify: upgrade plan or add egress management[^8][^11][^16] |
| Build minutes exhaust | Frequent releases, large bundles | Cloudflare: optimize builds; consider Pro if needed[^6] |
| Function/API usage grows | Invocations near daily or monthly limits | Cloudflare: move to paid Workers; Netlify/Vercel: paid tiers with higher invocations[^5][^10][^16] |
| Index too large for client | Mobile performance degrades | Introduce edge API with KV index; keep client suggestions |
| Commercial use required | Production site for orgs | Avoid Vercel Hobby; choose Cloudflare/Netlify paid tiers or other hosts[^10][^5][^16] |

Migration planning: Prefer designs that decouple data from platform-specific features. If switching hosts, retain the static site generator and index build pipeline to minimize rework.

---

## Recommendations and implementation plan

Primary recommendation: Use Cloudflare Pages for a static site with client-side, sharded search. This combination avoids per-request billing for static assets, leverages Cloudflare’s global edge, and provides room to evolve toward lightweight dynamic APIs if needed later[^6][^8][^5].

Fallbacks:
- Vercel Hobby for personal, non-commercial projects that benefit from its developer tooling and preview workflow; monitor data-transfer and function quotas[^10][^11].
- Netlify Starter if verified quotas and metering align with your traffic profile and you value Netlify’s build/deploy features; confirm exact free-tier values on the official pricing page[^16][^18].
- GitHub Pages for minimal static hosting needs where total output remains under 1 GB and monthly bandwidth stays comfortably under 100 GB[^1].

Implementation blueprint:
1. Prebuild the dataset into compressed shards (e.g., 26 alphabetical shards), each within Cloudflare’s 25 MiB per-file limit, and generate a minimal index per shard[^6].
2. Ship a compact client-side index and lazy-load shards based on user input; use Web Workers to keep the UI responsive[^14].
3. Aggressively cache all static assets with immutable, hashed filenames; minimize cache misses by bundling intelligently.
4. Instrument usage: track pageviews, shard access patterns, and initial load times. On Cloudflare, monitor Workers requests/day and CPU-time; on Vercel/Netlify, monitor bandwidth and function invocations[^5][^11][^16].
5. Add a minimal edge API only when client-side limits are reached (e.g., for advanced filters or fuzzy matching). Start with a small KV-backed index, respecting daily quotas[^5].
6. Establish guardrails: set alerts for bandwidth and function usage, and design a migration pathway to paid tiers if growth accelerates.

Documentation and verification plan:
- Before finalizing architecture, confirm Cloudflare’s “static requests free and unlimited” scope for Pages Functions and the latest Pages limits[^8][^6].
- Validate Netlify Starter’s 100 GB bandwidth and 300 build minutes figures and any function invocation caps on the official pricing and docs pages; document overage behavior[^16][^17][^18].
- Cross-check Vercel Hobby’s “build execution minutes” against the Limits page and clarify any variance in quotas across plan pages[^10][^11].
- Re-verify GitHub Pages site-count rules for user/org sites in the latest docs[^1].

---

## Appendix: Source notes and verification flags

The following matrix lists which assertions were validated by official documentation, which rely on third-party sources, and which remain to be confirmed.

Table 5 — Verification matrix
| Platform | Assertion | Source(s) | Status | Follow-up action |
|---|---|---|---|---|
| GitHub Pages | 100 GB/month soft bandwidth; published site ≤1 GB; 10 builds/hour soft; 10-minute timeout | [^1] | Official | Confirm site-count rules for user/org on latest docs |
| Cloudflare Pages | 20,000 files/site; 25 MiB/file; 500 builds/month; 20-minute build timeout; 100 custom domains/project | [^6] | Official | None |
| Cloudflare Workers/Functions | Requests to static assets free/unlimited; Workers Free: 100k requests/day and 10 ms CPU/invocation | [^5][^8] | Official | None |
| Cloudflare SSL | Free SSL via Free plan | [^19] | Official | None |
| Netlify | Free plan includes 100 GB bandwidth and 300 build minutes | [^16][^17] | Third-party/blog; extraction issue | Confirm on Netlify pricing/limits; document exact invocations |
| Netlify | Overages do not shut off site; metered services auto-billed/soft-throttled | [^18] | Official forum | Validate current behavior against billing docs |
| Vercel (Hobby) | Non-commercial use; 100 deployments/day; 45 min build time; 100 build hours; 100 GB fast data transfer; 10 GB fast origin transfer; 1-hour runtime logs; 23 GB disk; 50 domains/project | [^10][^11] | Official | Cross-check “build execution minutes” variance if any |
| Vercel Functions | Max duration configurable; 250 MB uncompressed function size | [^13] | Official | None |
| Vercel Pricing | Billable metrics and pricing model | [^12] | Official | None |

---

## References

[^1]: GitHub Pages limits — https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits  
[^2]: GitHub Pricing — https://github.com/pricing  
[^3]: GitHub Pricing Calculator — https://github.com/pricing/calculator  
[^4]: GitHub Plans for every developer — https://docs.github.com/en/get-started/learning-about-github/githubs-plans  
[^5]: Workers & Pages Pricing (Workers Free plan, daily limits) — https://developers.cloudflare.com/workers/platform/pricing/  
[^6]: Cloudflare Pages Limits — https://developers.cloudflare.com/pages/platform/limits/  
[^7]: Workers & Pages Pricing | Cloudflare — https://www.cloudflare.com/plans/developer-platform/  
[^8]: Pages Functions Pricing (static requests are free and unlimited) — https://developers.cloudflare.com/pages/functions/pricing/  
[^9]: Cloudflare Pages Pricing — https://pages.cloudflare.com/#pricing  
[^10]: Vercel Hobby Plan — https://vercel.com/docs/plans/hobby  
[^11]: Vercel Limits — https://vercel.com/docs/limits  
[^12]: Pricing on Vercel — https://vercel.com/docs/pricing  
[^13]: Vercel Functions Limitations (max duration, bundle size) — https://vercel.com/docs/functions/limitations  
[^14]: Lunr.js Pre-building Indexes (client-side search index guidance) — https://lunrjs.com/guides/index_prebuilding.html  
[^15]: Elasticlunr.js Documentation — http://elasticlunr.com/docs/  
[^16]: Netlify Pricing (verification flag due to extraction issues) — https://www.netlify.com/pricing/  
[^17]: Introducing Netlify’s Free plan (verification flag) — https://www.netlify.com/blog/introducing-netlify-free-plan/  
[^18]: Netlify Answers: Free plan overage behavior — https://answers.netlify.com/t/what-happens-if-a-free-plan-exceeds-bandwidth-and-or-build-minutes-limit/16244  
[^19]: Cloudflare Free Plan Overview (SSL included) — https://www.cloudflare.com/plans/free/