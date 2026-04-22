"""Google Gemini AI integration for scheduling logic"""
import json
import google.generativeai as genai
import os
from typing import Optional, List, Any, Dict
from models import SyllabusData, CalendarSlot, ScheduleOutput, ScheduledTask, Assignment
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it in your .env file.")
genai.configure(api_key=api_key)

# Use Gemini Pro model
model = genai.GenerativeModel('gemini-pro')


def parse_syllabus_with_gemini(syllabus_text: str) -> Dict[str, Any]:
    """
    Use Gemini to parse raw syllabus text and extract structured data.
    
    Args:
        syllabus_text: Raw text extracted from PDF or entered manually
        
    Returns:
        Dictionary with parsed assignments and course info
    """
    prompt = f"""
    Analyze the following syllabus text and extract all assignment/assessment information.
    
    Return a JSON object with this exact structure:
    {{
        "course_name": "Course Name (Code)",
        "assignments": [
            {{
                "title": "Assignment Title",
                "description": "Brief description",
                "due_date": "YYYY-MM-DD",
                "estimated_hours": 5.0,
                "priority": 4,
                "assignment_type": "essay|project|exam|reading|other"
            }}
        ]
    }}
    
    Guidelines:
    - Extract ALL assignments, quizzes, exams, projects, and major deadlines
    - For due_date, use the format YYYY-MM-DD. If only a month is given, use the last day of that month
    - estimated_hours: Estimate based on assignment type and description. Typical values: reading=2-5, essay=5-10, project=10-20, exam=3-8
    - priority: 1-5 scale. Exams and major projects = 5. Regular assignments = 3-4. Optional readings = 1-2
    - If specific dates aren't clear, note "date_uncertain": true
    
    SYLLABUS TEXT:
    {syllabus_text}
    """
    
    response = model.generate_content(prompt)
    response_text = response.text
    
    # Extract JSON from response
    try:
        # Find JSON in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    raise ValueError("Failed to parse Gemini response as JSON")


def generate_schedule_with_gemini(
    syllabus: SyllabusData,
    calendar_slots: List[CalendarSlot],
    constraints: Optional[dict] = None
) -> str:
    """
    Use Gemini to generate an optimal schedule.
    
    Args:
        syllabus: Parsed syllabus data
        calendar_slots: List of available time slots
        constraints: Additional scheduling constraints
        
    Returns:
        JSON string with proposed schedule
    """
    
    # Validate inputs
    if not syllabus.assignments:
        raise ValueError("No assignments found in syllabus. Cannot generate schedule.")
    if not calendar_slots:
        raise ValueError("No available time slots. Cannot generate schedule.")
    
    # Format assignments for the prompt
    assignments_text = "\n".join([
        f"- {a.title} (Due: {a.due_date.strftime('%Y-%m-%d')}, {a.estimated_hours}h, Priority: {a.priority}/5)"
        for a in syllabus.assignments
    ])
    
    # Format calendar availability
    slots_text = "\n".join([
        f"- {slot.day_of_week}: {slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
        for slot in calendar_slots
    ])
    
    prompt = f"""
    You are an expert academic scheduler. Create an optimal study schedule that balances:
    1. Meeting all assignment deadlines
    2. Distributing work evenly (avoiding cramming)
    3. Respecting the student's available time
    4. Prioritizing high-importance assignments
    
    COURSE: {syllabus.course_name}
    
    ASSIGNMENTS TO COMPLETE:
    {assignments_text}
    
    AVAILABLE TIME SLOTS (per week):
    {slots_text}
    
    Generate a schedule as a JSON object with this structure:
    {{
        "schedule_summary": "Brief summary of the schedule strategy",
        "daily_tasks": [
            {{
                "date": "YYYY-MM-DD",
                "day": "Monday",
                "tasks": [
                    {{
                        "assignment_title": "Assignment Name",
                        "start_time": "HH:MM",
                        "end_time": "HH:MM",
                        "notes": "Why this time/order"
                    }}
                ]
            }}
        ],
        "tips": "General study tips for this schedule"
    }}
    
    Be realistic about:
    - Breaking large projects into multiple sessions
    - Starting major assignments 1-2 weeks before deadline
    - Spacing review sessions for exams
    - Not scheduling too many tasks on the same day
    """
    
    response = model.generate_content(prompt)
    return response.text
