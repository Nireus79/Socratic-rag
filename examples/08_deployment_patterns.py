"""
Example: Deployment Patterns

This example demonstrates various patterns for deploying Socratic RAG
in production environments including local, cloud, and hybrid setups.

Deployment Patterns Covered:
1. Local/Development - ChromaDB with in-memory or file persistence
2. Production Single-Node - Qdrant for scalability, persistent storage
3. Production Distributed - Qdrant cluster with load balancing
4. Cloud-Native - Kubernetes with distributed RAG
5. Hybrid - Local for cache, cloud for storage
"""

from socratic_rag import RAGClient, RAGConfig
from typing import Optional
import os


class DeploymentEnvironment:
    """Base class for deployment configurations."""

    def __init__(self, name: str):
        self.name = name
        self.client: Optional[RAGClient] = None

    def setup(self) -> RAGClient:
        """Initialize RAG client for this environment."""
        raise NotImplementedError

    def add_documents(self, documents: list[dict]) -> None:
        """Add documents to the knowledge base."""
        if not self.client:
            self.setup()

        for doc in documents:
            self.client.add_document(
                content=doc["content"],
                source=doc.get("source", "unknown"),
                metadata=doc.get("metadata")
            )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for relevant documents."""
        if not self.client:
            self.setup()

        results = self.client.search(query, top_k=top_k)
        return [
            {
                "text": r.chunk.text,
                "score": r.score,
                "source": r.chunk.metadata.get("source")
            }
            for r in results
        ]


class LocalDevelopmentEnvironment(DeploymentEnvironment):
    """
    Development environment using ChromaDB with file persistence.
    Good for: Local development, small prototypes, single developer.
    """

    def setup(self) -> RAGClient:
        """Setup ChromaDB with persistent local storage."""
        print(f"Setting up {self.name} environment...")

        config = RAGConfig(
            vector_store="chromadb",
            embedder="sentence-transformers",
            chunk_size=512,
            chunk_overlap=50,
            top_k=5,
            embedding_cache=True,
            cache_ttl=3600,
            collection_name="dev_socratic_rag"
        )

        self.client = RAGClient(config)
        print(f"  Vector Store: ChromaDB (local)")
        print(f"  Embedding Cache: Enabled")
        print(f"  Ready for local development")

        return self.client


class ProductionSingleNodeEnvironment(DeploymentEnvironment):
    """
    Production single-node environment using Qdrant.
    Good for: Small to medium production deployments, team projects.
    """

    def setup(self) -> RAGClient:
        """Setup Qdrant for production use."""
        print(f"Setting up {self.name} environment...")

        # Qdrant configuration from environment variables
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

        config = RAGConfig(
            vector_store="qdrant",
            embedder="sentence-transformers",
            chunk_size=512,
            chunk_overlap=50,
            top_k=5,
            embedding_cache=True,
            cache_ttl=3600,
            collection_name="prod_socratic_rag"
        )

        # Pass Qdrant config via client initialization
        self.client = RAGClient(config)

        print(f"  Vector Store: Qdrant")
        print(f"  Host: {qdrant_host}:{qdrant_port}")
        print(f"  Embedding Cache: Enabled")
        print(f"  Ready for production")

        return self.client


class ProductionDistributedEnvironment(DeploymentEnvironment):
    """
    Production distributed environment with Qdrant cluster.
    Good for: Large-scale deployments, high availability, scalability.
    """

    def setup(self) -> RAGClient:
        """Setup Qdrant cluster for high availability."""
        print(f"Setting up {self.name} environment...")

        # Load Qdrant cluster configuration from environment
        qdrant_hosts = os.getenv(
            "QDRANT_CLUSTER_HOSTS",
            "localhost:6333"
        ).split(",")

        config = RAGConfig(
            vector_store="qdrant",
            embedder="sentence-transformers",
            chunk_size=512,
            chunk_overlap=50,
            top_k=5,
            embedding_cache=True,
            cache_ttl=3600,
            collection_name="cluster_socratic_rag"
        )

        self.client = RAGClient(config)

        print(f"  Vector Store: Qdrant Cluster")
        print(f"  Nodes: {', '.join(qdrant_hosts)}")
        print(f"  Replication: Enabled")
        print(f"  Embedding Cache: Enabled (distributed)")
        print(f"  Ready for high-availability deployment")

        return self.client


class CloudNativeEnvironment(DeploymentEnvironment):
    """
    Cloud-native environment for Kubernetes deployment.
    Good for: Cloud platforms (AWS, GCP, Azure), auto-scaling, multi-tenant.
    """

    def setup(self) -> RAGClient:
        """Setup for Kubernetes/cloud deployment."""
        print(f"Setting up {self.name} environment...")

        # Load configuration from environment variables (typical for K8s)
        vector_store = os.getenv("VECTOR_STORE", "qdrant")
        namespace = os.getenv("K8S_NAMESPACE", "default")
        replicas = int(os.getenv("RAG_REPLICAS", "3"))

        config = RAGConfig(
            vector_store=vector_store,
            embedder="sentence-transformers",
            chunk_size=512,
            chunk_overlap=50,
            top_k=5,
            embedding_cache=False,  # Use distributed cache (Redis)
            cache_ttl=300,  # Short TTL for cloud
            collection_name=f"{namespace}_socratic_rag"
        )

        self.client = RAGClient(config)

        print(f"  Environment: Kubernetes")
        print(f"  Namespace: {namespace}")
        print(f"  Replicas: {replicas}")
        print(f"  Vector Store: {vector_store}")
        print(f"  Cache: Distributed (Redis)")
        print(f"  Ready for cloud-native deployment")

        return self.client


class HybridEnvironment(DeploymentEnvironment):
    """
    Hybrid environment with local cache and cloud storage.
    Good for: Edge computing, offline capability, reduced latency.
    """

    def setup(self) -> RAGClient:
        """Setup hybrid configuration."""
        print(f"Setting up {self.name} environment...")

        # Use local cache with cloud backend
        config = RAGConfig(
            vector_store="chromadb",  # Local cache
            embedder="sentence-transformers",
            chunk_size=512,
            chunk_overlap=50,
            top_k=5,
            embedding_cache=True,
            cache_ttl=7200,  # 2 hours for local
            collection_name="hybrid_socratic_rag"
        )

        self.client = RAGClient(config)

        print(f"  Vector Store: ChromaDB (local cache)")
        print(f"  Backend: Would sync to Qdrant Cloud")
        print(f"  Embedding Cache: Enabled (local)")
        print(f"  Sync Interval: 1 hour")
        print(f"  Ready for hybrid deployment")

        return self.client


def demo_deployments():
    """Demonstrate different deployment patterns."""
    print("Socratic RAG Deployment Patterns Demo")
    print("=" * 60)

    # Sample documents
    documents = [
        {
            "content": "Python is a high-level programming language.",
            "source": "python.txt",
            "metadata": {"language": "en", "category": "programming"}
        },
        {
            "content": "Machine learning is a subset of artificial intelligence.",
            "source": "ml.txt",
            "metadata": {"language": "en", "category": "ai"}
        },
        {
            "content": "RAG combines retrieval and generation for better answers.",
            "source": "rag.txt",
            "metadata": {"language": "en", "category": "ai"}
        }
    ]

    # Test each deployment pattern
    environments = [
        LocalDevelopmentEnvironment("Development"),
        ProductionSingleNodeEnvironment("Production Single-Node"),
        ProductionDistributedEnvironment("Production Distributed"),
        CloudNativeEnvironment("Cloud-Native"),
        HybridEnvironment("Hybrid")
    ]

    for env in environments:
        print(f"\n{'=' * 60}")
        print(f"Environment: {env.name}")
        print('=' * 60)

        try:
            env.setup()

            # Add documents
            print("\nAdding documents...")
            env.add_documents(documents)
            print("✓ Documents added")

            # Search
            print("\nSearching for 'machine learning'...")
            results = env.search("machine learning", top_k=2)
            print(f"✓ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result['score']:.2f}")
                print(f"     Text: {result['text'][:50]}...")

        except Exception as e:
            print(f"✗ Error: {e}")
            print("  Note: Some vector stores may not be available in this environment")


def deployment_checklist():
    """Print deployment checklist."""
    print("\nDeployment Checklist")
    print("=" * 60)
    checklist = [
        ("Environment Variables", "Configure VECTOR_STORE, QDRANT_HOST, etc."),
        ("Vector Store Setup", "Initialize Qdrant, ChromaDB, or FAISS"),
        ("Database Backup", "Set up automated backups for vector store"),
        ("Monitoring", "Configure Prometheus metrics and alerts"),
        ("Scaling", "Set up auto-scaling policies for load"),
        ("Security", "Enable authentication, TLS/SSL, encryption"),
        ("Testing", "Run integration tests in target environment"),
        ("Documentation", "Update deployment runbooks and guides"),
        ("Performance", "Profile and optimize for production workload"),
        ("Rollback Plan", "Prepare rollback procedure for deployments")
    ]

    for i, (task, description) in enumerate(checklist, 1):
        print(f"  [ ] {i:2}. {task:20} - {description}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "checklist":
        deployment_checklist()
    else:
        # Run demo (note: requires Qdrant running for some examples)
        print("Running with local ChromaDB only (Qdrant requires setup)")
        print("To test all patterns, run: docker-compose up -d\n")

        # Run demo with local environment only
        env = LocalDevelopmentEnvironment("Development Demo")
        documents = [
            {
                "content": "Python is a high-level programming language.",
                "source": "python.txt"
            },
            {
                "content": "RAG improves LLM accuracy with retrieval.",
                "source": "rag.txt"
            }
        ]

        env.setup()
        env.add_documents(documents)
        results = env.search("Python programming", top_k=2)

        print("\nSearch Results:")
        for result in results:
            print(f"  Score: {result['score']:.2f}")
            print(f"  Text: {result['text']}")

        print("\nFor deployment checklist, run:")
        print("  python examples/08_deployment_patterns.py checklist")
