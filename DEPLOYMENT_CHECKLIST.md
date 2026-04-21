# Deployment Checklist

## ✅ Before Deployment

### Prerequisites
- [ ] GitHub account
- [ ] GitHub repository created and code pushed to `main` branch
- [ ] Google Gemini API key (free from https://makersuite.google.com/app/apikey)
- [ ] Backend hosting service account (Railway, Render, or Heroku)

### Code Setup
- [ ] Update `/frontend/vite.config.js` - ensure `base` path matches your repo name
- [ ] Update `/frontend/.env.production` - set VITE_API_URL to your backend URL
- [ ] Backend `.env` has `GOOGLE_API_KEY` set
- [ ] Verified `.gitignore` includes `.env` and `node_modules/`

## 🌐 Frontend Deployment (GitHub Pages)

### Step 1: GitHub Pages Configuration
- [ ] Go to repository Settings → Pages
- [ ] Ensure "Deploy from a branch" is selected
- [ ] Branch is set to `gh-pages`
- [ ] GitHub Actions workflow exists at `.github/workflows/deploy.yml`

### Step 2: Deploy Frontend
- [ ] Commit all changes to `main` branch
- [ ] Push to GitHub: `git push origin main`
- [ ] Go to Actions tab and verify build passes ✅
- [ ] Visit `https://yourusername.github.io/ai-scheduler/` 
- [ ] Verify frontend loads (you'll see "API Connection Error" until backend is deployed)

### Frontend Verification Checklist
- [ ] App loads at GitHub Pages URL
- [ ] Styling is correct
- [ ] Can reach upload page without errors

## 🔌 Backend Deployment (Choose One)

### Option A: Railway (Recommended)

- [ ] Sign up at https://railway.app
- [ ] Create new project from GitHub
- [ ] Select your repository
- [ ] Set `backend` as the root directory
- [ ] Add environment variables:
  - [ ] `GOOGLE_API_KEY` = your Gemini API key
  - [ ] `DEBUG` = False
  - [ ] `SERVER_HOST` = 0.0.0.0
  - [ ] `SERVER_PORT` = 8000
- [ ] Deploy
- [ ] Copy Railway URL (e.g., `https://ai-scheduler-prod.railway.app`)
- [ ] Set as `VITE_API_URL` in frontend

### Option B: Render

- [ ] Sign up at https://render.com
- [ ] New Web Service → Connect GitHub repo
- [ ] Set runtime to Python 3.11
- [ ] Set start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
- [ ] Add environment variables:
  - [ ] `GOOGLE_API_KEY` = your Gemini API key
  - [ ] `DEBUG` = False
- [ ] Deploy
- [ ] Copy Render URL
- [ ] Set as `VITE_API_URL` in frontend

### Option C: Heroku

- [ ] Sign up at https://heroku.com
- [ ] Create `backend/Procfile`:
  ```
  web: uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- [ ] Push to Heroku: `git push heroku main`
- [ ] Add environment variables in Heroku dashboard
- [ ] Copy Heroku URL
- [ ] Set as `VITE_API_URL` in frontend

## 🔗 Connect Frontend to Backend

- [ ] Update `VITE_API_URL` in `frontend/.env.production`
- [ ] Commit and push to `main` branch
- [ ] Verify GitHub Actions builds successfully
- [ ] Wait for frontend to redeploy (~5 minutes)
- [ ] Visit your GitHub Pages site
- [ ] Test API calls (health check should work)

## 🧪 Final Testing

### Health Check
- [ ] Visit `https://yourusername.github.io/ai-scheduler/`
- [ ] Open browser DevTools (F12)
- [ ] Check Console tab - should see successful health check API call

### Upload Test
- [ ] Click "Upload Syllabus"
- [ ] Try uploading a test PDF or pasting text
- [ ] Verify extraction works

### Schedule Generation
- [ ] Enter sample assignments
- [ ] Click "Generate Schedule"
- [ ] Verify Gemini creates a schedule

### Export
- [ ] Generate a schedule
- [ ] Try exporting as ICS, Markdown, JSON
- [ ] Verify files download

## 🎯 Post-Deployment

- [ ] Set backend URL in GitHub Pages CNAME file (if using custom domain)
- [ ] Update project documentation with deployed URLs
- [ ] Set up monitoring for backend logs
- [ ] Monitor API usage to avoid hitting Gemini rate limits
- [ ] Share deployed site with users

## 🆘 Troubleshooting

### Frontend won't load
- [ ] Check GitHub Pages URL is correct
- [ ] Check Actions tab for build errors
- [ ] Clear browser cache (Ctrl+Shift+Del)

### API calls fail
- [ ] Check backend is running (visit backend health endpoint)
- [ ] Check `VITE_API_URL` matches backend URL
- [ ] Check browser Console for CORS errors
- [ ] Verify backend has correct GOOGLE_API_KEY

### Backend won't start
- [ ] Check `GOOGLE_API_KEY` is set in environment
- [ ] Check Python version is 3.8+
- [ ] Check all dependencies installed: `pip install -r requirements.txt`

### Cold starts slow (Render)
- [ ] Normal - Render puts free tier apps to sleep
- [ ] Upgrade to paid tier to keep server warm
- [ ] Or use Railway instead

## 📊 Monitoring Commands

### Check backend logs (Railway)
```bash
railway logs
```

### Check backend logs (Render)
```
# Use Render dashboard → Logs
```

### Test API directly
```bash
curl https://your-backend-url.com/health
```

## 🔒 Security Checklist

- [ ] Never commit `.env` file to GitHub
- [ ] Never share API keys in public channels
- [ ] Use strong password for GitHub account
- [ ] Enable 2FA on GitHub
- [ ] Rotate API keys periodically
- [ ] Keep dependencies updated
- [ ] Monitor API logs for suspicious activity

## ✨ Done!

Your AI Scheduler is now live! 🎉

- Frontend: `https://yourusername.github.io/ai-scheduler/`
- Backend: `https://your-backend-url.com`

Share with friends and enjoy scheduling! 📚
