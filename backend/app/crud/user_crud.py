from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
# NUEVO: Importamos el tipo UUID para la función de búsqueda
from uuid import UUID

# --- Importaciones existentes (sin cambios) ---
from ..models.user import User, UserRole
from ..utils.schemas import UserCreate, UserUpdate, UserLogin as TokenRequest # Renombrado
from ..utils.password_utils import get_password_hash, verify_password 
from ..excepciones import BusinessException # Importar para manejar errores
# ----------------------------------------------


# =====================================================================
# Operaciones de Lectura (READ)
# =====================================================================

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Obtiene un usuario por su ID local."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Alias de get_user, usado en security.py."""
    return get_user(db, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Obtiene un usuario por su dirección de email."""
    return db.query(User).filter(User.email == email).first()

# NUEVO: Función crítica para el login con Supabase
def get_user_by_supabase_id(db: Session, supabase_id: UUID) -> Optional[User]:
    """
    Obtiene un usuario local por el UUID que proporciona Supabase Auth.
    """
    # Usamos .filter() con el tipo UUID de SQLAlchemy
    return db.query(User).filter(User.supabase_id == supabase_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Obtiene una lista paginada de usuarios."""
    return db.query(User).offset(skip).limit(limit).all()


# =====================================================================
# Operación de Creación (CREATE)
# =====================================================================

# CRÍTICO: Añadimos 'supabase_id: Optional[UUID]' para la sincronización
def create_user(
    db: Session, 
    user_data: UserCreate, 
    supabase_id: Optional[UUID] = None # Nuevo parámetro
) -> User:
    """
    Crea un nuevo usuario en la base de datos local.
    Si se proporciona, vincula con el UUID de Supabase Auth.
    """
    if get_user_by_email(db, email=user_data.email):
        raise BusinessException(409, "El email ya está registrado.")
        
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        email=user_data.email,
        full_name=user_data.name, # Mapeamos 'name' del schema a 'full_name' del modelo
        hashed_password=hashed_password,
        # Si el rol no viene, se usa el valor por defecto del modelo (PATIENT)
        role=user_data.role if user_data.role else UserRole.PATIENT, 
        # CRÍTICO: Asignamos el ID de Supabase
        supabase_id=supabase_id 
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        # Manejo más específico de errores de BD si es necesario
        print(f"Error de integridad al crear usuario: {e}")
        raise BusinessException(500, "Error al guardar el usuario en la base de datos.")


# =====================================================================
# Autenticación y Actualización
# =====================================================================

def authenticate_user(db: Session, token_request: TokenRequest) -> Optional[User]:
    """
    Verifica las credenciales de un usuario localmente (para login con contraseña).
    """
    # Usamos get_user_by_email, que busca el usuario localmente
    user = get_user_by_email(db, email=token_request.email)
    
    if user and verify_password(token_request.password, user.hashed_password):
        return user
    
    return None

# Operación de Actualización (UPDATE) y Google Token (sin cambios sustanciales)
def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    """
    Actualiza los campos de un usuario existente.
    """
    # Usamos model_dump para obtener un diccionario de los campos con valores
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"] 
    
    # Mapeamos 'name' del schema a 'full_name' del modelo antes de la asignación
    if "name" in update_data:
        update_data["full_name"] = update_data["name"]
        del update_data["name"]

    for key, value in update_data.items():
        # Usamos setattr para asignar el valor al atributo correspondiente del modelo
        setattr(db_user, key, value)
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def save_google_refresh_token(db: Session, user: User, refresh_token: str) -> User:
    """
    Guarda o actualiza el Google Refresh Token en la base de datos para el usuario dado.
    """
    user.google_refresh_token = refresh_token
    db.add(user) 
    db.commit() 
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Elimina un usuario por su ID.
    """
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
