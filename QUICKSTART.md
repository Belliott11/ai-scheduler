# Quick Start Guide

## 1. Clone or Download the Project

The project is located at: `C:\Users\breso\Documents\ai-scheduler`

## 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
```

### Edit `.env` with your settings:

```env
GOOGLE_API_KEY=your_gemini_api_key_from_makersuite
DEBUG=True
SERVER_HOST=localhost
SERVER_PORT=8000
```

### Run backend:
```bash
python main.py
```
Backend will run at: `http://localhost:8000`

## 3. Set Up Frontend

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend will run at: `http://localhost:5173`

## 4. Open the App

Open your browser to: `http://localhost:5173`

## 5. Use the App

1. **Upload Syllabus**: Upload your PDF or paste text
2. **Connect Calendar** (optional): Link Google Calendar
3. **Generate Schedule**: Let Gemini create your study plan
4. **Export**: Download as ICS, Markdown, or JSON

## Getting API Keys

### Google Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Paste it into your `.env` file as `GOOGLE_API_KEY`

### Google Calendar (Optional)
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download JSON and save as `backend/credentials.json`

## Troubleshooting

| Problem | Solution |
| --- | --- |
| "Module not found" | Run `pip install -r requirements.txt` in backend |
| "Port already in use" | Change port in `.env` or vite.config.js |
| "GOOGLE_API_KEY" error | Check `.env` file exists with correct key from makersuite.google.com |
| Frontend won't load | Check backend is running at localhost:8000 |
| PDF extraction fails | Try copying/pasting text instead |

## Project Architecture

```
Frontend (React)              Backend (FastAPI)
    ↓                              ↓
Upload PDF        →      Parse with pdfplumber
  ↓                              ↓
Review Text       →      Send to Gemini API
  ↓                              ↓
Google Calendar   →      Fetch calendar slots
  ↓                              ↓
Generate Schedule →      Gemini schedules tasks
  ↓                              ↓
Export (ICS/MD)   →      Generate exports
```

## Next Steps

After setup:
1. Try uploading a test syllabus
2. Review extracted assignments
3. Generate a schedule
4. Export as ICS and import into calendar app

## For Production

### Backend
```bash
pip freeze > requirements.txt
# Then deploy with a production server like Gunicorn
gunicorn -w 4 main:app
```

### Frontend
```bash
npm run build
# Creates `dist/` folder - deploy this as static files
```

## Support

Check the main [README.md](README.md) for more details and troubleshooting.
