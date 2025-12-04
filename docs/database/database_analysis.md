# Database Strategy for Scaling a Street Name History Website from UK (~790k records) to 1M+ Records

## Executive Summary

The current dataset for the United Kingdom contains approximately 790,000 records and is expected to grow beyond one million rows. The goal is to move from an initial development environment to a production-grade database that can sustain reliable growth and spatial workloads. Based on the capabilities and limits documented by providers, the recommended high-level path is as follows:

- Build and test locally with SQLite to minimize friction, validate schemas, and iterate quickly on query design. Use this phase to finalize indices and confirm data quality.
- Migrate to a hosted PostgreSQL platform that supports PostGIS to enable spatial features and more robust concurrency. Two primary options emerge:
  - Supabase (PostgreSQL) for a full backend platform with clear free-tier quotas and PostGIS support; Pro tier begins at $25/month.
  - Neon (serverless PostgreSQL) for generous compute allowances (100 CU-hours per project) and PostGIS support; Launch plan starts at $19/month.
- Consider PlanetScale if a MySQL-compatible stack is preferred. PlanetScale no longer offers a free tier; a single-node non-HA Postgres database starts at $5/month, and a PS5 high-availability cluster starts at $15/month. MySQL remains a viable option for non-spatial or lightly spatial use cases.

SQLite is suitable for initial development but has fundamental production limitations: serialized writes, in-process architecture, and limited operational controls. PostgreSQL with PostGIS provides spatial data types, indexing, and operators necessary to model and query street name history with geographic context. Migration from SQLite to PostgreSQL can be executed efficiently with pgloader using a controlled, testable process.

A pragmatic decision rule for the move from SQLite to PostgreSQL is to trigger migration when any of the following occur: approaching free-tier storage caps; increasing concurrency demands (multiple writers or readers); requirement for spatial features (e.g., bounding box or distance queries); need for backup/restore and high availability; or approaching performance limits for read/write workloads under load.

## Workload Profile and Data Characteristics

The primary dataset consists of street name history records, initially concentrated in the United Kingdom and expected to expand to one million or more rows. Non-functional requirements include the ability to perform full-text search, temporal filtering (e.g., by date ranges or renaming events), and—most importantly—geographic operations such as bounding box queries, nearest-neighbor searches, and intersections with administrative boundaries. Spatial capabilities will be essential for map-based exploration, proximity searches, and region-specific historical analysis.

Concurrency needs must be clarified. The workload likely involves more readers than writers; edits may be periodic rather than continuous. The migration strategy and platform choice should reflect the expected traffic patterns and growth trajectory.

## SQLite for Initial Development: Capabilities and Limitations

SQLite’s in-process, file-based design makes it ideal for local development and early testing. It is fast to set up, simple to operate, and sufficient for validating schemas, sample queries, and indexing choices. However, its architecture imposes constraints in production: writes are serialized, there is no built-in high availability, and operational controls for monitoring, connection management, and scaling are minimal.

SQLite’s official implementation limits are generous but not without practical considerations. The database file size can be very large (up to 281 terabytes in recent versions), but performance depends on query patterns and whether working sets fit in memory and cache. Other limits include a default maximum of 2,000 columns, a maximum of 64 tables in a join, and maximum expression depth and function argument counts that are ample for typical usage but configurable where necessary.[^1] While SQLite can store large datasets, the absence of multi-user concurrency controls and distributed operations means it is not well suited for production web-scale traffic.

A crucial caveat is concurrency: SQLite serializes writes, so concurrent write workloads will hit a bottleneck. For read-heavy workloads, it can perform well, especially with proper indexing and queries designed to minimize full scans. Nevertheless, SQLite’s design trade-offs favor simplicity over multi-tenant production resilience, making it appropriate for development and prototyping but not as the final production database for this use case.[^2]

To illustrate key limits and their relevance, Table 1 summarizes selected SQLite implementation limits and notes implications for this project.

Table 1. Selected SQLite implementation limits and notes

