# RAG Web Application - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Web Browser                                │  │
│  │  • Chrome, Firefox, Safari, Edge                              │  │
│  │  • Mobile & Desktop Support                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              │ HTTPS/HTTP                            │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Frontend Application (index.html)                 │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Presentation Layer                                     │  │  │
│  │  │  • HTML5 Semantic Structure                             │  │  │
│  │  │  • CSS3 Responsive Design                               │  │  │
│  │  │  • Mobile-First Approach                                 │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Application Logic (JavaScript)                          │  │  │
│  │  │  • File Upload Handler                                   │  │  │
│  │  │  • API Communication                                    │  │  │
│  │  │  • UI State Management                                  │  │  │
│  │  │  • Input Validation & Sanitization                      │  │  │
│  │  │  • Error Handling                                        │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ REST API
                              │ (JSON, FormData)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API LAYER                                   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (app.py)                        │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  HTTP Endpoints                                          │  │  │
│  │  │  • POST /upload                                         │  │  │
│  │  │  • POST /ask                                            │  │  │
│  │  │  • GET /health                                          │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Middleware                                            │  │  │
│  │  │  • CORS Handler                                        │  │  │
│  │  │  • Request Validation                                  │  │  │
│  │  │  • Error Handling                                      │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Security Layer                                         │  │  │
│  │  │  • File Validation (type, size)                        │  │  │
│  │  │  • Filename Sanitization                                │  │  │
│  │  │  • Input Length Limits                                  │  │  │
│  │  │  • Session Management                                   │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Function Calls
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                           │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              RAG Engine (rag.py)                             │  │
│  │                                                               │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Document Processing Pipeline                            │  │  │
│  │  │                                                          │  │  │
│  │  │  1. PDF Loading                                          │  │  │
│  │  │     PyPDFLoader → Extract text from PDF                  │  │  │
│  │  │                                                          │  │  │
│  │  │  2. Text Chunking                                        │  │  │
│  │  │     RecursiveCharacterTextSplitter                       │  │  │
│  │  │     • Chunk size: 800 chars                              │  │  │
│  │  │     • Overlap: 200 chars                                 │  │  │
│  │  │                                                          │  │  │
│  │  │  3. Embedding Generation                                 │  │  │
│  │  │     OpenAIEmbeddings (text-embedding-3-small)            │  │  │
│  │  │     • Converts text chunks to vectors                    │  │  │
│  │  │                                                          │  │  │
│  │  │  4. Vector Storage                                       │  │  │
│  │  │     ChromaDB.from_documents()                            │  │  │
│  │  │     • Stores embeddings with metadata                    │  │  │
│  │  │     • Creates session-based vector store                 │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                               │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Question Answering Pipeline                             │  │  │
│  │  │                                                          │  │  │
│  │  │  1. Query Embedding                                     │  │  │
│  │  │     OpenAIEmbeddings → Convert question to vector       │  │  │
│  │  │                                                          │  │  │
│  │  │  2. Similarity Search                                    │  │  │
│  │  │     ChromaDB.similarity_search_with_score()             │  │  │
│  │  │     • Find top 5 relevant chunks                        │  │  │
│  │  │     • Get similarity scores                              │  │  │
│  │  │                                                          │  │  │
│  │  │  3. Score Normalization                                  │  │  │
│  │  │     Convert distance → similarity (0-1)                 │  │  │
│  │  │                                                          │  │  │
│  │  │  4. Context Building                                     │  │  │
│  │  │     Format chunks with source metadata                   │  │  │
│  │  │                                                          │  │  │
│  │  │  5. Answer Generation                                    │  │  │
│  │  │     ChatOpenAI (GPT-4o-mini)                             │  │  │
│  │  │     • Prompt: Context + Question                         │  │  │
│  │  │     • Generate answer with citations                     │  │  │
│  │  │                                                          │  │  │
│  │  │  6. Metadata Extraction                                  │  │  │
│  │  │     Extract: page numbers, sources, scores               │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   ChromaDB   │    │   OpenAI     │    │   OpenAI     │
│              │    │  Embeddings  │    │     LLM      │
│  Vector      │    │   API        │    │    API       │
│  Database    │    │              │    │              │
│              │    │ • text-      │    │ • GPT-4o-    │
│ • Stores     │    │   embedding- │    │   mini       │
│   document   │    │   3-small    │    │              │
│   chunks as  │    │              │    │ • Generates  │
│   vectors    │    │ • 1536      │    │   answers    │
│              │    │   dimensions │    │              │
│ • Fast       │    │              │    │ • With       │
│   similarity │    │ • Semantic   │    │   citations  │
│   search     │    │   search     │    │              │
│              │    │              │    │              │
│ • Session-   │    │              │    │              │
│   based      │    │              │    │              │
│   storage   │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │
        │ File System
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                  │
│                                                                     │
│  ┌──────────────────────┐        ┌──────────────────────┐         │
│  │   uploads/           │        │   vecdb/             │         │
│  │                      │        │                      │         │
│  │  • PDF files         │        │  • Vector stores      │         │
│  │  • Temporary storage │        │  • Session-based      │         │
│  │  • Cleanup on error  │        │  • Persistent         │         │
│  └──────────────────────┘        └──────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

