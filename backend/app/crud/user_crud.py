from sqlalchemy.orm import Session
from typing import Optional, List


from ..models.user import User 
from ..models.appointment import Appointment 
from ..models.clinical_record import ClinicalRecord 

from ..utils.schemas import UserCreate, UserUpdate
from ..utils.password_utils import get_password_hash



def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Obtiene un usuario por su ID primario.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Obtiene un usuario por su dirección de correo electrónico (necesario para el registro).
    """
    return db.query(User).filter(User.email == email).first()


get_user = get_user_by_id 



def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Crea un nuevo usuario en la base de datos, hasheando la contraseña.
    """
    
    hashed_password = get_password_hash(user_in.password)
    
    # obtener dict desde el schema (sin la contraseña)
    user_data = user_in.model_dump(exclude={'password'}, exclude_none=True)
    
    # Extraer el campo 'name' (si viene) y evitar pasarlo como keyword inválido al constructor
    name = user_data.pop('name', None)
    
    db_user = User(
        **user_data, 
        full_name=name if name is not None else user_data.get('full_name'),
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    """Actualiza los campos de un usuario existente."""
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        hashed_password = get_password_hash(update_data.pop("password"))
        update_data["hashed_password"] = hashed_password
        
    if "name" in update_data:
        update_data["full_name"] = update_data.pop("name")

    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
