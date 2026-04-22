import React, { useState } from 'react';
import { api } from '../api/client';
import '../styles/Export.css';

export default function ExportPage({ sessionId }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [exportSuccess, setExportSuccess] = useState(false);

  const handleExport = async (format) => {
    setIsLoading(true);
    setError('');
    setExportSuccess(false);
    
    try {
      const response = await api.exportCalendar(sessionId, format);
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      if (format === 'ics') {
        link.setAttribute('download', `schedule_${new Date().toISOString().split('T')[0]}.ics`);
      } else if (format === 'markdown') {
        link.setAttribute('download', `schedule_${new Date().toISOString().split('T')[0]}.md`);
      }
      
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      
      setExportSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to export as ${format}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page export-page">
      <div className="container">
        <h1>🎉 You're All Set!</h1>
        <p className="description">
          Your personalized study schedule is ready. Download it in your preferred format to start studying smarter.
        </p>

        <div className="instructions">
          <h3>📥 Choose Your Export Format</h3>
          <p>Select how you'd like to access your schedule:</p>
          <ul>
            <li><strong>Google Calendar:</strong> Sync directly with your calendar app</li>
            <li><strong>Markdown:</strong> Print-friendly document with detailed notes</li>
          </ul>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginTop: '24px' }}>
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>📅</div>
            <h3 style={{ marginTop: '0' }}>Google Calendar</h3>
            <p className="description" style={{ fontSize: '0.9rem' }}>
              Download as an iCalendar file (.ics) to import into Google Calendar, Outlook, Apple Calendar, or other apps.
            </p>
            <button 
              onClick={() => handleExport('ics')}
              disabled={isLoading}
              style={{ marginTop: '16px', width: '100%' }}
            >
              {isLoading ? '⏳ Exporting...' : '📥 Export as ICS'}
            </button>
          </div>

          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>📝</div>
            <h3 style={{ marginTop: '0' }}>Markdown Document</h3>
            <p className="description" style={{ fontSize: '0.9rem' }}>
              Download as a readable markdown file with your full schedule, assignments, and study tips. Perfect for printing.
            </p>
            <button 
              onClick={() => handleExport('markdown')}
              disabled={isLoading}
              style={{ marginTop: '16px', width: '100%' }}
            >
              {isLoading ? '⏳ Exporting...' : '📥 Export as Markdown'}
            </button>
          </div>
        </div>

        {exportSuccess && (
          <div className="success-message" style={{ marginTop: '24px' }}>
            ✅ <strong>Export successful!</strong> Your schedule has been downloaded. Check your downloads folder to get started!
          </div>
        )}

        {error && (
          <div className="error-message" style={{ marginTop: '24px' }}>
            ⚠️ <strong>Export failed:</strong> {error}
          </div>
        )}

        <div className="instructions" style={{ marginTop: '40px' }}>
          <h3>🚀 What's Next?</h3>
          <ul>
            <li><strong>Import to Calendar:</strong> Open the .ics file with your calendar app to add all study sessions</li>
            <li><strong>Set Reminders:</strong> Get notifications before each study session</li>
            <li><strong>Adjust as Needed:</strong> Feel free to modify the schedule based on how you're feeling</li>
            <li><strong>Track Progress:</strong> Monitor your assignments as you complete them</li>
          </ul>
          <p style={{ marginTop: '16px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            💡 Pro tip: Start with the first assignment and work through the schedule. Consistency is key to success!
          </p>
        </div>
      </div>
    </div>
  );
}
