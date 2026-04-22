"""Main FastAPI application"""
import os
import tempfile
import json
from datetime import datetime, timedelta

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from dotenv import load_dotenv

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from models import SyllabusData, CalendarSlot, Assignment, ScheduledTask, ScheduleOutput
from services.pdf_parser import extract_text_from_file
from services.claude_scheduler import parse_syllabus_with_claude, generate_schedule_with_claude
from services.exporters import (
    generate_markdown_schedule,
    generate_ics_calendar,
    generate_json_schedule,
)

# ======================
# INIT
# ======================
load_dotenv()

app = FastAPI(title="AI Scheduler API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://belliott11.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_sessions = {}

GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
REDIRECT_URI = "http://localhost:8000/oauth/callback"


# ======================
# HEALTH
# ======================
@app.get("/health")
def health():
    return {"status": "ok"}


# ======================
# UPLOAD SYLLABUS
# ======================
@app.post("/upload-syllabus")
async def upload_syllabus(file: UploadFile = File(...)):
    if file.filename.endswith(".pdf"):
        suffix = ".pdf"
    elif file.filename.endswith(".docx"):
        suffix = ".docx"
    else:
        raise HTTPException(400, "Only PDF and DOCX files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    try:
        text = extract_text_from_file(path)
        return {"success": True, "text": text}
    finally:
        os.unlink(path)


# ======================
# PARSE SYLLABUS
# ======================
@app.post("/parse-syllabus")
async def parse_syllabus(request: dict):
    text = request.get("syllabus_text")
    session_id = request.get("session_id", "default")

    if not text:
        raise HTTPException(400, "Missing syllabus_text")

    parsed = parse_syllabus_with_claude(text)

    user_sessions[session_id] = {
        "syllabus": parsed,
        "created": datetime.now().isoformat(),
    }

    return {"success": True, "session_id": session_id}


# ======================
# GOOGLE AUTH START
# ======================
@app.get("/authorize-calendar")
def authorize_calendar():
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=GOOGLE_SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )

    user_sessions["oauth_state"] = state

    return RedirectResponse(auth_url)


# ======================
# GOOGLE CALLBACK
# ======================
@app.get("/oauth/callback")
def oauth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    print("OAuth callback received")
    print("Code:", code[:10] if code else None)
    print("State:", state)

    if not code:
        raise HTTPException(400, "Missing code")

    # OPTIONAL: disable this check if debugging issues
    saved_state = user_sessions.get("oauth_state")
    if saved_state and state != saved_state:
        raise HTTPException(400, "Invalid OAuth state")

    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=GOOGLE_SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI,
    )

    try:
        # Use the full authorization response URL when exchanging the code.
        # This avoids issues when additional query params (e.g. iss) are present.
        flow.fetch_token(authorization_response=str(request.url))
    except Exception as e:
        print("TOKEN ERROR:", repr(e))
        raise HTTPException(500, f"OAuth token exchange failed: {str(e)}")

    creds = flow.credentials

    user_sessions["google_creds"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }

    print("OAuth success")

    return RedirectResponse("http://localhost:5173/calendar?connected=true")


# ======================
# CALENDAR EVENTS
# ======================
@app.post("/get-calendar-slots")
async def get_calendar_slots(request: dict):
    session_id = request.get("session_id", "default")
    start_date = request.get("start_date")
    end_date = request.get("end_date")

    if not start_date or not end_date:
        raise HTTPException(400, "Missing dates")

    creds_data = user_sessions.get("google_creds")
    if not creds_data:
        raise HTTPException(401, "Not authenticated")

    creds = Credentials(**creds_data)
    service = build("calendar", "v3", credentials=creds)

    events = service.events().list(
        calendarId="primary",
        timeMin=f"{start_date}T00:00:00Z",
        timeMax=f"{end_date}T23:59:59Z",
        singleEvents=True,
    ).execute()

    items = events.get("items", [])

    # Helper to parse RFC3339 datetimes
    def _parse_dt(s: str):
        if not s:
            return None
        try:
            if s.endswith('Z'):
                s = s.replace('Z', '+00:00')
            return datetime.fromisoformat(s)
        except Exception:
            return None

    # Organize busy intervals by date
    busy_by_day = {}
    for e in items:
        start_raw = e.get('start', {}).get('dateTime') or e.get('start', {}).get('date')
        end_raw = e.get('end', {}).get('dateTime') or e.get('end', {}).get('date')
        start_dt = _parse_dt(start_raw) if start_raw and 'T' in start_raw else None
        end_dt = _parse_dt(end_raw) if end_raw and 'T' in end_raw else None
        # fallback: skip all-day events (date-only) for now
        if not start_dt or not end_dt:
            continue

        day_key = start_dt.date().isoformat()
        busy_by_day.setdefault(day_key, []).append((start_dt, end_dt))

    # For each day in the range, compute free slots between 08:00 and 22:00
    start_dt_day = datetime.fromisoformat(f"{start_date}T00:00:00+00:00")
    end_dt_day = datetime.fromisoformat(f"{end_date}T00:00:00+00:00")
    curr = start_dt_day
    free_slots = []
    while curr.date() <= end_dt_day.date():
        day_str = curr.date().isoformat()
        day_start = datetime.fromisoformat(f"{day_str}T08:00:00+00:00")
        day_end = datetime.fromisoformat(f"{day_str}T22:00:00+00:00")

        busy = sorted(busy_by_day.get(day_str, []), key=lambda x: x[0])

        cursor = day_start
        for bstart, bend in busy:
            if bstart > cursor:
                # free slot between cursor and bstart
                if (bstart - cursor).total_seconds() >= 30 * 60:
                    free_slots.append({
                        'start': cursor.isoformat(),
                        'end': bstart.isoformat(),
                        'day_of_week': cursor.strftime('%A')
                    })
            cursor = max(cursor, bend)

        # trailing free slot
        if cursor < day_end and (day_end - cursor).total_seconds() >= 30 * 60:
            free_slots.append({
                'start': cursor.isoformat(),
                'end': day_end.isoformat(),
                'day_of_week': cursor.strftime('%A')
            })

        curr = curr + timedelta(days=1)

    user_sessions.setdefault(session_id, {})["calendar"] = items

    return {"success": True, "slots": free_slots}


