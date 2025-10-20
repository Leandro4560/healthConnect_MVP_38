# app/models/user.py
import enum
from sqlalchemy import Column, String, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as SQAlchemyUUID 
from uuid import uuid4 

from ..database import Base
# Se importan las clases para las relaciones
from .appointment import Appointment 
from .clinical_record import ClinicalRecord
from sqlalchemy import Integer # Se mantiene por si se usa en otros lugares, pero no en id

class UserRole(enum.Enum):
    """Define los roles de usuario disponibles en el sistema."""
    PATIENT = "Patient"
    DOCTOR = "Doctor" 
    ADMIN = "Admin"

class User(Base):
    __tablename__ = "users"

    # CORRECCIÓN CLAVE: ID como UUID con generación automática
    id = Column(SQAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4) 
    
    # Campos de Autenticación/Perfil
    supabase_id = Column(
        SQAlchemyUUID(as_uuid=True), 
        unique=True, 
        nullable=True, 
        index=True
    )
    
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Roles y Estado
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True)

    # Integración con Google Calendar
    google_refresh_token = Column(Text, nullable=True) 
    
    # ----------------------------------------------------------------------
    # RELACIONES
    # ----------------------------------------------------------------------
    
    patient_records = relationship(
        "ClinicalRecord", 
        back_populates="patient",
        foreign_keys=lambda: [ClinicalRecord.patient_id], 
        lazy="joined",
        cascade="all, delete-orphan"
    )

    doctor_records = relationship(
        "ClinicalRecord", 
        back_populates="doctor", 
        foreign_keys=lambda: [ClinicalRecord.doctor_id],
        lazy="joined"
    )

    patient_appointments = relationship(
        "Appointment", 
        back_populates="patient", 
        foreign_keys=lambda: [Appointment.patient_id],
        lazy="joined",
        cascade="all, delete-orphan"
    )

    doctor_appointments = relationship(
        "Appointment", 
        back_populates="doctor", 
        foreign_keys=lambda: [Appointment.doctor_id],
        lazy="joined"
    )
    
    def __repr__(self):
        return (f"<User(id={self.id}, email='{self.email}', "
                f"role='{self.role.value}', active={self.is_active})>")