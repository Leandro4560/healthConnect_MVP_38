from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import List, Optional


app = FastAPI(
    title="HealthConnect API",
    description="API para la gestión de usuarios, médicos, citas y registros de salud.",
    version="0.1.0"
)



class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:

        from_attributes = True



@app.get("/")
def read_root():
    """Endpoint de bienvenida para verificar que la API está activa."""
    return {"message": "¡Bienvenido a HealthConnect API! (Servidor activo)"}


