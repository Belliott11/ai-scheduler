# AI Scheduler - Complete Project Setup ✅

## What's Been Created

Your AI Scheduler application is now fully scaffolded and ready to run! Here's what you have:

### 📁 Project Structure
```
ai-scheduler/
├── backend/
│   ├── main.py                    # FastAPI app with all endpoints
│   ├── models.py                  # Data models
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example               # Environment template
│   ├── services/
│   │   ├── pdf_parser.py          # PDF extraction
│   │   ├── gemini_scheduler.py    # Gemini AI integration
│   │   ├── calendar_service.py    # Google Calendar API
│   │   └── exporters.py           # Schedule export formats
│   └── prompts/                   # Gemini prompts (expandable)
│
├── frontend/
│   ├── index.html                 # HTML entry
│   ├── package.json               # React dependencies
│   ├── vite.config.js             # Vite config
│   └── src/
│       ├── App.jsx                # Main component with routing
│       ├── App.css                # App layout styles
│       ├── index.css              # Global styles
│       ├── main.jsx               # React entry
│       ├── pages/
│       │   ├── Upload.jsx         # Step 1: Upload syllabus
│       │   ├── Calendar.jsx       # Step 2: Connect calendar
│       │   ├── Schedule.jsx       # Step 3: Generate schedule
│       │   └── Export.jsx         # Step 4: Export schedule
│       ├── api/
│       │   └── client.js          # API client wrapper
│       └── styles/
│           ├── Upload.css
│           ├── Calendar.css
│           ├── Schedule.css
│           └── Export.css
│
├── README.md                      # Full documentation
├── QUICKSTART.md                  # Quick setup guide
└── .gitignore                    # Git ignore rules
```

### 🎯 Core Features Implemented
1. **PDF Parsing** - Extract text from syllabus PDFs (pdfplumber)
2. **AI Analysis** - Parse assignments with Google Gemini API
3. **Schedule Generation** - Create optimized study schedules with Gemini
4. **Calendar Integration** - Sync with Google Calendar (optional)
5. **Multiple Export Formats** - ICS, Markdown, JSON

1. **Syllabus Processing**
   - PDF extraction using pdfplumber
   - Gemini AI parsing to extract assignments
   - Manual text editing before processing

2. **Calendar Integration**
   - Google Calendar OAuth setup
   - Free time slot detection
   - Session-based state management

3. **AI Scheduling**
   - Gemini API integration for intelligent scheduling
   - Balances workload, prevents cramming
   - Prioritizes high-importance tasks

4. **Export Options**
   - ICS format (import to any calendar app)
   - Markdown (readable document)
   - JSON (for programmatic access)

5. **Modern UI**
   - React + Vite frontend
   - Progress tracker showing steps
   - Responsive design
   - Professional styling

### 🚀 Getting Started (5 Minutes)

#### Step 1: Set Up Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and add your Gemini API key:
```env
GOOGLE_API_KEY=your_key_from_makersuite
```

Run backend:
```bash
python main.py
```
✅ Backend runs at: http://localhost:8000

#### Step 2: Set Up Frontend
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend runs at: http://localhost:5173

#### Step 3: Open the App
Open browser to: **http://localhost:5173**

### 📋 Application Flow

```
User Opens App
    ↓
[Step 1] Upload Syllabus PDF
    ↓ (PDF extracted by pdfplumber)
[Step 2] Review & Edit Text
    ↓ (Sent to Gemini)
Gemini Parses Assignments
    ↓
[Step 3] Optional: Connect Google Calendar
    ↓ (OAuth flow)
Fetch Free Time Slots
    ↓
[Step 4] Generate Schedule
    ↓ (Gemini creates optimized schedule)
Display Day-by-Day Schedule
    ↓
[Step 5] Export Options
    ↓
Download ICS / Markdown / JSON
    ↓ (User imports to calendar or saves document)
```

