import os
from supabase import create_client
from app.config import settings

# Si tu .env no se carga automáticamente, exporta SUPABASE_SERVICE_KEY en el entorno
SUPABASE_URL = getattr(settings, "SUPABASE_URL", os.getenv("SUPABASE_URL"))
SUPABASE_SERVICE_KEY = getattr(settings, "SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_SERVICE_KEY"))

if not SUPABASE_SERVICE_KEY:
    raise SystemExit("Falta SUPABASE_SERVICE_KEY en el entorno. Exportala antes de ejecutar.")

svc = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

email = "doctor@ejemplo.com"
password = "PasswordDePrueba123!"
display_name = "Dr. Leonardo Roa"

# Prueba admin.create_user si la librería lo expone
admin = getattr(svc.auth, "admin", None)
if admin and hasattr(admin, "create_user"):
    try:
        # Intenta la firma común (kwargs)
        result = admin.create_user(email=email, password=password, email_confirm=True)
        print("create_user result:", result)
    except TypeError:
        # Fallback a dict arg
        result = admin.create_user({"email": email, "password": password, "email_confirm": True})
        print("create_user (dict) result:", result)
else:
    print("admin.create_user no disponible en este cliente. Intentando insert en tabla 'users' con service key (requiere esquema).")
    res = svc.table("users").insert({"email": email, "full_name": display_name}).execute()
    print("insert table users result:", res)