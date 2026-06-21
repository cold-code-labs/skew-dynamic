<!-- Official CCL web template. Keep it lean and stub-first. -->

## What & why

<!-- One or two lines. -->

## Checklist

- [ ] App still boots in **stub mode** with no backend and no required env
      (`AUTH_MODE`/`DATA_MODE` default to `stub`)
- [ ] `pnpm typecheck` passes
- [ ] `pnpm build` passes
- [ ] `docker build .` passes (or CI is green)
- [ ] New backend dependencies are **optional** (behind an env flag, with a stub
      fallback) — no new always-required env var
- [ ] Docs updated (`README.md` / `.env.example` / `db/README.md`) if behavior,
      env, or schema changed
