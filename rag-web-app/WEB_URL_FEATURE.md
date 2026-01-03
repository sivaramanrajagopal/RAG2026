# Web URL Processing Feature

## Overview

The RAG application now supports processing web URLs in addition to PDF files. The system automatically:
1. Fetches web content using LangChain's WebBaseLoader
2. Generates an AI-powered summary
3. Creates a vector store for RAG queries
4. Allows asking questions about the web content

## Features

### ✅ URL Processing
- **Input**: Paste or type any web URL (http:// or https://)
- **Processing**: Automatically scrapes and extracts content
- **Summary**: AI-generated comprehensive summary
- **RAG**: Full RAG support for question answering

### ✅ Security Features
- URL format validation
- Protocol validation (only http/https)
- Local/private IP blocking
- URL length limits (2048 characters)
- Error handling for inaccessible URLs

### ✅ User Experience
- Real-time status updates
- Summary display with source link
- Automatic session creation
- Seamless integration with existing PDF workflow

## How to Use

### 1. Process a Web URL
1. Navigate to the "Upload Documents" section
2. Find the "Process Web URL" section
3. Paste or type a URL (e.g., `https://example.com/article`)
4. Click "📎 Process URL & Generate Summary"
5. Wait for processing (scraping + summary generation)
6. View the generated summary

### 2. Ask Questions
1. After processing, the session is automatically selected
2. Go to "Ask Questions" section
3. Type or use voice search to ask questions
4. Get answers based on the web content
5. View source citations with similarity scores

## Technical Implementation

### Backend (`rag.py`)

#### New Function: `ingest_url(url: str)`
```python
def ingest_url(url: str) -> Tuple[str, Chroma, str]:
    """
    Process a web URL, generate summary, and create a session-based vector store.
    
    Returns:
        Tuple of (session_id, vectordb, summary)
    """
```

**Process:**
1. Uses `WebBaseLoader` from LangChain to fetch content
2. Extracts text from HTML
3. Generates summary using GPT-4o-mini
4. Splits content into chunks (800 chars, 200 overlap)
5. Creates ChromaDB vector store
6. Returns session ID, vector store, and summary

#### Summary Generation
- Uses dedicated prompt template
- Focuses on main points and key information
- Comprehensive and concise summaries
- Token-efficient (limits content to 8000 chars for summary)

### Backend (`app.py`)

#### New Endpoint: `/process-url`
```python
POST /process-url
Body: {"url": "https://example.com"}
Response: {
    "session_id": "uuid",
    "summary": "AI-generated summary...",
    "url": "https://example.com"
}
```

**Security Checks:**
- URL format validation
- Protocol validation
- Local IP blocking
- Length limits
- Error handling

### Frontend (`index.html`)

#### New UI Elements
- URL input field
- Process URL button
- Summary display area
- Status messages

#### JavaScript Functions
- `validateURL()`: Validates URL format
- URL processing handler with error handling
- Summary display with source link
- Automatic session selection

## Dependencies Added

```txt
beautifulsoup4==4.12.2  # HTML parsing
requests==2.31.0         # HTTP requests
lxml==4.9.3              # XML/HTML parser
```

## Example Workflow

1. **User pastes URL**: `https://www.example.com/article`
2. **Backend processes**:
   - Fetches HTML content
   - Extracts text
   - Generates summary: "This article discusses..."
   - Creates vector embeddings
   - Stores in ChromaDB
3. **Frontend displays**:
   - Summary in formatted box
   - Source URL as clickable link
   - Success message with session ID
4. **User asks question**: "What are the main points?"
5. **RAG system**:
   - Searches vector store
   - Finds relevant chunks
   - Generates answer with citations
   - Returns answer with similarity scores

## Supported Content Types

- ✅ News articles
- ✅ Blog posts
- ✅ Documentation pages
- ✅ Wikipedia articles
- ✅ Product pages
- ✅ Any HTML-based content

## Limitations

- ⚠️ Requires accessible URLs (no authentication)
- ⚠️ JavaScript-rendered content may not be fully captured
- ⚠️ Large pages may be truncated
- ⚠️ Rate limiting may apply to frequent requests

## Error Handling

The system handles:
- Invalid URLs → Clear error message
- Inaccessible URLs → Connection error message
- 404 Not Found → Specific error message
- Timeout errors → User-friendly timeout message
- Processing errors → Detailed error information

## Integration with Existing Features

- ✅ Works alongside PDF uploads
- ✅ Same RAG query interface
- ✅ Same voice search support
- ✅ Same voice readout feature
- ✅ Same session management
- ✅ Same source citation format

## Future Enhancements

- [ ] Support for multiple URLs in one session
- [ ] URL batch processing
- [ ] Custom summary length options
- [ ] Content filtering (remove ads, navigation)
- [ ] Support for authenticated URLs
- [ ] JavaScript rendering support
- [ ] PDF export of summaries
- [ ] URL history tracking

---

**Status**: ✅ **FULLY IMPLEMENTED AND READY TO USE**

