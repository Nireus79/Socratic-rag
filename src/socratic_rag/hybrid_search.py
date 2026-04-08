"""Hybrid search implementation for socratic-rag."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from hybrid search."""

    content: str
    score: float
    source: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize metadata."""
        if self.metadata is None:
            self.metadata = {}


class HybridSearcher:
    """Hybrid search combining semantic and keyword approaches."""

    def __init__(self, semantic_weight: float = 0.7, keyword_weight: float = 0.3):
        """Initialize hybrid searcher.

        Args:
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword match (0-1)
        """
        if not (0 <= semantic_weight <= 1) or not (0 <= keyword_weight <= 1):
            raise ValueError("Weights must be between 0 and 1")

        total_weight = semantic_weight + keyword_weight
        self.semantic_weight = semantic_weight / total_weight
        self.keyword_weight = keyword_weight / total_weight
        self.tfidf = None

    def prepare_documents(self, documents: List[str]) -> None:
        """Prepare documents for hybrid search.

        Args:
            documents: List of document texts
        """
        self.tfidf = TfidfVectorizer(max_features=500)
        self.tfidf.fit(documents)

    def hybrid_search(
        self,
        query: str,
        semantic_scores: List[float],
        documents: List[str],
        top_k: int = 5,
    ) -> List[SearchResult]:
        """Perform hybrid search combining semantic and keyword scores.

        Args:
            query: Query text
            semantic_scores: Semantic similarity scores
            documents: Document texts
            top_k: Number of top results to return

        Returns:
            List of SearchResult objects
        """
        if self.tfidf is None:
            self.prepare_documents(documents)

        # Compute TF-IDF scores
        query_tfidf = self.tfidf.transform([query])
        doc_tfidf = self.tfidf.transform(documents)
        keyword_scores = cosine_similarity(query_tfidf, doc_tfidf)[0]

        # Combine scores
        combined_scores = (
            self.semantic_weight * np.array(semantic_scores) + self.keyword_weight * keyword_scores
        )

        # Get top k indices
        top_indices = np.argsort(combined_scores)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append(
                SearchResult(
                    content=documents[idx],
                    score=float(combined_scores[idx]),
                    source="hybrid",
                )
            )

        return results
