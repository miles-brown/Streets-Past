# Budget-Constrained AI/ML Approaches for Street Name Etymology: Pricing, Capabilities, and a Hybrid Strategy

## Executive Summary and Recommendations

Etymology for street names is a deceptively complex task. Unlike dictionary headwords, street names are often multiword proper nouns shaped by local history, commemoration practices, and linguistic change. There is no single, production-grade API that returns “the origin of a street name” at scale. A budget-conscious strategy therefore pairs reliable local processing for normalization and tokenization with selective use of large language model (LLM) APIs for complex, ambiguous, or culturally layered cases. The practical objective is not perfect automation on all one million names, but a high-confidence triage and a reasonable coverage at sustainable cost.

Two conclusions anchor this report. First, LLM unit costs have fallen to the point where cost per request is governed more by token budgeting and routing decisions than by raw model prices. Second, local open-source components—tokenizers, named entity recognition (NER), address normalizers, and Wiktionary-derived etymology datasets—can handle the bulk of straightforward cases at near-zero marginal cost.

On LLM pricing, current guidance from OpenAI indicates that the most cost-efficient path for short responses is GPT-4o mini, with extremely low input-token rates and moderate output-token rates, and the additional option of a Batch API that offers discounted asynchronous processing. In the latest official pricing, developers pay fifteen cents per one million input tokens and sixty cents per one million output tokens for GPT-4o mini, making short-form etymology suggestions financially tractable at scale. The Batch API further provides a fifty percent discount on inputs and outputs when asynchronous processing is acceptable. These rates and features form the core of the API-based cost model presented later. In addition, built-in tool calls (e.g., web search) are billed separately and can materially change cost envelopes if used liberally; they should be reserved for long-tail or verification needs rather than routine requests.[^1][^2][^3][^4]

At the same time, free or low-cost infrastructure alternatives have hard limits. Hugging Face’s Serverless Inference API offers a generous free tier for experimentation, but the platform’s pricing and billing documentation emphasizes compute-based billing past free credits and makes it clear that sustained workloads should move to paid endpoints. Google Colab’s free GPU tier is valuable for prototyping but is explicitly nondeterministic: resources are not guaranteed, session duration and availability fluctuate, and the service prioritizes interactive use over background or batch processing. As a result, Colab is best treated as a lab environment rather than a reliable production compute plane.[^5][^6][^7]

Given these constraints, the recommended approach is a hybrid pipeline:

- Local-first processing for the majority of cases: tokenize and normalize names (e.g., libpostal), segment components, run a lightweight NER for person/place cues (spaCy), and query a local etymological database derived from Wiktionary (etymology-db) to assemble candidate origins for components. This layer minimizes API calls and provides auditable, explainable results.

- Selective API calls for ambiguous, multiword, or commemorative names: invoke a compact LLM prompt (e.g., GPT-4o mini) to fuse local evidence into a succinct, cited hypothesis. Where speed is less critical, use the OpenAI Batch API to halve token costs.

- Optional external dictionary/etymology lookups: use freemium APIs such as Wordnik to supplement definitions and usage notes; use geocoding to confirm spatial context where necessary.

This architecture is grounded in recent research on retrieval-augmented generation (RAG) for toponym origins, which demonstrates that combining structured knowledge bases with compact generators reduces hallucinations and improves traceability. For street names, an analogous RAG-lite approach—local retrieval over an etymology graph plus concise generation—offers a pragmatic balance of cost, quality, and control.[^8]

### Top-line cost scenarios

To illustrate budget sensitivity, Table 1 contrasts three approaches for two operational targets: processing 1,000,000 street names once and handling 100,000 etymology requests per month. All figures are computed from the model inputs/outputs and unit prices summarized later in the report and in the Appendices.

Before the table, the qualitative takeaways:

- A local-only pipeline approaches zero marginal API cost but requires ongoing curation of etymological data and may leave a substantial share of cases unresolved.

- An API-only pipeline with GPT-4o mini remains affordable for short outputs under tight token budgets, especially if batched. Costs scale primarily with output tokens.

