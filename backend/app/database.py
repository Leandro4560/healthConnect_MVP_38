import os
import time
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# Decidir proveedor: si DB_PROVIDER=sqlite o no existe DATABASE_URL => usar SQLite local
DB_PROVIDER = os.environ.get("DB_PROVIDER", "").lower()
DATABASE_URL = os.environ.get("DATABASE_URL")

if DB_PROVIDER == "sqlite" or not DATABASE_URL:
    sqlite_path = os.environ.get("SQLITE_PATH", "/data/dev.db")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    DATABASE_URL = f"sqlite:///{sqlite_path}"
    IS_SQLITE = True
else:
    IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Configuración por driver
if IS_SQLITE:
    CONNECT_ARGS = {"check_same_thread": False}
    ENGINE_CREATION_KWARGS = {}  # no pool sizing para sqlite
else:
    CONNECT_ARGS = {"sslmode": os.environ.get("DB_SSLMODE", "require")}
    ENGINE_CREATION_KWARGS = {
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "2")),
        "pool_timeout": int(os.environ.get("DB_POOL_TIMEOUT", "30")),
        "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", "1800")),
    }

def create_engine_with_retry(url: str, retries: int = 4, backoff: float = 1.0):
    if IS_SQLITE:
        return create_engine(url, connect_args=CONNECT_ARGS, **ENGINE_CREATION_KWARGS)

    last_exc = None
    for attempt in range(retries):
        try:
            engine = create_engine(url, connect_args=CONNECT_ARGS, **ENGINE_CREATION_KWARGS)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as e:
            last_exc = e
            time.sleep(backoff * (2 ** attempt))

    if last_exc:
        print("No se pudo verificar la conexión en el startup; se devolverá engine y la app continuará; conexiones posteriores intentarán conectarse.", last_exc)
    return create_engine(url, connect_args=CONNECT_ARGS, **ENGINE_CREATION_KWARGS)

# Crear engine y sesión
engine = create_engine_with_retry(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Intentar crear tablas (no detendrá la app si falla)
try:
    # Intentar importar modelos para registrar metadata (si existe)
    try:
        from app import models  # noqa: F401
    except Exception:
        pass
    Base.metadata.create_all(engine)
except Exception as e:
    print("Aviso: creación de tablas falló:", e)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()