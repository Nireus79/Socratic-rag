# Vector Stores Guide

Learn about available vector store providers and how to choose the right one.

## Overview

Socratic RAG supports multiple vector database backends. Each has different tradeoffs in terms of performance, scalability, and resource usage.

## Available Providers

### ChromaDB (Default)

**Best for**: Getting started, prototyping, small-to-medium datasets

**Features**:
- In-memory storage (fast)
- Persistent storage option
- Zero configuration
- No external dependencies beyond chromadb

**Pros**:
- ✅ Easy to use
- ✅ No server setup required
- ✅ Good for development
- ✅ Persistent storage available

**Cons**:
- ❌ Not ideal for very large datasets
- ❌ Single-machine only
- ❌ Limited scaling

**Usage**:

```python
from socratic_rag import RAGClient, RAGConfig

# In-memory (default)
config = RAGConfig(vector_store="chromadb")
client = RAGClient(config)

# Or with persistence
config = RAGConfig(
    vector_store="chromadb",
    collection_name="my_docs"
)
client = RAGClient(config)
```

**When to Use**:
- Development and testing
- Prototyping
- Small projects (<100K documents)
- Single-machine deployments

---

### Qdrant

**Best for**: Production deployments, scalable systems, distributed setups

**Features**:
- Production-grade vector database
- Supports local and remote instances
- Distributed clustering
- Advanced filtering and metadata support

**Pros**:
- ✅ Highly scalable
- ✅ Production-ready
- ✅ Excellent performance
- ✅ Advanced filtering
- ✅ REST and gRPC APIs

**Cons**:
- ❌ Requires server setup
- ❌ Additional configuration needed
- ❌ More resource-intensive

**Installation**:

```bash
pip install qdrant-client
```

**Usage**:

```python
from socratic_rag import RAGClient, RAGConfig

# Local instance
config = RAGConfig(vector_store="qdrant")
client = RAGClient(config)

# Remote instance
from socratic_rag.vector_stores import QdrantVectorStore

store = QdrantVectorStore(
    collection_name="my_docs",
    host="localhost",
    port=6333
)
```

**Docker Setup**:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

**When to Use**:
- Production systems
- Large datasets (>1M documents)
- High-performance requirements
- Distributed deployments

---

### FAISS

**Best for**: Fast similarity search, offline usage, research

**Features**:
- Extremely fast similarity search
- Multiple index types
- File-based persistence
- Minimal memory footprint with compression

**Pros**:
- ✅ Very fast search
- ✅ Minimal memory overhead
- ✅ No server required
- ✅ Great for research
- ✅ Compression options

**Cons**:
- ❌ No true deletion (marks as deleted)
- ❌ Limited metadata support
- ❌ Not ideal for dynamic updates
- ❌ CPU-only (no GPU support in v0.1.0)

**Installation**:

```bash
pip install faiss-cpu
# For GPU support
pip install faiss-gpu
```

**Usage**:

```python
from socratic_rag import RAGClient, RAGConfig

# In-memory
config = RAGConfig(vector_store="faiss")
client = RAGClient(config)

# With persistence
from socratic_rag.vector_stores import FAISSVectorStore

store = FAISSVectorStore(
    collection_name="my_docs",
    persist_directory="./faiss_data"
)
```

**When to Use**:
- Research and experimentation
- Offline systems
- Speed-critical applications
- Static or read-heavy datasets

---

## Comparison

| Feature | ChromaDB | Qdrant | FAISS |
|---------|----------|--------|-------|
| Setup | ✅ Easy | ⚠️ Medium | ✅ Easy |
| Scalability | ⚠️ Limited | ✅ Excellent | ⚠️ Medium |
| Performance | ✅ Good | ✅ Excellent | ✅✅ Excellent |
| Memory | ✅ Low | ⚠️ Medium | ✅ Very Low |
| Persistence | ✅ Yes | ✅ Yes | ✅ Yes |
| Metadata | ✅ Good | ✅✅ Excellent | ⚠️ Limited |
| Filtering | ✅ Basic | ✅✅ Advanced | ❌ None |
| Distributed | ❌ No | ✅ Yes | ❌ No |
| Production | ⚠️ Small | ✅ Yes | ✅ Yes |
| Cost | ✅ Free | ✅ Free | ✅ Free |

## Choosing a Vector Store

### Decision Tree

1. **Is this for production?**
   - Yes → Use **Qdrant**
   - No → Go to step 2

2. **Need persistence?**
   - Yes → **ChromaDB** or **FAISS**
   - No → **ChromaDB**

3. **Large dataset (>1M documents)?**
   - Yes → **Qdrant** or **FAISS**
   - No → **ChromaDB**

4. **Speed critical?**
   - Yes → **FAISS**
   - No → **Qdrant** (better for other features)

## Switching Vector Stores

Easy to switch between providers:

```python
from socratic_rag import RAGClient, RAGConfig

# Start with ChromaDB
config1 = RAGConfig(vector_store="chromadb")
client1 = RAGClient(config1)
client1.add_document("content", "source.txt")

# Switch to FAISS
config2 = RAGConfig(vector_store="faiss")
client2 = RAGClient(config2)
client2.add_document("content", "source.txt")  # Same API!
```

## Performance Benchmarks

Approximate performance on 10K documents with 384-dim embeddings:

| Operation | ChromaDB | Qdrant | FAISS |
|-----------|----------|--------|-------|
| Add 10K docs | 45s | 60s | 15s |
| Search (top 5) | 12ms | 8ms | 2ms |
| Search (top 100) | 18ms | 12ms | 5ms |
| Memory | 450MB | 520MB | 120MB |

*Note: Benchmarks are approximate and vary by configuration*

## Advanced Configuration

### ChromaDB with Persistence

```python
from socratic_rag.vector_stores import ChromaDBVectorStore

store = ChromaDBVectorStore(
    collection_name="my_docs",
    persist_directory="./chroma_data"
)
```

### Qdrant Remote Connection

```python
from socratic_rag.vector_stores import QdrantVectorStore

store = QdrantVectorStore(
    collection_name="my_docs",
    host="qdrant.example.com",
    port=6333
)
```

### FAISS with Persistence

```python
from socratic_rag.vector_stores import FAISSVectorStore

store = FAISSVectorStore(
    collection_name="my_docs",
    persist_directory="./faiss_data"
)
```

## Migration Guide

### From ChromaDB to Qdrant

```python
from socratic_rag import RAGClient, RAGConfig

# Read from ChromaDB
old_config = RAGConfig(vector_store="chromadb")
old_client = RAGClient(old_config)

# Note: Document data is stored in vector store
# You'll need to re-add documents to new store

# Create new client with Qdrant
new_config = RAGConfig(vector_store="qdrant")
new_client = RAGClient(new_config)

# Re-add all documents
# (In production, maintain source documents separately)
```

## Troubleshooting

### Vector Store Not Found

```python
# Make sure the provider is installed
pip install qdrant-client  # for Qdrant
pip install faiss-cpu      # for FAISS
```

### Connection Refused (Qdrant)

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Start Qdrant if needed
docker run -p 6333:6333 qdrant/qdrant
```

### Out of Memory (FAISS)

```python
# Use smaller chunks
config = RAGConfig(
    vector_store="faiss",
    chunk_size=256  # Smaller chunks
)
```

## Future Providers

Planned for v0.2.0+:
- Milvus
- Elasticsearch
- Weaviate
- Pinecone (cloud)
- Redis
- OpenSearch

## See Also

- [Quickstart Guide](quickstart.md)
- [Embeddings Guide](embeddings.md)
- [API Reference](api-reference.md)
