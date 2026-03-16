# Socratic RAG - Architecture & System Design

## System Overview

Socratic RAG provides production-grade Retrieval-Augmented Generation (RAG) with support for multiple vector stores, flexible embeddings, smart chunking, and full async/await support.

## Core Components

### 1. RAGClient

Main synchronous interface for RAG operations.

**Key Methods**:
- `add_document(content, source, metadata=None)` - Add document to knowledge base
- `search(query, top_k=5)` - Search for relevant documents
- `retrieve_context(query)` - Get formatted context for LLM
- `clear()` - Clear all documents

### 2. AsyncRAGClient

Asynchronous version for non-blocking RAG operations.

**Key Methods**:
- `async add_document(content, source, metadata=None)`
- `async search(query, top_k=5)`
- `async retrieve_context(query)`

### 3. Vector Store Providers

Pluggable vector storage backends.

**Supported**:
- ChromaDB (default, in-memory)
- Qdrant (production vector DB)
- FAISS (local, fast)
- Pinecone (cloud vector DB)

### 4. Embedding Providers

Convert text to vector embeddings.

**Supported**:
- Sentence Transformers (default, local)
- OpenAI Embeddings (via Socrates Nexus)

### 5. Chunking Strategies

Split documents for optimal embedding/retrieval.

**Strategies**:
- Fixed-size chunking (default)
- Semantic chunking (groups by meaning)
- Recursive chunking (hierarchical)

## Data Models

### Document
Raw document with metadata.

### Chunk
Text segment with position and metadata.

### SearchResult
Search result with relevance score.

### RAGConfig
Configuration object with all RAG settings.

## Request Flow

1. Document added
2. Chunked by strategy
3. Embedded by provider
4. Stored in vector database
5. On search: Query embedded, similar vectors retrieved
6. Results returned with similarity scores

## Integration Points

- Socrates Nexus for LLM integration
- Openclaw skills integration
- LangChain components
- Custom vector store support
