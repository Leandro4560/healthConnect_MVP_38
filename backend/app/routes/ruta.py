# app/routes/ruta.py
from fastapi import APIRouter, Depends, status, HTTPException, Request
from typing import Optional
from fastapi.responses import RedirectResponse
import urllib.parse
from sqlalchemy.orm import Session
from datetime import timedelta
import secrets  
import string  

# Importaciones específicas para login con credenciales OAuth2
from fastapi.security import OAuth2PasswordRequestForm 

# ---------------------------
# NOTE: Removed Supabase client usage — all user operations are local DB only
# ---------------------------

from app.database import get_db
from app.utils import schemas
from app.crud import user_crud
from app.utils import security as auth_security
from app.utils import auth_utils
from app.utils.password_utils import verify_password, get_password_hash, needs_update
from app.excepciones import BusinessException, CredencialesInvalidas
from app.models.user import User, UserRole 
from app.config import settings

# IMPORTAR CurrentUserDep para la dependencia de perfil
from app.utils.security import CurrentUserDep

import logging
logger = logging.getLogger(__name__)
import secrets as _secrets

router = APIRouter()

def generate_random_password(length=12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

def _generate_refresh_token() -> str:
    return _secrets.token_urlsafe(48)

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
    # Generar refresh token y guardarlo en la DB
    refresh = _generate_refresh_token()
    user.refresh_token = refresh
    db.add(user)
    db.commit()

    # 4. Retornar el token, refresh y la info del usuario
    return schemas.TokenResponse(
        access_token=access_token, 
        token_type="bearer",
        refresh_token=refresh,
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

        # Generar refresh token y guardarlo
        refresh = _generate_refresh_token()
        user.refresh_token = refresh
        db.add(user)
        db.commit()

        # 7. Si hay FRONTEND_URL, redirigimos al frontend con el token y refresh en query param
        frontend = getattr(settings, "FRONTEND_URL", None)
        if frontend:
            # usamos quote_plus para evitar problemas con caracteres
            token_qs = urllib.parse.quote_plus(access_token)
            refresh_qs = urllib.parse.quote_plus(refresh)
            redirect_url = f"{frontend.rstrip('/')}" + f"/auth/success?token={token_qs}&refresh={refresh_qs}"
            return RedirectResponse(url=redirect_url)

        # Fallback: retornar JSON con token
        return schemas.TokenResponse(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh,
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
def read_current_user(current_user: User = Depends(CurrentUserDep)):
    """
    Retorna la información del usuario autenticado (requiere JWT válido).
    """
    response_user = schemas.UserResponse.model_validate(current_user, from_attributes=True)
    
    # Añadir un campo dinámico para el frontend (no modifica la lógica del modelo)
    setattr(response_user, 'has_google_token', bool(current_user.google_refresh_token))

    return response_user


# Endpoint para refresh de tokens
@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh_access_token(refresh_data: dict, db: Session = Depends(get_db)):
    """
    Refresh the access token given a refresh_token in body: {"refresh_token": "..."}
    Returns a new access_token and rotated refresh_token.
    """
    token = refresh_data.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="refresh_token required")

    user = user_crud.get_user_by_refresh_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")

    # generar nuevo access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_security.create_access_token(
        data={"user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires,
    )

    # rotar refresh token
    new_refresh = _generate_refresh_token()
    user.refresh_token = new_refresh
    db.add(user)
    db.commit()

    return schemas.TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=new_refresh,
        user=schemas.UserResponse.model_validate(user, from_attributes=True),
    )


# ----------------------------
# Endpoint: registrar usuario
# ----------------------------
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db), request: Request = None):
    """
    Registra un usuario localmente y (si está configurado) lo crea en Supabase.
    - user_in: espera el schema UserCreate (email, name, password, role, ...)
    """
    # Log basic request info to help debug 429 / rate-limit issues
    try:
        client_host = request.client.host if request is not None else "unknown"
        user_agent = request.headers.get("user-agent") if request is not None else None
        logger.info(f"register_user called from {client_host}; UA={user_agent}")
    except Exception:
        # avoid breaking the endpoint if logging fails
        pass

    # 1) verificar si ya existe
    existing = user_crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado.")

    # Normalizar roles (misma lógica)
    role_val = getattr(user_in, "role", None)
    if role_val:
        # Mapear valores recibidos a los valores del Enum UserRole (ej.: 'Patient','Doctor','Admin')
        role_map = {
            "PACIENTE": "Patient", "PACIENT": "Patient", "PATIENT": "Patient", "PATIENTE": "Patient",
            "DOCTOR": "Doctor", "MEDICO": "Doctor",
            "ADMIN": "Admin", "ADMINISTRADOR": "Admin", "ADMINISTRACION": "Admin",
        }
        try:
            mapped = role_map.get(str(role_val).upper(), None)
            if mapped:
                user_in.role = mapped
        except Exception:
            pass

    # Verificar políticas de creación para roles sensibles (Admin/Doctor)
    # Leemos secretos/códigos desde cabeceras para no exponerlos en el body
    admin_secret_hdr = None
    doctor_code_hdr = None
    try:
        admin_secret_hdr = request.headers.get("x-admin-secret") or request.headers.get("admin-secret") if request is not None else None
        doctor_code_hdr = request.headers.get("x-doctor-code") or request.headers.get("doctor-code") if request is not None else None
    except Exception:
        admin_secret_hdr = None
        doctor_code_hdr = None

    # Si se solicita crear un Admin, requiere la secret en settings
    try:
        requested_role = str(getattr(user_in, "role", "")).lower()
    except Exception:
        requested_role = ""

    if requested_role == "admin" or requested_role == "adminstrator":
        # ADMIN_SECRET debe estar configurado en settings para permitir creación de admin
        if not getattr(settings, "ADMIN_SECRET", None):
            logger.warning("Intento de crear Admin pero ADMIN_SECRET no está configurado en settings.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Creación de admin no permitida.")
        if admin_secret_hdr != settings.ADMIN_SECRET:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin secret inválido.")

    # Si se solicita crear un Doctor, requerimos código de invitación o email del dominio autorizado
    if requested_role == "doctor":
        allowed_doctor = False
        # 1) Código de invitación
        if doctor_code_hdr and getattr(settings, "DOCTOR_INVITE_CODE", None) and doctor_code_hdr == settings.DOCTOR_INVITE_CODE:
            allowed_doctor = True
        # 2) Dominio de email autorizado
        domain = getattr(settings, "DOCTOR_EMAIL_DOMAIN", "")
        try:
            if domain and user_in.email and user_in.email.lower().endswith("@" + domain.lower()):
                allowed_doctor = True
        except Exception:
            pass

        if not allowed_doctor:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Creación de doctor no permitida. Proporcione un código de invitación o use un email del dominio autorizado.")

    # 2) crear usuario local exclusivamente
    try:
        db_user = user_crud.create_user(db, user_in)
    except Exception as e:
        # Loguear la excepción completa para facilitar el debug en entornos remotos (Render)
        logger.exception("Error creando usuario en create_user")
        # Exponer un mensaje de error controlado al cliente (evitar filtrar secretos)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # generar refresh token para el usuario creado y almacenarlo
    try:
        refresh = _generate_refresh_token()
        db_user.refresh_token = refresh
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception:
        pass

    print("register_user result -> local_id:", getattr(db_user, "id", None))

    return schemas.UserResponse.model_validate(db_user, from_attributes=True)