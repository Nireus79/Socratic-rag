"""Tests for document processors."""

import tempfile
from pathlib import Path

import pytest

from socratic_rag.exceptions import ProcessorError
from socratic_rag.processors import MarkdownProcessor, TextProcessor


class TestTextProcessor:
    """Test TextProcessor."""

    @pytest.fixture
    def processor(self):
        """Provide a text processor."""
        return TextProcessor()

    def test_process_text_file(self, processor):
        """Test processing a text file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("This is test content.")
            f.flush()
            temp_path = f.name

        try:
            documents = processor.process(temp_path)
            assert len(documents) == 1
            assert documents[0].content == "This is test content."
            assert documents[0].source == temp_path
        finally:
            Path(temp_path).unlink()

    def test_process_nonexistent_file(self, processor):
        """Test processing nonexistent file."""
        with pytest.raises(ProcessorError):
            processor.process("nonexistent_file.txt")

    def test_process_empty_file(self, processor):
        """Test processing empty file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.flush()
            temp_path = f.name

        try:
            with pytest.raises(ProcessorError):
                processor.process(temp_path)
        finally:
            Path(temp_path).unlink()


class TestMarkdownProcessor:
    """Test MarkdownProcessor."""

    @pytest.fixture
    def processor(self):
        """Provide a markdown processor."""
        return MarkdownProcessor()

    def test_process_markdown_file(self, processor):
        """Test processing a markdown file."""
        content = "# Hello\n\nThis is markdown content."

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            documents = processor.process(temp_path)
            assert len(documents) == 1
            assert documents[0].content == content
        finally:
            Path(temp_path).unlink()

    def test_process_nonexistent_file(self, processor):
        """Test processing nonexistent markdown file."""
        with pytest.raises(ProcessorError):
            processor.process("nonexistent_file.md")
