"""Fixed-size chunking strategy."""

import logging
from typing import List

from ..exceptions import ChunkingError
from ..models import Chunk
from .base import BaseChunker

logger = logging.getLogger(__name__)


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
            raise ChunkingError(f"chunk_size must be positive, got {chunk_size}")
        if overlap < 0 or overlap >= chunk_size:
            raise ChunkingError(f"overlap must be between 0 and chunk_size, got {overlap}")

        self.chunk_size = chunk_size
        self.overlap = overlap

    async def chunk(self, text: str) -> List[Chunk]:
        """Split text into fixed-size chunks.

        Args:
            text: Text to split

        Returns:
            List of Chunk objects
        """
        if not text:
            return []

        chunks = []
        step = self.chunk_size - self.overlap

        for i in range(0, len(text), step):
            chunk_text = text[i : i + self.chunk_size]
            if chunk_text.strip():
                chunks.append(Chunk(content=chunk_text, metadata={"start": i}))

        return chunks
