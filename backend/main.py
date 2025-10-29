from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.database import engine
from app.models.base import Base
from app.core.config import settings
import os

# Importa routers (ajusta rutas si es necesario)
from app.routes import ruta, citas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas si no existen (solo en dev; en producción usa Alembic)
#Base.metadata.create_all(bind=engine)
logger.info("Conexión exitosa a la base de datos. Tablas creadas/verificadas.")
try:
    logger.info(f"DATABASE_URL used: {settings.DATABASE_URL}")
    # Si es sqlite con ruta relativa, mostramos la ruta absoluta para aclarar
    if settings.DATABASE_URL.startswith("sqlite"):
        path = settings.DATABASE_URL.replace("sqlite://", "")
        abs_path = os.path.abspath(path)
        logger.info(f"Resolved SQLite file path: {abs_path}")
except Exception:
    logger.exception("Error al obtener DATABASE_URL para logging")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando FastAPI server...")
    yield
    logger.info("Cerrando FastAPI server...")

app = FastAPI(title="No Country - API de Gestion Medica", version="1.0.0", lifespan=lifespan)

# CORS y routers (mantén lo que ya tenías)
from starlette.middleware.cors import CORSMiddleware

# ** CORRECCIÓN DE CORS: Definir explícitamente el origen del Frontend **
_frontend = os.environ.get("FRONTEND_ORIGINS", "https://healthconnect-mvp-38-1.onrender.com")
allow_all = os.environ.get("ALLOW_ALL_CORS","0")=="1"
origins = ["*"] if allow_all else [o.strip() for o in _frontend.split(",")]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Incluir routers con los prefijos que espera el frontend
app.include_router(ruta.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(citas.router, prefix="/api/v1/appointments", tags=["Citas"])

@app.get("/")
def read_root():
    return {"message": "API de Gestión Médica funcionando."}


