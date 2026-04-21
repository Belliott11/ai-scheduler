import React, { useState } from 'react';
import { api } from '../api/client';
import '../styles/Calendar.css';

export function CalendarPage({ sessionId, onCalendarData, syllabusData }) {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [slots, setSlots] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [authInfo, setAuthInfo] = useState(null);

  const handleAuthorize = async () => {
    try {
      const response = await api.authorizeCalendar();
      setAuthInfo(response.data);
    } catch (err) {
      setError('Failed to get authorization info');
    }
  };

  const handleFetchSlots = async () => {
    if (!startDate || !endDate) {
      setError('Please select both start and end dates');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      const response = await api.getCalendarSlots(startDate, endDate, sessionId);
      setSlots(response.data.slots);
      onCalendarData(response.data.slots);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch calendar slots');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page calendar-page">
      <div className="container">
        <h1>📅 Connect Your Calendar</h1>
        <p className="subtitle">
          Link your Google Calendar to identify your free time slots.
        </p>

        {!authInfo && (
          <div className="auth-section">
            <h2>Step 1: Authorize Google Calendar</h2>
            <button 
              onClick={handleAuthorize}
              className="btn btn-google"
            >
              🔐 Setup Google Calendar
            </button>
          </div>
        )}

        {authInfo && (
          <div className="info-box">
            <h3>Google Calendar Setup Instructions</h3>
            <ol>
              {authInfo.steps?.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ol>
            <p>
              Once credentials are set up, fill in the date range below and click "Fetch Free Slots".
            </p>
          </div>
        )}

        <div className="date-section">
          <h2>Step 2: Select Date Range</h2>
          <p>Find free time slots between these dates:</p>
          
          <div className="date-inputs">
            <div className="input-group">
              <label htmlFor="start-date">Start Date</label>
              <input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="input"
              />
            </div>
            
            <div className="input-group">
              <label htmlFor="end-date">End Date</label>
              <input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="input"
              />
            </div>
          </div>

          <button 
            onClick={handleFetchSlots}
            disabled={isLoading || !startDate || !endDate}
            className="btn btn-primary"
          >
            {isLoading ? 'Fetching...' : 'Fetch Free Slots'}
          </button>
        </div>

        {slots.length > 0 && (
          <div className="slots-section">
            <h2>Available Time Slots ({slots.length} days)</h2>
            <div className="slots-list">
              {slots.map((slot, idx) => (
                <div key={idx} className="slot-card">
                  <strong>{slot.day_of_week}</strong>
                  <p>{slot.start_time} - {slot.end_time}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
}