| Limit                                | Default/Hard Limit                    | Notes                                                                                           |
|--------------------------------------|---------------------------------------|-------------------------------------------------------------------------------------------------|
| Maximum database size                | Up to 281 TB (recent versions)        | Large file sizes are possible; performance depends on query patterns and memory/cache fit.[^1]  |
| Maximum columns per table            | Default 2,000 (hard 32,767)           | Very wide tables increase memory and slow prepare; prefer normalized designs.[^1]              |
| Maximum tables in a join             | 64                                    | Complex joins with many tables may be constrained; simplify or break up queries.[^1]           |
| SQL statement length                 | Up to 1 billion bytes                 | Use host parameters instead of embedding large literals for safety and performance.[^1]        |
| Expression depth                     | Default 1,000                         | Protects stack usage during code generation; most real-world queries far below this.[^1]       |
| Function arguments                   | Default 1,000 (hard 32,767)           | Sufficient for typical UDF usage; raised from 100 in recent versions.[^1]                      |
| LIKE/GLOB pattern length             | 50,000 bytes                          | Pathological patterns can cause O(N²) performance; constrain untrusted input.[^1]              |
| Maximum attached databases           | Default 10 (hard 125)                 | Multiple attached files are supported but increase complexity.[^1]                              |

### Implications for the Street Name History Use Case

For the initial development phase, SQLite can be used to finalize schemas, design indices, and refine queries. However, as concurrency increases, the serialized write model becomes limiting. If the application requires multi-user editing, background updates, or more robust operational controls (backups, HA, monitoring, connection pooling), the system should migrate to a hosted PostgreSQL platform that supports PostGIS. In practice, the moment the project requires spatial queries or moves toward production usage, PostgreSQL becomes the more appropriate foundation.

## Platform Deep Dives and Free-Tier Limits

Four platforms are considered for the production database: Supabase, PlanetScale, Railway, and Neon. All provide credible routes to production, but their free tiers and cost models differ. Spatial requirements and migration tooling also influence the choice.

### Supabase (PostgreSQL)

Supabase’s free tier provides 500 MB database storage, 1 GB file storage, 5 GB egress (with an additional 5 GB cached egress), 50,000 monthly active users, shared CPU compute with 500 MB RAM, and basic log retention of one day. Projects pause after one week of inactivity. PostGIS is supported via extension enablement with spatial data types and operators for bounding box and nearest-neighbor queries, as documented by Supabase and PostGIS.[^4][^3] Connection pooling guidance indicates Nano (free) and Micro tiers allow up to 60 direct connections and 200 pooler connections, with higher tiers increasing these limits.[^5]

The Pro plan starts at $25 per month and expands quotas (e.g., larger compute, 100,000 MAUs, 8 GB disk included), with usage-based charges beyond included allowances.[^3] Supabase also documents billing policies, including storage overage pricing and project-level quotas, providing a clear path to scale as usage grows.[^6]

Table 2 summarizes Supabase’s free-tier constraints and key Pro-tier entry points.

Table 2. Supabase free-tier limits and Pro-tier baseline

| Category           | Free Tier                                                        | Pro Tier Baseline                                      |
|--------------------|------------------------------------------------------------------|--------------------------------------------------------|
| Database storage   | 500 MB per project                                               | 8 GB disk included; overage billed per documentation[^6] |
| File storage       | 1 GB                                                             | Larger quotas with plan upgrades[^3]                   |
| Egress             | 5 GB egress + 5 GB cached egress                                 | Larger quotas with plan upgrades[^3]                   |
| Compute            | Shared CPU, 500 MB RAM                                           | Larger compute sizes available[^3]                     |
| Connections        | Up to 60 direct and 200 pooler on Nano/Micro                     | Higher per tier per guidance[^5]                       |
| Auth/MAUs          | 50,000 MAUs                                                      | 100,000 MAUs included; overage billed[^3][^6]          |
| PostGIS            | Available via extension                                          | Available                                              |

Supabase’s documentation for PostGIS details geometry types, GIST indexing, and common operators, including distance-based ordering and bounding box filtering.[^4] This support is crucial for spatial queries in a street name history application.

### PlanetScale (MySQL and Postgres)

PlanetScale offers both MySQL (Vitess) and Postgres engines, but does not provide a free tier. A single-node non-high-availability Postgres database starts at $5/month; the base PS5 high-availability cluster starts at $15/month and includes three nodes and 10 GB storage. A resource-based Scaler Pro plan provides flexibility for scaling compute and storage, and includes 100 GB of egress with overage at $0.06 per GB.[^7]

