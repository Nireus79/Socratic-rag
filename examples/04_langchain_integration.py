"""Example of LangChain retriever integration."""

from socratic_rag import RAGClient, RAGConfig
from socratic_rag.integrations.langchain import SocraticRAGRetriever

# Initialize RAG client
print("=" * 60)
print("LangChain Retriever Integration Example")
print("=" * 60)

config = RAGConfig(
    vector_store="chromadb",
    chunk_size=256,
    top_k=5,
)
client = RAGClient(config)

# Add documents
print("\nAdding documents...")
client.add_document(
    content="Python is a high-level programming language known for simplicity.",
    source="python.txt",
)
client.add_document(
    content="Machine learning is a subset of artificial intelligence.",
    source="ml.txt",
)
client.add_document(
    content="Deep learning uses artificial neural networks.",
    source="dl.txt",
)

# Create LangChain retriever
print("\nCreating LangChain retriever...")
retriever = SocraticRAGRetriever(client=client, top_k=3)

# Use the retriever
print("\n" + "=" * 60)
print("Retrieving Documents")
print("=" * 60)

query = "What is machine learning?"
documents = retriever.get_relevant_documents(query)

print(f"\nQuery: {query}")
print(f"Found {len(documents)} documents:")

for i, doc in enumerate(documents, 1):
    print(f"\n[{i}] Page Content:")
    print(f"    {doc.page_content[:100]}...")
    print(f"    Score: {doc.metadata.get('score', 'N/A'):.4f}")

# Demonstrate integration with LangChain chains
print("\n" + "=" * 60)
print("LangChain Integration Notes")
print("=" * 60)

print("""
The SocraticRAGRetriever can be used with LangChain chains:

from langchain.chat_models import ChatAnthropic
from langchain.chains import RetrievalQA

# Create chain
llm = ChatAnthropic(model="claude-sonnet")
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff"
)

# Ask questions
answer = qa.run("What is machine learning?")
""")

# Cleanup
print("\n" + "=" * 60)
print("Cleanup")
print("=" * 60)

client.clear()
print("Knowledge base cleared!")
