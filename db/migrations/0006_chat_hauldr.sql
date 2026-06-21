-- 0006_chat_hauldr.sql — the Chat module (channels + DMs), Hauldr-native.
--
-- Conversations in `chat_channels`, messages in `chat_messages`. Like the
-- PocketBase path, access control is enforced in app code (canSeeChannel) — the
-- RLS here is just the authenticated gate (shared workspace): any authenticated
-- user can read/write, and the server filters visibility per role/membership.
-- `members` holds GoTrue subs (the directory upsert in lib/chat/rest keeps
-- `usuarios.id` = sub so DMs resolve). Idempotent.

create extension if not exists pgcrypto;
create schema if not exists hauldr;
set search_path = public;

create or replace function hauldr.current_user_id() returns uuid
  language sql stable as $$
  select nullif(current_setting('request.jwt.claims', true)::json ->> 'sub', '')::uuid;
$$;

-- ── chat_channels ─────────────────────────────────────────────────────────────
create table if not exists chat_channels (
  id            uuid primary key default gen_random_uuid(),
  owner         uuid not null default hauldr.current_user_id(),
  nome          text not null default 'Canal',
  slug          text not null default '',
  descricao     text not null default '',
  tipo          text not null default 'canal',
  allowed_roles text not null default '',
  members       text[] not null default '{}',
  icone         text not null default '',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create unique index if not exists chat_channels_slug_idx
  on chat_channels (slug) where slug <> '';

-- ── chat_messages ─────────────────────────────────────────────────────────────
create table if not exists chat_messages (
  id         uuid primary key default gen_random_uuid(),
  owner      uuid not null default hauldr.current_user_id(),
  channel    uuid not null references chat_channels(id) on delete cascade,
  autor      text not null default '',
  autor_nome text not null default 'Usuário',
  corpo      text not null default '',
  tipo       text not null default 'mensagem',
  anexo      text,
  created_at timestamptz not null default now()
);
create index if not exists chat_messages_channel_idx on chat_messages (channel);

-- ── RLS (shared workspace; visibility filtered in app via canSeeChannel) ──────
alter table chat_channels enable row level security;
alter table chat_messages enable row level security;

drop policy if exists chat_channels_rw on chat_channels;
create policy chat_channels_rw on chat_channels for all to authenticated
  using (true) with check (true);

drop policy if exists chat_messages_rw on chat_messages;
create policy chat_messages_rw on chat_messages for all to authenticated
  using (true) with check (true);

grant usage on schema public, hauldr to anon, authenticated;
grant execute on all functions in schema hauldr to anon, authenticated;
grant select, insert, update, delete on chat_channels, chat_messages to authenticated;
