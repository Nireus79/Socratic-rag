"""Example of Openclaw RAG skill integration."""

from socratic_rag.integrations.openclaw import SocraticRAGSkill

# Initialize the skill
print("=" * 60)
print("Openclaw RAG Skill Example")
print("=" * 60)

skill = SocraticRAGSkill(
    vector_store="chromadb",
    chunk_size=256,
    top_k=5,
)

# Add documents
print("\nAdding documents...")
doc1 = skill.add_document(
    content="Python is a high-level programming language.",
    source="python_basics.txt",
    metadata={"category": "programming", "language": "Python"},
)
print(f"Added document: {doc1}")

doc2 = skill.add_document(
    content="Machine learning enables computers to learn from data.",
    source="ml_basics.txt",
    metadata={"category": "AI", "topic": "Machine Learning"},
)
print(f"Added document: {doc2}")

doc3 = skill.add_document(
    content="Deep learning uses neural networks with multiple layers.",
    source="dl_basics.txt",
    metadata={"category": "AI", "topic": "Deep Learning"},
)
print(f"Added document: {doc3}")

# Search using the skill
print("\n" + "=" * 60)
print("Searching for 'Python'")
print("=" * 60)

results = skill.search("Python", top_k=3)
for i, result in enumerate(results, 1):
    print(f"\n[{i}] Score: {result['score']:.4f}")
    print(f"    Text: {result['text'][:100]}...")
    print(f"    Source: {result['metadata'].get('language', 'N/A')}")

# Retrieve context for LLM
print("\n" + "=" * 60)
print("Retrieving Context for LLM")
print("=" * 60)

context = skill.retrieve_context("What is machine learning?", top_k=2)
print("\nFormatted Context:")
print(context)

# Get config
print("\n" + "=" * 60)
print("Skill Configuration")
print("=" * 60)

config = skill.get_config()
print(f"Vector Store: {config.vector_store}")
print(f"Embedder: {config.embedder}")
print(f"Chunk Size: {config.chunk_size}")
print(f"Top K: {config.top_k}")

# Cleanup
print("\n" + "=" * 60)
print("Cleanup")
print("=" * 60)

skill.clear()
print("Knowledge base cleared!")
