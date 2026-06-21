# Stack — template-web-coolify-light

Canonical Cold Code Labs **light tier**: one Next.js app + PocketBase embedded in
one Docker container.

## Layout

```
┌──────────────────────────── one container ────────────────────────────┐
│  Next.js (port 3000, public)  ──localhost──▶  PocketBase (8090, data)  │
│         the app / the UI                       auth + DB, admin /_/     │
└──────────────────────────────────────── /pb_data volume ──────────────┘
```

| Concern | Stub (default) | Production |
| ------- | -------------- | ---------- |
| Auth | demo cookie login | `AUTH_MODE=pocketbase` |
| Data | in-code demo rows | `DATA_MODE=pocketbase` |
| Storage | — | PocketBase file fields |
| Deploy | — | Coolify Dockerfile on `*.coldcodelabs.com` |

## Repo vs local checkout

| | |
| --- | --- |
| **GitHub repo** | `cold-code-labs/template-web-coolify-light` (`is_template`) |
| **ymir checkout** | `~/ccl/template-light` (symlink `~/tpl-light`) |
| **Ice Breaker** | Generates a new repo from the GitHub template per instance |

Instâncias Ice Breaker (arte-one, zyramed, …) são **repos próprios** no GitHub —
não herdam mudanças do template automaticamente.

## Seams (do not bypass)

- `lib/auth/` — `getSession()`, `app/api/auth/*`
- `lib/data/` — per-entity readers; `lib/data/client.ts` for `pbServer()` / `pbAdmin()`
- `lib/functions/invoke.ts` — optional edge-runtime
- `config/env.ts` + `.env.example` — every new env var

## Feature modules

- Catalog: `features.json` (root)
- Runtime gate: `APP_FEATURES` env (unset = showroom completo)
- Core list: `config/features.ts` (always on)
- Ice Breaker reads `features.json` via GitHub API for the picker

## Safe evolution workflow

1. **Develop** in `~/ccl/template-light` on a branch → PR → merge `main`.
2. **Validate** on a live test instance (`arte-one` or `logcheck.coldcodelabs.com`).
3. **New instances** — Ice Breaker provisions from the GitHub template at merge time.
4. **Existing instances** — merge template changes into their repo + redeploy via Coolify
   (or use Heimdall Fleet → Clonar for a fresh checkout).

## Archived templates

These GitHub repos are **archived** and must not be used for new apps:

- `cold-code-labs/template-web` (v0 scaffold)
- `cold-code-labs/template-web-coolify` (Logto + PostgREST à-la-carte)

## Persistence

All PocketBase state lives in `/pb_data`. Coolify must mount a persistent volume
there. Ice Breaker does this automatically for new instances.

## Admin panel

Optional second domain: `data-<sub>.coldcodelabs.com:8090` (behind Cloudflare Access).
Use `pb.sh` with `~/.pb_admin_cli_token` or Heimdall Fleet → Abrir Studio.
