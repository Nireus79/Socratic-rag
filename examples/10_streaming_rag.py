"""
Example: Streaming RAG Responses

This example demonstrates streaming responses for RAG:
1. Stream search results as they arrive
2. Stream LLM-powered answers
3. Real-time result processing

Run with:
    python examples/10_streaming_rag.py
"""

from typing import AsyncGenerator, Generator, List
import asyncio
from socratic_rag import RAGClient, AsyncRAGClient, RAGConfig


class StreamingRAG:
    """RAG client with streaming support."""

    def __init__(self, client: RAGClient):
        self.client = client

    def stream_search(
        self, query: str, top_k: int = 10
    ) -> Generator[dict, None, None]:
        """
        Stream search results as they arrive.

        Yields individual results instead of waiting for all.
        """
        results = self.client.search(query, top_k=top_k)

        for i, result in enumerate(results):
            yield {
                "rank": i + 1,
                "text": result.chunk.text,
                "score": result.score,
                "source": result.chunk.metadata.get("source", "unknown"),
                "is_last": i == len(results) - 1
            }

    def stream_retrieve_context(
        self, query: str, top_k: int = 5
    ) -> Generator[str, None, None]:
        """
        Stream context retrieval line by line.

        Useful for showing progress as results are retrieved.
        """
        results = self.client.search(query, top_k=top_k)

        for i, result in enumerate(results, 1):
            chunk_header = f"[{i}] {result.chunk.metadata.get('source', 'unknown')}"
            yield chunk_header
            yield f"Relevance: {result.score:.2f}"
            yield result.chunk.text
            yield ""  # Blank line separator


class AsyncStreamingRAG:
    """Async RAG client with streaming support."""

    def __init__(self, client: AsyncRAGClient):
        self.client = client

    async def stream_search(
        self, query: str, top_k: int = 10
    ) -> AsyncGenerator[dict, None]:
        """
        Async stream search results.

        Yields results as they're processed asynchronously.
        """
        results = await self.client.search(query, top_k=top_k)

        for i, result in enumerate(results):
            # Simulate processing time
            await asyncio.sleep(0.1)

            yield {
                "rank": i + 1,
                "text": result.chunk.text,
                "score": result.score,
                "source": result.chunk.metadata.get("source", "unknown"),
                "is_last": i == len(results) - 1
            }

    async def stream_parallel_searches(
        self, queries: List[str], top_k: int = 5
    ) -> AsyncGenerator[dict, None]:
        """
        Stream results from multiple queries in parallel.

        Useful for running multiple searches concurrently.
        """
        # Create search tasks
        tasks = [
            self.client.search(query, top_k=top_k)
            for query in queries
        ]

        # Run searches concurrently
        all_results = await asyncio.gather(*tasks)

        # Stream results as they complete
        for query, results in zip(queries, all_results):
            for i, result in enumerate(results):
                yield {
                    "query": query,
                    "rank": i + 1,
                    "text": result.chunk.text,
                    "score": result.score,
                    "source": result.chunk.metadata.get("source", "unknown")
                }


def stream_to_file(stream: Generator, filename: str) -> int:
    """
    Write streaming results to file.

    Returns count of items written.
    """
    count = 0
    with open(filename, 'w') as f:
        for item in stream:
            if isinstance(item, dict):
                f.write(f"{item}\n")
            else:
                f.write(f"{item}\n")
            count += 1
    return count


async def stream_to_websocket(
    stream: AsyncGenerator,
    send_func,
) -> int:
    """
    Stream results to WebSocket (for web apps).

    Useful for real-time updates in web interfaces.
    """
    count = 0
    async for item in stream:
        # Send to WebSocket
        await send_func(item)
        count += 1
    return count


