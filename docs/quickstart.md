# Quickstart Guide

Get started with Socratic RAG in 5 minutes.

## Installation

```bash
pip install socratic-rag
```

For all features:

```bash
pip install socratic-rag[all]
```

## Basic Usage

### 1. Create a RAG Client

```python
from socratic_rag import RAGClient

# Use default configuration
client = RAGClient()
```

### 2. Add Documents

```python
# Add a single document
client.add_document(
    content="Python is a programming language.",
    source="python_basics.txt"
)

# Add multiple documents
documents = [
    ("Machine learning is AI", "ml.txt"),
    ("Deep learning uses neural networks", "dl.txt"),
]

for content, source in documents:
    client.add_document(content, source)
```

### 3. Search

```python
# Search for relevant documents
results = client.search("What is machine learning?", top_k=3)

for result in results:
    print(f"Score: {result.score:.2f}")
    print(f"Text: {result.chunk.text}\n")
```

### 4. Retrieve Context

```python
# Get formatted context for your LLM
context = client.retrieve_context("machine learning")
print(context)

# Output:
# [1] Machine learning is AI
#
# [2] Deep learning uses neural networks
```

## Configuration

Customize the behavior:

```python
from socratic_rag import RAGClient, RAGConfig

config = RAGConfig(
    vector_store="chromadb",          # Vector database
    embedder="sentence-transformers",  # Embedding model
    chunking_strategy="fixed",         # How to split documents
    chunk_size=256,                    # Characters per chunk
    chunk_overlap=25,                  # Overlap between chunks
    top_k=5,                           # Default number of results
)

client = RAGClient(config)
```

## Async Usage

For non-blocking operations:

```python
import asyncio
from socratic_rag import AsyncRAGClient

async def main():
    client = AsyncRAGClient()

    # Add document
    doc_id = await client.add_document("Content", "source.txt")

    # Search
    results = await client.search("query")

    # Retrieve context
    context = await client.retrieve_context("query")

    await client.clear()

asyncio.run(main())
```

## LLM Integration

Use with a Language Model for answer generation:

```python
from socratic_rag import RAGClient, LLMPoweredRAG
from socrates_nexus import LLMClient

# Initialize RAG
rag = RAGClient()
rag.add_document("Python is great", "python.txt")

# Initialize LLM
llm = LLMClient(provider="anthropic", model="claude-sonnet")

# Create LLM-powered RAG
llm_rag = LLMPoweredRAG(rag, llm)

# Generate answers
answer = llm_rag.generate_answer("What is Python?")
print(answer)
```

## Framework Integration

### Openclaw

```python
from socratic_rag.integrations.openclaw import SocraticRAGSkill

# Create skill
skill = SocraticRAGSkill(vector_store="chromadb")

# Use in Openclaw
skill.add_document("content", "source.txt")
results = skill.search("query")
context = skill.retrieve_context("query")
```

### LangChain

```python
from socratic_rag import RAGClient
from socratic_rag.integrations.langchain import SocraticRAGRetriever
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatAnthropic

# Create RAG client
client = RAGClient()
client.add_document("content", "source.txt")

# Create retriever
retriever = SocraticRAGRetriever(client=client, top_k=5)

# Create QA chain
llm = ChatAnthropic(model="claude-sonnet")
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff"
)

# Ask questions
answer = qa.run("What is the content about?")
```

## Next Steps

- Learn about [Vector Stores](vector-stores.md)
- Explore [Embedding Options](embeddings.md)
- Review [Integration Guides](integrations.md)
- Check [API Reference](api-reference.md)
- See [Examples](../examples/)

## Common Tasks

### Process Files

```python
from socratic_rag.processors import TextProcessor, PDFProcessor

# Process text file
text_processor = TextProcessor()
documents = text_processor.process("file.txt")

# Process PDF
pdf_processor = PDFProcessor()
documents = pdf_processor.process("file.pdf")

# Add to knowledge base
for doc in documents:
    client.add_document(doc.content, doc.source)
```

### Clear Knowledge Base

```python
# Remove all documents
client.clear()
```

### Custom Chunk Size

```python
config = RAGConfig(
    chunk_size=1024,      # Larger chunks
    chunk_overlap=100,    # More overlap
)
client = RAGClient(config)
```

## Troubleshooting

### No Results Found

- Check if documents were added: `client.search("test")` should return results
- Try a more specific query
- Increase `top_k`: `client.search("query", top_k=10)`

### Memory Issues

- Use `chunk_size=256` for smaller chunks
- Use FAISS or Qdrant for large datasets
- Process files incrementally

### Slow Search

- Use FAISS for faster searches on large datasets
- Reduce `chunk_size` for better matching
- Check if embeddings are cached

## Need Help?

- Check [Examples](../examples/)
- Read [Documentation](../README.md)
- Open an [Issue](https://github.com/Nireus79/Socratic-rag/issues)
- Start a [Discussion](https://github.com/Nireus79/Socratic-rag/discussions)
