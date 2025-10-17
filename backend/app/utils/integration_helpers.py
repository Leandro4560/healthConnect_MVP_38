from datetime import datetime, timedelta
from typing import List, Optional



def get_doctor_available_slots(doctor_id: int, date: datetime) -> List[datetime]:
    """
    Retorna una lista de slots de 30 minutos disponibles para un doctor en una fecha dada.
    (Lógica simplificada: Lunes a Viernes, de 9 AM a 12 PM)
    """
    
    
    if date.weekday() in [5, 6]:
        return []

    available_slots = []
    start_hour = 9
    end_hour = 12
    slot_duration_minutes = 30

    
    current_time = datetime(date.year, date.month, date.day, start_hour, 0, 0)
    
    end_of_day = datetime(date.year, date.month, date.day, end_hour, 0, 0)

    while current_time < end_of_day:
        available_slots.append(current_time)
        current_time += timedelta(minutes=slot_duration_minutes)
        
    return available_slots


