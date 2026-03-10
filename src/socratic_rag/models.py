"""Data models for Socratic RAG."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class Chunk:
    """Text chunk with metadata."""

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
        end_char: int = 0,
    ) -> "Chunk":
        """Create a chunk with auto-generated ID."""
        return cls(
            text=text,
            chunk_id=str(uuid.uuid4()),
            document_id=document_id,
            metadata=metadata or {},
            start_char=start_char,
            end_char=end_char,
        )


@dataclass
class Document:
    """Document to be indexed."""

    content: str
    document_id: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Document":
        """Create a document with auto-generated ID."""
        return cls(
            content=content,
            document_id=str(uuid.uuid4()),
            source=source,
            metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
        )


@dataclass
class SearchResult:
    """Search result with score."""

    chunk: Chunk
    score: float
    document: Optional[Document] = None


@dataclass
class RAGConfig:
    """Configuration for RAG client."""

    vector_store: str = "chromadb"
    embedder: str = "sentence-transformers"
    chunking_strategy: str = "fixed"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5
    embedding_cache: bool = True
    cache_ttl: int = 3600
    collection_name: str = "socratic_rag"

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.cache_ttl <= 0:
            raise ValueError("cache_ttl must be positive")
