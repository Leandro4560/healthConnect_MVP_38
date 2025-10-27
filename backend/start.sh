#!/bin/bash

# Determinar el host de la base de datos.
# Prioridad: SUPABASE_DB_HOST (opcional) -> extraído desde DATABASE_URL -> fallback genérico
if [ -n "$SUPABASE_DB_HOST" ]; then
        DB_HOST="$SUPABASE_DB_HOST"
else
        DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\).*/\1/p')
fi

if [ -z "$DB_HOST" ]; then
        echo "WARNING: Could not extract database host from DATABASE_URL and SUPABASE_DB_HOST not set"
        DB_HOST="db.supabase.co"
fi

DB_PORT=5432

echo "Setting up proxy to database host: $DB_HOST:$DB_PORT"

# Función para probar conectividad TCP al host:puerto usando /dev/tcp
test_tcp() {
    timeout=2
    (echo > /dev/tcp/$1/$2) >/dev/null 2>&1
}

# Esperar hasta que el upstream acepte conexiones (retries con backoff)
max_checks=12
for i in $(seq 1 $max_checks); do
    echo "Checking TCP $DB_HOST:$DB_PORT (attempt $i/$max_checks)"
    if test_tcp "$DB_HOST" "$DB_PORT"; then
        echo "Host $DB_HOST:$DB_PORT is reachable"
        break
    fi
    sleep 2
done

if ! test_tcp "$DB_HOST" "$DB_PORT"; then
    echo "WARNING: $DB_HOST:$DB_PORT not reachable after $max_checks attempts. Socat will still be started but connections may fail."
fi

# Iniciar socat en segundo plano para hacer proxy del tráfico de Supabase
echo "Launching socat listeners (local 5432 and 6543 -> $DB_HOST:$DB_PORT)"
socat TCP4-LISTEN:5432,fork TCP4:$DB_HOST:$DB_PORT &
socat TCP4-LISTEN:6543,fork TCP4:$DB_HOST:$DB_PORT &

# Esperar un momento para que socat se inicie
sleep 2

# Iniciar la aplicación
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}