import React, { useState } from "react";
import { api } from "../api/client";
import "../styles/Schedule.css";

export default function SchedulePage({ sessionId }) {
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await api.createSchedule(sessionId);
      setSchedule(res.data.schedule);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to generate schedule");
    }

    setLoading(false);
  };

  return (
    <div className="page">
      <h1>Schedule</h1>
      <p className="subtitle">AI-optimized study plan</p>

      {!schedule && (
        <div className="card">
          <p>Your schedule is not generated yet.</p>
          <button onClick={generate} disabled={loading}>
            {loading ? "Generating..." : "Generate Schedule"}
          </button>
        </div>
      )}

      {schedule && (
        <>
          <div className="card">
            <h3>Summary</h3>
            <p>{schedule.schedule_summary}</p>
          </div>

          {schedule.daily_tasks?.map((day, i) => (
            <div key={i} className="card">
              <h3>{day.day} • {day.date}</h3>

              <div className="timeline">
                {day.tasks?.map((t, j) => (
                  <div key={j} className="task">
                    <div className="time">
                      {t.start_time} → {t.end_time}
                    </div>
                    <div className="title">{t.assignment_title}</div>
                    <div className="note">{t.notes}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {schedule.tips && (
            <div className="card">
              <h3>Study Tips</h3>
              <p>{schedule.tips}</p>
            </div>
          )}
        </>
      )}

      {error && <p className="error">{error}</p>}
    </div>
  );
}