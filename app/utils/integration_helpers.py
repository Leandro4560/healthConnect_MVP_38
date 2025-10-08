from datetime import datetime, timedelta
from typing import List, Optional


def get_doctor_available_slots(doctor_id: int, date: datetime) -> List[datetime]:
 
    
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


def generate_teleconsult_link(appointment_id: int, is_virtual: bool) -> Optional[str]:
     
    if not is_virtual:
        return None
    
    unique_id = f"{appointment_id}-{datetime.now().strftime('%Y%m%d%H%M')}"
    return f"https://meet.healthtech.com/consult/{unique_id}"
