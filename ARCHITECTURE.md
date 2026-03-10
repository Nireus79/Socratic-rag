# Architecture Overview

This document describes the architecture and design decisions of Socratic RAG.

## System Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
│  (Your code using Socratic RAG)                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                    Socratic RAG API Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  RAGClient / AsyncRAGClient                                     │
│  ├── add_document()                                             │
│  ├── search()                                                   │
│  ├── retrieve_context()                                         │
│  └── clear()                                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                  Orchestration Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Document Processing  │  Chunking  │  Embedding  │  Vector Ops  │
│  ├── TextProcessor    │  ├── Fixed │  ├── ST    │  ├── Add      │
│  ├── PDFProcessor     │  └── Custom│  └── Custom│  ├── Search   │
│  └── MarkdownProc     │            │            │  └── Delete   │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                  Provider Layer (Pluggable)                      │
├─────────────────────────────────────────────────────────────────┤
│  Embedders              │  Vector Stores      │  Framework       │
│  ├── SentenceTransformers│ ├── ChromaDB        │ ├── Openclaw     │
│  └── Future: OpenAI     │ ├── Qdrant          │ └── LangChain    │
│     Future: Claude      │ └── FAISS           │                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│               External Services Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Vector Databases  │  LLM Services    │  File Systems           │
│  ├── ChromaDB      │  ├── Anthropic   │  ├── Local FS           │
│  ├── Qdrant        │  ├── OpenAI      │  └── S3/Cloud           │
│  └── FAISS         │  └── Others      │                         │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Document Ingestion
   Input Document
        ↓
   [TextProcessor / PDFProcessor / MarkdownProcessor]
        ↓
   Raw Text Content
        ↓

2. Processing Pipeline
   Raw Text
        ↓
   [Chunking: FixedSizeChunker]
        ↓
   Text Chunks
        ↓
   [Embedding: SentenceTransformersEmbedder]
        ↓
   Vector Embeddings
        ↓

3. Storage
   Chunk + Embedding + Metadata
        ↓
   [Vector Store: ChromaDB/Qdrant/FAISS]
        ↓
   Indexed & Searchable
        ↓

4. Retrieval
   User Query
        ↓
   [Embedding: Generate query vector]
        ↓
   Query Vector
        ↓
   [Vector Store: Similarity search]
        ↓
   Top-K Similar Chunks
        ↓

5. Context Formatting
   Search Results
        ↓
   [Format as context string]
        ↓
   LLM-ready Context
        ↓
   [Send to LLM]
```

---

## Provider Pattern

Socratic RAG uses the **Provider Pattern** for extensibility. Each major component has:

1. **Abstract Base Class**: Defines the interface
2. **Default Implementation**: Production-ready implementation
3. **Extensibility**: Easy to add custom implementations

### Vector Store Provider Pattern

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict

class BaseVectorStore(ABC):
    """Abstract base for all vector database providers."""

    @abstractmethod
    def add_documents(
        self,
        documents: List['Document'],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents with embeddings. Returns document IDs."""
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> List['SearchResult']:
        """Search for similar documents."""
        pass

    @abstractmethod
    def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs."""
        pass

    @abstractmethod
    def get(self, document_id: str) -> Optional['Document']:
        """Get document by ID."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all documents."""
        pass
```

**Implementations**:
- `ChromaDBVectorStore`: In-memory and file-based
- `QdrantVectorStore`: Distributed and scalable
- `FAISSVectorStore`: High-performance local search
- Custom implementations following the same interface

### Embedder Provider Pattern

```python
class BaseEmbedder(ABC):
    """Abstract base for embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector dimension."""
        pass
```

**Implementations**:
- `SentenceTransformersEmbedder`: Default, local (384 dims)
- Future: OpenAI embeddings, Claude embeddings, etc.

### Chunker Provider Pattern

```python
class BaseChunker(ABC):
    """Abstract base for chunking strategies."""

    @abstractmethod
    def chunk(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ) -> List['Chunk']:
        """Split text into chunks."""
        pass
```

**Implementations**:
- `FixedSizeChunker`: Character-based chunks with overlap (default)
- Future: Semantic chunking, recursive chunking

### Document Processor Pattern

```python
class BaseDocumentProcessor(ABC):
    """Abstract base for document processors."""

    @abstractmethod
    def process(self, file_path: str) -> str:
        """Extract text from document."""
        pass
```

**Implementations**:
- `TextProcessor`: Plain text files
- `PDFProcessor`: PDF documents
- `MarkdownProcessor`: Markdown files
- Future: DOCX, Excel, HTML, etc.

---

## Module Structure

