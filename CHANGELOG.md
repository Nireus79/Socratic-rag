# Changelog

All notable changes to Socratic RAG will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-03-10

### Added

#### Core Features
- **RAGClient**: Main synchronous client for RAG operations
- **AsyncRAGClient**: Async/await interface for non-blocking operations
- **LLMPoweredRAG**: RAG with LLM-powered answer generation

#### Vector Store Providers
- **ChromaDBVectorStore**: Default vector store using Chroma (in-memory and persistent)
- **QdrantVectorStore**: Qdrant vector store for local and remote instances
- **FAISSVectorStore**: FAISS vector store with persistence support

#### Embedding Providers
- **SentenceTransformersEmbedder**: Default embedder using sentence-transformers models

#### Chunking Strategies
- **FixedSizeChunker**: Fixed-size text chunking with overlap support

#### Document Processors
- **TextProcessor**: Process plain text files
- **PDFProcessor**: Process PDF documents
- **MarkdownProcessor**: Process Markdown files

#### Framework Integrations
- **SocraticRAGSkill**: Openclaw skill for RAG operations
- **SocraticRAGRetriever**: LangChain-compatible retriever

#### Data Models
- **Document**: Raw document with metadata
- **Chunk**: Text chunk with position and metadata
- **SearchResult**: Search result with relevance score
- **RAGConfig**: Configuration object for RAG client

#### Exception Hierarchy
- SocraticRAGError (base)
- ConfigurationError
- VectorStoreError
- EmbeddingError
- ChunkingError
- ProcessorError
- DocumentNotFoundError
- ProviderNotFoundError
- InvalidProviderError
- AsyncRAGError

#### Examples
- 01_basic_rag.py: Basic RAG workflow
- 02_multi_vector_stores.py: Using different vector stores
- 03_openclaw_integration.py: Openclaw skill usage
- 04_langchain_integration.py: LangChain integration
- 05_llm_powered_rag.py: LLM-powered answer generation

#### Testing
- Comprehensive test suite with 70%+ coverage
- Unit tests for all major components
- Integration tests for end-to-end workflows
- Pytest configuration with coverage reporting

#### Documentation
- README.md with quick start and examples
- CONTRIBUTING.md with contribution guidelines
- API documentation in docstrings
- Type hints throughout codebase

#### CI/CD
- GitHub Actions workflow for testing
- Multi-platform testing (Linux, Windows, macOS)
- Python version matrix (3.8-3.12)
- Code quality checks (black, ruff, mypy)
- Coverage reporting

### Project Structure

```
socratic-rag/
├── src/socratic_rag/
│   ├── client.py                 # Main RAG client
│   ├── async_client.py          # Async RAG client
│   ├── llm_rag.py               # LLM integration
│   ├── models.py                # Data models
│   ├── exceptions.py            # Exception hierarchy
│   ├── embeddings/              # Embedding providers
│   ├── chunking/                # Chunking strategies
│   ├── vector_stores/           # Vector store providers
│   ├── processors/              # Document processors
│   └── integrations/            # Framework integrations
├── tests/                       # Comprehensive test suite
├── examples/                    # Usage examples
├── docs/                        # Documentation
└── pyproject.toml              # Project configuration
```

### Dependencies

**Core**:
- numpy >= 1.20.0
- sentence-transformers >= 2.0.0

**Optional Vector Stores**:
- chromadb >= 0.4.0
- qdrant-client >= 1.0.0
- faiss-cpu >= 1.7.0
- pinecone-client >= 2.0.0

**Optional Document Processing**:
- PyPDF2 >= 3.0.0
- markdown >= 3.0.0

**Optional Integrations**:
- langchain >= 0.1.0
- socrates-nexus >= 0.3.0

**Development**:
- pytest >= 7.0
- pytest-asyncio >= 0.21.0
- pytest-cov >= 4.0
- black >= 23.0
- ruff >= 0.1.0
- mypy >= 1.0

## Roadmap

### v0.2.0 (Planned)
- [ ] Additional vector store providers (Milvus, Elasticsearch)
- [ ] Advanced chunking strategies (semantic, recursive)
- [ ] Hybrid search (vector + keyword)
- [ ] Re-ranking with cross-encoders
- [ ] OpenAI embeddings provider
- [ ] Vision model support

### v0.3.0 (Planned)
- [ ] Multi-language support
- [ ] Document metadata indexing
- [ ] Query expansion and reformulation
- [ ] Caching layer optimization
- [ ] Streaming responses
- [ ] Custom similarity metrics

## Known Limitations

- FAISS doesn't support true document deletion (marks as deleted in metadata)
- LangChain integration requires langchain package
- Qdrant integration requires qdrant-client package
- No built-in query expansion or reformulation
- No keyword search (vector-only)

## Upgrading

No breaking changes yet. All future 0.x releases will maintain backward compatibility.

---

## Version History

### [0.1.0] - 2024-03-10

Initial release with core RAG functionality, multiple vector stores, and framework integrations.
