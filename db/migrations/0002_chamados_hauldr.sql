-- 0002_chamados_hauldr.sql — the "Chamados" (service desk) slice, Hauldr-native.
--
-- Applies on top of Hauldr's base schema (migrations/0001_base.sql), which
-- creates the `hauldr` schema + `hauldr.current_user_id()` (reads the JWT `sub`
-- claim PostgREST injects). This file is self-contained and idempotent: it
-- re-declares the helper defensively so it also applies to a bare Postgres that
-- has the `authenticated`/`anon` PostgREST roles but no Hauldr base yet.
--
-- RLS is sub-keyed (per-user): every row carries an `owner` defaulting to the
-- caller's JWT `sub`, and the policies only expose rows the caller owns. This is
-- the foundation proof that per-user RLS reaches the app through PostgREST. The
-- broader port can swap to org-scoping once Hauldr grows tenancy.

create extension if not exists pgcrypto;
create schema if not exists hauldr;

-- A Hauldr project DB has search_path = `auth, public` (GoTrue). Pin to public so
-- every unqualified table below is created in public — the schema PostgREST
-- exposes — and never lands in the auth schema (where REST can't reach it).
set search_path = public;

create or replace function hauldr.current_user_id() returns uuid
  language sql stable as $$
  select nullif(current_setting('request.jwt.claims', true)::json ->> 'sub', '')::uuid;
$$;

-- ── chamados (tickets) ───────────────────────────────────────────────────────
create table if not exists chamados (
  id           uuid primary key default gen_random_uuid(),
  owner        uuid not null default hauldr.current_user_id(),
  assunto      text not null,
  descricao    text not null default '',
  departamento text not null default 'Geral',
  prioridade   text not null default 'Média',
  status       text not null default 'Aberto',
  solicitante  text not null default '',
  responsavel  text not null default '',
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

-- ── chamados_comentarios (thread: comments + system events) ───────────────────
create table if not exists chamados_comentarios (
  id         uuid primary key default gen_random_uuid(),
  owner      uuid not null default hauldr.current_user_id(),
  chamado    uuid not null references chamados(id) on delete cascade,
  autor      text not null default 'Usuário',
  corpo      text not null default '',
  tipo       text not null default 'comentario',
  created_at timestamptz not null default now()
);
create index if not exists chamados_comentarios_chamado_idx
  on chamados_comentarios (chamado);

-- ── notificacoes (in-app notification center, written by ticket events) ───────
create table if not exists notificacoes (
  id         uuid primary key default gen_random_uuid(),
  owner      uuid not null default hauldr.current_user_id(),
  titulo     text not null,
  mensagem   text not null default '',
  tipo       text not null default 'info',
  lida       boolean not null default false,
  data       date not null default current_date,
  created_at timestamptz not null default now()
);

-- ── Row Level Security (owner = JWT sub) ──────────────────────────────────────
alter table chamados              enable row level security;
alter table chamados_comentarios  enable row level security;
alter table notificacoes          enable row level security;

drop policy if exists chamados_owner on chamados;
create policy chamados_owner on chamados
  for all to authenticated
  using (owner = hauldr.current_user_id())
  with check (owner = hauldr.current_user_id());

drop policy if exists chamados_comentarios_owner on chamados_comentarios;
create policy chamados_comentarios_owner on chamados_comentarios
  for all to authenticated
  using (owner = hauldr.current_user_id())
  with check (owner = hauldr.current_user_id());

drop policy if exists notificacoes_owner on notificacoes;
create policy notificacoes_owner on notificacoes
  for all to authenticated
  using (owner = hauldr.current_user_id())
  with check (owner = hauldr.current_user_id());

-- ── Grants for the shared non-owner roles (RLS gates the rows) ────────────────
grant usage on schema public, hauldr to anon, authenticated;
grant execute on all functions in schema hauldr to anon, authenticated;
grant select, insert, update, delete
  on chamados, chamados_comentarios, notificacoes to authenticated;
