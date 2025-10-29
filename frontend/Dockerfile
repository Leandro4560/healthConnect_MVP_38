# Stage 1: Build la aplicación
FROM node:20-alpine AS builder
WORKDIR /app
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
COPY package*.json ./
RUN npm ci
# Copia todo el contexto de build (cuando el contexto es la carpeta `frontend`).
COPY . ./
RUN npm run build

# ----------------------------------------------------

# Stage 2: Servir la aplicación con Nginx
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# copia entrypoint que genera env.js con la URL del backend
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
# instalar envsubst (gettext) para renderizar plantillas de nginx en tiempo de arranque
RUN apk add --no-cache gettext
# copia la plantilla nginx
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 80
# Start script will generate /usr/share/nginx/html/env.js using BACKEND_URL env var
ENTRYPOINT ["/docker-entrypoint.sh"]