PlanetScale’s MySQL compatibility and Vitess architecture provide excellent horizontal scaling via explicit sharding. However, PostGIS is a PostgreSQL extension; MySQL-compatible deployments do not provide PostGIS. If the project requires PostGIS, the recommended path is to choose PlanetScale Postgres or use a platform that natively supports PostgreSQL with PostGIS.[^8] System limits for Vitess (e.g., schema tables and column counts) are documented, providing operational guardrails for large schemas.[^9]

Table 3 outlines PlanetScale’s entry pricing and key plan elements.

Table 3. PlanetScale entry plans and features

| Plan/Option                   | Pricing (Monthly) | Included Resources                         | Notes                                      |
|------------------------------|-------------------|--------------------------------------------|--------------------------------------------|
| Postgres single-node (non-HA)| Starting at $5    | Single node                                 | No free tier[^7]                           |
| PS5 HA cluster               | Starting at $15   | 3 nodes, 10 GB storage, 99.99% SLA          | High availability, multi-AZ[^7]            |
| Scaler Pro                   | Resource-based    | Configurable instance sizes, storage        | 100 GB egress included; $0.06/GB overage[^7] |
| Enterprise                   | Custom            | Bring-your-own-cloud option                 | Discounts, upgraded support[^7]            |

### Railway (PostgreSQL; usage-based)

Railway offers a usage-based pricing model with a free plan that includes a 30-day trial and $5 credits, followed by a $1/month minimum usage after the trial. Resource usage (CPU per vCPU-second, memory per GB-second, and volumes per GB-second) is billed per second, with published rates. Free and paid plans include object storage priced per GB-month, and egress priced per GB.[^10][^11]

Railway provides PostgreSQL services and supports extension-based PostGIS installations; however, the PostGIS extension’s availability and any provider-specific constraints are not explicitly documented in the materials reviewed here. As a result, users should validate PostGIS enablement on Railway’s PostgreSQL service before relying on it for spatial workloads.[^12]

Table 4 summarizes Railway’s usage-based model and free-plan constraints.

Table 4. Railway usage pricing and free-plan quotas

| Category                  | Pricing/Quota                                             | Notes                                                 |
|--------------------------|------------------------------------------------------------|-------------------------------------------------------|
| CPU                      | $0.00000772 per vCPU per second                           | Billed per second[^11]                                |
| Memory                   | $0.00000386 per GB per second                             | Billed per second[^11]                                |
| Volumes (disk)           | $0.00000006 per GB per second                             | Billed per second[^11]                                |
| Egress (services)        | $0.05 per GB                                              | Public transfer billed[^11]                           |
| Object storage           | $0.015 per GB-month                                       | Class A/B operations free[^11]                        |
| Free plan                | $0/month with 30-day $5 credits; $1/month minimum after   | 1 project, 0.5 GB volume, 1 GB ephemeral disk[^10][^11] |

Given the trial-based nature of Railway’s free plan and the per-second billing model, it is a flexible option for short-term testing and controlled production workloads with predictable resource needs.

### Neon (Serverless PostgreSQL)

Neon’s free tier provides 0.5 GB of database storage per project, 100 compute unit (CU)-hours per project (with autoscaling up to 2 CU, 4 GB RAM per CU), branching, built-in connection pooling, and high availability with multi-zone storage. The free plan includes up to 6 hours of point-in-time restore (PITR) covering up to 1 GB of data changes, and 5 GB of public network transfer. Monitoring retention is one day. PostGIS is supported via extension enablement, with documented usage of geometry and geography types, GIST indexing, and spatial functions for distance and intersection queries.[^14][^13]

Neon’s Launch plan starts at $19/month, and Scale plans provide larger compute allowances; exact quotas vary by plan.[^14][^17] Neon’s architecture is serverless and autoscaling, making it attractive for variable workloads and developer-friendly branching.

Table 5 summarizes Neon’s free-tier allowances and extension support.

Table 5. Neon free-tier allowances and PostGIS support

