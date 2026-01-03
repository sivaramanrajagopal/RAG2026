# Quick Start Guide

## Application Status

✅ **Backend Server**: Running on `http://localhost:8000`
✅ **Frontend Server**: Running on `http://localhost:3000`

## Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## How to Use

1. **Upload a PDF**:
   - Click the upload area or drag & drop a PDF file
   - Wait for processing (creates embeddings)
   - Session ID will be automatically selected

2. **Ask Questions**:
   - Select a session from the dropdown
   - Type your question
   - Click "Ask Question" or press Enter
   - View answer with source citations and similarity scores

## API Endpoints

- `GET http://localhost:8000/health` - Health check
- `POST http://localhost:8000/upload` - Upload PDF
- `POST http://localhost:8000/ask` - Ask question

## Stop Servers

To stop the servers, press `Ctrl+C` in the terminal or run:
```bash
lsof -ti:8000 | xargs kill  # Stop backend
lsof -ti:3000 | xargs kill  # Stop frontend
```

