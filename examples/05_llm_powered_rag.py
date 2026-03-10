"""Example of LLM-powered RAG with answer generation."""

from socratic_rag import RAGClient, RAGConfig, LLMPoweredRAG

# Mock LLM client for demonstration
class MockLLMClient:
    """Mock LLM client for demonstration purposes."""

    def chat(self, prompt: str, **kwargs):
        """Generate a mock response."""
        class Response:
            def __init__(self, content):
                self.content = content

        # Return a simple response based on the prompt
        if "Python" in prompt:
            return Response(
                "Python is a high-level, interpreted programming language "
                "that emphasizes code readability and simplicity. "
                "It was created by Guido van Rossum and released in 1991."
            )
        elif "machine learning" in prompt:
            return Response(
                "Machine learning is a subset of artificial intelligence "
                "that enables systems to learn from data. "
                "It uses algorithms and statistical models to improve performance "
                "on a specific task."
            )
        else:
            return Response(
                "Based on the provided context, I can answer your question about "
                "various topics including Python and machine learning."
            )


print("=" * 60)
print("LLM-Powered RAG Example")
print("=" * 60)

# Initialize RAG client
rag_config = RAGConfig(
    vector_store="chromadb",
    chunk_size=256,
    top_k=3,
)
rag_client = RAGClient(rag_config)

# Create LLM client (use mock for demo)
llm_client = MockLLMClient()

# Initialize LLM-powered RAG
llm_rag = LLMPoweredRAG(rag_client=rag_client, llm_client=llm_client)

# Add documents
print("\nAdding documents...")
documents = [
    (
        "Python is a high-level programming language known for its simplicity "
        "and readability. Created by Guido van Rossum, it was first released in 1991.",
        "python_basics.txt",
    ),
    (
        "Machine learning is a subset of artificial intelligence that enables "
        "computers to learn from data without being explicitly programmed.",
        "ml_basics.txt",
    ),
    (
        "Deep learning is a specialized field of machine learning that uses "
        "neural networks with multiple layers to process complex data patterns.",
        "dl_basics.txt",
    ),
]

for content, source in documents:
    doc_id = llm_rag.add_document(content, source)
    print(f"Added: {source}")

# Generate answers
print("\n" + "=" * 60)
print("Generating Answers with LLM + RAG")
print("=" * 60)

queries = [
    "What is Python?",
    "What is machine learning?",
    "Tell me about deep learning",
]

for query in queries:
    print(f"\nQuery: {query}")
    print("-" * 40)

    # Show retrieved context
    context = llm_rag.retrieve_context(query, top_k=2)
    print("\nRetrieved Context:")
    print(context[:200] + "..." if len(context) > 200 else context)

    # Generate answer
    answer = llm_rag.generate_answer(query, top_k=2)
    print("\nGenerated Answer:")
    print(answer)

# Search functionality
print("\n" + "=" * 60)
print("Search Functionality")
print("=" * 60)

search_query = "neural networks"
results = llm_rag.search(search_query, top_k=2)
print(f"\nSearch for: {search_query}")
print(f"Found {len(results)} results:")
for i, result in enumerate(results, 1):
    print(f"  [{i}] Score: {result.score:.4f}")

# Cleanup
print("\n" + "=" * 60)
print("Cleanup")
print("=" * 60)

llm_rag.clear()
print("Knowledge base cleared!")

print("\n" + "=" * 60)
print("Integration with Real LLM")
print("=" * 60)

print("""
To use with a real LLM client (e.g., Socrates Nexus):

from socrates_nexus import LLMClient

# Initialize real LLM client
llm_client = LLMClient(provider="anthropic", model="claude-sonnet")

# Create LLM-powered RAG
llm_rag = LLMPoweredRAG(rag_client=rag_client, llm_client=llm_client)

# Generate answers
answer = llm_rag.generate_answer("What is machine learning?")
""")
