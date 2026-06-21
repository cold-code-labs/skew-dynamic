-- 0003_resources_hauldr.sql — the generic resource engine, Hauldr-native.
--
-- One table per ResourceDef in config/resources.ts (clientes, lancamentos,
-- projetos, tarefas). Columns mirror each def's declared display/edit fields.
-- Owner-keyed RLS (owner = JWT sub), same pattern as 0002. Idempotent.

create extension if not exists pgcrypto;
create schema if not exists hauldr;
set search_path = public;

create or replace function hauldr.current_user_id() returns uuid
  language sql stable as $$
  select nullif(current_setting('request.jwt.claims', true)::json ->> 'sub', '')::uuid;
$$;

-- ── clientes ──────────────────────────────────────────────────────────────────
create table if not exists clientes (
  id         uuid primary key default gen_random_uuid(),
  owner      uuid not null default hauldr.current_user_id(),
  nome       text not null default '',
  contato    text not null default '',
  plano      text not null default '',
  status     text not null default 'Ativo',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ── lancamentos (Financeiro) ──────────────────────────────────────────────────
create table if not exists lancamentos (
  id         uuid primary key default gen_random_uuid(),
  owner      uuid not null default hauldr.current_user_id(),
  descricao  text not null default '',
  categoria  text not null default '',
  valor      numeric not null default 0,
  status     text not null default 'Pendente',
  vencimento date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ── projetos ──────────────────────────────────────────────────────────────────
create table if not exists projetos (
  id          uuid primary key default gen_random_uuid(),
  owner       uuid not null default hauldr.current_user_id(),
  nome        text not null default '',
  responsavel text not null default '',
  fase        text not null default 'Planejamento',
  prazo       date,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- ── tarefas ───────────────────────────────────────────────────────────────────
create table if not exists tarefas (
  id          uuid primary key default gen_random_uuid(),
  owner       uuid not null default hauldr.current_user_id(),
  titulo      text not null default '',
  responsavel text not null default '',
  prioridade  text not null default 'Média',
  status      text not null default 'A fazer',
  prazo       date,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- ── RLS (shared workspace: any authenticated staff sees/edits all rows) ───────
-- Parity with the PocketBase apps + coldcodelabs. `owner` is an audit stamp.
alter table clientes    enable row level security;
alter table lancamentos enable row level security;
alter table projetos    enable row level security;
alter table tarefas     enable row level security;

drop policy if exists clientes_rw on clientes;
create policy clientes_rw on clientes for all to authenticated
  using (true) with check (true);

drop policy if exists lancamentos_rw on lancamentos;
create policy lancamentos_rw on lancamentos for all to authenticated
  using (true) with check (true);

drop policy if exists projetos_rw on projetos;
create policy projetos_rw on projetos for all to authenticated
  using (true) with check (true);

drop policy if exists tarefas_rw on tarefas;
create policy tarefas_rw on tarefas for all to authenticated
  using (true) with check (true);

-- ── Grants (RLS gates the rows) ───────────────────────────────────────────────
grant usage on schema public, hauldr to anon, authenticated;
grant execute on all functions in schema hauldr to anon, authenticated;
grant select, insert, update, delete
  on clientes, lancamentos, projetos, tarefas to authenticated;
