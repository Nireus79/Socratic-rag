"""LLM-powered RAG client using Socrates Nexus integration."""

from typing import Any, Dict, Optional

from .client import RAGClient
from .exceptions import SocraticRAGError


class LLMPoweredRAG:
    """RAG with LLM for answer generation.

    Combines document retrieval with LLM-powered answer generation
    using Socrates Nexus LLM client.
    """

    def __init__(
        self,
        rag_client: RAGClient,
        llm_client: Optional[Any] = None,
    ) -> None:
        """Initialize LLM-powered RAG.

        Args:
            rag_client: RAGClient instance for retrieval.
            llm_client: Socrates Nexus LLMClient instance.
                If None, LLM features will not be available.

        Raises:
            SocraticRAGError: If initialization fails.
        """
        self.rag = rag_client
        self.llm = llm_client

    def generate_answer(
        self,
        query: str,
        top_k: Optional[int] = None,
        context_prefix: str = "Context:\n",
        context_separator: str = "\n\n",
        system_prompt: Optional[str] = None,
        **llm_kwargs: Any,
    ) -> str:
        """Generate answer using RAG + LLM.

        Retrieves relevant documents and uses LLM to generate an answer
        based on the retrieved context.

        Args:
            query: Question to answer.
            top_k: Number of context documents to retrieve.
            context_prefix: Prefix for context section.
            context_separator: Separator between context documents.
            system_prompt: Custom system prompt for the LLM.
            **llm_kwargs: Additional arguments passed to LLM.

        Returns:
            Generated answer string.

        Raises:
            SocraticRAGError: If LLM is not configured or generation fails.
        """
        if not self.llm:
            raise SocraticRAGError(
                "LLM client is not configured. "
                "Provide llm_client when initializing LLMPoweredRAG."
            )

        # Retrieve context
        context = self.rag.retrieve_context(query, top_k=top_k)

        # Build prompt
        if not context:
            context = "No relevant documents found."

        prompt_parts = [context_prefix + context]

        if system_prompt:
            full_prompt = f"{system_prompt}\n\n" + context_separator.join(prompt_parts)
        else:
            full_prompt = context_separator.join(prompt_parts)

        full_prompt += f"\n\nQuestion: {query}\n\nAnswer:"

        # Generate answer with LLM
        try:
            response = self.llm.chat(full_prompt, **llm_kwargs)
            return response.content if hasattr(response, "content") else str(response)
        except AttributeError as e:
            raise SocraticRAGError(
                f"LLM client does not have expected interface. "
                f"Ensure it's a Socrates Nexus LLMClient. Error: {e}"
            )
        except Exception as e:
            raise SocraticRAGError(f"Failed to generate answer: {e}")

    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> str:
        """Retrieve context for a query.

        Args:
            query: Query string.
            top_k: Number of results to retrieve.

        Returns:
            Formatted context string.
        """
        return self.rag.retrieve_context(query, top_k=top_k)

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> list:
        """Search for documents.

        Args:
            query: Search query.
            top_k: Number of results to return.
            filters: Optional metadata filters.

        Returns:
            List of SearchResult objects.
        """
        return self.rag.search(query, top_k=top_k, filters=filters)

    def add_document(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add document to knowledge base.

        Args:
            content: Document content.
            source: Document source.
            metadata: Optional metadata.

        Returns:
            Document ID.
        """
        return self.rag.add_document(content, source, metadata)

    def clear(self) -> bool:
        """Clear knowledge base.

        Returns:
            True if successful.
        """
        return self.rag.clear()
