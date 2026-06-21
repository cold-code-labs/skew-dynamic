# template-web-coolify-light

> **Cold Code Labs — "light" tier web template.** One repo, **one 1-click Coolify
> deploy** that brings up a working app **with its own database and domain**.

This is the **canonical Cold Code Labs web template** (the former à-la-carte
`template-web-coolify` stack is **archived** on GitHub). Instead of Logto +
PostgREST + Postgres it bundles a single **[PocketBase](https://pocketbase.io)** backend
**inside the same container**: auth + database in one ~30 MB Go binary on SQLite.

```
┌──────────────────────────── one container ────────────────────────────┐
│  Next.js (port 3000, public)  ──localhost──▶  PocketBase (8090, data)  │
│         the app / the UI                       auth + DB, admin /_/     │
└──────────────────────────────────────── /pb_data volume ──────────────┘
```

The **app** is what users see on the domain. **PocketBase is data-only** — the
browser never talks to it; the Next.js server reads it over localhost through
the same `lib/auth` / `lib/data` seams as the full template. The admin panel at
`/_/` is for you (login-gated), not for end users.

**Use this for:** internal tools / ops dashboards, ≤ ~20 users, one app per
client, no realtime/pgvector needs. For Postgres-grade multi-app SSO, use an
external stack — the legacy à-la-carte template is archived.

## Showroom out of the box

A fresh deploy comes up as a **complete, populated internal platform** — every
module is on and seeded with demo data so you can walk a client through the
whole thing, then prune to what they want. Modules included:

- **Dashboard** · **Clientes** · **Financeiro** · **Projetos** · **Suporte** —
  searchable tables with create/edit/delete (the generic *resource* engine).
- **Arquivos** — file storage by category (PocketBase native files).
- **Acessos** — team members + a roles/permissions matrix.

Everything is multi-tenant-capable but ships **single-tenant** (the org concept
stays invisible until you flip `MULTI_TENANT=true`).

## Make it yours (the few things you change per project)

| Want to change…        | Edit this                                              |
| ---------------------- | ----------------------------------------------------- |
| **Name / logo / tagline** | [`config/brand.ts`](config/brand.ts) (or `NEXT_PUBLIC_APP_NAME`) |
| **Color** (whole app)  | `BRAND.theme` in [`config/brand.ts`](config/brand.ts) or `NEXT_PUBLIC_THEME` — `neutral · indigo · emerald · violet · amber · rose` |
| **Core business** (screens, columns, fields, demo data) | [`config/resources.ts`](config/resources.ts) — one block per module |
| **Which modules show** | flip `enabled` in [`config/modules.ts`](config/modules.ts), or delete a block from `config/resources.ts` |
| **Roles & permissions** | [`config/roles.ts`](config/roles.ts) |

### Add a custom module (e.g. "Financeiro", "Estoque")

Most modules are just a declaration. Copy a block in `config/resources.ts`,
rename the fields, and add a 3-line page under `app/(app)/<key>/page.tsx`:

```tsx
import { ResourcePage } from "@/components/resource/resource-page"
import { estoque } from "@/config/resources"
export default function EstoquePage() {
  return <ResourcePage def={estoque} />
}
```

Then add the matching PocketBase collection + seed in a new
`pocketbase/pb_migrations/<ts>_*.js` (mirror `1749480000_modules.js`). In stub
mode (`DATA_MODE=stub`) the `stub` rows render with zero backend.

## Deploy (Coolify, 1-click)

1. Generate a repo from this template.
2. New application → build pack **Dockerfile** → from your repo.
3. **Port `3000`**, domain `https://<name>.coldcodelabs.com`.
4. Add a **persistent volume** mounted at **`/pb_data`** (or PocketBase data is
   lost on every redeploy).
5. Env: `AUTH_MODE=pocketbase`, `DATA_MODE=pocketbase`,
   `APP_BASE_URL=https://<name>.coldcodelabs.com`, `NEXT_PUBLIC_APP_NAME=<Name>`.
   Optionally `PB_SUPERUSER_EMAIL` / `PB_SUPERUSER_PASSWORD` for the admin panel.
6. Deploy. The app is live on the domain; log in with the seeded demo user
   (`demo@coldcodelabs.com` / `snowdemo123`) and manage data at `/_/`.

The wildcard `*.coldcodelabs.com` tunnel route maps straight to port 3000 — no
Cloudflare step. `/api/health` is the healthcheck.

### Optional: expose the PocketBase admin panel

PocketBase listens on `0.0.0.0:8090` but is only reachable in-container unless
you map a domain to it. To get the admin panel + API on its own host, add the
container port and a second domain (the app stays on the main domain):

- `ports_exposes = "3000,8090"`
- `domains = "https://<app>.coldcodelabs.com:3000,https://data-<app>.coldcodelabs.com:8090"`

Then the admin panel is at `https://data-<app>.coldcodelabs.com/_/`
(superuser-gated). The `data-<app>` host stays on the `*.coldcodelabs.com`
wildcard (one label) — no extra Cloudflare step. Note this exposes the whole
PocketBase API on that host (rule-gated), not just `/_/`.

## Local development

**Um comando, sem `.env`** (modo demo zero-config — também é o que o Preview do
Claude Code roda, via `.claude/launch.json` → `scripts/dev-preview.sh`):

```bash
pnpm preview      # instala deps se faltar, sobe PocketBase + Next, abre o login demo
                  # honra a porta injetada via $PORT (autoPort do Preview)
```

Outras formas:

```bash
pnpm install
pnpm dev          # só o app (auto-instala deps via predev) — stub mode, no backend
pnpm dev:local    # app + PocketBase local num comando (porta 3000)

# Full path (app + bundled PocketBase), the way Coolify runs it:
docker build -t twcl-light .
docker run --rm -p 3000:3000 -v "$PWD/pb_data:/pb_data" \
  -e AUTH_MODE=pocketbase -e DATA_MODE=pocketbase \
  -e PB_SUPERUSER_EMAIL=admin@example.com -e PB_SUPERUSER_PASSWORD=change-me \
  twcl-light
# → app on http://127.0.0.1:3000 , admin on http://127.0.0.1:3000/_/
```

## How the PocketBase mode works

- **Auth** — `lib/auth/pocketbase.ts`: email/password against PocketBase's
  `users` auth collection; token in the standard `pb_auth` httpOnly cookie.
  `getSession()` resolves it server-side. Login is a real form (`AUTH_MODE`
  branch in `app/login`).
- **Data** — `lib/data/<entity>.ts` reads PocketBase collections via the SDK
  when `DATA_MODE=pocketbase` (stub data otherwise — the template still boots
  with no backend).
- **Schema + seed** — `pocketbase/pb_migrations/*.js`. PocketBase applies these
  on boot, creating the `clientes` / `usuarios` collections + demo data + the
  demo login user. Edit collections in `/_/` (persists in `/pb_data`) or commit
  migrations for schema-as-code.
- **Custom backend logic** — add JS hooks in `pocketbase/pb_hooks/` (keeps it
  one binary; no need for PocketBase's Go "extend as framework" mode).

## ⚠️ Persistence

All PocketBase state (DB, schema, files, settings) lives in **`/pb_data`** —
mount a persistent volume there. The Ice Breaker factory does this automatically.

## Bumping PocketBase

Edit `ARG PB_VERSION` in the `Dockerfile`; review the
[changelog](https://github.com/pocketbase/pocketbase/releases) before bumping.
