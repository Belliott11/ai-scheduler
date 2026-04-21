import React, { useState } from 'react';
import { api } from '../api/client';
import '../styles/Schedule.css';

export function SchedulePage({ sessionId }) {
  const [schedule, setSchedule] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerateSchedule = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await api.createSchedule(sessionId);
      setSchedule(response.data.schedule);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate schedule');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page schedule-page">
      <div className="container">
        <h1>📖 Generated Schedule</h1>
        <p className="subtitle">
          Claude has intelligently scheduled your assignments.
        </p>

        {!schedule && (
          <div className="generate-section">
            <p>Click the button below to generate your personalized study schedule.</p>
            <button 
              onClick={handleGenerateSchedule}
              disabled={isLoading}
              className="btn btn-primary btn-large"
            >
              {isLoading ? '🤖 Generating Schedule...' : '✨ Generate Schedule'}
            </button>
          </div>
        )}

        {schedule && (
          <div className="schedule-display">
            <div className="schedule-summary">
              <h2>Schedule Summary</h2>
              <p>{schedule.schedule_summary}</p>
            </div>

            <div className="daily-tasks">
              <h2>Daily Breakdown</h2>
              {schedule.daily_tasks?.map((day, idx) => (
                <div key={idx} className="day-card">
                  <h3>{day.day} - {day.date}</h3>
                  <div className="tasks">
                    {day.tasks?.map((task, tidx) => (
                      <div key={tidx} className="task">
                        <strong className="task-time">
                          {task.start_time} - {task.end_time}
                        </strong>
                        <p className="task-title">{task.assignment_title}</p>
                        {task.notes && <p className="task-notes">{task.notes}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {schedule.tips && (
              <div className="tips-section">
                <h2>📝 Study Tips</h2>
                <p>{schedule.tips}</p>
              </div>
            )}
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
}
