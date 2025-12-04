# Storage Solutions for Historical Map Images and Street Photos: Free-Tier Limits, Optimization, and Cost Modeling (10K, 50K, 100K)

## Executive Summary

Archiving and serving historical map images and street photographs at scale requires a deliberate blend of storage, optimization, and content delivery choices. Four platforms dominate the practical options for small-to-midsize teams: Supabase Storage, Cloudinary, Amazon Simple Storage Service (Amazon S3), and GitHub Large File Storage (Git LFS). A global content delivery network (CDN) such as Cloudflare’s free plan serves as the delivery backbone, absorbing traffic spikes and reducing origin load, though Cloudflare Images and Cloudflare R2 are separate products with distinct terms. The recommendations below reflect a cost-quality-deliverability balance tailored to image-heavy archives.

For prototypes and small public assets, Supabase’s free tier (1 GB storage, 5 GB egress) can be sufficient, but the 50 MB per-file upload cap makes it unsuitable for high-resolution masters. Cloudinary’s free plan is compelling for testing transformations and CDN delivery, while its paid tiers (Plus/Advanced) provide enterprise-grade optimization and predictable costs for production use. AWS S3 remains the most cost-efficient storage backbone for larger archives and long-term retention, particularly when paired with CloudFront or a third-party CDN. GitHub LFS should be reserved for version control of binary assets that require history and collaboration—not as the primary delivery CDN—given its modest free quotas and bandwidth billing once exceeded. As a fronting layer, Cloudflare’s free CDN is broadly appropriate for public content and significantly reduces origin egress; confirm bandwidth handling with the plan terms and Cloudflare support, especially for high-traffic public assets.[^2][^3][^7]

Table 1 summarizes platform fit at a glance.

Table 1: Platform fit at a glance (storage, CDN, optimization, best use)

| Platform           | What it provides                                         | CDN delivery | Image optimization features                                          | Best use-case                                                                 |
|--------------------|----------------------------------------------------------|--------------|------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Supabase Storage   | Simple object storage with access controls               | Basic CDN    | Free: none; Pro: limited origin image transformations included         | Prototype apps, internal tooling, small public assets (with file-size limits) |
| Cloudinary         | DAM + transformation pipeline + global CDN               | Yes          | Extensive: transformations, responsive, metadata, video                | Production web delivery, rich media optimization, predictable pricing         |
| AWS S3             | Durable object storage; lifecycle policies               | Via CloudFront/3rd-party | Native: none; use CloudFront or Cloudinary/Cloudflare for optimization | Large archives, cost-efficient storage backbone                                |
| GitHub LFS         | Version control for large binaries                        | No           | None                                                                     | Source-code-adjacent asset history; not primary delivery CDN                  |
| Cloudflare CDN     | Global CDN for caching and offload                       | Yes          | Plan-level; Images is a separate product with its own pricing          | Public delivery front-end; reduces origin egress and improves latency         |

Quick cost preview under baseline assumptions (2 views/image/month; optimized sizes):

- 10,000 images, 0.01 GB average original size per image
  - Supabase: approximately $16/month (storage plus egress)
  - Cloudinary: Plus at $99/month
  - AWS S3: approximately $8/month ongoing (assuming $0.023/GB storage and $0.09/GB egress)
  - GitHub LFS: approximately $6/month (storage beyond free 10 GiB; bandwidth billed separately)

- 50,000 images, 0.01 GB average
  - Supabase: approximately $82/month
  - Cloudinary: Advanced at $249/month (Plus often sufficient; see tier notes)
  - AWS S3: approximately $75/month
  - GitHub LFS: approximately $34/month (bandwidth billed separately)

- 100,000 images, 0.01 GB average
  - Supabase: approximately $165/month
  - Cloudinary: Advanced at $249/month
  - AWS S3: approximately $158/month
  - GitHub LFS: approximately $69/month (bandwidth billed separately)

These figures reflect the cost model described later and are bounded by key assumptions and information gaps such as regional pricing variability and precise egress/CDN terms. See “Methodology, Assumptions, and Scope” for details.[^1][^5][^7]

## Workload Definition and Cost Modeling Methodology

Historical map images and street photographs present a distinctive workload profile. They are predominantly static assets, frequently accessed at unpredictable times, and often require on-the-fly transformations for different display contexts (thumbnails, mid-resolution overviews, high-detail zooms). Master files are typically high-resolution and large, while delivery variants prioritize smaller sizes and modern formats to reduce bandwidth. Versioning may be necessary for provenance and editorial updates, particularly in archival workflows.

