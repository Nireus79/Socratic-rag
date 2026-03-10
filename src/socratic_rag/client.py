"""Main RAG client interface."""

from typing import Any, Dict, List, Optional
from .models import Document, RAGConfig, SearchResult
from .embeddings.base import BaseEmbedder
from .embeddings.sentence_transformers import SentenceTransformersEmbedder
from .chunking.base import BaseChunker
from .chunking.fixed_size import FixedSizeChunker
from .vector_stores.base import BaseVectorStore
from .vector_stores.chromadb import ChromaDBVectorStore
from .vector_stores.qdrant import QdrantVectorStore
from .vector_stores.faiss import FAISSVectorStore
from .exceptions import ConfigurationError, ProviderNotFoundError


class RAGClient:
    """Main RAG client interface.

    Provides a unified interface for document processing, embedding,
    chunking, and vector store operations.
    """

    def __init__(self, config: Optional[RAGConfig] = None) -> None:
        """Initialize RAG client.

        Args:
            config: RAGConfig object. If None, uses default configuration.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        self.config = config or RAGConfig()
        self._vector_store: Optional[BaseVectorStore] = None
        self._embedder: Optional[BaseEmbedder] = None
        self._chunker: Optional[BaseChunker] = None

    @property
    def vector_store(self) -> BaseVectorStore:
        """Lazy initialization of vector store.

        Returns:
            Configured vector store instance.

        Raises:
            ProviderNotFoundError: If vector store provider is not found.
        """
        if self._vector_store is None:
            self._vector_store = self._create_vector_store()
        return self._vector_store

    @property
    def embedder(self) -> BaseEmbedder:
        """Lazy initialization of embedder.

        Returns:
            Configured embedder instance.

        Raises:
            ProviderNotFoundError: If embedder provider is not found.
        """
        if self._embedder is None:
            self._embedder = self._create_embedder()
        return self._embedder

    @property
    def chunker(self) -> BaseChunker:
        """Lazy initialization of chunker.

        Returns:
            Configured chunker instance.

        Raises:
            ProviderNotFoundError: If chunker provider is not found.
        """
        if self._chunker is None:
            self._chunker = self._create_chunker()
        return self._chunker

    def _create_vector_store(self) -> BaseVectorStore:
        """Create vector store based on configuration.

        Returns:
            Vector store instance.

        Raises:
            ProviderNotFoundError: If provider is not found.
        """
        if self.config.vector_store == "chromadb":
            return ChromaDBVectorStore(
                collection_name=self.config.collection_name,
            )
        elif self.config.vector_store == "qdrant":
            return QdrantVectorStore(
                collection_name=self.config.collection_name,
            )
        elif self.config.vector_store == "faiss":
            return FAISSVectorStore(
                collection_name=self.config.collection_name,
            )
        else:
            raise ProviderNotFoundError(
                f"Vector store provider '{self.config.vector_store}' not found. "
                f"Available: chromadb, qdrant, faiss"
            )

    def _create_embedder(self) -> BaseEmbedder:
        """Create embedder based on configuration.

        Returns:
            Embedder instance.

        Raises:
            ProviderNotFoundError: If provider is not found.
        """
        if self.config.embedder == "sentence-transformers":
            return SentenceTransformersEmbedder()
        else:
            raise ProviderNotFoundError(
                f"Embedder provider '{self.config.embedder}' not found. "
                f"Available: sentence-transformers"
            )

    def _create_chunker(self) -> BaseChunker:
        """Create chunker based on configuration.

        Returns:
            Chunker instance.

        Raises:
            ProviderNotFoundError: If provider is not found.
        """
        if self.config.chunking_strategy == "fixed":
            return FixedSizeChunker(
                chunk_size=self.config.chunk_size,
                overlap=self.config.chunk_overlap,
            )
        else:
            raise ProviderNotFoundError(
                f"Chunking strategy '{self.config.chunking_strategy}' not found. "
                f"Available: fixed"
            )

    def add_document(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add document to knowledge base.

        Chunks the document, generates embeddings, and stores in vector database.

        Args:
            content: Document content.
            source: Document source (e.g., filename, URL).
            metadata: Optional metadata to attach to document.

        Returns:
            Document ID.

        Raises:
            Various exceptions for processing failures.
        """
        # Create document
        doc = Document.create(
            content=content,
            source=source,
            metadata=metadata,
        )

        # Chunk document
        chunks = self.chunker.chunk(
            text=content,
            document_id=doc.document_id,
            metadata=metadata,
        )

        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedder.embed_batch(texts)

        # Store in vector database
        self.vector_store.add_documents(chunks, embeddings)

        return doc.document_id

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for relevant documents.

        Args:
            query: Search query.
            top_k: Number of results to return. If None, uses config.top_k.
            filters: Optional metadata filters.

        Returns:
            List of SearchResult objects ordered by relevance.

        Raises:
            Various exceptions for search failures.
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_text(query)

        # Search vector store
        k = top_k or self.config.top_k
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=k,
            filters=filters,
        )

        return results

    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> str:
        """Retrieve and format context for LLM.

        Args:
            query: Search query.
            top_k: Number of results to return. If None, uses config.top_k.

        Returns:
            Formatted context string suitable for LLM input.

        Raises:
            Various exceptions for retrieval failures.
        """
        results = self.search(query, top_k=top_k)

        if not results:
            return ""

        # Format context
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{i}] {result.chunk.text}")

        return "\n\n".join(context_parts)

    def clear(self) -> bool:
        """Clear all documents from the knowledge base.

        Returns:
            True if clearing was successful.

        Raises:
            Various exceptions for clearing failures.
        """
        return self.vector_store.clear()
