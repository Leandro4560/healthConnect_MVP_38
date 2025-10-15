import os
from datetime import timedelta
from dotenv import load_dotenv
from pydantic import Field
# Nota: Usamos BaseSettings de pydantic_settings
from pydantic_settings import BaseSettings, SettingsConfigDict 

# Carga las variables de entorno desde .env
load_dotenv()

# Define los roles de usuario para evitar errores de tipeo en todo el código
class UserRole:
    PACIENTE = "PACIENTE"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

# Define la configuración de la aplicación y lee de variables de entorno
class Settings(BaseSettings):
    # --- Configuración de Seguridad JWT ---
    # Usa Field con getenv para mayor robustez
    SECRET_KEY: str = Field(default=os.getenv("SECRET_KEY", "super_secreto_y_largo_default"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Usando tu valor
    
    # --- Configuración de Base de Datos ---
    DATABASE_URL: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./sql_app.db"))
    
    # --- Configuración de Google OAuth ---
    GOOGLE_CLIENT_ID: str = Field(default=os.getenv("GOOGLE_CLIENT_ID", ""))
    GOOGLE_CLIENT_SECRET: str = Field(default=os.getenv("GOOGLE_CLIENT_SECRET", ""))
    GOOGLE_REDIRECT_URI: str = Field(default=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"))
    
    # --- Configuración de Google Calendar API ---
    TIME_ZONE: str = Field(default=os.getenv("TIME_ZONE", "America/Bogota"))
    GOOGLE_CALENDAR_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/calendar.readonly"
    ]
    
    # Configuración para pydantic_settings (similar a tu clase Config)
    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")

settings = Settings()
