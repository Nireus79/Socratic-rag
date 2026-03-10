"""Tests for LLM-powered RAG."""

import pytest
from socratic_rag import RAGClient, RAGConfig, LLMPoweredRAG
from socratic_rag.exceptions import SocraticRAGError


class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, response_text: str = "Test response"):
        self.response_text = response_text
        self.last_prompt = None

    def chat(self, prompt: str, **kwargs):
        """Return mock response."""
        self.last_prompt = prompt

        class Response:
            def __init__(self, content):
                self.content = content

        return Response(self.response_text)


class TestLLMPoweredRAG:
    """Test LLMPoweredRAG."""

    @pytest.fixture
    def rag_client(self):
        """Provide a RAG client."""
        config = RAGConfig(chunk_size=100)
        client = RAGClient(config)
        yield client
        client.clear()

    @pytest.fixture
    def llm_client(self):
        """Provide a mock LLM client."""
        return MockLLMClient(response_text="This is a test answer.")

    @pytest.fixture
    def llm_rag(self, rag_client, llm_client):
        """Provide LLM-powered RAG."""
        return LLMPoweredRAG(rag_client=rag_client, llm_client=llm_client)

    def test_initialization(self, llm_rag):
        """Test LLMPoweredRAG initialization."""
        assert llm_rag.rag is not None
        assert llm_rag.llm is not None

    def test_initialization_without_llm(self, rag_client):
        """Test initialization without LLM."""
        llm_rag = LLMPoweredRAG(rag_client=rag_client, llm_client=None)
        assert llm_rag.rag is not None
        assert llm_rag.llm is None

    def test_add_document(self, llm_rag):
        """Test adding document."""
        doc_id = llm_rag.add_document(
            content="Test content",
            source="test.txt",
        )
        assert doc_id is not None

    def test_search(self, llm_rag):
        """Test search."""
        llm_rag.add_document("Test content", "test.txt")
        results = llm_rag.search("test")
        assert isinstance(results, list)

    def test_retrieve_context(self, llm_rag):
        """Test context retrieval."""
        llm_rag.add_document("Test content", "test.txt")
        context = llm_rag.retrieve_context("test")
        assert isinstance(context, str)

    def test_generate_answer(self, llm_rag):
        """Test answer generation."""
        llm_rag.add_document("Python is great", "test.txt")

        answer = llm_rag.generate_answer("What is Python?")
        assert isinstance(answer, str)
        assert len(answer) > 0

    def test_generate_answer_without_llm(self, rag_client):
        """Test that answer generation fails without LLM."""
        llm_rag = LLMPoweredRAG(rag_client=rag_client, llm_client=None)
        llm_rag.add_document("Test content", "test.txt")

        with pytest.raises(SocraticRAGError):
            llm_rag.generate_answer("test")

    def test_generate_answer_with_custom_prompt(self, llm_rag):
        """Test answer generation with custom system prompt."""
        llm_rag.add_document("Python is great", "test.txt")

        answer = llm_rag.generate_answer(
            "What is Python?",
            system_prompt="You are a Python expert.",
        )
        assert isinstance(answer, str)
        assert "You are a Python expert" in llm_rag.llm.last_prompt

    def test_clear(self, llm_rag):
        """Test clearing knowledge base."""
        llm_rag.add_document("Test content", "test.txt")
        assert llm_rag.clear()

    def test_custom_context_prefix_and_separator(self, llm_rag):
        """Test custom context prefix and separator."""
        llm_rag.add_document("Content 1", "test1.txt")
        llm_rag.add_document("Content 2", "test2.txt")

        answer = llm_rag.generate_answer(
            "test",
            context_prefix="Documents:\n",
            context_separator=" | ",
        )
        assert "Documents:" in llm_rag.llm.last_prompt

    def test_answer_contains_context(self, llm_rag):
        """Test that generated answer incorporates context."""
        llm_rag.add_document("Important fact about Python", "test.txt")

        _ = llm_rag.generate_answer("Python question")

        # The prompt sent to LLM should contain the context
        assert "Important fact about Python" in llm_rag.llm.last_prompt
