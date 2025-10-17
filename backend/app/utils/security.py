from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated 

from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.crud.user_crud import get_user_by_id
from app.excepciones import CredencialesInvalidas

from app.utils.schemas import TokenData 





oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 




def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT con fecha de expiración."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
       
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    
    to_encode.update({"exp": expire, "sub": str(data["user_id"])})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """Decodifica un token JWT y retorna su payload."""
    try:
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        user_id: Optional[int] = payload.get("user_id")
        role: Optional[str] = payload.get("role")
        
        if user_id is None:
            raise CredencialesInvalidas(detail="Token incompleto: Falta el user_id")
            
        
        return TokenData(user_id=user_id, role=role)
        
    except JWTError:
        
        raise CredencialesInvalidas(detail="Token inválido o expirado")




def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependencia para obtener el usuario autenticado a partir del token JWT.
    Usa oauth2_scheme para extraer el token del header 'Authorization: Bearer <token>'.
    """
    token_data = decode_access_token(token)
    
    
        raise CredencialesInvalidas(detail="Usuario no encontrado en el token")

    
    user = get_user_by_id(db, user_id=token_data.user_id)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario de la base de datos no encontrado")
        
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def role_required(required_role: str):
    """
    Dependencia factory para requerir un rol específico.
    """
    def role_checker(current_user: CurrentUserDep) -> User:
        
        if current_user.role.value != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere el rol '{required_role}' para acceder a este recurso."
            )
        return current_user
        
    return role_checker