def demo_sync_streaming():
    """Demonstrate synchronous streaming."""
    print("=" * 60)
    print("Synchronous Streaming Demo")
    print("=" * 60)

    # Setup
    client = RAGClient(RAGConfig(vector_store="chromadb"))
    streaming_rag = StreamingRAG(client)

    # Add sample documents
    print("\nLoading documents...")
    documents = [
        "Python supports functional programming paradigms",
        "Python uses indentation for code blocks",
        "Python has dynamic typing and automatic memory management",
        "Python is widely used for data science and AI",
        "Python has a rich ecosystem of libraries like NumPy and Pandas",
    ]

    for i, doc in enumerate(documents):
        client.add_document(doc, f"doc_{i}.txt")

    # Stream search results
    print("\nStreaming search results for 'Python features':\n")
    for result in streaming_rag.stream_search("Python features", top_k=3):
        print(f"[Result {result['rank']}]")
        print(f"  Score: {result['score']:.2f}")
        print(f"  Source: {result['source']}")
        print(f"  Text: {result['text'][:60]}...")
        print()

    # Stream context
    print("\nStreaming context for 'Python programming':\n")
    for line in streaming_rag.stream_retrieve_context("Python programming", top_k=2):
        print(line)


async def demo_async_streaming():
    """Demonstrate asynchronous streaming."""
    print("\n" + "=" * 60)
    print("Asynchronous Streaming Demo")
    print("=" * 60)

    # Setup
    client = AsyncRAGClient(RAGConfig(vector_store="chromadb"))
    streaming_rag = AsyncStreamingRAG(client)

    # Add sample documents
    print("\nLoading documents...")
    documents = [
        "Machine learning requires training data",
        "Neural networks learn through backpropagation",
        "Deep learning uses multiple layers of neural networks",
        "Reinforcement learning learns through reward signals",
        "Transfer learning reuses pre-trained models",
    ]

    for i, doc in enumerate(documents):
        await client.add_document(doc, f"ml_doc_{i}.txt")

    # Async stream search
    print("\nAsync streaming search results:\n")
    async for result in streaming_rag.stream_search("machine learning concepts", top_k=3):
        print(f"[Result {result['rank']}] {result['text'][:50]}... (Score: {result['score']:.2f})")

    # Async parallel searches
    print("\nAsync parallel searches:")
    queries = ["machine learning", "deep learning", "neural networks"]
    results_count = 0

    async for result in streaming_rag.stream_parallel_searches(queries, top_k=2):
        results_count += 1
        print(f"  [{result['query']}] {result['text'][:40]}... (#{result['rank']})")

    print(f"\nTotal results streamed: {results_count}")


class StreamingBuffer:
    """Buffer for managing streaming results."""

    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self.buffer: List[dict] = []

    def add(self, item: dict) -> None:
        """Add item to buffer."""
        self.buffer.append(item)

    def flush(self) -> List[dict]:
        """Get batch from buffer."""
        batch = self.buffer[:self.batch_size]
        self.buffer = self.buffer[self.batch_size:]
        return batch

    def is_full(self) -> bool:
        """Check if buffer is full."""
        return len(self.buffer) >= self.batch_size

    def has_items(self) -> bool:
        """Check if buffer has items."""
        return len(self.buffer) > 0

    def get_remaining(self) -> List[dict]:
        """Get all remaining items."""
        remaining = self.buffer
        self.buffer = []
        return remaining


def demo_buffered_streaming():
    """Demonstrate buffered streaming for batch processing."""
    print("\n" + "=" * 60)
    print("Buffered Streaming Demo")
    print("=" * 60)

    # Setup
    client = RAGClient(RAGConfig(vector_store="chromadb"))
    streaming_rag = StreamingRAG(client)

    # Add documents
    print("\nLoading documents...")
    for i in range(20):
        client.add_document(f"Document {i} content", f"doc_{i}.txt")

    # Stream with buffering
    print("\nStreaming with buffering (batch_size=5):\n")
    buffer = StreamingBuffer(batch_size=5)

    for result in streaming_rag.stream_search("content", top_k=15):
        buffer.add(result)

        if buffer.is_full():
            batch = buffer.flush()
            print(f"Batch: {[r['rank'] for r in batch]}")

    # Get remaining items
    remaining = buffer.get_remaining()
    if remaining:
        print(f"Final batch: {[r['rank'] for r in remaining]}")


if __name__ == "__main__":
    # Run sync demo
    demo_sync_streaming()

    # Run buffered demo
    demo_buffered_streaming()

    # Run async demo
    print("\n" + "=" * 60)
    print("Starting async demo...")
    asyncio.run(demo_async_streaming())
