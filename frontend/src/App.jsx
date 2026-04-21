import React, { useState, useEffect } from 'react';
import { UploadPage } from './pages/Upload';
import { CalendarPage } from './pages/Calendar';
import { SchedulePage } from './pages/Schedule';
import { ExportPage } from './pages/Export';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState('upload'); // 'upload' | 'calendar' | 'schedule' | 'export'
  const [sessionId] = useState(`session_${Date.now()}`);
  const [syllabusData, setSyllabusData] = useState(null);
  const [calendarData, setCalendarData] = useState(null);

  const handleSyllabusData = (data) => {
    setSyllabusData(data);
    setCurrentStep('calendar');
  };

  const handleCalendarData = (data) => {
    setCalendarData(data);
    setCurrentStep('schedule');
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1 className="logo">🎓 AI Scheduler</h1>
          <p className="tagline">Intelligently schedule your coursework with AI</p>
        </div>
        <div className="progress">
          <ProgressStep 
            number={1} 
            label="Syllabus" 
            active={currentStep === 'upload'}
            completed={syllabusData !== null}
            onClick={() => setCurrentStep('upload')}
          />
          <ProgressStep 
            number={2} 
            label="Calendar" 
            active={currentStep === 'calendar'}
            completed={calendarData !== null}
            onClick={() => syllabusData && setCurrentStep('calendar')}
            disabled={!syllabusData}
          />
          <ProgressStep 
            number={3} 
            label="Schedule" 
            active={currentStep === 'schedule'}
            completed={currentStep === 'export'}
            onClick={() => syllabusData && setCurrentStep('schedule')}
            disabled={!syllabusData}
          />
          <ProgressStep 
            number={4} 
            label="Export" 
            active={currentStep === 'export'}
            onClick={() => syllabusData && setCurrentStep('export')}
            disabled={!syllabusData}
          />
        </div>
      </header>

      <main className="main-content">
        {currentStep === 'upload' && (
          <UploadPage 
            sessionId={sessionId}
            onSyllabusData={handleSyllabusData}
          />
        )}
        {currentStep === 'calendar' && (
          <CalendarPage 
            sessionId={sessionId}
            onCalendarData={handleCalendarData}
            syllabusData={syllabusData}
          />
        )}
        {currentStep === 'schedule' && (
          <SchedulePage sessionId={sessionId} />
        )}
        {currentStep === 'export' && (
          <ExportPage sessionId={sessionId} />
        )}
      </main>

      <footer className="footer">
        <p>AI Scheduler © 2024 | Powered by Claude AI</p>
      </footer>
    </div>
  );
}

function ProgressStep({ number, label, active, completed, onClick, disabled }) {
  return (
    <button
      className={`progress-step ${active ? 'active' : ''} ${completed ? 'completed' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      <span className="step-number">{completed ? '✓' : number}</span>
      <span className="step-label">{label}</span>
    </button>
  );
}

export default App;
