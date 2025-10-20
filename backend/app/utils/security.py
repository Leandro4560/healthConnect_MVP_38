# app/utils/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated 
# Importaciones de terceros
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
# Importaciones locales (de tu proyecto)
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.crud import user_crud 
from app.excepciones import CredencialesInvalidas
from app.utils.schemas import Token # Importación corregida a Token

# ----------------------------------------------------------------------
## Inicialización de Esquema de Autenticación
# ----------------------------------------------------------------------

# Esquema de seguridad de OAuth2. El tokenUrl apunta al endpoint de login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 

# ----------------------------------------------------------------------
## Funciones Principales
# ----------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT con fecha de expiración."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Usa el valor predeterminado de settings
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire.timestamp()}) # Asegura que exp sea un timestamp
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Token:
    """Decodifica el token JWT y retorna los datos."""
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise CredencialesInvalidas(detail="Token incompleto: Falta ID de usuario.")
        
        # Pydantic validará los datos
        token_data = Token(
            user_id=int(user_id), 
            role=payload.get("role"),
            exp=datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        )
        
    except JWTError:
        # Esto captura expiración, firma inválida, etc.
        raise CredencialesInvalidas(detail="Token de acceso inválido o expirado")
    except ValueError:
        # Captura si user_id no es un entero válido
        raise CredencialesInvalidas(detail="ID de usuario en el token no es válido")

    return token_data


def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependencia de FastAPI para obtener el objeto User completo a partir del token JWT.
    """
    # 1. Decodificar y validar el token
    token_data = decode_access_token(token)

    # 2. Buscar el usuario en la base de datos
    user = user_crud.get_user_by_id(db, user_id=token_data.user_id) 

    if user is None:
        raise CredencialesInvalidas(detail="Usuario de la base de datos no encontrado")
    
    # El usuario fue encontrado, se retorna
    return user


# ----------------------------------------------------------------------
## Dependencias de Rol (Role Dependencies)
# ----------------------------------------------------------------------

# Tipo anotado para simplificar la dependencia de obtención de usuario
CurrentUserDep = Annotated[User, Depends(get_current_user)]

def role_required(required_role: str):
    """
    Dependencia factory para requerir un rol específico.
    """
    def role_checker(current_user: CurrentUserDep) -> User:
        
        # Comparamos el valor del Enum con el string del rol requerido
        if current_user.role.value != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere el rol '{required_role}' para acceder a este recurso."
            )
        return current_user
        
    return role_checker

# Dependencias predefinidas para roles
requires_doctor = role_required("Doctor")
requires_patient = role_required("Patient")
requires_admin = role_required("Admin")