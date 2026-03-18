"""
Embedding Cache - LRU cache for text embeddings.

Caches embedding vectors to avoid redundant encoding operations.
Typical speedup: 100x improvement for cached embeddings.
"""

import hashlib
import logging
import threading
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """LRU (Least Recently Used) cache for text embeddings."""

    def __init__(self, max_size: int = 10000):
        """
        Initialize embedding cache.

        Args:
            max_size: Maximum number of embeddings to cache (default: 10000)
        """
        self._cache: Dict[str, List[float]] = {}
        self._access_order: List[str] = []
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._lock = threading.RLock()
        logger.debug(f"EmbeddingCache initialized with max_size={max_size}")

    def get(self, text: str) -> Optional[List[float]]:
        """Retrieve cached embedding for text."""
        text_hash = self._hash_text(text)

        with self._lock:
            if text_hash in self._cache:
                self._access_order.remove(text_hash)
                self._access_order.append(text_hash)
                self._hits += 1
                return self._cache[text_hash]

            self._misses += 1
            return None

    def put(self, text: str, embedding: List[float]) -> None:
        """Store embedding in cache."""
        text_hash = self._hash_text(text)

        with self._lock:
            if len(self._cache) >= self._max_size:
                if self._access_order:
                    oldest = self._access_order.pop(0)
                    del self._cache[oldest]
                    logger.debug("Evicted oldest embedding from cache")

            if text_hash in self._cache:
                self._access_order.remove(text_hash)

            self._cache[text_hash] = embedding
            self._access_order.append(text_hash)

    def stats(self) -> Dict[str, any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "total_calls": total,
                "hit_rate": f"{hit_rate:.1f}%",
                "cache_size": len(self._cache),
                "max_size": self._max_size,
            }

    def clear(self) -> None:
        """Clear all cached embeddings."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            logger.info("EmbeddingCache cleared")

    @staticmethod
    def _hash_text(text: str) -> str:
        """Generate hash key for text."""
        return hashlib.sha256(text.encode()).hexdigest()
