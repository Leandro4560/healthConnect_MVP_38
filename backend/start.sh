#!/bin/bash

# Extraer el host de la URL de la base de datos
DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\).*/\1/p')

# Si no se puede extraer el host, usar un valor por defecto
if [ -z "$DB_HOST" ]; then
    echo "WARNING: Could not extract database host from DATABASE_URL"
    DB_HOST="db.supabase.co"
fi

echo "Setting up proxy to database host: $DB_HOST"

# Iniciar socat en segundo plano para hacer proxy del tráfico de Supabase
socat TCP4-LISTEN:5432,fork TCP4:$DB_HOST:5432 &
socat TCP4-LISTEN:6543,fork TCP4:$DB_HOST:5432 &

# Esperar un momento para que socat se inicie
sleep 2

# Iniciar la aplicación
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}