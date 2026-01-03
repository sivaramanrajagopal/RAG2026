import os
import re
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from rag import ingest_document, answer_question, ingest_url, get_session_technical_info

load_dotenv()

# Create uploads directory (relative to backend or absolute)
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "../uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

app = FastAPI(
    title="RAG Web App API",
    description="RAG API for document processing and question answering",
    version="1.0.0"
)

# CORS middleware - Railway compatible
# Security: Restrict CORS in production
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    # In production, default to empty (same-origin only)
    # For Railway, set ALLOWED_ORIGINS environment variable
    allowed_origins = ["*"]  # Only for development - set ALLOWED_ORIGINS in Railway

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

sessions = {}


class QuestionRequest(BaseModel):
    session_id: str
    question: str


class URLRequest(BaseModel):
    url: str


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Security: Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Security: Sanitize filename
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
    if not safe_filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Security: File size limit (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE / (1024*1024)}MB limit")
    
    file_path = os.path.join(UPLOADS_DIR, safe_filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)

        session_id, vectordb, technical_info = ingest_document(file_path)
        sessions[session_id] = vectordb

        return {
            "session_id": session_id,
            "technical_info": technical_info
        }
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        # Security: Don't expose internal error details
        error_msg = str(e)
        if "OPENAI_API_KEY" in error_msg.upper() or "API" in error_msg.upper():
            raise HTTPException(status_code=500, detail="Error processing file. Please try again.")
        raise HTTPException(status_code=500, detail=f"Error processing file: {error_msg}")


@app.post("/ask")
async def ask(req: QuestionRequest):
    # Security: Validate input
    if not req.session_id or not req.session_id.strip():
        raise HTTPException(status_code=400, detail="Session ID is required")
    
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
    
    # Security: Limit question length
    if len(req.question) > 1000:
        raise HTTPException(status_code=400, detail="Question too long (max 1000 characters)")
    
    vectordb = sessions.get(req.session_id)
    if not vectordb:
        raise HTTPException(status_code=404, detail="Invalid session")
    
    try:
        answer, metadata, technical_info = answer_question(vectordb, req.question)
        return {
            "answer": answer,
            "metadata": metadata,
            "technical_info": technical_info
        }
    except Exception as e:
        # Security: Don't expose internal error details
        error_msg = str(e)
        if "OPENAI_API_KEY" in error_msg.upper() or "API" in error_msg.upper():
            raise HTTPException(status_code=500, detail="Error processing question. Please try again.")
        raise HTTPException(status_code=500, detail=f"Error processing question: {error_msg}")


@app.post("/process-url")
async def process_url(req: URLRequest):
    """
    Process a web URL, generate summary, and create a session for RAG queries.
    """
    import re
    from urllib.parse import urlparse
    
    # Security: Validate URL
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    
    url = req.url.strip()
    
    # Security: Validate URL format
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    
    # Security: Validate URL structure
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Security: Block local/private IPs (optional but recommended)
    blocked_domains = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.', '10.', '172.']
    if any(blocked in url.lower() for blocked in blocked_domains):
        raise HTTPException(status_code=400, detail="Local/private URLs are not allowed")
    
    # Security: URL length limit
    if len(url) > 2048:
        raise HTTPException(status_code=400, detail="URL too long (max 2048 characters)")
    
    try:
        session_id, vectordb, summary, technical_info = ingest_url(url)
        sessions[session_id] = vectordb
        
        return {
            "session_id": session_id,
            "summary": summary,
            "url": url,
            "technical_info": technical_info
        }
    except Exception as e:
        error_msg = str(e)
        # Provide user-friendly error messages
        if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            raise HTTPException(status_code=408, detail="Unable to connect to URL. Please check if the URL is accessible.")
        elif "404" in error_msg or "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail="URL not found. Please check the URL.")
        else:
            raise HTTPException(status_code=500, detail=f"Error processing URL: {error_msg}")


@app.get("/session/{session_id}/technical")
async def get_technical_info(session_id: str):
    """Get technical information about a session"""
    technical_info = get_session_technical_info(session_id)
    if not technical_info:
        raise HTTPException(status_code=404, detail="Session not found")
    return technical_info


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "service": "RAG API"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
