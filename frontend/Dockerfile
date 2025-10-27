# Stage 1: Build la aplicación
FROM node:22-alpine as builder
WORKDIR /app
COPY package.json .
COPY package-lock.json .

# Instala dependencias y variables de entorno de React/Vite
# VITE_APP_API_URL se inyectará aquí desde Render
RUN npm install

# Copia el resto del código fuente (incluyendo src/)
COPY . .

# Ejecuta el comando de construcción (crea la carpeta 'dist')
# --no-tty es una buena práctica en contenedores
RUN npm run build --no-tty

# ----------------------------------------------------

# Stage 2: Servir la aplicación con Nginx
FROM nginx:stable-alpine
# Copia los archivos estáticos desde el Stage 1
COPY --from=builder /app/dist /usr/share/nginx/html

# Opcional: Copia tu archivo de configuración de Nginx si tienes uno
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
