from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Motor SQLAlchemy (ajusta opciones si necesitas Postgres)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
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