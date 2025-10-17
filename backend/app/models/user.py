import enum
from sqlalchemy import Column, Integer, String, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as SQAlchemyUUID # Importamos el tipo UUID
from uuid import uuid4 # Importamos para posible uso, aunque no es estrictamente necesario aquí


from ..database import Base


class UserRole(enum.Enum):
    """Define los roles de usuario disponibles en el sistema."""
    PATIENT = "Patient"
    
    DOCTOR = "Doctor" 
    ADMIN = "Admin"

class User(Base):
    __tablename__ = "users"

    
    id = Column(Integer, primary_key=True, index=True) 
    
   
    supabase_id = Column(
        SQAlchemyUUID(as_uuid=True), 
        unique=True, 
        nullable=True, 
        index=True
    )
    
    
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
   
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True)

    google_refresh_token = Column(Text, nullable=True) 

    
    
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
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    def __str__(self):
        return f"User {self.full_name} ({self.email}) - Role: {self.role.value}"
    