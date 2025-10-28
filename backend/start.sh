# ...existing code...
#!/usr/bin/env bash
set -euo pipefail

# Inicio sin socat. La app usará DATABASE_URL directamente (p. ej. el pooler de Supabase).
# Asegúrate de configurar DATABASE_URL en Render:
# postgresql://postgres:<PASSWORD>@aws-1-us-east-2.pooler.supabase.com:6543/postgres

echo "Starting app without socat. Using DATABASE_URL from environment."

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL no definida. Configura la variable en Render (Environment -> Environment Variables)."
  exit 1
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}" --log-level info
# ...existing code...