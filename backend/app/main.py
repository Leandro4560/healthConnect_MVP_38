from fastapi import FastAPI, Request  # <--- añadir Request
from contextlib import asynccontextmanager
from sqlalchemy.exc import OperationalError
from starlette.middleware.cors import CORSMiddleware
import logging

from app.database import Base, engine
from app.models.base import Base
from app.core.config import settings
import os
from fastapi.middleware.cors import CORSMiddleware
import requests

logger = logging.getLogger("uvicorn.access")

# Crear tablas si no existen (solo en dev; en producción usa Alembic)
#Base.metadata.create_all(bind=engine)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Conexión exitosa a la base de datos. Tablas creadas/verificadas.")
except OperationalError as e:
    logger.error(f" Falló la conexión a la base de datos PostgreSQL en el inicio. {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando FastAPI server...")
    yield
    logger.info("Cerrando FastAPI server...")

app = FastAPI(title="No Country - API de Gestion Medica", version="1.0.0", lifespan=lifespan)

# CORS (temporal para debug)
_frontend = os.environ.get("FRONTEND_ORIGINS", "https://healthconnect-mvp-38-1.onrender.com")
_allow_all = os.environ.get("ALLOW_ALL_CORS", "0") == "1"
origins = ["*"] if _allow_all else [o.strip() for o in _frontend.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming {request.method} {request.url} from {request.client.host}")
    response = await call_next(request)
    logger.info(f"Response {response.status_code} for {request.method} {request.url}")
    return response

# Asegurar importar las rutas (ruta y citas) antes de usarlas
from app.routes import ruta, citas  # <--- asegurar que estén importadas

app.include_router(ruta.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(citas.router, prefix="/api/v1/appointments", tags=["Citas"])

@app.get("/")
def read_root():
    return {"message": "API de Gestión Médica funcionando."}
