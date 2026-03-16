# Socratic RAG - Troubleshooting

## Vector Store Issues

### ChromaDB not persisting data

Symptom: Data disappears after restart

Solution: Use explicit persistent storage:
```python
config = RAGConfig(
    vector_store="chromadb",
    persist_directory="./chroma_db"
)
```

### Qdrant connection failed

Symptom: Cannot connect to Qdrant server

Solution: Start Qdrant and verify connection:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

## Embedding Issues

### Embeddings are slow

Cause: Large embedding model

Solution: Use smaller, faster model:
```python
config = RAGConfig(
    embedder="sentence-transformers",
    embedding_model="all-MiniLM-L6-v2"  # Faster
)
```

### Out of memory errors

Cause: Large batch of embeddings

Solution: Batch embeddings:
```python
for chunk in chunks:
    rag.add_document(chunk.text, source)  # One at a time
```

## Search Quality Issues

### Results not relevant

Cause: Chunk size too small/large

Solution: Adjust chunking:
```python
config = RAGConfig(
    chunk_size=1024,      # Larger for dense content
    chunk_overlap=200
)
```

### Too few results

Solution: Increase top_k:
```python
results = rag.search(query, top_k=10)  # Was 5
```

## Performance Issues

### Search is slow

Cause: Large number of documents

Solution:
- Use Qdrant instead of ChromaDB
- Add indexes
- Use FAISS for local efficiency

### Memory usage high

Cause: Too many documents in memory

Solution:
- Use external vector store (Qdrant)
- Reduce chunk size
- Clear old documents