# ======================
# SCHEDULE
# ======================
@app.post("/schedule")
async def create_schedule(request: dict):
    session_id = request.get("session_id", "default")
    session = user_sessions.get(session_id)

    if not session:
        raise HTTPException(400, "No session")

    # Convert stored syllabus dict into SyllabusData model if needed
    raw_syllabus = session.get("syllabus")
    if raw_syllabus is None:
        raise HTTPException(400, "No syllabus data in session")

    if isinstance(raw_syllabus, SyllabusData):
        syllabus_model = raw_syllabus
    else:
        try:
            syllabus_model = SyllabusData.parse_obj(raw_syllabus)
        except Exception as e:
            raise HTTPException(400, f"Invalid syllabus format: {e}")

    # Convert calendar slot dicts into CalendarSlot models
    raw_slots = session.get("calendar", []) or []
    calendar_slots = []
    def _parse_dt(s: str):
        if not s:
            return None
        try:
            if s.endswith('Z'):
                s = s.replace('Z', '+00:00')
            return datetime.fromisoformat(s)
        except Exception:
            return None

    for s in raw_slots:
        start = _parse_dt(s.get('start'))
        end = _parse_dt(s.get('end'))
        if not start or not end:
            continue
        day_name = start.strftime('%A')
        calendar_slots.append(CalendarSlot(start_time=start, end_time=end, day_of_week=day_name))

    # Call the Gemini scheduling function (returns JSON text)
    schedule_raw = generate_schedule_with_claude(syllabus_model, calendar_slots)

    # Try to parse the AI response into a structured ScheduleOutput
    schedule_obj = None
    try:
        parsed = json.loads(schedule_raw)
        # Expecting { schedule_summary, daily_tasks: [{date, day, tasks: [{assignment_title, start_time, end_time, notes}]}], tips }
        tasks = []
        for day_block in parsed.get('daily_tasks', []):
            date = day_block.get('date')
            for t in day_block.get('tasks', []):
                title = t.get('assignment_title') or t.get('assignment') or t.get('title') or 'Study'
                start_time = t.get('start_time')
                end_time = t.get('end_time')
                if not date or not start_time or not end_time:
                    continue
                # Build datetimes
                try:
                    start_dt = datetime.fromisoformat(f"{date}T{start_time}")
                    end_dt = datetime.fromisoformat(f"{date}T{end_time}")
                except Exception:
                    continue

                # Try to find matching assignment from syllabus
                match = None
                for a in syllabus_model.assignments:
                    try:
                        if a.title.strip().lower() == title.strip().lower():
                            match = a
                            break
                    except Exception:
                        continue

                if not match:
                    # create a lightweight Assignment placeholder
                    match = Assignment(
                        title=title,
                        description=t.get('notes') or '',
                        due_date=datetime.now(),
                        estimated_hours=1.0,
                        priority=3,
                        assignment_type='other'
                    )

                sched_task = ScheduledTask(
                    assignment=match,
                    scheduled_start=start_dt,
                    scheduled_end=end_dt,
                    day=start_dt.strftime('%A')
                )
                tasks.append(sched_task)

        schedule_obj = ScheduleOutput(
            course_name=syllabus_model.course_name or 'Course',
            schedule=tasks,
            summary=parsed.get('schedule_summary') or parsed.get('summary') or parsed.get('tips', ''),
            created_at=datetime.now(),
        )
    except Exception:
        # If parsing fails, store the raw response
        schedule_obj = schedule_raw

    session["schedule"] = schedule_obj

    return {"success": True, "schedule": schedule_obj}


# ======================
# EXPORT
# ======================
@app.post("/export-calendar")
async def export_calendar(request: dict):
    session_id = request.get("session_id", "default")
    fmt = (request.get("format", "ics") or "ics").lower()
    allowed = {"ics", "json", "md", "markdown"}
    if fmt == 'markdown':
        fmt = 'md'
    if fmt not in allowed:
        raise HTTPException(400, "Invalid export format; must be one of: ics, json, md")

    schedule = user_sessions.get(session_id, {}).get("schedule")

    if not schedule:
        raise HTTPException(400, "No schedule")

    # schedule may be a ScheduleOutput object or a raw AI string; handle both
    if fmt == "ics":
        if isinstance(schedule, ScheduleOutput):
            content = generate_ics_calendar(schedule)
        else:
            # cannot generate ICS from raw string; return raw text
            content = str(schedule)
        filename = "schedule.ics"
        media = "text/calendar"
    elif fmt == "json":
        if isinstance(schedule, ScheduleOutput):
            content = generate_json_schedule(schedule)
        else:
            # return raw JSON/string
            try:
                content = json.dumps(json.loads(schedule), indent=2)
            except Exception:
                content = json.dumps({"raw": str(schedule)})
        filename = "schedule.json"
        media = "application/json"
    else:
        if isinstance(schedule, ScheduleOutput):
            content = generate_markdown_schedule(schedule)
        else:
            content = str(schedule)
        filename = "schedule.md"
        media = "text/markdown"

    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmp:
        tmp.write(content)
        path = tmp.name

    return FileResponse(path, filename=filename, media_type=media)


# ======================
# RUN LOCAL
# ======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)