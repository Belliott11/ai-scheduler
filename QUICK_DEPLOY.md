# 🚀 Quick Deployment Guide

Deploy your AI Scheduler to the web in **10 minutes**.

## Step 1: Push Frontend to GitHub (2 min)

```bash
git add .
git commit -m "Deploy to GitHub Pages and Render"
git push origin main
```

✅ **Check**: Go to GitHub **Actions** tab → wait for green checkmark

**Result**: Frontend live at `https://yourusername.github.io/ai-scheduler/`

---

## Step 2: Deploy Backend to Render (5 min)

### Get API Key First
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (you'll need it next)

### Deploy on Render
1. Go to https://render.com
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Select your repository
5. Fill in:
   ```
   Name:              ai-scheduler-backend
   Environment:       Python 3.11
   Root Directory:    backend  ⚠️
   Build Command:     pip install -r requirements.txt
   Start Command:     uvicorn main:app --host 0.0.0.0 --port 8000
   ```
6. Click **"Advanced"** → **"Add Environment Variable"**:
   - Key: `GOOGLE_API_KEY`
   - Value: `<paste your key here>`
   - Add another:
   - Key: `DEBUG`
   - Value: `False`
7. Click **"Create Web Service"**
8. ⏳ Wait ~3 minutes for deployment
9. 📋 Copy your URL from the dashboard (looks like `https://ai-scheduler-backend-xxxxx.onrender.com`)

---

## Step 3: Connect Frontend to Backend (1 min)

Edit `frontend/.env.production`:
```env
VITE_API_URL=https://ai-scheduler-backend-xxxxx.onrender.com
VITE_BASE_PATH=/ai-scheduler/
```

Push to redeploy:
```bash
git add frontend/.env.production
git commit -m "Update backend URL"
git push origin main
```

---

## Step 4: Test It! ✅

1. Visit: `https://yourusername.github.io/ai-scheduler/`
2. Open browser console (F12)
3. Try uploading a test PDF
4. Check **Network** tab to see API calls
5. If it works → 🎉 You're done!

---

## Troubleshooting

### "CORS Error" 
- Make sure Render backend URL is correct in `.env.production`
- Make sure Render deployment finished (check Render dashboard)
- Wait 1 minute after Render deployment completes

### "404 Not Found"
- Check your GitHub username in the URL matches your actual username
- Verify Actions workflow passed (green checkmark)

### "GOOGLE_API_KEY error on backend"
- Make sure you added the env variable in Render dashboard
- Make sure the key is valid (test it: https://makersuite.google.com/app/apikey)

### "Can't upload PDF"
- Check backend is running (visit `/health` endpoint)
- Check Network tab in browser console for error details

---

## That's It!

Your app is now live on the web. Share the URL with friends! 🎓

