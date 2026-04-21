"""Export functionality for schedules"""
import json
from datetime import datetime
from typing import List
from models import ScheduleOutput, ScheduledTask


def generate_markdown_schedule(schedule: ScheduleOutput) -> str:
    """
    Generate a markdown representation of the schedule.
    
    Args:
        schedule: ScheduleOutput object
        
    Returns:
        Markdown string
    """
    markdown = f"""# Study Schedule for {schedule.course_name}

Generated: {schedule.created_at.strftime('%B %d, %Y at %H:%M')}

## Schedule Summary
{schedule.summary}

## Daily Breakdown

"""
    
    # Group tasks by date
    tasks_by_date = {}
    for task in schedule.schedule:
        date_str = task.scheduled_start.strftime('%Y-%m-%d')
        if date_str not in tasks_by_date:
            tasks_by_date[date_str] = []
        tasks_by_date[date_str].append(task)
    
    # Generate daily sections
    for date_str in sorted(tasks_by_date.keys()):
        tasks = tasks_by_date[date_str]
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        markdown += f"### {date_obj.strftime('%A, %B %d, %Y')}\n\n"
        
        for task in sorted(tasks, key=lambda t: t.scheduled_start):
            start = task.scheduled_start.strftime('%H:%M')
            end = task.scheduled_end.strftime('%H:%M')
            markdown += f"- **{start} - {end}**: {task.assignment.title}\n"
            if task.assignment.description:
                markdown += f"  - {task.assignment.description}\n"
        
        markdown += "\n"
    
    return markdown


def generate_ics_calendar(schedule: ScheduleOutput) -> str:
    """
    Generate an ICS calendar file content.
    
    Args:
        schedule: ScheduleOutput object
        
    Returns:
        ICS format string
    """
    ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI Scheduler//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:AI Scheduler - Study Schedule
X-WR-TIMEZONE:UTC
"""
    
    for task in schedule.schedule:
        start = task.scheduled_start.strftime('%Y%m%dT%H%M%SZ')
        end = task.scheduled_end.strftime('%Y%m%dT%H%M%SZ')
        
        ics += f"""BEGIN:VEVENT
DTSTART:{start}
DTEND:{end}
SUMMARY:{task.assignment.title}
DESCRIPTION:{task.assignment.description or 'Study session'}
CREATED:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
LAST-MODIFIED:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
SEQUENCE:0
STATUS:CONFIRMED
TRANSP:OPAQUE
UID:{task.assignment.title}-{task.scheduled_start.timestamp()}@aischeduler.local
END:VEVENT
"""
    
    ics += "END:VCALENDAR"
    return ics


def generate_json_schedule(schedule: ScheduleOutput) -> str:
    """
    Generate JSON representation of the schedule.
    
    Args:
        schedule: ScheduleOutput object
        
    Returns:
        JSON string
    """
    schedule_dict = {
        "course_name": schedule.course_name,
        "created_at": schedule.created_at.isoformat(),
        "summary": schedule.summary,
        "tasks": [
            {
                "assignment_title": task.assignment.title,
                "description": task.assignment.description,
                "due_date": task.assignment.due_date.isoformat(),
                "scheduled_start": task.scheduled_start.isoformat(),
                "scheduled_end": task.scheduled_end.isoformat(),
                "estimated_hours": task.assignment.estimated_hours,
                "priority": task.assignment.priority,
                "type": task.assignment.assignment_type
            }
            for task in schedule.schedule
        ]
    }
    
    return json.dumps(schedule_dict, indent=2)
