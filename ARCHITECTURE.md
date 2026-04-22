# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│              (http://localhost:5173)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   React App     │
                    │   (Frontend)    │
                    │  - Upload Page  │
                    │  - Calendar     │
                    │  - Schedule     │
                    │  - Export       │
                    └────────┬────────┘
                             │
                    HTTP/JSON │ (API Calls)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     FASTAPI BACKEND                             │
│                (http://localhost:8000)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Request Router (main.py)                    │  │
│  │  - POST /upload-syllabus                                 │  │
│  │  - POST /parse-syllabus                                  │  │
│  │  - GET  /authorize-calendar                              │  │
│  │  - POST /get-calendar-slots                              │  │
│  │  - POST /schedule                                        │  │
│  │  - POST /export-calendar                                 │  │
│  └──────────┬───────┬───────┬──────────┬──────────┬─────────┘  │
│             │       │       │          │          │             │
│  ┌──────────▼─┐ ┌───▼──┐ ┌─▼────────┐ ┌▼─────────┐ ┌────────┐ │
│  │   PDF      │ │Gemini│ │ Google   │ │Schedule  │ │Exporters
│  │  Parser    │ │  API │ │ Calendar │ │  Logic   │ │        │
│  │            │ │      │ │   API    │ │          │ │- ICS   │
│  │- Extract   │ │- Parse│ │          │ │- Balance │ │- MD    │
│  │  text      │ │Assign.│ │- OAuth   │ │ workload │ │- JSON  │
│  │            │ │       │ │- Get     │ │- Spread  │ │        │
│  │- Tables    │ │- Dates│ │ free     │ │  tasks   │ │        │
│  │            │ │       │ │ slots    │ │- Prioritize          │
│  └────────────┘ └───────┘ └──────────┘ └──────────┘ └────────┘
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
      ┌─────▼──────┐   ┌─────▼──────┐  ┌────▼────────┐
      │ Uploaded   │   │   Google   │  │    Google   │
      │  PDFs      │   │   Gemini   │  │  Calendar   │
      │ (temp)     │   │    API     │  │     API     │
      └────────────┘   └────────────┘  └─────────────┘
```

## Data Flow Diagram

```
┌─────────────────┐
│  User Uploads   │
│    PDF File     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Backend: pdf_parser.py         │
│  Extract text from PDF          │
│  (using pdfplumber)             │
└────────┬────────────────────────┘
         │
         ├──► Raw text
         │
         ▼
┌─────────────────────────────────┐
│   Frontend: Review Page         │
│   User edits extracted text     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Backend: gemini_scheduler.py   │
│  Send text to Gemini:           │
│  "Extract all assignments"      │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Google Gemini API             │
│   Returns parsed assignments    │
│   (JSON with dates, hours, etc) │
└────────┬────────────────────────┘
         │
         ├──► Assignments list
         │    (title, date, hours, priority)
         │
         ▼
┌─────────────────────────────────┐
│  Frontend: Calendar Page        │
│  User authorizes Google         │
│  (optional: select dates)       │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Backend: calendar_service.py   │
│  Query Google Calendar          │
│  Get free time slots            │
└────────┬────────────────────────┘
         │
         ├──► Available time blocks
         │
         ▼
┌─────────────────────────────────┐
│  Backend: gemini_scheduler.py   │
│  Send to Gemini:                │
│  "Schedule these assignments"   │
│  "In these time slots"          │
│  "Avoid cramming"               │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Google Gemini API             │
│   Returns optimized schedule    │
│   (day-by-day task breakdown)   │
└────────┬────────────────────────┘
         │
         ├──► Scheduled tasks
         │    (assignment, date, time, notes)
         │
         ▼
┌─────────────────────────────────┐
│  Frontend: Schedule Page        │
│  Display day-by-day schedule   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Frontend: Export Page          │
│  User chooses export format     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Backend: exporters.py          │
│  Generate export file:          │
│  - ICS (calendar import)        │
│  - Markdown (readable doc)      │
│  - JSON (data format)           │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  User Downloads File            │
│  Can import to calendar app     │
│  or save as document            │
└─────────────────────────────────┘
```

## Component Interaction Diagram

```
                    ┌──────────────────┐
                    │   App.jsx        │
                    │  (Main Container)│
                    │  - Session ID    │
                    │  - Step Tracker  │
                    │  - Progress Bar  │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐          ┌──────────┐        ┌────────┐
   │ Upload  │          │ Calendar │        │Schedule│
   │ Page    │          │  Page    │        │ Page   │
   │         │          │          │        │        │
   │ 1. File │          │ 1. Auth  │        │1.Generate
   │ 2. Edit │          │ 2. Slots │        │2.Review
   │ 3. Send │          │ 3. Fetch │        │
   └────┬────┘          └────┬─────┘        └───┬────┘
        │                    │                   │
        └────────────────────┼───────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   Export Page    │
                    │                  │
                    │ 1. Choose format │
                    │ 2. Download      │
                    │ 3. Import to app │
                    └──────────────────┘

    API Client (client.js)
    ├─ api.uploadSyllabus(file)
    ├─ api.parseSyllabus(text, sessionId)
    ├─ api.authorizeCalendar()
    ├─ api.getCalendarSlots(dates, sessionId)
    ├─ api.createSchedule(sessionId)
    └─ api.exportCalendar(sessionId, format)
```

## Session State Management

```
┌──────────────────────────────────────┐
│     Session (user_sessions dict)     │
│     Key: session_id                  │
│     Value: {                         │
│       "syllabus_data": {             │
│         "course_name": "...",        │
│         "assignments": [...]         │
│       },                             │
│       "calendar_slots": [            │
│         {                            │
│           "start_time": "...",       │
│           "end_time": "...",         │
│           "day_of_week": "..."       │
│         }                            │
│       ],                             │
│       "schedule": {                  │
│         "schedule_summary": "...",   │
│         "daily_tasks": [...]         │
│       }                              │
│     }                                │
└──────────────────────────────────────┘

Session Lifecycle:
1. User starts app → sessionId created (timestamp)
2. Upload → parse → store syllabus_data
3. Authorize calendar → fetch slots → store calendar_slots
4. Generate schedule → store schedule
5. Export → read from schedule
6. Session ends (data not persisted in MVP)
```

## Database Schema (Future Enhancement)

```sql
-- Future: For production with persistence

CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email STRING UNIQUE,
  created_at TIMESTAMP
);

