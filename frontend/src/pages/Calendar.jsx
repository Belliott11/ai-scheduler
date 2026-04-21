import React, { useState } from "react";
import { api } from "../api/client";
import "../styles/Calendar.css";

export function CalendarPage({ sessionId, onCalendarData }) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [authInfo, setAuthInfo] = useState(null);
  const [error, setError] = useState("");

  const authorize = async () => {
    try {
      const res = await api.authorizeCalendar();
      setAuthInfo(res.data);
    } catch {
      setError("Authorization failed");
    }
  };

  const fetchSlots = async () => {
    if (!startDate || !endDate) return;

    setLoading(true);
    setError("");

    try {
      const res = await api.getCalendarSlots(startDate, endDate, sessionId);
      setSlots(res.data.slots);
      onCalendarData(res.data.slots);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to fetch slots");
    }

    setLoading(false);
  };

  return (
    <div className="page">
      <h1>Calendar</h1>
      <p className="subtitle">Find your free time automatically</p>

      {/* STEP 1 */}
      <div className="card">
        <h3>1. Connect Google Calendar</h3>

        {!authInfo ? (
          <button onClick={authorize}>Connect Calendar</button>
        ) : (
          <div className="hint">
            Follow setup instructions below
          </div>
        )}

        {authInfo && (
          <ul>
            {authInfo.steps?.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        )}
      </div>

      {/* STEP 2 */}
      <div className="card">
        <h3>2. Select Date Range</h3>

        <div className="row">
          <input type="date" onChange={(e) => setStartDate(e.target.value)} />
          <input type="date" onChange={(e) => setEndDate(e.target.value)} />
        </div>

        <button onClick={fetchSlots} disabled={loading}>
          {loading ? "Finding free time..." : "Fetch Free Slots"}
        </button>
      </div>

      {/* RESULTS */}
      {slots.length > 0 && (
        <div className="card">
          <h3>Available Time Slots</h3>

          <div className="grid">
            {slots.map((s, i) => (
              <div key={i} className="slot">
                <strong>{s.day_of_week}</strong>
                <p>{s.start_time}</p>
                <p>{s.end_time}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && <p className="error">{error}</p>}
    </div>
  );
}