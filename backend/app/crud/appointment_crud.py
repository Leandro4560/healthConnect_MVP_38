from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.config import settings
from app.excepciones import BusinessException
import logging

from app.models.appointment import Appointment, PriorityLevel, AppointmentStatus
from app.models.user import User, UserRole 
from app.utils import schemas as datos
# Intentar importar la excepción específica de servicios_meet_calendar si existe
try:
    from app.utils.servicios_meet_calendar import create_google_calendar_event, GoogleCalendarError
except Exception:
    from app.utils.servicios_meet_calendar import create_google_calendar_event
    class GoogleCalendarError(Exception):
        pass

from app.crud.user_crud import get_user 
from app.services.supabase_client import insert_appointment

logger = logging.getLogger(__name__)


def create_appointment(db: Session, appointment_data: datos.AppointmentCreate, patient: User) -> Appointment:
    """
    Crea una nueva cita en la base de datos y, si es virtual, un evento en Google Calendar
    del doctor asignado.
    """
    patient_id = patient.id

    # Normalizar start_time y end_time y ahora para evitar comparar naive vs aware
    start_time = appointment_data.start_time
    end_time = appointment_data.end_time

    # Determinar zona objetivo (desde settings.TIME_ZONE o UTC)
    try:
        tz = ZoneInfo(settings.TIME_ZONE)
    except Exception:
        tz = timezone.utc

    if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
        start_time = start_time.replace(tzinfo=tz)
    if end_time.tzinfo is None or end_time.tzinfo.utcoffset(end_time) is None:
        end_time = end_time.replace(tzinfo=tz)

    now = datetime.now(tz=start_time.tzinfo)

    if start_time <= now:
        # BusinessException espera (status_code, message)
        raise BusinessException(400, "La fecha/hora de inicio debe ser futura.")

    if not appointment_data.doctor_id:
        raise BusinessException(400, "Debe seleccionar un doctor para agendar la cita.")

    doctor = get_user(db, user_id=appointment_data.doctor_id)
    if not doctor or doctor.role != UserRole.DOCTOR:
        raise BusinessException(404, "Doctor no encontrado o rol incorrecto.")

    # Conflicto de horarios - usar las fechas normalizadas
    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == appointment_data.doctor_id,
        Appointment.status != AppointmentStatus.CANCELED,
        Appointment.start_time < end_time,
        Appointment.end_time > start_time
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
                start_time=start_time,
                end_time=end_time,
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
        start_time=start_time,
        end_time=end_time,
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

    # Intentar sincronizar con Supabase (no debe romper la creación local)
    try:
        # Obtener los UUIDs de Supabase guardados en los usuarios (si están)
        patient_supabase_id = getattr(patient, "supabase_id", None)
        doctor_supabase_id = getattr(doctor, "supabase_id", None)

        payload = {
            "start_time": db_appointment.start_time.isoformat(),
            "end_time": db_appointment.end_time.isoformat(),
            "is_virtual": bool(db_appointment.is_virtual),
            "priority_level": db_appointment.priority_level.name if hasattr(db_appointment.priority_level, "name") else str(db_appointment.priority_level),
            "notes": db_appointment.notes,
            "status": db_appointment.status.name if hasattr(db_appointment.status, "name") else str(db_appointment.status),
            "video_url": db_appointment.video_url,
            "google_event_id": db_appointment.google_event_id
        }

        # Añadir sólo si tenemos los UUIDs de Supabase (las columnas en Supabase esperan UUID)
        if patient_supabase_id:
            payload["patient_id"] = str(patient_supabase_id)
        if doctor_supabase_id:
            payload["doctor_id"] = str(doctor_supabase_id)

        # Si ninguno de los dos UUID está disponible, omitimos la inserción en Supabase
        if "patient_id" in payload or "doctor_id" in payload:
            insert_appointment(payload)
        else:
            logger.warning("No se encontró supabase_id para patient/doctor — sincronización con Supabase omitida.")
    except Exception:
        # ya fue logged en supabase_client; no interrumpe la respuesta a cliente
        pass

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
        try:
            tz = ZoneInfo(settings.TIME_ZONE)
        except Exception:
            tz = timezone.utc
        now_with_tz = datetime.now(tz)
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
        try:
            tz = ZoneInfo(settings.TIME_ZONE)
        except Exception:
            tz = timezone.utc
        now_with_tz = datetime.now(tz)
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
