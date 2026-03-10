"""Performance benchmarks for Socratic RAG."""

import time

import pytest

from socratic_rag import RAGClient, RAGConfig


class TestPerformanceBenchmarks:
    """Benchmark tests for Socratic RAG components."""

    @pytest.fixture
    def client(self):
        """Provide a RAG client."""
        config = RAGConfig(chunk_size=512, chunk_overlap=50)
        return RAGClient(config)

    @pytest.mark.slow
    def test_add_documents_performance(self, client, benchmark):
        """Benchmark document addition."""
        documents = [
            (f"Document {i} content about topic {i % 5}", f"doc{i}.txt") for i in range(100)
        ]

        def add_all():
            for content, source in documents:
                client.add_document(content, source)

        _ = benchmark(add_all)
        client.clear()

    @pytest.mark.slow
    def test_search_performance(self, client, benchmark):
        """Benchmark search operation."""
        # Add documents
        for i in range(100):
            client.add_document(
                f"Document {i} with content about Python and machine learning", f"doc{i}.txt"
            )

        def search():
            return client.search("Python machine learning", top_k=5)

        _ = benchmark(search)
        client.clear()

    @pytest.mark.slow
    def test_retrieve_context_performance(self, client, benchmark):
        """Benchmark context retrieval."""
        # Add documents
        for i in range(100):
            client.add_document(f"Document {i} content for context retrieval test", f"doc{i}.txt")

        def retrieve():
            return client.retrieve_context("test query", top_k=5)

        _ = benchmark(retrieve)
        client.clear()

    @pytest.mark.slow
    def test_large_document_performance(self, client):
        """Test performance with large documents."""
        # Create a large document (100KB)
        large_content = "word " * 20000  # ~100KB

        start = time.time()
        doc_id = client.add_document(large_content, "large.txt")
        add_time = time.time() - start

        start = time.time()
        results = client.search("word", top_k=5)
        search_time = time.time() - start

        print("\nLarge document benchmark:")
        print(f"  Add time: {add_time:.3f}s")
        print(f"  Search time: {search_time:.3f}s")
        print(f"  Results found: {len(results)}")

        assert doc_id is not None
        assert search_time < 1.5  # Should be reasonably fast (allows for CI environment variation)

        client.clear()

    @pytest.mark.slow
    def test_many_documents_search_performance(self, client):
        """Test search performance with many documents."""
        # Add 500 documents
        num_docs = 500
        start = time.time()

        for i in range(num_docs):
            client.add_document(
                f"Document {i} with unique content for performance testing", f"doc{i}.txt"
            )

        add_time = time.time() - start

        # Search
        start = time.time()
        results = client.search("testing", top_k=10)
        search_time = time.time() - start

        print(f"\nMany documents benchmark ({num_docs} docs):")
        print(f"  Total add time: {add_time:.3f}s")
        print(f"  Average per doc: {add_time/num_docs*1000:.1f}ms")
        print(f"  Search time: {search_time:.3f}s")
        print(f"  Results found: {len(results)}")

        assert search_time < 5.0  # Should complete in reasonable time

        client.clear()

    @pytest.mark.slow
    def test_chunking_performance(self, client):
        """Test chunking performance."""
        content = "word " * 100000  # ~500KB

        start = time.time()
        doc_id = client.add_document(content, "large.txt")
        elapsed = time.time() - start

        print("\nChunking benchmark:")
        print("  Content size: ~500KB")
        print(f"  Processing time: {elapsed:.3f}s")

        assert doc_id is not None

        client.clear()

    @pytest.mark.slow
    def test_embedding_performance(self, client):
        """Test embedding performance."""
        from socratic_rag.embeddings import SentenceTransformersEmbedder

        embedder = SentenceTransformersEmbedder()

        # Single text
        start = time.time()
        emb1 = embedder.embed_text("Hello world")
        single_time = time.time() - start

        # Batch
        texts = ["Hello world"] * 10
        start = time.time()
        embs = embedder.embed_batch(texts)
        batch_time = time.time() - start

        print("\nEmbedding benchmark:")
        print(f"  Single text time: {single_time*1000:.1f}ms")
        print(f"  Batch (10) time: {batch_time*1000:.1f}ms")
        print(f"  Per doc in batch: {batch_time/10*1000:.1f}ms")
        print(f"  Speedup: {(single_time*10)/batch_time:.1f}x")

        assert len(emb1) == embedder.dimension
        assert len(embs) == 10


class TestMemoryUsage:
    """Test memory usage characteristics."""

    @pytest.mark.slow
    def test_vector_store_memory(self):
        """Estimate vector store memory usage."""
        from socratic_rag import RAGConfig

        config = RAGConfig()
        client = RAGClient(config)

        # Add documents and measure
        num_docs = 1000

        for i in range(num_docs):
            client.add_document(f"Document {i} content for memory testing", f"doc{i}.txt")

        # Note: Actual memory measurement would require psutil or similar
        print("\nMemory characteristics:")
        print(f"  Documents added: {num_docs}")
        print(f"  Vector dimension: {client.embedder.dimension}")
        print(f"  Expected memory: ~{num_docs * client.embedder.dimension * 4 / (1024**2):.1f}MB")

        client.clear()


class TestScalability:
    """Test scalability characteristics."""

    @pytest.mark.slow
    def test_linear_search_scaling(self):
        """Test if search time scales linearly with document count."""
        from socratic_rag import RAGConfig

        results = {}

        for num_docs in [10, 50, 100, 200]:
            config = RAGConfig()
            client = RAGClient(config)

            # Add documents
            for i in range(num_docs):
                client.add_document(f"Document {i} scaling test", f"doc{i}.txt")

            # Search
            start = time.time()
            client.search("scaling", top_k=5)
            search_time = time.time() - start

            results[num_docs] = search_time
            client.clear()

        print("\nSearch scaling:")
        for docs, time_taken in sorted(results.items()):
            print(f"  {docs:3d} docs: {time_taken*1000:6.1f}ms")
