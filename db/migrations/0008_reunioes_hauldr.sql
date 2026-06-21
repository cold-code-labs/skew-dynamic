-- 0008_reunioes_hauldr.sql — the Reuniões Gravadas module, Hauldr-native.
--
-- Recorded audio bytes live in Garage (S3); this table holds the meeting
-- metadata, the structured transcript (segmentos/locutores as jsonb) and the
-- audio object key. Audio streams back through /api/reunioes/<id>/audio. Shared
-- workspace RLS. Idempotent.

create extension if not exists pgcrypto;
create schema if not exists hauldr;
set search_path = public;

create or replace function hauldr.current_user_id() returns uuid
  language sql stable as $$
  select nullif(current_setting('request.jwt.claims', true)::json ->> 'sub', '')::uuid;
$$;

create table if not exists reunioes (
  id          uuid primary key default gen_random_uuid(),
  owner       uuid not null default hauldr.current_user_id(),
  titulo      text not null default 'Reunião',
  duracao     integer not null default 0,
  mime        text not null default 'audio/webm',
  status      text not null default 'gravada',
  idioma      text not null default 'pt',
  transcricao text not null default '',
  segmentos   jsonb not null default '[]'::jsonb,
  locutores   jsonb not null default '{}'::jsonb,
  audio_key   text,
  created_at  timestamptz not null default now()
);

alter table reunioes enable row level security;

drop policy if exists reunioes_rw on reunioes;
create policy reunioes_rw on reunioes for all to authenticated
  using (true) with check (true);

grant usage on schema public, hauldr to anon, authenticated;
grant execute on all functions in schema hauldr to anon, authenticated;
grant select, insert, update, delete on reunioes to authenticated;
