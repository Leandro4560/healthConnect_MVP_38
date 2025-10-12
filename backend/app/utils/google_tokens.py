
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from app.config import settings
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from fastapi import status, HTTPException 

CLIENT_CONFIG = {
    "web": {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "project_id": "fastapi-calendar-app", 
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uris": [settings.GOOGLE_REDIRECT_URI], 
        "javascript_origins": ["http://localhost:8000"] 
    }
}

def get_google_auth_flow() -> Flow:
    
    try:
        flow = Flow.from_client_config(
            client_config=CLIENT_CONFIG,
            scopes=settings.GOOGLE_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI 
        )
        return flow
    except Exception as e:
        print(f"Error al inicializar Google Flow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración de Google OAuth."
        )

def exchange_code_for_tokens(auth_code: str) -> dict:
  
    flow = get_google_auth_flow()
    
    flow.fetch_token(code=auth_code)
    
    return {
        "refresh_token": flow.credentials.refresh_token,
        "access_token": flow.credentials.token,
        "expiry": flow.credentials.expiry,
        "email": flow.credentials.id_token.get('email')
    }

def get_credentials_from_refresh_token(refresh_token: str) -> Optional[Credentials]:
   
    if not refresh_token:
        return None
        
    try:
        
        credentials = Credentials(
            token=None,  
            refresh_token=refresh_token,
            token_uri=CLIENT_CONFIG['web']['token_uri'],
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=settings.GOOGLE_SCOPES
        )
        
        credentials.refresh(Request())
        
        return credentials
    except Exception as e:
        print(f"Error al refrescar el token de Google: {e}")
        return None
