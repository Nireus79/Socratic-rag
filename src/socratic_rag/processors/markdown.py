"""Markdown file processor."""

from pathlib import Path
from typing import List

from ..exceptions import ProcessorError
from ..models import Document
from .base import BaseDocumentProcessor


class MarkdownProcessor(BaseDocumentProcessor):
    """Markdown file processor.

    Processes Markdown files and extracts documents.
    """

    def process(self, file_path: str) -> List[Document]:
        """Process a Markdown file.

        Args:
            file_path: Path to the Markdown file.

        Returns:
            List containing a single Document object.

        Raises:
            ProcessorError: If processing fails.
        """
        try:
            path = Path(file_path)

            if not path.exists():
                raise ProcessorError(f"File not found: {file_path}")

            if not path.is_file():
                raise ProcessorError(f"Not a file: {file_path}")

            # Read file content
            with open(path, encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                raise ProcessorError(f"File is empty: {file_path}")

            # Create document
            doc = Document.create(
                content=content,
                source=str(path),
                metadata={
                    "filename": path.name,
                    "file_type": "markdown",
                    "encoding": "utf-8",
                },
            )

            return [doc]

        except ProcessorError:
            raise
        except Exception as e:
            raise ProcessorError(f"Failed to process markdown file: {e}")