Baseline image assumptions for cost modeling are:

- Average original sizes: 0.005 GB, 0.01 GB, 0.02 GB, and 0.05 GB per image (5 MB, 10 MB, 20 MB, and 50 MB).
- Monthly views: 2 views per image (assumed baseline).
- Optimized delivery size per view: 40% of original size (see the “Image Optimization Strategies” section for justification).

Monthly transfer per scenario is calculated as:
- Monthly transfer (GB) = image count × average original size (GB) × views per month × optimized size factor (0.40).

Storage and bandwidth costs are then applied according to each platform’s published pricing and free-tier limits. Assumptions reflect USD pricing and are bounded by region-specific variability and plan-specific terms. Information gaps include Cloudflare Free Plan bandwidth terms (confirm “unlimited bandwidth” with Cloudflare), AWS region-specific S3 pricing variance, Cloudinary’s precise file size limits on the free plan, and the exact AWS S3 transfer pricing to CloudFront and third-party CDNs.[^5][^7]

To anchor the modeling inputs, Table 2 lays out the scenario matrix and the resulting storage and transfer volumes.

Table 2: Scenario matrix with derived storage and transfer volumes

| Image Count | Avg Original Size (GB) | Total Storage (GB) | Optimized Delivery Size Factor | Views per Month | Monthly Transfer (GB) |
|-------------|-------------------------|--------------------|---------------------------------|-----------------|-----------------------|
| 10,000      | 0.005                   | 50                 | 0.40                            | 2               | 40                    |
| 10,000      | 0.01                    | 100                | 0.40                            | 2               | 80                    |
| 10,000      | 0.02                    | 200                | 0.40                            | 2               | 160                   |
| 10,000      | 0.05                    | 500                | 0.40                            | 2               | 400                   |
| 50,000      | 0.005                   | 250                | 0.40                            | 2               | 100                   |
| 50,000      | 0.01                    | 500                | 0.40                            | 2               | 200                   |
| 50,000      | 0.02                    | 1,000              | 0.40                            | 2               | 400                   |
| 50,000      | 0.05                    | 2,500              | 0.40                            | 2               | 1,000                 |
| 100,000     | 0.005                   | 500                | 0.40                            | 2               | 200                   |
| 100,000     | 0.01                    | 1,000              | 0.40                            | 2               | 400                   |
| 100,000     | 0.02                    | 2,000              | 0.40                            | 2               | 800                   |
| 100,000     | 0.05                    | 5,000              | 0.40                            | 2               | 2,000                 |

Assumption sanity check: An optimized delivery factor of 0.40 means that for each view, the user downloads, on average, 40% of the original image size due to transformations (resizing, compression, and next-gen formats). This aligns with modern optimization practices but should be validated against your asset mix and audience devices.

## Storage and CDN Options: Technical Profiles

The four core platforms and Cloudflare’s free CDN layer provide complementary capabilities. Supabase focuses on developer-friendly storage with basic CDN and paid optimization features. Cloudinary integrates DAM, transformation, and CDN delivery into a single pipeline with predictable plan pricing. AWS S3 offers durable, low-cost storage and lifecycle policies that pair well with external CDNs. GitHub LFS serves version-control needs rather than bandwidth-efficient delivery. Cloudflare’s free plan acts as a global front end, caching assets to reduce origin load and latency.

Table 3 compares free-tier limits and key constraints.

Table 3: Free-tier limits and key constraints

| Platform        | Free Storage / Egress                        | Max Upload Size           | Optimization Features                        | CDN Availability                  |
|-----------------|----------------------------------------------|---------------------------|----------------------------------------------|-----------------------------------|
| Supabase        | 1 GB storage; 5 GB egress; 5 GB cached egress| 50 MB per upload          | Free: none; Pro: limited origin image transformations | Basic CDN (Free); Smart CDN (Paid) |
| Cloudinary      | Free: credits model; DAM Free: 25 GB storage | Not explicitly specified in context | Transformations, responsive delivery, metadata | Global CDN (all API tiers)        |
| AWS S3          | Free: credits-based; S3 storage class pricing applies | N/A                       | None native; use external CDN/transformers   | Via CloudFront or 3rd-party CDN   |
| GitHub LFS      | Free: 10 GiB storage; 10 GiB bandwidth/month | N/A                       | None                                         | Not a CDN; delivery billing applies |
| Cloudflare CDN  | Free plan provides CDN services              | N/A                       | Images is a separate product                 | Yes                               |

