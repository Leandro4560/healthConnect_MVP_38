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
    current_user: User = Depends(CurrentUserDep),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva cita médica. Solo un paciente puede agendar citas.
    Ahora delega en el CRUD corregido.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los pacientes pueden agendar citas."
        )

    created = appointment_crud.create_appointment(db=db, appointment_data=appointment_data, patient=current_user)
    return created

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

# Nueva ruta: obtener una cita por id (accesible solo al doctor o paciente involucrado)
@router.get("/{appointment_id}", response_model=datos.AppointmentResponse)
def get_appointment_by_id(
    appointment_id: int,
    current_user: User = Depends(CurrentUserDep),
    db: Session = Depends(get_db)
):
    """
    Recupera una cita por su id. Solo el paciente que la creó o el doctor asignado pueden verla.
    """
    # Intentar usar el CRUD si existe, si no hacer consulta directa
    if hasattr(appointment_crud, "get_appointment_by_id"):
        appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    else:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada.")

    # Permisos: solo doctor asignado o paciente creador
    if current_user.role == UserRole.DOCTOR:
        if appointment.doctor_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para ver esta cita.")
    elif current_user.role == UserRole.PATIENT:
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para ver esta cita.")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol no autorizado para esta operación.")

    return appointment

# Nueva ruta: cancelar una cita (patient o doctor asignado pueden cancelar)
@router.put("/{appointment_id}/cancel", response_model=datos.AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(CurrentUserDep),
    db: Session = Depends(get_db)
):
    """
    Cancela la cita especificada. Solo el paciente que la creó o el doctor asignado pueden cancelarla.
    No permite cancelar citas en el pasado ni re-cancelar una ya cancelada.
    """
    # Obtener cita
    if hasattr(appointment_crud, "get_appointment_by_id"):
        appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    else:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada.")

    # Verificar permisos
    if current_user.role == UserRole.PATIENT and appointment.patient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para cancelar esta cita.")
    if current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para cancelar esta cita.")

    # Validaciones de estado/tiempo
    if appointment.status == AppointmentStatus.CANCELED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cita ya ha sido cancelada.")
    if appointment.start_time <= datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pueden cancelar citas que ya han comenzado o que están en el pasado.")

    # Delegar al CRUD si existe una función específica que gestione la cancelación (por ejemplo para sincronizar con Google)
    if hasattr(appointment_crud, "cancel_appointment"):
        updated = appointment_crud.cancel_appointment(db, appointment_id, canceled_by=current_user)
        return updated

    # Fallback: actualización simple de estado
    appointment.status = AppointmentStatus.CANCELED
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment

# Podrías añadir la ruta @router.get("/{appointment_id}") para ver una cita específica
# y @router.put("/{appointment_id}/cancel") para cancelar una cita.