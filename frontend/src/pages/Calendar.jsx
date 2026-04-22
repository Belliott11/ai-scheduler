import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import "../styles/Calendar.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function CalendarPage({ sessionId, onCalendarData }) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    if (searchParams.get('connected') === 'true') {
      setIsConnected(true);
      setError(""); // clear any error
    }
  }, [searchParams]);

  // ✅ REAL OAUTH FLOW (FIXED)
  const authorize = () => {
    // open authorization in a new tab so users keep the app open
    window.open(`${API_URL}/authorize-calendar`, "_blank", "noopener,noreferrer");
  };

  const fetchSlots = async () => {
    if (!startDate || !endDate) {
      setError("Please select both dates");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await api.getCalendarSlots(
        startDate,
        endDate,
        sessionId
      );

      setSlots(res.data.slots || []);
      onCalendarData?.(res.data.slots || []);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to fetch slots");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h1>📅 Find Your Free Time</h1>
      <p className="description">Connect your calendar and we'll automatically identify when you can study.</p>

      {/* STEP 1 */}
      <div className="instructions">
        <h3>📅 Connect Your Calendar</h3>
        <p>By connecting your Google Calendar, we can automatically find your free time blocks for studying.</p>
      </div>

      <div className="card">
        <h3>Step 1: Authorize Google Calendar</h3>
        <p className="description">Click the button below to grant us access to view your calendar availability.</p>

        {isConnected ? (
          <p style={{ color: 'green', fontWeight: 'bold' }}>✅ Calendar Connected Successfully!</p>
        ) : (
          <button onClick={authorize} style={{ marginTop: '16px' }}>
            🔗 Connect Google Calendar
          </button>
        )}

        <p className="description" style={{ fontSize: '0.85rem', marginTop: '12px', color: 'var(--text-secondary)' }}>
          We only read your free/busy information and never modify your calendar.
        </p>
      </div>

      {/* STEP 2 */}
      <div className="card">
        <h3>Step 2: Select Your Study Period</h3>
        <p className="description">Choose the date range you want to plan your studies for:</p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="input"
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="input"
            />
          </div>
        </div>

        <button onClick={fetchSlots} disabled={loading} style={{ marginTop: '16px' }}>
          {loading ? "⏳ Finding your free time..." : "🔍 Analyze Calendar"}
        </button>
      </div>

      {/* RESULTS */}
      {slots.length > 0 && (
        <div className="card">
          <h3>✅ Available Time Slots Found</h3>
          <p className="description">We found {slots.length} free time blocks in your calendar:</p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px', marginTop: '16px' }}>
            {slots.map((s, i) => (
              <div key={i} style={{ 
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(99, 102, 241, 0.1))',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid var(--card-light)'
              }}>
                <div style={{ fontWeight: '600', color: 'var(--accent)', marginBottom: '8px' }}>📌 {s.day_of_week}</div>
                <p style={{ fontSize: '0.9rem', margin: '4px 0', color: 'var(--text-secondary)' }}>Start: {s.start_time}</p>
                <p style={{ fontSize: '0.9rem', margin: '4px 0', color: 'var(--text-secondary)' }}>End: {s.end_time}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && <p className="error">{error}</p>}
    </div>
  );
}