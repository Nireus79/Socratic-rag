"""Abstract base classes for chunking strategies."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models import Chunk


class BaseChunker(ABC):
    """Abstract base for chunking strategies."""

    @abstractmethod
    def chunk(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """Split text into chunks.

        Args:
            text: Text to chunk.
            document_id: ID of the document.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.

        Raises:
            ChunkingError: If chunking fails.
        """
        pass
