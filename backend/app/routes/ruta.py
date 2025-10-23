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

# IMPORTAR CurrentUserDep para la dependencia de perfil
from app.utils.security import CurrentUserDep
from app.services.supabase_client import insert_user, update_google_refresh_token
import logging
logger = logging.getLogger(__name__)

# --- CLIENTE SUPABASE (anon) pero solo si está la key configurada ---
SUPABASE_CLIENT: Optional[Client] = None
if getattr(settings, "SUPABASE_KEY_ANON", None):
    try:
        SUPABASE_CLIENT = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY_ANON)
    except Exception as e:
        SUPABASE_CLIENT = None
        print("Warning: no se pudo inicializar SUPABASE_CLIENT (anon):", e)

def get_supabase_client() -> Optional[Client]:
    """
    Dependencia que devuelve el cliente anon de Supabase o None si no está configurado.
    No lanza excepción en import time.
    """
    return SUPABASE_CLIENT

# --- CLIENTE PARA OPERACIONES DE BACKEND (service role), si está disponible ---
SUPABASE_SERVICE_CLIENT: Optional[Client] = None
if getattr(settings, "SUPABASE_SERVICE_KEY", None):
    try:
        SUPABASE_SERVICE_CLIENT = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    except Exception as e:
        SUPABASE_SERVICE_CLIENT = None
        print("Warning: no se pudo inicializar SUPABASE_SERVICE_CLIENT (service):", e)


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
    supabase: Optional[Client] = Depends(get_supabase_client)
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
def read_current_user(current_user: User = Depends(CurrentUserDep)):
    """
    Retorna la información del usuario autenticado (requiere JWT válido).
    """
    response_user = schemas.UserResponse.model_validate(current_user, from_attributes=True)
    
    # Añadir un campo dinámico para el frontend (no modifica la lógica del modelo)
    setattr(response_user, 'has_google_token', bool(current_user.google_refresh_token))

    return response_user


