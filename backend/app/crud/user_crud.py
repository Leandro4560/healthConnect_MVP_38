from sqlalchemy.orm import Session
from typing import Optional, List

# Importaciones de tu proyecto
# FIX: Usar '..' para subir un nivel (a 'app') y luego bajar a 'models'
from ..models.user import User 
from ..models.appointment import Appointment 
from ..models.clinical_record import ClinicalRecord 

from ..utils.schemas import UserCreate, UserUpdate
from ..utils.password_utils import get_password_hash


# =====================================================================
# OPERACIONES DE LECTURA (READ)
# =====================================================================

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

# Alias para compatibilidad con appointment_crud.py
get_user = get_user_by_id 

# =====================================================================
# OPERACIÓN DE CREACIÓN (CREATE)
# =====================================================================

def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Crea un nuevo usuario en la base de datos, hasheando la contraseña.
    """
    
    # 1. Hashear la contraseña
    hashed_password = get_password_hash(user_in.password)
    
    # 2. Convertir el schema a un diccionario y preparar para el modelo
    user_data = user_in.model_dump(exclude={'password'}, exclude_none=True)
    
    # Mapeo de 'name' del schema a 'full_name' del modelo
    db_user = User(
        **user_data, 
        full_name=user_data['name'], 
        hashed_password=hashed_password
    )
    
    # 3. Guardar en la DB
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# =====================================================================
# OPERACIÓN DE ACTUALIZACIÓN (UPDATE)
# =====================================================================

def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    """Actualiza los campos de un usuario existente."""
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        # Si la contraseña se va a actualizar, se hashea
        hashed_password = get_password_hash(update_data.pop("password"))
        update_data["hashed_password"] = hashed_password
        
    # El campo 'name' del schema se mapea a 'full_name' del modelo
    if "name" in update_data:
        update_data["full_name"] = update_data.pop("name")

    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user