# Embeddings Guide

Understanding embeddings and how to choose the right embedder for your use case.

## What Are Embeddings?

Embeddings are dense vector representations of text that capture semantic meaning. They allow us to:
- Measure similarity between texts
- Find semantically similar documents
- Enable neural search capabilities

Example:
```
"Python is great" → [0.123, -0.456, 0.789, ..., 0.234]  # 384-dimensional vector
```

Semantically similar texts have similar embeddings:
```
"Python is great" ≈ "Python is awesome"  # High similarity
"Python is great" ≠ "Java is powerful"    # Low similarity
```

## Available Embedders

### Sentence Transformers (Default)

**Best for**: Local usage, privacy, development

**Features**:
- Local execution (no API calls)
- Multiple pre-trained models
- Fast inference
- Privacy-preserving

**Models Available**:
- `all-MiniLM-L6-v2` (default) - 384 dimensions, fast
- `all-mpnet-base-v2` - 768 dimensions, better quality
- `paraphrase-multilingual-MiniLM-L12-v2` - 384 dimensions, multilingual
- And 1000+ more at [sentence-transformers.com](https://www.sbert.net/)

**Pros**:
- ✅ No API key required
- ✅ Privacy: data stays local
- ✅ Fast: runs on CPU/GPU
- ✅ Free
- ✅ Wide model selection

**Cons**:
- ❌ Requires model download
- ❌ GPU optional but slow on CPU
- ❌ Limited to available models

**Usage**:

```python
from socratic_rag import RAGClient, RAGConfig
from socratic_rag.embeddings import SentenceTransformersEmbedder

# Use default model
config = RAGConfig(embedder="sentence-transformers")
client = RAGClient(config)

# Or use custom model
embedder = SentenceTransformersEmbedder(
    model_name="all-mpnet-base-v2"  # Better quality
)
```

**Installation**:

```bash
pip install sentence-transformers
```

**When to Use**:
- Development and prototyping
- Privacy-sensitive applications
- Offline systems
- Cost-conscious projects
- Small to medium datasets

---

## Planned Providers (v0.2.0+)

### OpenAI Embeddings

```python
# Coming in v0.2.0
from socratic_rag import RAGConfig

config = RAGConfig(embedder="openai")
client = RAGClient(config)
```

**Features**:
- State-of-the-art quality
- Multiple models (Ada, Babbage, Curie, Davinci)
- Up-to-date knowledge

**Costs**: ~$0.0001 per 1K tokens

### Claude Embeddings

```python
# Coming in v0.2.0
from socratic_rag import RAGConfig

config = RAGConfig(embedder="claude")
client = RAGClient(config)
```

---

## Choosing an Embedder

### Decision Tree

1. **Can you send data to external API?**
   - No → Use **Sentence Transformers**
   - Yes → Go to step 2

2. **Need latest/best quality?**
   - Yes → Use **OpenAI** (when available)
   - No → Use **Sentence Transformers**

3. **Cost sensitive?**
   - Yes → Use **Sentence Transformers**
   - No → Use **OpenAI** or **Claude**

## Model Selection Guide

### Sentence Transformers Models

| Model | Dimensions | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | ⚡⚡⚡ Fast | ✅ Good | Default choice |
| all-mpnet-base-v2 | 768 | ⚡⚡ Medium | ✅✅ Better | Quality matters |
| paraphrase-MiniLM | 384 | ⚡⚡⚡ Fast | ✅ Good | Semantic search |
| multilingual-MiniLM | 384 | ⚡⚡⚡ Fast | ✅ Good | Multiple languages |
| all-roberta-large-v1 | 1024 | ⚡ Slow | ✅✅✅ Best | Maximum quality |

**All-in-one comparison**:

| Aspect | MiniLM | MPNET | RoBERTa |
|--------|--------|-------|---------|
| Speed | 95ms/doc | 180ms/doc | 420ms/doc |
| Memory | 80MB | 430MB | 1.3GB |
| Quality | Good | Better | Best |
| Cost | 🟢 | 🟢 | 🟢 |

**Recommendation**:
- Start with `all-MiniLM-L6-v2` (default)
- Switch to `all-mpnet-base-v2` if quality is insufficient
- Use `all-roberta-large-v1` only if quality is critical

---

## Advanced Usage

### Custom Embedder

Implement your own:

```python
from socratic_rag.embeddings import BaseEmbedder

class MyEmbedder(BaseEmbedder):
    """Custom embedder implementation."""

    def embed_text(self, text: str) -> list:
        # Your embedding logic here
        pass

    def embed_batch(self, texts: list) -> list:
        # Batch embedding
        pass

    @property
    def dimension(self) -> int:
        return 384  # Your embedding dimension
```

### Model Caching

Models are cached after first download:

```bash
# Cache location (Linux/Mac)
~/.cache/huggingface/hub/

# Cache location (Windows)
%USERPROFILE%\.cache\huggingface\hub\
```

To use a custom cache location:

```python
import os
os.environ['HF_HOME'] = '/path/to/cache'

# Then create embedder
from socratic_rag.embeddings import SentenceTransformersEmbedder
embedder = SentenceTransformersEmbedder()
```

### GPU Acceleration

Enable GPU for faster embeddings:

```python
import torch
from socratic_rag.embeddings import SentenceTransformersEmbedder

# Check if GPU is available
print(torch.cuda.is_available())

# Models will automatically use GPU if available
embedder = SentenceTransformersEmbedder()
```

## Performance Tips

### Batch Embedding

```python
# Good: Batch embedding is much faster
texts = ["text 1", "text 2", "text 3"]
embeddings = embedder.embed_batch(texts)  # 3x faster than loop

# Avoid: Looping
embeddings = [embedder.embed_text(t) for t in texts]  # Slow
```

### Optimal Batch Size

```python
# For Sentence Transformers
# Typical optimal batch sizes:
# - CPU: 32-64
# - GPU (4GB): 64-128
# - GPU (8GB): 256-512

# Adjust based on your hardware
```

### Caching Strategy

```python
from socratic_rag import RAGConfig

# Enable embedding cache (default)
config = RAGConfig(
    embedding_cache=True,
    cache_ttl=3600  # Cache for 1 hour
)
```

## Embedding Dimensions Impact

### Memory Usage

```
Documents: 10,000
Dimensions: 384 (default)
Memory: ~15MB

Documents: 10,000
Dimensions: 1024 (larger)
Memory: ~40MB
```

### Search Speed

- Smaller dimensions (384) = Faster search
- Larger dimensions (768+) = Better accuracy, slower search

**Recommendation**: Use 384-dim for most cases, upgrade if needed

## Multilingual Support

### Using Multilingual Models

```python
from socratic_rag.embeddings import SentenceTransformersEmbedder

# Multilingual model (44 languages)
embedder = SentenceTransformersEmbedder(
    model_name="sentence-transformers/multilingual-MiniLM-L12-v2"
)

# Works with multiple languages
english = embedder.embed_text("Hello world")
spanish = embedder.embed_text("Hola mundo")
chinese = embedder.embed_text("你好世界")

# Can still find similarities across languages
```

## Troubleshooting

### Model Download Fails

```python
# Check internet connection
# Models download from huggingface.co

# Use custom cache directory if needed
import os
os.environ['HF_HOME'] = '/tmp/hf_cache'
```

### Out of Memory

```python
# Use smaller model
from socratic_rag.embeddings import SentenceTransformersEmbedder

embedder = SentenceTransformersEmbedder(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # Smallest
)
```

### Slow Embeddings

```python
# Enable GPU
import torch
print(torch.cuda.is_available())

# Use batch embedding
texts = ["doc1", "doc2", "doc3"]
embeddings = embedder.embed_batch(texts)  # Faster than loop
```

## Quality Evaluation

### Semantic Similarity Benchmark

Approximate cosine similarity scores:

```python
embedder = SentenceTransformersEmbedder("all-MiniLM-L6-v2")

# Very similar
emb1 = embedder.embed_text("The cat sat on the mat")
emb2 = embedder.embed_text("A cat sat on a mat")
similarity = cosine_similarity(emb1, emb2)  # ~0.95

# Similar
emb1 = embedder.embed_text("I like cats")
emb3 = embedder.embed_text("I like dogs")
similarity = cosine_similarity(emb1, emb3)  # ~0.75

# Different
emb1 = embedder.embed_text("I like cats")
emb4 = embedder.embed_text("Python programming")
similarity = cosine_similarity(emb1, emb4)  # ~0.20
```

## See Also

- [Quickstart Guide](quickstart.md)
- [Vector Stores Guide](vector-stores.md)
- [API Reference](api-reference.md)
- [Sentence Transformers Docs](https://www.sbert.net/)
