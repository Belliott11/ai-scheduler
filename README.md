# AI Scheduler

An intelligent course scheduling application that uses Google Gemini AI to help you plan your assignments and balance your workload across your available time.

## Features

- 📄 **PDF Syllabus Upload**: Upload your course syllabus PDF and AI automatically extracts assignments, deadlines, and due dates
- 📅 **Google Calendar Integration**: Connect your Google Calendar to identify your free time slots
- 🤖 **AI-Powered Scheduling**: Gemini AI creates an optimized schedule that:
  - Balances workload across available time
  - Prevents cramming by spreading tasks appropriately
  - Prioritizes high-importance assignments (exams, major projects)
  - Provides study tips and schedule strategy
- � **Workload Predictor**: Machine learning model (R statistical analysis) that:
  - Predicts how long assignments will take based on historical data
  - Provides confidence intervals for predictions
  - Suggests optimal scheduling and session lengths
  - Works with or without R installed (graceful fallback)
- �📤 **Multiple Export Formats**: Download your schedule as:
  - `.ics` file (import to Google Calendar, Outlook, Apple Calendar)
  - Markdown document (readable timeline with notes)
  - JSON (for integration with other tools)

## Project Structure

```
ai-scheduler/
├── backend/                      # FastAPI Python backend
│   ├── main.py                  # FastAPI app entry point
│   ├── models.py                # Pydantic data models
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variables template
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py        # PDF extraction with pdfplumber
│   │   ├── claude_scheduler.py  # Gemini API integration
│   │   ├── calendar_service.py  # Google Calendar API integration
│   │   ├── workload_predictor.py # ML workload predictions (Python)
│   │   ├── workload_predictor.R  # Statistical models (R)
│   │   └── exporters.py         # Schedule export functionality
│   └── prompts/
│       └── (Claude prompt templates)
│
├── frontend/                     # React + Vite frontend
│   ├── index.html               # HTML entry point
│   ├── package.json             # Node dependencies
│   ├── vite.config.js           # Vite configuration
│   └── src/
│       ├── main.jsx             # React entry point
│       ├── App.jsx              # Main app component
│       ├── pages/
│       │   ├── Upload.jsx       # Syllabus upload page
│       │   ├── Calendar.jsx     # Calendar authorization page
│       │   ├── Schedule.jsx     # Schedule generation page
│       │   └── Export.jsx       # Schedule export page
│       ├── api/
│       │   └── client.js        # API client wrapper
│       ├── styles/
│       │   ├── Upload.css
│       │   ├── Calendar.css
│       │   ├── Schedule.css
│       │   └── Export.css
│       └── index.css            # Global styles
│
└── README.md                    # This file
```

## Getting Started

### Prerequisites

