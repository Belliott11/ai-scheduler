import React, { useState } from 'react';
import { api } from '../api/client';
import '../styles/Export.css';

export function ExportPage({ sessionId }) {
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
        <h1>📤 Export Your Schedule</h1>
        <p className="subtitle">
          Download your schedule in the format that works best for you.
        </p>

        <div className="export-options">
          <div className="export-card">
            <h3>📅 Google Calendar (.ics)</h3>
            <p>
              Download as an iCalendar file to import into Google Calendar,
              Outlook, or other calendar apps.
            </p>
            <button 
              onClick={() => handleExport('ics')}
              disabled={isLoading}
              className="btn btn-primary"
            >
              {isLoading ? 'Exporting...' : 'Export as ICS'}
            </button>
          </div>

          <div className="export-card">
            <h3>📝 Markdown Document</h3>
            <p>
              Download as a readable markdown file with your full schedule
              and study tips.
            </p>
            <button 
              onClick={() => handleExport('markdown')}
              disabled={isLoading}
              className="btn btn-primary"
            >
              {isLoading ? 'Exporting...' : 'Export as Markdown'}
            </button>
          </div>

          <div className="export-card">
            <h3>� JSON Format</h3>
            <p>
              Download as JSON for integration with other applications
              and tools.
            </p>
            <button 
              onClick={() => handleExport('json')}
              disabled={isLoading}
              className="btn btn-secondary"
            >
              {isLoading ? 'Exporting...' : 'Export as JSON'}
            </button>
          </div>
        </div>

        {exportSuccess && (
          <div className="success-message">
            ✅ Export successful! Check your downloads folder.
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
}
