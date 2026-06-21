-- 0004_acessos_hauldr.sql — the "Acessos" (team/members) screen, Hauldr-native.
--
-- `usuarios` is the display/role list the admin manages — distinct from the
-- GoTrue auth users people log in with. In the Hauldr tier this is a plain
-- owner-keyed table (CRUD over PostgREST). Provisioning an actual login is a
-- GoTrue-admin concern (service_role), out of scope for the app's RLS token.
-- Owner-keyed RLS, same pattern as 0002/0003. Idempotent.

create extension if not exists pgcrypto;
create schema if not exists hauldr;
set search_path = public;

create or replace function hauldr.current_user_id() returns uuid
  language sql stable as $$
  select nullif(current_setting('request.jwt.claims', true)::json ->> 'sub', '')::uuid;
$$;

create table if not exists usuarios (
  id         uuid primary key default gen_random_uuid(),
  owner      uuid not null default hauldr.current_user_id(),
  nome       text not null default '',
  email      text not null default '',
  papel      text not null default 'Membro',
  status     text not null default 'Ativo',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Shared workspace: the team directory is visible to all authenticated staff
-- (the DM picker + dashboard read it). `owner` is an audit stamp.
alter table usuarios enable row level security;

drop policy if exists usuarios_owner on usuarios;
drop policy if exists usuarios_rw on usuarios;
create policy usuarios_rw on usuarios for all to authenticated
  using (true) with check (true);

grant usage on schema public, hauldr to anon, authenticated;
grant execute on all functions in schema hauldr to anon, authenticated;
grant select, insert, update, delete on usuarios to authenticated;
