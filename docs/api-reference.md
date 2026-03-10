# API Reference

Complete API documentation for Socratic RAG.

## Table of Contents

- [RAGClient](#ragclient)
- [AsyncRAGClient](#asyncragclient)
- [LLMPoweredRAG](#llmpoweredrag)
- [Data Models](#data-models)
- [Vector Stores](#vector-stores)
- [Embedders](#embedders)
- [Chunkers](#chunkers)
- [Processors](#processors)
- [Integrations](#integrations)
- [Exceptions](#exceptions)

---

## RAGClient

Main synchronous client for RAG operations.

### Constructor

```python
RAGClient(config: Optional[RAGConfig] = None) -> RAGClient
```

**Parameters**:
- `config` (RAGConfig, optional): Configuration object. Uses defaults if not provided.

**Example**:
```python
from socratic_rag import RAGClient, RAGConfig

config = RAGConfig(vector_store="chromadb", chunk_size=512)
client = RAGClient(config)
```

### Methods

#### add_document

```python
add_document(
    content: str,
    source: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str
```

Add a document to the knowledge base.

**Parameters**:
- `content` (str): Document content
- `source` (str): Document source identifier
- `metadata` (dict, optional): Additional metadata

**Returns**: Document ID (str)

**Example**:
```python
doc_id = client.add_document(
    content="Python is great",
    source="python.txt",
    metadata={"topic": "programming"}
)
```

#### search

```python
search(
    query: str,
    top_k: Optional[int] = None,
    filters: Optional[Dict[str, Any]] = None
) -> List[SearchResult]
```

Search for relevant documents.

**Parameters**:
- `query` (str): Search query
- `top_k` (int, optional): Number of results. Uses config default if not provided.
- `filters` (dict, optional): Metadata filters (vector-store specific)

**Returns**: List of SearchResult objects

**Example**:
```python
results = client.search("Python programming", top_k=5)
for result in results:
    print(f"Score: {result.score}, Text: {result.chunk.text}")
```

#### retrieve_context

```python
retrieve_context(
    query: str,
    top_k: Optional[int] = None
) -> str
```

Retrieve formatted context for LLM input.

**Parameters**:
- `query` (str): Search query
- `top_k` (int, optional): Number of results

**Returns**: Formatted context string

**Example**:
```python
context = client.retrieve_context("Python programming")
print(context)
# Output:
# [1] Python is great
#
# [2] Python is powerful
```

#### clear

```python
clear() -> bool
```

Clear all documents from knowledge base.

**Returns**: True if successful

**Example**:
```python
success = client.clear()
```

### Properties

#### vector_store

```python
@property
vector_store() -> BaseVectorStore
```

Get the vector store instance (lazy initialized).

#### embedder

```python
@property
embedder() -> BaseEmbedder
```

Get the embedder instance (lazy initialized).

#### chunker

```python
@property
chunker() -> BaseChunker
```

Get the chunker instance (lazy initialized).

#### config

```python
@property
config() -> RAGConfig
```

Get the configuration object.

---

## AsyncRAGClient

Async version of RAGClient with the same methods but async/await interface.

### Constructor

```python
AsyncRAGClient(config: Optional[RAGConfig] = None) -> AsyncRAGClient
```

### Methods

All methods are async versions of RAGClient methods:

```python
async def add_document(...) -> str
async def search(...) -> List[SearchResult]
async def retrieve_context(...) -> str
async def clear() -> bool
```

**Example**:
```python
import asyncio
from socratic_rag import AsyncRAGClient

async def main():
    client = AsyncRAGClient()
    doc_id = await client.add_document("content", "source.txt")
    results = await client.search("query")
    context = await client.retrieve_context("query")
    await client.clear()

asyncio.run(main())
```

---

## LLMPoweredRAG

RAG with LLM-powered answer generation.

### Constructor

```python
LLMPoweredRAG(
    rag_client: RAGClient,
    llm_client: Optional[Any] = None
) -> LLMPoweredRAG
```

**Parameters**:
- `rag_client` (RAGClient): RAG client instance
- `llm_client` (optional): LLM client (Socrates Nexus LLMClient or similar)

### Methods

#### generate_answer

```python
generate_answer(
    query: str,
    top_k: Optional[int] = None,
    context_prefix: str = "Context:\n",
    context_separator: str = "\n\n",
    system_prompt: Optional[str] = None,
    **llm_kwargs: Any
) -> str
```

Generate answer using RAG + LLM.

**Parameters**:
- `query` (str): Question to answer
- `top_k` (int, optional): Number of context documents
- `context_prefix` (str): Prefix for context section
- `context_separator` (str): Separator between documents
- `system_prompt` (str, optional): Custom system prompt
- `**llm_kwargs`: Additional arguments for LLM

**Returns**: Generated answer (str)

**Example**:
```python
from socratic_rag import LLMPoweredRAG
from socrates_nexus import LLMClient

rag = RAGClient()
rag.add_document("Python is great", "python.txt")

llm = LLMClient(provider="anthropic", model="claude-sonnet")
llm_rag = LLMPoweredRAG(rag, llm)

answer = llm_rag.generate_answer(
    "What is Python?",
    system_prompt="You are a Python expert"
)
```

#### retrieve_context

```python
retrieve_context(query: str, top_k: Optional[int] = None) -> str
```

Same as RAGClient.retrieve_context()

#### search

```python
search(
    query: str,
    top_k: Optional[int] = None,
    filters: Optional[Dict[str, Any]] = None
) -> List[SearchResult]
```

Same as RAGClient.search()

#### add_document

```python
add_document(
    content: str,
    source: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str
```

Same as RAGClient.add_document()

#### clear

```python
clear() -> bool
```

Same as RAGClient.clear()

---

## Data Models

### Document

```python
@dataclass
class Document:
    content: str
    document_id: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document
```

Represents a document in the knowledge base.

### Chunk

```python
@dataclass
class Chunk:
    text: str
    chunk_id: str
    document_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_char: int = 0
    end_char: int = 0

    @classmethod
    def create(
        cls,
        text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        start_char: int = 0,
        end_char: int = 0
    ) -> Chunk
```

Represents a text chunk extracted from a document.

### SearchResult

```python
@dataclass
class SearchResult:
    chunk: Chunk
    score: float
    document: Optional[Document] = None
```

Represents a search result with relevance score.

### RAGConfig

```python
@dataclass
class RAGConfig:
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

Configuration for RAG client.

---

## Vector Stores

### BaseVectorStore

Abstract base class for vector stores.

```python
class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]]
    ) -> List[str]: ...

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]: ...

    @abstractmethod
    def delete(self, document_ids: List[str]) -> bool: ...

    @abstractmethod
    def get(self, document_id: str) -> Optional[Chunk]: ...

    @abstractmethod
    def clear(self) -> bool: ...
```

### ChromaDBVectorStore

```python
ChromaDBVectorStore(
    collection_name: str = "socratic_rag",
    persist_directory: Optional[str] = None
)
```

### QdrantVectorStore

```python
QdrantVectorStore(
    collection_name: str = "socratic_rag",
    host: str = "localhost",
    port: int = 6333,
    memory_mode: bool = True,
    path: Optional[str] = None
)
```

### FAISSVectorStore

```python
FAISSVectorStore(
    collection_name: str = "socratic_rag",
    persist_directory: Optional[str] = None
)
```

---

## Embedders

### BaseEmbedder

```python
class BaseEmbedder(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]: ...

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]: ...

    @property
    @abstractmethod
    def dimension(self) -> int: ...
```

### SentenceTransformersEmbedder

```python
SentenceTransformersEmbedder(
    model_name: str = "all-MiniLM-L6-v2"
)
```

---

## Chunkers

### BaseChunker

```python
class BaseChunker(ABC):
    @abstractmethod
    def chunk(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]: ...
```

### FixedSizeChunker

```python
FixedSizeChunker(
    chunk_size: int = 512,
    overlap: int = 50
)
```

---

## Processors

### TextProcessor

```python
TextProcessor().process(file_path: str) -> List[Document]
```

### PDFProcessor

```python
PDFProcessor().process(file_path: str) -> List[Document]
```

### MarkdownProcessor

```python
MarkdownProcessor().process(file_path: str) -> List[Document]
```

---

## Integrations

### SocraticRAGSkill (Openclaw)

```python
from socratic_rag.integrations.openclaw import SocraticRAGSkill

SocraticRAGSkill(
    vector_store: str = "chromadb",
    embedder: str = "sentence-transformers",
    chunking_strategy: str = "fixed",
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    top_k: int = 5,
    collection_name: str = "socratic_rag"
)
```

**Methods**:
- `add_document(content, source, metadata=None) -> str`
- `search(query, top_k=None) -> List[Dict]`
- `retrieve_context(query, top_k=None) -> str`
- `clear() -> bool`
- `get_config() -> RAGConfig`

### SocraticRAGRetriever (LangChain)

```python
from socratic_rag.integrations.langchain import SocraticRAGRetriever

SocraticRAGRetriever(
    client: RAGClient,
    top_k: int = 5
)
```

**Methods**:
- `get_relevant_documents(query: str) -> List[Document]`

---

## Exceptions

### Exception Hierarchy

```
SocraticRAGError
├── ConfigurationError
├── VectorStoreError
│   └── DocumentNotFoundError
├── EmbeddingError
├── ChunkingError
├── ProcessorError
├── ProviderNotFoundError
├── InvalidProviderError
└── AsyncRAGError
```

### Common Exceptions

```python
from socratic_rag.exceptions import (
    SocraticRAGError,          # Base exception
    ConfigurationError,         # Config validation error
    VectorStoreError,          # Vector store operation error
    EmbeddingError,            # Embedding operation error
    ChunkingError,             # Chunking operation error
    ProcessorError,            # Document processing error
    DocumentNotFoundError,     # Document not found
    ProviderNotFoundError,     # Provider not found
    InvalidProviderError,      # Invalid provider config
    AsyncRAGError,             # Async operation error
)
```

**Example**:
```python
from socratic_rag.exceptions import ConfigurationError

try:
    config = RAGConfig(chunk_size=-1)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

---

## Type Hints

All public APIs are fully type-hinted for MyPy compatibility:

```python
from typing import List, Optional, Dict, Any

results: List[SearchResult] = client.search(query)
document_id: str = client.add_document(content, source)
context: str = client.retrieve_context(query)
success: bool = client.clear()
```

---

## See Also

- [Quickstart Guide](quickstart.md)
- [Vector Stores Guide](vector-stores.md)
- [Embeddings Guide](embeddings.md)
- [Integrations Guide](integrations.md)
