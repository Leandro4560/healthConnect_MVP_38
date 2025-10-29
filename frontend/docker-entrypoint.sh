#!/bin/sh
set -e

# Genera /usr/share/nginx/html/env.js usando la variable BACKEND_URL en tiempo de ejecución.
# Si BACKEND_URL no está definida, dejamos window.__API_ROOT__ como cadena vacía y mostramos
# una advertencia clara en la consola del navegador para que el desarrollador la vea.
: ${BACKEND_URL:=}

# Escapar comillas en la URL (por si acaso)
escaped=$(printf '%s' "$BACKEND_URL" | sed 's/"/\\"/g')

cat > /usr/share/nginx/html/env.js <<EOF
// Este archivo es generado en tiempo de ejecución. No lo edites manualmente.
;(function(){
	var backend = "${escaped}" || "";
	window.__API_ROOT__ = backend;
	if (!backend) {
		// Warning visible en la consola del navegador para facilitar debugging en despliegues.
		console.warn("[env.js] BACKEND_URL no está configurado. El frontend hará peticiones al mismo origen (esto normalmente provoca 404).\n\nPor favor configura la variable de entorno BACKEND_URL en tu servicio frontend en Render con la URL pública de tu backend, por ejemplo:\nBACKEND_URL=https://mi-backend.onrender.com\n");
	} else {
		console.info("[env.js] BACKEND_URL configurado: ", backend);
	}
})();
EOF

# Renderizar plantilla de nginx usando BACKEND_URL (si no está definida, usamos fallback local)
# Nota: para producción debes configurar BACKEND_URL en las Environment Variables del servicio frontend
if [ -z "$BACKEND_URL" ]; then
	echo "[docker-entrypoint] WARNING: BACKEND_URL no definido; usando fallback http://127.0.0.1:8000 (esto no funcionará en producción si el backend está en otra máquina)." >&2
	export BACKEND_URL="http://127.0.0.1:8000"
fi

# Usar envsubst para generar la configuración final de nginx
if [ -f /etc/nginx/templates/default.conf.template ]; then
	echo "[docker-entrypoint] Generando /etc/nginx/conf.d/default.conf usando BACKEND_URL=$BACKEND_URL"
	envsubst '\$BACKEND_URL' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf
else
	echo "[docker-entrypoint] Plantilla de nginx no encontrada, usando configuración por defecto." >&2
fi

# Arrancar nginx en primer plano
exec nginx -g 'daemon off;'
