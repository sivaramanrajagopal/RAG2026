# Railway Build Fix Guide

## Issue
Railway is not detecting Python correctly because the app is in a subdirectory.

## Solution Options

### Option 1: Set Root Directory in Railway (RECOMMENDED)

1. Go to your Railway project
2. Click on your service
3. Go to **Settings** → **Source**
4. Set **Root Directory** to: `rag-web-app`
5. Railway will then look for files in that directory
6. Update `Procfile` in `rag-web-app/` to: `web: cd backend && python3 app.py`

### Option 2: Use Railway's Auto-Detection

Railway should auto-detect Python if you have:
- `requirements.txt` in the root (we have this)
- `runtime.txt` in the root (we have this)
- `Procfile` in the root (we have this)

But since files are in subdirectory, use Option 1 is better.

### Option 3: Move Files to Root (Alternative)

If Options 1-2 don't work, you can restructure:
- Move `backend/` to root
- Move `frontend/` to root
- Update all paths accordingly

## Current Configuration

- `nixpacks.toml` - Nixpacks build config
- `railway.json` - Railway deployment config
- `Procfile` - Process file pointing to subdirectory
- `requirements.txt` - Python detection helper
- `runtime.txt` - Python version

## Environment Variables to Set in Railway

```
OPENAI_API_KEY=your_key_here
ALLOWED_ORIGINS=https://your-app.railway.app
```

## Build Command (if setting manually)

```bash
cd rag-web-app/backend && pip install -r requirements.txt
```

## Start Command (if setting manually)

```bash
cd rag-web-app/backend && python3 app.py
```

