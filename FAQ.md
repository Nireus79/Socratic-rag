# Frequently Asked Questions

## General Questions

### What is Socratic RAG?

Socratic RAG is a production-grade Python package for building Retrieval-Augmented Generation (RAG) systems. It provides:

- **Multiple vector stores**: ChromaDB, Qdrant, FAISS (extensible for more)
- **Flexible embeddings**: Sentence Transformers, OpenAI (via Socrates Nexus)
- **Smart document processing**: Text, PDF, Markdown files
- **Framework integrations**: Openclaw skills, LangChain components
- **Async support**: Non-blocking operations with asyncio
- **Production-ready**: 70%+ test coverage, type hints, comprehensive docs

### Why use Socratic RAG instead of alternatives?

**Socratic RAG excels at**:
- **Flexibility**: Choose your vector store, embeddings, chunking strategy
- **Production-ready**: Comprehensive testing, error handling, validation
- **Extensibility**: Provider pattern makes adding new backends easy
- **Documentation**: Extensive guides, examples, API reference
- **Framework support**: Built-in integrations with popular frameworks
- **Async-first**: Full async/await support from day one

### Is Socratic RAG production-ready?

**Yes!** v0.1.0 is production-ready with:
- ✅ 110+ tests with 70%+ code coverage
- ✅ Type hints (100% MyPy compliant)
- ✅ Comprehensive error handling
- ✅ Input validation on all APIs
- ✅ Full documentation
- ✅ CI/CD workflows
- ✅ Security best practices

### What license is Socratic RAG under?

Socratic RAG is open source under the **MIT License**, allowing commercial and private use.

---

## Installation & Setup

### How do I install Socratic RAG?

```bash
# Basic installation
pip install socratic-rag

# With all features
pip install socratic-rag[all]

# With specific features
pip install socratic-rag[chromadb,langchain,pdf]
```

