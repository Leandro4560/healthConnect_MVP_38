from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os


DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    future=True
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
