from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from fastapi.responses import RedirectResponse

GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# -----------------------------
# START OAUTH
# -----------------------------
@app.get("/authorize-calendar")
async def authorize_calendar():
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=GOOGLE_SCOPES,
        redirect_uri="http://localhost:8000/oauth/callback"
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes=True,
        prompt="consent"
    )

    user_sessions["oauth_state"] = state

    return RedirectResponse(auth_url)


# -----------------------------
# OAUTH CALLBACK
# -----------------------------
@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str):

    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=GOOGLE_SCOPES,
        state=state,
        redirect_uri="http://localhost:8000/oauth/callback"
    )

    flow.fetch_token(code=code)
    credentials = flow.credentials

    user_sessions["google_credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    return RedirectResponse("http://localhost:5173/calendar?connected=true")


# -----------------------------
# GET CALENDAR SLOTS
# -----------------------------
@app.post("/get-calendar-slots")
async def get_calendar_slots(request: dict):

    session_id = request.get("session_id", "default")
    start_date = request.get("start_date")
    end_date = request.get("end_date")

    creds_data = user_sessions.get("google_credentials")

    if not creds_data:
        raise HTTPException(status_code=401, detail="Calendar not connected")

    creds = Credentials(
        token=creds_data["token"],
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"],
    )

    service = get_calendar_service(creds)

    free_slots = get_free_slots(
        service,
        datetime.fromisoformat(start_date),
        datetime.fromisoformat(end_date)
    )

    if session_id not in user_sessions:
        user_sessions[session_id] = {}

    user_sessions[session_id]["calendar_slots"] = [
        {
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat(),
            "day_of_week": s.day_of_week
        }
        for s in free_slots
    ]

    return {
        "success": True,
        "slots": user_sessions[session_id]["calendar_slots"]
    }