"""Example showing usage of multiple vector store providers."""

from socratic_rag import RAGClient, RAGConfig

# Sample documents
documents = [
    ("Python is a programming language", "python.txt"),
    ("Machine learning is AI", "ml.txt"),
    ("Deep learning uses neural networks", "dl.txt"),
]

# Example 1: ChromaDB (Default)
print("=" * 60)
print("Example 1: ChromaDB Vector Store (Default)")
print("=" * 60)

config_chromadb = RAGConfig(
    vector_store="chromadb",
    chunk_size=100,
)
client_chromadb = RAGClient(config_chromadb)

for content, source in documents:
    client_chromadb.add_document(content, source)

results = client_chromadb.search("Python programming")
print(f"\nChromaDB Results: {len(results)} documents found")
for r in results:
    print(f"  - {r.chunk.text[:60]}... (score: {r.score:.4f})")

client_chromadb.clear()

# Example 2: FAISS
print("\n" + "=" * 60)
print("Example 2: FAISS Vector Store")
print("=" * 60)

config_faiss = RAGConfig(
    vector_store="faiss",
    chunk_size=100,
)
client_faiss = RAGClient(config_faiss)

for content, source in documents:
    client_faiss.add_document(content, source)

results = client_faiss.search("machine learning")
print(f"\nFAISS Results: {len(results)} documents found")
for r in results:
    print(f"  - {r.chunk.text[:60]}... (score: {r.score:.4f})")

client_faiss.clear()

# Example 3: Qdrant
print("\n" + "=" * 60)
print("Example 3: Qdrant Vector Store")
print("=" * 60)

try:
    config_qdrant = RAGConfig(
        vector_store="qdrant",
        chunk_size=100,
    )
    client_qdrant = RAGClient(config_qdrant)

    for content, source in documents:
        client_qdrant.add_document(content, source)

    results = client_qdrant.search("neural networks")
    print(f"\nQdrant Results: {len(results)} documents found")
    for r in results:
        print(f"  - {r.chunk.text[:60]}... (score: {r.score:.4f})")

    client_qdrant.clear()

except Exception as e:
    print(f"\nQdrant example requires qdrant-client to be installed.")
    print(f"Install with: pip install qdrant-client")

print("\nDone!")
