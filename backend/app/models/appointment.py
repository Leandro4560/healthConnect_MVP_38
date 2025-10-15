from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

# Importación absoluta
from app.database import Base 

class Appointment(Base):
    """
    Modelo de SQLAlchemy para la tabla de Citas Médicas.
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Llave foránea que apunta al doctor que agendó la cita
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    
    patient_name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="Pendiente") # Ej: Pendiente, Agendada, Cancelada
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Nuevos campos para la integración con Google Calendar
    google_event_id = Column(String, nullable=True)
    google_meet_link = Column(String, nullable=True)
    
    # Relación para saber a qué doctor pertenece la cita
    doctor = relationship("User", back_populates="appointments") 