-- 0005_dashboard_hauldr.sql — the dashboard data sources, Hauldr-native.
--
-- The postgrest path in lib/data/dashboard.ts reads a `dashboard_stats` view and
-- a `recent_activity` table. The view is `security_invoker` so its counts run
-- under the caller's RLS (each user counts only their own rows), mirroring the
-- PocketBase path. recent_activity is an owner-keyed feed table (empty on a fresh
-- deploy → the activity panel simply shows nothing until rows are written).
-- Depends on 0003 (clientes) + 0004 (usuarios). Idempotent.

create schema if not exists hauldr;
set search_path = public;

-- ── dashboard_stats (live counts, RLS-scoped via security_invoker) ────────────
create or replace view dashboard_stats with (security_invoker = true) as
  select 'clients'    as key, 'Clientes'        as label,
         count(*)::text as value, 'cadastrados'  as delta from clientes
  union all
  select 'active', 'Clientes ativos',
         count(*)::text, 'status Ativo' from clientes where status = 'Ativo'
  union all
  select 'sessions', 'Usuários',
         count(*)::text, 'equipe' from usuarios
  union all
  select 'conversion', 'Conversão', '—', '—';

-- ── recent_activity (owner-keyed feed; "when" is a reserved word → quoted) ─────
create table if not exists recent_activity (
  id         uuid primary key default gen_random_uuid(),
  owner      uuid not null default hauldr.current_user_id(),
  who        text not null default '',
  what       text not null default '',
  "when"     text not null default '',
  created_at timestamptz not null default now()
);

-- Shared workspace feed (all authenticated staff see the same activity).
alter table recent_activity enable row level security;

drop policy if exists recent_activity_owner on recent_activity;
drop policy if exists recent_activity_rw on recent_activity;
create policy recent_activity_rw on recent_activity for all to authenticated
  using (true) with check (true);

grant usage on schema public, hauldr to anon, authenticated;
grant select on dashboard_stats to authenticated;
grant select, insert, update, delete on recent_activity to authenticated;
