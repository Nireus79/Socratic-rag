"""
Caching Module

Performance optimization caches for RAG systems:
- EmbeddingCache: LRU cache for text embeddings (100x speedup)
- SearchResultCache: TTL-based cache for search results (20x speedup)
"""

from socratic_rag.caching.embedding_cache import EmbeddingCache
from socratic_rag.caching.search_cache import SearchResultCache

__all__ = [
    "EmbeddingCache",
    "SearchResultCache",
]
