# RAG Web Application

A production-ready Retrieval-Augmented Generation (RAG) web application for uploading PDFs and asking questions using AI.

## Features

- 📄 PDF document upload and processing
- 🔍 Semantic search with similarity scores
- 💬 AI-powered question answering
- 📊 Audit-ready metadata with source citations
- 🔒 Security-first design
- 📱 Mobile-responsive interface
- ♿ Accessibility compliant

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Vector DB**: ChromaDB
- **Embeddings**: OpenAI text-embedding-3-small
- **LLM**: OpenAI GPT-4o-mini
- **Hosting**: Railway-ready

## Security Features

- ✅ XSS protection (input sanitization)
- ✅ File size validation (10MB limit)
- ✅ Filename sanitization
- ✅ Input length validation
- ✅ CORS configuration
- ✅ Request timeout handling
- ✅ Error handling and cleanup

## Deployment to Railway

### Prerequisites

1. Railway account
2. OpenAI API key

### Steps

1. **Create a new Railway project**
   - Connect your GitHub repository or deploy directly

2. **Set Environment Variables**
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PORT=8000
   ALLOWED_ORIGINS=*
   ```

3. **Deploy Backend**
   - Railway will automatically detect Python and install dependencies
   - The `Procfile` specifies the start command

4. **Deploy Frontend**
   - Option 1: Serve static files from Railway
   - Option 2: Use a separate service (Vercel, Netlify, etc.)
   - Update `API_URL` in `frontend/index.html` to your Railway backend URL

5. **Configure CORS** (if needed)
   - Update `ALLOWED_ORIGINS` in Railway environment variables
   - Format: `https://your-frontend-domain.com,https://another-domain.com`

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on `http://localhost:8000`

### Frontend

```bash
cd frontend
python -m http.server 3000
```

Frontend runs on `http://localhost:3000`

## API Endpoints

- `POST /upload` - Upload and process a PDF file
- `POST /ask` - Ask a question about uploaded documents
- `GET /health` - Health check endpoint

## File Structure

```
rag-web-app/
├── backend/
│   ├── app.py          # FastAPI application
│   ├── rag.py         # RAG logic
│   └── requirements.txt
├── frontend/
│   └── index.html     # Production-ready UI
├── uploads/           # Uploaded PDFs
├── vecdb/             # Vector database storage
├── Procfile           # Railway deployment config
└── README.md
```

## Environment Variables

- `OPENAI_API_KEY` - Required: Your OpenAI API key
- `PORT` - Optional: Server port (default: 8000)
- `ALLOWED_ORIGINS` - Optional: Comma-separated list of allowed origins (default: *)

## Production Checklist

- ✅ Security vulnerabilities fixed
- ✅ Mobile-responsive design
- ✅ Accessibility features (ARIA labels, keyboard navigation)
- ✅ Error handling and validation
- ✅ Loading states and user feedback
- ✅ Railway deployment ready
- ✅ Environment-based configuration
- ✅ Request timeout handling
- ✅ File size limits
- ✅ Input sanitization

## License

MIT

