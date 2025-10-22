# app/utils/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
# Importaciones de terceros
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
# importa tu función para obtener usuario o decodificar token
from app.crud.user_crud import get_user_by_id

from app.config import settings
from app.models.user import User
from app.crud import user_crud
from app.excepciones import CredencialesInvalidas
from app.utils.schemas import Token  # Importación corregida a Token

# ----------------------------------------------------------------------
## Inicialización de Esquema de Autenticación
# ----------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ----------------------------------------------------------------------
## Funciones Principales
# ----------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT con fecha de expiración."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire.timestamp()})  # Asegura que exp sea un timestamp

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

        token_data = Token(
            user_id=int(user_id),
            role=payload.get("role"),
            exp=datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        )

    except JWTError:
        raise CredencialesInvalidas(detail="Token de acceso inválido o expirado")
    except ValueError:
        raise CredencialesInvalidas(detail="ID de usuario en el token no es válido")

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependencia correcta: NO usar *args/**kwargs.
    Decodifica el token, obtiene el user_id y devuelve el User.
    """
    try:
        token_data = decode_access_token(token)
    except CredencialesInvalidas as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user = get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    return user

# Permite usar Depends(CurrentUserDep) en rutas
CurrentUserDep = get_current_user

# ----------------------------------------------------------------------
## Dependencias de Rol (Role Dependencies)
# ----------------------------------------------------------------------

# Tipo anotado para simplificar la dependencia de obtención de usuario
# CurrentUserDep = Annotated[User, Depends(get_current_user)]

def role_required(required_role: str):
    """
    Dependencia factory para requerir un rol específico.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Comparamos el valor del Enum (o string) con el string del rol requerido
        role_value = getattr(current_user.role, "value", str(current_user.role))
        if role_value != required_role:
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