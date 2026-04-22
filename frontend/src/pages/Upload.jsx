import { useState } from "react";
import { api } from "../api/client";

export default function Upload({ next }) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

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

  const handleFileChange = (e) => {
    const f = e.target.files && e.target.files[0];
    setFile(f || null);
    setResult(null);
    setError("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    setUploading(true);
    setError("");
    setResult(null);

    try {
      const res = await api.uploadSyllabus(file);
      // show the returned data (API may return extracted text or structured JSON)
      setResult(res.data || { message: 'Upload successful' });
    } catch (e) {
      setError(e.response?.data?.detail || e.message || "Upload failed");
    } finally {
      setUploading(false);
    }
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
            onChange={handleFileChange}
          />
          {file && <div style={{ marginTop: 10 }}>{file.name}</div>}
          <div style={{ marginTop: 12 }}>
            <button onClick={handleUpload} disabled={uploading || !file} className="btn">
              {uploading ? 'Uploading…' : 'Upload Syllabus'}
            </button>
          </div>
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

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="card" style={{ marginTop: 20 }}>
          <h3>Upload Result</h3>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem' }}>{typeof result === 'string' ? result : JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      <div style={{ marginTop: 24 }}>
        <button 
          onClick={next}
          style={{ 
            padding: '14px 32px',
            fontSize: '1rem'
          }}
        >
          Continue to Next Step →
        </button>
      </div>
    </div>
  );
}