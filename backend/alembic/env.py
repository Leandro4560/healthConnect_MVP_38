import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

# Aseguramos que la carpeta backend (raíz del paquete) esté en sys.path
# para que `from app...` funcione cuando alembic se ejecute desde backend/
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import Base y settings desde tu paquete
from app.models.base import Base
from app.core.config import settings

# Importa los módulos que definen modelos para que se registren en metadata
# (esto hace que Base.metadata incluya todas las tablas)
# Ajusta los import según los nombres reales de tus módulos
from app.models import user, appointment, clinical_record  # noqa: F401

# this is the Alembic Config object, which provides access to the .ini file.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------
# Definir target_metadata para autogenerate (Pylance y alembic lo usan)
# ---------------------------------------------------------------------
target_metadata = Base.metadata
# ---------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    db_url = settings.DATABASE_URL
    if not db_url:
        raise Exception("DATABASE_URL no está configurada en app.core.config.settings.DATABASE_URL")

    connectable = create_engine(
        db_url,
        poolclass=pool.NullPool,
        future=True
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
