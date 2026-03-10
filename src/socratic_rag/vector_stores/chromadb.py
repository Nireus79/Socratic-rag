"""ChromaDB vector store provider."""

from typing import Any, Dict, List, Optional
import json
from .base import BaseVectorStore
from ..models import Chunk, SearchResult
from ..exceptions import VectorStoreError


class ChromaDBVectorStore(BaseVectorStore):
    """ChromaDB vector store provider.

    Uses Chroma for vector storage and retrieval.
    Supports both in-memory and persistent storage.
    """

    def __init__(
        self,
        collection_name: str = "socratic_rag",
        persist_directory: Optional[str] = None,
    ) -> None:
        """Initialize ChromaDB vector store.

        Args:
            collection_name: Name of the collection.
            persist_directory: Directory for persistent storage.
                If None, uses in-memory storage.

        Raises:
            VectorStoreError: If initialization fails.
        """
        try:
            import chromadb
            from chromadb.config import Settings

            self.collection_name = collection_name
            self.persist_directory = persist_directory

            if persist_directory:
                settings = Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=persist_directory,
                    anonymized_telemetry=False,
                )
                self.client = chromadb.Client(settings)
            else:
                self.client = chromadb.Client()

            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )

        except ImportError:
            raise VectorStoreError(
                "chromadb is required for ChromaDBVectorStore. "
                "Install with: pip install chromadb"
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize ChromaDB: {e}")

    def add_documents(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]],
    ) -> List[str]:
        """Add chunks with embeddings to ChromaDB.

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

            # Prepare data for ChromaDB
            ids = [chunk.chunk_id for chunk in chunks]
            texts = [chunk.text for chunk in chunks]
            metadatas = [
                {
                    "document_id": chunk.document_id,
                    "source": chunk.metadata.get("source", "unknown"),
                    "chunk_metadata": json.dumps(chunk.metadata),
                    "start_char": str(chunk.start_char),
                    "end_char": str(chunk.end_char),
                }
                for chunk in chunks
            ]

            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )

            return ids

        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents to ChromaDB: {e}")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents in ChromaDB.

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

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters,
            )

            search_results: List[SearchResult] = []

            if not results["ids"] or not results["ids"][0]:
                return search_results

            for i, chunk_id in enumerate(results["ids"][0]):
                text = results["documents"][0][i]
                distance = results["distances"][0][i]
                metadata = results["metadatas"][0][i]

                # Convert distance to similarity score
                # ChromaDB returns distances, convert to similarity (0-1)
                score = 1 / (1 + distance)

                # Reconstruct chunk
                chunk = Chunk(
                    text=text,
                    chunk_id=chunk_id,
                    document_id=metadata["document_id"],
                    metadata=json.loads(metadata["chunk_metadata"]),
                    start_char=int(metadata["start_char"]),
                    end_char=int(metadata["end_char"]),
                )

                search_results.append(SearchResult(chunk=chunk, score=score))

            return search_results

        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to search ChromaDB: {e}")

    def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs from ChromaDB.

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

            self.collection.delete(ids=document_ids)
            return True

        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents from ChromaDB: {e}")

    def get(self, document_id: str) -> Optional[Chunk]:
        """Get document by ID from ChromaDB.

        Args:
            document_id: ID of the chunk to retrieve.

        Returns:
            Chunk object if found, None otherwise.

        Raises:
            VectorStoreError: If retrieval fails.
        """
        try:
            result = self.collection.get(ids=[document_id])

            if not result["ids"] or not result["ids"]:
                return None

            metadata = result["metadatas"][0]
            return Chunk(
                text=result["documents"][0],
                chunk_id=document_id,
                document_id=metadata["document_id"],
                metadata=json.loads(metadata["chunk_metadata"]),
                start_char=int(metadata["start_char"]),
                end_char=int(metadata["end_char"]),
            )

        except Exception as e:
            raise VectorStoreError(f"Failed to get document from ChromaDB: {e}")

    def clear(self) -> bool:
        """Clear all documents from ChromaDB collection.

        Returns:
            True if clearing was successful.

        Raises:
            VectorStoreError: If clearing fails.
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            return True

        except Exception as e:
            raise VectorStoreError(f"Failed to clear ChromaDB: {e}")
