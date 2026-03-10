"""Sentence Transformers embedding provider."""

from typing import List
from .base import BaseEmbedder
from ..exceptions import EmbeddingError


class SentenceTransformersEmbedder(BaseEmbedder):
    """Embedding provider using sentence-transformers.

    Uses pre-trained sentence transformer models for generating embeddings locally.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize the embedder.

        Args:
            model_name: Name of the sentence-transformer model to use.
                Default is 'all-MiniLM-L6-v2' which provides a good balance
                of speed and quality.

        Raises:
            EmbeddingError: If model initialization fails.
        """
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            self._dimension = self.model.get_sentence_embedding_dimension()
        except ImportError:
            raise EmbeddingError(
                "sentence-transformers is required for SentenceTransformersEmbedder. "
                "Install with: pip install sentence-transformers"
            )
        except Exception as e:
            raise EmbeddingError(f"Failed to initialize SentenceTransformersEmbedder: {e}")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed.

        Returns:
            List of floats representing the embedding.

        Raises:
            EmbeddingError: If embedding fails.
        """
        try:
            if not text or not text.strip():
                raise EmbeddingError("Cannot embed empty text")
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            raise EmbeddingError(f"Failed to embed text: {e}")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embeddings, one for each input text.

        Raises:
            EmbeddingError: If embedding fails.
        """
        try:
            if not texts:
                raise EmbeddingError("Cannot embed empty list of texts")
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            raise EmbeddingError(f"Failed to embed batch: {e}")

    @property
    def dimension(self) -> int:
        """Embedding dimension.

        Returns:
            Number of dimensions in the embedding vector.
        """
        return self._dimension
