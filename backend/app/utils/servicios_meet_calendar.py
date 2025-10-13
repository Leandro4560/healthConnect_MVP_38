from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.utils.google_tokens import get_credentials_from_refresh_token
from app.excepciones import GoogleCalendarError  
from app.models.user import User
from app.config import settings
from typing import Dict, Optional
import datetime
import pytz

TIME_ZONE = settings.TIME_ZONE 

def create_google_calendar_event(
    doctor: User,
    summary: str,
    description: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
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
        Un diccionario con la URL de Meet y la URL del evento, o None si falla.
    """
    
    refresh_token = doctor.google_refresh_token
    if not refresh_token:
        raise GoogleCalendarError("Doctor no tiene el calendario de Google conectado.")

    credentials = get_credentials_from_refresh_token(refresh_token)
    
    if not credentials:
        raise GoogleCalendarError("Token de refresco de Google inválido o expirado.")

    try:
        service = build('calendar', 'v3', credentials=credentials)

        local_tz = pytz.timezone(TIME_ZONE)
        
        start_dt_aware = local_tz.localize(start_time) if start_time.tzinfo is None else start_time
        end_dt_aware = local_tz.localize(end_time) if end_time.tzinfo is None else end_time

        event = {
            'summary': summary,
            'description': description,
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{doctor.id}-{start_time.strftime('%Y%m%d%H%M%S')}",
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
            'attendees': [
                {'email': doctor.email},
                {'email': patient_email, 'responseStatus': 'needsAction'},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60}, 
                    {'method': 'email', 'minutes': 10},      
                ],
            },
        }

        event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1,
            sendNotifications=True
        ).execute()

        meet_link = None
        for entry in event.get('conferenceData', {}).get('entryPoints', []):
            if entry.get('entryPointType') == 'video':
                meet_link = entry.get('uri')
                break

        return {
            "meet_url": meet_link,
            "event_url": event.get('htmlLink')
        }

    except HttpError as e:
        print(f"Error HTTP de Google Calendar: {e}")
        raise GoogleCalendarError(f"Error de la API de Google: {e.content.decode()}")
    except Exception as e:
        print(f"Error inesperado al crear evento: {e}")
        raise GoogleCalendarError("Error inesperado al procesar la cita.")
