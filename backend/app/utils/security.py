from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated 

from passlib.context import CryptContext
from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.crud.user_crud import get_user_by_id
from app.excepciones import CredencialesInvalidas
from app.utils.schemas import TokenPayload # Usamos el schema para tipado seguro

# --- Configuración de Encriptación ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Configuración de OAuth2 ---
# Instancia que se usará como Inyección de Dependencia para obtener el token del header
# Apunta al endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 


# --- Funciones de Hash ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña plana."""
    return pwd_context.hash(password)


# --- Funciones JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT con fecha de expiración."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Usamos timezone.utc para evitar problemas de zona horaria
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # El payload debe ser JSON serializable
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenPayload]:
    """Decodifica un token de acceso y verifica su firma y expiración."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if user_id is None or role is None:
            # Lanza una excepción específica para FastAPI
            raise CredencialesInvalidas(detail="Token incompleto o inválido")
            
        return TokenPayload(user_id=user_id, role=role)
        
    except JWTError:
        # Lanza una excepción específica si el token falla
        raise CredencialesInvalidas(detail="Token inválido o expirado")


# --- Inyección de Dependencia (Protección de Rutas) ---

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependencia para obtener el usuario autenticado a partir del token JWT.
    Usa oauth2_scheme para extraer el token del header 'Authorization: Bearer <token>'.
    """
    token_data = decode_access_token(token)
    
    # Si decode_access_token no lanzó una excepción, tenemos el TokenPayload
    if token_data.user_id is None:
        raise CredencialesInvalidas(detail="Usuario no encontrado en el token")

    user = get_user_by_id(db, user_id=token_data.user_id)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario de la base de datos no encontrado")
        
    return user

# Tipo anotado para simplificar la inyección en los routers
CurrentUserDep = Annotated[User, Depends(get_current_user)]


def role_required(required_role: str):
    """
    Dependencia factory para requerir un rol específico.
    """
    def role_checker(current_user: CurrentUserDep) -> User:
        if current_user.role.value != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere el rol: {required_role}"
            )
        return current_user
    return role_checker
