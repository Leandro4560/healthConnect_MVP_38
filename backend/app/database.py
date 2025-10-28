import os
import time
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# Determinar URL de BD: usar DATABASE_URL si existe, si no usar SQLite local
DATABASE_URL = os.environ.get("DATABASE_URL")
DB_PROVIDER = os.environ.get("DB_PROVIDER", "").lower()  # opcional: "sqlite" o "postgres"

if not DATABASE_URL:
    # si explícitamente piden postgres pero no hay URL -> error
    if DB_PROVIDER == "postgres":
        raise RuntimeError("DATABASE_URL no definida para proveedor Postgres.")
    # fallback a sqlite en archivo local
    sqlite_path = os.environ.get("SQLITE_PATH", "/data/dev.db")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    DATABASE_URL = f"sqlite:///{sqlite_path}"
    print(f"No DATABASE_URL encontrado. Usando SQLite local: {DATABASE_URL}")

# Configuración general
ENGINE_KWARGS = {
    "pool_size": int(os.environ.get("DB_POOL_SIZE", "5")),
    "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "2")),
    "pool_timeout": int(os.environ.get("DB_POOL_TIMEOUT", "30")),
    "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", "1800")),
}

# Ajustes por driver
if DATABASE_URL.startswith("sqlite"):
    CONNECT_ARGS = {"check_same_thread": False}
    # para sqlite no aplican pool_size/max_overflow en general
    ENGINE_CREATION_KWARGS = {}
else:
    CONNECT_ARGS = {"sslmode": os.environ.get("DB_SSLMODE", "require")}
    ENGINE_CREATION_KWARGS = ENGINE_KWARGS

def create_engine_with_retry(url: str, retries: int = 4, backoff: float = 1.0):
    last_exc = None
    for attempt in range(retries):
        try:
            engine = create_engine(url, connect_args=CONNECT_ARGS, **ENGINE_CREATION_KWARGS)
            # Smoke test (usa text para compatibilidad)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as e:
            last_exc = e
            wait = backoff * (2 ** attempt)
            print(f"Database connection test attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(wait)

    if last_exc:
        print("No se pudo verificar la conexión en el startup; se devolverá engine y la app continuará; conexiones posteriores intentarán conectarse.")
    return create_engine(url, connect_args=CONNECT_ARGS, **ENGINE_CREATION_KWARGS)

# Crear engine y sesión
engine = create_engine_with_retry(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()