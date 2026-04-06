"""Hybrid search implementation for socratic-rag."""
import asyncio
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from a search operation."""
    document_id: str
    content: str
    score: float
    search_method: str
    metadata: Dict[str, Any]


class BM25Searcher:
    """BM25 implementation for lexical search."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.documents = {}
        self.doc_vectors = None
        self.fitted = False
    
    def add_documents(self, documents: Dict[str, str]) -> None:
        """Add documents for indexing."""
        self.documents = documents
        doc_texts = list(documents.values())
        self.doc_vectors = self.vectorizer.fit_transform(doc_texts)
        self.fitted = True
        logger.info(f"BM25: Indexed {len(documents)} documents")
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search using BM25."""
        if not self.fitted:
            return []
        
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.doc_vectors)[0]
        
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        doc_ids = list(self.documents.keys())
        for idx in top_indices:
            if scores[idx] > 0:
                results.append(SearchResult(
                    document_id=doc_ids[idx],
                    content=self.documents[doc_ids[idx]],
                    score=float(scores[idx]),
                    search_method="bm25",
                    metadata={}
                ))
        
        return results


class SemanticSearcher:
    """Semantic search using embeddings."""
    
    def __init__(self):
        self.embeddings: Dict[str, np.ndarray] = {}
        self.documents: Dict[str, str] = {}
    
    def add_documents(self, documents: Dict[str, str], embeddings: Dict[str, np.ndarray]) -> None:
        """Add documents with their embeddings."""
        self.documents = documents
        self.embeddings = embeddings
        logger.info(f"Semantic: Indexed {len(documents)} documents")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        """Search using semantic similarity."""
        if not self.documents:
            return []
        
        results = []
        doc_ids = list(self.documents.keys())
        
        for doc_id in doc_ids:
            if doc_id in self.embeddings:
                embedding = self.embeddings[doc_id]
                score = float(np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding) + 1e-8))
                results.append((doc_id, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [SearchResult(
            document_id=doc_id,
            content=self.documents[doc_id],
            score=score,
            search_method="semantic",
            metadata={}
        ) for doc_id, score in results[:top_k]]


class HybridSearchEngine:
    """Combines BM25 and semantic search."""
    
    def __init__(self, bm25_weight: float = 0.4, semantic_weight: float = 0.6):
        self.bm25 = BM25Searcher()
        self.semantic = SemanticSearcher()
        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight
    
    async def index_documents(self, documents: Dict[str, str], embeddings: Dict[str, np.ndarray]) -> None:
        """Index documents for hybrid search."""
        self.bm25.add_documents(documents)
        self.semantic.add_documents(documents, embeddings)
        logger.info(f"Hybrid search: Indexed {len(documents)} documents")
    
    async def search(self, query: str, query_embedding: np.ndarray, top_k: int = 10) -> List[SearchResult]:
        """Perform hybrid search combining BM25 and semantic."""
        bm25_results = self.bm25.search(query, top_k=top_k)
        semantic_results = self.semantic.search(query_embedding, top_k=top_k)
        
        merged = {}
        
        for result in bm25_results:
            merged[result.document_id] = {
                "content": result.content,
                "bm25_score": result.score * self.bm25_weight,
                "semantic_score": 0.0,
                "metadata": result.metadata
            }
        
        for result in semantic_results:
            if result.document_id not in merged:
                merged[result.document_id] = {
                    "content": result.content,
                    "bm25_score": 0.0,
                    "semantic_score": 0.0,
                    "metadata": result.metadata
                }
            merged[result.document_id]["semantic_score"] = result.score * self.semantic_weight
        
        final_results = []
        for doc_id, data in merged.items():
            combined_score = data["bm25_score"] + data["semantic_score"]
            final_results.append(SearchResult(
                document_id=doc_id,
                content=data["content"],
                score=combined_score,
                search_method="hybrid",
                metadata=data["metadata"]
            ))
        
        final_results.sort(key=lambda x: x.score, reverse=True)
        return final_results[:top_k]
    
    async def rerank_results(self, results: List[SearchResult], rerank_scores: Dict[str, float]) -> List[SearchResult]:
        """Rerank results using provided scores."""
        for result in results:
            if result.document_id in rerank_scores:
                result.score = rerank_scores[result.document_id]
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results