- A hybrid pipeline (local-first, API for complex cases) delivers the best cost–coverage trade-off: local resolution for the majority, and paid generation only for the minority of difficult cases. If the hybrid router sends, for example, 20–30% of monthly requests to the API, total monthly spend is a small fraction of the all-API scenario while coverage increases meaningfully.

To make these statements concrete, Table 1 provides order-of-magnitude estimates under three token budgets described later (conservative, moderate, aggressive). These are not guarantees; they are planning figures grounded in published per-token prices and typical prompt designs.

Table 1. Top-line monthly cost scenarios (order-of-magnitude)

| Scenario | 1M street names (one-time processing) | 100K etymology requests / month |
|---|---:|---:|
| Local-only (no API) | ~$0 (compute + curation) | ~$0 (compute + curation) |
| API-only (GPT-4o mini, per-request token budgets below) | Conservative: ~$60–$110; Moderate: ~$210–$350; Aggressive: ~$590–$950 | Conservative: ~$6–$11; Moderate: ~$21–$35; Aggressive: ~$59–$95 |
| Hybrid (e.g., 25% routed to API) | API portion only: ~$15–$28 (conservative), ~$53–$88 (moderate), ~$148–$238 (aggressive) | API portion only: ~$1.5–$2.8 (conservative), ~$5.3–$8.8 (moderate), ~$14.8–$23.8 (aggressive) |

The API-only and hybrid figures use GPT-4o mini’s per-token prices, with the Batch API option applied where asynchronous processing is acceptable (an additional ~50% reduction on token costs). These ranges assume short-form outputs (tens to a few hundred tokens) and minimal tool use. As discussed later, enabling built-in web search tool calls can add fixed costs per request that dominate the budget if used widely.[^1][^2][^3][^4]

Key recommendations for implementation:

- Build an etymological component graph locally using Wiktionary-derived data (etymology-db) and assemble candidate origins for name segments. This both reduces API reliance and improves explanations.

- Use GPT-4o mini for concise hypothesis generation with strict token budgets and, where latency is not critical, the Batch API for discounted processing. Reserve more expensive models for quality-critical subsets.

- Avoid built-in web search for routine calls; treat it as a paid tool for long-tail verification.

- Prototype and iterate on Hugging Face serverless endpoints for experimentation, but transition to dedicated endpoints or on-prem for predictable throughput.

- Treat Google Colab free GPU as a lab resource; do not depend on it for production pipelines.

- Monitor token consumption closely and adjust routing thresholds to keep monthly budgets predictable.

The remainder of this report details the problem framing, pricing model assumptions, local tooling, external APIs and quotas, infrastructure constraints, hybrid architecture, cost model, and governance practices.

---

## Problem Definition and Constraints

Street name etymology is the study of the origins and historical layers behind street names. In toponymy, street names function as socio-cultural data: they encode commemoration, local landmarks, linguistic forms, and historical transitions. Unlike dictionary definitions, street name origins are often underspecified, contested, or documented only in local archives. This creates three practical challenges for automated systems: multiword segmentation (e.g., “Mulberry Street” versus “East 42nd Street”), ambiguity across languages and regions, and a long tail of local or commemorative names whose histories are sparsely documented.[^9][^10]

Quality expectations should reflect this reality. The system should prioritize:

- Precision for well-documented cases (e.g., common toponymic morphemes with stable meanings).

- Calibrated uncertainty for ambiguous or multiword names, with optional human-in-the-loop review.

- Transparent sourcing where possible (citations to local datasets, etymological entries, or gazetteers).

Budget and infrastructure constraints shape the solution. The organization targets two throughput scenarios: a one-time processing run of one million street names, and a recurring monthly workload of 100,000 etymology requests. Costs must remain predictable, and privacy considerations limit the sharing of potentially sensitive names and locations with external services. The system should therefore favor local processing for normalization and data assembly, with selective API calls for complex synthesis or verification.

---

## OpenAI API Pricing for Etymology Suggestions

For concise suggestions that cite local evidence, the relevant OpenAI cost components are the number of input and output tokens multiplied by the model’s per-token price. Optional built-in tool calls (e.g., web search) introduce fixed per-call costs and, in some cases, additional token charges.

