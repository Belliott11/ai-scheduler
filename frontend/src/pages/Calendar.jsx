import React, { useState } from "react";
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

  // ✅ REAL OAUTH FLOW (FIXED)
  const authorize = () => {
    window.location.href = `${API_URL}/authorize-calendar`;
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
      <h1>Calendar</h1>
      <p className="subtitle">Find your free time automatically</p>

      {/* STEP 1 */}
      <div className="card">
        <h3>1. Connect Google Calendar</h3>

        <button onClick={authorize}>
          Connect Google Calendar
        </button>

        <p className="hint">
          You will be redirected to Google to authorize access.
        </p>
      </div>

      {/* STEP 2 */}
      <div className="card">
        <h3>2. Select Date Range</h3>

        <div className="row">
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />

          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
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