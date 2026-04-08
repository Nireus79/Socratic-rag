"""Document deduplication with semantic similarity detection."""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .embeddings.base import BaseEmbedder
from .models import Document

logger = logging.getLogger(__name__)


@dataclass
class DeduplicateResult:
    """Result of document deduplication analysis."""

    document_id: str
    is_duplicate: bool
    matched_document_id: Optional[str] = None
    similarity_score: float = 0.0
    distance_metric: str = "cosine"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DuplicateGroup:
    """Group of duplicate documents."""

    primary_id: str
    duplicate_ids: List[str]
    similarity_scores: Dict[str, float]
    group_size: int = 0

    def __post_init__(self) -> None:
        """Calculate group size."""
        self.group_size = len(self.duplicate_ids) + 1


class DocumentDeduplicator:
    """Detects and manages duplicate documents using semantic similarity."""

    def __init__(
        self,
        embedder: BaseEmbedder,
        similarity_threshold: float = 0.95,
        distance_metric: str = "cosine",
    ):
        """
        Initialize document deduplicator.

        Args:
            embedder: Embedding model for computing document vectors
            similarity_threshold: Threshold for marking documents as duplicates (0-1)
            distance_metric: Distance metric ('cosine', 'euclidean', 'manhattan')
        """
        self.embedder = embedder
        self.similarity_threshold = similarity_threshold
        self.distance_metric = distance_metric
        self.logger = logging.getLogger(__name__)

        if not 0 < similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be between 0 and 1")

        if distance_metric not in ("cosine", "euclidean", "manhattan"):
            raise ValueError(
                "Invalid distance_metric. Must be 'cosine', 'euclidean', or 'manhattan'"
            )

    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float],
    ) -> float:
        """
        Compute similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1 for cosine, higher values for distance metrics)
        """
        try:
            if self.distance_metric == "cosine":
                return self._cosine_similarity(embedding1, embedding2)
            elif self.distance_metric == "euclidean":
                return self._euclidean_similarity(embedding1, embedding2)
            else:  # manhattan
                return self._manhattan_similarity(embedding1, embedding2)
        except Exception as e:
            self.logger.error(f"Error computing similarity: {e}")
            return 0.0

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    @staticmethod
    def _euclidean_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute euclidean distance (inverted for similarity)."""
        distance = sum((a - b) ** 2 for a, b in zip(vec1, vec2)) ** 0.5
        # Invert distance to similarity (closer = higher similarity)
        return 1.0 / (1.0 + distance)

    @staticmethod
    def _manhattan_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute manhattan distance (inverted for similarity)."""
        distance = sum(abs(a - b) for a, b in zip(vec1, vec2))
        # Invert distance to similarity (closer = higher similarity)
        return 1.0 / (1.0 + distance)

    async def find_duplicates(
        self,
        documents: List[Document],
    ) -> List[DeduplicateResult]:
        """
        Find duplicate documents in a list.

        Args:
            documents: List of documents to analyze

        Returns:
            List of deduplication results
        """
        if not documents:
            return []

        results = []

        # Compute embeddings for all documents
        embeddings = []
        for doc in documents:
            try:
                embedding = await self.embedder.embed_text(doc.content)
                embeddings.append(embedding)
            except Exception as e:
                self.logger.error(f"Error embedding document {doc.document_id}: {e}")
                embeddings.append(None)

        # Compare each document with others
        for i, doc_i in enumerate(documents):
            if embeddings[i] is None:
                continue

            is_duplicate = False
            best_match_id = None
            best_similarity = 0.0

            for j, doc_j in enumerate(documents):
                if i >= j or embeddings[j] is None:
                    continue

                similarity = self.compute_similarity(embeddings[i], embeddings[j])

                if similarity >= self.similarity_threshold:
                    is_duplicate = True
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match_id = doc_j.document_id

            result = DeduplicateResult(
                document_id=doc_i.document_id,
                is_duplicate=is_duplicate,
                matched_document_id=best_match_id,
                similarity_score=best_similarity,
                distance_metric=self.distance_metric,
                metadata={
                    "source": doc_i.source,
                    "content_length": len(doc_i.content),
                },
            )
            results.append(result)

        return results

    async def deduplicate_batch(
        self,
        documents: List[Document],
        keep_strategy: str = "first",
    ) -> Tuple[List[Document], List[DuplicateGroup]]:
        """
        Remove duplicate documents from a batch.

        Args:
            documents: List of documents to deduplicate
            keep_strategy: Strategy for choosing which duplicate to keep ('first', 'longest', 'latest')

        Returns:
            Tuple of (deduplicated documents, duplicate groups)
        """
        if keep_strategy not in ("first", "longest", "latest"):
            raise ValueError("keep_strategy must be 'first', 'longest', or 'latest'")

        # Find duplicates
        dedup_results = await self.find_duplicates(documents)

        # Build duplicate groups
        groups_dict: Dict[str, DuplicateGroup] = {}
        processed = set()

        for result in dedup_results:
            if result.is_duplicate and result.matched_document_id:
                primary_id = result.matched_document_id
                dup_id = result.document_id

                if primary_id in processed:
                    continue

                if primary_id not in groups_dict:
                    groups_dict[primary_id] = DuplicateGroup(
                        primary_id=primary_id,
                        duplicate_ids=[],
                        similarity_scores={},
                    )

                groups_dict[primary_id].duplicate_ids.append(dup_id)
                groups_dict[primary_id].similarity_scores[dup_id] = result.similarity_score
                processed.add(dup_id)

        # Select which documents to keep
        doc_by_id = {doc.document_id: doc for doc in documents}
        kept_ids = set()

        for doc in documents:
            if doc.document_id not in processed:
                kept_ids.add(doc.document_id)
            elif doc.document_id in [g.primary_id for g in groups_dict.values()]:
                kept_ids.add(doc.document_id)

        # Apply keep strategy for duplicates
        for group in groups_dict.values():
            dup_docs = [doc_by_id[dup_id] for dup_id in group.duplicate_ids if dup_id in doc_by_id]

            if keep_strategy == "longest":
                primary = max(dup_docs, key=lambda d: len(d.content))
                kept_ids.add(primary.document_id)
            elif keep_strategy == "latest":
                primary = max(dup_docs, key=lambda d: d.created_at)
                kept_ids.add(primary.document_id)
            # 'first' strategy keeps the primary by default

        deduplicated = [doc for doc in documents if doc.document_id in kept_ids]
        groups = list(groups_dict.values())

        self.logger.info(
            f"Deduplicated {len(documents)} documents -> {len(deduplicated)} unique documents. "
            f"Found {len(groups)} duplicate groups."
        )

        return deduplicated, groups

    def get_similarity_matrix(
        self,
        embeddings: List[List[float]],
    ) -> List[List[float]]:
        """
        Compute pairwise similarity matrix for embeddings.

        Args:
            embeddings: List of embedding vectors

        Returns:
            2D list of similarity scores
        """
        n = len(embeddings)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i, n):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    similarity = self.compute_similarity(embeddings[i], embeddings[j])
                    matrix[i][j] = similarity
                    matrix[j][i] = similarity

        return matrix
