from fastapi import APIRouter, Depends, status, HTTPException
from typing import Optional, List
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from app.database import get_db
from app.utils import schemas
from app.crud import user_crud
from app.utils import security as auth_security
from app.utils import auth_utils 
from app.excepciones import BusinessException, CredencialesInvalidas
from app.models.user import User, UserRoleDB
from app.config import settings, UserRole
from app.utils.security import CurrentUserDep 

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en la base de datos (con hash de contraseña).
    Permite registrar Doctores, Administradores y Pacientes.
    """
    if user_crud.get_user_by_email(db, email=user_data.email):
        raise BusinessException(status_code=409, detail="El email ya está registrado.")
    
    
    role_map = {
        UserRole.DOCTOR: UserRoleDB.DOCTOR,
        UserRole.ADMIN: UserRoleDB.ADMIN,
        UserRole.PACIENTE: UserRoleDB.PACIENTE
    }
    
    role_db = role_map.get(user_data.role, UserRoleDB.PACIENTE) 
    
    db_user = user_crud.create_user(db, user=user_data, role=role_db)
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Autenticación por credenciales (email/contraseña), devuelve un token JWT.
    """
    user = user_crud.get_user_by_email(db, email=form_data.email)
    
    if not user or not auth_security.verify_password(form_data.password, user.hashed_password):
        # Lanza excepción HTTP 401 Unauthorized
        raise CredencialesInvalidas(detail="Email o contraseña incorrectos")
        

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_security.create_access_token(
        data={"user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/google/login", description="Inicia el flujo de OAuth de Google.")
def google_login():
    """
    Redirige al usuario al flujo de consentimiento de Google para iniciar sesión.
    Nota: En un caso de uso típico de Doctor, este endpoint se usaría para 
    vincular la cuenta y obtener el Refresh Token para Google Calendar.
    """
   
    state_token = auth_security.get_password_hash(settings.SECRET_KEY + str(datetime.now()))[:32] 
    auth_url = auth_utils.get_google_login_url(state=state_token)
    
    return RedirectResponse(auth_url, status_code=status.HTTP_302_FOUND)


@router.get("/google/callback", response_model=schemas.Token)
def google_callback(
    code: str, 
    
    state: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """
    Callback de Google: Recibe el código, lo intercambia por tokens de Google,
    actualiza el Refresh Token del Doctor (si aplica) y devuelve el JWT de la aplicación.
    """
    try:
        
        tokens = auth_utils.exchange_code_for_tokens(auth_code=code)
        
        access_token_google = tokens.get("access_token")
        refresh_token_google = tokens.get("refresh_token") 

        
        user_info = auth_utils.get_google_user_info(access_token=access_token_google)
        email = user_info.get("email")
        full_name = user_info.get("name")
        
        if not email:
            raise BusinessException(400, "El perfil de Google no proporcionó un email.")
        
        user = user_crud.get_user_by_email(db, email=email)

       
        is_doctor_registration = bool(refresh_token_google) 
        
        if not user:
           
            temp_password = auth_security.get_password_hash(email + settings.SECRET_KEY) 
            
            user_data = schemas.UserCreate(
                email=email,
                full_name=full_name,
                password=temp_password,
                
                role=UserRole.DOCTOR if is_doctor_registration else UserRole.PACIENTE
            )
            
           
            user_data.google_refresh_token = refresh_token_google
            
            user = user_crud.create_user(
                db, 
                user=user_data,
                role=UserRoleDB.DOCTOR if is_doctor_registration else UserRoleDB.PACIENTE
            )
            
       
        elif user.role.value == UserRole.DOCTOR and refresh_token_google:
          
            if user.google_refresh_token != refresh_token_google:
                user.google_refresh_token = refresh_token_google
                db.commit()
            
       
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_security.create_access_token(
            data={"user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return schemas.Token(access_token=access_token, token_type="bearer")

    except (BusinessException, CredencialesInvalidas) as e:
        
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error desconocido en google_callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la autenticación de Google."
        )



@router.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: CurrentUserDep):
    """
    Retorna la información del usuario autenticado (requiere JWT válido).
    """
    return current_user
