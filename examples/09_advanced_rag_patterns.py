"""
Example: Advanced RAG Patterns

This example demonstrates advanced patterns for using Socratic RAG:
1. Multi-agent RAG system
2. Question routing and classification
3. Context chaining and conversation
4. Fallback strategies for low-confidence results

Run with:
    python examples/09_advanced_rag_patterns.py
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
from socratic_rag import RAGClient, RAGConfig


class QueryType(Enum):
    """Classification of query types."""
    FACTUAL = "factual"          # What is X? / Definition
    PROCEDURAL = "procedural"    # How do I? / Steps
    EXPLANATORY = "explanatory"  # Why? / Explanation
    COMPARATIVE = "comparative"  # Compare X and Y
    UNKNOWN = "unknown"          # Can't classify


@dataclass
class QueryClassification:
    """Result of query classification."""
    query_type: QueryType
    confidence: float
    reasoning: str


@dataclass
class AgentResponse:
    """Response from an agent."""
    content: str
    confidence: float
    agent: str
    metadata: Dict[str, Any]


class QueryRouter:
    """Route queries to appropriate agents/handlers."""

    def __init__(self):
        self.factual_keywords = [
            "what is", "definition", "meaning", "explain",
            "tell me about", "how many", "when was"
        ]
        self.procedural_keywords = [
            "how do i", "how to", "steps to", "guide",
            "tutorial", "instructions", "process"
        ]
        self.explanatory_keywords = [
            "why", "reason", "because", "explain why",
            "motivation", "purpose"
        ]
        self.comparative_keywords = [
            "compare", "difference", "vs", "versus",
            "similar", "same", "different"
        ]

    def classify(self, query: str) -> QueryClassification:
        """Classify a query into a type."""
        query_lower = query.lower()

        # Check for keyword matches
        scores = {
            QueryType.FACTUAL: self._score_keywords(
                query_lower, self.factual_keywords
            ),
            QueryType.PROCEDURAL: self._score_keywords(
                query_lower, self.procedural_keywords
            ),
            QueryType.EXPLANATORY: self._score_keywords(
                query_lower, self.explanatory_keywords
            ),
            QueryType.COMPARATIVE: self._score_keywords(
                query_lower, self.comparative_keywords
            ),
        }

        # Find best match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        if best_score == 0:
            return QueryClassification(
                query_type=QueryType.UNKNOWN,
                confidence=0.0,
                reasoning="No keyword matches found"
            )

        return QueryClassification(
            query_type=best_type,
            confidence=min(best_score / 100, 1.0),
            reasoning=f"Matched {best_type.value} keywords"
        )

    def _score_keywords(self, text: str, keywords: List[str]) -> float:
        """Score text based on keyword matches."""
        score = 0.0
        for keyword in keywords:
            if keyword in text:
                score += 100
        return score


class MultiAgentRAG:
    """Multi-agent RAG system with different handlers."""

    def __init__(self, base_client: RAGClient):
        self.client = base_client
        self.router = QueryRouter()

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query with routing and agent selection."""
        # Step 1: Classify query
        classification = self.router.classify(query)
        print(f"Query type: {classification.query_type.value}")
        print(f"Confidence: {classification.confidence:.2f}")

        # Step 2: Route to agent
        if classification.query_type == QueryType.FACTUAL:
            response = self._handle_factual(query)
        elif classification.query_type == QueryType.PROCEDURAL:
            response = self._handle_procedural(query)
        elif classification.query_type == QueryType.EXPLANATORY:
            response = self._handle_explanatory(query)
        elif classification.query_type == QueryType.COMPARATIVE:
            response = self._handle_comparative(query)
        else:
            response = self._handle_unknown(query)

        return {
            "query": query,
            "classification": {
                "type": classification.query_type.value,
                "confidence": classification.confidence
            },
            "response": {
                "content": response.content,
                "agent": response.agent,
                "confidence": response.confidence
            }
        }

    def _handle_factual(self, query: str) -> AgentResponse:
        """Handle factual queries."""
        results = self.client.search(query, top_k=3)

        content = f"Based on knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            content += f"{i}. {result.chunk.text}\n"
            content += f"   (Relevance: {result.score:.2f})\n\n"

        confidence = results[0].score if results else 0.0

        return AgentResponse(
            content=content,
            confidence=confidence,
            agent="FactualAgent",
            metadata={"top_k": len(results), "query": query}
        )

    def _handle_procedural(self, query: str) -> AgentResponse:
        """Handle procedural queries (how-to)."""
        results = self.client.search(query, top_k=5)

        content = "Steps based on knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            content += f"Step {i}: {result.chunk.text}\n"

        confidence = results[0].score if results else 0.0

        return AgentResponse(
            content=content,
            confidence=confidence,
            agent="ProceduralAgent",
            metadata={"format": "steps", "query": query}
        )

    def _handle_explanatory(self, query: str) -> AgentResponse:
        """Handle explanatory queries (why)."""
        results = self.client.search(query, top_k=3)

        content = "Explanation:\n\n"
        for result in results:
            content += f"• {result.chunk.text}\n"

        confidence = results[0].score if results else 0.0

        return AgentResponse(
            content=content,
            confidence=confidence,
            agent="ExplanationAgent",
            metadata={"depth": "detailed", "query": query}
        )

    def _handle_comparative(self, query: str) -> AgentResponse:
        """Handle comparative queries."""
        results = self.client.search(query, top_k=4)

        content = "Comparison:\n\n"
        if len(results) >= 2:
            content += f"Option A: {results[0].chunk.text}\n\n"
            content += f"Option B: {results[1].chunk.text}\n\n"
            if len(results) > 2:
                content += f"Other perspectives:\n"
                for result in results[2:]:
                    content += f"• {result.chunk.text}\n"

        confidence = results[0].score if results else 0.0

        return AgentResponse(
            content=content,
            confidence=confidence,
            agent="ComparativeAgent",
            metadata={"comparison_count": len(results), "query": query}
        )

    def _handle_unknown(self, query: str) -> AgentResponse:
        """Handle unclassified queries."""
        results = self.client.search(query, top_k=5)

        content = "Information found:\n\n"
        for i, result in enumerate(results, 1):
            content += f"{i}. {result.chunk.text}\n\n"

        confidence = results[0].score if results else 0.0

        return AgentResponse(
            content=content,
            confidence=confidence,
            agent="GeneralAgent",
            metadata={"type": "unknown", "query": query}
        )


