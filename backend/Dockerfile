FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend
# Render proporciona $PORT al runtime; usamos shell form para que se expanda.
EXPOSE 8000
CMD gunicorn -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:$PORT --workers 2
