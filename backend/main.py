"""Main FastAPI application"""
import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

from models import SyllabusData, CalendarSlot, ScheduleOutput, Assignment
from services.pdf_parser import extract_text_from_pdf
from services.claude_scheduler import parse_syllabus_with_claude, generate_schedule_with_claude
from services.calendar_service import get_calendar_service, get_free_slots, create_calendar_event
from services.exporters import generate_markdown_schedule, generate_ics_calendar, generate_json_schedule
from services.workload_predictor import get_predictor

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Scheduler API",
    description="Schedule your assignments intelligently with AI",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store state for MVP (in production, use a database)
user_sessions = {}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/upload-syllabus")
async def upload_syllabus(file: UploadFile = File(...)):
    """
    Upload and parse a syllabus PDF.
    Returns extracted text for review before processing.
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Extract text
        extracted_text = extract_text_from_pdf(tmp_path)
        
        # Clean up
        os.unlink(tmp_path)
        
        return {
            "success": True,
            "extracted_text": extracted_text,
            "filename": file.filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse-syllabus")
async def parse_syllabus(request: dict):
    """
    Parse syllabus text using Claude to extract assignments.
    
    Expected request body:
    {
        "syllabus_text": "Raw text from PDF or manual input",
        "session_id": "unique_session_id"
    }
    """
    try:
        syllabus_text = request.get("syllabus_text", "")
        session_id = request.get("session_id", "default")
        
        if not syllabus_text:
            raise HTTPException(status_code=400, detail="syllabus_text is required")
        
        # Parse with Claude
        parsed_data = parse_syllabus_with_claude(syllabus_text)
        
        # Store in session
        user_sessions[session_id] = {
            "syllabus_data": parsed_data,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "course_name": parsed_data.get("course_name"),
            "assignments_count": len(parsed_data.get("assignments", [])),
            "data": parsed_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/authorize-calendar")
async def authorize_calendar():
    """
    Initiate Google Calendar OAuth flow.
    For MVP, we'll provide instructions to set up credentials manually.
    """
    return {
        "message": "To use Google Calendar integration:",
        "steps": [
            "1. Go to https://console.cloud.google.com/",
            "2. Create a new project",
            "3. Enable Google Calendar API",
            "4. Create OAuth 2.0 credentials (Desktop app)",
            "5. Download credentials JSON and place in backend folder as 'credentials.json'",
            "6. Call /get-calendar-slots endpoint"
        ],
        "docs": "https://developers.google.com/calendar/api/quickstart/python"
    }


@app.post("/get-calendar-slots")
async def get_calendar_slots(request: dict):
    """
    Get free time slots from Google Calendar.
    
    Expected request body:
    {
        "start_date": "2024-01-15",
        "end_date": "2024-02-15",
        "session_id": "unique_session_id"
    }
    """
    try:
        start_date_str = request.get("start_date")
        end_date_str = request.get("end_date")
        session_id = request.get("session_id", "default")
        
        if not start_date_str or not end_date_str:
            raise HTTPException(
                status_code=400,
                detail="start_date and end_date are required (YYYY-MM-DD format)"
            )
        
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        
        # Initialize Google Calendar service
        service = get_calendar_service()
        
        # Get free slots
        free_slots = get_free_slots(service, start_date, end_date)
        
        # Store in session
        if session_id not in user_sessions:
            user_sessions[session_id] = {}
        user_sessions[session_id]["calendar_slots"] = [
            {
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat(),
                "day_of_week": slot.day_of_week
            }
            for slot in free_slots
        ]
        
        return {
            "success": True,
            "session_id": session_id,
            "free_slots_count": len(free_slots),
            "slots": user_sessions[session_id]["calendar_slots"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule")
async def create_schedule(request: dict):
    """
    Generate an optimized schedule using Claude.
    
    Expected request body:
    {
        "session_id": "unique_session_id"
    }
    """
    try:
        session_id = request.get("session_id", "default")
        
        if session_id not in user_sessions:
            raise HTTPException(status_code=400, detail="Invalid session_id")
        
        session = user_sessions[session_id]
        
        if "syllabus_data" not in session:
            raise HTTPException(
                status_code=400,
                detail="No syllabus data found. Parse syllabus first."
            )
        
        # Reconstruct objects from session data
        syllabus_dict = session["syllabus_data"]
        calendar_slots_data = session.get("calendar_slots", [])
        
        # Convert dict data to Pydantic models
        try:
            # Convert assignment dicts to Assignment objects
            assignments = []
            for a in syllabus_dict.get("assignments", []):
                assignments.append(Assignment(
                    title=a.get("title"),
                    description=a.get("description"),
                    due_date=datetime.fromisoformat(a.get("due_date")) if isinstance(a.get("due_date"), str) else a.get("due_date"),
                    estimated_hours=a.get("estimated_hours", 0),
                    priority=a.get("priority", 3),
                    assignment_type=a.get("assignment_type", "other")
                ))
            
            # Create SyllabusData object
            syllabus = SyllabusData(
                course_name=syllabus_dict.get("course_name", "Course"),
                course_code=syllabus_dict.get("course_code"),
                assignments=assignments
            )
            
            # Convert calendar slot dicts to CalendarSlot objects
            calendar_slots = []
            for slot in calendar_slots_data:
                calendar_slots.append(CalendarSlot(
                    start_time=datetime.fromisoformat(slot.get("start_time")) if isinstance(slot.get("start_time"), str) else slot.get("start_time"),
                    end_time=datetime.fromisoformat(slot.get("end_time")) if isinstance(slot.get("end_time"), str) else slot.get("end_time"),
                    day_of_week=slot.get("day_of_week", "")
                ))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
        
        # Generate schedule with Claude
        schedule_json_str = generate_schedule_with_claude(
            syllabus,
            calendar_slots,
        )
        
        # Parse Claude's response
        try:
            start_idx = schedule_json_str.find('{')
            end_idx = schedule_json_str.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                schedule_dict = json.loads(schedule_json_str[start_idx:end_idx])
            else:
                schedule_dict = json.loads(schedule_json_str)
        except json.JSONDecodeError:
            schedule_dict = {"error": "Could not parse schedule", "raw": schedule_json_str}
        
        # Store schedule in session
        user_sessions[session_id]["schedule"] = schedule_dict
        
        return {
            "success": True,
            "session_id": session_id,
            "schedule": schedule_dict
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export-calendar")
async def export_calendar(request: dict):
    """
    Export schedule as ICS file (compatible with Google Calendar).
    
    Expected request body:
    {
        "session_id": "unique_session_id",
        "format": "ics|json|markdown"
    }
    """
    try:
        session_id = request.get("session_id", "default")
        export_format = request.get("format", "ics")
        
        if session_id not in user_sessions or "schedule" not in user_sessions[session_id]:
            raise HTTPException(
                status_code=400,
                detail="No schedule found. Generate schedule first."
            )
        
        schedule_dict = user_sessions[session_id]["schedule"]
        
        # Note: export_format parameter is not used in this endpoint
        # All export formats use the same /export-calendar endpoint
        if export_format == "ics":
            content = generate_ics_calendar(schedule_dict)
            filename = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics"
            media_type = "text/calendar"
        elif export_format == "markdown":
            content = generate_markdown_schedule(schedule_dict)
            filename = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            media_type = "text/markdown"
        elif export_format == "json":
            content = generate_json_schedule(schedule_dict)
            filename = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            media_type = "application/json"
        else:
            raise HTTPException(status_code=400, detail="Invalid export format. Supported formats: ics, markdown, json")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".tmp") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        return FileResponse(
            tmp_path,
            media_type=media_type,
            filename=filename
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export-schedule-json")
async def export_schedule_json(request: dict):
    """
    Get schedule as JSON (for display in frontend).
    """
    try:
        session_id = request.get("session_id", "default")
        
        if session_id not in user_sessions or "schedule" not in user_sessions[session_id]:
            raise HTTPException(
                status_code=400,
                detail="No schedule found. Generate schedule first."
            )
        
        schedule_dict = user_sessions[session_id]["schedule"]
        
        return {
            "success": True,
            "schedule": schedule_dict
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WORKLOAD PREDICTOR ENDPOINTS ====================

@app.post("/workload/train")
async def train_workload_predictor(request: dict):
    """
    Train the workload prediction model with historical assignment data.
    
    Expected request body:
    {
        "historical_assignments": [
            {
                "assignment_type": "essay|project|exam|reading|other",
                "priority": 1-5,
                "estimated_hours": 5.0,
                "actual_hours": 6.5,
                "grade": 92.0
            },
            ...
        ]
    }
    """
    try:
        historical = request.get("historical_assignments", [])
        
        if not historical:
            raise HTTPException(status_code=400, detail="historical_assignments required")
        
        predictor = get_predictor()
        result = predictor.train_model(historical)
        
        return {
            "success": True,
            **result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workload/predict")
async def predict_workload(request: dict):
    """
    Predict how long an assignment will take.
    
    Expected request body:
    {
        "assignment": {
            "assignment_type": "essay",
            "priority": 4,
            "estimated_hours": 5.0,
            "grade": 85.0
        }
    }
    """
    try:
        assignment = request.get("assignment")
        
        if not assignment:
            raise HTTPException(status_code=400, detail="assignment required")
        
        predictor = get_predictor()
        prediction = predictor.predict_workload(assignment)
        
        return {
            "success": True,
            "assignment": assignment,
            "prediction": prediction
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workload/batch-predict")
async def batch_predict_workload(request: dict):
    """
    Predict workload for multiple assignments.
    
    Expected request body:
    {
        "assignments": [
            {"assignment_type": "essay", "priority": 4, "estimated_hours": 5.0},
            {"assignment_type": "exam", "priority": 5, "estimated_hours": 8.0},
            ...
        ]
    }
    """
    try:
        assignments = request.get("assignments", [])
        
        if not assignments:
            raise HTTPException(status_code=400, detail="assignments required")
        
        predictor = get_predictor()
        predictions = predictor.batch_predict(assignments)
        
        return {
            "success": True,
            "count": len(assignments),
            "predictions": [
                {
                    "assignment": a,
                    "prediction": p
                }
                for a, p in zip(assignments, predictions)
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workload/stats")
async def get_workload_stats():
    """Get statistics about the workload predictor model"""
    try:
        predictor = get_predictor()
        stats = predictor.get_model_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("SERVER_HOST", "localhost")
    port = int(os.getenv("SERVER_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(app, host=host, port=port, reload=debug)
