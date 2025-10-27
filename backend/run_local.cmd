@echo off
REM Script para crear (si hace falta) el venv e iniciar uvicorn desde cmd.exe
REM Ejecutar desde la carpeta backend o con la ruta completa.
cd /d %~dp0
n
if not exist venv (
  echo Creando virtualenv venv...
  python -m venv venv
  echo Actualizando pip y herramientas...
  venv\Scripts\python -m pip install --upgrade pip setuptools wheel
  if exist requirements.txt (
    echo Instalando dependencias desde requirements.txt...
    venv\Scripts\python -m pip install -r requirements.txt
  )
)

echo Iniciando servidor uvicorn en http://localhost:8000 ...
venv\Scripts\python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