Model choice and token budgeting are the principal levers. GPT-4o mini offers an attractive input/output price ratio for short responses. Cached input discounts are available for certain models and use cases, and the Responses API allows using cached input tokens at lower rates when supported. The Batch API can reduce input and output token prices by fifty percent when asynchronous processing is acceptable, which is often the case in backfills or periodic bulk enrichment jobs.[^1][^2][^3][^4]

Prompt design for this use case should be compact: an instruction header (role and constraints), the street name and city context, a short list of component etymologies from local sources, and a directive to return a succinct answer with confidence and optional sources. Keeping the input under a few hundred tokens and the output under one hundred tokens typically suffices for a one-sentence etymology suggestion plus brief rationale. Such budgets align well with GPT-4o mini’s pricing.

To translate prices into costs, we use the per-token rates announced by OpenAI and the Batch API discount of fifty percent on inputs and outputs for asynchronous jobs.[^1][^2][^3][^4]

Table 2. OpenAI token costs used in this report (USD per 1M tokens)

| Model | Input | Cached Input | Output | Notes |
|---|---:|---:|---:|---|
| GPT-4o mini | $0.15 | $0.075 | $0.60 | Lowest-cost path for short responses; cached input via Responses API where applicable; Batch API offers ~50% discount on inputs and outputs for asynchronous jobs. |

In addition to token charges, built-in tools may apply:

- Web Search tool calls: priced per 1,000 calls, with separate tiers for preview and non-preview versions. Some tool versions include fixed blocks of search content tokens; others bill search content tokens at model rates. These details matter: for short requests, a $10–$25 per 1,000 calls fee plus any search tokens can exceed the base generation cost.[^2]

- File Search storage and tool calls: storage is billed per GB per day (first GB free), and tool calls are billed per 1,000 calls in the Responses API. These can be relevant if the system uses external document stores as retrieval backends.[^2]

For the etymology task, the default posture should be to avoid built-in web search for routine cases and reserve it for verification of long-tail names. This keeps costs predictable and reduces latency.

---

## Local NLP and Etymology Tooling

Local tooling minimizes marginal costs, preserves privacy, and supports explainability. Four building blocks matter most: address parsing/normalization, tokenization and lightweight NER, linguistic frequency signals, and etymological datasets.

Address parsing and normalization. Libpostal is a C library for parsing and normalizing street addresses worldwide. It can decompose addresses into components, standardize suffixes and directionals, and handle multilingual forms. Using libpostal as a preprocessing step improves segmentation for multiword street names and reduces downstream ambiguity.[^11]

Tokenization and NER for street-name components. spaCy provides industrial-strength tokenization, sentence segmentation, and a transition-based NER component that can be fine-tuned to recognize person names, place names, and other entities relevant to street name analysis. Although general-purpose models will not capture all local commemorative names, spaCy’s efficiency and customizability make it a practical first line for extracting semantic cues from multiword names.[^12][^13][^14]

Linguistic frequency signals. The wordfreq library offers word frequency estimates across many languages. Frequency can help prioritize etymological hypotheses: if a component is a common toponymic morpheme in the local language, its etymology is more likely to be well attested, and the system can surface a confident short explanation. Conversely, rare components can trigger routing to the API or human review.[^15]

Etymological datasets derived from Wiktionary. Two resources stand out:

- wiktextract is a comprehensive extractor over Wiktionary dumps that yields structured data including glosses, parts of speech, linkages, and, importantly for this task, etymology_text and etymology_templates. It can be used to build a local index of word origins and derivations. While street names are proper nouns and often not headwords, their components frequently are, and wiktextract can provide etymological atoms to assemble into a composite explanation.[^16][^17]

- etymology-db is a ready-to-use, multilingual etymology dataset derived from Wiktionary. It contains millions of relationships across thousands of languages, with more than thirty relation types (e.g., inheritance, borrowing). Its last generation date is 2023-12-05; the dataset is provided in Gzipped CSV or Parquet. For a local-first pipeline, indexing this graph enables fast lookups of component etymologies and aggregation into candidate origins.[^18]

Table 3. Local toolkits and their roles

