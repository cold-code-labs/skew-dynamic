#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# pb-dev.sh — roda o PocketBase desta instância localmente.
#
# Mesmo binário + versão + migrations + hooks da produção, contra um sandbox
# local ./pb_data (gitignored). O ponto: mudanças de schema no Admin UI (/_/)
# viram arquivos de migration em pocketbase/pb_migrations — commit + push e o
# backend ao vivo aplica no próximo deploy (`pocketbase serve --migrationsDir`).
#
#   pnpm pb:dev                      # → http://127.0.0.1:8090/_/
#   PB_PORT=8091 pnpm pb:dev         # outra porta
#   PB_VERSION=0.39.3 pnpm pb:dev    # fixar versão (default = a da produção)
#
# Nota: a variável da porta é PB_PORT (NUNCA PORT) para não colidir com a env
# PORT que ferramentas externas (preview/CI) injetam para o app.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

PB_VERSION="${PB_VERSION:-0.39.3}"   # manter em sync com o ARG do Dockerfile
PB_PORT="${PB_PORT:-8090}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN_DIR="$ROOT/.pb"
BIN="$BIN_DIR/pocketbase"
DATA_DIR="$ROOT/pb_data"

# Resolve o asset do release p/ este OS/arch.
os="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "$os" in
  linux)  OS=linux ;;
  darwin) OS=darwin ;;
  *) echo "✗ OS não suportado pelo pb:dev: $os (rode o PocketBase à mão)"; exit 1 ;;
esac
arch="$(uname -m)"
case "$arch" in
  x86_64|amd64)   ARCH=amd64 ;;
  arm64|aarch64)  ARCH=arm64 ;;
  *) echo "✗ arquitetura não suportada: $arch"; exit 1 ;;
esac

# Baixa uma vez (cache em .pb/), re-baixa se a versão não bater.
if [ ! -x "$BIN" ] || ! "$BIN" --version 2>/dev/null | grep -q "$PB_VERSION"; then
  echo "→ baixando PocketBase $PB_VERSION ($OS/$ARCH)…"
  mkdir -p "$BIN_DIR"
  url="https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_${OS}_${ARCH}.zip"
  tmp="$(mktemp -d)"
  curl -fsSL "$url" -o "$tmp/pb.zip"
  # Extrai com unzip se houver; senão cai pro python3 (quase sempre presente).
  if command -v unzip >/dev/null 2>&1; then
    unzip -oq "$tmp/pb.zip" -d "$BIN_DIR"
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$tmp/pb.zip" "$BIN_DIR"
  else
    echo "✗ preciso de 'unzip' ou 'python3' pra extrair o PocketBase"; rm -rf "$tmp"; exit 1
  fi
  chmod +x "$BIN"
  rm -rf "$tmp"
fi

# Bootstrap de um admin local p/ o /_/ (idempotente; defaults SÓ p/ dev local).
EMAIL="${PB_SUPERUSER_EMAIL:-admin@local.dev}"
PASS="${PB_SUPERUSER_PASSWORD:-admin1234567}"
"$BIN" superuser upsert "$EMAIL" "$PASS" --dir "$DATA_DIR" >/dev/null 2>&1 || true

echo "→ PocketBase $PB_VERSION em http://127.0.0.1:$PB_PORT/_/"
echo "  admin local: $EMAIL / $PASS"
echo "  migrations:  pocketbase/pb_migrations   (mudanças no /_/ viram arquivos aqui)"
echo "  dados:       ./pb_data                  (gitignored — sandbox local)"
exec "$BIN" serve \
  --http="127.0.0.1:$PB_PORT" \
  --dir="$DATA_DIR" \
  --migrationsDir="$ROOT/pocketbase/pb_migrations" \
  --hooksDir="$ROOT/pocketbase/pb_hooks"
