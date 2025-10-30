from sqlalchemy.orm import Session
from typing import Optional, List


import logging
from ..models.user import User, UserRole
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
    logger = logging.getLogger(__name__)

    hashed_password = get_password_hash(user_in.password)

    # obtener dict desde el schema (sin la contraseña)
    user_data = user_in.model_dump(exclude={'password'}, exclude_none=True)

    # loguear payload (sin contraseña) para debug remoto
    try:
        logger.info("create_user payload: %s", {k: v for k, v in user_data.items() if k != 'password'})
    except Exception:
        pass

    # Normalizar/mapeo seguro del campo role hacia el Enum UserRole
    role_val = user_data.get('role')
    if role_val:
        try:
            if isinstance(role_val, str):
                # comparar tanto con name como con value (case-insensitive)
                for r in UserRole:
                    if role_val.lower() == r.name.lower() or role_val.lower() == str(r.value).lower():
                        user_data['role'] = r
                        break
        except Exception as e:
            logger.warning("No se pudo normalizar role en create_user: %s", e)

    # Extraer el campo 'name' (si viene) y evitar pasarlo como keyword inválido al constructor
    name = user_data.pop('name', None)

    try:
        db_user = User(
            **user_data, 
            full_name=name if name is not None else user_data.get('full_name'),
            hashed_password=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
    except Exception:
        logger.exception("Error al persistir nuevo usuario en la base de datos")
        # Re-lanzar para que el handler superior lo capture y loguee
        raise


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


def get_user_by_refresh_token(db: Session, refresh_token: str) -> Optional[User]:
    """
    Busca un usuario por su refresh_token.
    """
    return db.query(User).filter(User.refresh_token == refresh_token).first()
