from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.exc import OperationalError
from starlette.middleware.cors import CORSMiddleware
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from app.database import Base, engine
from app.routes import ruta, citas 


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

app = FastAPI(
    title="No Country - API de Gestión Médica",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ruta.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(citas.router, prefix="/api/v1/appointments", tags=["Citas"])

@app.get("/")
def read_root():
    return {"message": "API de Gestión Médica funcionando."}
