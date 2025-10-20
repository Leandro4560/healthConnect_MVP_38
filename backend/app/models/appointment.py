# app/models/appointment.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum
from sqlalchemy.dialects.postgresql import UUID as SQAlchemyUUID 

class PriorityLevel(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AppointmentStatus(enum.Enum):
    PENDIENTE = "PENDIENTE"
    SCHEDULED = "SCHEDULED"
    CONFIRMADA = "CONFIRMADA"
    CANCELED = "CANCELED"
    FINALIZADA = "FINALIZADA"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    
    patient_id = Column(SQAlchemyUUID(as_uuid=True), ForeignKey("users.id"))

    doctor_id = Column(SQAlchemyUUID(as_uuid=True), ForeignKey("users.id"))

    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    notes = Column(Text, nullable=True)
    
    is_virtual = Column(Boolean, default=True)
    priority_level = Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDIENTE)
    
    video_url = Column(String, nullable=True) 
    google_event_id = Column(String, nullable=True)
    
    patient = relationship(
        "User", 
        foreign_keys=[patient_id],
        back_populates="patient_appointments" 
    ) 
    
    doctor = relationship(
        "User", 
        foreign_keys=[doctor_id],
        back_populates="doctor_appointments" 
    ) 

    def __repr__(self):
        return (f"<Appointment(id={self.id}, doctor={self.doctor_id}, "
                f"start='{self.start_time}', status='{self.status.value}')>")
