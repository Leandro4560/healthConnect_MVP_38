from sqlalchemy.orm import Session
from app.models.appointment import Appointment, PriorityLevel, AppointmentStatus
from app.models.user import User, UserRole
from app.utils import schemas as datos
from app.excepciones import BusinessException, GoogleCalendarError
from app.utils.servicios_meet_calendar import create_google_calendar_event
from app.crud.user_crud import get_user_by_id, get_user_by_email # Necesitas un CRUD de usuario completo
from app.config import settings
from datetime import datetime
from typing import List, Optional

# --- Lógica de Negocio de Citas (CRUD) ---

def create_appointment(db: Session, appointment_data: datos.AppointmentCreate, patient: User) -> Appointment:
    """
    Crea una nueva cita en la base de datos y, si es virtual, un evento en Google Calendar
    del doctor asignado.
    """
    # 1. Validación de Roles y Datos
    
    # El paciente es el que crea la cita, por lo que su ID ya está disponible
    patient_id = patient.id
    
    # Debe haber un doctor seleccionado
    if not appointment_data.doctor_id:
        raise BusinessException(400, "Debe seleccionar un doctor para agendar la cita.")
        
    # El doctor debe existir y tener rol DOCTOR
    doctor = get_user_by_id(db, user_id=appointment_data.doctor_id)
    if not doctor or doctor.role != UserRole.DOCTOR:
        raise BusinessException(404, "Doctor no encontrado o rol incorrecto.")
        
    # 2. Verificar disponibilidad (Lógica simplificada: no se permiten solapamientos)
    # Buscamos citas existentes para el doctor en el rango de tiempo
    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == appointment_data.doctor_id,
        Appointment.status != AppointmentStatus.CANCELED, # Ignoramos citas canceladas
        # El nuevo inicio debe ser antes de que termine una cita existente
        Appointment.start_time < appointment_data.end_time,
        # El nuevo fin debe ser después de que inicie una cita existente
        Appointment.end_time > appointment_data.start_time
    ).first()

    if existing_appointment:
        # En una aplicación real, se devolvería un 409 Conflict.
        raise BusinessException(400, "El doctor no está disponible en ese horario. Por favor, seleccione otro.")

    # 3. Creación del Evento de Google Calendar (Si es virtual)
    video_url = None
    if appointment_data.is_virtual:
        if not doctor.google_refresh_token:
            raise BusinessException(400, "El doctor aún no ha conectado su Google Calendar. No se puede agendar la cita virtual.")
        
        try:
            # Creamos el evento en Google Calendar
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
            # Si Google falla, la transacción debe abortarse o la cita debe marcarse diferente
            raise BusinessException(500, f"Error al crear el evento de Google Calendar: {e.detail}")

    # 4. Crear el Objeto Cita en la DB
    db_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=appointment_data.doctor_id,
        start_time=appointment_data.start_time,
        end_time=appointment_data.end_time,
        is_virtual=appointment_data.is_virtual,
        priority_level=appointment_data.priority_level,
        notes=appointment_data.notes,
        video_url=video_url,
        # Estado inicial
        status=AppointmentStatus.SCHEDULED 
    )

    # 5. Guardar en la base de datos
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
    ).order_by(Appointment.start_time.asc()) # Ordenar por fecha ascendente

    if not include_past:
        # Filtra solo las citas que comienzan en el futuro
        # Opcionalmente, puedes añadir 'OR' para incluir citas 'IN_PROGRESS' si lo necesitas.
        query = query.filter(Appointment.start_time >= datetime.now(settings.TIME_ZONE_INFO))

    return query.all()

def get_appointments_by_doctor(db: Session, doctor_id: int, include_past: bool = False) -> List[Appointment]:
    """
    Obtiene todas las citas agendadas para un doctor.
    Si include_past es False, solo devuelve citas futuras o activas.
    """
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id
    ).order_by(Appointment.start_time.asc()) # Ordenar por fecha ascendente

    if not include_past:
        # Filtra solo las citas que comienzan en el futuro
        query = query.filter(Appointment.start_time >= datetime.now(settings.TIME_ZONE_INFO))

    return query.all()