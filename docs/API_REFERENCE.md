# Socratic RAG - API Reference

## RAGClient

### Constructor
```python
RAGClient(config=None)
```

### Methods

#### add_document(content, source, metadata=None) -> str
Add document and return document ID.

#### search(query, top_k=5, filters=None) -> List[SearchResult]
Search for relevant documents.

#### retrieve_context(query, top_k=5) -> str
Get formatted context string for LLM.

#### clear() -> bool
Clear all documents.

## AsyncRAGClient

Async version of RAGClient with same methods but async.

```python
doc_id = await rag.add_document(content, source)
results = await rag.search(query)
```

## RAGConfig

```python
RAGConfig(
    vector_store="chromadb",
    embedder="sentence-transformers",
    chunking_strategy="fixed",
    chunk_size=512,
    chunk_overlap=50,
    top_k=5,
    collection_name="socratic_rag"
)
```

## SearchResult

```python
@dataclass
class SearchResult:
    chunk: Chunk
    score: float
    metadata: Dict[str, Any]
```

## Document

```python
@dataclass
class Document:
    doc_id: str
    content: str
    source: str
    metadata: Dict[str, Any]
```

## Chunk

```python
@dataclass
class Chunk:
    chunk_id: str
    text: str
    start_position: int
    end_position: int
    doc_id: str
```