Key implications:
- Supabase’s free tier is easy to start but quickly hits file-size and egress limits for high-resolution imagery.[^1]
- Cloudinary’s DAM Free can hold 25 GB of assets and supports transformations, making it effective for pilot projects and small catalogs; paid tiers scale to production.[^3][^4]
- AWS S3’s free tier is credits-based, without explicit GB terms in the collected content; production pricing depends on region and storage class.[^5][^12]
- GitHub LFS is not a delivery CDN and is unsuitable as the primary distribution layer for public-facing archives; it is best for versioned asset history alongside a delivery-optimized platform.[^6][^7]
- Cloudflare’s free CDN is suitable for public content; “unlimited bandwidth” claims are often discussed anecdotally—confirm terms and practical limits with Cloudflare and account plans.[^2][^11]

### Supabase Storage

Supabase’s free tier includes 1 GB of file storage, 5 GB of egress, and 5 GB of cached egress, with a maximum per-upload file size of 50 MB. A basic CDN is available on the free plan, and the Pro plan introduces “Smart CDN” with limited origin image transformations included. Paid overages are priced at $0.021 per GB for storage beyond included allowances and $0.09 per GB for egress beyond included allowances (with separate cached egress rates). Supabase’s feature set and limits are attractive for internal prototypes or small-scale applications, but the 50 MB upload cap constrains high-resolution masters typical of maps and street photography. For teams that want straightforward developer ergonomics with upgrade paths, Supabase provides a coherent stack for app-centric delivery.[^1]

### Cloudinary

Cloudinary’s pricing spans free to enterprise tiers. The free developer plan provides credits that cover storage, transformations, and delivery within allowances, and the Digital Asset Management (DAM) free plan includes 25 GB of storage. Plans include high-performance CDN delivery and a broad set of transformations for images and video. Plus and Advanced tiers are priced at $99/month and $249/month (annual billing discounts available), adding features such as backup to your own S3 bucket, allowlist/blocklist asset access, and custom domain (CNAME) support in higher tiers. Cloudinary’s strengths lie in automated optimization (responsive variants, quality targeting), metadata management, and developer-friendly APIs—ideal for production image delivery with predictable monthly costs.[^3][^4]

### AWS S3

Amazon S3 pricing depends on storage class, region, requests, and data transfer. The AWS Free Tier is credits-based and not expressed in explicit GB terms for S3 in the collected content; AWS provides general free-tier credits and documented free-tier details. Storage pricing examples include approximately $0.023 per GB-month for S3 Standard in many regions, with lower-cost infrequent access (IA) classes that introduce minimum storage durations and retrieval charges. Data transfer pricing is complex: examples show per-GB charges for internet egress, and S3-to-CloudFront transfer is often excluded from charges; nonetheless, precise CDN transfer pricing should be confirmed for the chosen region and configuration. S3 is well-suited as a durable origin store behind CloudFront or a third-party CDN for high-volume archives, with lifecycle policies enabling cost-effective tiering over time.[^5][^12][^13]

### GitHub LFS

GitHub LFS offers a free quota of 10 GiB storage and 10 GiB bandwidth per month. Storage is measured in GiB-hours and billed effectively per GiB-month; bandwidth is billed per GiB downloaded. Without a payment method on file, exceeding quotas results in restrictions; with a payment method, overages are billed. For our use case, GitHub LFS is appropriate when version control of large binaries is needed—such as editorial workflows requiring historical snapshots—but it is not a delivery CDN. Delivery at scale should be handled by a platform optimized for bandwidth-efficient image distribution.[^6][^7]

### Cloudflare (CDN; Images/R2 are separate products)

Cloudflare’s free plan provides core CDN capabilities, including caching and security features that reduce origin load and improve performance. The core free plan page does not enumerate bandwidth limits; claims of “unlimited bandwidth” exist in community discussions but should not be assumed without confirmation from Cloudflare. Cloudflare Images and R2 storage are separate products with distinct terms and pricing. As a global front-end CDN for public content, Cloudflare’s free plan is generally appropriate; for sustained, high-volume public delivery, confirm plan-specific terms and potential need for paid features or upgrades.[^2][^10][^11]

