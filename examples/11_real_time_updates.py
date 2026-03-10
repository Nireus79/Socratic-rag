"""
Example: Real-Time Knowledge Base Updates

This example demonstrates real-time updates to the RAG knowledge base:
1. Dynamic document addition/removal
2. Incremental indexing
3. Change notifications
4. Version-aware retrieval

Run with:
    python examples/11_real_time_updates.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Callable, Set
from enum import Enum
import asyncio
from socratic_rag import RAGClient, AsyncRAGClient, RAGConfig


class UpdateType(Enum):
    """Type of update to knowledge base."""
    DOCUMENT_ADDED = "document_added"
    DOCUMENT_REMOVED = "document_removed"
    DOCUMENT_UPDATED = "document_updated"
    BATCH_ADDED = "batch_added"
    CLEARED = "cleared"


@dataclass
class Update:
    """A knowledge base update event."""
    update_type: UpdateType
    timestamp: datetime
    document_id: str
    content: Optional[str] = None
    source: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"[{self.timestamp.isoformat()}] "
            f"{self.update_type.value}: {self.source or self.document_id}"
        )


class UpdateListener:
    """Listen to and handle knowledge base updates."""

    def __init__(self, name: str):
        self.name = name
        self.updates: List[Update] = []

    def on_update(self, update: Update) -> None:
        """Handle an update."""
        self.updates.append(update)
        print(f"[{self.name}] {update}")

    def get_updates(self) -> List[Update]:
        """Get all received updates."""
        return self.updates

    def clear_updates(self) -> None:
        """Clear update history."""
        self.updates = []


class VersionedRAGClient:
    """RAG client with versioning and update tracking."""

    def __init__(self, config: RAGConfig):
        self.client = RAGClient(config)
        self.version = 0
        self.document_versions: Dict[str, int] = {}
        self.update_history: List[Update] = []
        self.listeners: List[UpdateListener] = []

    def subscribe(self, listener: UpdateListener) -> None:
        """Subscribe to updates."""
        self.listeners.append(listener)

    def unsubscribe(self, listener: UpdateListener) -> None:
        """Unsubscribe from updates."""
        self.listeners.remove(listener)

    def _notify_listeners(self, update: Update) -> None:
        """Notify all listeners of an update."""
        for listener in self.listeners:
            listener.on_update(update)

    def add_document(self, content: str, source: str) -> str:
        """Add document and track version."""
        doc_id = self.client.add_document(content, source)

        # Update version tracking
        self.version += 1
        self.document_versions[doc_id] = self.version

        # Record update
        update = Update(
            update_type=UpdateType.DOCUMENT_ADDED,
            timestamp=datetime.utcnow(),
            document_id=doc_id,
            content=content,
            source=source
        )
        self.update_history.append(update)

        # Notify listeners
        self._notify_listeners(update)

        return doc_id

    def remove_document(self, doc_id: str) -> bool:
        """Remove document."""
        try:
            self.client.vector_store.delete([doc_id])

            # Update tracking
            self.version += 1
            if doc_id in self.document_versions:
                del self.document_versions[doc_id]

            # Record update
            update = Update(
                update_type=UpdateType.DOCUMENT_REMOVED,
                timestamp=datetime.utcnow(),
                document_id=doc_id
            )
            self.update_history.append(update)

            # Notify listeners
            self._notify_listeners(update)

            return True
        except Exception as e:
            print(f"Error removing document: {e}")
            return False

    def add_batch(self, documents: List[dict]) -> List[str]:
        """Add multiple documents at once."""
        doc_ids = []
        for doc in documents:
            doc_id = self.add_document(doc["content"], doc["source"])
            doc_ids.append(doc_id)

        # Single batch update notification
        update = Update(
            update_type=UpdateType.BATCH_ADDED,
            timestamp=datetime.utcnow(),
            document_id="batch",
            metadata={"count": len(doc_ids), "ids": doc_ids}
        )
        self._notify_listeners(update)

        return doc_ids

    def get_version(self) -> int:
        """Get current knowledge base version."""
        return self.version

    def get_update_history(self) -> List[Update]:
        """Get all updates."""
        return self.update_history

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """Search with version info."""
        results = self.client.search(query, top_k=top_k)
        return [
            {
                "text": r.chunk.text,
                "score": r.score,
                "document_id": r.chunk.document_id,
                "version_added": self.document_versions.get(
                    r.chunk.document_id, "unknown"
                )
            }
            for r in results
        ]

    def clear(self) -> None:
        """Clear all documents."""
        self.client.clear()

        # Track clearing
        self.version += 1
        update = Update(
            update_type=UpdateType.CLEARED,
            timestamp=datetime.utcnow(),
            document_id="all"
        )
        self.update_history.append(update)

        # Notify listeners
        self._notify_listeners(update)


class ChangeTracker:
    """Track changes to documents."""

    def __init__(self):
        self.added: Set[str] = set()
        self.removed: Set[str] = set()
        self.updated: Set[str] = set()

    def track_add(self, doc_id: str) -> None:
        """Track document addition."""
        self.added.add(doc_id)
        # Remove from removed if it was previously deleted
        self.removed.discard(doc_id)

    def track_remove(self, doc_id: str) -> None:
        """Track document removal."""
        self.removed.add(doc_id)
        self.added.discard(doc_id)

    def track_update(self, doc_id: str) -> None:
        """Track document update."""
        if doc_id not in self.added:
            self.updated.add(doc_id)

    def get_summary(self) -> Dict[str, int]:
        """Get summary of changes."""
        return {
            "added": len(self.added),
            "removed": len(self.removed),
            "updated": len(self.updated),
            "total_changes": len(self.added) + len(self.removed) + len(self.updated)
        }

    def reset(self) -> None:
        """Reset tracking."""
        self.added.clear()
        self.removed.clear()
        self.updated.clear()


class IncrementalIndexer:
    """Incrementally index documents as they arrive."""

    def __init__(self, client: RAGClient, batch_size: int = 10):
        self.client = client
        self.batch_size = batch_size
        self.queue: List[dict] = []
        self.indexed_count = 0

    def queue_document(self, content: str, source: str) -> None:
        """Queue document for indexing."""
        self.queue.append({
            "content": content,
            "source": source
        })

        # Auto-flush if batch size reached
        if len(self.queue) >= self.batch_size:
            self.flush()

    def flush(self) -> int:
        """Index all queued documents."""
        count = 0
        for doc in self.queue:
            self.client.add_document(doc["content"], doc["source"])
            count += 1

        self.indexed_count += count
        self.queue.clear()

        return count

    def get_pending(self) -> int:
        """Get count of pending documents."""
        return len(self.queue)

    def get_indexed(self) -> int:
        """Get total indexed count."""
        return self.indexed_count


def demo_versioned_rag():
    """Demonstrate versioned RAG with tracking."""
    print("=" * 60)
    print("Versioned RAG with Update Tracking Demo")
    print("=" * 60)

    # Setup
    config = RAGConfig(vector_store="chromadb")
    rag = VersionedRAGClient(config)

    # Create listeners
    listener1 = UpdateListener("Listener1")
    listener2 = UpdateListener("Listener2")

    rag.subscribe(listener1)
    rag.subscribe(listener2)

    # Add documents
    print("\n1. Adding documents...\n")
    rag.add_document("Python is a programming language", "python.txt")
    rag.add_document("JavaScript runs in browsers", "javascript.txt")
    rag.add_document("Java is used for enterprise apps", "java.txt")

    print(f"\nCurrent version: {rag.get_version()}")

    # Search
    print("\n2. Searching...\n")
    results = rag.search("programming", top_k=2)
    for result in results:
        print(f"  - {result['text'][:50]}... (v{result['version_added']})")

    # Remove a document
    print("\n3. Removing a document...\n")
    all_docs = list(rag.document_versions.keys())
    if all_docs:
        rag.remove_document(all_docs[0])

    print(f"\nCurrent version: {rag.get_version()}")

    # Show update history
    print("\n4. Update History:\n")
    for update in rag.get_update_history():
        print(f"  {update}")

    # Show listener updates
    print("\n5. Listener1 Received:\n")
    for update in listener1.get_updates():
        print(f"  {update}")


def demo_change_tracking():
    """Demonstrate change tracking."""
    print("\n" + "=" * 60)
    print("Change Tracking Demo")
    print("=" * 60)

    tracker = ChangeTracker()

    print("\n1. Tracking changes...\n")

    # Simulate changes
    tracker.track_add("doc1")
    tracker.track_add("doc2")
    tracker.track_add("doc3")
    print("Added 3 documents")

    tracker.track_remove("doc2")
    print("Removed 1 document")

    tracker.track_update("doc1")
    print("Updated 1 document")

    # Show summary
    print("\n2. Change Summary:\n")
    summary = tracker.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")


def demo_incremental_indexing():
    """Demonstrate incremental indexing."""
    print("\n" + "=" * 60)
    print("Incremental Indexing Demo")
    print("=" * 60)

    # Setup
    config = RAGConfig(vector_store="chromadb")
    client = RAGClient(config)
    indexer = IncrementalIndexer(client, batch_size=3)

    print("\n1. Queuing documents...\n")

    # Queue documents
    documents = [
        ("Document 1 content", "doc1.txt"),
        ("Document 2 content", "doc2.txt"),
        ("Document 3 content", "doc3.txt"),
        ("Document 4 content", "doc4.txt"),
        ("Document 5 content", "doc5.txt"),
    ]

    for content, source in documents:
        print(f"Queuing: {source}")
        indexer.queue_document(content, source)
        print(f"  Pending: {indexer.get_pending()}")

        if indexer.get_pending() % 3 == 0:
            print(f"  → Flushing batch (auto)...")

    # Final flush
    print(f"\n2. Final flush...\n")
    remaining = indexer.flush()
    print(f"Indexed {remaining} remaining documents")

    # Show stats
    print(f"\n3. Statistics:\n")
    print(f"  Total indexed: {indexer.get_indexed()}")
    print(f"  Pending: {indexer.get_pending()}")


if __name__ == "__main__":
    demo_versioned_rag()
    demo_change_tracking()
    demo_incremental_indexing()
