import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship
from datetime import datetime


from app.database import Base 



class PriorityLevel(enum.Enum):
    
    LOW = "Baja"
    MEDIUM = "Media"
    HIGH = "Alta"
    URGENT = "Urgente"

class AppointmentStatus(enum.Enum):
    
    REQUESTED = "Solicitada"      
    CONFIRMED = "Confirmada"      
    CANCELLED = "Cancelada"      
    COMPLETED = "Completada"      
    NO_SHOW = "No Presentado"     



class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    
    
    patient_id = Column(Integer, ForeignKey("users.id"), index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True) 

   
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_virtual = Column(Boolean, default=True)
    
    
    priority_level = Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.REQUESTED)
    
    
    video_url = Column(Text, nullable=True) 
    
   
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
    
    
    patient = relationship(
        "User", 
        back_populates="patient_appointments", 
        foreign_keys=[patient_id],
        lazy="joined"
    )

    
    doctor = relationship(
        "User", 
        back_populates="doctor_appointments", 
        foreign_keys=[doctor_id],
        lazy="joined"
    )
