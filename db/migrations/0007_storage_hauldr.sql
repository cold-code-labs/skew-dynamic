-- 0007_storage_hauldr.sql — the Storage / Arquivos module, Hauldr-native.
--
-- File bytes live in Garage (S3); this table holds the metadata + the object key
-- so the UI can list/group/label and the proxy can stream the bytes. Shared
-- workspace RLS (all authenticated staff see the file library). Idempotent.

create extension if not exists pgcrypto;
create schema if not exists hauldr;
set search_path = public;

create or replace function hauldr.current_user_id() returns uuid
  language sql stable as $$
  select nullif(current_setting('request.jwt.claims', true)::json ->> 'sub', '')::uuid;
$$;

create table if not exists documentos (
  id           uuid primary key default gen_random_uuid(),
  owner        uuid not null default hauldr.current_user_id(),
  name         text not null default 'arquivo',
  category     text not null default 'Geral',
  size         bigint not null default 0,
  s3_key       text not null,
  content_type text not null default 'application/octet-stream',
  created_at   timestamptz not null default now()
);

alter table documentos enable row level security;

drop policy if exists documentos_rw on documentos;
create policy documentos_rw on documentos for all to authenticated
  using (true) with check (true);

grant usage on schema public, hauldr to anon, authenticated;
grant execute on all functions in schema hauldr to anon, authenticated;
grant select, insert, update, delete on documentos to authenticated;
