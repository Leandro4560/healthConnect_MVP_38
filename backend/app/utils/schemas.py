from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

# --- Schemas de Autenticación y Usuarios ---

class UserBase(BaseModel):
    """Base para la creación/lectura de usuarios."""
    email: EmailStr = Field(..., example="doctor@hospital.com")
    name: str = Field(..., example="Dr. Ana García")
    role: str = Field(..., example="doctor")

class UserCreate(UserBase):
    """Schema para crear un nuevo usuario. Incluye la contraseña."""
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """Schema para la autenticación de usuarios."""
    email: EmailStr = Field(..., example="doctor@hospital.com")
    password: str

class UserResponse(UserBase):
    """Schema de respuesta para el usuario (omite la contraseña)."""
    id: int
    is_active: bool
    # Token de Google no se expone directamente por seguridad, solo si existe.
    has_google_token: bool = Field(default=False) 

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema para el token de acceso JWT."""
    access_token: str
    token_type: str = "bearer"
    # Opcional: para saber si se requiere la conexión a Google
    requires_google_auth: bool = False 
    
class GoogleAuthURL(BaseModel):
    """Schema para devolver la URL de autenticación de Google."""
    auth_url: str


# --- Schemas de Citas (NUEVOS) ---

class AppointmentCreate(BaseModel):
    """Schema para la creación de una nueva cita."""
    patient_name: str = Field(..., example="Juan Pérez")
    description: Optional[str] = Field(None, example="Revisión anual y chequeo general.")
    
    # Usamos datetime para manejar la hora de inicio y fin
    start_time: datetime = Field(..., example=datetime.now())
    end_time: datetime = Field(..., example=datetime.now())

class AppointmentResponse(AppointmentCreate):
    """Schema de respuesta para una cita, incluyendo datos de la DB y Google."""
    id: int
    doctor_id: int
    status: str = Field(..., example="Agendada")
    
    # Campos opcionales de Google Calendar
    google_event_id: Optional[str] = None
    google_meet_link: Optional[str] = None

    class Config:
        from_attributes = True
        
# --- Schema de Error (Mantenido o añadido si no existía) ---

class HTTPError(BaseModel):
    """Schema estándar para respuestas de error de la API."""
    detail: str = Field(..., example="Un error inesperado ha ocurrido.")

    class Config:
        from_attributes = True
