from googleapiclient.discovery import build
from datetime import datetime, timedelta


def get_calendar_service(credentials):
    return build("calendar", "v3", credentials=credentials)


def get_free_slots(service, start_date, end_date):
    """
    Returns simple free slots (MVP logic placeholder)
    """
    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_date.isoformat() + "Z",
        timeMax=end_date.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    # SIMPLE MVP: just return gaps between days (not full algorithm)
    free_slots = []

    current = start_date
    while current < end_date:
        free_slots.append({
            "start_time": current,
            "end_time": current + timedelta(hours=1),
            "day_of_week": current.strftime("%A")
        })
        current += timedelta(days=1)

    return free_slots