# Integrations Guide

Learn how to integrate Socratic RAG with popular frameworks.

## Openclaw Integration

### Installation

```bash
pip install socratic-rag[openclaw]
```

### Creating a Skill

```python
from socratic_rag.integrations.openclaw import SocraticRAGSkill

# Create skill with defaults
skill = SocraticRAGSkill()

# Or customize
skill = SocraticRAGSkill(
    vector_store="chromadb",
    chunk_size=512,
    top_k=5,
)
```

### Basic Usage

```python
from socratic_rag.integrations.openclaw import SocraticRAGSkill

skill = SocraticRAGSkill()

# Add documents
doc_id = skill.add_document(
    content="Python is great",
    source="python.txt",
    metadata={"topic": "programming"}
)

# Search
results = skill.search("Python", top_k=3)
# Returns: [
#     {"text": "...", "score": 0.95, "metadata": {...}},
#     ...
# ]

# Get formatted context
context = skill.retrieve_context("Python")

# Clear
skill.clear()
```

### Skill Methods

#### add_document

```python
doc_id = skill.add_document(
    content: str,          # Document content
    source: str,           # Document source/identifier
    metadata: dict = None  # Optional metadata
) -> str  # Document ID
```

#### search

```python
results = skill.search(
    query: str,           # Search query
    top_k: int = None     # Number of results
) -> List[Dict]  # Results with score, text, metadata
```

#### retrieve_context

```python
context = skill.retrieve_context(
    query: str,           # Search query
    top_k: int = None     # Number of results
) -> str  # Formatted context for LLM
```

#### clear

```python
success = skill.clear() -> bool  # Clear all documents
```

#### get_config

```python
config = skill.get_config() -> RAGConfig  # Get configuration
```

### Configuration Options

```python
skill = SocraticRAGSkill(
    vector_store="chromadb",       # Vector store to use
    embedder="sentence-transformers",  # Embedder to use
    chunking_strategy="fixed",     # Chunking strategy
    chunk_size=512,                # Characters per chunk
    chunk_overlap=50,              # Overlap between chunks
    top_k=5,                       # Default results count
    collection_name="socratic_rag" # Collection name
)
```

---

## LangChain Integration

### Installation

```bash
pip install socratic-rag[langchain]
pip install langchain
```

### Creating a Retriever

```python
from socratic_rag import RAGClient, RAGConfig
from socratic_rag.integrations.langchain import SocraticRAGRetriever

# Create RAG client
config = RAGConfig(
    vector_store="chromadb",
    chunk_size=512,
)
rag_client = RAGClient(config)

# Create retriever
retriever = SocraticRAGRetriever(
    client=rag_client,
    top_k=5
)
```

### Using in RetrievalQA Chain

```python
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatAnthropic

# Create chain
llm = ChatAnthropic(model="claude-sonnet")
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",  # or "map_reduce", "refine", etc.
    verbose=True
)

# Ask questions
answer = qa.run("What is Python?")
print(answer)
```

### Using in Conversational Chain

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet")
chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    verbose=True
)

# Track conversation history
chat_history = []

# First turn
result = chain({"question": "What is machine learning?", "chat_history": chat_history})
chat_history.append((result["question"], result["answer"]))

# Second turn (with history)
result = chain({"question": "Tell me more about it", "chat_history": chat_history})
chat_history.append((result["question"], result["answer"]))
```

### Using in Custom Chain

```python
from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet")

def custom_rag_chain(question):
    # Get documents
    docs = retriever.get_relevant_documents(question)
    context = "\n".join([d.page_content for d in docs])

    # Create messages
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=f"Context: {context}\n\nQuestion: {question}")
    ]

    # Get response
    response = llm(messages)
    return response.content

answer = custom_rag_chain("What is Python?")
```

### Retriever Methods

#### get_relevant_documents

```python
documents = retriever.get_relevant_documents(query: str) -> List[Document]
```

Returns LangChain Document objects with:
- `page_content`: The chunk text
- `metadata`: Metadata including score, source, etc.

#### Example Document Structure

```python
{
    "page_content": "Python is a programming language",
    "metadata": {
        "chunk_id": "uuid-1234",
        "document_id": "uuid-5678",
        "score": 0.95,
        "source": "python.txt"
    }
}
```

---

## Socrates Nexus Integration (v0.2.0+)

### Installation

```bash
pip install socratic-rag[nexus]
pip install socrates-nexus
```

### Using LLM Client

```python
from socratic_rag import RAGClient, LLMPoweredRAG
from socrates_nexus import LLMClient

