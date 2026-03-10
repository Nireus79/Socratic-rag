"""Tests for vector store providers."""

import pytest
from socratic_rag.vector_stores import ChromaDBVectorStore
from socratic_rag.models import Chunk
from socratic_rag.exceptions import VectorStoreError


@pytest.mark.unit
class TestChrmaDBVectorStore:
    """Test ChromaDBVectorStore."""

    @pytest.fixture
    def vector_store(self):
        """Provide a vector store instance."""
        store = ChromaDBVectorStore(collection_name="test_collection")
        yield store
        # Cleanup
        store.clear()

    def test_vector_store_initialization(self, vector_store):
        """Test vector store initialization."""
        assert vector_store.collection_name == "test_collection"
        assert vector_store.collection is not None

    def test_add_documents(self, vector_store):
        """Test adding documents to vector store."""
        chunks = [
            Chunk.create(
                text="Hello world",
                document_id="doc1",
            ),
            Chunk.create(
                text="Test document",
                document_id="doc1",
            ),
        ]
        embeddings = [
            [0.1] * 384,  # 384-dimensional embedding
            [0.2] * 384,
        ]

        chunk_ids = vector_store.add_documents(chunks, embeddings)
        assert len(chunk_ids) == 2
        assert all(isinstance(id, str) for id in chunk_ids)

    def test_add_empty_documents(self, vector_store):
        """Test adding empty document list."""
        chunk_ids = vector_store.add_documents([], [])
        assert chunk_ids == []

    def test_mismatched_chunks_embeddings(self, vector_store):
        """Test that mismatched chunks and embeddings raise error."""
        chunks = [
            Chunk.create(text="Hello", document_id="doc1"),
        ]
        embeddings = [
            [0.1] * 384,
            [0.2] * 384,
        ]

        with pytest.raises(VectorStoreError):
            vector_store.add_documents(chunks, embeddings)

    def test_search(self, vector_store):
        """Test searching documents."""
        chunks = [
            Chunk.create(
                text="Python is a programming language",
                document_id="doc1",
            ),
            Chunk.create(
                text="Java is another programming language",
                document_id="doc2",
            ),
        ]
        embeddings = [
            [0.1] * 384,
            [0.2] * 384,
        ]

        vector_store.add_documents(chunks, embeddings)

        # Search with similar embedding to first chunk
        query_embedding = [0.11] * 384
        results = vector_store.search(query_embedding, top_k=2)

        assert len(results) <= 2
        assert all(hasattr(r, "chunk") and hasattr(r, "score") for r in results)

    def test_search_empty_store(self, vector_store):
        """Test searching empty store."""
        query_embedding = [0.1] * 384
        results = vector_store.search(query_embedding, top_k=5)
        assert results == []

    def test_delete_documents(self, vector_store):
        """Test deleting documents."""
        chunks = [
            Chunk.create(text="Hello", document_id="doc1"),
            Chunk.create(text="World", document_id="doc1"),
        ]
        embeddings = [
            [0.1] * 384,
            [0.2] * 384,
        ]

        chunk_ids = vector_store.add_documents(chunks, embeddings)
        assert vector_store.delete(chunk_ids)

    def test_delete_empty_list(self, vector_store):
        """Test deleting empty list."""
        assert vector_store.delete([])

    def test_get_document(self, vector_store):
        """Test getting document by ID."""
        chunk = Chunk.create(
            text="Hello world",
            document_id="doc1",
            metadata={"key": "value"},
        )
        embeddings = [[0.1] * 384]

        chunk_ids = vector_store.add_documents([chunk], embeddings)
        chunk_id = chunk_ids[0]

        retrieved = vector_store.get(chunk_id)
        assert retrieved is not None
        assert retrieved.text == "Hello world"
        assert retrieved.document_id == "doc1"

    def test_get_nonexistent_document(self, vector_store):
        """Test getting nonexistent document."""
        retrieved = vector_store.get("nonexistent_id")
        assert retrieved is None

    def test_clear(self, vector_store):
        """Test clearing vector store."""
        chunks = [
            Chunk.create(text="Hello", document_id="doc1"),
        ]
        embeddings = [[0.1] * 384]

        vector_store.add_documents(chunks, embeddings)
        assert vector_store.clear()

        # After clearing, search should return empty
        results = vector_store.search([0.1] * 384, top_k=5)
        assert results == []
