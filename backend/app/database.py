from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import time
import logging
import os

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL or os.environ.get("DATABASE_URL")

# Ajustes de pool recomendados para entornos con límites (Render / free tier)
ENGINE_KWARGS = {
    "pool_size": 5,
    "max_overflow": 2,
    "pool_timeout": 30,
    "pool_recycle": 1800,
    "pool_pre_ping": True,
    "future": True,
}

# Forzar sslmode=require si no está en la URL (Supabase lo requiere en muchos casos)
connect_args = {}
if DATABASE_URL and ("postgres://" in DATABASE_URL or "postgresql://" in DATABASE_URL):
    if "sslmode" not in DATABASE_URL:
        connect_args = {"sslmode": "require"}
        logger.info("Añadiendo connect_args={'sslmode':'require'} para la conexión PostgreSQL.")

def create_engine_with_retry(url, retries=4, backoff=1.0):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            engine = create_engine(url, connect_args=connect_args, **ENGINE_KWARGS)
            # probar conexión rápida
            with engine.connect() as conn:
                pass
            logger.info("Engine creado y test de conexión OK.")
            return engine
        except Exception as e:
            last_exc = e
            logger.warning("Database connection test attempt %d/%d failed: %s", attempt, retries, e)
            time.sleep(backoff * (2 ** (attempt - 1)))
    # si fallan los retries, devolver engine (creado sin test) para que la app no caiga al arranque
    try:
        engine = create_engine(url, connect_args=connect_args, **ENGINE_KWARGS)
        logger.warning("No se pudo verificar la conexión en el startup, se devuelve engine y la app continuará; conexiones posteriores intentarán conectarse.")
        return engine
    except Exception as e:
        logger.error("No se pudo crear engine: %s", e)
        raise last_exc

# Crear engine (no bloquear el arranque indefinidamente)
engine = create_engine_with_retry(DATABASE_URL, retries=4, backoff=1.0)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()