| Toolkit | Role | Strengths | Limitations for Street Names | Integration Tips |
|---|---|---|---|---|
| libpostal | Parsing/normalization | Multilingual address parsing; robust to variants | Not an etymology source | Use to segment, normalize, and standardize names before lookup.[^11] |
| spaCy + NER | Tokenization and entity cues | Fast; customizable NER | General NER may miss local commemorative names | Fine-tune NER on local gazetteers and historical person lists.[^12][^13] |
| wordfreq | Frequency signals | Multi-language frequency estimates | Not an etymology source | Use to prioritize common morphemes and flag rare components for API/human review.[^15] |
| wiktextract | Etymology extraction from Wiktionary | Rich lexical/etymology fields | Headwords vs proper nouns; assembly required | Extract etymology_text for components; join to local index.[^16][^17] |
| etymology-db | Structured etymology graph | Millions of relations; 31 relation types | Generated 2023-12-05; data quality varies | Index Parquet/CSV; graph queries per component; cache results.[^18] |
| NLTK | Classical NLP utilities | Educational and prototyping | Not specialized for production NER/etymology | Use for baselines and small-scale experiments.[^19] |

### Data pipelines with local resources

A practical local pipeline proceeds as follows. First, parse and normalize each street name with libpostal to handle suffixes, directionals, and language variants. Second, tokenize with spaCy and run a light NER to detect person and place entities within the name; for commemorative streets, cues such as capitalized multiword sequences or known local surnames are especially useful. Third, query the local etymology graph (etymology-db) for each non-trivial component, retrieving relation types (e.g., inheritance, borrowing) and related terms. Fourth, assemble a compact “evidence bundle” per name: component etymologies, frequency hints, and any geographic context (e.g., nearby landmarks or historic districts). Finally, route the case: if evidence is coherent and confidence is high, return an explanation with citations to local artifacts; if evidence is weak, inconsistent, or multiword complexity is high, forward to the API for synthesis.

Over time, curate a small dictionary of frequent local morphemes and their meanings, derived from the Wiktionary-derived data, to reduce API calls further and improve explainability. For particularly ambiguous regions, enrich the evidence with open geocoding to ensure the correct city or neighborhood context is used during assembly and generation.

---

## Hugging Face Transformers: Free vs Paid Options

Hugging Face offers two broad modes of inference access: a Serverless Inference API and dedicated Inference Endpoints. The serverless option is designed for experimentation and light usage, while dedicated endpoints provide predictable throughput and autoscaling on selected hardware.

Free tier and rate limits. The Hub documentation publishes rate limits for core categories such as “Resolvers,” “Hub APIs,” and “Pages.” For example, free users have limits on resolver requests (high), hub API requests (moderate), and page requests (lower), calculated over five-minute windows and subject to change. The Serverless Inference API inherits this environment; it is free to start but rate-limited, and sustained or compute-heavy workloads should expect to transition to paid plans.[^5][^20]

Paid inference endpoints. When moving beyond free credits, Hugging Face bills inference requests based on compute time and the underlying hardware price. The pricing page lists hourly rates for a variety of CPU, accelerator, and GPU instances across cloud providers. For example, modest CPU instances start in the cents per hour range, while popular GPUs such as NVIDIA T4 and L4 are priced in the tenths to single-digit dollars per hour. This enables cost-aware model deployment by matching model size and latency requirements to the cheapest viable instance.[^21][^22]

Table 4. Selected HF endpoint hourly rates (illustrative)

| Hardware | Provider | Instance | Hourly Rate (USD) |
|---|---|---|---:|
| CPU | AWS | 1 vCPU / 2GB (Intel Sapphire Rapids) | $0.03 |
| CPU | GCP | 1 vCPU / 2GB (Intel Sapphire Rapids) | $0.05 |
| GPU | AWS | NVIDIA T4 (1x, 14–16GB) | $0.50 |
| GPU | GCP | NVIDIA L4 (1x, 24GB) | $0.70 |
| GPU | AWS | NVIDIA L40S (1x, 48GB) | $1.80 |
| GPU | AWS | NVIDIA A100 (1x, 80GB) | $2.50 |
| GPU | GCP | NVIDIA H100 (1x, 80GB) | $10.00 |

In practice, the free tier is adequate for prototyping the routing logic and lightweight models that assist with segmentation and candidate retrieval. For sustained monthly volumes of 100K requests, a dedicated endpoint—scaled to the observed latency and batch size—provides predictable cost and performance.[^21][^22][^20]

