import requests
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from datetime import datetime

from app.config import settings
from app.excepciones import BusinessException, CredencialesInvalidas
from app.models.user import User


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token" 
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"




def get_google_login_url(state: str) -> str:
    """Genera la URL de redirección a Google para iniciar el proceso de OAuth."""
    
    scopes = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        
        "https://www.googleapis.com/auth/calendar.events",
    ]
    
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(scopes),
        "access_type": "offline",  
        "prompt": "consent",       
        "state": state             
    }
    
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)




def exchange_code_for_tokens(auth_code: str) -> Dict[str, Any]:
    """
    Intercambia el código de autorización recibido de Google por Access Token 
    y Refresh Token.
    """
    data = {
        "code": auth_code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    
    if response.status_code != 200:
        print(f"Error al obtener tokens de Google (Status: {response.status_code}): {response.text}") 
        raise BusinessException(
            status_code=400, 
            detail="Error al intercambiar el código de Google. Intente de nuevo."
        )
        
    return response.json()




def get_google_user_info(access_token: str) -> Dict[str, Any]:
    """Obtiene el email y nombre del usuario de Google usando el Access Token."""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
    
    if response.status_code != 200:
        print(f"Error al obtener info de usuario de Google: {response.text}")
        raise BusinessException(
            status_code=400, 
            detail="Error al obtener la información del perfil de Google."
        )
        
    return response.json()




def refresh_google_access_token(user: User) -> str:
    """
    Usa el refresh_token almacenado en la DB del usuario (Doctor) para obtener un nuevo
    Access Token válido para interactuar con Google Calendar.
    """
    if not user.google_refresh_token:
        raise CredencialesInvalidas(
            status_code=400, 
            detail="El usuario no tiene un Refresh Token de Google."
        )
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "refresh_token": user.google_refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(GOOGLE_TOKEN_URL, data=data)

    if response.status_code != 200:
        print(f"Error al refrescar el token de Google: {response.text}")
        raise BusinessException(
            status_code=400, 
            detail="Error al refrescar el token de Google."
        )
        
    return response.json().get("access_token")