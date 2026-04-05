-- Streets data QA — read-only checks for Supabase / Postgres (SQL Editor or psql).
--
-- Usage:
--   Run against production during low-traffic windows. Uses aggregates only; safe to re-run.
--   In Supabase: Dashboard → SQL Editor → paste → Run.
--   Locally: psql "$DATABASE_URL" -f scripts/data-quality/streets.sql
--
-- Notes:
--   The `streets` table can be very large (~790k rows). COUNT(*) scans the full heap;
--   run off-peak if your project is sensitive to load. Consider ANALYZE public.streets
--   after bulk imports so planner stats stay fresh.

-- ---------------------------------------------------------------------------
-- 1. Row count
-- ---------------------------------------------------------------------------
SELECT COUNT(*) AS street_row_count
FROM public.streets;

-- ---------------------------------------------------------------------------
-- 2. Missing coordinates (counts and share of rows)
-- ---------------------------------------------------------------------------
SELECT
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE latitude IS NULL) AS null_latitude,
  COUNT(*) FILTER (WHERE longitude IS NULL) AS null_longitude,
  COUNT(*) FILTER (WHERE latitude IS NULL OR longitude IS NULL) AS null_either_coord,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE latitude IS NULL OR longitude IS NULL) / NULLIF(COUNT(*), 0),
    4
  ) AS pct_missing_either_coord
FROM public.streets;

-- ---------------------------------------------------------------------------
-- 3. County distribution (top 25 + other summary)
-- ---------------------------------------------------------------------------
SELECT county, COUNT(*) AS n
FROM public.streets
GROUP BY county
ORDER BY n DESC
LIMIT 25;

SELECT COUNT(DISTINCT county) AS distinct_county_values
FROM public.streets;

-- ---------------------------------------------------------------------------
-- 4. Name quality: null, empty, or whitespace-only
-- ---------------------------------------------------------------------------
SELECT
  COUNT(*) FILTER (WHERE name IS NULL) AS null_name,
  COUNT(*) FILTER (WHERE name IS NOT NULL AND btrim(name) = '') AS empty_name
FROM public.streets;

-- ---------------------------------------------------------------------------
-- 5. Duplicate (name, city, county) — sample only (spot-check; not full dedup)
-- ---------------------------------------------------------------------------
SELECT name, city, county, COUNT(*) AS dup_count
FROM public.streets
GROUP BY name, city, county
HAVING COUNT(*) > 1
ORDER BY dup_count DESC
LIMIT 50;

-- ---------------------------------------------------------------------------
-- 6. Etymology coverage
-- ---------------------------------------------------------------------------
SELECT
  COUNT(*) FILTER (WHERE etymology_suggestion IS NULL) AS null_etymology_suggestion,
  COUNT(*) FILTER (WHERE etymology_suggestion IS NOT NULL AND btrim(etymology_suggestion) = '') AS blank_etymology_suggestion,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE etymology_suggestion IS NULL) / NULLIF(COUNT(*), 0),
    4
  ) AS pct_null_etymology_suggestion
FROM public.streets;

-- ---------------------------------------------------------------------------
-- 7. Timestamps: rows where updated_at is strictly before created_at (should be 0)
-- ---------------------------------------------------------------------------
SELECT COUNT(*) AS rows_updated_before_created
FROM public.streets
WHERE created_at IS NOT NULL
  AND updated_at IS NOT NULL
  AND updated_at < created_at;
