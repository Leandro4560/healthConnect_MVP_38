import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import urllib.parse
import time

DATABASE_URL = settings.DATABASE_URL

# Configurar logging para debug de conexión
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Motor SQLAlchemy configurado para Postgres
# Configuración de SSL para conexiones seguras (requerido por Supabase)
connect_args = {"connect_timeout": 30}  # Timeout más largo para debug

# Asegurarnos que tenemos una URL válida
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada")

def modify_url_for_local_proxy(url):
    """Modifica la URL para usar el proxy local"""
    parsed = urllib.parse.urlparse(url)
    # Mantener las mismas credenciales y base de datos, pero usar localhost
    new_netloc = f"{parsed.username}:{parsed.password}@localhost:{parsed.port}"
    return urllib.parse.urlunparse((
        parsed.scheme,
        new_netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    # Modificar la URL para usar el proxy local
    DATABASE_URL = modify_url_for_local_proxy(DATABASE_URL)
    parsed_url = urllib.parse.urlparse(DATABASE_URL)
    
    logger.info(f"Using local proxy connection: {parsed_url.hostname}:{parsed_url.port}")
    
    # Configuración de conexión con todas las opciones necesarias
    connect_args = {
        "connect_timeout": 30,
        "application_name": "healthconnect_backend",
        "sslmode": "require",
        "options": "-c statement_timeout=30000"  # 30 segundos timeout para queries
    }

logger.info("Initializing database engine (no blocking connect)...")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    connect_args=connect_args,
    pool_size=5,               # Limitar conexiones concurrentes
    max_overflow=10,           # Máximo de conexiones extra
    pool_timeout=30,           # Timeout para obtener conexión del pool
    pool_recycle=1800,        # Reciclar conexiones cada 30 min
)

# Intentar una conexión de comprobación con reintentos para dar tiempo al proxy
max_attempts = 6
for attempt in range(1, max_attempts + 1):
    try:
        logger.info(f"Database connection test attempt {attempt}/{max_attempts}...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        break
    except Exception as e:
        logger.warning(f"Database connection attempt {attempt} failed: {e}")
        if attempt == max_attempts:
            logger.error("All database connection attempts failed, raising error")
            raise
        # esperar exponencialmente (2, 4, 8...) para darle tiempo al proxy
        sleep_seconds = 2 ** attempt
        logger.info(f"Waiting {sleep_seconds}s before next attempt...")
        time.sleep(sleep_seconds)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

def get_db():
    """Dependencia de FastAPI: yield una sesión y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()