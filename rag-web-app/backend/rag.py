import os
import uuid
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate

load_dotenv()

# Security: Verify OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is required. Set it in Railway environment variables.")

# Use environment variables or default to relative paths
UPLOAD_DIR = Path(os.getenv("UPLOADS_DIR", "../uploads"))
VECDB_DIR = Path(os.getenv("VECDB_DIR", "../vecdb"))

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
VECDB_DIR.mkdir(exist_ok=True, parents=True)

# Initialize embeddings with specific model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Initialize prompt template
prompt = PromptTemplate(
    template="""
Answer ONLY using the context below.
Add the source filename (without path) after EACH sentence in [filename] format.
Use only the filename, not the full path.

Context:
{context}

Question:
{question}
""",
    input_variables=["context", "question"]
)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Summary prompt template
summary_prompt = PromptTemplate(
    template="""
Summarize the following web content in a clear and concise manner.
Focus on the main points, key information, and important details.

Content:
{content}

Provide a comprehensive summary:
""",
    input_variables=["content"]
)


def ingest_document(file_path: str) -> Tuple[str, Chroma, Dict]:
    """
    Process PDF and create a session-based vector store.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple of (session_id, vectordb, technical_info)
    """
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    if not docs:
        raise Exception("No text extracted from PDF")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)
    
    # Calculate total characters
    total_chars = sum(len(chunk.page_content) for chunk in chunks)
    avg_chunk_size = total_chars / len(chunks) if chunks else 0

    session_id = str(uuid.uuid4())
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECDB_DIR / session_id)
    )
    
    # Technical information
    technical_info = {
        "num_chunks": len(chunks),
        "chunk_size": 800,
        "chunk_overlap": 200,
        "total_characters": total_chars,
        "avg_chunk_size": round(avg_chunk_size, 2),
        "embedding_model": "text-embedding-3-small",
        "embedding_dimension": 1536,  # OpenAI text-embedding-3-small dimension
        "vector_db": "ChromaDB",
        "source_type": "PDF",
        "source": Path(file_path).name
    }

    return session_id, vectordb, technical_info


def answer_question(vectordb: Chroma, question: str) -> Tuple[str, List[Dict], Dict]:
    """
    Answer a question using RAG with source citations and similarity scores.
    
    Args:
        vectordb: ChromaDB vector store instance
        question: The question to answer
        
    Returns:
        Tuple of (answer, metadata, technical_info)
    """
    # Use similarity_search_with_score to get documents with similarity scores
    results = vectordb.similarity_search_with_score(question, k=5)
    
    # Get total chunks in vector store
    try:
        collection = vectordb._collection
        total_chunks = collection.count()
    except:
        total_chunks = len(results)

    context = ""
    metadata = []

    for i, (doc, score) in enumerate(results):
        source_path = doc.metadata.get('source', 'unknown')
        # Handle both file paths and URLs
        if isinstance(source_path, str) and (source_path.startswith('http://') or source_path.startswith('https://')):
            # It's a URL, extract domain name
            from urllib.parse import urlparse
            try:
                parsed_url = urlparse(source_path)
                source_filename = parsed_url.netloc + (parsed_url.path[:50] if parsed_url.path else '')
            except:
                source_filename = source_path[:60]  # Fallback: truncate URL
        else:
            # It's a file path, extract just the filename
            source_filename = Path(source_path).name if source_path != 'unknown' else 'unknown'
        # Get page number from metadata (if available)
        page = doc.metadata.get('page', None)
        
        # Normalize score: ChromaDB with OpenAI embeddings returns L2 distance scores
        # L2 distance: lower values = better matches (0 = identical, higher = more different)
        # For normalized embeddings, max L2 distance is typically around 2.0
        # We'll convert distance to similarity score (0-1, higher is better)
        score_float = float(score)
        
        # ChromaDB with OpenAI embeddings uses L2 distance on normalized vectors
        # Typical range: 0 (identical) to ~2.0 (opposite)
        # Convert distance to similarity score (0-1, higher is better)
        if 0 <= score_float <= 2.0:
            # L2 distance score (0 = perfect match, 2 = opposite)
            # Convert to similarity: similarity = 1 - (distance / 2)
            # Maps: 0 -> 1.0, 1.0 -> 0.5, 2.0 -> 0.0
            normalized_score = 1.0 - (score_float / 2.0)
        elif score_float < 0:
            # Negative score, might be cosine similarity (-1 to 1)
            # Normalize to 0-1: (score + 1) / 2
            normalized_score = (score_float + 1) / 2
        elif score_float > 2.0:
            # Very large distance, use exponential decay
            normalized_score = max(0.0, 1.0 / (1.0 + (score_float - 2.0)))
        else:
            # Fallback: assume it's already a similarity score (0-1)
            normalized_score = score_float
        
        # Ensure final score is between 0 and 1
        normalized_score = max(0.0, min(1.0, normalized_score))
        
        context += f"Chunk {i+1} ({source_filename}): {doc.page_content}\n\n"
        
        # Normalized metadata format
        meta_item = {
            "chunk_id": i + 1,
            "source": source_filename,
            "score": round(normalized_score, 2)  # Round to 2 decimal places
        }
        
        # Add page if available
        if page is not None:
            meta_item["page"] = int(page)
        
        # Add content preview for reference
        meta_item["content_preview"] = doc.page_content[:200]
        
        metadata.append(meta_item)

    chain_input = prompt.format(context=context, question=question)
    answer = llm.invoke(chain_input).content
    
    # Calculate relevance statistics
    scores = [meta["score"] for meta in metadata]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    # Technical information for RAG query
    technical_info = {
        "total_chunks_in_db": total_chunks,
        "chunks_retrieved": len(results),
        "avg_relevance_score": round(avg_score, 3),
        "max_relevance_score": round(max_score, 3),
        "min_relevance_score": round(min_score, 3),
        "embedding_model": "text-embedding-3-small",
        "embedding_dimension": 1536,
        "vector_db": "ChromaDB",
        "similarity_metric": "L2 Distance (normalized to 0-1)",
        "llm_model": "gpt-4o-mini"
    }

    return answer, metadata, technical_info


