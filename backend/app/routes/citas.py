from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List


from app.database import get_db
from app.utils.security import CurrentUserDep
from app.utils import schemas as datos
from app.models.user import User, UserRole
from app.models.appointment import Appointment
from app.utils.servicios_meet_calendar import create_google_calendar_event
from app.excepciones import GoogleCalendarError


router = APIRouter(
    tags=["Citas Médicas"],
    
    dependencies=[Depends(CurrentUserDep)], 
)



@router.post("/", response_model=datos.AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: datos.AppointmentCreate,
    current_user: User = Depends(CurrentUserDep),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva cita médica y, si el doctor ha conectado su cuenta,
    crea un evento de Google Calendar/Meet.
    """
    
    if current_user.role != UserRole.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los doctores pueden crear citas."
        )

    
    if appointment_data.start_time <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La hora de inicio de la cita debe ser en el futuro."
        )

    
    db_appointment = Appointment(
        patient_name=appointment_data.patient_name,
        doctor_id=current_user.id, 
        start_time=appointment_data.start_time,
        end_time=appointment_data.end_time,
        description=appointment_data.description,
        status="Pendiente"
    )

    
    if current_user.google_access_token:
        try:
            meet_link, event_id = create_google_calendar_event(
                access_token=current_user.google_access_token,
                summary=f"Consulta con {appointment_data.patient_name}",
                description=appointment_data.description,
                start_time=appointment_data.start_time.isoformat() + 'Z', 
                end_time=appointment_data.end_time.isoformat() + 'Z',
                timezone="UTC" 
            )
            
            db_appointment.google_meet_link = meet_link
            db_appointment.google_event_id = event_id
            db_appointment.status = "Agendada"
            
        except GoogleCalendarError as e:
            
            print(f"Error al crear evento de Google Calendar para el usuario {current_user.id}: {e}")
            db_appointment.status = "Error Calendar"
            
        except Exception as e:
            print(f"Error desconocido al interactuar con Google Calendar: {e}")
            db_appointment.status = "Error Calendar"
    
    else:
        
        db_appointment.status = "Pendiente"



    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return db_appointment


@router.get("/", response_model=List[datos.AppointmentResponse])
def get_appointments(
    current_user: User = Depends(CurrentUserDep),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las citas agendadas por el doctor actualmente autenticado.
    """
    
    if current_user.role != UserRole.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los doctores pueden ver sus citas."
        )

    
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == current_user.id
    ).order_by(Appointment.start_time).all()

    return appointments


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from typing import Optional
