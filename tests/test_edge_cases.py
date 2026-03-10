"""Edge case tests for Socratic RAG."""

import pytest

from socratic_rag import RAGClient, RAGConfig
from socratic_rag.exceptions import EmbeddingError, VectorStoreError


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def client(self):
        """Provide a RAG client."""
        config = RAGConfig(chunk_size=100, chunk_overlap=10)
        client = RAGClient(config)
        yield client
        client.clear()

    # Text Edge Cases
    def test_very_short_document(self, client):
        """Test document with minimal text."""
        doc_id = client.add_document("a", "test.txt")
        assert doc_id is not None

    def test_very_long_document(self, client):
        """Test document with very long text."""
        long_text = "word " * 10000  # ~50KB
        doc_id = client.add_document(long_text, "test.txt")
        assert doc_id is not None
        results = client.search("word")
        assert len(results) > 0

    def test_document_with_special_characters(self, client):
        """Test document with special characters."""
        special_text = "Hello! @#$%^&*() 你好 🎉 日本語"
        doc_id = client.add_document(special_text, "special.txt")
        assert doc_id is not None

    def test_document_with_newlines(self, client):
        """Test document with multiple newlines."""
        multiline = "Line 1\n\n\n\nLine 2\n\n\n\nLine 3"
        doc_id = client.add_document(multiline, "multiline.txt")
        assert doc_id is not None

    def test_whitespace_only_document(self, client):
        """Test document with only whitespace."""
        # Single space should add
        doc_id = client.add_document("   ", "whitespace.txt")
        assert doc_id is not None

    # Search Edge Cases
    def test_search_empty_query(self, client):
        """Test search with empty query."""
        client.add_document("test content", "test.txt")
        # Empty query might be handled differently by embedder
        try:
            results = client.search("")
            # If no error, results should be empty or valid
            assert isinstance(results, list)
        except EmbeddingError:
            # Expected behavior
            pass

    def test_search_very_long_query(self, client):
        """Test search with very long query."""
        client.add_document("content", "test.txt")
        long_query = "word " * 1000
        results = client.search(long_query)
        assert isinstance(results, list)

    def test_search_special_character_query(self, client):
        """Test search with special characters."""
        client.add_document("Hello world", "test.txt")
        results = client.search("!@#$%^&*()")
        assert isinstance(results, list)

    def test_search_with_zero_top_k(self, client):
        """Test search with top_k=0."""
        client.add_document("content", "test.txt")
        with pytest.raises(VectorStoreError):
            client.search("query", top_k=0)

    def test_search_with_negative_top_k(self, client):
        """Test search with negative top_k."""
        client.add_document("content", "test.txt")
        with pytest.raises(VectorStoreError):
            client.search("query", top_k=-5)

    def test_search_with_very_large_top_k(self, client):
        """Test search with very large top_k."""
        client.add_document("content", "test.txt")
        results = client.search("query", top_k=1000000)
        # Should return available results, not error
        assert isinstance(results, list)
        assert len(results) <= 1

    # Configuration Edge Cases
    def test_chunk_size_equals_text_length(self, client):
        """Test when chunk size equals text length."""
        config = RAGConfig(chunk_size=11, chunk_overlap=0)
        client = RAGClient(config)
        doc_id = client.add_document("hello world", "test.txt")
        assert doc_id is not None

    def test_chunk_size_larger_than_text(self, client):
        """Test when chunk size is larger than text."""
        config = RAGConfig(chunk_size=1000, chunk_overlap=0)
        client = RAGClient(config)
        doc_id = client.add_document("short", "test.txt")
        assert doc_id is not None

    def test_zero_chunk_overlap(self, client):
        """Test with zero chunk overlap."""
        config = RAGConfig(chunk_size=50, chunk_overlap=0)
        client = RAGClient(config)
        doc_id = client.add_document("a" * 200, "test.txt")
        assert doc_id is not None

    def test_max_chunk_overlap(self, client):
        """Test with maximum valid chunk overlap."""
        config = RAGConfig(chunk_size=100, chunk_overlap=99)
        client = RAGClient(config)
        doc_id = client.add_document("x" * 500, "test.txt")
        assert doc_id is not None

    # Metadata Edge Cases
    def test_document_with_large_metadata(self, client):
        """Test document with large metadata."""
        large_metadata = {
            f"key_{i}": f"value_{i}" * 100
            for i in range(100)
        }
        doc_id = client.add_document(
            "content",
            "test.txt",
            metadata=large_metadata
        )
        assert doc_id is not None

    def test_document_with_nested_metadata(self, client):
        """Test document with nested metadata."""
        nested_metadata = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        doc_id = client.add_document(
            "content",
            "test.txt",
            metadata=nested_metadata
        )
        assert doc_id is not None

    def test_document_with_null_metadata_values(self, client):
        """Test document with null metadata values."""
        metadata = {"key1": None, "key2": "value"}
        doc_id = client.add_document(
            "content",
            "test.txt",
            metadata=metadata
        )
        assert doc_id is not None

    # Multiple Operations
    def test_add_many_documents(self, client):
        """Test adding many documents."""
        for i in range(100):
            client.add_document(f"content {i}", f"test{i}.txt")

        results = client.search("content", top_k=10)
        assert len(results) > 0

    def test_search_after_clear(self, client):
        """Test search after clearing knowledge base."""
        client.add_document("content", "test.txt")
        client.clear()

        results = client.search("content")
        assert results == []

    def test_multiple_clears(self, client):
        """Test calling clear multiple times."""
        client.add_document("content", "test.txt")
        assert client.clear()
        assert client.clear()  # Should not error

    # Unicode and Encoding
    def test_unicode_content(self, client):
        """Test with unicode content."""
        unicode_text = "Hello 世界 🌍 مرحبا العالم"
        doc_id = client.add_document(unicode_text, "unicode.txt")
        assert doc_id is not None

        results = client.search("世界")
        assert isinstance(results, list)

    def test_emoji_only_content(self, client):
        """Test with emoji-only content."""
        emoji_text = "🎉 🎊 🎈 🎀 🎁"
        doc_id = client.add_document(emoji_text, "emoji.txt")
        assert doc_id is not None

    # Numerical Edge Cases
    def test_very_small_chunk_size(self, client):
        """Test with very small chunk size."""
        config = RAGConfig(chunk_size=1, chunk_overlap=0)
        client = RAGClient(config)
        doc_id = client.add_document("abc", "test.txt")
        assert doc_id is not None

    # Retrieval Edge Cases
    def test_retrieve_context_no_results(self, client):
        """Test retrieve_context when no documents match."""
        client.add_document("Python content", "python.txt")
        context = client.retrieve_context("completely unrelated query xyz")
        # Should return empty string or minimal context
        assert isinstance(context, str)

    def test_retrieve_context_with_large_top_k(self, client):
        """Test retrieve_context with large top_k."""
        client.add_document("content", "test.txt")
        context = client.retrieve_context("query", top_k=10000)
        assert isinstance(context, str)

    # Concurrent-like Operations
    def test_add_and_search_interleaved(self, client):
        """Test adding and searching interleaved."""
        client.add_document("first", "test1.txt")
        results1 = client.search("first")

        client.add_document("second", "test2.txt")
        results2 = client.search("second")

        assert len(results1) > 0
        assert len(results2) > 0

    def test_same_document_multiple_times(self, client):
        """Test adding same document multiple times."""
        content = "same content"
        id1 = client.add_document(content, "test1.txt")
        id2 = client.add_document(content, "test2.txt")

        # Should have different IDs
        assert id1 != id2

        # Search should find both
        results = client.search("same", top_k=10)
        assert len(results) >= 2
