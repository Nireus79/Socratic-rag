# Architecture Diagrams

Visual representations of Socratic RAG's architecture and data flows.

## System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Application Layer                           │
│                  (Your code using RAG)                         │
└─────────────────────────┬──────────────────────────────────────┘
                          │
┌─────────────────────────┴──────────────────────────────────────┐
│                Socratic RAG Public API                          │
│  RAGClient / AsyncRAGClient                                    │
│  ├── add_document(content, source)                             │
│  ├── search(query, top_k)                                      │
│  ├── retrieve_context(query)                                   │
│  └── clear()                                                   │
└─────────────────────────┬──────────────────────────────────────┘
                          │
┌─────────────────────────┴──────────────────────────────────────┐
│              Core Orchestration Layer                           │
│  ┌──────────────┬──────────────┬───────────────┬────────────┐  │
│  │  Document    │   Chunking   │   Embedding   │   Vector   │  │
│  │ Processing   │              │               │   Storage  │  │
│  └──────────────┴──────────────┴───────────────┴────────────┘  │
└─────────────────────────┬──────────────────────────────────────┘
                          │
┌─────────────────────────┴──────────────────────────────────────┐
│             Provider Layer (Pluggable)                          │
│  ┌─────────────────┬─────────────────┬──────────────────────┐  │
│  │   Embedders     │ Vector Stores   │  Document Processors │  │
│  │ ┌─────────────┐ │ ┌─────────────┐ │ ┌──────────────────┐ │  │
│  │ │SentenceTrans│ │ │ChromaDB     │ │ │TextProcessor     │ │  │
│  │ │(default)    │ │ │             │ │ │                  │ │  │
│  │ │             │ │ │Qdrant       │ │ │PDFProcessor      │ │  │
│  │ │Future:      │ │ │             │ │ │                  │ │  │
│  │ │OpenAI       │ │ │FAISS        │ │ │MarkdownProcessor │ │  │
│  │ │Claude       │ │ │             │ │ │                  │ │  │
│  │ └─────────────┘ │ │Future:      │ │ │Future: DOCX, etc.│ │  │
│  │                 │ │Milvus, etc. │ │ └──────────────────┘ │  │
│  │                 │ └─────────────┘ │                      │  │
│  └─────────────────┴─────────────────┴──────────────────────┘  │
└─────────────────────────┬──────────────────────────────────────┘
                          │
┌─────────────────────────┴──────────────────────────────────────┐
│           External Services & Storage                           │
│  ┌──────────────────┬──────────────┬────────────────────────┐  │
│  │Vector Databases  │ LLM Services │   File Storage         │  │
│  │ • ChromaDB       │ • Anthropic  │ • Local filesystem     │  │
│  │ • Qdrant         │ • OpenAI     │ • S3 / Cloud Storage   │  │
│  │ • FAISS          │ • Others     │                        │  │
│  └──────────────────┴──────────────┴────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Document Addition

```
User Input
   │
   ├─ Content: "Python is great"
   ├─ Source: "python.txt"
   └─ Metadata: {...}
   │
   ▼
┌─────────────────────────────────┐
│  1. Create Document Object      │
│  • doc_id: auto-generated       │
│  • timestamp: now()             │
│  • metadata: merged             │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  2. Chunk Document              │
│  • Strategy: Fixed 512 chars    │
│  • Overlap: 50 chars            │
│  • Result: List[Chunk]          │
└──────────────┬──────────────────┘
               │
        Text Chunks:
        • "Python is great and..."
        • "is great and widely..."
        • "and widely used in..."
        │
        ▼
┌─────────────────────────────────┐
│  3. Generate Embeddings         │
│  • Model: all-MiniLM-L6-v2      │
│  • Dimension: 384               │
│  • Result: List[List[float]]    │
└──────────────┬──────────────────┘
               │
        Vectors:
        • [0.23, -0.15, 0.08, ...]
        • [0.25, -0.12, 0.07, ...]
        • [0.22, -0.18, 0.09, ...]
        │
        ▼
┌─────────────────────────────────┐
│  4. Store in Vector Database    │
│  • Store chunks with vectors    │
│  • Store metadata               │
│  • Create index                 │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  ✓ Document Indexed & Ready     │
│  Return: document_id            │
└─────────────────────────────────┘
```

---

## Data Flow: Search & Retrieval

