import axios from 'axios';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const api = {
  // Health check
  health: () => client.get('/health'),
  
  // Syllabus operations
  uploadSyllabus: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return client.post('/upload-syllabus', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  parseSyllabus: (syllabusText, sessionId) => 
    client.post('/parse-syllabus', {
      syllabus_text: syllabusText,
      session_id: sessionId
    }),
  
  // Calendar operations
  authorizeCalendar: () => client.get('/authorize-calendar'),
  
  getCalendarSlots: (startDate, endDate, sessionId) =>
    client.post('/get-calendar-slots', {
      start_date: startDate,
      end_date: endDate,
      session_id: sessionId
    }),
  
  // Scheduling
  createSchedule: (sessionId) =>
    client.post('/schedule', { session_id: sessionId }),
  
  // Export operations
  exportSchedule: (sessionId, format = 'json') =>
    client.post('/export-schedule-json', { session_id: sessionId }),
  
  exportCalendar: (sessionId, format = 'ics') =>
    client.post('/export-calendar', {
      session_id: sessionId,
      format: format
    }, {
      responseType: format === 'json' ? 'json' : 'blob'
    }),
  
  // Workload Predictor operations
  trainWorkloadPredictor: (historicalAssignments) =>
    client.post('/workload/train', {
      historical_assignments: historicalAssignments
    }),
  
  predictWorkload: (assignment) =>
    client.post('/workload/predict', {
      assignment: assignment
    }),
  
  batchPredictWorkload: (assignments) =>
    client.post('/workload/batch-predict', {
      assignments: assignments
    }),
  
  getWorkloadStats: () =>
    client.get('/workload/stats')
};

export default client;
