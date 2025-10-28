#!/usr/bin/env bash
set -euo pipefail

echo "Starting app without socat. Using DATABASE_URL from environment."

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL no definida. Configura la variable en Render (Environment -> Environment Variables)."
  exit 1
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}" --log-level info