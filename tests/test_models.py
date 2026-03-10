"""Tests for data models."""

from datetime import datetime

import pytest

from socratic_rag.models import Chunk, Document, RAGConfig, SearchResult


class TestChunk:
    """Test Chunk model."""

    def test_chunk_creation(self):
        """Test creating a chunk."""
        chunk = Chunk(
            text="Hello world",
            chunk_id="id1",
            document_id="doc1",
            metadata={"key": "value"},
        )
        assert chunk.text == "Hello world"
        assert chunk.chunk_id == "id1"
        assert chunk.document_id == "doc1"
        assert chunk.metadata == {"key": "value"}

    def test_chunk_create_with_auto_id(self):
        """Test creating a chunk with auto-generated ID."""
        chunk = Chunk.create(
            text="Hello world",
            document_id="doc1",
            metadata={"key": "value"},
        )
        assert chunk.text == "Hello world"
        assert chunk.document_id == "doc1"
        assert chunk.chunk_id is not None
        assert len(chunk.chunk_id) > 0

    def test_chunk_default_metadata(self):
        """Test chunk with default metadata."""
        chunk = Chunk.create(
            text="Hello",
            document_id="doc1",
        )
        assert chunk.metadata == {}


class TestDocument:
    """Test Document model."""

    def test_document_creation(self):
        """Test creating a document."""
        doc = Document(
            content="Hello world",
            document_id="doc1",
            source="test.txt",
            metadata={"key": "value"},
        )
        assert doc.content == "Hello world"
        assert doc.document_id == "doc1"
        assert doc.source == "test.txt"
        assert doc.metadata == {"key": "value"}

    def test_document_create_with_auto_id(self):
        """Test creating a document with auto-generated ID."""
        doc = Document.create(
            content="Hello world",
            source="test.txt",
        )
        assert doc.content == "Hello world"
        assert doc.source == "test.txt"
        assert doc.document_id is not None
        assert len(doc.document_id) > 0

    def test_document_created_at(self):
        """Test document created_at timestamp."""
        doc = Document.create(
            content="Hello",
            source="test.txt",
        )
        assert isinstance(doc.created_at, datetime)


class TestSearchResult:
    """Test SearchResult model."""

    def test_search_result_creation(self):
        """Test creating a search result."""
        chunk = Chunk.create(
            text="Hello",
            document_id="doc1",
        )
        result = SearchResult(chunk=chunk, score=0.95)
        assert result.chunk == chunk
        assert result.score == 0.95
        assert result.document is None

    def test_search_result_with_document(self):
        """Test search result with document."""
        chunk = Chunk.create(
            text="Hello",
            document_id="doc1",
        )
        doc = Document.create(
            content="Hello world",
            source="test.txt",
        )
        result = SearchResult(chunk=chunk, score=0.95, document=doc)
        assert result.chunk == chunk
        assert result.score == 0.95
        assert result.document == doc


class TestRAGConfig:
    """Test RAGConfig model."""

    def test_default_config(self):
        """Test default configuration."""
        config = RAGConfig()
        assert config.vector_store == "chromadb"
        assert config.embedder == "sentence-transformers"
        assert config.chunking_strategy == "fixed"
        assert config.chunk_size == 512
        assert config.chunk_overlap == 50
        assert config.top_k == 5

    def test_custom_config(self):
        """Test custom configuration."""
        config = RAGConfig(
            vector_store="qdrant",
            chunk_size=256,
            chunk_overlap=25,
        )
        assert config.vector_store == "qdrant"
        assert config.chunk_size == 256
        assert config.chunk_overlap == 25

    def test_invalid_chunk_size(self):
        """Test that negative chunk_size raises error."""
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            RAGConfig(chunk_size=-1)

    def test_overlap_greater_than_chunk_size(self):
        """Test that overlap >= chunk_size raises error."""
        with pytest.raises(ValueError, match="chunk_overlap must be less"):
            RAGConfig(chunk_size=100, chunk_overlap=100)

    def test_invalid_top_k(self):
        """Test that negative top_k raises error."""
        with pytest.raises(ValueError, match="top_k must be positive"):
            RAGConfig(top_k=-1)

    def test_invalid_cache_ttl(self):
        """Test that negative cache_ttl raises error."""
        with pytest.raises(ValueError, match="cache_ttl must be positive"):
            RAGConfig(cache_ttl=-1)
