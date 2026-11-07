> **Proof of concept, not a product.** This library belongs to the earlier Python research prototype ([Socrates](https://github.com/Nireus79/Socrates)) and is not maintained as a product. The current products are listed at [nireus79.github.io](https://nireus79.github.io/). Contact: Hermes_creative@proton.me.

# Socratic RAG

[![PyPI version](https://badge.fury.io/py/socratic-rag.svg)](https://badge.fury.io/py/socratic-rag)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A small vector-search layer extracted from the Socrates prototype. It stores text entries in a local [ChromaDB](https://www.trychroma.com/) collection, embeds them with a [sentence-transformers](https://www.sbert.net/) model and returns the entries closest to a query.

## What is in the package

- `VectorDatabase`: add text or `KnowledgeEntry` objects, search for similar entries, delete entries, and keep entries per project (`project_id`).
- `KnowledgeEntry`: a small dataclass (`id`, `content`, `category`, `embedding`, `metadata`).
- `EmbeddingCache` and `SearchResultCache`: in-memory caches used by `VectorDatabase` (an LRU cache for embeddings and a time-limited cache for search results). Their speedup has not been measured.

The modules `project_db`, `project_file_manager` and `read_write_split` come from the prototype and import its `socratic_system` package. They work only inside the prototype and are not usable on their own.

There is no chunking, no PDF or Markdown reader, no other vector store than ChromaDB, no async interface and no integration layer. Earlier versions of this README described such features; they do not exist in the code.

## Install

```bash
pip install socratic-rag
```

The first search downloads the embedding model (`all-MiniLM-L6-v2` by default) from the internet.

## Use

```python
from socratic_rag import KnowledgeEntry, VectorDatabase

db = VectorDatabase("./chroma_data")

db.add_text("Python uses indentation to define code blocks.", {"topic": "python"})
db.add_knowledge(
    KnowledgeEntry(id="tests", content="Unit tests check one function at a time.", category="testing")
)

for hit in db.search_similar("how does Python mark blocks?", top_k=3):
    print(hit["content"], hit["score"])  # score is the distance: lower is closer

db.close()
```

`search_similar` returns an empty list when the query is empty or the search fails (the failure is logged as a warning).

## Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/
```

The tests check that the package imports and that a `VectorDatabase` can be created. They do not download the embedding model or measure search quality.

## License

MIT. Contact: Hermes_creative@proton.me