class ConversationContext:
    """Maintain conversation context for multi-turn interactions."""

    def __init__(self, client: RAGClient, max_history: int = 5):
        self.client = client
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history

    def add_turn(self, query: str, response: str) -> None:
        """Add a turn to conversation history."""
        self.history.append({
            "query": query,
            "response": response
        })

        # Keep only recent history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_context_string(self) -> str:
        """Get formatted conversation history."""
        if not self.history:
            return ""

        context = "Recent conversation:\n"
        for i, turn in enumerate(self.history, 1):
            context += f"\n{i}. Query: {turn['query']}\n"
            context += f"   Response: {turn['response'][:100]}...\n"

        return context

    def search_with_context(
        self, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search with conversation context."""
        # Augment query with context if available
        context_str = self.get_context_string()

        if context_str:
            augmented_query = f"{query}\n\nContext: {context_str}"
        else:
            augmented_query = query

        results = self.client.search(augmented_query, top_k=top_k)

        return [
            {
                "text": r.chunk.text,
                "score": r.score,
                "source": r.chunk.metadata.get("source", "unknown")
            }
            for r in results
        ]


def demo_multi_agent():
    """Demonstrate multi-agent RAG system."""
    print("=" * 60)
    print("Multi-Agent RAG Demo")
    print("=" * 60)

    # Setup
    client = RAGClient(RAGConfig(vector_store="chromadb"))
    multi_agent = MultiAgentRAG(client)

    # Add sample documents
    print("\nLoading knowledge base...")
    documents = [
        {
            "content": "Python is a high-level programming language known for simplicity.",
            "source": "python_intro.txt"
        },
        {
            "content": "To install Python: download from python.org, run installer, add to PATH.",
            "source": "python_install.txt"
        },
        {
            "content": "Python was created by Guido van Rossum to be readable and efficient.",
            "source": "python_history.txt"
        },
        {
            "content": "Java and Python differ in syntax, typing, and performance characteristics.",
            "source": "comparison.txt"
        }
    ]

    for doc in documents:
        client.add_document(doc["content"], doc["source"])

    # Process different query types
    queries = [
        "What is Python?",              # Factual
        "How do I install Python?",     # Procedural
        "Why is Python popular?",       # Explanatory
        "Compare Python and Java",      # Comparative
    ]

    print("\nProcessing queries with routing...\n")
    for query in queries:
        print(f"Query: {query}")
        result = multi_agent.process_query(query)
        print(f"\nResponse:\n{result['response']['content']}")
        print("-" * 60)


def demo_conversation():
    """Demonstrate conversation context."""
    print("\n" + "=" * 60)
    print("Conversation Context Demo")
    print("=" * 60)

    client = RAGClient(RAGConfig(vector_store="chromadb"))
    conversation = ConversationContext(client)

    # Add documents
    print("\nLoading knowledge base...")
    documents = [
        {
            "content": "Machine learning is a subset of AI",
            "source": "ml_basics.txt"
        },
        {
            "content": "Neural networks are inspired by biological neurons",
            "source": "neural_networks.txt"
        },
        {
            "content": "Deep learning uses multiple neural network layers",
            "source": "deep_learning.txt"
        }
    ]

    for doc in documents:
        client.add_document(doc["content"], doc["source"])

    # Multi-turn conversation
    queries = [
        "What is machine learning?",
        "Tell me more about neural networks",
        "How does deep learning differ?",
    ]

    print("\nMulti-turn conversation:")
    for query in queries:
        print(f"\nQuery: {query}")

        # Search with context
        results = conversation.search_with_context(query, top_k=2)

        # Format response
        response = " ".join([r["text"] for r in results])[:100]
        print(f"Response: {response}...\n")

        # Add to history
        conversation.add_turn(query, response)

    # Show conversation history
    print("\nConversation History:")
    print(conversation.get_context_string())


if __name__ == "__main__":
    demo_multi_agent()
    demo_conversation()
