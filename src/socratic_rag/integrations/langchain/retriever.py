"""LangChain retriever integration."""

from typing import Any, List

from ...client import RAGClient


class SocraticRAGRetriever:
    """LangChain-compatible retriever using Socratic RAG.

    This retriever integrates Socratic RAG with LangChain for
    use in chains and agents.
    """

    def __init__(
        self,
        client: RAGClient,
        top_k: int = 5,
    ) -> None:
        """Initialize LangChain retriever.

        Args:
            client: RAGClient instance to use for retrieval.
            top_k: Number of results to return.
        """
        self.client = client
        self.top_k = top_k

    def _get_relevant_documents(self, query: str) -> List[Any]:
        """Get documents relevant to query.

        This method returns documents in a format compatible with LangChain.

        Args:
            query: Search query.

        Returns:
            List of LangChain Document objects.

        Raises:
            ImportError: If langchain is not installed.
        """
        try:
            # Try newer langchain API first
            try:
                from langchain_core.documents import Document as LCDocument
            except ImportError:
                # Fall back to older API
                from langchain.schema import Document as LCDocument
        except ImportError:
            raise ImportError(
                "langchain is required for LangChain integration. "
                "Install with: pip install langchain"
            )

        results = self.client.search(query, top_k=self.top_k)

        documents = [
            LCDocument(
                page_content=r.chunk.text,
                metadata={
                    "chunk_id": r.chunk.chunk_id,
                    "document_id": r.chunk.document_id,
                    "score": r.score,
                    "source": r.chunk.metadata.get("source", "unknown"),
                    **r.chunk.metadata,
                },
            )
            for r in results
        ]

        return documents

    def get_relevant_documents(self, query: str) -> List[Any]:
        """Public method for getting relevant documents.

        Args:
            query: Search query.

        Returns:
            List of LangChain Document objects.
        """
        return self._get_relevant_documents(query)
