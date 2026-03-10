"""Openclaw RAG skill integration."""

from typing import Any, Dict, List, Optional

from ...client import RAGClient
from ...models import RAGConfig


class SocraticRAGSkill:
    """Openclaw skill for RAG operations.

    Provides a unified interface for RAG operations within Openclaw framework.
    """

    def __init__(
        self,
        vector_store: str = "chromadb",
        embedder: str = "sentence-transformers",
        chunking_strategy: str = "fixed",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        top_k: int = 5,
        collection_name: str = "socratic_rag",
        **kwargs: Any,
    ) -> None:
        """Initialize Openclaw RAG skill.

        Args:
            vector_store: Vector store provider to use.
            embedder: Embedding provider to use.
            chunking_strategy: Chunking strategy to use.
            chunk_size: Size of chunks in characters.
            chunk_overlap: Overlap between chunks in characters.
            top_k: Number of results to return by default.
            collection_name: Name of the collection.
            **kwargs: Additional arguments passed to RAGConfig.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        config = RAGConfig(
            vector_store=vector_store,
            embedder=embedder,
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            top_k=top_k,
            collection_name=collection_name,
        )
        self.client = RAGClient(config)

    def add_document(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add document to knowledge base.

        Args:
            content: Document content.
            source: Document source identifier.
            metadata: Optional metadata to attach to document.

        Returns:
            Document ID.

        Raises:
            Various exceptions for processing failures.
        """
        return self.client.add_document(
            content=content,
            source=source,
            metadata=metadata,
        )

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents.

        Args:
            query: Search query.
            top_k: Number of results to return.

        Returns:
            List of dictionaries with 'text' and 'score' keys.

        Raises:
            Various exceptions for search failures.
        """
        results = self.client.search(query, top_k=top_k)

        return [
            {
                "text": r.chunk.text,
                "score": r.score,
                "document_id": r.chunk.document_id,
                "chunk_id": r.chunk.chunk_id,
                "metadata": r.chunk.metadata,
            }
            for r in results
        ]

    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> str:
        """Retrieve formatted context for LLM.

        Args:
            query: Search query.
            top_k: Number of results to return.

        Returns:
            Formatted context string suitable for LLM input.

        Raises:
            Various exceptions for retrieval failures.
        """
        return self.client.retrieve_context(query, top_k=top_k)

    def clear(self) -> bool:
        """Clear all documents from knowledge base.

        Returns:
            True if clearing was successful.

        Raises:
            Various exceptions for clearing failures.
        """
        return self.client.clear()

    def get_config(self) -> RAGConfig:
        """Get current configuration.

        Returns:
            Current RAGConfig object.
        """
        return self.client.config
