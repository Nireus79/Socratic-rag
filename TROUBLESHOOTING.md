# Troubleshooting Guide

This guide helps you solve common issues with Socratic RAG.

## Installation Issues

### ImportError: No module named 'socratic_rag'

**Problem**: Python can't find the socratic_rag module.

**Solutions**:
```bash
# 1. Make sure you installed the package
pip install socratic-rag

# 2. Verify installation
python -c "import socratic_rag; print(socratic_rag.__version__)"

# 3. If using a virtual environment, make sure it's activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### ModuleNotFoundError: No module named 'sentence_transformers'

**Problem**: Optional dependency not installed.

**Solution**:
```bash
# Install core + optional dependencies
pip install socratic-rag[all]

# Or install specific dependencies
pip install sentence-transformers numpy
```

### ModuleNotFoundError: No module named 'chromadb' / 'qdrant_client' / 'faiss'

**Problem**: Vector store dependency not installed.

**Solutions**:
```bash
# Install specific vector store
pip install socratic-rag[chromadb]  # ChromaDB
pip install socratic-rag[qdrant]    # Qdrant
pip install socratic-rag[faiss]     # FAISS

# Or install all vector stores
pip install socratic-rag[chromadb,qdrant,faiss]
```

---

## Vector Store Issues

### ChromaDB Connection Error

**Problem**: "Failed to connect to ChromaDB" or "Directory not found"

**Solutions**:
```python
# 1. Check directory permissions
import os
db_path = "./chroma_data"
os.makedirs(db_path, exist_ok=True)

# 2. Use in-memory ChromaDB (no persistence)
from socratic_rag import RAGClient, RAGConfig
config = RAGConfig(vector_store="chromadb")
client = RAGClient(config)  # Uses in-memory by default

# 3. Explicitly set persistence
# See ChromaDB documentation for details
```

### Qdrant Connection Refused

**Problem**: "Connection refused" when connecting to Qdrant server

**Solutions**:
```bash
# 1. Start Qdrant server
docker run -p 6333:6333 qdrant/qdrant

# 2. Verify Qdrant is running
curl http://localhost:6333/health

# 3. Check host and port in configuration
from socratic_rag import RAGClient, RAGConfig
config = RAGConfig(
    vector_store="qdrant",
    # Configuration passed to Qdrant client
)
```

### FAISS Index Not Found

**Problem**: "FAISS index file not found" or index corruption

**Solutions**:
```python
# 1. Create fresh FAISS index
from socratic_rag import RAGClient, RAGConfig
config = RAGConfig(vector_store="faiss")
client = RAGClient(config)  # Creates new index

# 2. Clear corrupted index
import shutil
shutil.rmtree("./faiss_index", ignore_errors=True)

# 3. Recreate index from documents
client = RAGClient(config)
# Re-add documents
```

---

## Embedding Issues

### Out of Memory When Embedding

**Problem**: "CUDA out of memory" or "Memory exceeded"

**Solutions**:
```python
from socratic_rag import RAGClient, RAGConfig

# 1. Use smaller model (default is already small)
config = RAGConfig(
    embedder="sentence-transformers",
    # Default: all-MiniLM-L6-v2 (384 dims, 22M params)
)

# 2. Process documents in smaller batches
client = RAGClient(config)
for i, doc in enumerate(documents):
    client.add_document(doc["content"], doc["source"])
    if (i + 1) % 10 == 0:
        print(f"Processed {i + 1} documents")

# 3. Reduce chunk size
config = RAGConfig(chunk_size=256)  # Default: 512

# 4. Disable embedding cache
config = RAGConfig(embedding_cache=False)
```

### Sentence Transformers Model Download Failed

**Problem**: "Connection error downloading model" or "Model not found"

**Solutions**:
```bash
# 1. Manually download model
python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('all-MiniLM-L6-v2')"

# 2. Use offline mode (after download)
import os
os.environ['SENTENCE_TRANSFORMERS_HOME'] = './models'

# 3. Check disk space
# Model is ~60MB; ensure sufficient free space

# 4. Use system proxy if behind corporate proxy
pip install --proxy [user:passwd@]proxy.server:port socratic-rag
```

---

## Search & Retrieval Issues

### No Search Results

**Problem**: `search()` returns empty results

**Solutions**:
```python
from socratic_rag import RAGClient

