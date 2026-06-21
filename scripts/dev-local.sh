#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# dev-local.sh — UM comando pra rodar tudo local: PocketBase + o app Next.
#
#   pnpm dev:local
#
# Instala deps se faltarem, sobe o PocketBase local (pb-dev.sh) em background,
# espera o health, e roda o app em foreground forçando APP_ENV=dev (→ aponta
# pro PB local). Mata o PocketBase ao sair (trap). Para mexer no remoto, use
# `APP_ENV=PRD pnpm dev`.
#
# A porta interna do PocketBase é PB_PORT (NUNCA PORT) — assim a env PORT que
# ferramentas externas injetam fica reservada pro app.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PB_PORT="${PB_PORT:-8090}"

# Deps (clone limpo): instala se faltar.
bash "$ROOT/scripts/ensure-deps.sh"

# Sobe o PocketBase em background.
bash "$ROOT/scripts/pb-dev.sh" &
PB_PID=$!

# Garante que o PocketBase morre quando este script terminar (saída/Ctrl-C).
cleanup() { kill "$PB_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

# Espera o PocketBase ficar saudável antes de subir o app.
echo "→ aguardando PocketBase em :$PB_PORT…"
for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:$PB_PORT/api/health" >/dev/null 2>&1; then
    echo "✓ PocketBase up"
    break
  fi
  sleep 1
done

# App em foreground (APP_ENV=dev → fala com o PB local). Honra PORT se injetada.
echo "→ subindo o app (APP_ENV=dev) em http://localhost:${PORT:-3000}"
APP_ENV=dev pnpm dev
