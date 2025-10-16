from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.user import User, UserRoleDB
from app.utils import schemas
from app.utils.security import get_password_hash # Importamos la utilidad de hashing


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Obtiene un usuario por su ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Obtiene un usuario por su dirección de email."""
    # El email es único, usamos first()
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Obtiene una lista paginada de todos los usuarios."""
    return db.query(User).offset(skip).limit(limit).all()

def get_doctors(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Obtiene una lista paginada de solo los Doctores."""
    return db.query(User).filter(User.role == UserRoleDB.DOCTOR).offset(skip).limit(limit).all()


# --- Función de Creación (CREATE) ---

def create_user(db: Session, user: schemas.UserCreate, role: UserRoleDB) -> User:
    """
    Crea un nuevo usuario en la base de datos.
    Hashea la contraseña antes de guardar.
    """
    
    hashed_password = get_password_hash(user.password)
    
   
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=role,
       
        google_refresh_token=getattr(user, 'google_refresh_token', None)
    )
    
 
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user



def update_user(db: Session, db_user: User, user_update: schemas.UserUpdate) -> User:
    """
    Actualiza los campos de un usuario existente.
    """
    update_data = user_update.model_dump(exclude_unset=True)
    
   
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"] 
        
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user



def delete_user(db: Session, user_id: int) -> bool:
    """
    Elimina un usuario por su ID.
    Retorna True si el usuario fue eliminado, False si no fue encontrado.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