```
socratic_rag/
├── __init__.py                    # Public API exports
├── models.py                      # Data models & configuration
├── exceptions.py                  # Exception hierarchy
├── client.py                      # Main RAGClient (sync)
├── async_client.py                # AsyncRAGClient (async)
├── llm_rag.py                     # LLM-powered RAG
│
├── embeddings/                    # Embedding providers
│   ├── __init__.py
│   ├── base.py                    # Abstract base class
│   └── sentence_transformers.py   # Default implementation
│
├── chunking/                      # Chunking strategies
│   ├── __init__.py
│   ├── base.py                    # Abstract base class
│   └── fixed_size.py              # Fixed-size chunking
│
├── vector_stores/                 # Vector store providers
│   ├── __init__.py
│   ├── base.py                    # Abstract base class
│   ├── chromadb.py                # ChromaDB provider
│   ├── qdrant.py                  # Qdrant provider
│   └── faiss.py                   # FAISS provider
│
├── processors/                    # Document processors
│   ├── __init__.py
│   ├── base.py                    # Abstract base class
│   ├── text.py                    # Text file processor
│   ├── pdf.py                     # PDF processor
│   └── markdown.py                # Markdown processor
│
├── integrations/                  # Framework integrations
│   ├── openclaw/
│   │   └── skill.py               # Openclaw RAG skill
│   └── langchain/
│       └── retriever.py           # LangChain retriever
│
└── utils/                         # Utilities
    ├── cache.py                   # Embedding cache
    └── text.py                    # Text utilities
```

---

## Data Models

### Document Model

```python
@dataclass
class Document:
    """A document to be indexed."""
    content: str                   # Full document content
    document_id: str               # Unique identifier
    source: str                    # Original source (filename)
    metadata: Dict[str, Any]       # Custom metadata
    created_at: datetime           # Creation timestamp
```

### Chunk Model

```python
@dataclass
class Chunk:
    """A text chunk from a document."""
    text: str                      # Chunk text content
    chunk_id: str                  # Unique chunk ID
    document_id: str               # Parent document ID
    start_char: int                # Position in original
    end_char: int                  # Position in original
    metadata: Dict[str, Any]       # Inherited + custom metadata
```

### SearchResult Model

```python
@dataclass
class SearchResult:
    """A search result with similarity score."""
    chunk: Chunk                   # The found chunk
    score: float                   # Similarity score (0-1)
    document: Optional[Document]   # Full document (optional)
```

### Configuration Model

```python
@dataclass
class RAGConfig:
    """Configuration for RAGClient."""
    vector_store: str = "chromadb"
    embedder: str = "sentence-transformers"
    chunking_strategy: str = "fixed"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5
    embedding_cache: bool = True
    cache_ttl: int = 3600
    collection_name: str = "socratic_rag"
```

---

## Lazy Initialization Pattern

Socratic RAG uses lazy initialization for performance:

```python
class RAGClient:
    def __init__(self, config: RAGConfig):
        self.config = config
        self._vector_store = None      # Not created yet
        self._embedder = None          # Not created yet
        self._chunker = None           # Not created yet

    @property
    def vector_store(self) -> BaseVectorStore:
        """Lazy initialization of vector store."""
        if self._vector_store is None:
            # Create on first use
            self._vector_store = self._create_vector_store()
        return self._vector_store
```

**Benefits**:
- Fast initialization (no unnecessary setup)
- Can change config before first use
- Memory-efficient
- Compatible with async patterns

---

## Error Handling

### Exception Hierarchy

```
SocraticRAGError (Base)
├── ConfigurationError
├── VectorStoreError
│   ├── VectorStoreConnectionError
│   └── VectorStoreOperationError
├── EmbeddingError
├── ChunkingError
├── ProcessorError
├── DocumentNotFoundError
├── ProviderNotFoundError
├── InvalidProviderError
└── AsyncRAGError
```

**Usage**:
```python
from socratic_rag.exceptions import *

try:
    client.search("query")
except VectorStoreError as e:
    print(f"Vector store error: {e}")
except SocraticRAGError as e:
    print(f"General error: {e}")
```

---

## Performance Considerations

### Chunking Strategy

- **Default**: Fixed 512-char chunks with 50-char overlap
- **Trade-offs**:
  - Larger chunks = faster processing but less precise matches
  - Smaller chunks = slower processing but more specific matches
  - Overlap helps preserve context across chunk boundaries

### Embedding Cache

- **Default**: Enabled with 1-hour TTL
- **Purpose**: Avoid re-embedding identical text
- **Trade-off**: Memory usage vs. computation time

### Vector Store Selection

| Store | Pros | Cons |
|-------|------|------|
| **ChromaDB** | Simple, no setup | Single-machine, slower |
| **Qdrant** | Distributed, fast | External service needed |
| **FAISS** | Fastest search | Single-machine, basic |

### Indexing Strategy

- **ChromaDB**: Uses HNSW (Hierarchical NSW graph)
- **Qdrant**: Uses HNSW with metadata filtering
- **FAISS**: Uses LSH (Locality-Sensitive Hashing)

