# RAG Retrieval System Refactoring

## Executive Summary

This document explains the refactoring of the RAG retrieval system to clearly distinguish between **Similarity Scores** (from vector search) and **Relevance Scores** (semantic understanding of whether a chunk answers the question).

## Key Concepts

### Similarity vs Relevance

**Similarity Score:**
- Measures semantic similarity in embedding space
- Computed using vector distance (L2 or cosine) between query and chunk embeddings
- Fast to compute (no LLM call needed)
- Indicates: "How similar is this chunk to the query in meaning?"
- Range: 0-100% (normalized from L2 distance)

**Relevance Score:**
- Measures whether a chunk actually answers the question
- Requires semantic understanding (typically needs LLM)
- Slower to compute (requires LLM call per chunk)
- Indicates: "Does this chunk answer the question?"
- Range: 0-100% (confidence that chunk is relevant)

### Why This Distinction Matters

1. **Similarity ≠ Relevance**: A chunk can be semantically similar but not answer the question
   - Example: Query "What is machine learning?" 
   - Chunk about "deep learning" has high similarity but may not directly answer the question

2. **Two-Stage Filtering**:
   - **Stage 1 (Similarity)**: Fast vector search to find semantically similar chunks
   - **Stage 2 (Relevance)**: Optional LLM-based filtering to check if chunks answer the question

3. **Production Readiness**: Clear labeling helps with:
   - Debugging retrieval issues
   - Explaining results to users
   - Auditing and compliance
   - Performance optimization

## Implementation Details

### Backend Changes (`rag.py`)

#### 1. New Helper Functions

**`_normalize_similarity_score(raw_score: float) -> float`**
- Normalizes ChromaDB's L2 distance to 0-1 similarity score
- Handles edge cases (negative scores, very large distances)
- Returns normalized score (0.0 = no similarity, 1.0 = identical)

**`_filter_by_similarity_threshold(results, threshold) -> List`**
- Filters chunks below similarity threshold
- Optional first-stage filtering
- Recommended threshold: 0.3-0.5 (30-50%)

**`_check_relevance_llm(doc_content, question) -> Tuple[bool, float]`**
- Placeholder for future LLM-based relevance checking
- Returns (is_relevant, confidence)
- Currently returns (True, 1.0) - not yet implemented

#### 2. Refactored `answer_question()` Function

**New Parameters:**
- `similarity_threshold: Optional[float]` - Filter chunks below this threshold (0.0-1.0)
- `use_relevance_filter: bool` - Enable LLM-based relevance filtering (future)

**Retrieval Pipeline:**
```
1. SIMILARITY SEARCH
   └─> similarity_search_with_score(question, k=10)
   └─> Returns: List[(doc, raw_score)]

2. SIMILARITY FILTERING (optional)
   └─> Filter chunks where similarity_score < threshold
   └─> Fast, embedding-based filtering

3. RELEVANCE FILTERING (optional, future)
   └─> Use LLM to check if chunks answer the question
   └─> Slower but more accurate

4. CONTEXT BUILDING
   └─> Build context string from filtered chunks
   └─> Generate metadata with similarity scores

5. ANSWER GENERATION
   └─> Use LLM to generate answer from context
```

**Metadata Structure:**
```python
{
    "chunk_id": 1,
    "source": "document.pdf",
    "similarity_score": 85.3,  # Percentage (0-100)
    "page": 5,  # Optional
    "content_preview": "..."  # First 200 chars
}
```

**Technical Info Structure:**
```python
{
    "total_chunks_in_db": 150,
    "chunks_retrieved_initial": 10,
    "chunks_after_similarity_filter": 7,
    "chunks_after_relevance_filter": 7,
    "chunks_used_for_answer": 7,
    "avg_similarity_score": 72.5,  # Percentage
    "max_similarity_score": 89.2,  # Percentage
    "min_similarity_score": 58.1,  # Percentage
    "similarity_threshold_applied": 0.4,  # or None
    "relevance_filter_applied": False,
    "embedding_model": "text-embedding-3-small",
    "similarity_metric": "L2 Distance (normalized to 0-1, displayed as percentage)",
    "retrieval_method": "similarity_search_with_score"
}
```

### Frontend Changes (`index.html`)

#### Updated Field Names
- `meta.score` → `meta.similarity_score` (already a percentage)
- `techInfo.avg_relevance_score` → `techInfo.avg_similarity_score`
- `techInfo.max_relevance_score` → `techInfo.max_similarity_score`
- `techInfo.min_relevance_score` → `techInfo.min_similarity_score`

#### Updated Thresholds
- Old: `score >= 0.8` (80% threshold on 0-1 scale)
- New: `similarity_score >= 80` (80% threshold on 0-100 scale)

#### Updated Labels
- "Relevance Score" → "Similarity Score"
- "Avg Relevance" → "Avg Similarity"
- "Max Relevance" → "Max Similarity"

