-- seed.sql — minimal demo data. Matches the stub identity (usr_demo) and the
-- DEFAULT_TENANT_ID zero-uuid, so AUTH_MODE=logto + DATA_MODE=postgrest line up
-- with the demo content out of the box. Safe to re-run.

insert into tenants (id, name) values
  ('00000000-0000-0000-0000-000000000000', 'Template Tenant')
on conflict (id) do nothing;

insert into profiles (id, tenant_id, display_name, email) values
  ('usr_demo', '00000000-0000-0000-0000-000000000000', 'Alex Morgan', 'alex@template.app')
on conflict (id) do nothing;

insert into user_roles (user_id, role) values
  ('usr_demo', 'admin')
on conflict (user_id, role) do nothing;

insert into clientes (tenant_id, nome, contato, plano, status) values
  ('00000000-0000-0000-0000-000000000000', 'Acme Corp',  'maria@acme.com',     'Enterprise', 'Ativo'),
  ('00000000-0000-0000-0000-000000000000', 'Globex',     'joao@globex.com',    'Pro',        'Ativo'),
  ('00000000-0000-0000-0000-000000000000', 'Initech',    'ana@initech.com',    'Pro',        'Inativo'),
  ('00000000-0000-0000-0000-000000000000', 'Umbrella',   'carlos@umbrella.com','Starter',    'Ativo')
on conflict do nothing;