See [Installation](README.md#installation) for more options.

### Which Python versions are supported?

Socratic RAG supports **Python 3.8, 3.9, 3.10, 3.11, and 3.12**.

### Do I need to install vector stores separately?

No, but they're optional:
- **ChromaDB**: Installed automatically (included in base package)
- **Qdrant**: `pip install socratic-rag[qdrant]`
- **FAISS**: `pip install socratic-rag[faiss]`

You only need to install the ones you'll use.

### How do I get started?

See [Quickstart Guide](docs/quickstart.md) for a 5-minute introduction.

---

## Architecture & Design

### What's the difference between RAGClient and AsyncRAGClient?

| Feature | RAGClient | AsyncRAGClient |
|---------|-----------|-----------------|
| **Async** | Synchronous (blocking) | Asynchronous (non-blocking) |
| **Usage** | Scripts, single-threaded apps | Web apps, concurrent operations |
| **Performance** | Good for simple use cases | Better for high-concurrency |
| **Ease** | Simpler to use | Requires asyncio knowledge |

Choose **RAGClient** for simplicity, **AsyncRAGClient** for performance.

### What's the "provider pattern"?

Socratic RAG uses the provider pattern for extensibility:

```python
class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents, embeddings): ...

    @abstractmethod
    def search(self, query_embedding, top_k): ...

# You can implement your own provider
class MyCustomVectorStore(BaseVectorStore):
    def add_documents(self, documents, embeddings): ...
    def search(self, query_embedding, top_k): ...
```

This allows easy addition of new vector stores, embeddings, chunking strategies.

### How does document chunking work?

Documents are split into chunks for better search:

```
Document: "Python is great. It's flexible. It's powerful."
           ↓
Chunks:   "Python is great. It's flexible."
          "It's flexible. It's powerful."
           ↓
Embed:    [0.2, 0.1, ...384 dims...]
           ↓
Search:   Find similar chunks, return results
```

Default: **512-character chunks** with **50-character overlap**.

### What embedding model is used by default?

**all-MiniLM-L6-v2** from Sentence Transformers:
- Dimensions: 384
- Parameters: 22M
- Size: ~60MB
- Speed: ~500ms per 1000 documents
- Accuracy: Very good for general-purpose RAG

### Why are embeddings important?

Embeddings convert text to numerical vectors, enabling semantic search:

```python
"Python programming" → [0.2, 0.5, -0.1, ..., 0.3]  # 384 dims
"Programming in Python" → [0.2, 0.5, -0.1, ..., 0.3]  # Similar!
"Machine learning" → [0.1, 0.2, 0.4, ..., 0.1]  # Different!
```

Similar embeddings = semantically similar content = better search.

---

## Vector Store Selection

### Which vector store should I use?

| Use Case | Recommendation |
|----------|----------------|
| **Development** | ChromaDB (in-memory) |
| **Small production** | ChromaDB (persistent) |
| **Large production** | Qdrant |
| **Maximum speed** | FAISS |
| **Cloud/scalable** | Qdrant Cloud |

See [Vector Stores Guide](docs/vector-stores.md) for detailed comparison.

### Can I switch vector stores later?

**Yes!** Socratic RAG provides a consistent API across all vector stores:

```python
# Start with ChromaDB
config = RAGConfig(vector_store="chromadb")
client = RAGClient(config)

# Later, switch to Qdrant
config = RAGConfig(vector_store="qdrant")
client = RAGClient(config)
# Same code works!
```

Migration requires re-adding documents to the new store.

### Do I need to run Qdrant separately?

**Yes**, Qdrant must be running:

```bash
# Option 1: Docker (recommended)
docker run -p 6333:6333 qdrant/qdrant

# Option 2: Binary
./qdrant  # Download from qdrant.io

# Option 3: Cloud
# Use Qdrant Cloud (managed service)
```

ChromaDB and FAISS work without external services.

### What's the difference between Qdrant and FAISS?

| Feature | Qdrant | FAISS |
|---------|--------|-------|
| **Speed** | Fast | Faster for search |
| **Scalability** | Distributed | Single machine |
| **Persistence** | Built-in | File-based |
| **API** | REST/gRPC | Library |
| **Deletion** | True deletion | Soft deletion |

**Qdrant**: Better for production, distributed, high availability
**FAISS**: Better for raw speed, local deployments

---

## Document Processing

### Which file formats are supported?

- ✅ **Text**: .txt (any encoding)
- ✅ **PDF**: .pdf (text-based, not scanned)
- ✅ **Markdown**: .md, .markdown
- ⏳ **Coming soon**: DOCX, PPT, Excel, HTML

### Can I use scanned PDFs (image-based)?

Not in v0.1.0 (OCR not supported). Options:

1. Use OCR tool first (Tesseract, AWS Textract)
2. Wait for v0.3.0 vision support
3. Use other RAG systems with OCR support

### How do I add custom file formats?

Implement a custom processor:

```python
from socratic_rag.processors import BaseDocumentProcessor

class MyDocumentProcessor(BaseDocumentProcessor):
    def process(self, file_path: str) -> str:
        # Read your custom format
        # Return text content
        return content

# Use it
processor = MyDocumentProcessor()
text = processor.process("file.custom")
client.add_document(text, "file.custom")
```

---

## Search & Retrieval

### How does search work?

```
Query: "Python programming"
  ↓
Embed: [0.2, 0.5, -0.1, ..., 0.3]  # Same model as documents
  ↓
Search: Find nearest vectors (cosine similarity)
  ↓
Return: Top K most similar documents
```

### What does the relevance score mean?

Scores range from 0 to 1:
- **0.9-1.0**: Excellent match
- **0.7-0.9**: Good match
- **0.5-0.7**: Moderate match
- **0.3-0.5**: Weak match
- **0.0-0.3**: Poor match (probably irrelevant)

### Can I filter search results by metadata?

Not in v0.1.0, but planned for v0.2.0:

```python
# v0.2.0+
results = client.search(
    "query",
    filters={"source": "documentation.pdf"}
)
```

Currently, you can filter after search:

```python
# v0.1.0
results = client.search("query")
filtered = [r for r in results if r.chunk.metadata.get("source") == "doc.pdf"]
```

### Can I do keyword search instead of semantic?

Not in v0.1.0 (vector-only), but planned for v0.2.0 (hybrid search).

Currently, use semantic search with specific queries:
- ❌ "python" (too general)
- ✅ "How do I use Python for machine learning?" (more specific)

---

## LLM Integration

### How do I use Socratic RAG with an LLM?

Option 1: **Manual integration**
```python
client = RAGClient()
context = client.retrieve_context("What is Python?")
# Pass context to your LLM
llm_response = your_llm(context, user_question)
```

Option 2: **LLMPoweredRAG** (with Socrates Nexus)
```python
from socratic_rag import LLMPoweredRAG
from socrates_nexus import LLMClient

rag = RAGClient()
llm = LLMClient(provider="anthropic", model="claude-sonnet")
llm_rag = LLMPoweredRAG(rag, llm)
answer = llm_rag.generate_answer("What is Python?")
```

See [LLM Integration Example](examples/05_llm_powered_rag.py).

### Does Socratic RAG work with OpenAI?

**Yes!** Options:

1. **Direct integration**
   ```python
   from openai import OpenAI
   client = RAGClient()
   context = client.retrieve_context("Question")
   response = OpenAI().chat.completions.create(
       messages=[{"role": "user", "content": f"Context: {context}..."}]
   )
   ```

2. **Via Socrates Nexus** (coming v0.2.0)

### Does Socratic RAG work with Claude?

**Yes!** Options:

1. **Direct integration**
   ```python
   from anthropic import Anthropic
   client = RAGClient()
   context = client.retrieve_context("Question")
   response = Anthropic().messages.create(
       messages=[{"role": "user", "content": f"Context: {context}..."}]
   )
   ```

2. **Via Socrates Nexus**
   ```python
   from socratic_rag import LLMPoweredRAG
   from socrates_nexus import LLMClient

   llm = LLMClient(provider="anthropic")  # Uses Claude
   llm_rag = LLMPoweredRAG(RAGClient(), llm)
   ```

---

## Performance

### How fast is Socratic RAG?

Approximate performance with 10K documents:

| Operation | Time | Notes |
|-----------|------|-------|
| Add document | 10-50ms | Includes chunking & embedding |
| Search (ChromaDB) | 10-20ms | Top 5 results |
| Search (FAISS) | 2-5ms | Much faster |
| Embed 1000 docs | 2-3s | CPU-based |

See [Performance Guide](docs/vector-stores.md#performance) for details.

### How much memory does it use?

Per document (average):
- **Text**: 50-100KB
- **With embedding**: Same + 1.5KB (384 dims × 4 bytes)

For 10K documents: ~500MB-1GB
For 100K documents: ~5-10GB

### How do I optimize performance?

1. **Use FAISS** for fastest search
2. **Increase chunk size** for faster processing
3. **Disable embedding cache** if memory-constrained
4. **Use async client** for concurrent operations
5. **Batch add documents** instead of one-by-one

See [Performance Tuning](docs/vector-stores.md) guide.

---

## Async & Concurrency

### When should I use AsyncRAGClient?

Use **AsyncRAGClient** when:
- Building web APIs (FastAPI, Starlette)
- Handling concurrent requests
- Want to avoid blocking operations
- Performance matters

Use **RAGClient** when:
- Writing simple scripts
- Single-threaded applications
- Simplicity is priority

### How do I use AsyncRAGClient?

```python
from socratic_rag import AsyncRAGClient
import asyncio

async def main():
    client = AsyncRAGClient()
    results = await client.search("query")
    return results

# Run it
results = asyncio.run(main())
```

### Can I use AsyncRAGClient in FastAPI?

**Yes!** Perfect combination:

```python
from fastapi import FastAPI
from socratic_rag import AsyncRAGClient

app = FastAPI()
client = AsyncRAGClient()

@app.get("/search")
async def search(query: str):
    results = await client.search(query)
    return results
```

---

## Framework Integrations

### How do I use Socratic RAG with LangChain?

```python
from socratic_rag import RAGClient
from socratic_rag.integrations.langchain import SocraticRAGRetriever
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

rag_client = RAGClient()
retriever = SocraticRAGRetriever(client=rag_client)
qa = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=retriever
)
answer = qa.run("Your question")
```

See [LangChain Integration](examples/04_langchain_integration.py).

### How do I use Socratic RAG with Openclaw?

```python
from socratic_rag.integrations.openclaw import SocraticRAGSkill

skill = SocraticRAGSkill(vector_store="chromadb")
skill.add_document("Content", "source.txt")
results = skill.search("query")
context = skill.retrieve_context("question")
```

See [Openclaw Integration](examples/03_openclaw_integration.py).

### Can I create a REST API with Socratic RAG?

**Yes!** See [REST API Example](examples/06_rest_api.py) using FastAPI:

```bash
python examples/06_rest_api.py
# Open http://localhost:8000/docs
```

---

## Troubleshooting

### I'm getting "ModuleNotFoundError" for optional dependencies

Install the optional dependency:

```bash
pip install socratic-rag[chromadb]  # For ChromaDB
pip install socratic-rag[pdf]       # For PDF support
pip install socratic-rag[langchain] # For LangChain
pip install socratic-rag[all]       # All at once
```

### My searches are returning irrelevant results

1. **Improve your query**: "python machine learning" vs "python"
2. **Adjust chunk size**: Smaller = more specific
3. **Try different vector store**: FAISS may perform better
4. **Check document quality**: Ensure documents are relevant
5. **Increase top_k**: Get more results and filter manually

See [Troubleshooting Guide](TROUBLESHOOTING.md#low-relevance-scores).

### Search is slow

1. **Use FAISS** instead of ChromaDB
2. **Reduce top_k** from 20 to 5
3. **Use AsyncRAGClient** for concurrency
4. **Profile** the bottleneck

See [Troubleshooting Guide](TROUBLESHOOTING.md#slow-search).

### Out of memory errors

1. **Reduce chunk size**: 512 → 256
2. **Disable embedding cache**: `embedding_cache=False`
3. **Process in batches**: Add documents one at a time
4. **Use smaller model**: Currently using smallest available

See [Troubleshooting Guide](TROUBLESHOOTING.md#out-of-memory-when-embedding).

---

## Contributing

### How can I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

### What areas need help?

- Additional vector store providers (Pinecone, Weaviate, Milvus)
- Embedding providers (Cohere, Jina, Aleph Alpha)
- Document processors (DOCX, Excel, HTML)
- Examples and tutorials
- Documentation improvements
- Bug reports and fixes

---

## Support & Community

### How do I report a bug?

Use [GitHub Issues](https://github.com/Nireus79/Socratic-rag/issues) with:
- Clear description
- Minimal reproducible example
- Error traceback
- Environment details

### Where can I ask questions?

- **GitHub Discussions**: Ask questions, share ideas
- **Issues**: Bug reports and feature requests
- **Documentation**: Check [docs/](docs/), [README.md](README.md)

### How do I stay updated?

- ⭐ Star the repository
- 👁️ Watch for notifications
- 📧 Follow GitHub releases

---

**Last Updated**: March 10, 2024
**Version**: 0.1.0
