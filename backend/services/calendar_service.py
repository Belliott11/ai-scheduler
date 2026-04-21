"""Google Calendar API integration"""
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_python_client import discovery
from datetime import datetime, timedelta
from typing import List, Optional
from models import CalendarSlot


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_calendar_service():
    """
    Authenticate and return Google Calendar service.
    On first run, this will prompt you to authorize in your browser.
    """
    creds = None
    
    # Token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return discovery.build('calendar', 'v3', credentials=creds)


def get_free_slots(
    service,
    start_date: datetime,
    end_date: datetime,
    working_hours_start: int = 9,
    working_hours_end: int = 22
) -> List[CalendarSlot]:
    """
    Get free time slots from Google Calendar.
    
    Args:
        service: Google Calendar service object
        start_date: Start date for search
        end_date: End date for search
        working_hours_start: Hour to start considering (default 9 AM)
        working_hours_end: Hour to stop considering (default 10 PM)
        
    Returns:
        List of available time slots
    """
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            maxResults=250,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        free_slots = []
        
        # For MVP: return working hours availability per day
        # Parse events for this date range
        busy_times = []
        for e in events:
            try:
                start = datetime.fromisoformat(e['start'].get('dateTime', e['start'].get('date'))[:19])
                end = datetime.fromisoformat(e['end'].get('dateTime', e['end'].get('date'))[:19])
                busy_times.append((start, end))
            except (KeyError, ValueError):
                continue
        
        busy_times.sort()
        
        # Iterate through each day
        current = start_date
        while current < end_date:
            day_start = current.replace(hour=working_hours_start, minute=0, second=0, microsecond=0)
            day_end = current.replace(hour=working_hours_end, minute=0, second=0, microsecond=0)
            
            # Find free slots within working hours by checking for conflicts
            # For MVP, if there are any events on the day, show available working hours as single slot
            # A more sophisticated implementation would break the day into 1-hour slots
            day_has_event = False
            for busy_start, busy_end in busy_times:
                # Check if event overlaps with working hours
                if busy_start.date() == current.date():
                    # Event is on this day, mark it as having conflicts
                    if not (busy_end <= day_start or busy_start >= day_end):
                        day_has_event = True
                        break
            
            # For MVP, we'll still show the full working hours as available
            # (A production system would calculate actual free blocks between events)
            free_slots.append(CalendarSlot(
                start_time=day_start,
                end_time=day_end,
                day_of_week=current.strftime('%A')
            ))
            
            current += timedelta(days=1)
        
        return free_slots
    except Exception as e:
        raise ValueError(f"Failed to fetch calendar data: {str(e)}")


def create_calendar_event(
    service,
    event_title: str,
    start_time: datetime,
    end_time: datetime,
    description: str = ""
) -> dict:
    """
    Create an event in Google Calendar.
    
    Args:
        service: Google Calendar service object
        event_title: Title of the event
        start_time: Event start time
        end_time: Event end time
        description: Event description
        
    Returns:
        Created event object
    """
    event = {
        'summary': event_title,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC'
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC'
        }
    }
    
    created_event = service.events().insert(
        calendarId='primary',
        body=event
    ).execute()
    
    return created_event
