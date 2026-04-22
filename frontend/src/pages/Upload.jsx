import { useState } from "react";

export default function Upload({ next }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    // Handle file drop logic here if needed
  };

  return (
    <div>
      <h1>📋 Upload Your Syllabus</h1>
      <p className="description">Let's get started! Upload your course syllabus to begin creating your study schedule.</p>

      {/* Instructions Card */}
      <div className="instructions">
        <h3>✨ How This Works</h3>
        <ol>
          <li><strong>Upload or Paste:</strong> Provide your syllabus as a PDF file or paste the text directly</li>
          <li><strong>Extract Assignments:</strong> We'll automatically identify all assignments, deadlines, and requirements</li>
          <li><strong>Review & Confirm:</strong> Check the extracted data and make any adjustments needed</li>
          <li><strong>Add Your Schedule:</strong> Tell us when you're available to study</li>
          <li><strong>Generate Plan:</strong> Get a personalized study schedule optimized for your workload</li>
        </ol>
      </div>

      {/* PDF Upload */}
      <div className="card">
        <h3>📄 Upload Document</h3>
        <div 
          className={`upload-area ${isDragging ? 'active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <span className="upload-icon">📤</span>
          <p style={{ fontSize: '1.1rem', fontWeight: '500', margin: '10px 0' }}>
            Drag & drop your syllabus here
          </p>
          <p style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>or</p>
          <input 
            type="file" 
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" 
            style={{ 
              padding: '8px 16px',
              cursor: 'pointer',
              fontSize: '0.95rem'
            }}
          />
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '12px' }}>
            Supported: PDF and DOCX files up to 10MB
          </p>
        </div>
      </div>

      {/* Text Paste */}
      <div className="card">
        <h3>✏️ Or Paste Syllabus Text</h3>
        <p className="description">If you can't upload a PDF, copy and paste the syllabus text below:</p>
        <textarea
          placeholder="Paste your course syllabus text here. Include course name, assignments, deadlines, and any other relevant details..."
          style={{ 
            width: "100%", 
            height: "180px",
            marginTop: "12px"
          }}
          className="text-area"
        />
      </div>

      {/* Tips */}
      <div className="instructions" style={{ background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(34, 197, 94, 0.1))', borderColor: 'var(--success-color)' }}>
        <h3 style={{ color: 'var(--success-color)' }}>💡 Tips for Best Results</h3>
        <ul style={{ marginLeft: '24px' }}>
          <li>Works with PDF and Word (.docx) files</li>
          <li>Include assignment names, types (essay, exam, project), and due dates</li>
          <li>Mention estimated time required for each task if available</li>
          <li>Include course name and instructor information</li>
          <li>The more detail you provide, the better our AI can help you</li>
        </ul>
      </div>

      <button 
        onClick={next}
        style={{ 
          marginTop: '24px',
          padding: '14px 32px',
          fontSize: '1rem'
        }}
      >
        Continue to Next Step →
      </button>
    </div>
  );
}