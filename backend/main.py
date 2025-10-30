from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import inspect
import logging

from app.database import engine
from app.models.base import Base
from app.core.config import settings
import os

# Importa routers (ajusta rutas si es necesario)
from app.routes import ruta, citas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas si no existen (solo en dev o cuando se usa SQLite). En producción
# preferimos usar alembic. Para evitar el error "no such table" en despliegues
# con SQLite (ephemeral FS en Render), comprobamos y creamos las tablas si faltan.
if os.environ.get("CREATE_TABLES","0") == "1":
    try:
        logger.info("CREATE_TABLES=1 -> creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas correctamente.")
    except Exception:
        logger.exception("Error creando tablas con create_all")
else:
    # Si no se pidió explicitamente crear tablas, y la DB es SQLite, intentar
    # detectarlas y crearlas automáticamente si faltan (comodín para Render).
    try:
        inspector = inspect(engine)
        existing = inspector.get_table_names()
        if 'users' not in existing:
            logger.info("No se encontró tabla 'users' en DB -> creando tablas automáticamente (sqlite fallback)")
            Base.metadata.create_all(bind=engine)
            logger.info("Tablas creadas correctamente (fallback).")
    except Exception:
        logger.exception("Error comprobando/creando tablas en startup")
logger.info("Conexión exitosa a la base de datos. Tablas creadas/verificadas.")
try:
    logger.info(f"DATABASE_URL used: {settings.DATABASE_URL}")
    # Si es sqlite con ruta relativa, mostramos la ruta absoluta para aclarar
    if settings.DATABASE_URL.startswith("sqlite"):
        rel_path = settings.DATABASE_URL.replace("sqlite://", "")
        # Resolver la ruta relativa respecto al paquete backend (evita depender del CWD)
        base_dir = os.path.dirname(__file__)  # /workspaces/.../backend
        if os.path.isabs(rel_path) and rel_path != "":
            abs_path = os.path.abspath(rel_path)
        else:
            abs_path = os.path.abspath(os.path.join(base_dir, rel_path or "."))
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
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# ** CORRECCIÓN DE CORS: Definir explícitamente el origen del Frontend **
# Si no se especifica FRONTEND_ORIGINS en el entorno, por compatibilidad
# asumimos allow_all (esto evita 404/CORS cuando no se configuró aún en Render).
_frontend = os.environ.get("FRONTEND_ORIGINS")
allow_all = os.environ.get("ALLOW_ALL_CORS","0")=="1"
if allow_all:
    origins = ["*"]
else:
    if _frontend and _frontend.strip():
        origins = [o.strip() for o in _frontend.split(",")]
    else:
        # Por defecto permitir todos los orígenes si no hay configuración explícita
        origins = ["*"]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


# Middleware para loggear cada request/response (útil para determinar si el 429
# proviene de la aplicación o de un proxy/infra externa). Logea host, método,
# path y el status code de la respuesta (y el header Retry-After si existe).
class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            client = request.client.host if request.client is not None else "unknown"
        except Exception:
            client = "unknown"
        try:
            # Limitar la cantidad de headers a logear para evitar llenar logs
            headers = {k: (v if k.lower() in ("user-agent","referer","host") else "(redacted)") for k,v in request.headers.items()}
        except Exception:
            headers = {}
        logger.info(f"[RQ] {client} -> {request.method} {request.url.path} headers={headers}")
        try:
            response: Response = await call_next(request)
        except Exception as e:
            # Si ocurre excepción, la registramos y volvemos a lanzar para preservarla
            logger.exception(f"Exception while handling request {request.method} {request.url.path}: {e}")
            raise
        try:
            ra = response.headers.get("Retry-After")
            logger.info(f"[RS] {client} <- {request.method} {request.url.path} status={response.status_code} Retry-After={ra}")
        except Exception:
            logger.info(f"[RS] {client} <- {request.method} {request.url.path} status={response.status_code}")
        return response


# Añadir la middleware de logging lo antes posible (después de CORS)
app.add_middleware(RequestResponseLoggingMiddleware)

# Incluir routers con los prefijos que espera el frontend
app.include_router(ruta.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(citas.router, prefix="/api/v1/appointments", tags=["Citas"])

@app.get("/")
def read_root():
    return {"message": "API de Gestión Médica funcionando."}


