# Socratic RAG - FAQ by Scenario

## Scenario 1: Adding Documents

How do I add documents to the knowledge base?

```python
rag = RAGClient()
doc_id = rag.add_document(
    content="Python is a programming language",
    source="python_facts.txt"
)
```

## Scenario 2: Searching

How do I search for relevant documents?

```python
results = rag.search("What is Python?", top_k=5)
for result in results:
    print(f"{result.score:.2f}: {result.chunk.text}")
```

## Scenario 3: RAG Workflow

How do I use RAG with an LLM?

```python
from socratic_rag import RAGClient
from socrates_nexus import LLMClient

rag = RAGClient()
rag.add_document("Python documentation...")
context = rag.retrieve_context("What is Python?")

llm = LLMClient(provider="anthropic")
response = llm.chat(f"Context: {context}\nQuestion: What is Python?")
```

## Scenario 4: Multiple Vector Stores

How do I switch between vector stores?

```python
# ChromaDB (default)
rag1 = RAGClient(vector_store="chromadb")

# Qdrant
rag2 = RAGClient(vector_store="qdrant")

# FAISS
rag3 = RAGClient(vector_store="faiss")
```

## Scenario 5: Processing Large Documents

How do I handle large documents?

```python
config = RAGConfig(
    chunking_strategy="recursive",
    chunk_size=1024,  # Larger chunks for dense content
    chunk_overlap=100
)
rag = RAGClient(config)
rag.add_document(large_document, source="large.txt")
```
