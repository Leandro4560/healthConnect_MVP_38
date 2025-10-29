#!/usr/bin/env bash
set -euo pipefail

echo "Starting app (socat optional). Using DATABASE_URL if definida, si no SQLite local."

# Detectar socat
SOCAT_CMD="$(command -v socat || true)"
SOCAT_PIDS=()

REMOTE_HOST="${DB_HOST:-aws-1-us-east-2.pooler.supabase.com}"
REMOTE_PORT="${DB_PORT:-5432}"

if [ -n "$SOCAT_CMD" ]; then
  echo "Launching socat listeners (local 5432 and 6543 -> ${REMOTE_HOST}:${REMOTE_PORT})"
  "$SOCAT_CMD" TCP4-LISTEN:5432,fork,reuseaddr TCP4:${REMOTE_HOST}:${REMOTE_PORT} &
  SOCAT_PIDS+=($!)
  "$SOCAT_CMD" TCP4-LISTEN:6543,fork,reuseaddr TCP4:${REMOTE_HOST}:${REMOTE_PORT} &
  SOCAT_PIDS+=($!)
  # dar tiempo a inicializar
  sleep 2
else
  echo "socat not found; skipping proxy listeners. To enable, install socat in the image."
fi

# Reescribir DATABASE_URL solo si está definida y es postgres remoto
if [ -n "${DATABASE_URL:-}" ]; then
  if echo "$DATABASE_URL" | grep -Eqi '^postgres(ql)?://' && ! echo "$DATABASE_URL" | grep -Eqi '@(localhost|127\.0\.0\.1)'; then
    PROXIED_DB_URL=$(echo "$DATABASE_URL" | sed -E 's#^(postgresql?://[^@]+@)[^:/]+(:[0-9]+)?/#\1localhost:6543/#')
    export DATABASE_URL="$PROXIED_DB_URL"
    echo "Using proxied DATABASE_URL: ${DATABASE_URL}"
  else
    echo "DATABASE_URL already points to localhost or is not postgres. No rewrite applied."
  fi
else
  echo "DATABASE_URL not set; ensure DATABASE_URL is configured or the app will use local SQLite."
fi

cleanup() {
  echo "Stopping socat..."
  for pid in "${SOCAT_PIDS[@]:-}"; do
    kill "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT

# Ejecutar la app
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}"