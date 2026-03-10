"""
Example: Docker Containerization

This example demonstrates packaging Socratic RAG in a Docker container
for consistent deployment across environments.

This file is a reference guide for creating Docker containers.
For actual usage, see the accompanying Dockerfile and docker-compose.yml.

Docker Setup Steps:

1. Create a Dockerfile:
    FROM python:3.11-slim

    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .

    CMD ["python", "-m", "examples.06_rest_api"]

2. Create requirements.txt with your dependencies

3. Build and run:
    docker build -t socratic-rag:latest .
    docker run -p 8000:8000 socratic-rag:latest

4. With docker-compose for more complex setups:
    docker-compose up -d

Reference Implementation:
"""

import os
from pathlib import Path
from socratic_rag import RAGClient, RAGConfig


def create_dockerfile_content() -> str:
    """Generate a Dockerfile for Socratic RAG REST API."""
    return '''FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port for API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["python", "-m", "uvicorn", "examples.06_rest_api:app", "--host", "0.0.0.0", "--port", "8000"]
'''


def create_docker_compose_content() -> str:
    """Generate a docker-compose.yml for multi-container setup."""
    return '''version: '3.8'

services:
  # Socratic RAG API service
  rag-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - VECTOR_STORE=chromadb
      - EMBEDDING_CACHE=true
    volumes:
      - ./data:/app/data
    depends_on:
      - chromadb
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  # ChromaDB vector store (optional - can use in-memory instead)
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chromadb_data:/chroma/chroma
    restart: unless-stopped

  # Optional: Qdrant vector store for larger deployments
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT_ALLOW_RECOVERY_MODE=true
    restart: unless-stopped
    # Uncomment to enable (modify docker-compose to use this)
    # profiles: ["with-qdrant"]

volumes:
  chromadb_data:
  qdrant_data:
'''


def create_requirements_content() -> str:
    """Generate a requirements.txt file."""
    return '''# Core dependencies
socratic-rag>=0.1.0

# REST API
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0

# Optional: Vector stores
chromadb>=0.4.0
qdrant-client>=2.0.0
faiss-cpu>=1.7.0

# Optional: Document processing
PyPDF2>=3.0.0
markdown>=3.0.0

# Optional: Framework integrations
langchain>=0.1.0

# Optional: Development
pytest>=7.0
pytest-asyncio>=0.21.0
'''


def save_docker_files(output_dir: str = ".") -> None:
    """Save Docker-related files to the specified directory."""
    output_path = Path(output_dir)

    # Save Dockerfile
    dockerfile_path = output_path / "Dockerfile"
    with open(dockerfile_path, "w") as f:
        f.write(create_dockerfile_content())
    print(f"Created {dockerfile_path}")

    # Save docker-compose.yml
    compose_path = output_path / "docker-compose.yml"
    with open(compose_path, "w") as f:
        f.write(create_docker_compose_content())
    print(f"Created {compose_path}")

    # Save requirements.txt
    requirements_path = output_path / "requirements.txt"
    with open(requirements_path, "w") as f:
        f.write(create_requirements_content())
    print(f"Created {requirements_path}")


def demo_in_container_usage() -> None:
    """
    Example of how to use Socratic RAG inside a Docker container.
    This function shows typical patterns for containerized RAG.
    """
    # Configuration from environment variables (typical in Docker)
    vector_store = os.getenv("VECTOR_STORE", "chromadb")
    chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
    top_k = int(os.getenv("TOP_K", "5"))

    print(f"Initializing RAG with vector store: {vector_store}")

    # Initialize client with configuration
    config = RAGConfig(
        vector_store=vector_store,
        chunk_size=chunk_size,
        top_k=top_k
    )

    client = RAGClient(config)

    # Add sample documents
    print("Adding sample documents...")
    client.add_document(
        "Docker is a containerization platform",
        "docker.txt"
    )
    client.add_document(
        "Kubernetes orchestrates Docker containers",
        "kubernetes.txt"
    )

    # Search
    print("Searching for 'container orchestration'...")
    results = client.search("container orchestration", top_k=2)

    for result in results:
        print(f"  Score: {result.score:.2f}")
        print(f"  Text: {result.chunk.text}")
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        # Generate Docker files
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        save_docker_files(output_dir)
        print("\nDocker files generated successfully!")
        print(f"Files created in: {output_dir}")
    else:
        # Run demo
        print("Socratic RAG Docker Containerization Demo")
        print("=" * 50)
        print("\nTo generate Docker files, run:")
        print("  python examples/07_docker_containerization.py generate")
        print("\nRunning in-container usage demo...")
        print("=" * 50)
        demo_in_container_usage()
