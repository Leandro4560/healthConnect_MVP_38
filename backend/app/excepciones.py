# app/excepciones.py
from fastapi import HTTPException, status
from typing import Any, Dict, Optional 


class BusinessException(HTTPException):
    """
    Excepción personalizada para manejar errores de lógica de negocio (reglas de la aplicación).
    Hereda de HTTPException para ser manejada automáticamente por FastAPI.
    """
    def __init__(self, status_code: int, detail: Any = None, headers: Optional[Dict[str, str]] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class CredencialesInvalidas(BusinessException):
    """
    Excepción para errores de autenticación/autorización (Token o Login fallido).
    """
    def __init__(self, detail: str = "Credenciales de acceso no válidas o expiradas."):
        # Usa el código 401 que es el estándar para credenciales inválidas.
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class GoogleCalendarError(BusinessException):
    """
    Excepción para manejar fallos de comunicación o errores de la API de Google.
    """
    def __init__(self, detail: str = "Error al comunicarse con la API de Google Calendar."):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class ResourceNotFound(BusinessException):
    """Excepción para cuando un recurso solicitado no existe."""
    def __init__(self, resource_name: str = "Recurso"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource_name} no encontrado.")