- **Python 3.8+** for the backend
- **Node.js 16+** for the frontend
- **Google Gemini API Key** (get free at https://makersuite.google.com/app/apikey)
- **Google Cloud Project** with Calendar API enabled (for calendar integration)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Google Gemini API key:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

5. **Run the FastAPI server**:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

### Google Calendar Setup (Optional)

To enable Google Calendar integration:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials (Application type: Desktop app)
5. Download the credentials JSON file
6. Place it in the `backend/` folder as `credentials.json`

On first use, the app will prompt you to authorize access to your Google Calendar.

## Usage

1. **Open the app** at `http://localhost:5173`
2. **Upload your syllabus** as a PDF (or paste text manually)
3. **Review and edit** the extracted assignment data
4. **Connect your Google Calendar** (optional) to account for existing commitments
5. **Generate your schedule** - Gemini AI will create an optimized plan
6. **Export** your schedule as an ICS file or markdown document

## API Endpoints

### Health Check
- `GET /health` - Check if the API is running

### Syllabus Processing
- `POST /upload-syllabus` - Upload and extract PDF
  - Request: `multipart/form-data` with `file` (PDF)
  - Response: `{success, extracted_text, filename}`

- `POST /parse-syllabus` - Parse syllabus text with Gemini
  - Request: `{syllabus_text, session_id}`
  - Response: `{success, session_id, course_name, assignments_count, data}`

### Calendar
- `GET /authorize-calendar` - Get authorization instructions

- `POST /get-calendar-slots` - Fetch free time from Google Calendar
  - Request: `{start_date, end_date, session_id}`
  - Response: `{success, session_id, free_slots_count, slots}`

### Scheduling
- `POST /schedule` - Generate optimized schedule
  - Request: `{session_id}`
  - Response: `{success, session_id, schedule}`

### Export
- `POST /export-calendar` - Export as ICS or other formats
  - Request: `{session_id, format: "ics"|"markdown"|"json"}`
  - Response: File download

- `POST /export-schedule-json` - Get schedule as JSON
  - Request: `{session_id}`
  - Response: `{success, schedule}`

## Data Models

### Assignment
```python
{
  "title": "Assignment Name",
  "description": "Brief description",
  "due_date": "2024-01-15",
  "estimated_hours": 5.0,
  "priority": 4,  # 1-5 scale
  "assignment_type": "essay|project|exam|reading|other"
}
```

### CalendarSlot
```python
{
  "start_time": "2024-01-15T09:00:00",
  "end_time": "2024-01-15T17:00:00",
  "day_of_week": "Monday"
}
```

### ScheduledTask
```python
{
  "assignment_title": "Assignment Name",
  "scheduled_start": "2024-01-15T14:00:00",
  "scheduled_end": "2024-01-15T16:00:00",
  "estimated_hours": 2.0,
  "priority": 4
}
```

## Environment Variables

### Backend (.env)
```
ANTHROPIC_API_KEY=your_key_here
GOOGLE_CREDENTIALS_PATH=./credentials.json
DEBUG=True
SERVER_HOST=localhost
SERVER_PORT=8000
```

## Development

### Running Tests
```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

### Building for Production

**Backend**:
```bash
pip freeze > requirements.txt
# Deploy with: pip install -r requirements.txt && gunicorn main:app
```

**Frontend**:
```bash
npm run build
# This creates a `dist/` folder ready for deployment
```

## Architecture

### Backend Flow
1. User uploads PDF → Extract text with pdfplumber
2. Send text to Gemini → Extract structured assignment data
3. User connects Google Calendar → Fetch free time slots
4. Send assignments + calendar to Gemini → Generate optimized schedule
5. **Optional**: Train and use Workload Predictor (ML model in R) for time estimates
6. Export schedule in multiple formats

### Workload Predictor (ML Component)
- Uses R statistical models (`lm()` linear regression)
- Predicts assignment duration based on historical data
- Provides confidence intervals and scheduling recommendations
- Falls back to heuristic if R unavailable
- See [WORKLOAD_PREDICTOR.md](WORKLOAD_PREDICTOR.md) for details

### Frontend Flow
1. Multi-step form guiding user through the process
2. Progress tracker showing completion status
3. Real-time error handling and loading states
4. Download/export functionality for generated schedules
5. Optional: Input historical assignments for workload prediction

## 🚀 Deployment

Ready to deploy? See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions:

- **Frontend**: Deploy to GitHub Pages (free) - automatically on every push to `main`
- **Backend**: Deploy to Railway, Render, or Heroku (free tier available)

**Quick Start**:
1. Push your code to GitHub
2. GitHub Actions automatically builds and deploys your frontend
3. Deploy backend to Railway (5 minutes)
4. Update API URL in frontend
5. Your app is live! 🎉

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed steps.

## Known Limitations (MVP)

- Single-session processing (data not persisted)
- No user authentication
- No database persistence
- Google Calendar is read-only (can fetch free time but not create events)
- Requires manual credentials setup for Google Calendar

## Future Enhancements

- [ ] User accounts and persistent data storage
- [ ] Write events directly to Google Calendar
- [ ] Support for other calendar systems (Outlook, Apple)
- [ ] Real-time schedule adjustments
- [ ] Collaboration features (share schedules with classmates)
- [ ] Mobile app
- [ ] Integration with course platforms (Canvas, Blackboard)
- [ ] Habit tracking and study reminders
- [ ] Performance analytics

## Troubleshooting

### "Failed to parse PDF"
- Ensure the file is a valid PDF
- Try extracting text manually and pasting it instead

### "ANTHROPIC_API_KEY not found"
- Check that you have an `.env` file in the `backend/` folder
- Verify your API key is correct
- Get a key from https://console.anthropic.com/

### "Google Calendar connection failed"
- Verify `credentials.json` is in the `backend/` folder
- Delete `token.pickle` and try authorizing again
- Check that Google Calendar API is enabled in Google Cloud Console

### "Port 8000 or 5173 already in use"
- Change port in `.env` (backend) or `vite.config.js` (frontend)
- Or kill the process using the port

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for personal or educational purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation
3. Open an issue on GitHub
4. Check Anthropic's Claude documentation: https://docs.anthropic.com/

## Credits

Built with:
- **FastAPI** - Modern Python web framework
- **React** - JavaScript UI library
- **Claude AI** - Anthropic's language model
- **Google Calendar API** - Calendar integration
- **Vite** - Frontend build tool