def get_session_technical_info(session_id: str) -> Optional[Dict]:
    """
    Get technical information about a session.
    
    Args:
        session_id: The session UUID
        
    Returns:
        Dictionary with technical information or None
    """
    vecdb_path = VECDB_DIR / session_id
    if not vecdb_path.exists():
        return None
    
    try:
        vectordb = Chroma(
            persist_directory=str(vecdb_path),
            embedding_function=embeddings
        )
        
        # Get collection info
        collection = vectordb._collection
        total_chunks = collection.count()
        
        # Try to get sample metadata
        try:
            results = collection.peek(limit=1)
            if results and results.get('metadatas') and len(results['metadatas']) > 0:
                sample_meta = results['metadatas'][0]
                source = sample_meta.get('source', 'unknown')
                source_type = "URL" if (isinstance(source, str) and 
                                        (source.startswith('http://') or source.startswith('https://'))) else "PDF"
            else:
                source_type = "Unknown"
                source = "unknown"
        except:
            source_type = "Unknown"
            source = "unknown"
        
        return {
            "session_id": session_id,
            "num_chunks": total_chunks,
            "embedding_model": "text-embedding-3-small",
            "embedding_dimension": 1536,
            "vector_db": "ChromaDB",
            "source_type": source_type,
            "source": source[:100] if isinstance(source, str) else str(source)[:100]
        }
    except Exception as e:
        print(f"Error getting session info: {e}")
        return None


def load_vectordb(session_id: str) -> Optional[Chroma]:
    """
    Load an existing vector store by session ID.
    
    Args:
        session_id: The session UUID
        
    Returns:
        ChromaDB instance or None if not found
    """
    vecdb_path = VECDB_DIR / session_id
    if not vecdb_path.exists():
        return None
    
    try:
        vectordb = Chroma(
            persist_directory=str(vecdb_path),
            embedding_function=embeddings
        )
        return vectordb
    except Exception as e:
        print(f"Error loading vectordb: {e}")
        return None


def delete_session(session_id: str):
    """
    Delete a session and its vector store.
    
    Args:
        session_id: The session UUID to delete
    """
    vecdb_path = VECDB_DIR / session_id
    if vecdb_path.exists():
        import shutil
        shutil.rmtree(vecdb_path)


def get_all_sessions() -> List[str]:
    """
    Get list of all session IDs.
    
    Returns:
        List of session UUIDs
    """
    if not VECDB_DIR.exists():
        return []
    
    sessions = []
    for path in VECDB_DIR.iterdir():
        if path.is_dir():
            sessions.append(path.name)
    
    return sessions


def ingest_url(url: str) -> Tuple[str, Chroma, str, Dict]:
    """
    Process a web URL, generate summary with citations, and create a session-based vector store.
    
    Args:
        url: Web URL to process
        
    Returns:
        Tuple of (session_id, vectordb, summary, technical_info)
    """
    try:
        # Load web content using LangChain's WebBaseLoader
        loader = WebBaseLoader(url)
        docs = loader.load()
        
        if not docs:
            raise Exception("No content extracted from URL")
        
        # Combine all documents into one text for summary
        full_text = "\n\n".join([doc.page_content for doc in docs])
        
        # Generate summary with source citation
        summary_with_citation_prompt = PromptTemplate(
            template="""
Summarize the following web content in a clear and concise manner.
Focus on the main points, key information, and important details.
Include source citations in the format [Source: {url}] at the end of each major point.

Content:
{content}

Provide a comprehensive summary with source citations:
""",
            input_variables=["content", "url"]
        )
        
        summary_input = summary_with_citation_prompt.format(content=full_text[:8000], url=url)
        summary = llm.invoke(summary_input).content
        
        # Split documents into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(docs)
        
        # Add URL as source metadata to each chunk
        for chunk in chunks:
            if 'source' not in chunk.metadata:
                chunk.metadata['source'] = url
            chunk.metadata['url'] = url
        
        # Calculate total characters
        total_chars = sum(len(chunk.page_content) for chunk in chunks)
        avg_chunk_size = total_chars / len(chunks) if chunks else 0
        
        # Create vector store
        session_id = str(uuid.uuid4())
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(VECDB_DIR / session_id)
        )
        
        # Technical information
        technical_info = {
            "num_chunks": len(chunks),
            "chunk_size": 800,
            "chunk_overlap": 200,
            "total_characters": total_chars,
            "avg_chunk_size": round(avg_chunk_size, 2),
            "embedding_model": "text-embedding-3-small",
            "embedding_dimension": 1536,
            "vector_db": "ChromaDB",
            "source_type": "URL",
            "source": url
        }
        
        return session_id, vectordb, summary, technical_info
        
    except Exception as e:
        raise Exception(f"Error processing URL: {str(e)}")
