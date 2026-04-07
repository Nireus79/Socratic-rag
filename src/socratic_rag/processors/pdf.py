"""PDF file processor."""

import logging
from pathlib import Path
from typing import List

from ..exceptions import ProcessorError
from ..models import Document
from .base import BaseDocumentProcessor

logger = logging.getLogger(__name__)


class PDFProcessor(BaseDocumentProcessor):
    """PDF file processor.

    Processes PDF files and extracts documents.
    """

    def process(self, file_path: str) -> List[Document]:
        """Process a PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            List of Document objects, one per page or extracted text chunk.

        Raises:
            ProcessorError: If processing fails.
        """
        try:
            import PyPDF2

            path = Path(file_path)

            if not path.exists():
                raise ProcessorError(f"File not found: {file_path}")

            if not path.is_file():
                raise ProcessorError(f"Not a file: {file_path}")

            documents: List[Document] = []

            # Read PDF
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                if len(reader.pages) == 0:
                    raise ProcessorError(f"PDF has no pages: {file_path}")

                # Extract text from each page
                full_text = ""
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text:
                            full_text += f"\n--- Page {page_num} ---\n{text}"
                    except Exception as e:
                        logger.warning(
                            f"Failed to extract text from page {page_num}: {e}", exc_info=True
                        )
                        # Continue with next page if one page fails

            if not full_text.strip():
                raise ProcessorError(f"Could not extract text from PDF: {file_path}")

            # Create document
            doc = Document.create(
                content=full_text,
                source=str(path),
                metadata={
                    "filename": path.name,
                    "file_type": "pdf",
                    "pages": len(reader.pages),
                },
            )

            documents.append(doc)
            return documents

        except ProcessorError:
            raise
        except ImportError as e:
            logger.error(f"PyPDF2 not installed: {e}")
            raise ProcessorError(
                "PyPDF2 is required for PDF processing. " "Install with: pip install PyPDF2"
            )
        except Exception as e:
            logger.error(f"Failed to process PDF file: {e}", exc_info=True)
            raise ProcessorError(f"Failed to process PDF file: {e}")
