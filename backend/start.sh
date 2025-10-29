#!/usr/bin/env bash
set -e

# REMOTE DB host/port (puedes dejar vacíos y usar DATABASE_URL desde Render)
REMOTE_HOST="${DB_HOST:-aws-1-us-east-2.pooler.supabase.com}"
REMOTE_PORT="${DB_PORT:-5432}"

echo "Launching socat listeners (local 5432 and 6543 -> ${REMOTE_HOST}:${REMOTE_PORT})"
# lanzar listeners en background
socat TCP4-LISTEN:5432,fork,reuseaddr TCP4:${REMOTE_HOST}:${REMOTE_PORT} &
SOCAT_PID1=$!
socat TCP4-LISTEN:6543,fork,reuseaddr TCP4:${REMOTE_HOST}:${REMOTE_PORT} &
SOCAT_PID2=$!

# Esperar que socat esté listo
sleep 2

# Reescribir DATABASE_URL para que apunte a localhost:6543 (si es postgres y no apunta ya a localhost)
if [ -n "${DATABASE_URL:-}" ]; then
  if echo "$DATABASE_URL" | grep -Eqi '^postgres(ql)?://' && ! echo "$DATABASE_URL" | grep -Eqi '@(localhost|127\.0\.0\.1)'; then
    PROXIED_DB_URL=$(echo "$DATABASE_URL" | sed -E 's#^(postgresql?://[^@]+@)[^:/]+(:[0-9]+)?/#\1localhost:6543/#')
    export DATABASE_URL="$PROXIED_DB_URL"
    echo "Using proxied DATABASE_URL: ${DATABASE_URL}"
  else
    echo "DATABASE_URL already points to localhost or is not a postgres URL. No rewrite applied."
  fi
else
  echo "DATABASE_URL no está definida; por favor define DATABASE_URL en Render."
fi

# Trap para detener socat al terminar
cleanup() {
  echo "Stopping socat..."
  kill ${SOCAT_PID1:-} ${SOCAT_PID2:-} 2>/dev/null || true
}
trap cleanup EXIT

# Iniciar la app (ajusta si tu comando es diferente)
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}