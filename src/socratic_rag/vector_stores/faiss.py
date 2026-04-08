"""FAISS vector store provider."""

import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..exceptions import VectorStoreError
from ..models import Chunk, SearchResult
from .base import BaseVectorStore

logger = logging.getLogger(__name__)



class FAISSVectorStore(BaseVectorStore):
    """FAISS vector store provider.

    Uses Facebook's FAISS library for vector storage and retrieval.
    Supports both in-memory and file-based persistence.
    """

    def __init__(
        self,
        collection_name: str = "socratic_rag",
        persist_directory: Optional[str] = None,
    ) -> None:
        """Initialize FAISS vector store.

        Args:
            collection_name: Name of the collection.
            persist_directory: Directory for persistent storage.
                If None, uses in-memory storage.

        Raises:
            VectorStoreError: If initialization fails.
        """
        try:
            import faiss
            import numpy as np

            self.faiss = faiss
            self.np = np
            self.collection_name = collection_name
            self.persist_directory = Path(persist_directory) if persist_directory else None

            self.index: Optional[Any] = None
            self.chunks: Dict[int, Chunk] = {}
            self.next_id = 0

            if self.persist_directory:
                self.persist_directory.mkdir(parents=True, exist_ok=True)

        except ImportError:
            raise VectorStoreError(
                "faiss-cpu is required for FAISSVectorStore. " "Install with: pip install faiss-cpu"
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize FAISS: {e}")

    def _create_index(self, vector_size: int) -> None:
        """Create FAISS index with given vector size.

        Args:
            vector_size: Size of vectors.

        Raises:
            VectorStoreError: If index creation fails.
        """
        try:
            self.index = self.faiss.IndexFlatL2(vector_size)
        except Exception as e:
            raise VectorStoreError(f"Failed to create FAISS index: {e}")

    def _save_metadata(self) -> None:
        """Save chunks metadata to disk.

        Raises:
            VectorStoreError: If saving fails.
        """
        if not self.persist_directory:
            return

        try:
            metadata_path = self.persist_directory / f"{self.collection_name}_metadata.pkl"
            with open(metadata_path, "wb") as f:
                pickle.dump(
                    {"chunks": self.chunks, "next_id": self.next_id},
                    f,
                )
        except Exception as e:
            raise VectorStoreError(f"Failed to save metadata: {e}")

    def _load_metadata(self) -> None:
        """Load chunks metadata from disk.

        Raises:
            VectorStoreError: If loading fails.
        """
        if not self.persist_directory:
            return

        try:
            metadata_path = self.persist_directory / f"{self.collection_name}_metadata.pkl"
            if metadata_path.exists():
                with open(metadata_path, "rb") as f:
                    data = pickle.load(f)
                    self.chunks = data["chunks"]
                    self.next_id = data["next_id"]
        except Exception as e:
            raise VectorStoreError(f"Failed to load metadata: {e}")

    def _save_index(self) -> None:
        """Save FAISS index to disk.

        Raises:
            VectorStoreError: If saving fails.
        """
        if not self.persist_directory or not self.index:
            return

        try:
            index_path = self.persist_directory / f"{self.collection_name}.faiss"
            self.faiss.write_index(self.index, str(index_path))
        except Exception as e:
            raise VectorStoreError(f"Failed to save FAISS index: {e}")

    def _load_index(self, vector_size: int) -> None:
        """Load FAISS index from disk.

        Args:
            vector_size: Size of vectors.

        Raises:
            VectorStoreError: If loading fails.
        """
        if not self.persist_directory:
            return

        try:
            index_path = self.persist_directory / f"{self.collection_name}.faiss"
            if index_path.exists():
                self.index = self.faiss.read_index(str(index_path))
            else:
                self._create_index(vector_size)
        except Exception as e:
            raise VectorStoreError(f"Failed to load FAISS index: {e}")

    def add_documents(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]],
    ) -> List[str]:
        """Add chunks with embeddings to FAISS.

        Args:
            chunks: List of Chunk objects.
            embeddings: List of embeddings corresponding to chunks.

        Returns:
            List of chunk IDs that were added.

        Raises:
            VectorStoreError: If addition fails.
        """
        try:
            if len(chunks) != len(embeddings):
                raise VectorStoreError(
                    f"Number of chunks ({len(chunks)}) must match "
                    f"number of embeddings ({len(embeddings)})"
                )

            if not chunks:
                return []

            # Create index if needed
            vector_size = len(embeddings[0])
            if self.index is None:
                self._load_index(vector_size)
                self._load_metadata()

            # Index should be created now
            if self.index is None:
                raise VectorStoreError("Failed to create or load FAISS index")

            # Convert embeddings to numpy array (FAISS expects float32)
            embeddings_array = self.np.array(embeddings, dtype=self.np.float32)

            # Add embeddings to index
            self.index.add(embeddings_array)

            # Store chunk metadata
            chunk_ids = []
            for chunk in chunks:
                self.chunks[self.next_id] = chunk
                chunk_ids.append(chunk.chunk_id)
                self.next_id += 1

            # Persist
            self._save_index()
            self._save_metadata()

            return chunk_ids

        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents to FAISS: {e}")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents in FAISS.

        Args:
            query_embedding: Embedding of the query.
            top_k: Number of results to return.
            filters: Optional metadata filters (not fully supported in v0.1.0).

        Returns:
            List of SearchResult objects ordered by relevance.

        Raises:
            VectorStoreError: If search fails.
        """
        try:
            if top_k <= 0:
                raise VectorStoreError("top_k must be positive")

            if self.index is None:
                return []

            # Convert query to numpy array
            query_array = self.np.array([query_embedding], dtype=self.np.float32)

            # Search
            distances, indices = self.index.search(query_array, min(top_k, self.index.ntotal))

            search_results: List[SearchResult] = []

            for i, idx in enumerate(indices[0]):
                if idx == -1:  # Invalid result
                    continue

                chunk = self.chunks[idx]
                # Convert L2 distance to similarity score
                distance = float(distances[0][i])
                score = 1 / (1 + distance)

                search_results.append(SearchResult(chunk=chunk, score=score))

            return search_results

        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to search FAISS: {e}")

    def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs from FAISS.

        Note: FAISS doesn't support deletion directly. This implementation
        marks chunks as deleted by removing them from the metadata.

        Args:
            document_ids: List of chunk IDs to delete.

        Returns:
            True if deletion was successful.

        Raises:
            VectorStoreError: If deletion fails.
        """
        try:
            if not document_ids:
                return True

            # Remove from chunks dictionary
            ids_to_remove = [
                idx for idx, chunk in self.chunks.items() if chunk.chunk_id in document_ids
            ]

            for idx in ids_to_remove:
                del self.chunks[idx]

            self._save_metadata()
            return True

        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents from FAISS: {e}")

    def get(self, document_id: str) -> Optional[Chunk]:
        """Get document by ID from FAISS.

        Args:
            document_id: ID of the chunk to retrieve.

        Returns:
            Chunk object if found, None otherwise.

        Raises:
            VectorStoreError: If retrieval fails.
        """
        try:
            for chunk in self.chunks.values():
                if chunk.chunk_id == document_id:
                    return chunk
            return None

        except Exception as e:
            raise VectorStoreError(f"Failed to get document from FAISS: {e}")

    def clear(self) -> bool:
        """Clear all documents from FAISS.

        Returns:
            True if clearing was successful.

        Raises:
            VectorStoreError: If clearing fails.
        """
        try:
            self.index = None
            self.chunks = {}
            self.next_id = 0

            # Remove persisted files
            if self.persist_directory:
                index_path = self.persist_directory / f"{self.collection_name}.faiss"
                metadata_path = self.persist_directory / f"{self.collection_name}_metadata.pkl"

                if index_path.exists():
                    index_path.unlink()
                if metadata_path.exists():
                    metadata_path.unlink()

            return True

        except Exception as e:
            raise VectorStoreError(f"Failed to clear FAISS: {e}")
