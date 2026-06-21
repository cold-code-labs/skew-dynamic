# Database — vanilla Postgres + PostgREST

The app reaches data through **PostgREST**, never connecting to Postgres
directly. This folder bootstraps a fresh database for that stack.

## Apply

```bash
export DATABASE_URL=postgres://postgres:postgres@localhost:5432/app

pnpm db:migrate   # runs every db/migrations/*.sql in order
pnpm db:seed      # optional demo data
```

> Run migrations as a **superuser** the first time — `0001_init.sql` creates the
> `anon` and `authenticated` roles PostgREST needs.

## What `0001_init.sql` sets up

- `tenants`, `profiles` (`id` = Logto `sub`), `app_role` enum + `user_roles`
  (roles kept off the profile), and a demo `clientes` table.
- `usuarios` view (profiles ⨝ user_roles) backing the Usuários screen.
- Claim helpers: `current_user_id()`, `current_tenant_id()`, `has_role()` —
  they read `request.jwt.claims` injected by PostgREST.
- RLS on every table + grants for the `authenticated` role.

## Wiring PostgREST

Point PostgREST at the same database and configure it to trust Logto's JWTs:

```
PGRST_DB_URI=postgres://authenticator:...@db:5432/app
PGRST_DB_SCHEMAS=public
PGRST_DB_ANON_ROLE=anon
PGRST_JWT_SECRET={ "jwks_uri": "https://logto.coldcodelabs.com/oidc/jwks" }
```

Then set `DATA_MODE=postgrest` and `DATA_API_URL` in the app's env. The JWT must
carry a `role` claim of `authenticated` (map it in Logto, or via a PostgREST
pre-request hook) so RLS applies.
