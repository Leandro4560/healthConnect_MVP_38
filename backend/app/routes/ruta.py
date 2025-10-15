from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Annotated, Optional
# CORRECCIÓN: Importar RedirectResponse aquí para que Pylance lo encuentre.
from starlette.responses import RedirectResponse 


# CORRECCIONES EN RUTAS RELATIVAS (usando doble punto '..')
# Subir al nivel 'app' y buscar los módulos:
from ..database import get_db
from ..utils import schemas as datos
from ..utils import security as validacion_api 
from ..config import settings
from ..utils.google_tokens import get_google_auth_flow, exchange_code_for_tokens
from ..utils.servicios_meet_calendar import create_google_calendar_event 
from ..excepciones import GoogleCalendarError 
from ..models.user import User, UserRole 
from ..utils.security import CurrentUserDep 


router = APIRouter(
    tags=["Autenticación"],
)

# ... (El resto del código sigue igual)



SessionDep = Annotated[Session, Depends(get_db)]




@router.post("/register", response_model=datos.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_data: datos.UserCreate, db: SessionDep):
    """
    Registra un nuevo usuario en el sistema.
    """
    
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    
    hashed_password = validacion_api.get_password_hash(user_data.password)

    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role 
    )

    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=datos.Token)
def login_for_access_token(user_data: datos.UserLogin, db: SessionDep):
    """
    Verifica las credenciales y devuelve un token JWT si son válidas.
    """
    
    db_user = db.query(User).filter(User.email == user_data.email).first()
    
    
    if not db_user or not validacion_api.verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de acceso inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )


    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = validacion_api.create_access_token(
        data={"user_id": db_user.id, "role": db_user.role.value},
        expires_delta=access_token_expires
    )
    
    
    return {"access_token": access_token}




@router.get("/google/login")
def google_login():
    """
    Inicia el flujo de autenticación de Google OAuth 2.0.
    Redirige al usuario a la página de consentimiento de Google.
    """
    flow = get_google_auth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
    
        prompt='consent' 
    )
    return RedirectResponse(authorization_url)


@router.get("/google/callback")
def google_callback(code: str, db: SessionDep):
    """
    Maneja la respuesta del servidor de Google (callback).
    Intercambia el código por tokens y guarda el refresh_token del doctor.
    """
    try:
        
        tokens = exchange_code_for_tokens(code)
        refresh_token = tokens.get('refresh_token')
        google_email = tokens.get('email')

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo obtener el token de refresco (Refresh Token). Reintente, asegurándose de dar todos los permisos."
            )

        
        db_user = db.query(User).filter(User.email == google_email).first()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Usuario con email {google_email} no encontrado en la base de datos."
            )

        
        db_user.google_refresh_token = refresh_token
        db.commit()

        
        return RedirectResponse(
            url="/", 
            status_code=status.HTTP_302_FOUND,
            headers={"X-Auth-Status": "Google Calendar conectado con éxito."}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en el callback de Google: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al procesar la autenticación de Google."
        )




class AppointmentCreateExample(datos.BaseModel):
    patient_email: str
    start_time: datetime
    end_time: datetime
    summary: str = "Consulta Médica Online"
    description: str = "Videoconsulta agendada por el sistema."


@router.post("/appointments/create", status_code=status.HTTP_201_CREATED)
def create_appointment_with_meet(
    appointment_data: AppointmentCreateExample,
    db: SessionDep,
    current_user: CurrentUserDep
):
    """
    Crea una nueva cita. Si el usuario actual es un Doctor,
    intenta crear un evento de Google Calendar con un enlace de Meet.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Solo los doctores pueden crear citas de calendario."
        )

    
    if not current_user.google_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El doctor debe conectar su calendario de Google a través de /auth/google/login primero."
        )


    try:
        meet_info = create_google_calendar_event(
            doctor=current_user,
            summary=appointment_data.summary,
            description=appointment_data.description,
            start_time=appointment_data.start_time,
            end_time=appointment_data.end_time,
            patient_email=appointment_data.patient_email
        )
        
        return {
            "message": "Cita agendada y evento de Google Calendar/Meet creado con éxito.",
            "meet_url": meet_info['meet_url'],
            "calendar_url": meet_info['event_url']
        }

    except GoogleCalendarError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el evento de Google: {e.detail}"
        )

    except Exception as e:
        print(f"Error al crear la cita: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la cita."
        )