-- Read-only: list columns for public.streets (types, nullability, defaults).
-- Run in Supabase → SQL Editor against production during low traffic.
-- For passwordless checks from CI or a local shell, you can instead use PostgREST:
--   GET /rest/v1/streets?select=*&limit=1
-- (see public.streets.live-snapshot.json in this folder).

SELECT
  column_name,
  data_type,
  udt_name,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'streets'
ORDER BY ordinal_position;