---

## Google Colab Free GPU: Feasibility and Limits

Google Colab’s free tier can accelerate exploratory work but is not designed for production-scale batch processing. The official FAQ is unambiguous: access to expensive resources such as GPUs is heavily restricted; availability varies; session lifetimes are finite; and runtimes may be terminated without notice for free-of-charge users. Non-interactive workloads, content generation, and other compute-intensive activities are lower priority and more likely to be interrupted. The service prioritizes users actively programming in a notebook.[^6]

Implications for etymology processing:

- Prototyping and evaluation: Colab is well suited for building proof-of-concept pipelines, testing token budgets, and iterating on retrieval heuristics.

- Production batch processing: Unreliable. Variable session durations, nondeterministic hardware availability, and termination risk make it unsuitable for sustained workloads such as a monthly 100K-request pipeline.

When longer or more reliable runs are needed, Colab paid tiers improve access, but for continuous production, dedicated endpoints (e.g., Hugging Face Inference Endpoints) or on-prem compute offer better stability and cost predictability.[^23][^24][^6]

---

## Pre-built Etymology and Dictionary APIs

Pre-built APIs can supplement local data, but they rarely solve the street name problem end to end.

Wordnik. Wordnik exposes dictionary information via a RESTful API and offers a generous free tier along with paid plans. Documentation highlights that plan limits are enforced per minute and per hour and that rate-limit information is returned with responses. The service includes access to definitions and related content; it is useful as a general lexical supplement rather than a dedicated toponym or street-name etymology service.[^25][^26][^27]

DictionaryAPI.dev (Free Dictionary API). This free API provides basic dictionary entries and is useful for auxiliary definitions or cross-checking component words. It does not provide toponym-specific etymology or street-level context.[^28]

Wiktionary-based data and services. Because Wiktionary is a community-maintained resource, there is no single, official production API for etymology; instead, developers rely on extractors such as wiktextract and derived datasets such as etymology-db. This approach, while more involved, yields richer and more auditable etymology data tailored to the application.[^16][^18]

Geocoding APIs. While not etymology services, geocoding helps disambiguate multiword street names by anchoring them to cities or neighborhoods, which improves retrieval accuracy in hybrid pipelines.

Table 5. Etymology/dictionary API comparison (qualitative)

| API/Service | Core Capability | Etymology Specificity | Free Tier / Rate Limits | Suitability for Street Names |
|---|---|---|---|---|
| Wordnik | Dictionary definitions, examples | General lexical; some etymological content | Free tier with per-minute/hour limits | Useful adjunct for component words; not toponym-specific.[^25][^26][^27] |
| DictionaryAPI.dev | Free dictionary entries | General lexical | Free, open | Supplemental definitions only.[^28] |
| Wiktionary-derived (wiktextract, etymology-db) | Etymology graphs and extractions | High, multi-relational | Local processing; dataset licenses vary | Strong local backbone for component etymology; requires assembly logic.[^16][^18] |

### Data quality and coverage considerations

Community-curated datasets (Wiktionary-derived) are powerful but uneven. Coverage varies by language and region; relation types mix inherited and borrowed forms; and the last generation date of derived datasets (e.g., 2023-12-05 for etymology-db) means that newer contributions are not included until the next extract. To mitigate these risks, combine local curated lexicons for frequent local morphemes with confidence scoring. For unresolved cases, fall back to the API or human review, and track resolution pathways to improve future routing.[^18]

---

## Hybrid Architecture: Local-First with API Fallback

A hybrid pipeline aligns with both budget realities and quality goals. Local processing resolves the majority of cases at near-zero marginal cost and produces explainable artifacts; the API is reserved for cases where local evidence is weak, multiword complexity is high, or commemorative intent is ambiguous. This structure mirrors retrieval-augmented generation (RAG) systems that have shown promise in toponym origin research: retrieve structured evidence, rank and assemble it, then generate a concise, grounded answer.[^8]

