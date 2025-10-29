import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

# Preferir la variable de entorno directa (start.sh la puede reescribir a localhost:6543)
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("ENV_DATABASE_URL") or "sqlite:///./sql_app.db"

IS_SQLITE = DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    connect_args = {"check_same_thread": False}
else:
    # Forzar sslmode si no está presente
    if "sslmode" not in DATABASE_URL:
        connect_args = {"sslmode": os.environ.get("DB_SSLMODE", "require")}
        logger.info("Aplicando connect_args sslmode=require para Postgres")
    else:
        connect_args = {}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