| Category           | Free Tier                                                | Notes                                     |
|--------------------|-----------------------------------------------------------|-------------------------------------------|
| Storage            | 0.5 GB per project                                       | Branching supported[^14]                  |
| Compute            | 100 CU-hours; autoscales up to 2 CU (4 GB RAM per CU)    | Scales to zero after inactivity[^14]      |
| Pooling            | Built-in (pgBouncer)                                     | Scales to high connection counts[^14]     |
| PITR               | Up to 6 hours / up to 1 GB changes                       | Applies to project branches[^14]          |
| Network transfer   | 5 GB public network transfer included                    | Monitoring retention 1 day[^14]           |
| PostGIS            | Available via extension                                  | GIST indexing supported[^13]              |

## PostGIS Capabilities and Spatial Workflows

PostGIS is an extension to PostgreSQL that adds spatial data types, functions, and operators. It supports both geometry (cartesian coordinates) and geography (spherical coordinates), enabling a range of spatial queries that are directly relevant to street name history: bounding box filters, distance calculations, nearest-neighbor searches, and geometric intersections.[^15]

Common operations include:

- Bounding box queries using operators such as && to test for intersections between geometries and functions like ST_MakeBox2D and ST_SetSRID (with SRID 4326 for standard longitude/latitude).
- Distance-based ordering and nearest-neighbor search using the <-> operator, which leverages spatial indexes to accelerate queries.
- Insertion and transformation of spatial data (e.g., ST_X and ST_Y to extract longitude and latitude from point geometries).

Supabase documents PostGIS usage and operators in its platform guidance, and Neon provides detailed extension documentation covering geometry and geography, GIST indexing, and spatial functions such as ST_DWithin, ST_Distance, ST_Intersects, ST_MakeLine, and ST_Buffer.[^4][^13] These capabilities provide a robust foundation for implementing map-based exploration and geographic filtering in the application.

## Migration Strategies: SQLite to PostgreSQL

Migrating from SQLite to PostgreSQL can be executed smoothly with pgloader, which supports automatic schema discovery, index creation, data type casting, and flexible options for controlling table creation, truncation, triggers, and sequences. A typical command-line migration copies data from a SQLite file to a PostgreSQL database with defaults that create tables and indexes and reset sequences after loading.[^16]

For this project, a pragmatic approach is to adopt a phased migration:

1. Schema-only migration to create tables and indexes in PostgreSQL, optionally enabling PostGIS first if spatial columns are present.
2. Data-only migration to copy rows with minimal friction, leveraging pgloader’s defaults and custom cast rules if needed.
3. Index rebuild to ensure proper index states and sequence reset for primary keys or identity columns.

Validation should include row counts, checksums of representative columns, index integrity checks, and query smoke tests to confirm that PostGIS-enabled queries perform as expected. If the dataset includes spatial data from SpatiaLite or GeoJSON, confirm PostGIS types and SRID values, and ensure that SRID 4326 is used consistently for lat/long geocoding.

Table 6 compares a few migration options.

Table 6. Migration options comparison

| Option          | Pros                                                     | Cons                                                         | Recommended Usage                                      |
|-----------------|----------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------|
| pgloader        | Single-command migration; auto schema discovery; indexes; flexible options | Requires attention to triggers/sequences and cast rules      | Primary tool for SQLite → PostgreSQL migration[^16]    |
| CSV + COPY      | Simple, transparent data movement                        | Manual schema setup; index creation; slower without parallel | Small tables or manual control scenarios               |
| FDW (postgres_fdw) | Remote query access; no full data movement               | Not ideal for one-time bulk migration; complexity            | Cross-database queries; staging integrations           |

### Spatial Data Handling in Migration

When migrating spatial data, enable PostGIS in the target PostgreSQL database and validate geometry/geography types and SRID. Ensure that indexes (GIST) are created on spatial columns. Common pitfalls include incorrect SRID, missing index creation leading to slow queries, and type mismatches between SQLite’s spatial representations and PostGIS geometry/geography.[^15]

## Platform Comparison and Cost Modeling

To support the decision, the following matrix compares free-tier characteristics relevant to this use case, focusing on storage, compute, PostGIS support, and migration tooling readiness.

Table 7. Free-tier comparison matrix

