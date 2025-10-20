# app/routes/citas.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

# Importaciones locales
from app.database import get_db
from app.utils.security import CurrentUserDep, requires_doctor, requires_patient 
from app.utils import schemas as datos
from app.models.user import User, UserRole
from app.models.appointment import Appointment, AppointmentStatus
from app.utils.servicios_meet_calendar import create_google_calendar_event
from app.excepciones import GoogleCalendarError, BusinessException
from app.crud import appointment_crud 
from app.crud.user_crud import get_user_by_id

router = APIRouter(
    tags=["Citas Médicas"],
    # Todas las rutas requieren autenticación
    dependencies=[Depends(CurrentUserDep)], 
)


@router.post("/", response_model=datos.AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: datos.AppointmentCreate,
    current_user: User = Depends(CurrentUserDep), # El usuario autenticado es el paciente
    db: Session = Depends(get_db)
):
    """
    Crea una nueva cita médica. Solo un paciente puede agendar citas.
    Si el doctor tiene Google Token, crea un evento en Calendar/Meet.
    """
    # Restricción: Solo un paciente puede agendar citas
    if current_user.role != UserRole.PATIENT: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los pacientes pueden agendar citas."
        )

    # Validación de tiempo (se puede mejorar con validación de slots disponibles)
    if appointment_data.start_time <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La hora de inicio de la cita debe ser en el futuro."
        )

    # 1. Obtener el doctor
    doctor = get_user_by_id(db, appointment_data.doctor_id)
    if not doctor or doctor.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor no encontrado o rol incorrecto."
        )

    # 2. Preparar el modelo de Appointment
    db_appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=appointment_data.doctor_id,
        start_time=appointment_data.start_time,
        end_time=appointment_data.end_time,
        is_virtual=appointment_data.is_virtual,
        priority_level=AppointmentStatus(appointment_data.priority_level).value if appointment_data.priority_level else AppointmentStatus.PENDIENTE.value,
        notes=appointment_data.description
    )
    
    # 3. Interacción con Google Calendar 
    if db_appointment.is_virtual and doctor.google_refresh_token:
        try:
            summary = f"Cita {current_user.full_name} ({current_user.email})"
            description = appointment_data.description or "Cita Médica Virtual"
            
            calendar_result = create_google_calendar_event(
                doctor=doctor,
                summary=summary,
                description=description,
                start_time=db_appointment.start_time,
                end_time=db_appointment.end_time,
                patient_email=current_user.email
            )
            
            db_appointment.video_url = calendar_result.get("meet_url")
            db_appointment.google_event_id = calendar_result.get("event_id")
            db_appointment.status = AppointmentStatus.SCHEDULED # Agendada en Google
            
        except GoogleCalendarError as e:
            # Si Google falla, se crea en estado PENDIENTE y se registra el error
            print(f"Error al crear evento de Google Calendar: {e}")
            db_appointment.status = AppointmentStatus.PENDIENTE 
            db_appointment.notes = (db_appointment.notes or "") + f" [ERROR CALENDAR: {e.detail}]"
            
    else:
        db_appointment.status = AppointmentStatus.PENDIENTE


    # 4. Guardar en DB
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return db_appointment


@router.get("/doctor", response_model=List[datos.AppointmentResponse], dependencies=[Depends(requires_doctor)])
def get_appointments_for_doctor(
    current_user: User = Depends(CurrentUserDep),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las citas agendadas para el doctor actualmente autenticado.
    """
    appointments = appointment_crud.get_appointments_by_doctor(
        db, 
        doctor_id=current_user.id, 
        include_past=False # Solo citas futuras por defecto
    )
    
    return appointments

@router.get("/patient", response_model=List[datos.AppointmentResponse], dependencies=[Depends(requires_patient)])
def get_appointments_for_patient(
    current_user: User = Depends(CurrentUserDep),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las citas agendadas por el paciente actualmente autenticado.
    """
    appointments = appointment_crud.get_appointments_by_patient(
        db, 
        patient_id=current_user.id, 
        include_past=False # Solo citas futuras por defecto
    )
    
    return appointments

# Podrías añadir la ruta @router.get("/{appointment_id}") para ver una cita específica
# y @router.put("/{appointment_id}/cancel") para cancelar una cita.