# app/routes/ruta.py
from fastapi import APIRouter, Depends, status, HTTPException
from typing import Optional
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import secrets  
import string  

# Importaciones específicas para login con credenciales OAuth2
from fastapi.security import OAuth2PasswordRequestForm 

# --- IMPORTS DE SUPABASE ---
from supabase import create_client, Client 
from uuid import UUID
# ---------------------------

from app.database import get_db
from app.utils import schemas
from app.crud import user_crud
from app.utils import security as auth_security
from app.utils import auth_utils # Para get_google_login_url, exchange_code_for_tokens, get_google_user_info
from app.utils.password_utils import verify_password, get_password_hash, needs_update # Se añade para el login con credenciales
from app.excepciones import BusinessException, CredencialesInvalidas
from app.models.user import User, UserRole 
from app.config import settings
from app.utils.security import CurrentUserDep 

# --- INICIALIZACIÓN DEL CLIENTE SUPABASE (usando settings) ---
SUPABASE_CLIENT: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY_ANON)

def get_supabase_client() -> Client:
    """Dependencia para obtener el cliente Supabase."""
    return SUPABASE_CLIENT
# ----------------------------------------------------------

router = APIRouter()

def generate_random_password(length=12) -> str:
    """Genera una contraseña aleatoria para usuarios creados por Google OAuth."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

# ----------------------------------------------------------------------
# ENDPOINTS DE AUTENTICACIÓN
# ----------------------------------------------------------------------

@router.post("/login", response_model=schemas.TokenResponse)
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login tradicional con email y contraseña. Retorna un token JWT.
    """
    # 1. Buscar usuario por email
    user = user_crud.get_user_by_email(db, email=form_data.username) # OAuth2 usa 'username' para el email
    
    if not user:
        raise CredencialesInvalidas(detail="Email o contraseña incorrectos.")
    
    # 2. Verificar la contraseña
    if not verify_password(form_data.password, user.hashed_password):
        raise CredencialesInvalidas(detail="Email o contraseña incorrectos.")

    # Si el hash del usuario necesita actualización (p.ej. es pbkdf2) lo re-hasheamos a bcrypt
    if needs_update(user.hashed_password):
        # Re-hashear con el esquema por defecto (bcrypt) usando la contraseña que entró el usuario
        new_hash = get_password_hash(form_data.password)
        user.hashed_password = new_hash
        db.add(user)
        db.commit()
        db.refresh(user)

    # 3. Crear el token de acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_security.create_access_token(
        data={"user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # 4. Retornar el token y la info del usuario
    return schemas.TokenResponse(
        access_token=access_token, 
        token_type="bearer",
        user=schemas.UserResponse.model_validate(user, from_attributes=True) 
    )


# ----------------------------------------------------------------------
# GOOGLE OAUTH2 FLOW
# ----------------------------------------------------------------------

@router.get("/google/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
def google_login(state: Optional[str] = None):
    """
    Paso 1: Redirige al usuario a la página de login de Google.
    """
    if not state:
        state = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(32))

    login_url = auth_utils.get_google_login_url(state)
    return RedirectResponse(url=login_url)


@router.get("/google/callback", response_model=schemas.TokenResponse)
def google_callback(
    code: str, 
    # state: str, # Normalmente se valida
    db: Session = Depends(get_db),
    supabase: Client = Depends(get_supabase_client) 
):
    """
    Paso 2: Recibe el código de autorización de Google, lo canjea por tokens, 
    obtiene la info del usuario y realiza el login.
    """
    try:
        # 1. Canjear el código por tokens
        # Se asume que auth_utils.exchange_code_for_tokens retorna el access y refresh token
        token_data = auth_utils.exchange_code_for_tokens(code)
        access_token_google = token_data.get("access_token")
        refresh_token_google = token_data.get("refresh_token")
        
        # 2. Obtener la info del perfil de Google
        user_info = auth_utils.get_google_user_info(access_token_google)
        user_email = user_info.get("email")
        user_name = user_info.get("name")
        
        if not user_email:
            raise BusinessException(400, "El perfil de Google no proporcionó un email.")
        
        # 3. Buscar usuario en la DB local
        user = user_crud.get_user_by_email(db, email=user_email)
        
        # 4. Si el usuario no existe, crearlo.
        if user is None:
            random_password = generate_random_password()
            user_in = schemas.UserCreate(
                email=user_email,
                name=user_name,
                password=random_password,
                role=UserRole.PATIENT.value # Por defecto como paciente
            )
            user = user_crud.create_user(db, user_in=user_in)

        # 5. Si es un DOCTOR y hay refresh_token, lo guardamos.
        if user.role == UserRole.DOCTOR and refresh_token_google:
            update_data = schemas.UserUpdate(
                google_refresh_token=refresh_token_google
            )
            user = user_crud.update_user(db, db_user=user, user_update=update_data)
        
        # 6. Crear el token JWT de la aplicación
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_security.create_access_token(
            data={"user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        # 7. Retornar el token y la info del usuario
        return schemas.TokenResponse(
            access_token=access_token, 
            token_type="bearer",
            user=schemas.UserResponse.model_validate(user, from_attributes=True)
        )

    except (BusinessException, CredencialesInvalidas) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error desconocido en google_callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la autenticación de Google."
        )


# ----------------------------------------------------------------------
# ENDPOINT DE PERFIL
# ----------------------------------------------------------------------

@router.get("/me", response_model=schemas.UserResponse)
def read_current_user(current_user: CurrentUserDep):
    """
    Retorna la información del usuario autenticado (requiere JWT válido).
    """
    response_user = schemas.UserResponse.model_validate(current_user, from_attributes=True)
    
    # Añadir un campo dinámico para el frontend
    setattr(response_user, 'has_google_token', bool(current_user.google_refresh_token))

    return response_user