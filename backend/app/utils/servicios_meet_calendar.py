from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.utils.google_tokens import get_credentials_from_refresh_token
from app.excepciones import GoogleCalendarError  
from app.models.user import User
from app.config import settings
from typing import Dict, Optional
from datetime import datetime
from zoneinfo import ZoneInfo # Usamos el módulo estándar 'zoneinfo'

# Configuración de zona horaria
TIME_ZONE = settings.TIME_ZONE
TIME_ZONE_INFO = ZoneInfo(TIME_ZONE)


def create_google_calendar_event(
    doctor: User,
    summary: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    patient_email: str
) -> Optional[Dict]:
    """
    Crea un evento de Google Calendar en el calendario principal del doctor,
    y automáticamente genera un enlace de Google Meet.

    Args:
        doctor: El objeto User del doctor, que debe contener el google_refresh_token.
        summary: Título del evento (ej: "Cita con Juan Pérez").
        description: Descripción del evento.
        start_time: Objeto datetime.datetime con el inicio de la cita.
        end_time: Objeto datetime.datetime con el final de la cita.
        patient_email: Email del paciente para enviarle la invitación.

    Returns:
        Un diccionario con la URL de Meet y el ID del evento de Google.
    """
    
    refresh_token = doctor.google_refresh_token
    if not refresh_token:
        # Aunque el router ya verificó esto, es una buena práctica de seguridad
        raise GoogleCalendarError("Doctor no tiene el calendario de Google conectado.")

    credentials = get_credentials_from_refresh_token(refresh_token)
    
    if not credentials:
        raise GoogleCalendarError("No se pudieron obtener credenciales válidas de Google.")
        
    try:
        # 1. Crear el servicio de Google Calendar
        service = build('calendar', 'v3', credentials=credentials)
        
        # 2. Asegurar que las fechas son timezone-aware (si vienen naive, se asume la zona del doctor)
        if start_time.tzinfo is None:
            start_dt_aware = start_time.replace(tzinfo=TIME_ZONE_INFO)
        else:
            start_dt_aware = start_time.astimezone(TIME_ZONE_INFO)
            
        if end_time.tzinfo is None:
            end_dt_aware = end_time.replace(tzinfo=TIME_ZONE_INFO)
        else:
            end_dt_aware = end_time.astimezone(TIME_ZONE_INFO)
            
        # 3. Construir el cuerpo del evento
        event = {
            'summary': summary,
            'description': description,
            'location': 'Consulta Online (Google Meet)',
            'conferenceData': { # Pide a Google que cree una conferencia (Meet)
                'createRequest': {
                    'requestId': f"meet-{doctor.id}-{start_dt_aware.timestamp()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                },
            },
            'start': {
                'dateTime': start_dt_aware.isoformat(),
                'timeZone': TIME_ZONE,
            },
            'end': {
                'dateTime': end_dt_aware.isoformat(),
                'timeZone': TIME_ZONE,
            },
            # Añade al doctor (organizador) y al paciente
            'attendees': [
                {'email': doctor.email},
                {'email': patient_email, 'responseStatus': 'needsAction'},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60}, # 1 día antes
                    {'method': 'email', 'minutes': 10},      # 10 minutos antes
                ],
            },
        }

        # 4. Insertar el evento
        event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1, # Indica que queremos la conferencia
            sendNotifications=True
        ).execute()

        # 5. Extraer el enlace de Meet
        meet_link = None
        for entry in event.get('conferenceData', {}).get('entryPoints', []):
            if entry.get('entryPointType') == 'video':
                meet_link = entry.get('uri')
                break

        return {
            "meet_url": meet_link,
            "event_id": event.get('id')
        }

    except HttpError as e:
        print(f"Error HTTP de Google Calendar: {e}")
        raise GoogleCalendarError(f"Error de la API de Google: {e.content.decode()}")
    except Exception as e:
        print(f"Error inesperado al crear evento: {e}")
        raise GoogleCalendarError("Error inesperado al procesar la cita.")