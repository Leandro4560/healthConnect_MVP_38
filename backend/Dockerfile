FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
# Copia requirements desde el contexto (cuando el contexto de build es la carpeta `backend`).
COPY requirements.txt .
# Instala curl (para healthcheck) y dependencias; asegura gunicorn instalado también.
RUN apt-get update \
		&& apt-get install -y --no-install-recommends curl \
		&& pip install --no-cache-dir -r requirements.txt \
		&& pip install --no-cache-dir gunicorn \
		&& rm -rf /var/lib/apt/lists/*

# Copia todo el contenido del contexto (ej. la carpeta `backend`).
COPY . .

# Healthcheck que consulta la raíz usando el puerto proporcionado en $PORT (o 8000 por defecto).
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD curl -f http://127.0.0.1:${PORT:-8000}/ || exit 1

# Render proporciona $PORT al runtime; usamos shell form para que se expanda.
EXPOSE 8000
CMD gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --workers 2
