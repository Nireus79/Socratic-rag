# Socratic RAG - Guides by Role

## For Developers

Key concepts: Provider pattern, async support, extensibility.

Implement custom:
- Vector store by extending BaseVectorStore
- Embedder by implementing BaseEmbedder
- Chunking strategy by extending BaseChunker

## For Data Scientists

Key features: Document management, semantic search, RAG workflow.

Typical workflow:
1. Create RAGClient with vector store
2. Add documents from various sources
3. Search by semantic similarity
4. Retrieve context for LLM
5. Generate answers using retrieved context

Cost optimization:
- Use local embeddings (Sentence Transformers)
- Cache embeddings to reduce API calls
- Batch document additions

## For DevOps

Deployment considerations:
- Vector store persistence (PostgreSQL, Qdrant server)
- Embedding model size and memory
- Scaling concurrent searches
- Monitoring search latency and quality

Production setup:
- Use Qdrant or Pinecone for cloud
- Enable embedding caching
- Monitor quality metrics
- Implement fallback retrievers

## For Business Users

Benefits:
- Better search quality than keyword matching
- Cost-effective knowledge management
- Easy to add/update documents
- Works with any LLM for answer generation
