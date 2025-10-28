#!/usr/bin/env bash
set -euo pipefail

echo "Starting app without socat. Using DATABASE_URL from environment."

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL no definida. Configura la variable en Render (Environment -> Environment Variables)."
  exit 1
fi

# Iniciar socat para proxear la BD de Supabase (remoto) a localhost
# Se exponen dos listeners locales por compatibilidad: 5432 y 6543 -> REMOTE_HOST:REMOTE_PORT
REMOTE_HOST="${DB_HOST:-aws-1-us-east-2.pooler.supabase.com}"
REMOTE_PORT="${DB_PORT:-5432}"

echo "Launching socat listeners (local 5432 and 6543 -> ${REMOTE_HOST}:${REMOTE_PORT})"
socat TCP4-LISTEN:5432,fork,reuseaddr TCP4:${REMOTE_HOST}:${REMOTE_PORT} &
SOCAT_PID1=$!
socat TCP4-LISTEN:6543,fork,reuseaddr TCP4:${REMOTE_HOST}:${REMOTE_PORT} &
SOCAT_PID2=$!

# Esperar un momento para que socat esté escuchando
sleep 2

# Reescribir DATABASE_URL para usar el proxy local en el puerto 6543 si aún no apunta a localhost
if [ -n "$DATABASE_URL" ]; then
  if echo "$DATABASE_URL" | grep -Eqi '^postgres(ql)?://' && ! echo "$DATABASE_URL" | grep -Eqi '@(localhost|127\.0\.0\.1)'; then
    PROXIED_DB_URL=$(echo "$DATABASE_URL" | sed -E 's#^(postgresql?://[^@]+@)[^:/]+(:[0-9]+)?/#\1localhost:6543/#')
    export DATABASE_URL="$PROXIED_DB_URL"
    echo "Using proxied DATABASE_URL: ${DATABASE_URL}"
  else
    echo "DATABASE_URL already points to localhost or is not a postgres URL. No rewrite applied."
  fi
else
  echo "DATABASE_URL not set; ensure Render environment variable DATABASE_URL está configurada."
fi

# Opcional: trap para matar socat al terminar
cleanup() {
  echo "Stopping socat..."
  kill ${SOCAT_PID1} ${SOCAT_PID2} 2>/dev/null || true
}
trap cleanup EXIT

# Iniciar la aplicación (ajusta comando si usa otro)
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}