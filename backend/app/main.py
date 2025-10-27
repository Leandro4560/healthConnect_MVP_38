from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.database import engine                # motor y sesiones
from app.models.base import Base               # Base está definido en app/models/base.py

# Import routers
from app.routes import ruta, citas
from app.routes import admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas si no existen (solo en dev; en producción usa Alembic)
#Base.metadata.create_all(bind=engine)
#logger.info("Conexión exitosa a la base de datos. Tablas creadas/verificadas.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando FastAPI server...")
    yield
    logger.info("Cerrando FastAPI server...")

app = FastAPI(title="No Country - API de Gestión Médica", version="1.0.0", lifespan=lifespan)

# CORS
from starlette.middleware.cors import CORSMiddleware
origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Routers
app.include_router(ruta.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(citas.router, prefix="/api/v1/appointments", tags=["Citas"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

@app.get("/")
def read_root():
    return {"message": "API de Gestión Médica funcionando."}


