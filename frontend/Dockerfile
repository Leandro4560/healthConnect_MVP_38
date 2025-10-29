# Stage 1: Build la aplicación
FROM node:20-alpine AS builder
WORKDIR /app
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ----------------------------------------------------

# Stage 2: Servir la aplicación con Nginx
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# copia archivo nginx.conf si necesitas rewrite/spa fallback
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
