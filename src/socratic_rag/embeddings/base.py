"""Abstract base classes for embedding providers."""

from abc import ABC, abstractmethod
from typing import List


class BaseEmbedder(ABC):
    """Abstract base for embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed.

        Returns:
            List of floats representing the embedding.

        Raises:
            EmbeddingError: If embedding fails.
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embeddings, one for each input text.

        Raises:
            EmbeddingError: If embedding fails.
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding dimension.

        Returns:
            Number of dimensions in the embedding vector.
        """
        pass
