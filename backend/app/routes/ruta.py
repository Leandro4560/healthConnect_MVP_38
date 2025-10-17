from fastapi import APIRouter, Depends, status, HTTPException
from typing import Optional
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import secrets  
import string  


from supabase import create_client, Client
import os
from dotenv import load_dotenv


from app.database import get_db
from app.utils import schemas
from app.crud import user_crud
from app.utils import security as auth_security
from app.utils import auth_utils 
from app.excepciones import BusinessException, CredencialesInvalidas
from app.models.user import User, UserRole 
from app.config import settings, UserRole as ConfigRole 
from app.utils.security import CurrentUserDep 


load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY_ANON = os.getenv("SUPABASE_KEY_ANON")

SUPABASE_CLIENT: Client = create_client(SUPABASE_URL, SUPABASE_KEY_ANON)

def get_supabase_client() -> Client:
    """Dependencia para obtener el cliente Supabase."""
    return SUPABASE_CLIENT




def generate_random_password(length=12):
    """Genera una contraseña aleatoria y segura para uso temporal en Supabase Auth."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        
        if (any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                any(c.isdigit() for c in password)):
            return password


router = APIRouter(
    tags=["Autenticación"]
)


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: schemas.UserCreate, 
    db: Session = Depends(get_db),
    supabase_client: Client = Depends(get_supabase_client) 
):
    """
    Crea un nuevo usuario en Supabase Auth y luego lo sincroniza en tu DB local (ORM).
    El ID (UUID) de Supabase se usará como ID local para la FK con la tabla 'profiles' de Supabase.
    """
    if user_crud.get_user_by_email(db, email=user_data.email):
        raise BusinessException(status_code=409, detail="El email ya está registrado.")
    
 
    try:
        
        auth_response = supabase_client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
           
            "options": {
                "data": {"name": user_data.name, "role": user_data.role}
            }
        })
        
        if not auth_response.user or not auth_response.user.id:
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al crear la cuenta en Supabase Auth. Verifique las credenciales."
            )

        supabase_id = auth_response.user.id
        
    except Exception as e:
       
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el registro de Supabase Auth: {e}"
        )

    
    role_map = {
        ConfigRole.DOCTOR: UserRole.DOCTOR,
        ConfigRole.ADMIN: UserRole.ADMIN,
        ConfigRole.PACIENTE: UserRole.PACIENTE
    }
    
    role_db = role_map.get(user_data.role, UserRole.PACIENTE) 
    
    
    user = user_crud.create_user(db, user=user_data, role=role_db, supabase_id=supabase_id) 
    
   
    try:
        profile_data = {
            "id": str(supabase_id),  
            "role": user_data.role,  
            "name": user_data.name, 
        }
        
        
        supabase_client.table("profiles").insert(profile_data).execute()
        
    except Exception as e:
        
        print(f"ALERTA CRÍTICA: Falla al crear el perfil de Supabase. Usuario local creado: {user.id}")
        pass 
        

    # 4. Crea el UserResponse
    response_user = schemas.UserResponse.model_validate(user, from_attributes=True)
    response_user.has_google_token = bool(user.google_refresh_token)
    return response_user

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: schemas.UserLogin, 
    db: Session = Depends(get_db),
    supabase_client: Client = Depends(get_supabase_client) 
):
    """
    Autentica al usuario con email y contraseña delegando a Supabase Auth
    y retorna un token JWT de la API local.
    """
    
    try:
        auth_response = supabase_client.auth.sign_in_with_password({
            "email": form_data.email,
            "password": form_data.password,
        })
        
        if not auth_response.user or not auth_response.user.id:
            
            raise CredencialesInvalidas() 
            
        supabase_id = auth_response.user.id

    except Exception as e:
        
        if "Invalid login credentials" in str(e):
             raise CredencialesInvalidas() 
        print(f"Error en la autenticación de Supabase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en la conexión con el servicio de autenticación."
        )

   
    user = user_crud.get_user_by_supabase_id(db, supabase_id=supabase_id)
    if not user:
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario autenticado en Supabase, pero no encontrado en el sistema local. Contacte a soporte."
        )
        
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_security.create_access_token(
        data={"user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    requires_google_auth = (user.role == UserRole.DOCTOR and not user.google_refresh_token)

    return schemas.Token(
        access_token=access_token, 
        token_type="bearer",
        requires_google_auth=requires_google_auth
    )
    



@router.get("/google/login", response_model=schemas.GoogleAuthURL)
def google_login():
    """
    Genera la URL de Google OAuth. 
    """
    state = "some_random_state_for_security"
    auth_url = auth_utils.get_google_login_url(state=state)
    return schemas.GoogleAuthURL(auth_url=auth_url)


@router.get("/google/callback", response_model=schemas.Token)
def google_callback(
    code: str, 
    state: str, 
    db: Session = Depends(get_db),
    supabase_client: Client = Depends(get_supabase_client) 
):
    """
    Endpoint al que Google redirige después de la autenticación. 
    Intercambia el código por tokens y autentica/registra al usuario, 
    sincronizándolo con Supabase Auth si es nuevo.
    """
    try:
        
        google_tokens = auth_utils.exchange_code_for_tokens(auth_code=code)
        access_token_google = google_tokens["access_token"]
        refresh_token_google = google_tokens.get("refresh_token") 
        
        google_user_info = auth_utils.get_google_user_info(access_token=access_token_google)
        email = google_user_info["email"]
        name = google_user_info["name"]
        
        user = user_crud.get_user_by_email(db, email=email)
        is_doctor_registration = ('doctor' in name.lower() or 'dr.' in name.lower())
        
        
        if user is None:
            
            random_plain_password = generate_random_password() 
            
            
            role_db = UserRole.DOCTOR if is_doctor_registration and refresh_token_google else UserRole.PACIENTE
            role_config_str = role_db.value 
            
            user_data = schemas.UserCreate(
                email=email, 
                name=name, 
                
                password=random_plain_password, 
                role=role_config_str
            )
            
          
            try:
                auth_response = supabase_client.auth.sign_up({
                    "email": email,
                    "password": random_plain_password, 
                    "options": {
                        "data": {"name": name, "role": role_config_str}
                    }
                })
                
                if not auth_response.user or not auth_response.user.id:
                    raise BusinessException(400, "Error al crear la cuenta en Supabase Auth.")
                
                supabase_id = auth_response.user.id
                
            except Exception as e:
               
                print(f"Error en Supabase sign_up durante Google Callback: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error en el registro de Supabase Auth: {e}"
                )

            
            user = user_crud.create_user(
                db, 
                user=user_data,
                role=role_db,
                supabase_id=supabase_id, 
                google_refresh_token=refresh_token_google if role_db == UserRole.DOCTOR else None
            )
            
            
            try:
                profile_data = {
                    "id": str(supabase_id),  
                    "role": role_config_str, 
                    "name": name, 
                }
                supabase_client.table("profiles").insert(profile_data).execute()
            except Exception as e:
                print(f"ALERTA CRÍTICA: Falla al crear el perfil de Supabase en Google Callback: {e}")
                pass
            
        elif user.role == UserRole.DOCTOR and refresh_token_google:
            
            if user.google_refresh_token != refresh_token_google:
                user_crud.save_google_refresh_token(db, user, refresh_token_google)
        
       
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


@router.get("/me", response_model=schemas.UserResponse)
def read_current_user(current_user: CurrentUserDep):
    """
    Retorna la información del usuario autenticado (requiere JWT válido).
    """
    response_user = schemas.UserResponse.model_validate(current_user, from_attributes=True)
    response_user.has_google_token = bool(current_user.google_refresh_token)
    return response_user
