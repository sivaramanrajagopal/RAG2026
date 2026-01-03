# Deployment Next Steps - Railway

## ✅ Current Status
- ✅ Backend built successfully
- ✅ Backend deployed to Railway
- ✅ Service is running

## 🚀 Next Steps

### 1. Generate Public Domain (REQUIRED)

1. In Railway dashboard, go to your service
2. Click on **"Networking"** tab
3. Under **"Public Networking"**, click **"Generate Domain"**
4. Railway will create a public URL like: `https://rag2026-production.up.railway.app`
5. **Copy this URL** - you'll need it!

### 2. Set Environment Variables (REQUIRED)

1. Go to your Railway service
2. Click on **"Variables"** tab
3. Add these environment variables:

```
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
ALLOWED_ORIGINS=https://your-generated-domain.railway.app
```

**Important:**
- Replace `your-actual-openai-key-here` with your real OpenAI API key
- Replace `your-generated-domain.railway.app` with your actual Railway domain

### 3. Deploy Frontend

You have **3 options**:

#### Option A: Serve Frontend from Railway (Recommended)

Add static file serving to your FastAPI backend:

1. Update `backend/app.py` to serve static files:

```python
from fastapi.staticfiles import StaticFiles

# Add this before the last line (if __name__ == "__main__")
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")
```

2. Commit and push:
```bash
git add backend/app.py
git commit -m "Add static file serving for frontend"
git push origin main
```

3. Railway will auto-deploy
4. Access your app at: `https://your-domain.railway.app`

#### Option B: Deploy Frontend to Vercel/Netlify (Free)

1. Go to [Vercel](https://vercel.com) or [Netlify](https://netlify.com)
2. Create new project
3. Connect your GitHub repo
4. Set root directory to: `rag-web-app/frontend`
5. Update `API_URL` in `frontend/index.html` to your Railway backend URL
6. Deploy

#### Option C: Use Railway Static Service

1. Create a new service in Railway
2. Choose "Static Files"
3. Set root to `rag-web-app/frontend`
4. Deploy

### 4. Test Your Deployment

1. **Test Backend:**
   - Visit: `https://your-domain.railway.app/health`
   - Should return: `{"status":"healthy","service":"RAG API"}`

2. **Test Frontend:**
   - Visit: `https://your-domain.railway.app` (if using Option A)
   - Or your Vercel/Netlify URL (if using Option B/C)

3. **Test Full Flow:**
   - Upload a PDF
   - Process a URL
   - Ask a question
   - Check voice features

### 5. Update CORS (If Using Separate Frontend)

If frontend is on a different domain (Vercel/Netlify):

1. Go to Railway → Variables
2. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-domain.railway.app
   ```
3. Redeploy

## 🔧 Troubleshooting

### Backend Not Starting
- Check Railway logs
- Verify `OPENAI_API_KEY` is set
- Check if venv was created correctly

### CORS Errors
- Set `ALLOWED_ORIGINS` in Railway variables
- Include your frontend domain
- Restart service

### Module Not Found Errors
- Verify venv is being used in start command
- Check build logs for dependency installation

### 404 Errors
- Verify domain is generated
- Check service is running
- Verify routes are correct

## 📝 Quick Checklist

- [ ] Generate public domain in Railway
- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Set `ALLOWED_ORIGINS` environment variable
- [ ] Choose frontend deployment option
- [ ] Test backend health endpoint
- [ ] Test frontend access
- [ ] Test full application flow
- [ ] Verify voice features work (requires HTTPS)

## 🎉 You're Done!

Once all steps are complete, your RAG application will be:
- ✅ Publicly accessible
- ✅ Secure (API keys in env vars)
- ✅ Fully functional
- ✅ Ready for users!

---

**Need Help?** Check Railway logs or the troubleshooting section above.

