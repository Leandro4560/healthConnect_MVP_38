from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# Añadir sslmode=require para conexiones a Supabase/Postgres si no está en la URL
connect_args = {}
if DATABASE_URL and DATABASE_URL.startswith(("postgres://", "postgresql://")):
    if "sslmode" not in DATABASE_URL:
        connect_args = {"sslmode": "require"}
        logger.info("Añadiendo connect_args={'sslmode':'require'} para la conexión PostgreSQL.")

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    future=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    future=True
)

Base = declarative_base()

def get_db():
    """Dependencia para obtener la sesión de la base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()