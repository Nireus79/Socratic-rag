"""Abstract base classes for document processors."""

from abc import ABC, abstractmethod
from typing import List

from ..models import Document


class BaseDocumentProcessor(ABC):
    """Abstract base for document processors."""

    @abstractmethod
    def process(self, file_path: str) -> List[Document]:
        """Process a document file.

        Args:
            file_path: Path to the document file.

        Returns:
            List of Document objects extracted from the file.

        Raises:
            ProcessorError: If processing fails.
        """
        pass
