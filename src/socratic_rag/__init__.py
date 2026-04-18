"""Socratic RAG - Production-grade Retrieval-Augmented Generation."""

from .async_client import AsyncRAGClient
from .chunking import BaseChunker, FixedSizeChunker, SemanticChunker, SlidingWindowChunker
from .client import RAGClient
from .deduplication import DeduplicateResult, DocumentDeduplicator, DuplicateGroup
from .embeddings import BaseEmbedder, SentenceTransformersEmbedder
from .exceptions import (
    AsyncRAGError,
    ChunkingError,
    ConfigurationError,
    DocumentNotFoundError,
    EmbeddingError,
    InvalidProviderError,
    ProcessorError,
    ProviderNotFoundError,
    SocraticRAGError,
    VectorStoreError,
)
from .llm_rag import LLMPoweredRAG
from .models import Chunk, Document, RAGConfig, SearchResult
from .query_enhancement import (
    MultimodalContent,
    MultimodalHandler,
    QueryExpander,
    QueryReranker,
    RankedResult,
)
from .vector_stores import BaseVectorStore, ChromaDBVectorStore, FAISSVectorStore, QdrantVectorStore

__version__ = "0.2.0"

__all__ = [
    "RAGClient",
    "AsyncRAGClient",
    "LLMPoweredRAG",
    "Chunk",
    "Document",
    "RAGConfig",
    "SearchResult",
    "SocraticRAGError",
    "ConfigurationError",
    "VectorStoreError",
    "EmbeddingError",
    "ChunkingError",
    "ProcessorError",
    "DocumentNotFoundError",
    "ProviderNotFoundError",
    "InvalidProviderError",
    "AsyncRAGError",
    "BaseEmbedder",
    "SentenceTransformersEmbedder",
    "BaseChunker",
    "FixedSizeChunker",
    "SemanticChunker",
    "SlidingWindowChunker",
    "BaseVectorStore",
    "ChromaDBVectorStore",
    "QdrantVectorStore",
    "FAISSVectorStore",
    # Deduplication
    "DocumentDeduplicator",
    "DeduplicateResult",
    # Query Enhancement
    "QueryReranker",
    "QueryExpander",
    "RankedResult",
    "MultimodalHandler",
    "MultimodalContent",
    "DuplicateGroup",
]