CREATE TABLE courses (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  name STRING,
  code STRING,
  created_at TIMESTAMP
);

CREATE TABLE assignments (
  id INTEGER PRIMARY KEY,
  course_id INTEGER FOREIGN KEY,
  title STRING,
  description TEXT,
  due_date DATE,
  estimated_hours FLOAT,
  priority INTEGER,
  assignment_type STRING,
  created_at TIMESTAMP
);

CREATE TABLE schedules (
  id INTEGER PRIMARY KEY,
  course_id INTEGER FOREIGN KEY,
  generated_at TIMESTAMP,
  schedule_data JSON
);

-- Indexes for performance
CREATE INDEX idx_user_courses ON courses(user_id);
CREATE INDEX idx_course_assignments ON assignments(course_id);
```

## Security Considerations

```
Frontend (React)
├─ No sensitive data stored
├─ API keys never exposed
├─ CORS controlled by backend
└─ Session ID generated on client side

Backend (FastAPI)
├─ Environment variables for API keys
├─ CORS whitelist (localhost only in dev)
├─ Input validation on all endpoints
├─ Google OAuth for calendar access
└─ Session data in memory (not persistent)

Google Calendar
├─ OAuth 2.0 authentication
├─ Read-only access (MVP)
├─ Credentials file in .gitignore
└─ Token refresh handled automatically

Gemini API
├─ API key (`GOOGLE_API_KEY`) in .env (never in code)
├─ HTTPS only
├─ No data persistence by default
└─ Latest security patches via pip install
```

## Performance Optimization

```
Frontend:
- React.lazy() for code splitting (future)
- Axios caching (future)
- Debounced form inputs

Backend:
- Async request handling (FastAPI default)
- PDF streaming (not loading whole file)
- Gemini prompt optimization
- Google Calendar batch queries

Browser:
- CSS minification (Vite)
- Bundle optimization (Vite)
- Client-side caching (future)
```
