"""Tests for integrations."""

import pytest
from socratic_rag import RAGClient, RAGConfig
from socratic_rag.integrations.openclaw import SocraticRAGSkill
from socratic_rag.integrations.langchain import SocraticRAGRetriever


class TestOpenclaw:
    """Test Openclaw RAG skill."""

    @pytest.fixture
    def skill(self):
        """Provide a RAG skill."""
        skill = SocraticRAGSkill(
            vector_store="chromadb",
            chunk_size=100,
        )
        yield skill
        skill.clear()

    def test_skill_initialization(self, skill):
        """Test skill initialization."""
        assert skill.client is not None
        assert skill.client.config.vector_store == "chromadb"

    def test_add_document(self, skill):
        """Test adding document through skill."""
        doc_id = skill.add_document(
            content="Test content",
            source="test.txt",
        )
        assert doc_id is not None

    def test_search(self, skill):
        """Test search through skill."""
        skill.add_document("Python is great", "test1.txt")
        skill.add_document("Java is powerful", "test2.txt")

        results = skill.search("Python")
        assert isinstance(results, list)
        assert all("score" in r and "text" in r for r in results)

    def test_retrieve_context(self, skill):
        """Test context retrieval through skill."""
        skill.add_document("Test content", "test.txt")
        context = skill.retrieve_context("test")
        assert isinstance(context, str)

    def test_get_config(self, skill):
        """Test getting config from skill."""
        config = skill.get_config()
        assert config.vector_store == "chromadb"
        assert config.chunk_size == 100


class TestLangChain:
    """Test LangChain retriever."""

    @pytest.fixture
    def client(self):
        """Provide a RAG client."""
        config = RAGConfig(chunk_size=100)
        client = RAGClient(config)
        yield client
        client.clear()

    @pytest.fixture
    def retriever(self, client):
        """Provide a LangChain retriever."""
        return SocraticRAGRetriever(client=client, top_k=5)

    def test_retriever_initialization(self, retriever):
        """Test retriever initialization."""
        assert retriever.client is not None
        assert retriever.top_k == 5

    def test_get_relevant_documents(self, client, retriever):
        """Test getting relevant documents."""
        client.add_document("Python is great", "test1.txt")
        client.add_document("Java is powerful", "test2.txt")

        documents = retriever.get_relevant_documents("Python")
        assert isinstance(documents, list)
        assert all(hasattr(d, "page_content") for d in documents)

    def test_documents_have_metadata(self, client, retriever):
        """Test that retrieved documents have metadata."""
        client.add_document("Test content", "test.txt")

        documents = retriever.get_relevant_documents("test")
        assert len(documents) > 0
        assert "chunk_id" in documents[0].metadata
        assert "score" in documents[0].metadata
