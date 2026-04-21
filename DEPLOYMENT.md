# Deployment Guide

This guide explains how to deploy the AI Scheduler frontend to GitHub Pages and backend to a hosting service.

## Quick Start Checklist

- [ ] **Step 1**: Push code to GitHub main branch (triggers frontend deployment)
- [ ] **Step 2**: Verify GitHub Actions workflow passes (check Actions tab)
- [ ] **Step 3**: Deploy backend to Render/Railway
- [ ] **Step 4**: Update frontend environment variables with backend URL  
- [ ] **Step 5**: Verify frontend at `https://yourusername.github.io/ai-scheduler/`
- [ ] **Step 6**: Test API calls in browser console

## Getting Started: Deploy This Now

### 1️⃣ Push to GitHub (Frontend Auto-Deploys)

```bash
# Commit all changes
git add .
git commit -m "Fix CORS configuration and update deployment"
git push origin main
```

Then:
- Go to GitHub **Actions** tab
- Wait for "Deploy to GitHub Pages" workflow to complete ✅
- Your frontend will be live at: `https://yourusername.github.io/ai-scheduler/`

### 2️⃣ Deploy Backend to Render (5 minutes)

1. Go to https://render.com and sign up with GitHub
2. Click **"New +"** → **Web Service**
3. Select your `ai-scheduler` repository
4. Configure:
   - Name: `ai-scheduler-backend`
   - Environment: `Python 3.11`
   - Root Directory: `backend` ⚠️ Important!
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Add Environment Variables:
   - `GOOGLE_API_KEY`: [Get from here](https://makersuite.google.com/app/apikey)
   - `DEBUG`: `False`
6. Click **"Create Web Service"** and wait for deployment
7. Copy your backend URL when ready

### 3️⃣ Connect Frontend to Backend

Update `frontend/.env.production`:
```env
VITE_API_URL=https://your-render-backend-url.onrender.com
VITE_BASE_PATH=/ai-scheduler/
```

Then push to trigger rebuild:
```bash
git add frontend/.env.production
git commit -m "Update backend URL"
git push origin main
```

### ✅ Done! 

Visit `https://yourusername.github.io/ai-scheduler/` and test it out!

---

## Frontend Deployment (GitHub Pages)

### Prerequisites
- GitHub account
- Repository pushed to GitHub

### Step 1: Configure GitHub Pages

1. Go to your GitHub repository
2. Click **Settings** → **Pages**
3. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **gh-pages**
   - Folder: **/ (root)**
4. Click **Save**

### Step 2: Enable GitHub Actions

GitHub Actions is already configured via `.github/workflows/deploy.yml`

1. Go to your repository
2. Click **Actions**
3. Confirm workflows are enabled

### Step 2b: Update Backend URL in Workflow (Optional but Recommended)

To set your backend URL for production builds:

1. Edit `.github/workflows/deploy.yml`
2. Find the "Build" step
3. Update `VITE_API_URL`:
   ```yaml
   - name: Build
     working-directory: ./frontend
     run: npm run build
     env:
       VITE_BASE_PATH: /ai-scheduler/
       VITE_API_URL: https://your-backend-url.com  # ← Update this
   ```
4. Push the change to trigger a rebuild with the new URL

### Step 3: Deploy

Simply push to `main` branch:
```bash
git add .
git commit -m "Deploy to GitHub Pages"
git push origin main
```

The workflow will automatically:
1. Checkout your code
2. Set up Node.js 18
3. Install frontend dependencies (`npm install`)
4. Build with Vite (`npm run build`)
5. Deploy to GitHub Pages

⏱️ **Build time**: ~2-3 minutes

**Your site will be live at**: `https://yourusername.github.io/ai-scheduler/`

### Verify Deployment

After pushing:
1. Go to **Actions** tab
2. Check the latest workflow run status
3. Once ✅ passes, visit your live site
4. You should see the AI Scheduler interface

## Backend Deployment

Since GitHub Pages only hosts static files, you need to deploy the FastAPI backend separately.

### Quick Recommendation: **Render** 
- Free tier includes 750 free hours/month
- Auto-deploys from GitHub (no manual steps)
- Good for hobby projects

See detailed instructions below: ⬇️

### Option 1: Railway (Recommended - Simple setup)

1. **Sign up**: https://railway.app
2. **Create new project** → **Deploy from GitHub**
3. **Connect your repository**
4. **Select the `backend` directory** as root
5. **Add environment variables**:
   - `GOOGLE_API_KEY`: Your Gemini API key
   - `DEBUG`: False
   - `SERVER_HOST`: 0.0.0.0
   - `SERVER_PORT`: 8000
   - `PYTHON_VERSION`: `3.11` ⚠️ Important - specify 3.11, not 3.14

6. **Deploy** - Railway will automatically detect it's a Python app
7. **Get your URL** from the Railway dashboard (e.g., `https://ai-scheduler-prod.railway.app`)

### Option 2: Render (Recommended - Easiest setup)

1. **Sign up**: https://render.com
2. **Create new Web Service**: Click "New +" → **Web Service**
3. **Connect GitHub**: 
   - Click "Connect account" and authorize GitHub
   - Select your `ai-scheduler` repository
4. **Configure deployment**:
   - Name: `ai-scheduler-backend`
   - Environment: **Python 3.11** ⚠️ **DO NOT use Python 3.14** (pandas incompatibility)
   - Root Directory: `backend` ✅ Important!
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Region: Choose closest to you
5. **Set environment variables** (in Render dashboard):
   - `GOOGLE_API_KEY`: [Get from Google AI Studio](#getting-google-api-key)
   - `DEBUG`: `False`
6. **Deploy**: Click "Create Web Service"
7. **Get URL**: Once deployed, copy your URL (e.g., `https://ai-scheduler-backend.onrender.com`)

#### Getting Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key
4. Paste in Render environment variables

✅ **Render will auto-deploy when you push to main** (you don't need to redeploy manually)

### Option 3: Heroku (Paid but reliable)

1. **Sign up**: https://heroku.com
2. **Create app** → **Connect to GitHub**
3. **Deploy branch**: main
4. **Add Procfile** to backend directory:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. **Set environment variables** in Heroku dashboard
6. **Deploy**

### Option 4: Vercel (Limited - no persistent state for MVP)

Not ideal because Vercel is serverless and your FastAPI uses session memory (`user_sessions = {}`). For production, you'd need a database anyway.

## Connecting Frontend to Backend

### Step 1: Get Your Backend URL

After deploying the backend, you'll have a URL like:
- **Render**: `https://ai-scheduler-backend.onrender.com`
- **Railway**: `https://ai-scheduler-prod.railway.app`

### Step 2: Update Environment Variables

Edit `frontend/.env.production`:
```env
VITE_API_URL=https://ai-scheduler-backend.onrender.com
VITE_BASE_PATH=/ai-scheduler/
```

Replace the URL with your actual backend URL.

### Step 3: Redeploy Frontend

Push to GitHub to trigger redeployment:
```bash
git add frontend/.env.production
git commit -m "Update backend URL for production"
git push origin main
```

### Step 4: Verify Connection

1. Go to **Actions** tab and wait for build to complete ✅
2. Visit `https://yourusername.github.io/ai-scheduler/`
3. Open **browser console** (F12)
4. Try uploading a PDF - you should see API calls in the Network tab

If you see CORS errors, check:
- Backend URL is correct in `.env.production`
- Backend API is running and accessible
- Your GitHub username is in `backend/main.py` CORS config (if not using Render env variables)

## Testing Locally Before Deployment

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with GOOGLE_API_KEY
echo GOOGLE_API_KEY=your_key_here > .env
echo DEBUG=True >> .env

# Run server
uvicorn main:app --reload
```

Server will be at: `http://localhost:8000`

Health check: Visit `http://localhost:8000/health`

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend will be at: `http://localhost:5173`

### Test the Application
1. Open `http://localhost:5173` in browser
2. Try uploading a test PDF
3. Check **Network** tab (F12) to see API calls
4. Should see successful responses from backend

### Verify CORS Works
Open browser console and run:
```javascript
fetch('http://localhost:8000/health').then(r => r.json()).then(console.log)
```

Should see: `{status: "healthy", timestamp: "..."}`

## Environment Variables Setup

### Frontend (.env for local dev, .env.production for build)
```env
VITE_API_URL=http://localhost:8000  # Local dev
VITE_BASE_PATH=/ai-scheduler/       # GitHub Pages path
```

### Backend (.env file)
```env
GOOGLE_API_KEY=your_gemini_api_key
DEBUG=False
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## Troubleshooting Deployment

### GitHub Actions permission error: "Permission denied to github-actions[bot]"
**Cause**: The workflow doesn't have write permissions to push to gh-pages branch  
**Status**: ✅ FIXED in latest workflow

The workflow now includes:
```yaml
jobs:
  build:
    permissions:
      contents: write
```

This allows the workflow to create and push the gh-pages branch automatically.

### Backend Python build fails: "Failed to build 'pandas'" or "too few arguments to _PyLong_AsByteArray"
**Cause**: pandas incompatibility with Python 3.14. When deploying, platforms may default to Python 3.14, but pandas 2.1.4 has Cython C code incompatible with Python 3.14's internal API.  
**Status**: ✅ FIXED

**Solution**: 
1. **Explicitly select Python 3.11 or 3.12** in your deployment configuration
2. Do NOT use Python 3.14 (pandas not fully compatible yet)
3. For **Render**: In the Environment dropdown, select **Python 3.11** instead of the latest version
4. For **Railway**: Add environment variable `PYTHON_VERSION=3.11`
5. Updated `backend/requirements.txt` uses pandas==2.1.4 (compatible with Python 3.11-3.13)

### "Failed to build 'pandas'" or other Python errors
**Cause**: The workflow is trying to install Python backend dependencies  
**Fix**: Make sure GitHub Actions workflow is in `frontend` directory only

Check `.github/workflows/deploy.yml`:
- All npm steps should have `working-directory: ./frontend`
- No Python (pip) steps should be present

### Frontend won't load / npm cache errors
- GitHub Actions workflow failed? Check the "Actions" tab for detailed error logs
- Look for "npm install" or "npm run build" errors
- Verify `working-directory: ./frontend` is set in workflow
- Check if `frontend/package.json` exists and is valid JSON

### Backend API calls fail
- Verify backend URL in frontend API client
- Check backend logs for errors
- Ensure CORS is enabled in backend (it is by default)
- Verify GOOGLE_API_KEY is set in backend

### CORS errors
Backend already has CORS enabled for common ports. If needed, update in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourusername.github.io"],  # Your GitHub Pages URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Session data lost
The MVP stores sessions in memory. This means:
- Sessions are lost when server restarts
- Not suitable for production with multiple users
- For production, implement a database (PostgreSQL, MongoDB, etc.)

## Production Improvements

For a production deployment:

1. **Database**: Replace `user_sessions = {}` with a real database
   - PostgreSQL + SQLAlchemy recommended
   
2. **Authentication**: Add user login system
   
3. **Rate limiting**: Prevent API abuse
   
4. **Caching**: Cache Gemini responses
   
5. **Error handling**: Better logging and monitoring
   
6. **HTTPS**: Both services should use HTTPS (handled by GitHub Pages and most hosting services)

## Monitoring

After deployment:

1. **Frontend**: 
   - Check browser console for errors
   - Use GitHub Pages analytics
   
2. **Backend**:
   - Check hosting service logs
   - Monitor API response times
   - Set up error alerts

## Custom Domain (Optional)

If you want a custom domain instead of `yourusername.github.io/ai-scheduler`:

1. **Purchase domain** (Namecheap, GoDaddy, etc.)
2. **GitHub Pages**: Settings → Pages → Custom domain (add your domain)
3. **Update DNS records** as per your registrar
4. **Backend**: Add custom domain to allowed origins in CORS config

## Summary

| Component | Service | Free | Notes |
| --- | --- | --- | --- |
| Frontend | GitHub Pages | ✅ | Auto-deploys from main branch |
| Backend | Railway | ✅ | $5/month after free tier |
| Backend | Render | ✅ | Auto-deploys, cold start delays |
| Backend | Heroku | ❌ | $7/month, reliable |
| Database | Not implemented | ✅ | Use in-memory for MVP |

Choose Railway or Render for easiest free deployment!
