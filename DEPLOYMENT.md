# Deployment Guide

This guide explains how to deploy the AI Scheduler frontend to GitHub Pages and backend to a hosting service.

## Architecture

- **Frontend**: React + Vite (static files) → GitHub Pages
- **Backend**: FastAPI server → External hosting (Railway, Render, Heroku, etc.)

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

### Option 1: Railway (Recommended - Free tier available)

1. **Sign up**: https://railway.app
2. **Create new project** → **Deploy from GitHub**
3. **Connect your repository**
4. **Select the `backend` directory** as root
5. **Add environment variables**:
   - `GOOGLE_API_KEY`: Your Gemini API key
   - `DEBUG`: False
   - `SERVER_HOST`: 0.0.0.0
   - `SERVER_PORT`: 8000

6. **Deploy** - Railway will automatically detect it's a Python app
7. **Get your URL** from the Railway dashboard (e.g., `https://ai-scheduler-prod.railway.app`)

### Option 2: Render

1. **Sign up**: https://render.com
2. **New** → **Web Service**
3. **Connect GitHub repository**
4. **Configure**:
   - Name: `ai-scheduler-backend`
   - Runtime: `Python 3.11`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Region: Choose closest to you
5. **Add environment variables**:
   - `GOOGLE_API_KEY`: Your Gemini API key
   - `DEBUG`: False

6. **Deploy**
7. **Get your URL** from Render dashboard

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

Once your backend is deployed:

1. **Update API configuration**:
   - In `frontend/src/api/client.js`, update the API base URL:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.com';
   ```

2. **Or use environment variables** (recommended):
   - Create `.env.production` in frontend directory:
   ```env
   VITE_API_URL=https://your-backend-url.com
   ```

3. **Redeploy frontend**:
   ```bash
   git push origin main
   ```

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

### Backend Python build fails: "Failed to build 'pandas'"
**Cause**: Older pandas version (2.0.3) doesn't support Python 3.14  
**Status**: ✅ FIXED

Updated `backend/requirements.txt`:
- `pandas==2.0.3` → `pandas==2.1.4` (Python 3.14 compatible)
- `numpy==1.24.3` → `numpy==1.26.3` (matching compatibility)

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
