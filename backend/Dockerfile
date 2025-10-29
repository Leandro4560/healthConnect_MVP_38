FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
# Copia requirements desde el contexto (cuando el contexto de build es la carpeta `backend`).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copia todo el contenido del contexto (ej. la carpeta `backend`).
COPY . .
# Render proporciona $PORT al runtime; usamos shell form para que se expanda.
EXPOSE 8000
CMD gunicorn -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:$PORT --workers 2
