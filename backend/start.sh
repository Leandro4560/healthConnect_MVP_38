#!/bin/bash

# Iniciar socat en segundo plano para hacer proxy del tráfico de Supabase
socat TCP4-LISTEN:5432,fork TCP4:db.aws-1-us-east-2.supabase.co:5432 &
socat TCP4-LISTEN:6543,fork TCP4:db.aws-1-us-east-2.supabase.co:5432 &

# Esperar un momento para que socat se inicie
sleep 2

# Iniciar la aplicación
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}