### Upload Flow
```
1. User selects PDF
   ↓
2. Frontend validates (size, type)
   ↓
3. Frontend sends to /upload endpoint
   ↓
4. Backend validates & sanitizes filename
   ↓
5. Backend saves to uploads/
   ↓
6. Backend calls ingest_document()
   ↓
7. RAG Engine:
   - Loads PDF → Extracts text
   - Chunks text (800 chars, 200 overlap)
   - Generates embeddings (OpenAI)
   - Stores in ChromaDB
   ↓
8. Returns session_id
   ↓
9. Frontend displays success, auto-selects session
```

### Query Flow
```
1. User enters question
   ↓
2. Frontend validates (not empty, session selected)
   ↓
3. Frontend sends to /ask endpoint
   ↓
4. Backend validates question (length, content)
   ↓
5. Backend retrieves vector DB for session
   ↓
6. Backend calls answer_question()
   ↓
7. RAG Engine:
   - Embeds question (OpenAI)
   - Searches ChromaDB (similarity_search_with_score)
   - Normalizes scores
   - Builds context with top 5 chunks
   - Sends to LLM (GPT-4o-mini)
   - Extracts metadata
   ↓
8. Returns answer + metadata
   ↓
9. Frontend displays answer with sources & scores
```

## Technology Stack Details

### Frontend
- **HTML5**: Semantic structure, accessibility
- **CSS3**: Modern styling, CSS variables, responsive design
- **Vanilla JavaScript**: No framework dependencies, fast, portable

### Backend
- **FastAPI**: Modern Python web framework
  - Async support
  - Automatic API documentation
  - Type validation with Pydantic
- **Uvicorn**: ASGI server for FastAPI

### RAG Components
- **LangChain**: LLM application framework
  - Document loaders (PyPDFLoader)
  - Text splitters (RecursiveCharacterTextSplitter)
  - Vector stores (ChromaDB integration)
  - LLM integration (OpenAI)
- **ChromaDB**: Vector database
  - Embedded (no separate server)
  - Fast similarity search
  - Persistent storage
- **OpenAI APIs**:
  - Embeddings API (text-embedding-3-small)
  - Chat API (GPT-4o-mini)

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Security Layers                            │
│                                                          │
│  1. Frontend Security                                    │
│     • Input sanitization (XSS prevention)                │
│     • File validation (client-side)                      │
│     • Request timeout handling                           │
│                                                          │
│  2. API Security                                        │
│     • CORS configuration                                 │
│     • File type validation                              │
│     • File size limits (10MB)                           │
│     • Filename sanitization                              │
│     • Input length limits                                │
│                                                          │
│  3. Data Security                                       │
│     • Session isolation                                  │
│     • Error cleanup (no data leakage)                    │
│     • Secure file storage                                │
│                                                          │
│  4. Environment Security                                │
│     • API keys in .env (not in code)                    │
│     • .gitignore for sensitive files                     │
└─────────────────────────────────────────────────────────┘
```

## Deployment Architecture (Railway)

```
┌─────────────────────────────────────────────────────────┐
│                    Railway Platform                     │
│                                                          │
│  ┌──────────────────────────────────────┐          │
│  │  Backend Service                         │          │
│  │  • FastAPI Application                   │          │
│  │  • Port: $PORT (Railway assigned)       │          │
│  │  • Environment: .env variables           │          │
│  │  • Health Check: /health                 │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │  Frontend Service (Optional)             │          │
│  │  • Static file serving                   │          │
│  │  • Or separate service (Vercel/Netlify) │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
│  Environment Variables:                                  │
│  • OPENAI_API_KEY                                        │
│  • PORT                                                  │
│  • ALLOWED_ORIGINS                                       │
└─────────────────────────────────────────────────────────┘
```

## Scalability Considerations

### Current Architecture
- **Sessions in Memory**: Fast but limited by server RAM
- **Single Server**: All requests to one instance
- **No Load Balancing**: Single point of failure

### Future Scalability Options
1. **Database for Sessions**: Move to PostgreSQL/Redis
2. **Load Balancing**: Multiple backend instances
3. **CDN for Frontend**: Faster global access
4. **Caching Layer**: Redis for frequent queries
5. **Queue System**: Background processing for large files

## Performance Optimizations

1. **Chunking Strategy**: 800 chars with 200 overlap balances context vs. retrieval speed
2. **Top-K Retrieval**: Only retrieve top 5 chunks (configurable)
3. **Embedding Caching**: Reuse embeddings for same documents
4. **Lazy Loading**: Load vector DB only when needed
5. **Request Timeouts**: Prevent hanging requests

## Error Handling Strategy

```
┌─────────────────────────────────────────────────────────┐
│              Error Handling Layers                     │
│                                                          │
│  Frontend:                                              │
│  • Try-catch blocks                                     │
│  • User-friendly error messages                        │
│  • Retry mechanisms                                    │
│  • Loading states                                      │
│                                                          │
│  Backend:                                               │
│  • HTTPException with proper status codes              │
│  • Input validation errors (400)                       │
│  • Not found errors (404)                              │
│  • Server errors (500)                                 │
│  • Cleanup on errors                                   │
│                                                          │
│  RAG Engine:                                           │
│  • Exception handling in document processing           │
│  • Fallback mechanisms                                 │
│  • Error logging                                       │
└─────────────────────────────────────────────────────────┘
```

This architecture provides a solid foundation for a production-ready RAG application with clear separation of concerns, security best practices, and scalability considerations.

