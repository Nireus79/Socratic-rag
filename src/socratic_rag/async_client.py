"""Async RAG client interface."""

import asyncio
from typing import Any, Dict, List, Optional
from .models import Document, RAGConfig, SearchResult
from .client import RAGClient


class AsyncRAGClient:
    """Async RAG client interface.

    Provides async/await interface for RAG operations.
    Wraps the synchronous RAGClient for async usage.
    """

    def __init__(self, config: Optional[RAGConfig] = None) -> None:
        """Initialize async RAG client.

        Args:
            config: RAGConfig object. If None, uses default configuration.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        self.client = RAGClient(config)
        self.config = self.client.config

    async def add_document(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add document to knowledge base asynchronously.

        Args:
            content: Document content.
            source: Document source (e.g., filename, URL).
            metadata: Optional metadata to attach to document.

        Returns:
            Document ID.

        Raises:
            Various exceptions for processing failures.
        """
        return await asyncio.to_thread(
            self.client.add_document,
            content,
            source,
            metadata,
        )

    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for relevant documents asynchronously.

        Args:
            query: Search query.
            top_k: Number of results to return. If None, uses config.top_k.
            filters: Optional metadata filters.

        Returns:
            List of SearchResult objects ordered by relevance.

        Raises:
            Various exceptions for search failures.
        """
        return await asyncio.to_thread(
            self.client.search,
            query,
            top_k,
            filters,
        )

    async def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> str:
        """Retrieve and format context for LLM asynchronously.

        Args:
            query: Search query.
            top_k: Number of results to return. If None, uses config.top_k.

        Returns:
            Formatted context string suitable for LLM input.

        Raises:
            Various exceptions for retrieval failures.
        """
        return await asyncio.to_thread(
            self.client.retrieve_context,
            query,
            top_k,
        )

    async def clear(self) -> bool:
        """Clear all documents from the knowledge base asynchronously.

        Returns:
            True if clearing was successful.

        Raises:
            Various exceptions for clearing failures.
        """
        return await asyncio.to_thread(self.client.clear)
