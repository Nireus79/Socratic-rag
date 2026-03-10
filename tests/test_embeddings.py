"""Tests for embedding providers."""

import pytest

from socratic_rag.embeddings import SentenceTransformersEmbedder
from socratic_rag.exceptions import EmbeddingError


class TestSentenceTransformersEmbedder:
    """Test SentenceTransformersEmbedder."""

    @pytest.fixture
    def embedder(self):
        """Provide an embedder instance."""
        return SentenceTransformersEmbedder()

    def test_embedder_initialization(self, embedder):
        """Test embedder initialization."""
        assert embedder.model is not None
        assert embedder.dimension > 0

    def test_embed_text(self, embedder):
        """Test embedding a single text."""
        embedding = embedder.embed_text("Hello world")
        assert isinstance(embedding, list)
        assert len(embedding) == embedder.dimension
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_batch(self, embedder):
        """Test embedding a batch of texts."""
        texts = ["Hello", "World", "Test"]
        embeddings = embedder.embed_batch(texts)
        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        assert all(len(e) == embedder.dimension for e in embeddings)

    def test_embed_empty_text(self, embedder):
        """Test that embedding empty text raises error."""
        with pytest.raises(EmbeddingError):
            embedder.embed_text("")

    def test_embed_empty_batch(self, embedder):
        """Test that embedding empty batch raises error."""
        with pytest.raises(EmbeddingError):
            embedder.embed_batch([])

    def test_embed_similar_texts(self, embedder):
        """Test that similar texts have similar embeddings."""
        text1 = "The cat sat on the mat"
        text2 = "A cat sat on a mat"
        text3 = "The dog ran in the park"

        emb1 = embedder.embed_text(text1)
        emb2 = embedder.embed_text(text2)
        emb3 = embedder.embed_text(text3)

        # Calculate cosine similarity
        def cosine_similarity(a, b):
            dot_product = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x**2 for x in a) ** 0.5
            norm_b = sum(x**2 for x in b) ** 0.5
            return dot_product / (norm_a * norm_b)

        similarity_12 = cosine_similarity(emb1, emb2)
        similarity_13 = cosine_similarity(emb1, emb3)

        # Similar texts should have higher similarity
        assert similarity_12 > similarity_13

    def test_embedding_dimension(self, embedder):
        """Test that embedding dimension is consistent."""
        dim = embedder.dimension
        assert dim == 384  # all-MiniLM-L6-v2 has 384 dimensions

    def test_custom_model(self):
        """Test embedder with custom model."""
        embedder = SentenceTransformersEmbedder(model_name="all-MiniLM-L6-v2")
        assert embedder.model_name == "all-MiniLM-L6-v2"
        assert embedder.dimension > 0
