# RAG Retrieval Refactoring - Code Snippets

## Key Code Changes

### 1. Similarity Score Normalization

```python
def _normalize_similarity_score(raw_score: float) -> float:
    """
    Normalize raw distance/similarity score from ChromaDB to a 0-1 similarity score.
    
    IMPORTANT: This is a SIMILARITY score (semantic similarity in embedding space),
    NOT a RELEVANCE score (which would require understanding if the chunk answers the question).
    
    ChromaDB with OpenAI embeddings returns L2 distance:
    - Lower values = more similar (0 = identical vectors)
    - Higher values = less similar (~2.0 = opposite vectors)
    """
    score_float = float(raw_score)
    
    if 0 <= score_float <= 2.0:
        # L2 distance: 0 = perfect match, 2 = opposite
        normalized_score = 1.0 - (score_float / 2.0)
    elif score_float < 0:
        # Cosine similarity: normalize -1 to 1 → 0 to 1
        normalized_score = (score_float + 1) / 2
    else:
        # Very large distance or already normalized
        normalized_score = max(0.0, min(1.0, score_float))
    
    return normalized_score
```

**Why Similarity First?**
- Fast: No LLM calls needed, just vector math
- Scalable: Can process thousands of chunks quickly
- Foundation: Filters down to most promising candidates

### 2. Similarity Threshold Filtering

```python
def _filter_by_similarity_threshold(
    results: List[Tuple[Any, float]], 
    threshold: Optional[float] = None
) -> List[Tuple[Any, float]]:
    """
    Filter retrieval results by similarity threshold.
    
    This is the FIRST filtering step (similarity-based).
    A SECOND filtering step (relevance-based) can be added later using LLM.
    
    Why two-stage filtering?
    1. Similarity (fast, embedding-based): "Is this chunk semantically similar?"
    2. Relevance (slower, LLM-based): "Does this chunk answer the question?"
    
    Similarity ≠ Relevance:
    - A chunk can be similar in meaning but not answer the question
    - Example: Query "What is ML?" → Chunk about "deep learning" is similar but may not directly answer
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

**Why Similarity Before Relevance?**
- **Cost**: Similarity filtering is free (vector math), relevance requires LLM calls
- **Speed**: Similarity is milliseconds, relevance is seconds per chunk
- **Efficiency**: Filter out obviously irrelevant chunks first, then check relevance on fewer chunks

### 3. Relevance Checking (Placeholder)

```python
def _check_relevance_llm(doc_content: str, question: str) -> Tuple[bool, float]:
    """
    (OPTIONAL) LLM-based relevance checking.
    
    This is a PLACEHOLDER for future enhancement.
    Similarity scores measure semantic similarity in embedding space,
    but relevance requires understanding if the chunk actually answers the question.
    
    Why Relevance Second?
    - Similarity finds semantically similar chunks (fast, cheap)
    - Relevance verifies chunks actually answer the question (slower, more expensive)
    - Two-stage approach: Filter by similarity first, then verify relevance
    
    Example implementation:
    1. Use LLM to classify: "Does this chunk answer the question?"
    2. Return (is_relevant: bool, relevance_confidence: float)
    """
    # TODO: Implement LLM-based relevance checking
    # This would use a separate LLM call to determine if the chunk is relevant
    # to the question, beyond just semantic similarity.
    return True, 1.0
