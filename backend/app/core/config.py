import os

class Settings:
    # Ajusta la URL por defecto a la que uses en desarrollo
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    # Compatibilidad: alias para scopes de Google si algún módulo lo requiere
    GOOGLE_SCOPES = os.getenv("GOOGLE_SCOPES", "")

settings = Settings()