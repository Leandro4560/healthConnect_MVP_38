import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime


from app.database import Base 
from app.models.user import User


class PriorityLevel(enum.Enum):
    """Nivel de prioridad de la cita."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"

class AppointmentStatus(enum.Enum):
    """Estado actual de la cita."""
    PENDING = "pending"        
    CONFIRMED = "confirmed"     
    CANCELLED = "cancelled"     
    COMPLETED = "completed"     
    NO_SHOW = "no_show"        



class Appointment(Base):
    """
    Representa una cita médica programada entre un paciente y un doctor.
    """
    __tablename__ = "appointment"

    id = Column(Integer, primary_key=True, index=True)
    
    
    patient_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    
    
    doctor_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=True)

   
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
   
    is_virtual = Column(Boolean, default=True) 
    notes = Column(String, nullable=True)
    
   
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False)
    priority_level = Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

   
    
   
    google_event_id = Column(String, index=True, nullable=True) 
    
   
    video_url = Column(String, nullable=True) 

    
    patient = relationship(
        "User", 
        foreign_keys=[patient_id], 
        backref="appointments_as_patient"
    )
    
    
    doctor = relationship(
        "User", 
        foreign_keys=[doctor_id], 
        backref="appointments_as_doctor"
    )