### 🔑 API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/upload-syllabus` | POST | Upload and extract PDF |
| `/parse-syllabus` | POST | Parse with Gemini |
| `/authorize-calendar` | GET | Get OAuth instructions |
| `/get-calendar-slots` | POST | Fetch free time slots |
| `/schedule` | POST | Generate optimized schedule |
| `/export-calendar` | POST | Export as ICS/Markdown/JSON |
| `/export-schedule-json` | POST | Get schedule as JSON |

### 🛠 Technology Stack

**Backend:**
- FastAPI (modern, fast Python web framework)
- Gemini API (Google's language model)
- pdfplumber (PDF extraction)
- Google Calendar API (calendar integration)
- Uvicorn (ASGI server)

**Frontend:**
- React 18 (UI library)
- Vite (ultra-fast build tool)
- Axios (HTTP client)
- Pure CSS (styling - no dependencies)

**Data Format:**
- JSON for all API communication
- ICS for calendar exports
- Markdown for human-readable exports

### 📝 Key Files Reference

**Backend Entry Points:**
- `backend/main.py` - Start FastAPI server here
- `backend/services/gemini_scheduler.py` - AI scheduling logic
- `backend/services/pdf_parser.py` - PDF processing

**Frontend Entry Points:**
- `frontend/src/App.jsx` - Main app with routing
- `frontend/src/pages/` - Individual pages
- `frontend/src/api/client.js` - API communication

### ⚙️ Configuration Files

**Backend:**
- `.env` - Environment variables
- `requirements.txt` - Python dependencies
- `vite.config.js` - (Frontend) Vite build config

**Frontend:**
- `package.json` - Node dependencies
- `vite.config.js` - Build tool config

### 📚 Documentation

- **README.md** - Complete feature documentation
- **QUICKSTART.md** - Quick setup guide
- **This file** - Project overview

### 🎓 Next Steps

1. **Get API Keys:**
    - Google (Gemini): https://makersuite.google.com/
   - Google (optional): https://console.cloud.google.com/

2. **Run the App:**
   - Follow the "Getting Started" section above

3. **Test with Sample:**
   - Create a simple test syllabus
    - Upload and watch Gemini parse it
   - Generate a schedule
   - Export and import to your calendar

4. **Customize:**
    - Modify Gemini prompts in `backend/services/gemini_scheduler.py`
   - Adjust colors in `frontend/src/index.css`
   - Add new features to pages

### 🔍 Common Customizations

**Change Gemini Model:**
In `backend/services/gemini_scheduler.py`, line ~50:
```python
# model selection handled via the google.generativeai client configuration
```

**Change Server Port:**
In `backend/.env`:
```
SERVER_PORT=8001  # Change from 8000
```

**Change Frontend Port:**
In `frontend/vite.config.js`, line ~6:
```javascript
port: 5174  // Change from 5173
```

**Customize UI Colors:**
In `frontend/src/index.css`, modify `:root` variables:
```css
--primary-color: #6366f1;  /* Change this */
```

### 🐛 Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `pip install -r requirements.txt` in backend |
| "ANTHROPIC_API_KEY" error | Create `.env` file with your API key |
| "Port in use" | Change port in `.env` or `vite.config.js` |
| "CORS error" | Backend CORS is pre-configured for localhost:5173 |
| "PDF extraction fails" | Use manual text input instead |

### 🚀 Production Deployment

**Backend Deployment:**
```bash
# Build
pip freeze > requirements.txt

# Deploy with Gunicorn
gunicorn -w 4 main:app
```

**Frontend Deployment:**
```bash
# Build static files
npm run build

# Deploy the `dist/` folder to any static host
# (Netlify, Vercel, AWS S3, GitHub Pages, etc.)
```

### 📞 Support Resources

- **Gemini Docs**: https://makersuite.google.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Google Calendar API**: https://developers.google.com/calendar/

### ✨ You're All Set!

Everything is ready to go. Just:
1. Add your API keys to `.env`
2. Run `python main.py` in backend folder
3. Run `npm run dev` in frontend folder
4. Open http://localhost:5173

Enjoy your AI Scheduler! 🎓📚