```
User Query: "What is Python?"
   │
   ▼
┌─────────────────────────────────┐
│  1. Generate Query Embedding    │
│  • Use same model (consistency) │
│  • all-MiniLM-L6-v2             │
│  • Result: List[float] (384)    │
└──────────────┬──────────────────┘
               │
        Query Vector:
        • [0.24, -0.13, 0.08, ...]
        │
        ▼
┌─────────────────────────────────┐
│  2. Similarity Search           │
│  • Algorithm: Cosine Similarity │
│  • Compare with indexed vectors │
│  • Find top_k=5 most similar    │
└──────────────┬──────────────────┘
               │
        Search Results:
        • doc_1: score=0.87
        • doc_3: score=0.82
        • doc_2: score=0.71
        • doc_5: score=0.65
        • doc_4: score=0.61
        │
        ▼
┌─────────────────────────────────┐
│  3. Format Context (Optional)   │
│  • Combine chunks with scores   │
│  • Format as readable text      │
│  • Ready for LLM prompt         │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Return to User:                │
│  • SearchResult objects         │
│  • Or formatted context string  │
└─────────────────────────────────┘
```

---

## Provider Pattern

### Vector Store Provider Pattern

```
BaseVectorStore (Abstract)
     ▲
     │ implements
     │
     ├─ ChromaDBVectorStore
     │  ├─ add_documents()
     │  ├─ search()
     │  ├─ delete()
     │  ├─ get()
     │  └─ clear()
     │
     ├─ QdrantVectorStore
     │  ├─ add_documents()
     │  ├─ search()
     │  ├─ delete()
     │  ├─ get()
     │  └─ clear()
     │
     ├─ FAISSVectorStore
     │  ├─ add_documents()
     │  ├─ search()
     │  ├─ delete()
     │  ├─ get()
     │  └─ clear()
     │
     └─ [Future Providers]
        ├─ MilvusVectorStore
        ├─ PineconeVectorStore
        ├─ WeaviateVectorStore
        └─ ...
```

**Benefits**:
- Consistent API across providers
- Easy to switch implementations
- Easy to test (mock providers)
- Easy to add new providers

### Embedder Provider Pattern

```
BaseEmbedder (Abstract)
     ▲
     │ implements
     │
     ├─ SentenceTransformersEmbedder (default)
     │  ├─ embed_text()
     │  ├─ embed_batch()
     │  └─ dimension property
     │
     ├─ [Future Providers]
     │  ├─ OpenAIEmbedder
     │  ├─ ClaudeEmbedder
     │  ├─ CohereEmbedder
     │  └─ ...
```

---

## Deployment Architectures

### Development (Single Machine)

```
┌──────────────────────┐
│   Your Application   │
│   using RAGClient    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   RAGClient (in-mem) │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  ChromaDB (in-memory)│
│  or persistent       │
└──────────────────────┘
```

### Production Single-Node

```
┌──────────────────────┐
│   Your Application   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   RAGClient          │
│   (Async-ready)      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Qdrant Server       │
│  (Persistent Store)  │
└──────────────────────┘
```

### Production Distributed (Kubernetes)

```
┌────────────────────────────────────────┐
│         Ingress / Load Balancer        │
└─────────────────┬──────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Pod 1    │ │ Pod 2    │ │ Pod 3    │
│RAGClient │ │RAGClient │ │RAGClient │
└────┬─────┘ └────┬─────┘ └────┬─────┘
     └──────────┬──────────────┘
                │
                ▼
     ┌──────────────────────┐
     │ Qdrant StatefulSet   │
     │ (Replicated Cluster) │
     │                      │
     │ Node 1 │ Node 2 │ ...│
     │ (Master)(Replica)   │
     └──────────────────────┘
```

---

## Module Dependencies

```
socratic_rag/
│
├── __init__.py
│   └─ Exports: RAGClient, AsyncRAGClient, LLMPoweredRAG, models, exceptions
│
├── models.py
│   ├─ Document
│   ├─ Chunk
│   ├─ SearchResult
│   └─ RAGConfig
│
├── exceptions.py
│   ├─ SocraticRAGError
│   ├─ ConfigurationError
│   ├─ VectorStoreError
│   └─ ...
│
├── client.py
│   └─ RAGClient (uses: embeddings, chunking, vector_stores, processors)
│
├── async_client.py
│   └─ AsyncRAGClient (wraps RAGClient with asyncio)
│
├── llm_rag.py
│   └─ LLMPoweredRAG (uses: RAGClient, external LLM)
│
├── embeddings/
│   ├─ base.py (BaseEmbedder)
│   └─ sentence_transformers.py (SentenceTransformersEmbedder)
│
├── chunking/
│   ├─ base.py (BaseChunker)
│   └─ fixed_size.py (FixedSizeChunker)
│
├── vector_stores/
│   ├─ base.py (BaseVectorStore)
│   ├─ chromadb.py (ChromaDBVectorStore)
│   ├─ qdrant.py (QdrantVectorStore)
│   └─ faiss.py (FAISSVectorStore)
│
├── processors/
│   ├─ base.py (BaseDocumentProcessor)
│   ├─ text.py (TextProcessor)
│   ├─ pdf.py (PDFProcessor)
│   └─ markdown.py (MarkdownProcessor)
│
├── integrations/
│   ├─ openclaw/skill.py (SocraticRAGSkill)
│   └─ langchain/retriever.py (SocraticRAGRetriever)
│
└── utils/
    ├─ cache.py (EmbeddingCache with LRU)
    └─ text.py (Text utilities)
```