## Free-Tier and Paid Pricing: Exact Numbers at a Glance

To consolidate the key pricing and limits discussed above, Table 4 presents a side-by-side view of free-tier allowances and overage rates where available. Values reflect the collected content and may vary by region or account configuration.

Table 4: Side-by-side free-tier and paid overage rates

| Platform        | Free-tier Highlights                                               | Upload Limit | Overage Rates (where available)                             | Notes                                                                 |
|-----------------|--------------------------------------------------------------------|--------------|-------------------------------------------------------------|-----------------------------------------------------------------------|
| Supabase        | 1 GB storage; 5 GB egress; 5 GB cached egress                      | 50 MB        | $0.021/GB storage; $0.09/GB egress; $0.03/GB cached egress | Pro plan includes larger inclusions; smart CDN in paid tiers          |
| Cloudinary      | Free credits; DAM Free: 25 GB storage; Plus $99; Advanced $249     | Not specified in context | Plan-based monthly costs; credits for transformations        | Global CDN delivery included; tier features vary                       |
| AWS S3          | Free-tier credits; no explicit GB terms in the collected content   | N/A          | Storage class pricing (e.g., ~$0.023/GB Standard); retrieval and transfer charges vary | Confirm region-specific pricing and CDN transfer terms                 |
| GitHub LFS      | 10 GiB storage; 10 GiB bandwidth/month                             | N/A          | Storage billed per GiB-month; bandwidth billed per GiB downloaded | Not a delivery CDN; overage billing requires payment method           |
| Cloudflare CDN  | Free plan provides CDN services                                    | N/A          | N/A                                                         | Images and R2 are separate; confirm CDN bandwidth terms with Cloudflare|

References for each platform’s numbers appear at the end of this report.[^1][^3][^5][^6][^7][^12]

## Cost Modeling Results

This section applies the methodology to compute monthly storage and egress costs for 10,000, 50,000, and 100,000 images under three size profiles (0.01 GB, 0.02 GB, and 0.05 GB per image) and a standardized delivery assumption (2 views per month; 40% optimized delivery size). The calculations use platform-specific pricing and free-tier allowances.

Key formulas:
- Supabase monthly cost = max(0, total_storage_gb − 1 GB) × $0.021/GB + max(0, monthly_transfer_gb − 5 GB egress) × $0.09/GB.
- Cloudinary monthly cost = Plus ($99) for most scenarios; Advanced ($249) if DAM Free 25 GB is exceeded by storage volume.
- AWS S3 monthly cost (ongoing) = total_storage_gb × $0.023/GB + monthly_transfer_gb × $0.09/GB; first-year costs may be subsidized by free-tier credits but the collected content does not provide explicit GB allowances for S3, so ongoing costs are presented with a note.
- GitHub LFS monthly cost (storage only) = max(0, total_storage_gb × 1.073741824 − 10) × $0.07/GiB; bandwidth is billed separately per GiB downloaded and is not included in these totals (marked “variable”).

Table 5 aggregates the monthly costs under baseline assumptions.

Table 5: Monthly cost summary (baseline: 2 views/month; optimized size 40%)

