"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest

from socratic_rag import RAGClient, RAGConfig


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def rag_client():
    """Provide a RAG client for testing."""
    config = RAGConfig(
        vector_store="chromadb",
        embedder="sentence-transformers",
        chunking_strategy="fixed",
        chunk_size=100,
        chunk_overlap=10,
    )
    client = RAGClient(config)
    yield client
    # Cleanup
    client.clear()


@pytest.fixture
def sample_text():
    """Provide sample text for testing."""
    return """
    Python is a high-level, interpreted programming language known for
    its simplicity and readability. It was created by Guido van Rossum
    and first released in 1991. Python is widely used in web development,
    data science, artificial intelligence, and automation. The language
    emphasizes code readability and uses indentation to define code blocks.
    """


@pytest.fixture
def sample_documents():
    """Provide sample documents for testing."""
    return [
        {
            "content": "Machine learning is a subset of artificial intelligence.",
            "source": "ml_intro.txt",
        },
        {
            "content": "Deep learning uses neural networks with multiple layers.",
            "source": "dl_intro.txt",
        },
        {
            "content": "Natural language processing enables computers to understand text.",
            "source": "nlp_intro.txt",
        },
    ]
