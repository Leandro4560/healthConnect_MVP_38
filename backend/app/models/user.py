import enum
from sqlalchemy import Column, String, Integer, Enum as SAEnum, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class UserRole(enum.Enum):
    PATIENT = "Patient"
    DOCTOR = "Doctor"
    ADMIN = "Admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    supabase_id = Column(String, unique=True, nullable=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True)
    google_refresh_token = Column(Text, nullable=True)

    # Relaciones (back_populates deben coincidir con los modelos)
    patient_records = relationship("ClinicalRecord", back_populates="patient", foreign_keys="ClinicalRecord.patient_id", lazy="joined", cascade="all, delete-orphan")
    doctor_records = relationship("ClinicalRecord", back_populates="doctor", foreign_keys="ClinicalRecord.doctor_id", lazy="joined")
    patient_appointments = relationship("Appointment", back_populates="patient", foreign_keys="Appointment.patient_id", lazy="joined", cascade="all, delete-orphan")
    doctor_appointments = relationship("Appointment", back_populates="doctor", foreign_keys="Appointment.doctor_id", lazy="joined")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}', active={self.is_active})>"