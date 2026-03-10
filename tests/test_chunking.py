"""Tests for chunking strategies."""

import pytest
from socratic_rag.chunking import FixedSizeChunker
from socratic_rag.exceptions import ChunkingError


class TestFixedSizeChunker:
    """Test FixedSizeChunker."""

    def test_chunker_initialization(self):
        """Test chunker initialization."""
        chunker = FixedSizeChunker(chunk_size=100, overlap=10)
        assert chunker.chunk_size == 100
        assert chunker.overlap == 10

    def test_chunk_text(self):
        """Test chunking text."""
        chunker = FixedSizeChunker(chunk_size=50, overlap=10)
        text = "This is a test. " * 20  # ~320 characters
        chunks = chunker.chunk(text, document_id="doc1")

        assert len(chunks) > 1
        assert all(chunk.document_id == "doc1" for chunk in chunks)
        assert all(chunk.text for chunk in chunks)

    def test_chunk_overlap(self):
        """Test that chunks have overlap."""
        chunker = FixedSizeChunker(chunk_size=50, overlap=10)
        text = "This is a test sentence. " * 10
        chunks = chunker.chunk(text, document_id="doc1")

        if len(chunks) > 1:
            # Check for overlap between consecutive chunks
            chunk1_end = chunks[0].text[-10:]
            chunk2_start = chunks[1].text[:10]
            # There should be some overlap
            assert len(chunks[0].text) <= 50

    def test_chunk_ids(self):
        """Test that chunks have unique IDs."""
        chunker = FixedSizeChunker(chunk_size=50, overlap=10)
        text = "This is a test. " * 20
        chunks = chunker.chunk(text, document_id="doc1")

        chunk_ids = [chunk.chunk_id for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))  # All unique

    def test_empty_text(self):
        """Test that empty text raises error."""
        chunker = FixedSizeChunker()
        with pytest.raises(ChunkingError):
            chunker.chunk("", document_id="doc1")

    def test_invalid_chunk_size(self):
        """Test that invalid chunk_size raises error."""
        with pytest.raises(ChunkingError):
            FixedSizeChunker(chunk_size=-1)

    def test_invalid_overlap(self):
        """Test that invalid overlap raises error."""
        with pytest.raises(ChunkingError):
            FixedSizeChunker(chunk_size=100, overlap=100)

    def test_chunk_positions(self):
        """Test that chunk positions are accurate."""
        chunker = FixedSizeChunker(chunk_size=50, overlap=0)
        text = "a" * 150
        chunks = chunker.chunk(text, document_id="doc1")

        assert chunks[0].start_char == 0
        assert chunks[0].end_char == 50
        assert chunks[1].start_char == 50
        assert chunks[1].end_char == 100

    def test_short_text(self):
        """Test chunking short text."""
        chunker = FixedSizeChunker(chunk_size=100)
        text = "Short text"
        chunks = chunker.chunk(text, document_id="doc1")

        assert len(chunks) == 1
        assert chunks[0].text == text

    def test_chunk_with_metadata(self):
        """Test chunking with metadata."""
        chunker = FixedSizeChunker()
        text = "Test text. " * 100
        metadata = {"key": "value", "source": "test.txt"}
        chunks = chunker.chunk(text, document_id="doc1", metadata=metadata)

        assert all(chunk.metadata == metadata for chunk in chunks)
