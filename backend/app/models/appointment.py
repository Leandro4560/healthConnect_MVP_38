import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

# Importación de la clase Base de tu configuración de base de datos
from app.database import Base 
from app.models.user import User # Necesario para las relaciones (ForeignKey)

# --- ENUMS (Definiciones de estados y prioridades) ---

class PriorityLevel(enum.Enum):
    """Nivel de prioridad de la cita."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"

class AppointmentStatus(enum.Enum):
    """Estado actual de la cita."""
    PENDING = "pending"         # Solicitada, esperando confirmación del doctor/sistema
    CONFIRMED = "confirmed"     # Doctor ha aceptado, evento en Google Calendar creado
    CANCELLED = "cancelled"     # Cancelada por paciente o doctor
    COMPLETED = "completed"     # Cita finalizada
    NO_SHOW = "no_show"         # Paciente no se presentó

# --- MODELO ORM (Tabla de citas) ---

class Appointment(Base):
    """
    Representa una cita médica programada entre un paciente y un doctor.
    """
    __tablename__ = "appointment"

    id = Column(Integer, primary_key=True, index=True)
    
    # Llave foránea al paciente que solicita la cita (User.id)
    patient_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    
    # Llave foránea al doctor asignado (User.id). Puede ser nulo si la asignación es posterior.
    doctor_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=True)

    # Horario de la cita
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Detalles de la cita
    is_virtual = Column(Boolean, default=True) # Indica si es Meet o presencial
    notes = Column(String, nullable=True)
    
    # Campos de control y estado
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False)
    priority_level = Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- Integración con Google Calendar ---
    
    # ID del evento en Google Calendar (necesario para actualizarlo o cancelarlo)
    google_event_id = Column(String, index=True, nullable=True) 
    
    # URL de Google Meet/Video Conferencia
    video_url = Column(String, nullable=True) 

    # --- Relaciones ---
    
    # Relación de la cita con el paciente
    patient = relationship(
        "User", 
        foreign_keys=[patient_id], 
        backref="appointments_as_patient"
    )
    
    # Relación de la cita con el doctor asignado
    doctor = relationship(
        "User", 
        foreign_keys=[doctor_id], 
        backref="appointments_as_doctor"
    )
