import os
import time
import pkgutil
import importlib
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# Configuración: forzar SQLite si DB_PROVIDER=sqlite o FORCE_LOCAL_SQLITE=1
DB_PROVIDER = os.environ.get("DB_PROVIDER", "").lower()
FORCE_LOCAL = os.environ.get("FORCE_LOCAL_SQLITE", "").lower() in ("1", "true", "yes")

ENV_DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
USE_SQLITE = FORCE_LOCAL or DB_PROVIDER == "sqlite" or (not ENV_DATABASE_URL)

if USE_SQLITE:
    SQLITE_PATH = os.environ.get("SQLITE_PATH", "/data/dev.db")
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
    IS_SQLITE = True
else:
    DATABASE_URL = ENV_DATABASE_URL
    IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Ajustes por driver
if IS_SQLITE:
    CONNECT_ARGS = {"check_same_thread": False}
    ENGINE_CREATION_KWARGS = {}
else:
    CONNECT_ARGS = {"sslmode": os.environ.get("DB_SSLMODE", "require")}
    ENGINE_CREATION_KWARGS = {
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "2")),
        "pool_timeout": int(os.environ.get("DB_POOL_TIMEOUT", "30")),
        "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", "1800")),
    }

def create_engine_with_retry(url: str, retries: int = 4, backoff: float = 1.0):
    """
    Crea el engine. Para Postgres intenta varios reintentos; para SQLite devuelve el engine directo.
    """
    if IS_SQLITE:
        return create_engine(url, connect_args=CONNECT_ARGS, **ENGINE_CREATION_KWARGS)

    last_exc = None
    for attempt in range(retries):
        try:
            engine = create_engine(url, connect_args=CONNECT_ARGS, **ENGINE_CREATION_KWARGS)
            # Smoke test
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as e:
            last_exc = e
            wait = backoff * (2 ** attempt)
            print(f"Database connection test attempt {attempt+1}/{retries} failed: {e}; waiting {wait}s")
            time.sleep(wait)

    if last_exc:
        print("No se pudo verificar la conexión en el startup; se devolverá engine y la app continuará; conexiones posteriores intentarán conectarse.")
    return create_engine(url, connect_args=CONNECT_ARGS, **ENGINE_CREATION_KWARGS)

# Crear engine y sesión
engine = create_engine_with_retry(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Intentar crear tablas: importar app.models y crear las tablas para
# cada clase mapeada (esto cubre casos donde los modelos usan otra Base/MetaData).
def _create_model_tables(engine):
    try:
        models_pkg = importlib.import_module("app.models")
    except Exception:
        # No hay paquete app.models
        return

    for finder, modname, ispkg in pkgutil.iter_modules(models_pkg.__path__):
        full_name = f"app.models.{modname}"
        try:
            mod = importlib.import_module(full_name)
        except Exception as e:
            print(f"Warning: no se pudo importar {full_name}: {e}")
            continue

        for obj in vars(mod).values():
            # mapped class tendrá __table__
            if hasattr(obj, "__table__"):
                try:
                    obj.__table__.metadata.create_all(engine)
                except Exception as e:
                    print(f"Warning: crear tabla para {getattr(obj, '__name__', str(obj))} falló: {e}")

# Intentar crear tablas tanto en la metadata local como en las de los modelos importados
try:
    # importar modelos (si existen) y crear sus tablas
    _create_model_tables(engine)

    # crear tablas registradas en Base de este módulo (si hubiera)
    Base.metadata.create_all(engine)

    print("Conexión exitosa a la base de datos. Tablas creadas/verificadas.")
    print(f"DATABASE_URL used: {DATABASE_URL}")
    if IS_SQLITE:
        print(f"Resolved SQLite file path: {DATABASE_URL.replace('sqlite://', '')}")
except Exception as e:
    print("Aviso: creación de tablas falló:", e)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()