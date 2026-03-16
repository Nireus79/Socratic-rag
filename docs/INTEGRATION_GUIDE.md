# Socratic RAG - Integration Guide

## Socrates Nexus Integration

RAG uses Socrates Nexus for embeddings and answer generation.

```python
from socratic_rag import RAGClient
from socrates_nexus import LLMClient

# RAG retrieves documents
rag = RAGClient()
documents = rag.search("user query", top_k=5)

# Socrates Nexus generates answer
llm = LLMClient(provider="anthropic", model="claude-opus")
context = rag.retrieve_context("user query")
response = llm.chat(f"Context: {context}\nAnswer: user query")
```

## Openclaw Integration

```python
from socratic_rag.integrations.openclaw import SocraticRAGSkill

skill = SocraticRAGSkill(vector_store="chromadb")
results = skill.search("query")
```

## LangChain Integration

```python
from socratic_rag.integrations.langchain import SocraticRAGRetriever
from langchain.chains import RetrievalQA

retriever = SocraticRAGRetriever(rag_client=rag, top_k=5)
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
```

## Custom Integration

Implement custom retriever:
```python
class CustomRetriever:
    def __init__(self, rag_client):
        self.rag = rag_client
    
    def retrieve(self, query):
        return self.rag.search(query, top_k=5)
```
