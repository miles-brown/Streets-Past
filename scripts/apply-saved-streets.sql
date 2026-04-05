-- Same as supabase/migrations/20260405120000_saved_streets.sql
-- Run in Supabase Dashboard → SQL Editor if `supabase db push` is unavailable.

create table if not exists public.saved_streets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  street_id uuid not null references public.streets (id) on delete cascade,
  created_at timestamptz not null default now(),
  unique (user_id, street_id)
);

create index if not exists saved_streets_user_id_idx on public.saved_streets (user_id);
create index if not exists saved_streets_street_id_idx on public.saved_streets (street_id);

alter table public.saved_streets enable row level security;

create policy "saved_streets_select_own"
  on public.saved_streets for select
  to authenticated
  using ((select auth.uid()) = user_id);

create policy "saved_streets_insert_own"
  on public.saved_streets for insert
  to authenticated
  with check ((select auth.uid()) = user_id);

create policy "saved_streets_delete_own"
  on public.saved_streets for delete
  to authenticated
  using ((select auth.uid()) = user_id);

grant select, insert, delete on table public.saved_streets to authenticated;
