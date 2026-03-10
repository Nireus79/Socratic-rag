"""
Example: REST API with FastAPI

This example demonstrates wrapping Socratic RAG in a REST API using FastAPI.
Useful for deploying RAG as a service that other applications can consume.

Run with:
    pip install socratic-rag fastapi uvicorn
    python examples/06_rest_api.py

Then test with curl:
    # Add a document
    curl -X POST http://localhost:8000/documents \
      -H "Content-Type: application/json" \
      -d '{"content": "Python is great for AI", "source": "ai.txt"}'

    # Search documents
    curl "http://localhost:8000/search?query=Python&top_k=5"

    # Get health check
    curl http://localhost:8000/health
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from socratic_rag import RAGClient, RAGConfig
import uvicorn


# Pydantic models for request/response
class DocumentRequest(BaseModel):
    """Request model for adding documents."""
    content: str
    source: str
    metadata: Optional[dict] = None


class SearchRequest(BaseModel):
    """Request model for search."""
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    """Response model for search results."""
    text: str
    score: float
    document_id: str
    source: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    message: str


# Initialize FastAPI app
app = FastAPI(
    title="Socratic RAG API",
    description="REST API for Retrieval-Augmented Generation",
    version="1.0.0"
)

# Initialize RAG client (with ChromaDB by default)
rag_client = RAGClient(
    RAGConfig(
        vector_store="chromadb",
        embedder="sentence-transformers",
        chunk_size=512,
        top_k=5
    )
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Socratic RAG API is running"
    )


@app.post("/documents")
async def add_document(request: DocumentRequest) -> dict:
    """
    Add a document to the RAG knowledge base.

    Args:
        request: Document content and metadata

    Returns:
        Document ID and status
    """
    try:
        doc_id = rag_client.add_document(
            content=request.content,
            source=request.source,
            metadata=request.metadata
        )
        return {
            "status": "success",
            "document_id": doc_id,
            "message": f"Document added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/search", response_model=List[SearchResult])
async def search(
    query: str,
    top_k: Optional[int] = 5
) -> List[SearchResult]:
    """
    Search for relevant documents.

    Args:
        query: Search query
        top_k: Number of results to return

    Returns:
        List of search results with scores
    """
    try:
        results = rag_client.search(query, top_k=top_k)
        return [
            SearchResult(
                text=result.chunk.text,
                score=result.score,
                document_id=result.chunk.document_id,
                source=result.chunk.metadata.get("source", "unknown")
            )
            for result in results
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/context")
async def retrieve_context(request: SearchRequest) -> dict:
    """
    Retrieve formatted context for LLM.

    Args:
        request: Query and optional top_k

    Returns:
        Formatted context string
    """
    try:
        context = rag_client.retrieve_context(
            query=request.query,
            top_k=request.top_k
        )
        return {
            "query": request.query,
            "context": context,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/documents")
async def clear_documents() -> dict:
    """Clear all documents from the knowledge base."""
    try:
        rag_client.clear()
        return {
            "status": "success",
            "message": "All documents cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    # Run the API server
    print("Starting Socratic RAG API on http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