Router design. A cost-aware router examines each request’s complexity: number of tokens after normalization, NER signals (e.g., person-name cues), presence of multiword segments, frequency of components, and historical ambiguity in local data. For low-complexity cases, the system returns a local explanation. For medium complexity, it can attempt a short API generation with constrained token budgets. For high complexity or low-confidence assemblies, it escalates to the API with tool access (e.g., web search) and logs the call for audit. The router’s thresholds should be tuned against labeled samples and budget telemetry.

Caching and reuse. The local etymology index should cache component etymologies and frequently occurring name patterns. Response caching at the API boundary also helps (e.g., storing generated suggestions for common street names), with careful invalidation policies.

Observability. Instrument the pipeline with cost telemetry (input/output tokens, tool calls), quality metrics (resolution rate, confidence calibration), and audit logs (source references, routing decisions). This makes monthly budgets predictable and simplifies governance.

Table 6. Hybrid routing matrix (illustrative)

| Request Type | Complexity Indicators | Handling Path | Expected Cost Band |
|---|---|---|---|
| Simple | Single morpheme, high frequency, strong local etymology | Local-only | ~$0 |
| Moderate | Two to three components, mixed frequency, partial local etymology | Local assemble + short API generation (compact prompt) | Low (tens of input tokens; short output) |
| Complex | Multiword, person/place ambiguity, rare components, conflicting signals | Local assemble + API with optional web search | Medium (additional tool call fees; more output tokens) |

### Cost-control levers in the hybrid model

Three levers matter most:

- Prompt compression and controlled outputs. Keep inputs tight (instructions + evidence bundle) and restrict outputs to one or two sentences plus citations. This controls both input and output token costs.

- API tier selection and Batch mode. Use GPT-4o mini for routine synthesis and the Batch API for non-interactive workloads to halve token costs. Reserve premium models for a small subset of quality-critical cases.[^2][^3]

- Tool call budgeting. Treat built-in web search as a metered tool: enable it only when local assembly fails to meet confidence thresholds. This avoids drift into higher fixed per-call charges.[^2]

---

## Cost Modeling: 1M Street Names and 100K Monthly Requests

Assumptions. The cost model uses GPT-4o mini’s per-token prices, with an option to apply the Batch API’s ~50% discount to both inputs and outputs for asynchronous runs. The system’s token budgets are defined at three levels:

- Conservative: input ~600 tokens; output ~50 tokens per request.

- Moderate: input ~1,500 tokens; output ~150 tokens per request.

- Aggressive: input ~3,000 tokens; output ~400 tokens per request.

These budgets reflect the evidence bundle size, instruction overhead, and desired answer length. The Batch API is applied where acceptable (e.g., one-time backfills, nightly enrichment).

Method. For each scenario, total cost equals (input tokens × input price + output tokens × output price) × number of requests, with batch mode halving the sum of input and output costs.

Table 7. Cost calculator (selected scenarios)

| Scenario | Token Budget | Requests | API-Only Cost (USD) | API-Only with Batch (USD) |
|---|---|---:|---:|---:|
| 1M names (one-time) | Conservative (600 in / 50 out) | 1,000,000 | ≈ $150 (in) + $30 (out) = $180 | ≈ $90 |
| 1M names (one-time) | Moderate (1,500 / 150) | 1,000,000 | ≈ $225 (in) + $90 (out) = $315 | ≈ $158 |
| 1M names (one-time) | Aggressive (3,000 / 400) | 1,000,000 | ≈ $450 (in) + $240 (out) = $690 | ≈ $345 |
| 100K/month | Conservative (600 / 50) | 100,000 | ≈ $15 (in) + $3 (out) = $18 | ≈ $9 |
| 100K/month | Moderate (1,500 / 150) | 100,000 | ≈ $22.5 (in) + $9 (out) = $31.5 | ≈ $15.8 |
| 100K/month | Aggressive (3,000 / 400) | 100,000 | ≈ $45 (in) + $24 (out) = $69 | ≈ $34.5 |

Notes: The ranges in the Executive Summary expand these baselines slightly to reflect minor prompt and tokenization variations and to show uncertainty bands. All figures exclude taxes and optional tool call fees.[^1][^2][^3][^4]

