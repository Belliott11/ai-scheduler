import React, { useState } from 'react';
import { api } from '../api/client';
import '../styles/Upload.css';

export function UploadPage({ sessionId, onSyllabusData }) {
  const [file, setFile] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState('upload'); // 'upload' | 'edit' | 'parse'

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      const response = await api.uploadSyllabus(file);
      setExtractedText(response.data.extracted_text);
      setStep('edit');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload PDF');
    } finally {
      setIsLoading(false);
    }
  };

  const handleParse = async () => {
    if (!extractedText.trim()) {
      setError('Please provide syllabus text');
      return;
    }

    setIsLoading(true);
    setError('');
    setStep('parse');
    
    try {
      const response = await api.parseSyllabus(extractedText, sessionId);
      onSyllabusData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to parse syllabus');
      setStep('edit');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page upload-page">
      <div className="container">
        <h1>📚 Upload Your Syllabus</h1>
        <p className="subtitle">
          Start by uploading your course syllabus (PDF) or pasting the text directly.
        </p>

        {step === 'upload' && (
          <div className="upload-section">
            <div className="file-input-wrapper">
              <label htmlFor="syllabus-file" className="file-label">
                <div className="file-input-area">
                  <span>📄 Choose PDF or drag and drop</span>
                  <input
                    id="syllabus-file"
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="file-input"
                  />
                </div>
              </label>
            </div>
            
            {file && <p className="file-selected">Selected: {file.name}</p>}
            
            <button 
              onClick={handleUpload} 
              disabled={!file || isLoading}
              className="btn btn-primary"
            >
              {isLoading ? 'Uploading...' : 'Upload & Extract'}
            </button>
          </div>
        )}

        {step === 'edit' && (
          <div className="edit-section">
            <h2>Review Extracted Text</h2>
            <p>Make any corrections before proceeding:</p>
            
            <textarea
              value={extractedText}
              onChange={(e) => setExtractedText(e.target.value)}
              className="text-area"
              rows="12"
              placeholder="Syllabus text will appear here..."
            />
            
            <div className="button-group">
              <button 
                onClick={() => setStep('upload')}
                className="btn btn-secondary"
              >
                Back
              </button>
              <button 
                onClick={handleParse} 
                disabled={isLoading}
                className="btn btn-primary"
              >
                {isLoading ? 'Parsing...' : 'Parse with AI'}
              </button>
            </div>
          </div>
        )}

        {step === 'parse' && (
          <div className="loading-section">
            <p>🤖 Claude is analyzing your syllabus...</p>
            <p>Extracting assignments, deadlines, and priorities...</p>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
}
