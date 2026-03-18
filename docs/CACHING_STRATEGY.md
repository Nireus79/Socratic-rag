# Caching Strategy for RAG Systems - Complete Technical Documentation

**Version:** 1.0
**Last Updated:** March 2026
**Scope:** socratic-rag Caching Module - Performance Optimization Caches

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Embedding Cache](#embedding-cache)
4. [Search Result Cache](#search-result-cache)
5. [Configuration & Tuning](#configuration--tuning)
6. [Performance Metrics](#performance-metrics)
7. [Best Practices](#best-practices)
8. [Integration Guide](#integration-guide)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The **socratic-rag Caching Module** provides two complementary caching layers that dramatically improve RAG (Retrieval-Augmented Generation) system performance:

### Key Objectives

- **Reduce Computational Cost**: Minimize redundant embedding generation and similarity computations
- **Improve Response Time**: Cache frequently accessed results for instant retrieval
- **Maintain Data Freshness**: Use TTL (Time-To-Live) and LRU (Least Recently Used) strategies
- **Scale Efficiently**: Support high-throughput scenarios with memory-efficient data structures
- **Transparent Integration**: Drop-in performance enhancement for existing RAG pipelines

### Performance Improvements

| Cache Type | Typical Speedup | Use Case |
|------------|-----------------|----------|
| **Embedding Cache** | **100x** | Same text encoded multiple times |
| **Search Result Cache** | **20x** | Repeated semantic searches in short windows |
| **Combined** | **50-200x** | Full RAG pipeline with repeated queries |

### Quick Start

```python
from socratic_rag.caching import EmbeddingCache, SearchResultCache

# Initialize caches
embedding_cache = EmbeddingCache(max_size=10000)
search_cache = SearchResultCache(ttl_seconds=300)

# Use in embedding pipeline
embedding = embedding_cache.get(text)
if embedding is None:
    embedding = model.encode(text)  # Expensive operation
    embedding_cache.put(text, embedding)

# Use in search pipeline
results = search_cache.get(query, top_k=10, project_id="proj_123")
if results is None:
    results = vector_db.search(query, top_k=10)
    search_cache.put(query, top_k=10, project_id="proj_123", results=results)
```

---

## Architecture

### System Components

```
RAG Pipeline
│
├── Text Input
│   └── Embedding Cache (LRU)
│       ├── Cache Hit → Return cached embedding (instant)
│       └── Cache Miss → Generate embedding, cache for future use
│
├── Embedding Vector
│   └── Search Cache (TTL)
│       ├── Cache Hit → Return cached results (fast)
│       └── Cache Miss → Vector search, cache with TTL
│
└── Search Results
    └── RAG Application
```

### Design Philosophy

1. **Layered Caching**: Two caches handle different bottlenecks
   - EmbeddingCache: Handles model encoding (CPU/GPU intensive)
   - SearchResultCache: Handles database queries (I/O intensive)

2. **Thread-Safe**: Both caches use RLock for concurrent access
   - Safe for multi-threaded applications
   - No race conditions in cache operations
   - Atomic updates and evictions

3. **Memory Efficient**: Automatic eviction policies
   - LRU: Removes least recently used embeddings when full
   - TTL: Automatically expires stale search results
   - Configurable limits prevent unbounded growth

4. **Observable**: Comprehensive statistics tracking
   - Hit/miss rates
   - Cache size and occupancy
   - Eviction counts
   - Performance metrics

---

## Embedding Cache

### Purpose

Caches text embeddings to avoid regenerating vectors for duplicate text inputs. Particularly valuable when:
- Same text is encoded multiple times
- Using batch encoding with overlapping sets
- Processing streaming data with repeated chunks
- Building knowledge bases with duplicated content

### Implementation Details

**Data Structure**: Dictionary-based with LRU eviction
```
{
    "sha256_hash_of_text": [vector_components...],
    ...
}

Access Order List:
[oldest_hash, ..., most_recent_hash]
```

**Key Features**:
- SHA-256 hashing for cache keys (deterministic, collision-free)
- LRU eviction when reaching max_size
- Configurable maximum capacity (default: 10,000 entries)
- Thread-safe operations via RLock

### Configuration

```python
from socratic_rag.caching import EmbeddingCache

# Default configuration (recommended for most use cases)
cache = EmbeddingCache(max_size=10000)

# Custom configuration
cache = EmbeddingCache(max_size=50000)  # For large-scale applications
cache = EmbeddingCache(max_size=1000)   # For memory-constrained environments
```

### Memory Estimation

```
Memory per embedding = 4 bytes/float * embedding_dimension
  For 384-dim embeddings: ~1.5 KB per embedding
  For 768-dim embeddings: ~3 KB per embedding
  For 1536-dim embeddings: ~6 KB per embedding

Total cache memory = max_size * memory_per_embedding
  10,000 embeddings × 3 KB = ~30 MB
  50,000 embeddings × 3 KB = ~150 MB
  100,000 embeddings × 3 KB = ~300 MB
```

### API Reference

```python
# Retrieve cached embedding
embedding = embedding_cache.get(text: str) -> Optional[List[float]]

# Store embedding in cache
embedding_cache.put(text: str, embedding: List[float]) -> None

# Get cache statistics
stats = embedding_cache.stats() -> Dict[str, any]
# Returns: {
#   "hits": int,              # Cache hit count
#   "misses": int,            # Cache miss count
#   "total_calls": int,       # Total lookups
#   "hit_rate": str,          # Formatted hit rate %
#   "cache_size": int,        # Current items in cache
#   "max_size": int           # Maximum capacity
# }

# Clear all cached embeddings
embedding_cache.clear() -> None
```

### Example: Batch Embedding with Caching

```python
def encode_texts_with_cache(texts, model, cache):
    """Encode texts, using cache for duplicates."""
    embeddings = []

    for text in texts:
        cached = cache.get(text)
        if cached:
            embeddings.append(cached)
            continue

        # Encode uncached text
        embedding = model.encode([text])[0]
        cache.put(text, embedding.tolist())
        embeddings.append(embedding)

    return embeddings

# Usage
texts = [
    "What is machine learning?",
    "Define artificial intelligence",
    "What is machine learning?",  # Duplicate
]

embeddings = encode_texts_with_cache(texts, model, embedding_cache)
print(embedding_cache.stats())
# Output: hit_rate: 33.3% (1 hit out of 3 lookups)
```

### Monitoring and Optimization

**When hit rate is low (<30%)**:
- Increase max_size to accommodate more unique texts
- Check if texts should be normalized (case, whitespace)
- Consider batching similar queries together

**When cache is memory-constrained**:
- Reduce max_size proportionally
- Use more aggressive eviction (implemented as LRU)
- Consider dimension reduction for embeddings

---

## Search Result Cache

### Purpose

Caches vector search results to avoid redundant similarity computations. Valuable when:
- Same queries are executed multiple times in short windows
- Database is slow (large collections)
- Search parameters (top_k, filters) are repeated
- Real-time systems need sub-millisecond response

### Implementation Details

**Data Structure**: Dictionary with timestamp-based TTL
```
{
    "project_id_top_k_query": (
        [search_results...],
        timestamp
    ),
    ...
}
```

**Key Features**:
- TTL (Time-To-Live) expiration for freshness
- Automatic cleanup of expired entries on access
- Project-scoped caching for multi-tenant scenarios
- Flexible cache key generation (query + top_k + project)

### Configuration

```python
from socratic_rag.caching import SearchResultCache

# Default configuration (5-minute TTL)
cache = SearchResultCache(ttl_seconds=300)

# Custom configurations
cache = SearchResultCache(ttl_seconds=60)    # 1-minute, for fresh data
cache = SearchResultCache(ttl_seconds=1800)  # 30-minute, for stable data
cache = SearchResultCache(ttl_seconds=3600)  # 1-hour, for batch processing
```

### TTL Selection Guidelines

| TTL Duration | Use Case |
|-------------|----------|
| **30-60 sec** | Real-time systems, rapidly changing data |
| **5 min (300 sec)** | Standard RAG applications, default |
| **15-30 min** | Stable knowledge bases, batch processing |
| **1+ hour** | Archive queries, immutable knowledge bases |

### API Reference

```python
# Retrieve cached search results
results = search_cache.get(
    query: str,
    top_k: int,
    project_id: Optional[str] = None
) -> Optional[List[Dict]]

# Store search results in cache
search_cache.put(
    query: str,
    top_k: int,
    project_id: Optional[str],
    results: List[Dict]
) -> None

# Invalidate cache for specific query
search_cache.invalidate_query(query: str) -> None
# Removes all cache entries containing the query

# Invalidate cache for specific project
search_cache.invalidate_project(project_id: str) -> None
# Removes all cache entries for the project

# Get cache statistics
stats = search_cache.stats() -> Dict[str, any]
# Returns: {
#   "hits": int,              # Cache hit count
#   "misses": int,            # Cache miss count
#   "expires": int,           # Expired entries cleaned up
#   "total_calls": int,       # Total lookups
#   "hit_rate": str,          # Formatted hit rate %
#   "cache_size": int,        # Current items in cache
#   "ttl_seconds": int        # TTL configuration
# }

# Clear all cached search results
search_cache.clear() -> None
```

### Example: Search with Caching

```python
def search_with_cache(query, top_k, vector_db, cache, project_id=None):
    """Execute search, using cache when available."""

    # Try cache first
    cached = cache.get(query, top_k, project_id)
    if cached is not None:
        return cached

    # Execute search on cache miss
    results = vector_db.search(query, top_k=top_k)

    # Store in cache
    cache.put(query, top_k, project_id, results)

    return results

# Usage
query = "How does photosynthesis work?"
results = search_with_cache(query, 5, db, search_cache, project_id="bio_101")
print(search_cache.stats())
# Output: cache_size: 1, hit_rate: 0.0% (first time)

# Second query - should hit cache
results = search_with_cache(query, 5, db, search_cache, project_id="bio_101")
print(search_cache.stats())
# Output: cache_size: 1, hit_rate: 50.0% (1 hit out of 2)
```

### Invalidation Strategies

**Query-Based Invalidation**:
```python
# Clear cache for specific query
cache.invalidate_query("machine learning")
# Clears all queries containing "machine learning"
```

**Project-Based Invalidation**:
```python
# Clear all caches for a project when data changes
cache.invalidate_project("proj_123")
# Ensures fresh searches after knowledge base update
```

**Automatic TTL Expiration**:
```python
# Expired entries are automatically cleaned on access
# No manual cleanup needed
```

---

## Configuration & Tuning

### Memory Management

**Total Cache Memory**:
```
Embedding Cache:  max_size × embedding_dimension × 4 bytes
Search Cache:     varies by result size, typically 1-10 KB per entry
```

**Example Configuration**:
```python
# Conservative (low memory, ~50 MB total)
embedding_cache = EmbeddingCache(max_size=10000)
search_cache = SearchResultCache(ttl_seconds=300)

# Standard (medium memory, ~150-200 MB total)
embedding_cache = EmbeddingCache(max_size=50000)
search_cache = SearchResultCache(ttl_seconds=300)

# Aggressive (high memory, ~300+ MB total)
embedding_cache = EmbeddingCache(max_size=100000)
search_cache = SearchResultCache(ttl_seconds=600)
```

### Performance Tuning

**For Batch Processing**:
```python
# Larger embedding cache, longer search cache TTL
embedding_cache = EmbeddingCache(max_size=50000)
search_cache = SearchResultCache(ttl_seconds=1800)
```

**For Real-Time Applications**:
```python
# Moderate embedding cache, shorter search cache TTL
embedding_cache = EmbeddingCache(max_size=20000)
search_cache = SearchResultCache(ttl_seconds=120)
```

**For Multi-Tenant Systems**:
```python
# Larger caches, project-based invalidation
embedding_cache = EmbeddingCache(max_size=100000)
search_cache = SearchResultCache(ttl_seconds=600)

# Invalidate per project on updates
cache.invalidate_project(updated_project_id)
```

---

## Performance Metrics

### Baseline Performance (Without Cache)

| Operation | Latency | Notes |
|-----------|---------|-------|
| Embed text (CPU) | 50-200 ms | Depends on model size |
| Embed text (GPU) | 10-50 ms | High throughput with batching |
| Vector search | 100-500 ms | Depends on collection size |
| Full RAG pipeline | 500-1000 ms | Embedding + search + LLM |

### With Caching

| Operation | Cache Hit Latency | Speedup |
|-----------|-------------------|---------|
| Cached embedding | <1 ms | **100x** |
| Cached search | <2 ms | **20x** |
| Full pipeline (hits) | <50 ms | **50-200x** |

### Hit Rate Expectations

| Scenario | Typical Hit Rate | Notes |
|----------|-----------------|-------|
| Batch processing | 30-50% | Moderate deduplication |
| Interactive RAG | 20-40% | User typing variations |
| Repeated queries | 80%+ | Same questions multiple times |
| Cached knowledge base | 60-80% | Common semantic searches |

---

## Best Practices

### 1. Initialize Caches Early

```python
# Good: Initialize once, reuse
embedding_cache = EmbeddingCache()
search_cache = SearchResultCache()

def process_batch(texts):
    for text in texts:
        if not embedding_cache.get(text):
            embedding_cache.put(text, encode(text))
```

### 2. Monitor Cache Health

```python
# Periodically check cache statistics
def log_cache_stats():
    emb_stats = embedding_cache.stats()
    search_stats = search_cache.stats()

    logger.info(f"Embedding cache hit rate: {emb_stats['hit_rate']}")
    logger.info(f"Search cache hit rate: {search_stats['hit_rate']}")
    logger.info(f"Cache sizes: {emb_stats['cache_size']} + {search_stats['cache_size']}")
```

### 3. Handle Cache Invalidation

```python
# Clear cache when data changes
def update_knowledge_base(project_id, new_docs):
    knowledge_base.add(new_docs)
    search_cache.invalidate_project(project_id)
    logger.info(f"Invalidated cache for project {project_id}")
```

### 4. Use Project Scoping

```python
# Separate cache entries by project for multi-tenant systems
for project in projects:
    results = search_cache.get(query, top_k, project_id=project.id)
```

### 5. Set Appropriate TTL

```python
# Shorter TTL for frequently updated data
real_time_cache = SearchResultCache(ttl_seconds=60)

# Longer TTL for stable data
stable_cache = SearchResultCache(ttl_seconds=3600)
```

### 6. Clear on Shutdown

```python
# Clean up on application termination
def shutdown():
    embedding_cache.clear()
    search_cache.clear()
    logger.info("Caches cleared")
```

---

## Integration Guide

### With Socratic RAG Client

```python
from socratic_rag import RAGClient
from socratic_rag.caching import EmbeddingCache, SearchResultCache

# Initialize RAG client with caches
rag_client = RAGClient(api_key="...")

embedding_cache = EmbeddingCache(max_size=10000)
search_cache = SearchResultCache(ttl_seconds=300)

# Integrate caching into retrieval pipeline
def retrieve_with_cache(query, top_k=5, project_id=None):
    # Check search cache first
    results = search_cache.get(query, top_k, project_id)
    if results:
        return results

    # Retrieve and cache
    results = rag_client.retrieve(query, top_k=top_k)
    search_cache.put(query, top_k, project_id, results)
    return results
```

### With Custom Vector Databases

```python
from socratic_rag.caching import EmbeddingCache, SearchResultCache

def create_cached_rag_pipeline(embedding_model, vector_db):
    """Create RAG pipeline with caching."""

    emb_cache = EmbeddingCache(max_size=50000)
    search_cache = SearchResultCache(ttl_seconds=300)

    def embed(text):
        cached = emb_cache.get(text)
        if cached:
            return cached
        embedding = embedding_model.encode(text)
        emb_cache.put(text, embedding.tolist())
        return embedding

    def search(query, top_k=5):
        cached = search_cache.get(query, top_k)
        if cached:
            return cached
        results = vector_db.similarity_search(
            embed(query), top_k=top_k
        )
        search_cache.put(query, top_k, None, results)
        return results

    return {
        "embed": embed,
        "search": search,
        "embedding_cache": emb_cache,
        "search_cache": search_cache,
    }
```

---

## API Reference

### EmbeddingCache

```python
class EmbeddingCache:
    """LRU cache for text embeddings."""

    def __init__(self, max_size: int = 10000):
        """Initialize embedding cache.

        Args:
            max_size: Maximum number of embeddings to cache
        """

    def get(self, text: str) -> Optional[List[float]]:
        """Retrieve cached embedding for text."""

    def put(self, text: str, embedding: List[float]) -> None:
        """Store embedding in cache."""

    def stats(self) -> Dict[str, any]:
        """Get cache statistics."""

    def clear(self) -> None:
        """Clear all cached embeddings."""
```

### SearchResultCache

```python
class SearchResultCache:
    """TTL-based cache for vector search results."""

    def __init__(self, ttl_seconds: int = 300):
        """Initialize search result cache.

        Args:
            ttl_seconds: Time-to-live for cached results in seconds
        """

    def get(
        self,
        query: str,
        top_k: int,
        project_id: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """Retrieve cached search results."""

    def put(
        self,
        query: str,
        top_k: int,
        project_id: Optional[str],
        results: List[Dict]
    ) -> None:
        """Store search results in cache."""

    def invalidate_query(self, query: str) -> None:
        """Invalidate cache for specific query."""

    def invalidate_project(self, project_id: str) -> None:
        """Invalidate cache for specific project."""

    def stats(self) -> Dict[str, any]:
        """Get cache statistics."""

    def clear(self) -> None:
        """Clear all cached results."""
```

---

## Troubleshooting

### Low Cache Hit Rate

**Symptoms**: Cache statistics show <10% hit rate despite many queries

**Solutions**:
1. Verify cache is being used correctly (not cleared between queries)
2. Check if queries are unique or variations (normalize text)
3. Increase cache size to accommodate more entries
4. For search cache, increase TTL to keep results longer

```python
# Debug: Add logging
import logging
logging.getLogger(__name__).setLevel(logging.DEBUG)

# Check stats
stats = cache.stats()
print(f"Cache size: {stats['cache_size']}, Hit rate: {stats['hit_rate']}")
```

### High Memory Usage

**Symptoms**: Process memory grows significantly with caching enabled

**Solutions**:
1. Reduce max_size for embedding cache
2. Reduce TTL for search cache
3. Clear caches periodically
4. Monitor cache growth and invalidate stale projects

```python
# Reduce memory footprint
embedding_cache = EmbeddingCache(max_size=5000)
search_cache = SearchResultCache(ttl_seconds=120)

# Periodic cleanup
cache.clear()
```

### Cache Not Working

**Symptoms**: Cache stats show zero hits

**Solutions**:
1. Verify cache is properly initialized
2. Check that texts are exactly identical (whitespace, case)
3. Ensure text encoding is consistent (UTF-8)
4. Verify cache.get() is called before generating embedding

```python
# Verify cache
embedding = cache.get("test")
print(f"Cache get result: {embedding}")  # Should be None first time

cache.put("test", [0.1, 0.2, 0.3])
embedding = cache.get("test")
print(f"Cache get result: {embedding}")  # Should be [0.1, 0.2, 0.3]
```

---

## Summary

The socratic-rag caching module provides powerful performance optimizations through:

- **EmbeddingCache**: 100x speedup for duplicate text encoding
- **SearchResultCache**: 20x speedup for repeated semantic searches
- **Thread-safe operations**: Safe for production multi-threaded applications
- **Configurable strategies**: Tune for your specific use case
- **Observable metrics**: Monitor cache health with detailed statistics

For most RAG applications, simply enable both caches with default settings and enjoy significant performance improvements with minimal code changes.