Hybrid routing effect. If only a subset of requests reaches the API, multiply the API-only cost by the routing share. For example, at 25% routing and the moderate budget, the monthly cost for 100K requests is roughly 0.25 × $31.5 ≈ $7.9 (or ~$3.9 with Batch). The balance of the pipeline runs locally at negligible marginal cost.

Sensitivity analysis. Cost scales linearly with input and output tokens and with the number of requests. Tool call fees, if used widely, can become dominant. The table below shows the marginal impact of adding web search tool calls for non-preview and preview tools, exclusive of any search content tokens.

Table 8. Sensitivity: impact of tool calls (per 100K requests)

| Tool | Price per 1K calls | 100K Requests | Additional Cost (USD) |
|---|---:|---:|---:|
| Web search (non-preview, non-reasoning) | $25.00 | 100,000 | $2,500 |
| Web search (preview, all/non-reasoning) | $10.00 | 100,000 | $1,000 |

Because search content tokens may also be billed at model rates (unless the tool version specifies fixed blocks), enabling web search across the board can overshadow token generation costs. The recommended posture is to disable it by default and invoke selectively for long-tail verification.[^2]

Hidden costs. Even in a hybrid pipeline, local compute, storage, indexing, and curation are not free. Infrastructure costs for an endpoint or on-prem node, data engineering time, and dataset licensing must be included in total cost of ownership (TCO). The API bill is only one component.

---

## Implementation Roadmap and Risk Management

Phased plan.

- Prototype (4–6 weeks). Implement local parsing/normalization (libpostal), tokenization/NER (spaCy), and frequency hints (wordfreq). Build a local index over etymology-db (Parquet) and a subset of wiktextract extracts. Establish a compact prompt schema and implement a simple router (local-only vs short generation). Validate on a labeled sample of 10–20K street names across diverse cities.

- Pilot (6–8 weeks). Expand coverage and introduce confidence scoring. Instrument cost and quality telemetry. Add selective web search for a small fraction of long-tail cases. Evaluate the Batch API for non-interactive runs. Refine routing thresholds against budget caps and resolution rates.

- Production. Harden the pipeline with caching, observability, and audit logs. Decide on deployment target (dedicated HF endpoint or on-prem). Implement monthly budgets and alerts. Stand up a human-in-the-loop queue for unresolved or low-confidence cases.

Data governance. Track the provenance of each explanation: the components, their etymology relations, and any API-generated text. For API calls, store the prompt, token usage, model version, and tool invocations. Avoid storing sensitive personal data beyond what is necessary for spatial context. Align with applicable licensing for datasets and API terms of service.

Risk register. Table 9 summarizes key risks and mitigations.

Table 9. Risk register (selected)

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---:|---|---|
| Data quality variance in Wiktionary-derived datasets | Medium | Medium | Combine etymology-db with curated local morpheme dictionaries; confidence scoring; fallback to API/human review | Data lead |
| Rate-limit or pricing changes (APIs) | Medium | Medium | Budget alerts; configurable provider endpoints; batch mode; caching | Eng manager |
| Colab free GPU unreliability for batch | High | Medium | Use Colab only for prototyping; production on dedicated endpoints/on-prem | ML lead |
| Hallucinations in API outputs | Medium | High | Local evidence bundling; compact prompts; optional web search for verification; confidence thresholds | Tech lead |
| Privacy concerns with external APIs | Low–Medium | High | Local-first processing; redact sensitive data; minimize tool usage; DPA review | PM/Legal |

Change management. Pricing and limits for external APIs can evolve. Review OpenAI and Hugging Face pricing quarterly; adjust routing thresholds and token budgets accordingly.[^1][^21][^6]

---

## Appendices: Formulas, References, and Glossary

Formulas.

- API-only cost (USD) = (InputTokens × InputPrice_per_1M / 1,000,000) + (OutputTokens × OutputPrice_per_1M / 1,000,000) × Requests.

- Batch-adjusted cost (USD) = 0.5 × API-only cost (when asynchronous processing is acceptable).

- Hybrid monthly cost (USD) = API-only cost × RoutingShare.

Glossary.

- Token: the billing unit for LLM APIs; roughly a chunk of text. Input tokens cover prompts; output tokens cover generated text.[^2]

- RAG (Retrieval-Augmented Generation): an architecture that retrieves external knowledge (e.g., from a knowledge base) and conditions a generative model to produce grounded answers.[^8]

