from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
# Eliminar la siguiente línea
# from uuid import UUID 


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
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    # Nuevo campo para indicar si el usuario tiene token de Google (opcional)
    has_google_token: Optional[bool] = False

    # Usar ConfigDict v2 para compatibilidad con pydantic v2
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema para los datos del payload del token JWT."""
    user_id: int
    role: str
    exp: datetime # Campo estándar de expiración de JWT


class TokenResponse(BaseModel):
    """Schema para la respuesta del token JWT."""
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    user: Optional[UserResponse] = None


# ----------------------------------------------------------------------
# Schemas para Citas Médicas
# ----------------------------------------------------------------------

class AppointmentCreate(BaseModel):
    """Schema para la creación de una nueva cita."""
    doctor_id: int = Field(..., description="ID del doctor que provee la cita.")
    start_time: datetime = Field(..., description="Fecha/hora inicio (ISO format)")
    end_time: datetime = Field(..., description="Fecha/hora fin (ISO format)")
    is_virtual: bool = Field(default=True, description="Indica si la cita es virtual")
    priority_level: Optional[str] = Field(None, description="LOW|MEDIUM|HIGH")
    description: Optional[str] = Field(None, description="Descripción de la cita (opcional)")

    model_config = ConfigDict(extra="forbid")


class AppointmentResponse(BaseModel):
    """Schema de respuesta para una cita, incluyendo datos de la DB y Google."""
    id: int
    patient_id: Optional[int] = None 
    
    # Objetos anidados
    patient: Optional['UserResponse'] = None
    doctor: Optional['UserResponse'] = None
    
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None
    is_virtual: bool
    priority_level: str
    status: str
    video_url: Optional[str] = None
    google_event_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)




class ClinicalRecordBase(BaseModel):
    """Schema base para el contenido del registro clínico."""
    patient_id: int = Field(..., description="ID del paciente al que pertenece el registro.")
    doctor_id: int = Field(..., description="ID del doctor que crea el registro.")
    
    diagnosis: str = Field(..., max_length=255)
    treatment: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=500)

class ClinicalRecordCreate(ClinicalRecordBase):
    """Schema para crear un nuevo registro clínico."""
    pass

class ClinicalRecordUpdate(BaseModel):
    """Schema para actualizar un registro clínico existente."""
    diagnosis: Optional[str] = Field(None, max_length=255)
    treatment: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=500)

class ClinicalRecordResponse(BaseModel):
    """Schema de respuesta para un registro clínico."""
    id: int
    patient_id: int
    doctor_id: int
    record_date: datetime
    diagnosis: str
    treatment: Optional[str] = None
    notes: Optional[str] = None
    
    patient: Optional['UserResponse'] = None
    doctor: Optional['UserResponse'] = None
    
    model_config = ConfigDict(from_attributes=True)


class HTTPError(BaseModel):
    """Schema estándar para respuestas de error de la API."""
    detail: str