"""Qdrant vector store provider."""

import json
import logging
from typing import Any, Dict, List, Optional

from ..exceptions import VectorStoreError
from ..models import Chunk, SearchResult
from .base import BaseVectorStore

logger = logging.getLogger(__name__)


class QdrantVectorStore(BaseVectorStore):
    """Qdrant vector store provider.

    Uses Qdrant for vector storage and retrieval.
    Supports both local and remote Qdrant instances.
    """

    def __init__(
        self,
        collection_name: str = "socratic_rag",
        host: str = "localhost",
        port: int = 6333,
        memory_mode: bool = True,
        path: Optional[str] = None,
    ) -> None:
        """Initialize Qdrant vector store.

        Args:
            collection_name: Name of the collection.
            host: Qdrant server host.
            port: Qdrant server port.
            memory_mode: If True and path is set, uses local in-memory storage.
            path: Path for local Qdrant instance.

        Raises:
            VectorStoreError: If initialization fails.
        """
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http.models import Distance, VectorParams

            self.collection_name = collection_name
            self.Distance = Distance
            self.VectorParams = VectorParams

            if path:
                self.client = QdrantClient(path=path)
            else:
                self.client = QdrantClient(host=host, port=port)

            self._dimension: Optional[int] = None

        except ImportError:
            raise VectorStoreError(
                "qdrant-client is required for QdrantVectorStore. "
                "Install with: pip install qdrant-client"
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize Qdrant: {e}")

    def _ensure_collection(self, vector_size: int) -> None:
        """Ensure collection exists with proper configuration.

        Args:
            vector_size: Size of vectors to store.

        Raises:
            VectorStoreError: If collection creation fails.
        """
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=self.VectorParams(
                        size=vector_size,
                        distance=self.Distance.COSINE,
                    ),
                )
                self._dimension = vector_size
        except Exception as e:
            raise VectorStoreError(f"Failed to ensure collection: {e}")

    def add_documents(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]],
    ) -> List[str]:
        """Add chunks with embeddings to Qdrant.

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

            # Ensure collection exists
            self._ensure_collection(len(embeddings[0]))

            # Prepare points for Qdrant
            from qdrant_client.http.models import PointStruct

            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                payload = {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "source": chunk.metadata.get("source", "unknown"),
                    "chunk_metadata": json.dumps(chunk.metadata),
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                }

                points.append(
                    PointStruct(
                        id=hash(chunk.chunk_id) % (2**31),  # Convert to positive int
                        vector=embedding,
                        payload=payload,
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

            return [chunk.chunk_id for chunk in chunks]

        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents to Qdrant: {e}")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents in Qdrant.

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

            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                return []

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
            )

            search_results: List[SearchResult] = []

            for result in results:
                payload = result.payload
                chunk = Chunk(
                    text=payload["text"],
                    chunk_id=payload["chunk_id"],
                    document_id=payload["document_id"],
                    metadata=json.loads(payload["chunk_metadata"]),
                    start_char=payload["start_char"],
                    end_char=payload["end_char"],
                )

                search_results.append(SearchResult(chunk=chunk, score=result.score))

            return search_results

        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to search Qdrant: {e}")

    def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs from Qdrant.

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

            # Qdrant requires point IDs, we use hash of chunk IDs
            point_ids = [hash(id) % (2**31) for id in document_ids]

            self.client.delete(
                collection_name=self.collection_name,
                points_selector={"points": point_ids},
            )
            return True

        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents from Qdrant: {e}")

    def get(self, document_id: str) -> Optional[Chunk]:
        """Get document by ID from Qdrant.

        Args:
            document_id: ID of the chunk to retrieve.

        Returns:
            Chunk object if found, None otherwise.

        Raises:
            VectorStoreError: If retrieval fails.
        """
        try:
            point_id = hash(document_id) % (2**31)
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
            )

            if not result:
                return None

            payload = result[0].payload
            return Chunk(
                text=payload["text"],
                chunk_id=payload["chunk_id"],
                document_id=payload["document_id"],
                metadata=json.loads(payload["chunk_metadata"]),
                start_char=payload["start_char"],
                end_char=payload["end_char"],
            )

        except Exception as e:
            raise VectorStoreError(f"Failed to get document from Qdrant: {e}")

    def clear(self) -> bool:
        """Clear all documents from Qdrant collection.

        Returns:
            True if clearing was successful.

        Raises:
            VectorStoreError: If clearing fails.
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            self._dimension = None
            return True

        except Exception as e:
            raise VectorStoreError(f"Failed to clear Qdrant: {e}")
