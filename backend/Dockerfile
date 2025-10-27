# 1. IMAGEN BASE: Usa Python 3.11 en su versión slim (más ligera)
FROM python:3.11-slim

# 2. WORKDIR: Establece /app como el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. DEPENDENCIAS: Copia el archivo requirements.txt e instala las dependencias.
#    Asegúrate de que 'supabase' esté en este archivo para evitar el error 'ModuleNotFoundError'.
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 4. CÓDIGO: Copia todo el código restante de la carpeta 'backend' al contenedor
COPY . /app

# 5. COMANDO DE INICIO (CMD): Ejecuta Uvicorn.
#    Usa la variable de entorno $PORT (inyectada por Render) y un valor por defecto (8000).
#    Asegúrate de que 'app.main:app' sea la ruta correcta a tu objeto FastAPI.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
