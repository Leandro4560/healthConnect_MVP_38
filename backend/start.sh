#!/usr/bin/env bash
set -euo pipefail

echo "Starting app (no socat). Using DATABASE_URL si está definida o SQLite local por defecto."

if [ -n "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL presente."
else
  echo "DATABASE_URL no definida. Usando SQLite local (/data/dev.db)."
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}" --log-level info