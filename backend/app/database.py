import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import urllib.parse

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
    
    # Configuración de conexión
    connect_args = {
        "connect_timeout": 30,
        "application_name": "healthconnect_backend"
    }

    # Intentar cada configuración
    connection_success = False
    for url, args in configs:
        logger.info(f"Attempting connection to: {urllib.parse.urlparse(url).hostname}:{urllib.parse.urlparse(url).port or 5432}")
        success, final_url = try_connection(url, args)
        if success:
            logger.info("Connection successful!")
            DATABASE_URL = str(final_url)
            connect_args = args
            connection_success = True
            break

    if not connection_success:
        raise ValueError("No se pudo establecer conexión con ninguna configuración")
    
    logger.info(f"Connecting to host: {parsed_url.hostname}, port: {parsed_url.port}")
    
    # Configuración SSL y timeout para todas las conexiones Postgres
    connect_args.update({
        "sslmode": "require",
        "application_name": "healthconnect_backend",
        "options": "-c statement_timeout=30000"  # 30 segundos timeout para queries
    })

try:
    logger.info("Initializing database connection...")
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
    # Probar conexión inmediatamente
    with engine.connect() as conn:
        conn.execute("SELECT 1")
        logger.info("Database connection test successful")
except Exception as e:
    logger.error(f"Database connection error: {str(e)}")
    raise

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