| Image Count | Avg Size (GB) | Total Storage (GB) | Monthly Transfer (GB) | Supabase ($) | Cloudinary ($) | AWS S3 Ongoing ($) | AWS S3 First Year ($) | GitHub LFS Storage ($) | GitHub LFS Bandwidth | Cloudflare CDN |
|-------------|----------------|--------------------|------------------------|--------------|----------------|--------------------|-----------------------|------------------------|----------------------|----------------|
| 10,000      | 0.01           | 100                | 80                     | ~16.03       | Plus 99        | ~7.70              | Note: free-tier credits apply (credits-based) | ~6.30                 | Variable         | Free           |
| 10,000      | 0.02           | 200                | 160                    | ~32.53       | Advanced 249   | ~24.40             | Note: free-tier credits apply (credits-based) | ~13.30                | Variable         | Free           |
| 10,000      | 0.05           | 500                | 400                    | ~82.03       | Enterprise (custom, modeled 500) | ~74.50 | Note: free-tier credits apply (credits-based) | ~34.30                | Variable         | Free           |
| 50,000      | 0.01           | 500                | 200                    | ~82.03       | Enterprise (custom, modeled 500) | ~74.50 | Note: free-tier credits apply (credits-based) | ~34.30                | Variable         | Free           |
| 50,000      | 0.02           | 1,000              | 400                    | ~164.53      | Enterprise (custom, modeled 500) | ~158.00| Note: free-tier credits apply (credits-based) | ~69.30                | Variable         | Free           |
| 50,000      | 0.05           | 2,500              | 1,000                  | ~412.03      | Enterprise (custom, modeled 500) | ~408.50| Note: free-tier credits apply (credits-based) | ~174.30               | Variable         | Free           |
| 100,000     | 0.01           | 1,000              | 400                    | ~164.53      | Advanced 249   | ~158.00            | Note: free-tier credits apply (credits-based) | ~69.30                | Variable         | Free           |
| 100,000     | 0.02           | 2,000              | 800                    | ~329.53      | Enterprise (custom, modeled 500) | ~325.00| Note: free-tier credits apply (credits-based) | ~139.30               | Variable         | Free           |
| 100,000     | 0.05           | 5,000              | 2,000                  | ~824.53      | Enterprise (custom, modeled 500) | ~826.00| Note: free-tier credits apply (credits-based) | ~349.30               | Variable         | Free           |

Interpretation:
- AWS S3 is the lowest-cost storage backbone under ongoing pricing assumptions for most scenarios, especially as volumes grow beyond tens of thousands of images.
- Supabase’s egress pricing becomes a significant driver at higher transfer volumes; with 5 GB free egress, many public-facing scenarios incur charges sooner.
- Cloudinary’s Plus and Advanced tiers provide predictable monthly costs inclusive of transformations and CDN delivery; DAM free 25 GB can support smaller catalogs but higher storage volumes typically require paid tiers.
- GitHub LFS storage costs are modest at the modeled volumes, but bandwidth is billed separately per GiB downloaded and should be accounted for separately in delivery scenarios.
- Cloudflare’s free CDN can materially reduce origin egress; bandwidth terms should be confirmed with Cloudflare for sustained high-traffic use.

Assumptions: Supabase egress is charged beyond 5 GB; Cloudinary plan selection is based on storage volume relative to DAM Free 25 GB; AWS S3 ongoing costs use ~$0.023/GB storage and ~$0.09/GB egress; GitHub LFS storage cost uses conversion from GB to GiB and the $0.07/GiB rate; first-year AWS S3 costs depend on credits rather than explicit GB allowances in the collected content.

## Image Optimization Strategies to Reduce Costs

Optimization materially lowers bandwidth and storage costs while improving user-perceived performance. For maps and photographs, the most effective techniques are format conversion, responsive delivery, metadata stripping, caching, and lazy loading.

Format conversion:
- Serve next-generation formats such as WebP and AVIF for lossy content, typically reducing file size materially at comparable perceptual quality compared to JPEG, with AVIF often achieving smaller files at a cost of decoding speed trade-offs.[^9]
- Target a quality level that balances clarity and compression; aggressive compression for thumbnails and previews yields larger savings with minimal perceptual impact.

Responsive delivery:
- Generate multiple resolutions and aspect-ratio variants, then deliver the smallest acceptable image for the user’s device and viewport. This approach avoids over-downloading large images to small screens.
- Pair responsive images with the CDN’s caching so repeated views of similar sizes hit cache efficiently.

Metadata and color profiles:
- Strip non-essential metadata (EXIF) to reduce file size, especially for delivery variants; preserve metadata for archival masters where provenance matters but avoid carrying it into web delivery.
- Normalize color profiles where possible to reduce unnecessary embedded data.

Caching and lazy loading:
- Use long time-to-live (TTL) for immutable variants and leverage cache-busting only when assets change. This approach increases CDN cache hit ratios and reduces origin requests.[^8]
- Lazy-load below-the-fold images to avoid downloading assets that users may never see.

CDN best practices:
- A global CDN reduces bandwidth costs by caching content near users and minimizing round trips to the origin, cutting origin egress and improving performance.[^8]
- Consider multi-CDN routing for large audiences across regions, but only if it simplifies cost and performance goals; monitor routing decisions and cache policies closely.

Table 6 maps each strategy to the primary benefit, expected impact, and platform support.

Table 6: Optimization strategy map