client = RAGClient()

# 1. Verify documents were added
# Check if knowledge base is empty
if client.search("test") == []:
    print("No documents in knowledge base")
    # Add documents first
    client.add_document("Test content", "test.txt")

# 2. Check similarity threshold
results = client.search("query", top_k=10)
for result in results:
    print(f"Score: {result.score}, Text: {result.chunk.text}")
    # Scores < 0.5 may indicate poor match

# 3. Verify query and documents are similar
# Try searching for exact phrases first
results = client.search("exact phrase from document")

# 4. Increase top_k to see more results
results = client.search("query", top_k=20)
```

### Low Relevance Scores

**Problem**: High scores but irrelevant results

**Solutions**:
```python
# 1. Check chunking strategy
from socratic_rag import RAGConfig
config = RAGConfig(
    chunk_size=256,    # Smaller chunks = more specific matches
    chunk_overlap=25   # Some overlap for context
)

# 2. Use better query formulation
# Bad: "python"
# Good: "How do I use Python for machine learning?"

# 3. Implement re-ranking (v0.2.0+)
results = client.search("query", top_k=20)
# Would support re-ranking in future version

# 4. Try different vector stores
# FAISS and Qdrant may have better performance
config = RAGConfig(vector_store="faiss")
```

### Duplicate Results

**Problem**: Same document appearing multiple times in results

**Solutions**:
```python
# 1. Check if documents were added multiple times
from socratic_rag import RAGClient
client = RAGClient()

# Add only once
client.add_document("Content", "source.txt")
# Not:
# client.add_document("Content", "source.txt")
# client.add_document("Content", "source.txt")

# 2. Clear and start fresh
client.clear()
# Re-add documents once

# 3. Check for similar document IDs
results = client.search("query", top_k=10)
seen_ids = set()
unique_results = []
for result in results:
    doc_id = result.chunk.document_id
    if doc_id not in seen_ids:
        unique_results.append(result)
        seen_ids.add(doc_id)
```

---

## Document Processing Issues

### PDF Processing Fails

**Problem**: "Failed to read PDF" or "No text extracted"

**Solutions**:
```python
from socratic_rag import RAGClient
from socratic_rag.processors import PDFProcessor

# 1. Verify PDF is not corrupted
import PyPDF2
with open("file.pdf", "rb") as f:
    reader = PyPDF2.PdfReader(f)
    print(f"Pages: {len(reader.pages)}")

# 2. Use explicit PDF processor
processor = PDFProcessor()
text = processor.process("file.pdf")
print(f"Extracted text: {text[:200]}")

# 3. Check if PDF is image-based
# OCR required for scanned PDFs (not supported in v0.1.0)

# 4. Handle encryption
# Remove PDF password protection if present
```

### Markdown Processing Issues

**Problem**: "Failed to process markdown" or formatting lost

**Solutions**:
```python
from socratic_rag.processors import MarkdownProcessor

processor = MarkdownProcessor()

# 1. Check for valid markdown
with open("file.md", "r") as f:
    content = f.read()
    print(content)

# 2. Process markdown
text = processor.process("file.md")

# 3. Preserve code blocks during chunking
# Code blocks should stay together (chunk_overlap helps)
```

### Text File Encoding Issues

**Problem**: "UnicodeDecodeError" or "Invalid encoding"

**Solutions**:
```python
from socratic_rag import RAGClient

# 1. Specify encoding when reading
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 2. Handle different encodings
import chardet
with open("file.txt", "rb") as f:
    encoding = chardet.detect(f.read())["encoding"]
    content = open("file.txt", "r", encoding=encoding).read()

# 3. Add document with proper encoding
client = RAGClient()
client.add_document(content, "file.txt")
```

---

## Performance Issues

### Slow Document Addition

**Problem**: Adding documents takes too long

**Solutions**:
```python
from socratic_rag import RAGClient, RAGConfig
import time

# 1. Increase chunk size (faster chunking)
config = RAGConfig(chunk_size=1024)  # Default: 512
client = RAGClient(config)

# 2. Disable embedding cache if not needed
config = RAGConfig(embedding_cache=False)

# 3. Use FAISS for faster embeddings
config = RAGConfig(vector_store="faiss")

# 4. Profile the bottleneck
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

