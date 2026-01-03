# Railway Deployment Guide

## Quick Start

### 1. Prepare Your Repository

Ensure these files exist:
- ✅ `backend/app.py`
- ✅ `backend/rag.py`
- ✅ `backend/requirements.txt`
- ✅ `Procfile` (or configure in Railway)
- ✅ `.gitignore` (with `.env` listed)

### 2. Set Up Railway

1. **Create Railway Account:**
   - Visit https://railway.app
   - Sign up with GitHub

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variables:**
   - Go to Project → Variables
   - Add these variables:

   ```
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ALLOWED_ORIGINS=https://your-app.railway.app
   ```

   **Important:** Replace with your actual OpenAI API key!

### 3. Configure Build Settings

Railway will auto-detect Python, but you can configure:

**Build Command:**
```bash
cd backend && pip install -r requirements.txt
```

**Start Command:**
```bash
cd backend && python app.py
```

Or use the `Procfile`:
```
web: cd backend && python app.py
```

### 4. Deploy

- Railway will automatically:
  - Detect Python
  - Install dependencies
  - Run your app
  - Provide HTTPS URL

### 5. Frontend Deployment Options

#### Option A: Serve from Railway (Recommended)
1. Add static file serving to FastAPI:
   ```python
   from fastapi.staticfiles import StaticFiles
   app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")
   ```

2. Update `Procfile`:
   ```
   web: cd backend && python app.py
   ```

#### Option B: Deploy Frontend Separately
- Deploy `frontend/index.html` to:
  - Vercel (free)
  - Netlify (free)
  - GitHub Pages (free)
- Update `API_URL` in frontend to your Railway backend URL

#### Option C: Railway Static Files
- Use Railway's static file serving
- Configure build to copy frontend files

## Environment Variables Reference

### Required:
- `OPENAI_API_KEY` - Your OpenAI API key

### Recommended:
- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins for CORS
- `PORT` - Railway sets this automatically (default: 8000)

### Optional:
- `PYTHONUNBUFFERED=1` - For better logging

## Security Checklist

- [x] ✅ `.env` in `.gitignore`
- [x] ✅ No API keys in code
- [x] ✅ Input validation
- [x] ✅ XSS protection
- [x] ✅ Error sanitization
- [ ] ⚠️ Set `OPENAI_API_KEY` in Railway
- [ ] ⚠️ Set `ALLOWED_ORIGINS` in Railway
- [ ] ⚠️ Test HTTPS connection

## Troubleshooting

### App Not Starting:
- Check Railway logs
- Verify `OPENAI_API_KEY` is set
- Check Python version (3.9+)

### CORS Errors:
- Set `ALLOWED_ORIGINS` in Railway
- Include your Railway domain

### API Key Errors:
- Verify key is set in Railway Variables
- Check key is valid
- Ensure no spaces in key value

## Monitoring

Railway provides:
- Real-time logs
- Metrics dashboard
- Deployment history
- Error tracking

## Cost Estimation

- Railway: Free tier available (500 hours/month)
- OpenAI API: Pay per use (check pricing)
- Total: ~$0-20/month for moderate usage

---

**Your app is ready for Railway!** 🚀

