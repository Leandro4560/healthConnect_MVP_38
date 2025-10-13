from sqlalchemy.orm import Session
from app.models.appointment import Appointment, PriorityLevel, AppointmentStatus
from app.models.user import User, UserRole
from app.utils import schemas as datos
from app.excepciones import BusinessException, GoogleCalendarError
from app.utils.servicios_meet_calendar import create_google_calendar_event
from app.crud.user_crud import get_user_by_id, get_user_by_email 
from app.config import settings
from datetime import datetime
from typing import List, Optional


def create_appointment(db: Session, appointment_data: datos.AppointmentCreate, patient: User) -> Appointment:
    """
    Crea una nueva cita en la base de datos y, si es virtual, un evento en Google Calendar
    del doctor asignado.
    """
   
    patient_id = patient.id
    
    if not appointment_data.doctor_id:
        raise BusinessException(400, "Debe seleccionar un doctor para agendar la cita.")

    doctor = get_user_by_id(db, user_id=appointment_data.doctor_id)
    if not doctor or doctor.role != UserRole.DOCTOR:
        raise BusinessException(404, "Doctor no encontrado o rol incorrecto.")
     
    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == appointment_data.doctor_id,
        Appointment.status != AppointmentStatus.CANCELED, 
        Appointment.start_time < appointment_data.end_time,
        Appointment.end_time > appointment_data.start_time
    ).first()

    if existing_appointment:
        raise BusinessException(400, "El doctor no está disponible en ese horario. Por favor, seleccione otro.")

    video_url = None
    if appointment_data.is_virtual:
        if not doctor.google_refresh_token:
            raise BusinessException(400, "El doctor aún no ha conectado su Google Calendar. No se puede agendar la cita virtual.")
        
        try:
            meet_info = create_google_calendar_event(
                doctor=doctor,
                summary=f"Cita con el Dr. {doctor.full_name}",
                description=f"Videoconsulta agendada con el paciente {patient.full_name}.",
                start_time=appointment_data.start_time,
                end_time=appointment_data.end_time,
                patient_email=patient.email
            )
            video_url = meet_info['meet_url']
            
        except GoogleCalendarError as e:
            raise BusinessException(500, f"Error al crear el evento de Google Calendar: {e.detail}")

    db_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=appointment_data.doctor_id,
        start_time=appointment_data.start_time,
        end_time=appointment_data.end_time,
        is_virtual=appointment_data.is_virtual,
        priority_level=appointment_data.priority_level,
        notes=appointment_data.notes,
        video_url=video_url,
        status=AppointmentStatus.SCHEDULED 
    )

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return db_appointment

def get_appointments_by_patient(db: Session, patient_id: int, include_past: bool = False) -> List[Appointment]:
    """
    Obtiene todas las citas de un paciente.
    Si include_past es False, solo devuelve citas futuras o activas.
    """
    query = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Appointment.start_time.asc()) 

    if not include_past:
       
        query = query.filter(Appointment.start_time >= datetime.now(settings.TIME_ZONE_INFO))

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
        query = query.filter(Appointment.start_time >= datetime.now(settings.TIME_ZONE_INFO))

    return query.all()
