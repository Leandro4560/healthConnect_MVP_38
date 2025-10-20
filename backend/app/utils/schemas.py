# app/utils/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID 


# ----------------------------------------------------------------------
# Schemas para Usuarios
# ----------------------------------------------------------------------

class UserBase(BaseModel):
    """Base para la creación/lectura de usuarios."""
    email: EmailStr = Field(..., example="doctor@hospital.com")
    name: str = Field(..., example="Dr. Ana García") 
    role: Optional[str] = Field(None, example="DOCTOR")

class UserCreate(UserBase):
    """Schema para crear un nuevo usuario. Incluye la contraseña."""
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """Schema para la autenticación de usuarios."""
    email: EmailStr = Field(..., example="doctor@hospital.com")
    password: str


class UserUpdate(BaseModel):
    """Schema para actualizar datos de un usuario. Todos los campos son opcionales."""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    
    # Para doctores que conectan Google Calendar
    google_refresh_token: Optional[str] = None 
    
    model_config = ConfigDict(extra="ignore")


class UserResponse(BaseModel):
    """Schema de salida para los datos del usuario."""
    id: int
    full_name: str = Field(..., alias="name") # Mapea full_name (modelo) a name (schema)
    email: EmailStr
    role: str
    is_active: bool
    supabase_id: Optional[UUID] = None
    has_google_token: Optional[bool] = None # Campo para el frontend
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Token(BaseModel):
    """Schema para los datos del payload del token JWT."""
    user_id: int
    role: str
    exp: datetime # Campo estándar de expiración de JWT


class TokenResponse(BaseModel):
    """Schema de respuesta para el login exitoso."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse 


# ----------------------------------------------------------------------
# Schemas para Citas Médicas
# ----------------------------------------------------------------------

class AppointmentCreate(BaseModel):
    """Schema para la creación de una nueva cita."""
    
    doctor_id: int = Field(..., description="ID del doctor que provee la cita.") 
    patient_name: str = Field(..., description="Nombre del paciente.")
    description: Optional[str] = Field(None, description="Descripción de la cita.")
    
    start_time: datetime = Field(..., description="Hora de inicio de la cita (con zona horaria).")
    end_time: datetime = Field(..., description="Hora de fin de la cita (con zona horaria).")
    is_virtual: Optional[bool] = True
    priority_level: Optional[str] = "MEDIUM"


class AppointmentResponse(BaseModel):
    """Schema de respuesta para una cita, incluyendo datos de la DB y Google."""
    id: int
    patient_id: Optional[int] = None 
    
    # Objetos anidados
    patient: Optional['UserResponse'] = None
    doctor: Optional['UserResponse'] = None
    
    # Datos de la cita
    start_time: datetime
    end_time: datetime
    is_virtual: bool
    priority_level: str
    description: Optional[str] = None
    status: str = Field(..., example="SCHEDULED")
    
    # Datos de Google
    google_event_id: Optional[str] = None
    google_meet_link: Optional[str] = Field(None, alias="video_url")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ----------------------------------------------------------------------
# Schemas para Registros Clínicos
# ----------------------------------------------------------------------

class ClinicalRecordBase(BaseModel):
    """Schema base para el contenido del registro clínico."""
    patient_id: int = Field(..., description="ID del paciente al que pertenece el registro.")
    doctor_id: int = Field(..., description="ID del doctor que crea el registro.")
    
    diagnosis: str = Field(..., max_length=255)
    treatment: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)

class ClinicalRecordCreate(ClinicalRecordBase):
    """Schema para crear un nuevo registro clínico."""
    pass

class ClinicalRecordUpdate(BaseModel):
    """Schema para actualizar un registro clínico. Todos los campos son opcionales."""
    diagnosis: Optional[str] = Field(None, max_length=255)
    treatment: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None

class ClinicalRecordResponse(BaseModel):
    """Schema de respuesta para un registro clínico."""
    id: int
    record_date: datetime
    
    patient: 'UserResponse'
    doctor: 'UserResponse'
    
    diagnosis: str
    treatment: Optional[str]
    notes: Optional[str]
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class HTTPError(BaseModel):
    """Schema estándar para respuestas de error de la API."""
    detail: str