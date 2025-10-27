from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Motor SQLAlchemy (ajusta opciones si necesitas Postgres)
# Añadimos connect_args para forzar SSL en conexiones a Postgres (ej. Supabase)
connect_args = {}
# Detectar tanto postgres:// como postgresql://
if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    # Si la URL ya incluye sslmode en la query, respetarla; si no, forzamos require
    if "sslmode" not in DATABASE_URL:
        connect_args = {"sslmode": "require"}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    connect_args=connect_args,
)

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