# Importamos la clase FastAPI para crear la aplicación
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import List, Optional

# --- Inicialización de la Aplicación ---
# La variable 'app' es la que uvicorn busca para iniciar el servidor.
app = FastAPI(
    title="HealthConnect API",
    description="API para la gestión de usuarios, médicos, citas y registros de salud.",
    version="0.1.0"
)

# --- Esquemámas de Pydantic (Definiciones temporales para que compile) ---

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        # Permite que el esquema Pydantic se mapee a un objeto SQLAlchemy
        from_attributes = True


# --- Rutas/Endpoints ---

@app.get("/")
def read_root():
    """Endpoint de bienvenida para verificar que la API está activa."""
    return {"message": "¡Bienvenido a HealthConnect API! (Servidor activo)"}

# NOTA: Agregaremos más rutas para usuarios, médicos, etc., más adelante.
