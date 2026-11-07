"""Data model shared by the vector database."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class KnowledgeEntry:
    """One piece of knowledge stored in the vector database."""

    id: str
    content: str
    category: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] | None = None
