"""Custom exceptions for Socratic RAG."""


class SocraticRAGError(Exception):
    """Base exception for Socratic RAG."""

    pass


class ConfigurationError(SocraticRAGError):
    """Raised when configuration is invalid."""

    pass


class VectorStoreError(SocraticRAGError):
    """Raised when vector store operation fails."""

    pass


class EmbeddingError(SocraticRAGError):
    """Raised when embedding operation fails."""

    pass


class ChunkingError(SocraticRAGError):
    """Raised when chunking operation fails."""

    pass


class ProcessorError(SocraticRAGError):
    """Raised when document processing fails."""

    pass


class DocumentNotFoundError(VectorStoreError):
    """Raised when document is not found."""

    pass


class ProviderNotFoundError(ConfigurationError):
    """Raised when provider is not found."""

    pass


class InvalidProviderError(ConfigurationError):
    """Raised when provider configuration is invalid."""

    pass


class AsyncRAGError(SocraticRAGError):
    """Raised when async operation fails."""

    pass