| Strategy                    | Primary Benefit                 | Expected Impact                       | Platform Support (examples)                                |
|----------------------------|---------------------------------|---------------------------------------|-------------------------------------------------------------|
| WebP/AVIF conversion       | Smaller delivery size           | Bandwidth reduction; faster loads     | Cloudinary transformations; Supabase via pipeline/CDN       |
| Responsive variants        | Fit-to-device images            | Lower transfer per view               | Cloudinary responsive delivery; custom pipelines            |
| Metadata stripping         | Smaller files                   | Reduced storage and transfer          | Cloudinary transformations; custom pipelines                |
| Long TTL + cache-busting   | Higher cache hit ratio          | Reduced origin egress                 | Cloudflare CDN; CloudFront; origin header control           |
| Lazy-loading               | Defer non-critical downloads    | Lower initial page transfer           | Front-end frameworks; CDN caching does not affect loading order |
| Color profile normalization| Remove redundant data           | Slight file size reduction            | Cloudinary transformations; custom pipelines                |

The optimization pipeline can be implemented in Cloudinary (transformations and responsive URLs), Supabase (store originals; transform via pipeline/CDN), or in conjunction with Cloudflare (cache and deliver optimized variants produced by an origin pipeline). A reasonable target is a 50–70% reduction in delivery size per view versus original masters, achieved through resizing and modern formats; quality tuning is essential for map legibility and street photo detail.

## Architecture Patterns and Recommendations

Three architecture patterns address the majority of archival and delivery needs:

1) Cloudinary-centric pipeline:
- Store originals in Cloudinary (or DAM), apply transformations, and deliver via CDN. This pattern simplifies operations and provides rich features—responsive variants, metadata, and video support—at predictable monthly costs (Plus/Advanced). It suits teams prioritizing rapid delivery and consistent optimization without building a bespoke pipeline.[^3][^4]

2) S3 + Cloudflare CDN:
- Use S3 as the durable origin store and front with Cloudflare’s free CDN. Generate delivery variants via an external optimization service (e.g., Cloudinary or a build-time pipeline) and cache them aggressively at the edge. This pattern optimizes cost for large archives and offers flexibility in transformation providers; confirm bandwidth terms and any image optimization needs with Cloudflare.[^5][^2][^10][^11]

3) Supabase + CDN:
- Leverage Supabase Storage for apps that require integrated access controls and simple developer workflows. Keep high-resolution masters outside Supabase or segment assets to respect the 50 MB upload limit; use the CDN for egress offload. This pattern is ideal for internal tools or small public catalogs with straightforward requirements.[^1][^2]

Table 7 compares architecture patterns.

Table 7: Architecture comparison

| Pattern                 | Pros                                                | Cons                                                   | Free-tier Fit                            | Optimization Path                                   | Estimated Cost (10K @ 0.01 GB; 2 views/mo) |
|-------------------------|-----------------------------------------------------|--------------------------------------------------------|------------------------------------------|-----------------------------------------------------|---------------------------------------------|
| Cloudinary-centric      | Integrated transformations + CDN; predictable costs | Higher monthly plan costs than bare storage            | Good for pilots (DAM Free 25 GB)         | Cloudinary transformations and responsive delivery  | Plus $99/month                              |
| S3 + Cloudflare CDN     | Lowest storage cost; durable; flexible optimization | Requires external optimization; transfer terms vary    | Depends on CDN terms and credits         | External pipeline (e.g., Cloudinary); edge caching  | ~$8/month storage + CDN offload             |
| Supabase + CDN          | Developer-friendly; access control; simple stack    | 50 MB upload cap; egress costs add up                  | Good for prototypes/internal tools       | Origin pipeline; CDN caching                        | ~$16/month                                  |

Choice guidance:
- Choose Cloudinary for immediate, high-quality optimization with minimal orchestration.
- Choose S3 + Cloudflare for cost-sensitive archives with large volumes and the willingness to manage transformations separately.
- Choose Supabase when app integration and access control simplicity outweigh file-size constraints and storage/egress economics.

## Risks, Caveats, and Compliance

Several practical caveats and risks should inform design choices:

