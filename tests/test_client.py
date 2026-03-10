"""Tests for RAG client."""

import pytest

from socratic_rag import AsyncRAGClient, RAGClient, RAGConfig
from socratic_rag.exceptions import ProviderNotFoundError


class TestRAGClient:
    """Test RAGClient."""

    @pytest.fixture
    def client(self):
        """Provide a RAG client."""
        config = RAGConfig(
            chunk_size=100,
            chunk_overlap=10,
        )
        client = RAGClient(config)
        yield client
        client.clear()

    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.config is not None
        assert client.config.vector_store == "chromadb"

    def test_add_document(self, client):
        """Test adding a document."""
        doc_id = client.add_document(
            content="Python is a programming language.",
            source="test.txt",
        )
        assert doc_id is not None
        assert isinstance(doc_id, str)

    def test_add_document_with_metadata(self, client):
        """Test adding document with metadata."""
        doc_id = client.add_document(
            content="Test content",
            source="test.txt",
            metadata={"author": "John", "date": "2024"},
        )
        assert doc_id is not None

    def test_search(self, client):
        """Test searching documents."""
        # Add documents
        client.add_document("Python is great", "test1.txt")
        client.add_document("Java is powerful", "test2.txt")

        # Search
        results = client.search("Python", top_k=5)
        assert len(results) > 0
        assert all(hasattr(r, "chunk") and hasattr(r, "score") for r in results)

    def test_search_empty_index(self, client):
        """Test searching empty index."""
        results = client.search("test")
        assert results == []

    def test_retrieve_context(self, client):
        """Test retrieving context."""
        client.add_document("Python is great", "test1.txt")
        client.add_document("Java is powerful", "test2.txt")

        context = client.retrieve_context("Python")
        assert isinstance(context, str)
        assert len(context) > 0

    def test_retrieve_context_empty(self, client):
        """Test retrieving context from empty index."""
        context = client.retrieve_context("test")
        assert context == ""

    def test_clear(self, client):
        """Test clearing the knowledge base."""
        client.add_document("Test content", "test.txt")
        assert client.clear()

        # After clearing, search should return nothing
        results = client.search("test")
        assert results == []

    def test_invalid_vector_store(self):
        """Test invalid vector store provider."""
        config = RAGConfig(vector_store="invalid_store")
        client = RAGClient(config)
        with pytest.raises(ProviderNotFoundError):
            _ = client.vector_store

    def test_invalid_embedder(self):
        """Test invalid embedder provider."""
        config = RAGConfig(embedder="invalid_embedder")
        client = RAGClient(config)
        with pytest.raises(ProviderNotFoundError):
            _ = client.embedder

    def test_invalid_chunker(self):
        """Test invalid chunker provider."""
        config = RAGConfig(chunking_strategy="invalid_chunker")
        client = RAGClient(config)
        with pytest.raises(ProviderNotFoundError):
            _ = client.chunker

    def test_multiple_documents(self, client):
        """Test adding and searching multiple documents."""
        documents = [
            ("Machine learning is a subset of AI", "ml.txt"),
            ("Deep learning uses neural networks", "dl.txt"),
            ("Natural language processing is important", "nlp.txt"),
        ]

        for content, source in documents:
            client.add_document(content, source)

        results = client.search("neural networks")
        assert len(results) > 0

    def test_search_with_top_k(self, client):
        """Test search with custom top_k."""
        for i in range(10):
            client.add_document(f"Document {i} about testing", f"test{i}.txt")

        results = client.search("testing", top_k=3)
        assert len(results) <= 3

    def test_default_config(self):
        """Test client with default config."""
        client = RAGClient()
        assert client.config.chunk_size == 512
        assert client.config.top_k == 5


class TestAsyncRAGClient:
    """Test AsyncRAGClient."""

    @pytest.fixture
    def async_client(self):
        """Provide an async RAG client."""
        config = RAGConfig(chunk_size=100)
        client = AsyncRAGClient(config)
        yield client
        client.client.clear()

    @pytest.mark.asyncio
    async def test_async_add_document(self, async_client):
        """Test async document addition."""
        doc_id = await async_client.add_document(
            content="Test content",
            source="test.txt",
        )
        assert doc_id is not None

    @pytest.mark.asyncio
    async def test_async_search(self, async_client):
        """Test async search."""
        await async_client.add_document("Python is great", "test1.txt")
        await async_client.add_document("Java is powerful", "test2.txt")

        results = await async_client.search("Python")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_async_retrieve_context(self, async_client):
        """Test async context retrieval."""
        await async_client.add_document("Test content", "test.txt")
        context = await async_client.retrieve_context("test")
        assert isinstance(context, str)

    @pytest.mark.asyncio
    async def test_async_clear(self, async_client):
        """Test async clearing."""
        await async_client.add_document("Test", "test.txt")
        result = await async_client.clear()
        assert result
