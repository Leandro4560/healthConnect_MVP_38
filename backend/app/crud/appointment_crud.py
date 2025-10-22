from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import pytz 

from app.models.appointment import Appointment, PriorityLevel, AppointmentStatus
from app.models.user import User, UserRole 
from app.utils import schemas as datos
from app.excepciones import BusinessException, GoogleCalendarError
from app.utils.servicios_meet_calendar import create_google_calendar_event
from app.crud.user_crud import get_user 
class Settings:
    """Configuración simulada para TIME_ZONE_INFO."""
    
    TIME_ZONE_INFO = pytz.timezone('UTC') 
settings = Settings() 


def create_appointment(db: Session, appointment_data: datos.AppointmentCreate, patient: User) -> Appointment:
    """
    Crea una nueva cita en la base de datos y, si es virtual, un evento en Google Calendar
    del doctor asignado.
    """
    from app.excepciones import BusinessException

    patient_id = patient.id

    if appointment_data.start_time <= datetime.now():
        raise BusinessException(400, "La hora de inicio de la cita debe ser en el futuro.")

    if not appointment_data.doctor_id:
        raise BusinessException(400, "Debe seleccionar un doctor para agendar la cita.")

    doctor = get_user(db, user_id=appointment_data.doctor_id)
    if not doctor or doctor.role != UserRole.DOCTOR:
        raise BusinessException(404, "Doctor no encontrado o rol incorrecto.")

    # Conflicto de horarios
    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == appointment_data.doctor_id,
        Appointment.status != AppointmentStatus.CANCELED,
        Appointment.start_time < appointment_data.end_time,
        Appointment.end_time > appointment_data.start_time
    ).first()

    if existing_appointment:
        raise BusinessException(400, "El doctor no está disponible en ese horario. Por favor, seleccione otro.")

    # Mapear prioridad (si se pasa)
    if appointment_data.priority_level:
        try:
            priority = PriorityLevel[appointment_data.priority_level]
        except KeyError:
            # intentar mayúsculas
            try:
                priority = PriorityLevel[appointment_data.priority_level.upper()]
            except Exception:
                priority = PriorityLevel.MEDIUM
    else:
        priority = PriorityLevel.MEDIUM

    video_url = None
    google_event_id = None
    status = AppointmentStatus.PENDIENTE

    if appointment_data.is_virtual:
        if not doctor.google_refresh_token:
            raise BusinessException(400, "El doctor aún no ha conectado su Google Calendar. No se puede agendar la cita virtual.")

        try:
            meet_info = create_google_calendar_event(
                doctor=doctor,
                summary=f"Cita con el Dr. {doctor.full_name}",
                description=appointment_data.description or f"Videoconsulta con {patient.full_name}",
                start_time=appointment_data.start_time,
                end_time=appointment_data.end_time,
                patient_email=patient.email
            )
            video_url = meet_info.get('meet_url')
            google_event_id = meet_info.get('event_id')
            status = AppointmentStatus.SCHEDULED
        except GoogleCalendarError as e:
            # Si falla Google, dejamos PENDIENTE y devolvemos error lógico
            raise BusinessException(500, f"Error al crear el evento de Google Calendar: {getattr(e, 'detail', str(e))}")

    db_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=appointment_data.doctor_id,
        start_time=appointment_data.start_time,
        end_time=appointment_data.end_time,
        is_virtual=appointment_data.is_virtual,
        priority_level=priority,
        notes=appointment_data.description,
        video_url=video_url,
        status=status,
        google_event_id=google_event_id
    )

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return db_appointment


# --- Funciones de Obtención (READ) ---

def get_appointment(db: Session, appointment_id: int) -> Optional[Appointment]:
    """Obtiene una cita por su ID."""
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()

def get_appointments_by_patient(db: Session, patient_id: int, include_past: bool = False) -> List[Appointment]:
    """
    Obtiene todas las citas de un paciente.
    Si include_past es False, solo devuelve citas futuras o activas.
    """
    query = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Appointment.start_time.asc()) 

    if not include_past:
        
        now_with_tz = datetime.now(settings.TIME_ZONE_INFO)
        query = query.filter(Appointment.start_time >= now_with_tz)

    return query.all()

def get_appointments_by_doctor(db: Session, doctor_id: int, include_past: bool = False) -> List[Appointment]:
    """
    Obtiene todas las citas agendadas para un doctor.
    Si include_past es False, solo devuelve citas futuras o activas.
    """
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id
    ).order_by(Appointment.start_time.asc()) 

    if not include_past:
        
        now_with_tz = datetime.now(settings.TIME_ZONE_INFO)
        query = query.filter(Appointment.start_time >= now_with_tz)

    return query.all()


def update_appointment_status(db: Session, appointment_id: int, new_status: AppointmentStatus) -> Optional[Appointment]:
    """Actualiza solo el estado de una cita."""
    db_appointment = get_appointment(db, appointment_id)
    if db_appointment:
        db_appointment.status = new_status
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    return None

def delete_appointment(db: Session, appointment_id: int) -> bool:
    """Elimina una cita por su ID."""
    db_appointment = get_appointment(db, appointment_id)
    if db_appointment:
        db.delete(db_appointment)
        db.commit()
        return True
    return False
