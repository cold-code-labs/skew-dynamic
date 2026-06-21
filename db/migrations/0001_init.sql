-- 0001_init.sql — base schema for the à-la-carte stack (vanilla Postgres).
--
-- Run on a fresh database as a superuser (it creates the PostgREST roles).
-- Idempotent: safe to re-run. The Next app never touches Postgres directly —
-- it talks to PostgREST, which switches role based on the JWT `role` claim.

create extension if not exists pgcrypto;  -- gen_random_uuid()

-- ── PostgREST roles ──────────────────────────────────────────────────────────
-- PostgREST authenticates as a connection role and SET ROLE to one of these
-- per request, based on the JWT `role` claim (default: anon when no JWT).
do $$
begin
  if not exists (select from pg_roles where rolname = 'anon') then
    create role anon nologin;
  end if;
  if not exists (select from pg_roles where rolname = 'authenticated') then
    create role authenticated nologin;
  end if;
end $$;

-- ── Tenants ──────────────────────────────────────────────────────────────────
create table if not exists tenants (
  id         uuid primary key default gen_random_uuid(),
  name       text not null,
  created_at timestamptz not null default now()
);

-- ── Profiles (1:1 with a Logto user; id = Logto `sub` claim) ──────────────────
create table if not exists profiles (
  id           text primary key,                              -- Logto subject
  tenant_id    uuid references tenants(id) on delete set null,
  display_name text,
  email        text,
  avatar_url   text,
  created_at   timestamptz not null default now()
);

-- ── Roles (kept OFF the profile, in a dedicated table) ────────────────────────
do $$
begin
  create type app_role as enum ('admin', 'member', 'viewer');
exception
  when duplicate_object then null;
end $$;

create table if not exists user_roles (
  id         uuid primary key default gen_random_uuid(),
  user_id    text not null references profiles(id) on delete cascade,
  role       app_role not null,
  active     boolean not null default true,
  created_at timestamptz not null default now(),
  unique (user_id, role)
);

-- ── Demo domain table backing the Clientes screen ────────────────────────────
create table if not exists clientes (
  id         uuid primary key default gen_random_uuid(),
  tenant_id  uuid references tenants(id) on delete cascade,
  nome       text not null,
  contato    text,
  plano      text,
  status     text not null default 'Ativo',
  created_at timestamptz not null default now()
);

-- ── Helpers reading the PostgREST-injected JWT claims ─────────────────────────
create or replace function current_user_id() returns text
  language sql stable as $$
  select nullif(current_setting('request.jwt.claims', true)::json ->> 'sub', '')
$$;

-- SECURITY DEFINER (+ fixed search_path): these read RLS-protected tables, so
-- they MUST bypass RLS — otherwise the policies below that call them would
-- recurse infinitely (profiles policy -> current_tenant_id -> profiles ...).
create or replace function current_tenant_id() returns uuid
  language sql stable security definer set search_path = public as $$
  select tenant_id from profiles where id = current_user_id()
$$;

create or replace function has_role(p_role app_role) returns boolean
  language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from user_roles
    where user_id = current_user_id() and role = p_role and active
  )
$$;

-- ── usuarios view (backs the Usuários screen) ────────────────────────────────
create or replace view usuarios with (security_invoker = true) as
  select
    p.id,
    coalesce(p.display_name, p.email, 'Usuário') as nome,
    p.email,
    coalesce(
      (select ur.role::text from user_roles ur
       where ur.user_id = p.id and ur.active
       order by ur.created_at limit 1),
      'viewer'
    ) as papel,
    case
      when exists (select 1 from user_roles ur where ur.user_id = p.id and ur.active)
      then 'Ativo' else 'Inativo'
    end as status
  from profiles p;

-- ── Row Level Security ───────────────────────────────────────────────────────
alter table tenants    enable row level security;
alter table profiles   enable row level security;
alter table user_roles enable row level security;
alter table clientes   enable row level security;

drop policy if exists profiles_select on profiles;
create policy profiles_select on profiles for select
  using (id = current_user_id() or tenant_id = current_tenant_id());

drop policy if exists profiles_update on profiles;
create policy profiles_update on profiles for update
  using (id = current_user_id());

drop policy if exists user_roles_select on user_roles;
create policy user_roles_select on user_roles for select
  using (user_id = current_user_id() or has_role('admin'));

drop policy if exists user_roles_admin on user_roles;
create policy user_roles_admin on user_roles for all
  using (has_role('admin')) with check (has_role('admin'));

drop policy if exists tenants_select on tenants;
create policy tenants_select on tenants for select
  using (id = current_tenant_id());

drop policy if exists clientes_rw on clientes;
create policy clientes_rw on clientes for all
  using (tenant_id = current_tenant_id())
  with check (tenant_id = current_tenant_id());

-- ── Grants for the PostgREST roles ───────────────────────────────────────────
grant usage on schema public to anon, authenticated;
grant select on tenants, profiles to authenticated;
grant select, insert, update, delete on clientes to authenticated;
grant select, insert, update, delete on user_roles to authenticated;
grant select on usuarios to authenticated;
-- anon intentionally gets no table grants (RLS would block it regardless).
