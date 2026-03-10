"""Abstract base classes for vector store providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models import Chunk, SearchResult


class BaseVectorStore(ABC):
    """Abstract base for vector database providers."""

    @abstractmethod
    def add_documents(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]],
    ) -> List[str]:
        """Add chunks with embeddings to the vector store.

        Args:
            chunks: List of Chunk objects.
            embeddings: List of embeddings corresponding to chunks.

        Returns:
            List of document IDs that were added.

        Raises:
            VectorStoreError: If addition fails.
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents.

        Args:
            query_embedding: Embedding of the query.
            top_k: Number of results to return.
            filters: Optional metadata filters.

        Returns:
            List of SearchResult objects ordered by relevance.

        Raises:
            VectorStoreError: If search fails.
        """
        pass

    @abstractmethod
    def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs.

        Args:
            document_ids: List of document IDs to delete.

        Returns:
            True if deletion was successful.

        Raises:
            VectorStoreError: If deletion fails.
        """
        pass

    @abstractmethod
    def get(self, document_id: str) -> Optional[Chunk]:
        """Get document by ID.

        Args:
            document_id: ID of the document to retrieve.

        Returns:
            Chunk object if found, None otherwise.

        Raises:
            VectorStoreError: If retrieval fails.
        """
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all documents from the vector store.

        Returns:
            True if clearing was successful.

        Raises:
            VectorStoreError: If clearing fails.
        """
        pass