```

**Why Relevance Second?**
- **Precision**: Similarity can return false positives (similar but not relevant)
- **Accuracy**: LLM can understand context and intent better than embeddings alone
- **Quality**: Final answer quality improves when only relevant chunks are used

### 4. Main Retrieval Function

```python
def answer_question(
    vectordb: Chroma, 
    question: str,
    similarity_threshold: Optional[float] = None,
    use_relevance_filter: bool = False
) -> Tuple[str, List[Dict], Dict]:
    """
    Answer a question using RAG with source citations and similarity scores.
    
    RETRIEVAL PIPELINE:
    1. SIMILARITY SEARCH: Use vector similarity to find semantically similar chunks
       - This uses embedding space distance (L2 or cosine)
       - Returns SIMILARITY scores (how similar in meaning, not if it answers the question)
    
    2. SIMILARITY FILTERING (optional): Filter low-similarity chunks by threshold
       - Removes chunks below similarity_threshold
       - This is a fast, embedding-based filter
    
    3. RELEVANCE FILTERING (optional, future): Use LLM to check if chunks answer the question
       - This would be a slower but more accurate filter
       - Currently not implemented (placeholder exists)
    
    Why This Order?
    - Step 1: Fast vector search finds candidates (milliseconds)
    - Step 2: Fast similarity filtering removes low-quality candidates (milliseconds)
    - Step 3: Slower relevance checking verifies quality (seconds, but on fewer chunks)
    """
    # STEP 1: SIMILARITY SEARCH
    k = 10  # Retrieve more chunks initially (will be filtered if threshold is set)
    results = vectordb.similarity_search_with_score(question, k=k)
    
    # STEP 2: SIMILARITY FILTERING (optional)
    chunks_before_filter = len(results)
    if similarity_threshold is not None:
        results = _filter_by_similarity_threshold(results, similarity_threshold)
    chunks_after_similarity_filter = len(results)
    
    # STEP 3: RELEVANCE FILTERING (optional, future enhancement)
    if use_relevance_filter:
        # TODO: Implement relevance filtering
        pass
    
    # Build context and metadata
    context = ""
    metadata = []
    
    for i, (doc, raw_score) in enumerate(results):
        # Normalize SIMILARITY score (0-1, then convert to percentage)
        # IMPORTANT: This is a SIMILARITY score, not a RELEVANCE score
        similarity_score_normalized = _normalize_similarity_score(raw_score)
        similarity_score_percentage = round(similarity_score_normalized * 100, 1)
        
        # Metadata with clear similarity_score labeling
        meta_item = {
            "chunk_id": i + 1,
            "source": source_filename,
            "similarity_score": similarity_score_percentage  # Percentage (0-100)
        }
        metadata.append(meta_item)
    
    # Generate answer
    answer = llm.invoke(prompt.format(context=context, question=question)).content
    
    return answer, metadata, technical_info
```

### 5. Metadata Structure

```python
# OLD (incorrect terminology)
{
    "chunk_id": 1,
    "source": "document.pdf",
    "score": 0.85  # Unclear: similarity or relevance?
}

# NEW (clear terminology)
{
    "chunk_id": 1,
    "source": "document.pdf",
    "similarity_score": 85.3,  # Percentage (0-100), clearly labeled as similarity
    "page": 5,  # Optional
    "content_preview": "..."  # First 200 chars
}
```

### 6. Technical Info Structure

```python
# OLD (incorrect terminology)
{
    "avg_relevance_score": 0.725,  # Actually similarity, not relevance
    "max_relevance_score": 0.892,
    "min_relevance_score": 0.581
}

# NEW (correct terminology)
{
    "avg_similarity_score": 72.5,  # Percentage, clearly labeled
    "max_similarity_score": 89.2,
    "min_similarity_score": 58.1,
    "similarity_threshold_applied": 0.4,  # or None
    "chunks_retrieved_initial": 10,
    "chunks_after_similarity_filter": 7,
    "chunks_used_for_answer": 7
}
```

## Summary: Similarity vs Relevance

| Aspect | Similarity | Relevance |
|--------|-----------|-----------|
| **What it measures** | Semantic similarity in embedding space | Whether chunk answers the question |
| **Computation** | Vector distance (L2/cosine) | LLM-based classification |
| **Speed** | Milliseconds | Seconds per chunk |
| **Cost** | Free (vector math) | LLM API call per chunk |
| **Use case** | First-stage filtering | Second-stage verification |
| **Range** | 0-100% (normalized) | 0-100% (confidence) |

## Production Recommendations

1. **Start with similarity filtering only** (threshold: 0.3-0.5)
2. **Monitor similarity scores** - if consistently low, adjust threshold
3. **Add relevance filtering** only if similarity filtering isn't sufficient
4. **Use batch processing** for relevance checks to reduce LLM calls

