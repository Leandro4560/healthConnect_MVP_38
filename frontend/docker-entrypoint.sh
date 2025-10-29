#!/bin/sh
set -e

# Genera /usr/share/nginx/html/env.js usando la variable BACKEND_URL en tiempo de ejecución.
# Si BACKEND_URL no está definida, usa una cadena vacía para que el frontend caiga a window.location.origin
: ${BACKEND_URL:=}

# Escapar comillas en la URL (por si acaso)
escaped=$(printf '%s' "$BACKEND_URL" | sed 's/"/\\"/g')

cat > /usr/share/nginx/html/env.js <<EOF
// Este archivo es generado en tiempo de ejecución. No lo edites manualmente.
window.__API_ROOT__ = "${escaped}";
EOF

# Arrancar nginx en primer plano
exec nginx -g 'daemon off;'
