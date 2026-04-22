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
      <h1>🎯 Your Study Schedule</h1>
      <p className="description">AI-powered study plan optimized for your workload and availability.</p>

      {!schedule && (
        <>
          <div className="instructions">
            <h3>Ready to Generate Your Schedule?</h3>
            <p>Based on your course assignments and available time slots, our AI will create a personalized study schedule that:</p>
            <ul>
              <li>Distributes work evenly across available time blocks</li>
              <li>Prioritizes high-priority assignments and exams</li>
              <li>Accounts for assignment difficulty and estimated time</li>
              <li>Provides realistic study session recommendations</li>
            </ul>
          </div>

          <div className="card">
            <p className="description">Click the button below to generate your personalized study schedule:</p>
            <button 
              onClick={generate} 
              disabled={loading}
              style={{ marginTop: '16px', padding: '14px 32px', fontSize: '1rem' }}
            >
              {loading ? "⏳ Creating your schedule..." : "✨ Generate My Schedule"}
            </button>
          </div>
        </>
      )}

      {schedule && (
        <>
          <div className="card" style={{ background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(34, 197, 94, 0.1))', borderColor: 'var(--success-color)' }}>
            <h3 style={{ color: 'var(--success-color)', marginTop: 0 }}>✅ Schedule Generated Successfully</h3>
            <p className="description" style={{ color: 'var(--text-secondary)' }}>{schedule.schedule_summary}</p>
          </div>

          {schedule.daily_tasks?.map((day, i) => (
            <div key={i} className="card" style={{ animation: `fadeIn 0.6s ease-out ${i * 0.1}s both` }}>
              <h3 style={{ color: 'var(--accent)', marginTop: 0 }}>📅 {day.day} • {day.date}</h3>

              <div style={{ marginTop: '16px' }}>
                {day.tasks?.map((t, j) => (
                  <div key={j} style={{
                    background: 'rgba(59, 130, 246, 0.05)',
                    padding: '16px',
                    borderRadius: '8px',
                    marginBottom: '12px',
                    borderLeft: '4px solid var(--accent)',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)'}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                      <div style={{ fontWeight: '600', color: 'var(--text)', fontSize: '1.05rem' }}>
                        {t.assignment_title}
                      </div>
                      <div style={{ fontSize: '0.9rem', color: 'var(--accent)', fontWeight: '500' }}>
                        ⏱️ {t.start_time} → {t.end_time}
                      </div>
                    </div>
                    {t.notes && (
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '8px 0' }}>
                        📝 {t.notes}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          {schedule.tips && (
            <div className="card" style={{ background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 146, 60, 0.1))', borderColor: 'var(--warning-color)' }}>
              <h3 style={{ color: 'var(--warning-color)', marginTop: 0 }}>💡 Study Tips</h3>
              <p className="description" style={{ color: 'var(--text-secondary)' }}>{schedule.tips}</p>
            </div>
          )}
        </>
      )}

      {error && <div className="error-message">⚠️ {error}</div>}
    </div>
  );
}