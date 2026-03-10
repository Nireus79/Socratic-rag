"""Fixed-size chunking strategy."""

from typing import Any, Dict, List, Optional
from .base import BaseChunker
from ..models import Chunk
from ..exceptions import ChunkingError


class FixedSizeChunker(BaseChunker):
    """Fixed-size chunking strategy.

    Splits text into fixed-size chunks with optional overlap.
    """

    def __init__(self, chunk_size: int = 512, overlap: int = 50) -> None:
        """Initialize the chunker.

        Args:
            chunk_size: Size of each chunk in characters.
            overlap: Number of overlapping characters between chunks.

        Raises:
            ChunkingError: If parameters are invalid.
        """
        if chunk_size <= 0:
            raise ChunkingError("chunk_size must be positive")
        if overlap >= chunk_size:
            raise ChunkingError("overlap must be less than chunk_size")
        if overlap < 0:
            raise ChunkingError("overlap cannot be negative")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """Split text into fixed-size chunks.

        Args:
            text: Text to chunk.
            document_id: ID of the document.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.

        Raises:
            ChunkingError: If chunking fails.
        """
        try:
            if not text:
                raise ChunkingError("Cannot chunk empty text")

            chunks: List[Chunk] = []
            start = 0

            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunk_text = text[start:end]

                chunk = Chunk.create(
                    text=chunk_text,
                    document_id=document_id,
                    metadata=metadata,
                    start_char=start,
                    end_char=end,
                )
                chunks.append(chunk)

                # Move start position by chunk_size - overlap
                start += self.chunk_size - self.overlap

            return chunks

        except ChunkingError:
            raise
        except Exception as e:
            raise ChunkingError(f"Failed to chunk text: {e}")
