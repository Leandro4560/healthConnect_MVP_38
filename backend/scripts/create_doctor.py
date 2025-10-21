# Asegúrate de ejecutar con PYTHONPATH=.
from app.database import SessionLocal
# Importar los módulos de modelos aquí para registrar todas las clases antes de usar Session
from app.models import user as user_model, appointment as appointment_model, clinical_record as clinical_record_model

from app.models.user import User, UserRole
from app.utils.password_utils import get_password_hash

EMAIL = "doctor@ejemplo.com"
FULL_NAME = "Dr. Leonardo Roa"
PLAIN_PASSWORD = "PasswordDePrueba123!"   # Cambia si quieres otra contraseña
SUPABASE_UUID = "a1b2c3d4-e5f6-7890-1234-567890abcdef"  # Opcional

def main():
    hashed = get_password_hash(PLAIN_PASSWORD)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == EMAIL).first()
        if user:
            print("Usuario existente. Actualizando hashed_password y supabase_id...")
            user.hashed_password = hashed
            user.supabase_id = SUPABASE_UUID
        else:
            print("Creando nuevo usuario doctor...")
            user = User(
                supabase_id=SUPABASE_UUID,
                full_name=FULL_NAME,
                email=EMAIL,
                hashed_password=hashed,
                role=UserRole.DOCTOR,  # si el modelo espera Enum, está bien; si espera string usa .value
                is_active=True
            )
            db.add(user)
        db.commit()
        db.refresh(user)
        print("Hecho. Usuario id local:", getattr(user, "id", None))
        print("hashed_password guardado:", (user.hashed_password or "")[:80], "...")
    finally:
        db.close()

if __name__ == "__main__":
    main()