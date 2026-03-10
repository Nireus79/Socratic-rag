"""Socratic RAG - Production-grade Retrieval-Augmented Generation."""

from .client import RAGClient
from .async_client import AsyncRAGClient
from .models import Chunk, Document, RAGConfig, SearchResult
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
from .embeddings import BaseEmbedder, SentenceTransformersEmbedder
from .chunking import BaseChunker, FixedSizeChunker
from .vector_stores import BaseVectorStore, ChromaDBVectorStore

__version__ = "0.1.0"

__all__ = [
    "RAGClient",
    "AsyncRAGClient",
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
    "BaseVectorStore",
    "ChromaDBVectorStore",
]
