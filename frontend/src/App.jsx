import "./styles.css";

function Sidebar() {
  return (
    <div className="sidebar">
      <h2>AI Scheduler</h2>
      <button className="primary">Upload Syllabus</button>
      <button>Connect Calendar</button>
      <button>View Schedule</button>
    </div>
  );
}

function UploadBox() {
  return (
    <div className="card">
      <h3>Upload Syllabus</h3>
      <div className="upload-box">
        <p>Drag & drop your syllabus PDF</p>
        <input type="file" accept="application/pdf" />
      </div>
    </div>
  );
}

function CalendarInput() {
  return (
    <div className="card">
      <h3>Availability</h3>
      <label>Start Date</label>
      <input type="date" />

      <label>End Date</label>
      <input type="date" />

      <button className="primary">Sync Calendar</button>
    </div>
  );
}

function AIPrompt() {
  return (
    <div className="card">
      <h3>Customize AI</h3>
      <textarea placeholder="Prioritize exams, avoid weekends..." />
      <button className="primary">Generate Schedule</button>
    </div>
  );
}

function SchedulePreview() {
  return (
    <div className="card">
      <h3>Schedule</h3>
      <div className="item">
        <strong>Essay Work</strong>
        <p>April 22 · 10:00–12:00</p>
      </div>
    </div>
  );
}

function MainPanel() {
  return (
    <div style={{ padding: "20px" }}>
      <UploadBox />
      <CalendarInput />
      <AIPrompt />
    </div>
  );
}

function RightPanel() {
  return (
    <div style={{ padding: "20px", borderLeft: "1px solid #1e293b" }}>
      <SchedulePreview />
    </div>
  );
}

export default function App() {
  return (
    <div className="app">
      <Sidebar />
      <MainPanel />
      <RightPanel />
    </div>
  );
}