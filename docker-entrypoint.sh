#!/bin/sh
set -e

PB_DATA_DIR="${PB_DATA_DIR:-/pb_data}"

# Optional superuser (admin /_/) bootstrap. `upsert` is idempotent.
if [ -n "$PB_SUPERUSER_EMAIL" ] && [ -n "$PB_SUPERUSER_PASSWORD" ]; then
  echo "[entrypoint] upserting PocketBase superuser: $PB_SUPERUSER_EMAIL"
  pocketbase superuser upsert "$PB_SUPERUSER_EMAIL" "$PB_SUPERUSER_PASSWORD" \
    --dir "$PB_DATA_DIR" || echo "[entrypoint] superuser upsert failed (continuing)"
fi

# Start PocketBase. It binds 0.0.0.0:8090 so the admin panel + API CAN be
# exposed on a separate domain (e.g. data-<app>.coldcodelabs.com), but exposure
# is opt-in: it's only public if Coolify maps a domain to port 8090. With no
# such domain, Traefik never routes it and PB stays reachable only in-container
# (the Next app always talks to it over 127.0.0.1). Migrations in
# /pb_migrations are applied automatically on serve.
echo "[entrypoint] starting PocketBase…"
pocketbase serve \
  --http=0.0.0.0:8090 \
  --dir="$PB_DATA_DIR" \
  --migrationsDir=/pb/pb_migrations \
  --hooksDir=/pb/pb_hooks &

# Wait for PocketBase to answer before starting the app.
echo "[entrypoint] waiting for PocketBase health…"
i=0
while [ "$i" -lt 30 ]; do
  if wget -qO- http://127.0.0.1:8090/api/health >/dev/null 2>&1; then
    echo "[entrypoint] PocketBase is up"
    break
  fi
  i=$((i + 1))
  sleep 1
done

# Start the Next.js standalone server in the foreground.
echo "[entrypoint] starting Next.js…"
exec node server.js
