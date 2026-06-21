# Contributing to template-web-coolify-light

This is the **official Cold Code Labs web template** — the base every new app on
our self-hosted stack starts from. Changes here ripple into every future app, so
the bar is: keep it small, correct, and runnable by anyone with a fresh clone.

Local checkout on ymir: `~/ccl/template-light` (symlink `~/tpl-light`).

## The golden rule: stub-first

**The template must always boot in stub mode with zero backend and zero required
env.** `AUTH_MODE` and `DATA_MODE` default to `stub`; in that mode the app uses a
one-click demo login and in-code demo data. A new contributor must be able to:

```bash
pnpm install && pnpm dev   # works immediately, no .env needed
```

Every backend integration is **optional**: behind an env flag, with a stub
fallback. Never add an always-required env var or a hard dependency on a running
service.

## Architecture you must preserve

Three thin seams — pages and components talk only to these, never to PocketBase
cookies or `fetch` directly:

- **Auth** — `lib/auth/`. Resolve users via `getSession()` (server-side). Add
  auth backends as new `AUTH_MODE` branches; keep `stub` intact.
- **Data** — `lib/data/`. Each `lib/data/<entity>.ts` returns demo data in stub
  mode and queries PocketBase when `DATA_MODE=pocketbase`. Pages are async server
  components reading through these functions.
- **Functions** — `lib/functions/invoke.ts`. Edge-runtime calls, used only when
  `FUNCTIONS_URL` is set.

Config: `config/app.ts` (client-safe identity) + `config/env.ts` (server-side
modes/URLs). All new env vars go in `config/env.ts` **and** `.env.example`, with
a comment and a safe default.

See [`docs/STACK.md`](docs/STACK.md) for the full stack map and safe evolution workflow.

## Adding a feature (the Features Library contract)

Every sidebar module is a **feature** that provisioners can toggle per
instance. When you box a new feature into the template:

1. Build it as a module: entry in `config/modules.ts` (or a `ResourceDef` in
   `config/resources.ts`), page under `app/(app)/<key>/`.
2. Gate its route: call `requireFeature("<key>")` first thing in the page's
   server component (core modules listed in `config/features.ts` skip this).
3. **Register it in `features.json`** (repo root) — key, label, description,
   group, `core` flag. This file is the machine-readable catalog Heimdall reads
   for the Ice Breaker picker and the Features Library; a feature missing here
   is invisible to provisioning.

Selection is env-driven: `APP_FEATURES` (comma-separated extra keys; unset =
everything on). Core modules are always on — keep the core list small.

## Database changes

Add a new numbered migration under `pocketbase/pb_migrations/` (e.g.
`<ts>_*.js`) — never edit an applied migration. Migrations must be idempotent.
For schema-as-code, commit migrations; for one-off tweaks, use the admin panel
at `/_/` (persists in `/pb_data`).

## Before opening a PR

```bash
pnpm typecheck      # tsc --noEmit
pnpm build          # next build (also type-checks)
docker build .      # the production image Coolify runs
```

For backend-touching changes, also verify the PocketBase path locally per
`README.md`. CI (`.github/workflows/ci.yml`) runs typecheck + build + docker
build on every PR.

## Conventions

- TypeScript strict — the build does **not** ignore type errors. Keep it that way.
- Keep the v0/shadcn UI primitives in `components/ui/` as-is unless upgrading
  them deliberately.
- Bump dependencies in their own PR and re-run the lockfile + Docker build.
