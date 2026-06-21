#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# dev-preview.sh — entrypoint ÚNICO para o Preview do Claude Code / CI / agente.
#
# Lançado pelo .claude/launch.json (config "dev"). O Preview é DONO do processo:
# ele escolhe a porta e injeta via $PORT, e lê o "ready" do stdout do Next.
#
# A partir de um clone limpo, SEM .env e SEM passo manual, este script:
#   1. instala deps se node_modules faltar;
#   2. roda o Next na PORTA INJETADA ($PORT) em modo demo zero-config
#      (APP_ENV=dev, AUTH_MODE=stub → login demo 1-clique, dados in-code);
#   3. sobe o PocketBase em background SÓ quando o app realmente vai usá-lo
#      (DATA_MODE/AUTH_MODE=pocketbase) — em modo demo (stub) o PB é dispensável,
#      então não pagamos download/serve à toa. Quando sobe, espera o /api/health.
#
# O Next roda como filho (não `exec`) e via binário local direto (APP_PID = o
# próprio processo Next). O handler de sinal mata Next + PocketBase e dá exit,
# então o cleanup é confiável em qualquer forma de parada (EXIT/INT/TERM).
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PORT="${PORT:-3000}"        # porta do app — injetada pelo Preview (autoPort)
PB_PORT="${PB_PORT:-8090}"  # porta do PocketBase — NUNCA colide com $PORT

PB_PID=""
APP_PID=""
cleanup() {
  trap - EXIT INT TERM
  [ -n "$APP_PID" ] && kill "$APP_PID" 2>/dev/null || true
  [ -n "$PB_PID" ] && kill "$PB_PID" 2>/dev/null || true
}
trap 'cleanup; exit 143' INT TERM
trap cleanup EXIT

# 1) Dependências (clone limpo / preview / CI).
bash "$ROOT/scripts/ensure-deps.sh"

# 2) Defaults de demo zero-config (sobrescrevíveis por env). Em stub o /login
#    mostra o "Entrar com um clique" e o dashboard usa dados demo in-code — sem
#    depender de backend, então o preview SEMPRE renderiza.
export APP_ENV="${APP_ENV:-dev}"
export AUTH_MODE="${AUTH_MODE:-stub}"
export DATA_MODE="${DATA_MODE:-stub}"
export DEMO_LOGIN="${DEMO_LOGIN:-true}"

# 3) PocketBase em background — somente se o app for usá-lo (modo pocketbase).
#    No preview demo (stub) pulamos: menos download, menos dependência, menos
#    superfície de falha. O app demo não depende do PB.
if [ "$AUTH_MODE" = "pocketbase" ] || [ "$DATA_MODE" = "pocketbase" ]; then
  bash "$ROOT/scripts/pb-dev.sh" >/tmp/pb-preview.log 2>&1 &
  PB_PID=$!
  echo "→ aguardando PocketBase em :$PB_PORT…"
  for _ in $(seq 1 30); do
    if curl -fsS "http://127.0.0.1:$PB_PORT/api/health" >/dev/null 2>&1; then
      echo "✓ PocketBase up"
      break
    fi
    sleep 1
  done
else
  echo "→ modo demo (AUTH_MODE=$AUTH_MODE, DATA_MODE=$DATA_MODE): PocketBase não é necessário."
fi

echo "→ subindo o Next em http://127.0.0.1:$PORT (APP_ENV=$APP_ENV, AUTH_MODE=$AUTH_MODE, DATA_MODE=$DATA_MODE)"
# Honra a porta injetada — NUNCA porta fixa. Binário local direto → APP_PID é o
# próprio Next (sem wrapper pnpm), então o cleanup o mata de forma confiável.
"$ROOT/node_modules/.bin/next" dev -p "$PORT" &
APP_PID=$!
wait "$APP_PID"