---

## Configuration & Runtime Setup

```
RAGConfig
  ├─ vector_store: str           (chromadb, qdrant, faiss)
  ├─ embedder: str               (sentence-transformers, ...)
  ├─ chunking_strategy: str      (fixed, semantic, recursive)
  ├─ chunk_size: int             (512 default)
  ├─ chunk_overlap: int          (50 default)
  ├─ top_k: int                  (5 default)
  ├─ embedding_cache: bool       (True default)
  ├─ cache_ttl: int              (3600 seconds default)
  └─ collection_name: str        (socratic_rag default)
         │
         ▼
     RAGClient.__init__(config)
         │
         ├─ Lazy init: embedder
         ├─ Lazy init: chunker
         ├─ Lazy init: vector_store
         │
         └─ Ready for operations:
            ├─ add_document()
            ├─ search()
            ├─ retrieve_context()
            └─ clear()
```

---

## Error Handling Flow

```
User Operation
   │
   ▼
Try Operation
   │
   ├─ Success ──────────► Return Result
   │
   └─ Exception
         │
         ├─ ConfigurationError ───────► Missing/invalid config
         ├─ VectorStoreError ──────────► Store connection/operation failed
         ├─ EmbeddingError ────────────► Embedding generation failed
         ├─ ChunkingError ─────────────► Chunking failed
         ├─ ProcessorError ────────────► Document processing failed
         ├─ DocumentNotFoundError ─────► Document doesn't exist
         ├─ ProviderNotFoundError ─────► Provider not available
         ├─ InvalidProviderError ──────► Provider not recognized
         └─ AsyncRAGError ─────────────► Async operation failed
                │
                ▼
           Log error with context
                │
                ▼
           Raise to user
```

---

## Performance Optimization Flow

```
Slower                              Faster
(↓ throughput)                      (↑ throughput)
   │                                   │
   ├─ Larger chunks ◄─────────────────┤
   │  (512 → 1024)                     │
   │                                   │
   ├─ Disable cache ◄─────────────────┤
   │                                   │
   ├─ Use Qdrant ◄──────────────────────── Use FAISS
   │                                   │
   ├─ Smaller top_k ◄─────────────────┤
   │  (20 → 5)                         │
   │                                   │
   └─ Use async ◄──────────────────────┤
      (AsyncRAGClient)                 │
```

---

## Integration Points

### With LangChain

```
LangChain Application
         │
         ├─ RetrievalQA
         │  └─ Uses: Retriever
         │
         ▼
SocraticRAGRetriever
  (implements: BaseRetriever)
         │
         ▼
RAGClient.search()
         │
         ▼
Return: LangChain Document objects
```

### With Openclaw

```
Openclaw Workflow
         │
         ├─ Uses: Skills
         │
         ▼
SocraticRAGSkill
  ├─ add_document()
  ├─ search()
  └─ retrieve_context()
         │
         ▼
RAGClient
         │
         ▼
Return: Results to Workflow
```

### With Socrates Nexus

```
User Application
         │
         ▼
LLMPoweredRAG
  ├─ RAGClient (for retrieval)
  └─ LLMClient (from Socrates Nexus)
         │
         ├─ Retrieve context
         │  └─ RAGClient.search()
         │
         ├─ Generate prompt
         │
         └─ Call LLM
            └─ LLMClient.chat()
                    │
                    ▼
               Return: Generated answer
```

---

## Async Execution Flow

```
Sync Operations               Async Operations
(sequential)                  (concurrent)

User
 │
 ├─ Query 1                  User
 │   └─ 20ms                  │
 │      Response              ├─ Query 1
 │                            │  ├─ 20ms
 ├─ Query 2                   │  │  (parallel)
 │   └─ 20ms                  │  │
 │      Response              ├─ Query 2
 │                            │  └─ 20ms
 └─ Query 3                   │
    └─ 20ms                   └─ Query 3
       Response                  └─ 20ms

Total: 60ms                   Total: ~20ms (3x faster)
```

---

**Last Updated**: March 10, 2024
**Version**: 0.1.0
