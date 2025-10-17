from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID 


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
    
   
    google_refresh_token: Optional[str] = None 
    
    class Config:
        
        extra = "ignore" 


class UserResponse(BaseModel):
    """Schema de salida para los datos del usuario."""
    id: int
    
    full_name: str = Field(..., alias="name") 
    email: EmailStr
    role: str
    is_active: bool
    
    supabase_id: Optional[UUID] = None 

    class Config:
        
        from_attributes = True
        




class TokenData(BaseModel):
    """Schema interno que representa los datos que van dentro del token JWT."""
    user_id: Optional[int] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None 

class TokenResponse(BaseModel):
    """Schema de respuesta para el login exitoso."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse 




class AppointmentCreate(BaseModel):
    """Schema para la creación de una nueva cita."""
    
    doctor_id: int = Field(..., example=1) 
    patient_name: str = Field(..., example="Juan Pérez")
    description: Optional[str] = Field(None, example="Revisión anual y chequeo general.")
    
  
    start_time: datetime = Field(..., example=datetime.now())
    end_time: datetime = Field(..., example=datetime.now())
    is_virtual: Optional[bool] = True
    priority_level: Optional[str] = "MEDIUM"


class AppointmentResponse(AppointmentCreate):
    """Schema de respuesta para una cita, incluyendo datos de la DB y Google."""
    id: int
    patient_id: Optional[int] = None 
    status: str = Field(..., example="SCHEDULED")
    
  
    google_event_id: Optional[str] = None
    google_meet_link: Optional[str] = Field(None, alias="video_url") 
    ics_uid: Optional[str] = None 

    class Config:
        from_attributes = True
        populate_by_name = True 

        


class HTTPError(BaseModel):
<<<<<<< HEAD
    """Schema estándar para la documentación de errores de la API."""
    detail: str
=======
    """Schema estándar para respuestas de error de la API."""
    detail: str = Field(..., example="Un error inesperado ha ocurrido.")

    class Config:
        from_attributes = True
>>>>>>> 54e5f519722c03ecd36a04a16f3725464eb77d33
