from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Assignment(BaseModel):
    """Represents a single assignment from the syllabus"""
    title: str
    description: Optional[str] = None
    due_date: datetime
    estimated_hours: float
    priority: int  # 1-5, where 5 is highest priority
    assignment_type: str  # e.g., "essay", "project", "exam", "reading"


class SyllabusData(BaseModel):
    """Represents parsed syllabus data"""
    course_name: str
    course_code: Optional[str] = None
    assignments: List[Assignment]
    semester_start: Optional[datetime] = None
    semester_end: Optional[datetime] = None


class CalendarSlot(BaseModel):
    """Represents a free time slot in the calendar"""
    start_time: datetime
    end_time: datetime
    day_of_week: str


class ScheduledTask(BaseModel):
    """Represents a task scheduled for a specific time"""
    assignment: Assignment
    scheduled_start: datetime
    scheduled_end: datetime
    day: str


class ScheduleOutput(BaseModel):
    """Final schedule output"""
    course_name: str
    schedule: List[ScheduledTask]
    summary: str  # AI-generated summary of the schedule
    created_at: datetime