---

## Async Architecture

### AsyncRAGClient

Wraps `RAGClient` with async support using `asyncio.to_thread`:

```python
class AsyncRAGClient:
    def __init__(self, config: RAGConfig):
        self._sync_client = RAGClient(config)

    async def add_document(self, content: str, source: str):
        """Async wrapper around sync method."""
        return await asyncio.to_thread(
            self._sync_client.add_document,
            content,
            source
        )

    async def search(self, query: str, top_k: int = 5):
        """Async wrapper around sync method."""
        return await asyncio.to_thread(
            self._sync_client.search,
            query,
            top_k
        )
```

**Benefits**:
- Non-blocking I/O
- Concurrent request handling
- Perfect for web frameworks (FastAPI, Starlette)
- Thread-safe (GIL-compatible)

---

## Integration Architecture

### LangChain Integration

```
LangChain RetrievalQA
    ↓
SocraticRAGRetriever (implements BaseRetriever)
    ↓
RAGClient.search()
    ↓
Vector Store
    ↓
LangChain Document objects
    ↓
LLM (OpenAI, Anthropic, etc.)
```

### Openclaw Integration

```
Openclaw Workflow
    ↓
SocraticRAGSkill
    ↓
RAGClient
    ↓
Vector Store
    ↓
Workflow Results
```

### Socrates Nexus Integration

```
LLMPoweredRAG
    ├── RAGClient (retrieval)
    └── LLMClient (generation)
    ↓
1. Retrieve relevant context
2. Format with prompt
3. Generate answer with LLM
```

---

## Design Decisions

### Why Provider Pattern?

1. **Flexibility**: Users can choose their components
2. **Extensibility**: Easy to add new providers
3. **Testing**: Easy to mock for unit tests
4. **Maintainability**: Changes to one provider don't affect others

### Why Lazy Initialization?

1. **Performance**: Fast startup, especially for async
2. **Configuration**: Can change settings before first use
3. **Resource Efficiency**: Don't allocate resources unnecessarily
4. **Flexibility**: Works with both sync and async

### Why Async Support?

1. **Modern Python**: Async is standard in web frameworks
2. **Concurrency**: Better resource utilization
3. **Performance**: Non-blocking I/O for web servers
4. **Future-ready**: Prepared for async vector stores

### Why LRU Cache for Embeddings?

1. **Performance**: Avoid re-embedding identical text
2. **Memory**: Bounded cache with TTL prevents unbounded growth
3. **Trade-off**: Small memory overhead for big CPU savings

---

## Future Improvements

### v0.2.0 Architecture Changes

- **Hybrid Search**: Combine vector + keyword search
- **Query Expansion**: Pre-process queries for better matches
- **Re-ranking**: Cross-encoder models for result refinement

### v0.3.0 Architecture Changes

- **Distributed Caching**: Redis backend for scaling
- **Monitoring**: Prometheus metrics export
- **Sharding**: Support for distributed RAG across systems

### v1.0.0 Architecture Vision

- **GraphRAG**: Knowledge graphs for semantic relationships
- **Adaptive Learning**: Learn from user feedback
- **Self-tuning**: Automatic parameter optimization

---

## Testing Architecture

### Test Organization

```
tests/
├── test_models.py             # Data model tests
├── test_embeddings.py         # Embedder provider tests
├── test_chunking.py           # Chunker strategy tests
├── test_vector_stores.py      # Vector store provider tests
├── test_client.py             # RAGClient tests
├── test_async_client.py       # AsyncRAGClient tests
├── test_processors.py         # Document processor tests
├── test_integrations.py       # Integration tests
├── test_llm_rag.py            # LLM integration tests
├── test_edge_cases.py         # Edge case tests
└── benchmarks/
    └── test_performance.py    # Performance benchmarks
```

### Coverage Strategy

- **Unit tests**: Individual components (embedders, chunkers, stores)
- **Integration tests**: Component interactions (client + store + embedder)
- **Edge case tests**: Boundaries, errors, Unicode, large data
- **Performance tests**: Benchmarks for key operations

---

## Deployment Architecture

### Single-Node Deployment

```
Application
    ↓
RAGClient (sync or async)
    ↓
ChromaDB (in-memory or file)
```

### Distributed Deployment

```
Load Balancer
    ↓
[App Instance 1] [App Instance 2] [App Instance 3]
    ↓
Qdrant Cluster (replication + sharding)
```

### Kubernetes Deployment

```
Ingress
    ↓
Service
    ↓
[Pod 1] [Pod 2] [Pod 3] (RAG containers)
    ↓
Qdrant StatefulSet (persistence)
```

See [Deployment Patterns](examples/08_deployment_patterns.py) for examples.

---

**Last Updated**: March 10, 2024
**Version**: 0.1.0
