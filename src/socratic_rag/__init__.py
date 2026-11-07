"""
Socratic RAG - Vector Database and RAG Implementation

Extracted from Socrates v1.3.3
"""

from __future__ import annotations

from .models import KnowledgeEntry
from .vector_db import VectorDatabase

__version__ = "0.1.6"
__all__ = ["KnowledgeEntry", "VectorDatabase"]
