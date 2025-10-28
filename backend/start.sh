#!/usr/bin/env bash
set -euo pipefail

echo "Starting app (no socat). Using DATABASE_URL if definida, si no SQLite local."

if [ -n "${DB_PROVIDER:-}" ] && [ "${DB_PROVIDER}" = "sqlite" ]; then
  echo "DB_PROVIDER=sqlite (forzando SQLite local)."
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}" --log-level info