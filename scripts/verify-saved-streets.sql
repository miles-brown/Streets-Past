-- Verify public.saved_streets after applying supabase/migrations/20260405120000_saved_streets.sql
-- (or scripts/apply-saved-streets.sql). Read-only; safe to run in Supabase → SQL Editor during low traffic.
--
-- Expect: one row per check with ok = true. If the table is missing, the first query fails.

-- 1) Table exists with expected columns
select
  c.column_name,
  c.data_type,
  c.is_nullable,
  true as ok
from information_schema.columns c
where c.table_schema = 'public'
  and c.table_name = 'saved_streets'
  and c.column_name in ('id', 'user_id', 'street_id', 'created_at')
order by c.ordinal_position;

-- 2) RLS enabled on saved_streets
select
  c.relname as table_name,
  c.relrowsecurity as rls_enabled,
  (c.relrowsecurity = true) as ok
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relname = 'saved_streets'
  and c.relkind = 'r';

-- 3) Policies: select / insert / delete for authenticated (names match migration)
select
  policyname,
  cmd as command,
  roles,
  true as ok
from pg_policies
where schemaname = 'public'
  and tablename = 'saved_streets'
  and policyname in (
    'saved_streets_select_own',
    'saved_streets_insert_own',
    'saved_streets_delete_own'
  )
order by policyname;

-- 4) Grants on table for authenticated (migration grants select, insert, delete)
select
  grantee,
  privilege_type,
  true as ok
from information_schema.role_table_grants
where table_schema = 'public'
  and table_name = 'saved_streets'
  and grantee = 'authenticated'
  and privilege_type in ('SELECT', 'INSERT', 'DELETE')
order by privilege_type;

-- 5) Indexes (optional sanity)
select
  indexname,
  indexdef,
  true as ok
from pg_indexes
where schemaname = 'public'
  and tablename = 'saved_streets'
order by indexname;
