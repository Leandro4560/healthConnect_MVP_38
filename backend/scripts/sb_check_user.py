from app.config import settings
from supabase import create_client

svc = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
email = "doctor@ejemplo.com"
res = svc.table("users").select("*").eq("email", email).execute()
print("select result:", res)
# intenta mostrar data y error de forma explícita
print("data:", getattr(res, "data", None))
print("error:", getattr(res, "error", None))
