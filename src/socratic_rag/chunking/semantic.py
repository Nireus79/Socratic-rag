"""Semantic chunking strategy - preserves sentence and paragraph boundaries."""

import logging
from typing import Any, Dict, List, Optional

from ..exceptions import ChunkingError
from ..models import Chunk
from .base import BaseChunker

logger = logging.getLogger(__name__)


class SemanticChunker(BaseChunker):
    """
    Semantic chunking strategy.

    Preserves semantic boundaries by splitting on sentences/paragraphs
    rather than fixed character positions. Ensures chunks don't break
    in the middle of sentences or ideas.
    """

    def __init__(
        self,
        target_chunk_size: int = 512,
        min_chunk_size: int = 100,
        max_chunk_size: int = 1024,
    ) -> None:
        """
        Initialize semantic chunker.

        Args:
            target_chunk_size: Target size for chunks (soft limit)
            min_chunk_size: Minimum chunk size (hard limit)
            max_chunk_size: Maximum chunk size (hard limit)

        Raises:
            ChunkingError: If parameters are invalid
        """
        if target_chunk_size <= 0:
            raise ChunkingError("target_chunk_size must be positive")
        if min_chunk_size <= 0:
            raise ChunkingError("min_chunk_size must be positive")
        if max_chunk_size <= 0:
            raise ChunkingError("max_chunk_size must be positive")
        if min_chunk_size > target_chunk_size:
            raise ChunkingError("min_chunk_size cannot exceed target_chunk_size")
        if target_chunk_size > max_chunk_size:
            raise ChunkingError("target_chunk_size cannot exceed max_chunk_size")

        self.target_chunk_size = target_chunk_size
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences

        Note:
            Simple sentence splitting on period/question/exclamation.
            For production, consider nltk or spacy for better accuracy.
        """
        import re

        # Split on sentence boundaries
        # Handles: . ! ? followed by space and capital letter
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.

        Args:
            text: Text to split

        Returns:
            List of paragraphs
        """
        paragraphs = text.split("\n\n")
        return [p.strip() for p in paragraphs if p.strip()]

    def chunk(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """
        Split text into semantic chunks.

        Preserves sentence and paragraph boundaries to maintain semantic meaning.

        Args:
            text: Text to chunk
            document_id: ID of the document
            metadata: Optional metadata to attach to chunks

        Returns:
            List of Chunk objects

        Raises:
            ChunkingError: If chunking fails
        """
        try:
            if not text:
                raise ChunkingError("Cannot chunk empty text")

            chunks: List[Chunk] = []

            # First split by paragraphs
            paragraphs = self._split_into_paragraphs(text)

            current_chunk = ""
            current_start = 0
            char_position = 0

            for para_idx, paragraph in enumerate(paragraphs):
                # Split paragraph into sentences
                sentences = self._split_into_sentences(paragraph)

                for sentence in sentences:
                    # Check if adding this sentence would exceed max_chunk_size
                    sentence_with_space = sentence if not current_chunk else " " + sentence
                    potential_chunk = current_chunk + sentence_with_space

                    if len(potential_chunk) > self.max_chunk_size:
                        # Current chunk is full, save it and start new one
                        if current_chunk:
                            chunk = Chunk.create(
                                text=current_chunk.strip(),
                                document_id=document_id,
                                metadata=metadata,
                                start_char=current_start,
                                end_char=char_position,
                            )
                            chunks.append(chunk)
                            logger.debug(f"Created semantic chunk: {len(current_chunk)} chars")

                        # Start new chunk with current sentence
                        current_chunk = sentence
                        current_start = char_position
                    else:
                        # Add sentence to current chunk
                        current_chunk += sentence_with_space

                    # Update position
                    char_position += len(sentence_with_space)

                # Add paragraph break (unless this is the last paragraph)
                if para_idx < len(paragraphs) - 1:
                    current_chunk += "\n\n"
                    char_position += 2

            # Save final chunk
            if current_chunk:
                chunk = Chunk.create(
                    text=current_chunk.strip(),
                    document_id=document_id,
                    metadata=metadata,
                    start_char=current_start,
                    end_char=char_position,
                )
                chunks.append(chunk)
                logger.debug(f"Created semantic chunk: {len(current_chunk)} chars")

            # Ensure minimum size (merge small chunks if needed)
            chunks = self._merge_small_chunks(chunks, document_id, metadata)

            return chunks

        except ChunkingError:
            raise
        except Exception as e:
            logger.error(f"Semantic chunking failed: {e}", exc_info=True)
            raise ChunkingError(f"Semantic chunking failed: {str(e)}")

    def _merge_small_chunks(
        self,
        chunks: List[Chunk],
        document_id: str,
        metadata: Optional[Dict[str, Any]],
    ) -> List[Chunk]:
        """
        Merge chunks that are smaller than min_chunk_size.

        Args:
            chunks: List of chunks to process
            document_id: Document ID
            metadata: Metadata dict

        Returns:
            List of chunks with small ones merged
        """
        if not chunks:
            return chunks

        merged = []
        current = None

        for chunk in chunks:
            if current is None:
                current = chunk
            elif len(current.text) < self.min_chunk_size:
                # Merge current with next chunk
                merged_text = current.text + "\n\n" + chunk.text
                current = Chunk(
                    text=merged_text,
                    chunk_id=current.chunk_id,
                    document_id=current.document_id,
                    metadata=current.metadata or {},
                    start_char=current.start_char,
                    end_char=chunk.end_char,
                )
            else:
                # Current chunk is large enough, save it
                merged.append(current)
                current = chunk

        if current is not None:
            merged.append(current)

        return merged


class SlidingWindowChunker(BaseChunker):
    """
    Sliding window chunking strategy.

    Creates overlapping chunks using a sliding window approach,
    useful for maintaining context between chunks.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        step_size: int = 256,
        min_overlap: int = 50,
    ) -> None:
        """
        Initialize sliding window chunker.

        Args:
            chunk_size: Size of each window
            step_size: How far to slide window (smaller = more overlap)
            min_overlap: Minimum overlap between chunks

        Raises:
            ChunkingError: If parameters are invalid
        """
        if chunk_size <= 0:
            raise ChunkingError("chunk_size must be positive")
        if step_size <= 0:
            raise ChunkingError("step_size must be positive")
        if step_size >= chunk_size:
            raise ChunkingError("step_size must be less than chunk_size")

        self.chunk_size = chunk_size
        self.step_size = step_size
        self.min_overlap = min_overlap

    def chunk(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """
        Split text using sliding window strategy.

        Args:
            text: Text to chunk
            document_id: ID of the document
            metadata: Optional metadata to attach to chunks

        Returns:
            List of Chunk objects

        Raises:
            ChunkingError: If chunking fails
        """
        try:
            if not text:
                raise ChunkingError("Cannot chunk empty text")

            chunks: List[Chunk] = []
            start = 0

            while start < len(text):
                # Calculate end position
                end = min(start + self.chunk_size, len(text))
                chunk_text = text[start:end]

                # Create chunk
                chunk = Chunk.create(
                    text=chunk_text,
                    document_id=document_id,
                    metadata=metadata,
                    start_char=start,
                    end_char=end,
                )
                chunks.append(chunk)

                # Move window by step_size
                start += self.step_size

                # Avoid creating tiny final chunks
                if len(text) - start < self.min_overlap:
                    break

            return chunks

        except ChunkingError:
            raise
        except Exception as e:
            logger.error(f"Sliding window chunking failed: {e}", exc_info=True)
            raise ChunkingError(f"Sliding window chunking failed: {str(e)}")
