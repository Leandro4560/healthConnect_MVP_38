import os
import time
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.environ.get("DATABASE_URL")
ENGINE_KWARGS = {
    "pool_size": int(os.environ.get("DB_POOL_SIZE", "5")),
    "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "2")),
    "pool_timeout": int(os.environ.get("DB_POOL_TIMEOUT", "30")),
    "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", "1800")),
}

def create_engine_with_retry(url: str, retries: int = 4, backoff: float = 1.0):
    last_exc = None
    for attempt in range(retries):
        try:
            engine = create_engine(url, **ENGINE_KWARGS)
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return engine
        except OperationalError as e:
            last_exc = e
            wait = backoff * (2 ** attempt)
            print(f"Database connection test attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(wait)

    if last_exc:
        print("No se pudo verificar la conexión en el startup, se devuelve engine y la app continuará; conexiones posteriores intentarán conectarse.")
    return create_engine(url, **ENGINE_KWARGS)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no definida. Configura la variable en Render con la URL del pooler.")

engine = create_engine_with_retry(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()