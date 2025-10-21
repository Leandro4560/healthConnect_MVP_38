import os

class Settings:
    # Ajusta la URL por defecto a la que uses en desarrollo
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

settings = Settings()