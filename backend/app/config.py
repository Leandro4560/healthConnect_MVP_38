import os
from datetime import timedelta
from dotenv import load_dotenv
from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict 


load_dotenv()


class UserRole:
    PACIENTE = "PACIENTE"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

class Settings(BaseSettings):
    
    SECRET_KEY: str = Field(default=os.getenv("SECRET_KEY", "super_secreto_y_largo_default"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 
    
    
    DATABASE_URL: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./sql_app.db"))
    
    
    SUPABASE_URL: str = Field(
        default=os.getenv("SUPABASE_URL", "https://owmxsumofvrlnjbtrsir.supabase.co")
    )
    SUPABASE_KEY_ANON: str = Field(
        default=os.getenv("SUPABASE_KEY_ANON", "")
    )
    # NEW: key de servicio (service role) usada por el backend para operaciones admin (crear usuarios, etc.)
    SUPABASE_SERVICE_KEY: str = Field(
        default=os.getenv("SUPABASE_SERVICE_KEY", "")
    )
    
    GOOGLE_CLIENT_ID: str = Field(default=os.getenv("GOOGLE_CLIENT_ID", ""))
    GOOGLE_CLIENT_SECRET: str = Field(default=os.getenv("GOOGLE_CLIENT_SECRET", ""))
    GOOGLE_REDIRECT_URI: str = Field(default=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"))
    FRONTEND_URL: str = Field(default=os.getenv("FRONTEND_URL", "http://localhost:5173"))
    
    
    TIME_ZONE: str = Field(default=os.getenv("TIME_ZONE", "America/Bogota"))
    GOOGLE_CALENDAR_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    # Alias para compatibilidad con otros módulos
    GOOGLE_SCOPES: list[str] = GOOGLE_CALENDAR_SCOPES

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
