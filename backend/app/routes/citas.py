from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.appointment import Appointment, AppointmentStatus, PriorityLevel
from app.utils.schemas import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.utils.security import get_current_user 


router = APIRouter(prefix="/citas", tags=["Citas Médicas"])


def assign_priority_and_schedule(db: Session, appointment: Appointment):
    
    
    priority_score = appointment.urgency_level.value
    
   
    available_doctor = db.query(User).filter(User.role == UserRole.DOCTOR).first()

    if available_doctor:
        appointment.doctor_id = available_doctor.id
        
       
        if priority_score == PriorityLevel.CRITICAL.value:
            scheduled_time = datetime.utcnow() + timedelta(minutes=30)
        elif priority_score == PriorityLevel.HIGH.value:
            scheduled_time = datetime.utcnow() + timedelta(hours=2)
        else:
            scheduled_time = datetime.utcnow() + timedelta(hours=24)

        appointment.scheduled_at = scheduled_time
        appointment.status = AppointmentStatus.CONFIRMED
        
 
        
    else:
       
        appointment.status = AppointmentStatus.PENDING 

    return appointment



@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def request_appointment(
    appointment_data: AppointmentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los pacientes pueden solicitar citas."
        )


    db_appointment = Appointment(
        patient_id=current_user.id,
        reason=appointment_data.reason,
        urgency_level=appointment_data.urgency_level,
        is_telemedicine=appointment_data.is_telemedicine,
        status=AppointmentStatus.PENDING 
    )
    
    
    db_appointment = assign_priority_and_schedule(db, db_appointment)

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment

@router.get("/my", response_model=List[AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    if current_user.role == UserRole.PATIENT:
        appointments = db.query(Appointment).filter(
            Appointment.patient_id == current_user.id
        ).all()
    elif current_user.role == UserRole.DOCTOR:
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == current_user.id
        ).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso no autorizado para este rol. Por favor use una ruta específica de administrador."
        )
        
    return appointments
