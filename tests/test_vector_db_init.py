"""The vector database can be created and its helper classes resolve."""

import pytest

pytest.importorskip("chromadb")
pytest.importorskip("sentence_transformers")


def test_knowledge_entry_fields():
    from socratic_rag import KnowledgeEntry

    entry = KnowledgeEntry(id="a", content="text", category="note")
    assert entry.metadata is None
    assert entry.embedding is None


def test_vector_database_creates_caches(tmp_path):
    from socratic_rag import VectorDatabase

    db = VectorDatabase(str(tmp_path / "chroma"))
    assert db.embedding_cache is not None
    assert db.search_cache is not None
    assert db.knowledge_loaded is False