## Usage Examples

### Basic Usage (No Filtering)
```python
answer, metadata, tech_info = answer_question(vectordb, "What is RAG?")
# Returns all top-10 chunks, no filtering
```

### With Similarity Threshold
```python
answer, metadata, tech_info = answer_question(
    vectordb, 
    "What is RAG?",
    similarity_threshold=0.4  # Filter chunks below 40% similarity
)
# Only chunks with similarity >= 40% are used
```

### Future: With Relevance Filtering
```python
answer, metadata, tech_info = answer_question(
    vectordb, 
    "What is RAG?",
    similarity_threshold=0.4,
    use_relevance_filter=True  # Also filter by LLM-based relevance
)
# Two-stage filtering: similarity + relevance
```

## Code Snippets

### Normalizing Similarity Score
```python
def _normalize_similarity_score(raw_score: float) -> float:
    """
    Normalize raw distance/similarity score from ChromaDB to a 0-1 similarity score.
    
    IMPORTANT: This is a SIMILARITY score (semantic similarity in embedding space),
    NOT a RELEVANCE score (which would require understanding if the chunk answers the question).
    """
    score_float = float(raw_score)
    
    if 0 <= score_float <= 2.0:
        # L2 distance: 0 = identical, 2 = opposite
        normalized_score = 1.0 - (score_float / 2.0)
    elif score_float < 0:
        # Cosine similarity: normalize -1 to 1 → 0 to 1
        normalized_score = (score_float + 1) / 2
    else:
        # Very large distance or already normalized
        normalized_score = max(0.0, min(1.0, score_float))
    
    return normalized_score
```

### Similarity Threshold Filtering
```python
def _filter_by_similarity_threshold(
    results: List[Tuple[Any, float]], 
    threshold: Optional[float] = None
) -> List[Tuple[Any, float]]:
    """
    Filter retrieval results by similarity threshold.
    
    This is the FIRST filtering step (similarity-based).
    A SECOND filtering step (relevance-based) can be added later using LLM.
    """
    if threshold is None:
        return results
    
    filtered = []
    for doc, raw_score in results:
        similarity_score = _normalize_similarity_score(raw_score)
        if similarity_score >= threshold:
            filtered.append((doc, raw_score))
    
    return filtered
```

## Production Recommendations

### Similarity Threshold Selection
- **Conservative (0.5-0.7)**: Higher precision, may miss relevant chunks
- **Balanced (0.3-0.5)**: Good trade-off (recommended)
- **Aggressive (0.0-0.3)**: Higher recall, may include irrelevant chunks

### When to Use Relevance Filtering
- Use when similarity filtering isn't sufficient
- Use when you need high precision (e.g., legal, medical)
- Consider cost: Each relevance check = 1 LLM call per chunk

### Monitoring
- Track `chunks_retrieved_initial` vs `chunks_used_for_answer`
- Monitor `avg_similarity_score` trends
- Alert if similarity scores drop below expected range

## Future Enhancements

1. **LLM-Based Relevance Checking**
   - Implement `_check_relevance_llm()` function
   - Use lightweight model (e.g., gpt-4o-mini) for cost efficiency
   - Batch relevance checks for better performance

2. **Hybrid Retrieval**
   - Combine similarity search with keyword search
   - Use reranking models (e.g., Cohere Rerank)

3. **Adaptive Thresholds**
   - Dynamically adjust similarity threshold based on query type
   - Learn optimal thresholds from user feedback

4. **Relevance Scoring**
   - Add relevance_score field to metadata
   - Display both similarity and relevance scores in UI

## Testing

### Test Cases
1. **High Similarity, Low Relevance**: Query about "Python" returns chunk about "Python snake"
2. **Low Similarity, High Relevance**: Query about "machine learning" returns chunk about "AI algorithms"
3. **Threshold Filtering**: Verify chunks below threshold are filtered
4. **Edge Cases**: Empty results, single chunk, all chunks filtered

### Validation
- Verify similarity scores are in 0-100% range
- Verify metadata structure matches specification
- Verify technical_info includes all required fields
- Verify frontend displays scores correctly

## Migration Notes

### Backward Compatibility
- Old code using `meta.score` will break
- Update frontend to use `meta.similarity_score`
- Update any code reading `techInfo.avg_relevance_score`

### API Changes
- `answer_question()` now accepts optional `similarity_threshold` parameter
- Metadata field renamed: `score` → `similarity_score`
- Technical info fields renamed: `*_relevance_score` → `*_similarity_score`

## Conclusion

This refactoring provides:
- ✅ Clear distinction between similarity and relevance
- ✅ Production-ready filtering pipeline
- ✅ Explainable retrieval process
- ✅ Foundation for future LLM-based relevance checking
- ✅ Better debugging and monitoring capabilities

The system is now more transparent, maintainable, and ready for production deployment.

