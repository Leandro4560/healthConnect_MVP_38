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

def try_connection(url, args):
    """Intenta establecer una conexión con los parámetros dados"""
    try:
        test_engine = create_engine(url, connect_args=args, poolclass=sqlalchemy.pool.NullPool)
        with test_engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
            return True, test_engine.url
    except Exception as e:
        logger.warning(f"Connection attempt failed: {str(e)}")
        return False, None

if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    parsed_url = urllib.parse.urlparse(DATABASE_URL)
    
    # Configuración base
    base_args = {
        "sslmode": "require",
        "connect_timeout": 30,
        "application_name": "healthconnect_backend"
    }

    # Lista de configuraciones a intentar
    configs = []
    
    if "pooler.supabase.com" in parsed_url.hostname:
        # 1. Intento: URL original con puerto 6543 (pooler)
        configs.append((DATABASE_URL, base_args.copy()))
        
        # 2. Intento: Convertir a conexión directa
        direct_host = parsed_url.hostname.replace("pooler.", "db.")
        url_parts = list(parsed_url)
        url_parts[1] = f"{direct_host}:5432"
        direct_url = urllib.parse.urlunparse(url_parts)
        configs.append((direct_url, base_args.copy()))
        
        # 3. Intento: Usar puerto 5432 con host original
        url_parts = list(parsed_url)
        url_parts[1] = f"{parsed_url.hostname}:5432"
        alt_url = urllib.parse.urlunparse(url_parts)
        configs.append((alt_url, base_args.copy()))
    else:
        # Si no es pooler, usar la URL tal cual
        configs.append((DATABASE_URL, base_args))

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