for doc in documents:
    client.add_document(doc["content"], doc["source"])

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(10)  # Top 10 slowest functions
```

### Slow Search

**Problem**: Search queries take too long

**Solutions**:
```python
# 1. Use FAISS for faster search
from socratic_rag import RAGConfig
config = RAGConfig(vector_store="faiss")

# 2. Reduce top_k
results = client.search("query", top_k=5)  # Not 100

# 3. Profile search operation
import time
start = time.time()
results = client.search("query", top_k=5)
elapsed = time.time() - start
print(f"Search took {elapsed:.2f}s")

# 4. Use async client for concurrent searches
from socratic_rag import AsyncRAGClient
async_client = AsyncRAGClient()
results = await async_client.search("query")
```

### High Memory Usage

**Problem**: Process uses too much RAM

**Solutions**:
```python
# 1. Disable embedding cache
from socratic_rag import RAGConfig
config = RAGConfig(embedding_cache=False)

# 2. Use smaller chunks
config = RAGConfig(chunk_size=256)

# 3. Use external vector store (Qdrant, FAISS)
# Instead of in-memory ChromaDB
config = RAGConfig(vector_store="qdrant")

# 4. Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f}MB")
```

---

## Async Issues

### RuntimeError: No running event loop

**Problem**: "RuntimeError: no running event loop" when using AsyncRAGClient

**Solutions**:
```python
import asyncio
from socratic_rag import AsyncRAGClient

async def main():
    client = AsyncRAGClient()
    results = await client.search("query")
    return results

# Run with asyncio
results = asyncio.run(main())

# Or in Jupyter
await main()
```

### Coroutine was never awaited

**Problem**: "Coroutine was never awaited" warning

**Solution**:
```python
from socratic_rag import AsyncRAGClient

client = AsyncRAGClient()

# Wrong
results = client.search("query")  # Returns coroutine, not results

# Right
import asyncio
results = asyncio.run(client.search("query"))
```

---

## Framework Integration Issues

### LangChain Retriever Not Working

**Problem**: "Error initializing retriever" or no results

**Solutions**:
```python
from socratic_rag import RAGClient
from socratic_rag.integrations.langchain import SocraticRAGRetriever

# 1. Verify RAGClient is initialized with documents
rag_client = RAGClient()
rag_client.add_document("Test content", "test.txt")

# 2. Verify retriever
retriever = SocraticRAGRetriever(client=rag_client, top_k=5)
results = retriever.get_relevant_documents("Test query")
print(results)

# 3. Check with LangChain chain
from langchain.chat_models import ChatAnthropic
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
answer = qa.run("Question")
```

### Openclaw Skill Not Available

**Problem**: "Cannot import SocraticRAGSkill" or "Openclaw not installed"

**Solutions**:
```bash
# 1. Install Openclaw
pip install socratic-rag[openclaw]

# 2. Verify installation
python -c "from socratic_rag.integrations.openclaw import SocraticRAGSkill"

# 3. Check Openclaw version compatibility
```

---

## Debug Logging

### Enable Debug Logging

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

# Now use RAG client
from socratic_rag import RAGClient
client = RAGClient()
results = client.search("query")  # Will print debug info
```

### Verbose Output

```python
from socratic_rag import RAGClient, RAGConfig

config = RAGConfig()
client = RAGClient(config)

# Add document with tracing
print("Adding document...")
doc_id = client.add_document("Content", "source.txt")
print(f"Document ID: {doc_id}")

# Search with tracing
print(f"Searching for 'query'...")
results = client.search("query", top_k=5)
print(f"Found {len(results)} results")
for i, result in enumerate(results):
    print(f"  {i+1}. Score: {result.score:.2f}, Text: {result.chunk.text[:50]}")
```

---

## Getting Help

If you can't find a solution here:

1. **Check the documentation**: [docs/](docs/), [README.md](README.md)
2. **Search existing issues**: [GitHub Issues](https://github.com/Nireus79/Socratic-rag/issues)
3. **Join discussions**: [GitHub Discussions](https://github.com/Nireus79/Socratic-rag/discussions)
4. **Report a bug**: Use the bug report issue template with:
   - Minimal reproducible example
   - Error traceback
   - Environment details (Python version, OS, dependencies)

---

**Last Updated**: March 10, 2024
**Version**: 0.1.0
