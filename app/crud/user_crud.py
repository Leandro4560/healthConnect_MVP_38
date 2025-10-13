from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Busca un usuario en la base de datos por su ID.
    Devuelve el objeto User si lo encuentra, o None si no.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Busca un usuario en la base de datos por su dirección de email.
    Esto es útil para la autenticación y validaciones.
    """
    return db.query(User).filter(User.email == email).first()

def get_doctors(db: Session) -> List[User]:
    """
    Obtiene la lista de todos los usuarios que tienen el rol de Doctor.
    """
    
    from app.models.user import UserRole
    return db.query(User).filter(User.role == UserRole.DOCTOR).all()