| Platform  | Storage (DB)                 | Compute                             | Connections                     | PostGIS Support            | Egress / Network                  | Pricing Baseline             |
|-----------|-------------------------------|-------------------------------------|----------------------------------|----------------------------|-----------------------------------|------------------------------|
| Supabase  | 500 MB per project[^3][^6]    | Shared CPU, 500 MB RAM[^3]          | Up to 60 direct / 200 pooler[^5] | Yes (extension)[^4]        | 5 GB egress + 5 GB cached[^3]     | Pro $25/month[^3]            |
| Neon      | 0.5 GB per project[^14]       | 100 CU-hours; up to 2 CU (8 GB RAM)[^14] | Built-in pooling[^14]            | Yes (extension)[^13]        | 5 GB public transfer[^14]         | Launch $19/month[^14]        |
| Railway   | Usage-based volumes[^11]      | CPU/memory per-second billing[^11]  | Varies by service                | Likely via extension (validate)[^12] | $0.05/GB egress[^11]           | Free trial + $5 credits[^10] |
| PlanetScale | No free tier; from $5 (Postgres) | HA cluster from $15/month[^7]        | Varies by plan                    | Postgres engine supports PostGIS; MySQL does not | 100 GB egress included[^7]     | Resource-based Scaler Pro[^7] |

Cost scenarios provide rough guidance for early production, recognizing that actual costs depend on workload patterns (compute utilization, storage growth, and egress).

Table 8. Cost scenarios: rough monthly estimates for early production

| Platform | Scenario                                   | Included Allowances                            | Estimated Monthly Cost (Early Production)              |
|----------|--------------------------------------------|------------------------------------------------|--------------------------------------------------------|
| Supabase | Pro plan baseline                          | 8 GB disk; 100,000 MAUs; larger compute[^3]    | $25/month baseline; storage/egress overages apply[^6]  |
| Neon     | Launch plan                                | Larger compute; branching; pooling[^14]        | $19/month baseline; usage-based beyond allowances[^14] |
| PlanetScale | PS5 HA cluster                            | 3 nodes; 10 GB storage; 99.99% SLA[^7]         | $15/month baseline; egress overage $0.06/GB[^7]        |
| Railway  | Small Postgres with modest usage           | CPU/memory volumes per-second billing[^11]     | Depends on usage; typically low tens of $/month[^11]   |

A simple decision tree helps choose the initial platform:

- Prefer Supabase if you value an integrated platform (Auth, Storage, Realtime) with clear quotas and PostGIS support.
- Prefer Neon if you want serverless compute with generous branching and connection pooling, and PostGIS availability.
- Consider PlanetScale Postgres if you need a low-cost HA cluster with predictable egress; choose PlanetScale MySQL only if you do not require PostGIS.
- Use Railway for usage-based control and short-term testing or for teams comfortable managing infrastructure details.

## Scalability Path and Operations

Once in production, scalability options vary by platform:

- Supabase: Scale compute sizes and upgrade plan tiers. Implement connection pooling, optimize queries, and consider caching for read-heavy endpoints. Monitor egress and storage growth, and plan for backup and point-in-time recovery (PITR) features available in paid tiers.[^3][^6]
- Neon: Use autoscaling to right-size compute, create read replicas for read-heavy workloads, and leverage branching for safe schema changes and data experiments. Built-in connection pooling simplifies high-connection scenarios.[^14]
- PlanetScale: Scale horizontally with Vitess sharding (MySQL) or move to larger Postgres clusters under resource-based plans. For high availability, deploy across availability zones and use the documented SLA tiers.[^7][^8]
- Railway: Scale CPU/memory and volumes per usage metrics; plan egress costs explicitly. Establish backups and volume snapshots and monitor IOPS characteristics and service limits.[^11]

Backups, point-in-time recovery (PITR), and monitoring retention should be factored into operations budgets. Supabase provides PITR and backups in paid tiers; Neon offers limited PITR on the free plan; Railway’s log retention varies by plan, and PlanetScale includes automated backups with enterprise options.[^3][^14][^7]

## Recommendations