# Initialize RAG
rag_client = RAGClient()
rag_client.add_document("Python is great", "python.txt")

# Initialize LLM
llm_client = LLMClient(
    provider="anthropic",
    model="claude-sonnet"
)

# Combine
llm_rag = LLMPoweredRAG(rag_client, llm_client)

# Generate answers
answer = llm_rag.generate_answer("What is Python?")
```

### Custom System Prompt

```python
system_prompt = """You are an expert programmer.
Answer questions based on the provided context.
If the context doesn't contain the answer, say so."""

answer = llm_rag.generate_answer(
    "What is Python?",
    system_prompt=system_prompt
)
```

### Context Formatting

```python
answer = llm_rag.generate_answer(
    "What is Python?",
    context_prefix="Reference Materials:\n",
    context_separator="\n---\n",
    top_k=3
)
```

---

## Comparison

| Feature | Openclaw | LangChain | Nexus |
|---------|----------|-----------|-------|
| Purpose | Workflow | Chains | LLM Client |
| Learning | Easy | Medium | Medium |
| Flexibility | Basic | High | High |
| Integration | Direct | Via Retriever | Direct |
| Ecosystem | Openclaw | Large | Socrates |

---

## Integration Patterns

### Pattern 1: Simple Search

```python
# Openclaw
results = skill.search("query")

# LangChain
docs = retriever.get_relevant_documents("query")

# Both return similar structures with score/relevance
```

### Pattern 2: Context for LLM

```python
# All frameworks support this
context = skill.retrieve_context("query")
# context is formatted and ready for LLM input
```

### Pattern 3: Full Answer Generation

```python
# Openclaw (basic)
context = skill.retrieve_context("query")
# Pass context to LLM separately

# LangChain (via chain)
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
answer = qa.run("query")

# Nexus (direct)
llm_rag = LLMPoweredRAG(rag_client, llm_client)
answer = llm_rag.generate_answer("query")
```

---

## Troubleshooting

### LangChain Retriever No Results

```python
# Check if documents are in RAG client
results = rag_client.search("test")
print(f"Found {len(results)} results")

# Try increasing top_k
retriever = SocraticRAGRetriever(client=rag_client, top_k=10)

# Check retrieval quality
docs = retriever.get_relevant_documents("your query")
print(f"Retrieved {len(docs)} documents")
```

### OpenClaw Skill Not Working

```python
# Check if skill was properly initialized
skill = SocraticRAGSkill()
config = skill.get_config()
print(config)

# Verify documents were added
search_results = skill.search("test")
print(f"Found {len(search_results)} results")
```

### Performance Issues

```python
# Reduce chunk size for faster search
skill = SocraticRAGSkill(chunk_size=256)

# Use FAISS for speed
skill = SocraticRAGSkill(vector_store="faiss")

# Reduce top_k
results = skill.search("query", top_k=3)
```

---

## Best Practices

### 1. Document Organization

```python
# Add metadata for filtering and context
skill.add_document(
    content="...",
    source="document.txt",
    metadata={
        "category": "python",
        "author": "John",
        "date": "2024-03-10"
    }
)
```

### 2. Query Design

```python
# Good: Specific queries
"What are the benefits of using Python for data science?"

# Bad: Too vague
"Tell me about Python"
```

### 3. Chunk Size Tuning

```python
# For dense technical docs
config = RAGConfig(chunk_size=256)

# For narrative/story content
config = RAGConfig(chunk_size=1024)
```

### 4. System Prompts

```python
# Custom prompt for specific domain
system_prompt = "You are a Python expert. Answer questions based only on the provided documentation."

answer = llm_rag.generate_answer(
    query,
    system_prompt=system_prompt
)
```

### 5. Error Handling

```python
from socratic_rag.exceptions import SocraticRAGError

try:
    answer = llm_rag.generate_answer("query")
except SocraticRAGError as e:
    print(f"RAG Error: {e}")
    # Handle gracefully
```

---

## See Also

- [Quickstart Guide](quickstart.md)
- [API Reference](api-reference.md)
- [Examples](../examples/)
- [LangChain Docs](https://python.langchain.com/)
- [Openclaw Docs](https://openclaw.dev/)
