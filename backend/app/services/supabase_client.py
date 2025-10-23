import logging
from typing import Optional, Dict, Any, Tuple

from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)

# Leer desde settings (compatible con tu .env)
SUPABASE_URL = getattr(settings, "SUPABASE_URL", None)
# tu .env tiene SUPABASE_SERVICE_KEY  — probamos ambos nombres por compatibilidad
SUPABASE_SERVICE_KEY = getattr(settings, "SUPABASE_SERVICE_KEY", None) or getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None)
SUPABASE_ANON_KEY = getattr(settings, "SUPABASE_KEY_ANON", None)

_supabase_client: Optional[Client] = None
_supabase_anon_client: Optional[Client] = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("Supabase service client inicializado correctamente.")
    except Exception as e:
        _supabase_client = None
        logger.exception("No se pudo inicializar Supabase service client: %s", e)
else:
    logger.warning("SUPABASE_URL o SUPABASE_SERVICE_KEY no configuradas en settings. Supabase service client deshabilitado.")

if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        _supabase_anon_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        logger.info("Supabase anon client inicializado correctamente.")
    except Exception as e:
        _supabase_anon_client = None
        logger.exception("No se pudo inicializar Supabase anon client: %s", e)
else:
    logger.info("SUPABASE_ANON_KEY no configurada. Supabase anon client deshabilitado.")


def get_supabase_service_client() -> Optional[Client]:
    return _supabase_client


def get_supabase_anon_client() -> Optional[Client]:
    return _supabase_anon_client


def _parse_response(res: Any) -> Tuple[Optional[Any], Optional[Any]]:
    """
    Helper para extraer data/error de la respuesta de la librería supabase-py.
    """
    data = getattr(res, "data", None) or (res and res.get("data") if isinstance(res, dict) else None)
    error = getattr(res, "error", None) or (res and res.get("error") if isinstance(res, dict) else None)
    return data, error


def insert_user(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inserta/crea un registro en la tabla 'users' de Supabase usando el service client.
    - Si el client no está configurado hace no-op y devuelve {}.
    - row debe respetar el esquema de la tabla en Supabase (UUID/id, email, full_name, role, hashed_password, etc.).
    """
    client = get_supabase_service_client()
    if client is None:
        logger.warning("insert_user: Supabase service client no configurado. Operación omitida.")
        return {}

    try:
        res = client.table("users").insert(row).execute()
        data, error = _parse_response(res)
        if error:
            raise RuntimeError(f"Supabase insert_user error: {error}")
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return {}
    except Exception as e:
        logger.exception("Error al insertar/crear user en Supabase: %s", e)
        raise


def insert_appointment(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inserta una fila en la tabla 'appointments' de Supabase.
    - Espera patient_id/doctor_id como UUID string (según tu esquema de Supabase).
    """
    client = get_supabase_service_client()
    if client is None:
        logger.warning("insert_appointment: Supabase service client no configurado. Operación omitida.")
        return {}

    try:
        res = client.table("appointments").insert(row).execute()
        data, error = _parse_response(res)
        if error:
            raise RuntimeError(f"Supabase insert_appointment error: {error}")
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return {}
    except Exception as e:
        logger.exception("Error al insertar appointment en Supabase: %s", e)
        raise


def update_google_refresh_token(supabase_id: Optional[str], refresh_token: str) -> Dict[str, Any]:
    """
    Actualiza google_refresh_token en tablas 'doctors' y 'users' (intenta en doctors primero).
    """
    client = get_supabase_service_client()
    if client is None:
        logger.warning("update_google_refresh_token: Supabase service client no configurado. Operación omitida.")
        return {}

    if not supabase_id:
        logger.warning("update_google_refresh_token: supabase_id no proporcionado. Operación omitida.")
        return {}

    payload = {"google_refresh_token": refresh_token}
    try:
        res = client.table("doctors").update(payload).eq("id", supabase_id).execute()
        data, error = _parse_response(res)
        if error:
            logger.debug("update_google_refresh_token: fallo al actualizar 'doctors': %s", error)
        if data:
            logger.info("Refreshtoken actualizado en tabla 'doctors' para id=%s", supabase_id)
            return data

        res2 = client.table("users").update(payload).eq("id", supabase_id).execute()
        data2, error2 = _parse_response(res2)
        if error2:
            logger.debug("update_google_refresh_token: fallo al actualizar 'users': %s", error2)
        if data2:
            logger.info("Refreshtoken actualizado en tabla 'users' para id=%s", supabase_id)
            return data2

        logger.warning("update_google_refresh_token: No se actualizó ninguna fila en Supabase para id=%s", supabase_id)
        return {}
    except Exception as e:
        logger.exception("Error al actualizar google_refresh_token en Supabase: %s", e)
        raise