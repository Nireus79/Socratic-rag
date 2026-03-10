# Socratic RAG

[![PyPI version](https://badge.fury.io/py/socratic-rag.svg)](https://badge.fury.io/py/socratic-rag)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Test Coverage](https://img.shields.io/badge/coverage-70%25-brightgreen.svg)](https://github.com/Nireus79/Socratic-rag)

Production-grade Retrieval-Augmented Generation (RAG) package for Python.

## Features

- **Multiple Vector Databases**: ChromaDB, Qdrant, FAISS, Pinecone (with extensible provider pattern)
- **Flexible Embedding Providers**: Sentence Transformers, OpenAI (via Socrates Nexus)
- **Smart Chunking**: Fixed-size, semantic, and recursive chunking strategies
- **Document Processing**: Text, PDF, Markdown, and code files
- **Framework Integrations**: Openclaw skills and LangChain components
- **Async Support**: Full async/await interface for non-blocking operations
- **Production Ready**: 70%+ test coverage, type hints, comprehensive documentation

## Installation

### Basic Installation

```bash
pip install socratic-rag
```

### With Optional Dependencies

```bash
# All features
pip install socratic-rag[all]

# Specific vector stores
pip install socratic-rag[chromadb,qdrant,faiss]

# Document processing
pip install socratic-rag[pdf,markdown]

# Integrations
pip install socratic-rag[langchain,openclaw,nexus]

# Development
pip install socratic-rag[dev]
```

## Quick Start

### Basic Usage

```python
from socratic_rag import RAGClient

# Initialize client
client = RAGClient()

# Add documents
doc_id = client.add_document(
    content="Python is a programming language created by Guido van Rossum.",
    source="python_facts.txt"
)

# Search
results = client.search("What is Python?", top_k=5)
for result in results:
    print(f"Score: {result.score:.2f}")
    print(f"Text: {result.chunk.text}\n")

# Retrieve formatted context for LLM
context = client.retrieve_context("What is Python?")
print(context)
```

### Custom Configuration

```python
from socratic_rag import RAGClient, RAGConfig

config = RAGConfig(
    vector_store="chromadb",
    embedder="sentence-transformers",
    chunking_strategy="fixed",
    chunk_size=512,
    chunk_overlap=50,
    top_k=5,
)

client = RAGClient(config)
```

### Async Usage

```python
import asyncio
from socratic_rag import AsyncRAGClient

async def main():
    client = AsyncRAGClient()

    # Add documents asynchronously
    doc_id = await client.add_document(
        content="Document content",
        source="source.txt"
    )

    # Search asynchronously
    results = await client.search("query")

    # Retrieve context asynchronously
    context = await client.retrieve_context("query")

asyncio.run(main())
```

## Architecture

### Provider Pattern

Socratic RAG uses an extensible provider pattern for easy integration of new components:

```
RAGClient
├── Embedder Provider (sentence-transformers, OpenAI, etc.)
├── Chunker Provider (fixed, semantic, recursive)
└── Vector Store Provider (ChromaDB, Qdrant, FAISS, Pinecone)
```

### Core Models

- **Document**: Raw document with metadata
- **Chunk**: Text chunk with position and metadata
- **SearchResult**: Search result with relevance score
- **RAGConfig**: Configuration object

## Examples

See the `examples/` directory for:

1. `01_basic_rag.py` - Basic RAG workflow
2. `02_qdrant_rag.py` - Using Qdrant vector store
3. `03_faiss_rag.py` - Using FAISS vector store
4. `04_document_processing.py` - Document processing
5. `05_openclaw_integration.py` - Openclaw skill integration
6. `06_langchain_integration.py` - LangChain integration
7. `07_llm_powered_rag.py` - RAG with LLM (using Socrates Nexus)

## Testing

Run the test suite:

```bash
pytest tests/ -v --cov=socratic_rag
```

Specific test categories:

```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests only
pytest tests/ -m integration

# Exclude slow tests
pytest tests/ -m "not slow"
```

## Vector Store Providers

### ChromaDB (Default)

```python
from socratic_rag import RAGClient, RAGConfig

config = RAGConfig(vector_store="chromadb")
client = RAGClient(config)
```

### Qdrant

```python
config = RAGConfig(vector_store="qdrant")
client = RAGClient(config)
```

### FAISS

```python
config = RAGConfig(vector_store="faiss")
client = RAGClient(config)
```

## Embedding Providers

### Sentence Transformers (Default)

```python
config = RAGConfig(embedder="sentence-transformers")
client = RAGClient(config)
```

### OpenAI (via Socrates Nexus)

```python
config = RAGConfig(embedder="openai")
client = RAGClient(config)
```

## Document Processing

### Text Files

```python
from socratic_rag.processors import TextProcessor

processor = TextProcessor()
documents = processor.process("path/to/file.txt")
```

### PDF Files

```python
from socratic_rag.processors import PDFProcessor

processor = PDFProcessor()
documents = processor.process("path/to/file.pdf")
```

### Markdown Files

```python
from socratic_rag.processors import MarkdownProcessor

processor = MarkdownProcessor()
documents = processor.process("path/to/file.md")
```

## Framework Integrations

### Openclaw

```python
from socratic_rag.integrations.openclaw import SocraticRAGSkill

skill = SocraticRAGSkill(vector_store="chromadb")
skill.add_document("content", "source.txt")
results = skill.search("query")
```

### LangChain

```python
from socratic_rag.integrations.langchain import SocraticRAGRetriever
from langchain.chat_models import ChatAnthropic
from langchain.chains import RetrievalQA

retriever = SocraticRAGRetriever(client=rag_client, top_k=5)
llm = ChatAnthropic(model="claude-sonnet")
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

answer = qa.run("What is Python?")
```

## API Reference

### RAGClient

#### Methods

- `add_document(content, source, metadata=None) -> str` - Add document to knowledge base
- `search(query, top_k=None, filters=None) -> List[SearchResult]` - Search for relevant documents
- `retrieve_context(query, top_k=None) -> str` - Retrieve formatted context for LLM
- `clear() -> bool` - Clear all documents

### AsyncRAGClient

Same methods as RAGClient but with async/await.

## Configuration Options

```python
RAGConfig(
    vector_store="chromadb",           # Vector store provider
    embedder="sentence-transformers",  # Embedding provider
    chunking_strategy="fixed",         # Chunking strategy
    chunk_size=512,                    # Characters per chunk
    chunk_overlap=50,                  # Overlap between chunks
    top_k=5,                           # Default number of results
    embedding_cache=True,              # Cache embeddings
    cache_ttl=3600,                    # Cache TTL in seconds
    collection_name="socratic_rag",    # Collection name
)
```

## Exceptions

- `SocraticRAGError` - Base exception
- `ConfigurationError` - Configuration validation error
- `VectorStoreError` - Vector store operation error
- `EmbeddingError` - Embedding operation error
- `ChunkingError` - Chunking operation error
- `ProcessorError` - Document processing error
- `DocumentNotFoundError` - Document not found
- `ProviderNotFoundError` - Provider not found

## Performance Tips

1. **Use appropriate chunk size**: Smaller chunks (256-512) for dense retrieval, larger (1024+) for sparse
2. **Set overlap wisely**: 10-15% overlap usually works well
3. **Cache embeddings**: Enable embedding cache for repeated queries
4. **Batch operations**: Use `embed_batch()` for multiple embeddings
5. **Choose right embedder**: Sentence Transformers for local, OpenAI for production scale

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## License

MIT License - see `LICENSE` file for details

## Citation

If you use Socratic RAG in your research, please cite:

```bibtex
@software{socratic_rag_2024,
  title={Socratic RAG: Production-grade Retrieval-Augmented Generation},
  author={Your Name},
  year={2024},
  url={https://github.com/Nireus79/Socratic-rag}
}
```

## Roadmap

### v0.1.0 (Current)
- ✅ Core RAG functionality
- ✅ ChromaDB vector store
- ✅ Sentence Transformers embeddings
- ✅ Fixed-size chunking
- ✅ Openclaw integration
- ✅ LangChain integration

### v0.2.0
- Qdrant and FAISS vector stores
- Semantic chunking
- Pinecone cloud provider
- Vision model support

### v0.3.0
- Hybrid search (vector + keyword)
- Re-ranking with cross-encoders
- Multi-language support

## Support

For issues, questions, or suggestions:
- GitHub Issues: https://github.com/Nireus79/Socratic-rag/issues
- Discussions: https://github.com/Nireus79/Socratic-rag/discussions
