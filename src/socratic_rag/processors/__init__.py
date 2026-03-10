"""Document processors for Socratic RAG."""

from .base import BaseDocumentProcessor
from .text import TextProcessor
from .pdf import PDFProcessor
from .markdown import MarkdownProcessor

__all__ = [
    "BaseDocumentProcessor",
    "TextProcessor",
    "PDFProcessor",
    "MarkdownProcessor",
]
