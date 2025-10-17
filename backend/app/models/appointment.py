from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


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
    
    
    patient_id = Column(Integer, ForeignKey("users.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))

    
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    
    
    is_virtual = Column(Boolean, default=True)
    priority_level = Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    notes = Column(Text, nullable=True)
    video_url = Column(String, nullable=True) 
    
 
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDIENTE)
    
    
    google_event_id = Column(String, nullable=True)
    
    
    patient = relationship("User", foreign_keys=[patient_id], backref="patient_appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_appointments")
    
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Appointment(id={self.id}, start={self.start_time}, status={self.status.value})>"
