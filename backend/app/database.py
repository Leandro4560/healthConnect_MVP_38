from sqlalchemy import create_engine
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

if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    parsed_url = urllib.parse.urlparse(DATABASE_URL)
    
    # Asegurarnos que la URL tiene todos los componentes necesarios
    if not parsed_url.hostname:
        raise ValueError("DATABASE_URL no tiene un hostname válido")
    
    # Siempre usar SSL para conexiones a Supabase
    connect_args.update({
        "sslmode": "require",
        "connect_timeout": 30
    })
    
    logger.info(f"Attempting connection to: {parsed_url.hostname}:{parsed_url.port or 5432}")
    
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