- Cloudflare free plan bandwidth terms are not explicitly enumerated on the core free plan page. Community discussions about “unlimited bandwidth” exist, but you should confirm CDN bandwidth handling and any fair-use policies with Cloudflare before relying on it for sustained high-traffic delivery.[^2][^11]
- AWS S3 egress and transfer pricing varies by region and by destination CDN. S3-to-CloudFront transfers are often excluded from charges, but precise costs depend on region, configuration, and provider terms; confirm using official pricing tables and the AWS Pricing Calculator.[^5][^13]
- GitHub LFS is not a delivery CDN. Bandwidth overages are billed per GiB downloaded, and exceeding storage without a payment method on file can restrict functionality.[^6]
- Image provenance and rights management are critical for historical archives. Ensure metadata preservation for masters, enforce access controls where needed, and document derivative-generation processes to maintain auditability.
- Vendor lock-in can affect portability. Cloudinary’s transformations are powerful but tied to its platform; S3 offers portability but requires building transformation pipelines elsewhere.

## Implementation Roadmap and Operationalization

A phased roadmap reduces risk and accelerates time-to-value:

Phase 1: Prototype
- Stand up a minimal pipeline: upload a small subset of images, apply basic transformations, and serve via CDN. Validate the optimization target (e.g., 40–60% size reduction) and the quality thresholds needed for legibility in maps and clarity in street photos.[^8][^9]

Phase 2: Optimization hardening
- Implement responsive variants and metadata stripping. Tune compression quality per asset type and device profile. Measure cache hit ratios and refine TTLs for static variants to minimize origin load.[^8]

Phase 3: Migration and scaling
- Migrate larger archives to the chosen storage backbone (S3 or Cloudinary DAM). Integrate lifecycle policies or tiered storage if using S3. Establish monitoring dashboards for bandwidth, storage growth, cache efficiency, and transformation performance.[^5][^8]

Phase 4: Governance
- Document provenance metadata for masters and ensure rights management policies are enforced. Establish audit trails for derivative generation and ensure that caching and cache-busting practices preserve content integrity over time.[^8]

## References

[^1]: Pricing & Fees — Supabase. https://supabase.com/pricing  
[^2]: Free Plan Overview — Cloudflare. https://www.cloudflare.com/plans/free/  
[^3]: Pricing and Plans — Cloudinary. https://cloudinary.com/pricing  
[^4]: Compare Plans — Cloudinary. https://cloudinary.com/pricing/compare-plans  
[^5]: S3 Pricing — AWS. https://aws.amazon.com/s3/pricing/  
[^6]: About billing for Git Large File Storage — GitHub Docs. https://docs.github.com/billing/managing-billing-for-git-large-file-storage/about-billing-for-git-large-file-storage  
[^7]: Pricing Calculator — GitHub. https://github.com/pricing/calculator  
[^8]: How can using a CDN reduce bandwidth costs? — Cloudflare. https://www.cloudflare.com/learning/cdn/how-cdns-reduce-bandwidth-cost/  
[^9]: Sustainability and Efficiency: The Green Side of Image Optimization with CDNs — CacheFly. https://www.cachefly.com/news/sustainability-and-efficiency-the-green-side-of-image-optimization-with-cdns/  
[^10]: Pricing · Cloudflare Images docs. https://developers.cloudflare.com/images/pricing/  
[^11]: How can Cloudflare offer a free CDN with unlimited bandwidth? — Webmasters StackExchange. https://webmasters.stackexchange.com/questions/88659/how-can-cloudflare-offer-a-free-cdn-with-unlimited-bandwidth  
[^12]: AWS Free Tier. https://aws.amazon.com/free/  
[^13]: AWS Pricing Calculator. https://calculator.aws/  
[^14]: S3 Billing FAQs — AWS. https://aws.amazon.com/s3/faqs/#Billing

---

Information gaps acknowledged in this report:
- Cloudflare free plan explicit bandwidth limits for CDN are not specified on the core free plan page; verify with Cloudflare support or plan documentation.
- AWS S3 region-specific pricing and exact data transfer rates to CloudFront or third-party CDNs require confirmation in official tables and the AWS Pricing Calculator.
- Cloudinary free plan per-file maximum size and precise monthly credit consumption per transformation are not explicitly stated in the collected content.
- GitHub LFS bandwidth billing rate per GiB beyond the free tier requires confirmation via GitHub’s pricing calculator or official billing docs.
- Supabase free-tier “cached egress” mechanics and its interaction with CDN caching should be validated against Supabase documentation.
- Real-world compression ratios for typical historical maps and street photos depend on content and require empirical measurement; scenarios here model a 40% optimized delivery size factor.