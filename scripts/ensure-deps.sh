#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# ensure-deps.sh — garante node_modules antes de rodar o app. Idempotente:
# não faz nada se as deps já estão instaladas. Elimina o "next: command not
# found" num clone limpo / preview / CI.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Já instalado? (checa o binário do Next, não só a pasta.)
if [ -x "$ROOT/node_modules/.bin/next" ]; then
  exit 0
fi

echo "→ node_modules ausente — instalando dependências…"
cd "$ROOT"

# pnpm via corepack (não falha o script se o corepack não puder habilitar).
if ! command -v pnpm >/dev/null 2>&1; then
  corepack enable >/dev/null 2>&1 || true
fi

pnpm install --frozen-lockfile
