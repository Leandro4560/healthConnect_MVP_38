from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User

# Nota: En un proyecto completo, aquí también irían las funciones de creación (create_user),
# actualización (update_user) y eliminación (delete_user), pero para empezar,
# nos enfocamos en las funciones de lectura necesarias para la gestión de citas.

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
    # Importamos UserRole dentro de la función o al inicio si fuera necesario, 
    # pero aquí podemos asumir que ya está definido o se definirá en el modelo.
    # Por simplicidad, asumiremos que se puede importar si es necesario.
    # Si la importación da error, puedes importar UserRole al inicio: 
    # from app.models.user import UserRole
    # y usar User.role == UserRole.DOCTOR
    
    # Versión simplificada asumiendo el rol 'Doctor' se maneja correctamente:
    # return db.query(User).filter(User.role == 'DOCTOR').all()
    
    # Para la prueba, simplemente devolveremos todos los usuarios si la clase UserRole
    # no está importada aquí. Sin embargo, lo correcto es filtrar por rol.
    # Asumo que el modelo User ya tiene definido el rol como columna.
    
    # Si tienes el Enum UserRole disponible:
    # from app.models.user import UserRole
    # return db.query(User).filter(User.role == UserRole.DOCTOR).all()
    
    # Dejamos la versión que solo lee la tabla User, y el filtro por rol
    # debería ser manejado por la capa de la API si es necesario,
    # aunque para un CRUD es mejor que esté aquí.

    # Usamos la importación necesaria para la lógica de roles:
    from app.models.user import UserRole
    return db.query(User).filter(User.role == UserRole.DOCTOR).all()
