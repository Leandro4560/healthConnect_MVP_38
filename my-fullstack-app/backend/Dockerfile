FROM python:3.11-slim

WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Usar $PORT para que Cloud Run inyecte el 8080 (o cualquier otro si se cambia).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]