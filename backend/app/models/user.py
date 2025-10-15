import enum
from sqlalchemy import Column, Integer, String, Enum, Boolean, Text
from sqlalchemy.orm import relationship

# =====================================================================
# Importación CORREGIDA:
# Usamos '..' para subir de 'app/models' a 'app' y acceder a 'database'.
# =====================================================================
from ..database import Base


class UserRole(enum.Enum):
    """Define los roles de usuario disponibles en el sistema."""
    PATIENT = "Patient"
    # ¡Corrección de un error tipográfico!
    DOCTOR = "Doctor" 
    ADMIN = "Admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Asegúrate de usar la clase Enum directamente
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True)

    google_refresh_token = Column(Text, nullable=True) 

    # Asumiendo que ClinicalRecord y Appointment están definidos en otro lugar
    
    patient_records = relationship(
        "ClinicalRecord", 
        back_populates="patient",
        foreign_keys="ClinicalRecord.patient_id",
        lazy="joined",
        cascade="all, delete-orphan"
    )

    doctor_records = relationship(
        "ClinicalRecord", 
        back_populates="doctor", 
        foreign_keys="ClinicalRecord.doctor_id",
        lazy="joined"
    )

    patient_appointments = relationship(
        "Appointment", 
        back_populates="patient", 
        foreign_keys="Appointment.patient_id",
        lazy="joined"
    )

    doctor_appointments = relationship(
        "Appointment", 
        back_populates="doctor", 
        foreign_keys="Appointment.doctor_id",
        lazy="joined"
    )
