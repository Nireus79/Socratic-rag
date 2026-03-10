"""Embedding providers for Socratic RAG."""

from .base import BaseEmbedder
from .sentence_transformers import SentenceTransformersEmbedder

__all__ = [
    "BaseEmbedder",
    "SentenceTransformersEmbedder",
]
