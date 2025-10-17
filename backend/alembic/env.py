import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ======================================================================
# 1. Ajuste de Path para importar la aplicación de FastAPI
# ======================================================================
# Agregamos la carpeta 'backend' al path para poder importar módulos como 'app.config'
# Este es un método robusto para un proyecto anidado como el tuyo.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ======================================================================
# 2. Importaciones de la Aplicación y Modelos
# ======================================================================
from app.config import settings
# Importamos Base (la metadata) para que Alembic sepa qué debe crear/comparar
from app.database import Base
target_metadata = Base.metadata

# Importa TUS MODELOS (los módulos donde están definidos los objetos de clase User, Appointment, etc.)
# Esto es CRUCIAL para que Alembic los detecte para la autogeneración.
import app.models.user
import app.models.appointment
# Si tienes más modelos (ej: clinical_record), añádelos aquí.
# ======================================================================

config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    # Esto soluciona el KeyError 'formatters' si tu alembic.ini no lo tenía bien
    fileConfig(config.config_file_name)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode. (No DB connection)"""
    # Aquí aún lee la URL del ini, pero no la usa para conectarse
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True, # Importante para autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode. (Conexión a la DB)"""
    
    # ======================================================================
    # 3. MODIFICACIÓN CLAVE: Obtener la URL desde settings
    # ======================================================================
    db_url = settings.DATABASE_URL

    if not db_url:
         # Mensaje de error útil si el .env no se lee correctamente
         raise Exception("DATABASE_URL no está configurada en app.config. Asegúrate de que tu archivo .env está cargado y accesible.")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        # Pasamos la URL correcta de settings, ignorando lo que haya en alembic.ini
        url=db_url, 
        poolclass=pool.NullPool,
        future=True # Usar API 2.0
    )
    # ======================================================================

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True, # Importante para autogenerate
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
