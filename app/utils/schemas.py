from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole
from app.models.appointment import PriorityLevel, AppointmentStatus


class Token(BaseModel):
    """Esquema de respuesta para el token de acceso."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Esquema para los datos contenidos en el token JWT."""
    user_id: Optional[int] = None
    role: Optional[UserRole] = None


class UserCreate(BaseModel):
    """Esquema de entrada para el registro de nuevos usuarios."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.PATIENT

    class Config:
     
        use_enum_values = True 
        json_schema_extra = {
            "example": {
                "email": "juan.perez@example.com",
                "password": "PasswordSeguro123",
                "full_name": "Juan Pérez",
                "role": "patient"
            }
        }


class UserLogin(BaseModel):
    """Esquema de entrada para el login de usuarios."""
    email: EmailStr
    password: str

class UserOut(BaseModel):
    """Esquema de salida para devolver información del usuario."""
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    role: UserRole

    class Config:
        from_attributes = True
        use_enum_values = True 


class AppointmentCreate(BaseModel):
    """Esquema de entrada para que un paciente solicite una cita."""
    doctor_id: Optional[int] = None 
    start_time: datetime
    end_time: datetime
    is_virtual: bool
    priority_level: PriorityLevel
    notes: Optional[str] = None

    class Config:
        use_enum_values = True

class AppointmentUpdate(BaseModel):
    """Esquema para modificar campos de una cita existente."""
    doctor_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_virtual: Optional[bool] = None
    priority_level: Optional[PriorityLevel] = None
    status: Optional[AppointmentStatus] = None 
    video_url: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        use_enum_values = True
        extra = "ignore" 

class AppointmentResponse(BaseModel):
    """Esquema de salida para devolver los detalles de la cita."""
    id: int
    patient_id: int
    doctor_id: Optional[int] = None
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    priority_level: PriorityLevel
    video_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True