# ----------------------------
# Endpoint: registrar usuario
# ----------------------------
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registra un usuario localmente y (si está configurado) lo crea en Supabase.
    - user_in: espera el schema UserCreate (email, name, password, role, ...)
    """
    # 1) verificar si ya existe
    existing = user_crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado.")

    # 2) crear usuario local
    db_user = user_crud.create_user(db, user_in)

    supabase_id = None
    supabase_error = None
    supabase_profile_created = False

    # 3) intentar crear en Supabase con service key (preferible)
    svc = SUPABASE_SERVICE_CLIENT
    if svc:
        try:
            # 3.a Intentamos crear en Auth (admin.create_user)
            admin = getattr(svc.auth, "admin", None)
            created = None
            if admin and hasattr(admin, "create_user"):
                try:
                    # intentamos la firma común (kwargs)
                    created = admin.create_user(email=user_in.email, password=user_in.password, email_confirm=True)
                except TypeError:
                    # fallback si la implementación requiere dict
                    created = admin.create_user({"email": user_in.email, "password": user_in.password, "email_confirm": True})

                # Extraer id del resultado en distintas formas posibles
                def _extract_id(obj):
                    if obj is None:
                        return None
                    if isinstance(obj, dict):
                        # casos: {'user': {...}} o {'id': '...'}
                        if "id" in obj:
                            return obj.get("id")
                        if "user" in obj and isinstance(obj["user"], dict):
                            return obj["user"].get("id")
                        if "data" in obj and isinstance(obj["data"], list) and len(obj["data"]) > 0:
                            # a veces res.data = [ ... ]
                            first = obj["data"][0]
                            if isinstance(first, dict):
                                return first.get("id") or first.get("supabase_id")
                    # try attributes
                    user_attr = getattr(obj, "user", None)
                    if user_attr:
                        # user_attr puede ser un objeto con id o dict
                        if hasattr(user_attr, "id"):
                            return getattr(user_attr, "id")
                        if isinstance(user_attr, dict):
                            return user_attr.get("id")
                    if hasattr(obj, "id"):
                        return getattr(obj, "id")
                    # fallback: try 'data' attribute
                    data_attr = getattr(obj, "data", None)
                    if data_attr:
                        try:
                            if isinstance(data_attr, list) and len(data_attr) > 0:
                                first = data_attr[0]
                                if isinstance(first, dict):
                                    return first.get("id") or first.get("supabase_id")
                        except Exception:
                            pass
                    return None

                supabase_id = _extract_id(created)
                # guardar posible error que devuelva la librería
                if isinstance(created, dict):
                    supabase_error = created.get("error")
            else:
                # 3.b Fallback: no admin.create_user disponible -> insertar directamente en tabla 'users' (service key)
                payload = {
                    "email": user_in.email,
                    "full_name": getattr(user_in, "name", None) or getattr(user_in, "full_name", None),
                    "role": getattr(user_in, "role", None),
                }
                try:
                    res = svc.table("users").insert(payload).execute()
                    data = getattr(res, "data", None) or (res and res.get("data") if isinstance(res, dict) else None)
                    if data and isinstance(data, list) and len(data) > 0:
                        # asumimos que la tabla devuelve el objeto insertado con id
                        supabase_id = data[0].get("id") or data[0].get("supabase_id")
                        supabase_profile_created = True
                    else:
                        supabase_error = getattr(res, "error", None) or (res and res.get("error") if isinstance(res, dict) else None)
                except Exception as e:
                    supabase_error = str(e)
        except Exception as e:
            supabase_error = str(e)
            print("Warning: fallo al crear usuario en Supabase (admin):", e)

        # 3.c Si creamos en Auth (supabase_id obtenido) intentamos crear el profile en la tabla 'users' (id = supabase auth id)
        if supabase_id and not supabase_profile_created:
            try:
                # Calculamos el hash con la utilidad del proyecto (NO almacenamos la contraseña en claro)
                hashed_for_supabase = get_password_hash(user_in.password)

                # -------------- OPCION A: if your Supabase table `users` has `id` as UUID (recommended)
                profile_payload = {
                    "id": supabase_id,  # forzar que la fila de perfil tenga el mismo id que Auth user
                    "email": user_in.email,
                    "full_name": getattr(user_in, "name", None) or getattr(user_in, "full_name", None),
                    "role": getattr(user_in, "role", None),
                    "hashed_password": hashed_for_supabase,  # <-- añadimos el hash aquí
                }
                # -------------- FIN OPCION A

                # Si tu tabla tiene schema distinto (por ejemplo `supabase_id` en vez de `id`), usa:
                # profile_payload = {
                #     "supabase_id": supabase_id,
                #     "email": user_in.email,
                #     "full_name": ...,
                #     "role": ...,
                #     "hashed_password": hashed_for_supabase,
                # }

                res_profile = svc.table("users").insert(profile_payload).execute()
                data_profile = getattr(res_profile, "data", None) or (res_profile and res_profile.get("data") if isinstance(res_profile, dict) else None)
                if data_profile and isinstance(data_profile, list) and len(data_profile) > 0:
                    supabase_profile_created = True
                else:
                    supabase_error = getattr(res_profile, "error", None) or (res_profile and res_profile.get("error") if isinstance(res_profile, dict) else supabase_error)
            except Exception as e:
                supabase_error = str(e)
                print("Warning: fallo al crear profile en tabla 'users':", e)

    # 4) si obtuvimos supabase_id, actualizar la fila local
    if supabase_id:
        db_user.supabase_id = supabase_id
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        if supabase_error:
            print("Supabase create warning/error:", supabase_error)

    # 5) devolver el usuario creado (serializado)
    # (en logs dejamos info para debugging)
    print("register_user result -> local_id:", getattr(db_user, "id", None), "supabase_id:", supabase_id, "profile_created:", supabase_profile_created, "error:", supabase_error)
    
    # Sincronizar con Supabase (intenta insertar el usuario en Supabase, no afecta la creación local)
    try:
        insert_user({
            "id": db_user.id,                 # si en supabase usas uuid/auto, omite id
            "email": db_user.email,
            "full_name": getattr(db_user, "name", None) or getattr(db_user, "full_name", None),
            "role": db_user.role,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at.isoformat() if db_user.created_at else None,
            "google_refresh_token": getattr(db_user, "google_refresh_token", None),
        })
    except Exception as e:
        logger.exception("Supabase sync failed (no se afecta la creación local)")
    
    return schemas.UserResponse.model_validate(db_user, from_attributes=True)