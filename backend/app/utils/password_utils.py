from passlib.context import CryptContext

# Usamos pbkdf2_sha256 como esquema por defecto para evitar depender de bcrypt nativo
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    default="pbkdf2_sha256",
    deprecated="auto",
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash almacenado."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña plana usando el esquema por defecto."""
    return pwd_context.hash(password)

def needs_update(hashed_password: str) -> bool:
    """Devuelve True si el hash existente debería ser actualizado."""
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception:
        return False
