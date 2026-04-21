"""Main FastAPI application"""
import os
import tempfile
import json
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from dotenv import load_dotenv

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from models import SyllabusData, CalendarSlot, Assignment
from services.pdf_parser import extract_text_from_pdf
from services.claude_scheduler import parse_syllabus_with_claude, generate_schedule_with_claude
from services.exporters import generate_markdown_schedule, generate_ics_calendar, generate_json_schedule
from services.workload_predictor import get_predictor

# ======================
# LOAD ENV
# ======================
load_dotenv()

app = FastAPI(
    title="AI Scheduler API",
    version="0.1.0"
)

# ======================
# CORS
# ======================
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

# ======================
# MEMORY STORE (MVP ONLY)
# ======================
user_sessions = {}

# ======================
# GOOGLE OAUTH CONFIG
# ======================
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

REDIRECT_URI = "http://localhost:8000/oauth/callback"


# ======================
# HEALTH
# ======================
@app.get("/health")
def health():
    return {"status": "ok"}


# ======================
# SYLLABUS UPLOAD
# ======================
@app.post("/upload-syllabus")
async def upload_syllabus(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "PDF required")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        path = tmp.name

    text = extract_text_from_pdf(path)
    os.unlink(path)

    return {"success": True, "text": text}


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
        "created": datetime.now().isoformat()
    }

    return {"success": True, "session_id": session_id}


# ======================
# OAUTH START
# ======================
@app.get("/authorize-calendar")
def authorize_calendar():
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=GOOGLE_SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    user_sessions["oauth_state"] = state

    return RedirectResponse(auth_url)


# ======================
# OAUTH CALLBACK
# ======================
@app.get("/oauth/callback")
def oauth_callback(code: str, state: str):

    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=GOOGLE_SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI
    )

    flow.fetch_token(code=code)

    creds = flow.credentials

    user_sessions["google_creds"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }

    return RedirectResponse("http://localhost:5173/calendar?connected=true")


# ======================
# CALENDAR SLOT FETCH
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

    creds = Credentials(
        token=creds_data["token"],
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"],
    )

    service = build("calendar", "v3", credentials=creds)

    events = service.events().list(
        calendarId="primary",
        timeMin=f"{start_date}T00:00:00Z",
        timeMax=f"{end_date}T23:59:59Z",
        singleEvents=True
    ).execute()

    items = events.get("items", [])

    slots = [
        {
            "summary": e.get("summary", "Busy"),
            "start": e["start"].get("dateTime"),
            "end": e["end"].get("dateTime"),
        }
        for e in items if "start" in e
    ]

    if session_id not in user_sessions:
        user_sessions[session_id] = {}

    user_sessions[session_id]["calendar"] = slots

    return {
        "success": True,
        "slots": slots
    }


# ======================
# SCHEDULE GENERATION
# ======================
@app.post("/schedule")
async def create_schedule(request: dict):

    session_id = request.get("session_id", "default")

    session = user_sessions.get(session_id)
    if not session:
        raise HTTPException(400, "No session")

    syllabus = session.get("syllabus")
    calendar = session.get("calendar", [])

    schedule = generate_schedule_with_claude(syllabus, calendar)

    user_sessions[session_id]["schedule"] = schedule

    return {"success": True, "schedule": schedule}


# ======================
# EXPORT
# ======================
@app.post("/export-calendar")
async def export_calendar(request: dict):

    session_id = request.get("session_id", "default")
    fmt = request.get("format", "ics")

    schedule = user_sessions.get(session_id, {}).get("schedule")

    if not schedule:
        raise HTTPException(400, "No schedule")

    if fmt == "ics":
        content = generate_ics_calendar(schedule)
        file = "schedule.ics"
        media = "text/calendar"

    elif fmt == "json":
        content = json.dumps(schedule)
        file = "schedule.json"
        media = "application/json"

    else:
        content = generate_markdown_schedule(schedule)
        file = "schedule.md"
        media = "text/markdown"

    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmp:
        tmp.write(content)
        path = tmp.name

    return FileResponse(path, filename=file, media_type=media)


# ======================
# RUN
# ======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)