- Adopt PostgreSQL with PostGIS for production. Supabase and Neon are the leading options due to documented PostGIS support and mature developer workflows. Supabase is particularly attractive if the application benefits from integrated backend services; Neon excels with autoscaling, branching, and built-in connection pooling.
- Use SQLite for local development and testing. It is well suited to validate schemas, indices, and sample queries. Define clear triggers for migration: storage limits approached, concurrency needs exceeding SQLite’s model, requirement for spatial operations, and the need for HA, backups, and monitoring.
- Plan the migration with pgloader. Execute schema-only and data-only phases, rebuild indices, and reset sequences. Validate row counts, checksums, and index integrity. Perform query smoke tests, including PostGIS bounding box and nearest-neighbor queries to confirm performance.
- Establish cost controls. Right-size compute, manage egress, and use caching for read-heavy endpoints. For Neon and Supabase, monitor MAUs, compute usage, and storage growth; for PlanetScale, track egress consumption; for Railway, model CPU/memory per second to avoid surprise bills.
- Prepare operations. Enable backups, configure PITR where available, and define clear monitoring and alerting thresholds (storage, connections, compute saturation, slow queries). Consider read replicas for scaling read-heavy workloads.

## Known Information Gaps and Validation Checklist

The following items require validation prior to final commitment:

- Confirm whether PlanetScale currently offers any free-tier quotas for new MySQL or Postgres databases; public materials emphasize paid plans only.[^7]
- Clarify Neon free-tier compute scaling behavior for sustained load and confirm the maximum compute size on free versus paid plans.[^14]
- Explicitly verify Railway’s PostgreSQL PostGIS extension availability and any provider-specific constraints.[^12]
- Confirm the exact storage allowance for Neon free-tier storage; documentation cites 0.5 GB per project; validate that this is the authoritative figure.[^14]
- Document Supabase’s daily database egress (10,000–50 MB mentions appear in community summaries); rely on official billing/pricing pages for final quotas.[^6][^3]
- Establish definitive database size projections for 1M+ records (including indexes and auxiliary tables) to assess free-tier adequacy across platforms.

## Appendix: Tools and References

- Migration tool: pgloader documentation for SQLite to PostgreSQL migrations.[^16]
- PostGIS resources: official documentation and introductory materials on spatial indexing, geometry/geography types, and common spatial functions and operators.[^15]
- Provider pricing and limits: Supabase pricing and billing docs; Neon pricing and plan docs; PlanetScale pricing; Railway pricing and plan docs.[^3][^6][^14][^7][^11]

## References

[^1]: Implementation Limits For SQLite. https://sqlite.org/limits.html  
[^2]: Appropriate Uses For SQLite. https://sqlite.org/whentouse.html  
[^3]: Pricing & Fees — Supabase. https://supabase.com/pricing  
[^4]: PostGIS: Geo queries — Supabase Docs. https://supabase.com/docs/guides/database/extensions/postgis  
[^5]: How to change max database connections — Supabase. https://supabase.com/docs/guides/troubleshooting/how-to-change-max-database-connections-_BQ8P5  
[^6]: About billing on Supabase. https://supabase.com/docs/guides/platform/billing-on-supabase  
[^7]: Pricing and plans — PlanetScale. https://planetscale.com/pricing  
[^8]: MySQL compatibility — PlanetScale. https://planetscale.com/docs/vitess/troubleshooting/mysql-compatibility  
[^9]: Vitess system limits — PlanetScale. https://planetscale.com/docs/vitess/troubleshooting/planetscale-system-limits  
[^10]: Railway Pricing and Plans. https://railway.com/pricing  
[^11]: Pricing Plans — Railway Docs. https://docs.railway.com/reference/pricing/plans  
[^12]: Deploy Supabase Postgres — Railway. https://railway.com/deploy/supabase-postgres-1  
[^13]: The postgis extension — Neon Docs. https://neon.com/docs/extensions/postgis  
[^14]: Neon plans — Neon Docs. https://neon.com/docs/introduction/plans  
[^15]: PostGIS Documentation. https://postgis.net/documentation/  
[^16]: SQLite to Postgres — pgloader documentation. https://pgloader.readthedocs.io/en/latest/ref/sqlite.html  
[^17]: Neon Pricing. https://neon.com/pricing