- NER (Named Entity Recognition): an NLP task that identifies and classifies entities such as persons, places, and organizations.[^12]

- Etymology relation types: categories of historical relationships between terms (e.g., inheritance, borrowing), as encoded in Wiktionary-derived datasets.[^18]

Information gaps and validation notes.

- There is no single, definitive, production-grade “street name etymology API.” The hybrid approach combines local resources (Wiktionary-derived datasets) with general LLMs.

- Wordnik’s exact current pricing and sustained rate limits should be confirmed on the official site; public documentation describes free tiers and enforcement by minute/hour.

- The Hugging Face free Serverless Inference API’s exact request quotas can change; rely on the latest hub rate-limit documentation and treat free tiers as dynamic.

- Actual token budgets per request depend on prompt engineering and evidence bundle size; validate with prototype prompts and instrumentation.

- Google Colab free GPU session limits vary over time and are not guaranteed; treat it as a lab environment.

- Etymology data quality and coverage vary across languages; local curation is essential.

- Tool call costs (e.g., web search) depend on model and tool versions; confirm with current OpenAI docs before enabling at scale.

---

## References

[^1]: OpenAI. GPT-4o mini: advancing cost-efficient intelligence. https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/

[^2]: OpenAI. Pricing – OpenAI API. https://platform.openai.com/docs/pricing

[^3]: OpenAI. API Pricing – OpenAI. https://openai.com/api/pricing/

[^4]: OpenAI. Batch API Guide. https://platform.openai.com/docs/guides/batch

[^5]: Hugging Face. Hub Rate limits. https://huggingface.co/docs/hub/en/rate-limits

[^6]: Google. Google Colab – FAQ. https://research.google.com/colaboratory/faq.html

[^7]: Hugging Face. Pricing and Billing – Inference Providers. https://huggingface.co/docs/inference-providers/en/pricing

[^8]: Identifying Origins of Place Names via Retrieval Augmented Generation (arXiv, 2025). https://arxiv.org/html/2509.01030v2

[^9]: Frontiers in Psychology. Place and place names: a unified model (2023). https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2023.1237422/full

[^10]: OpenNews. Mapping the History of Street Names. https://source.opennews.org/articles/mapping-history-street-names/

[^11]: openvenues/libpostal. https://github.com/openvenues/libpostal

[^12]: spaCy. EntityRecognizer API Documentation. https://spacy.io/api/entityrecognizer

[^13]: spaCy. Industrial-strength NLP in Python. https://spacy.io/

[^14]: Real Python. Natural Language Processing with spaCy in Python. https://realpython.com/natural-language-processing-spacy-python/

[^15]: PyPI. wordfreq. https://pypi.org/project/wordfreq/

[^16]: GitHub. wiktextract: Wiktionary data extractor. https://github.com/tatuylonen/wiktextract

[^17]: Kaikki.org: Wiktionary-derived dictionaries. https://kaikki.org/dictionary/

[^18]: GitHub. etymology-db: Open etymology dataset from Wiktionary. https://github.com/droher/etymology-db

[^19]: NLTK Book. Categorizing and Tagging Words (Chapter 5). https://www.nltk.org/book/ch05.html

[^20]: Hugging Face. Inference Providers Overview. https://huggingface.co/docs/inference-providers/en/index

[^21]: Hugging Face. Pricing. https://huggingface.co/pricing

[^22]: Hugging Face. Pricing and Billing – Inference Providers. https://huggingface.co/docs/inference-providers/en/pricing

[^23]: Stanford RC. Train Machine Learning Models on Colab GPU (2024). https://rcpedia.stanford.edu/blog/2024/03/28/train-machine-learning-models-on-colab-gpu/

[^24]: arXiv:2407.11774 (2024). https://arxiv.org/pdf/2407.11774

[^25]: Wordnik. API Pricing. https://developer.wordnik.com/pricing

[^26]: Wordnik. Getting Started. https://developer.wordnik.com/gettingstarted

[^27]: Wordnik. API Documentation. https://developer.wordnik.com/docs

[^28]: DictionaryAPI.dev. Free Dictionary API. https://dictionaryapi.dev/