"""Basic RAG example."""

from socratic_rag import RAGClient, RAGConfig

# Example 1: Using default configuration
print("=" * 60)
print("Example 1: Basic RAG with Default Configuration")
print("=" * 60)

client = RAGClient()

# Add some documents
print("\nAdding documents...")
doc1 = client.add_document(
    content="Python is a high-level programming language known for simplicity.",
    source="python_basics.txt",
)
print(f"Added document: {doc1}")

doc2 = client.add_document(
    content="Machine learning is a subset of artificial intelligence.",
    source="ml_basics.txt",
)
print(f"Added document: {doc2}")

doc3 = client.add_document(
    content="Deep learning uses neural networks with multiple layers.",
    source="dl_basics.txt",
)
print(f"Added document: {doc3}")

# Search for documents
print("\n" + "=" * 60)
print("Searching for 'Python'")
print("=" * 60)
results = client.search("Python", top_k=3)

for i, result in enumerate(results, 1):
    print(f"\n[{i}] Score: {result.score:.4f}")
    print(f"    Text: {result.chunk.text[:100]}...")
    print(f"    Document ID: {result.chunk.document_id}")

# Retrieve formatted context
print("\n" + "=" * 60)
print("Retrieving Context for LLM")
print("=" * 60)
context = client.retrieve_context("What is machine learning?", top_k=2)
print("\nFormatted Context:")
print(context)

# Example 2: Custom configuration
print("\n" + "=" * 60)
print("Example 2: Custom Configuration")
print("=" * 60)

config = RAGConfig(
    vector_store="chromadb",
    embedder="sentence-transformers",
    chunking_strategy="fixed",
    chunk_size=256,
    chunk_overlap=25,
    top_k=3,
)

custom_client = RAGClient(config)

# Add documents with custom configuration
print("\nAdding documents with custom chunk size...")
custom_client.add_document(
    content="Artificial intelligence is transforming industries worldwide.",
    source="ai_impact.txt",
    metadata={"category": "technology", "date": "2024"},
)

# Search with custom top_k
print("\nSearching with custom top_k=2...")
results = custom_client.search("artificial intelligence", top_k=2)
print(f"Found {len(results)} results")

# Cleanup
print("\n" + "=" * 60)
print("Cleanup")
print("=" * 60)
client.clear()
custom_client.clear()
print("Knowledge bases cleared!")
