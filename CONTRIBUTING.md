# Contributing to Socratic RAG

Thank you for your interest in contributing to Socratic RAG! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/Socratic-rag.git
cd Socratic-rag
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

### 3. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Code Style

We follow PEP 8 style guidelines with some customizations:

- **Formatter**: Black (line length: 100 characters)
- **Linter**: Ruff
- **Type Hints**: MyPy (strict mode)

Run formatting:

```bash
black src/ tests/
ruff check --fix src/ tests/
```

Run type checking:

```bash
mypy src/socratic_rag
```

### Testing

Write tests for all new features:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=socratic_rag --cov-report=html

# Run specific test file
pytest tests/test_client.py -v

# Run with markers
pytest tests/ -m unit  # Only unit tests
pytest tests/ -m "not slow"  # Exclude slow tests
```

Aim for:
- **Unit tests** for individual functions/classes
- **Integration tests** for component interactions
- **70%+ code coverage** minimum

### Test Structure

```python
import pytest
from socratic_rag import RAGClient

class TestFeature:
    """Tests for feature."""

    @pytest.fixture
    def client(self):
        """Provide test client."""
        return RAGClient()

    def test_feature(self, client):
        """Test specific feature."""
        result = client.method()
        assert result is not None
```

## Commit Guidelines

Write clear, descriptive commit messages:

```
[Type] Short description (50 chars max)

Detailed explanation if needed (72 char wrap).
- Bullet points for multiple items
- Explain what and why, not how

Fixes #123
Co-Authored-By: Name <email@example.com>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Pull Request Process

1. **Update from main**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push changes**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create PR** with:
   - Clear title and description
   - Reference related issues
   - Screenshots for UI changes
   - Test results summary

4. **Address review feedback**:
   - Make requested changes
   - Respond to comments
   - Push additional commits

5. **Merge** once approved

## Adding New Features

### 1. Vector Store Provider

```python
# src/socratic_rag/vector_stores/new_store.py
from .base import BaseVectorStore

class NewVectorStore(BaseVectorStore):
    """New vector store implementation."""

    def add_documents(self, chunks, embeddings):
        # Implement
        pass

    # Implement other abstract methods
```

### 2. Embedder Provider

```python
# src/socratic_rag/embeddings/new_embedder.py
from .base import BaseEmbedder

class NewEmbedder(BaseEmbedder):
    """New embedder implementation."""

    def embed_text(self, text):
        # Implement
        pass

    # Implement other abstract methods
```

### 3. Chunking Strategy

```python
# src/socratic_rag/chunking/new_chunker.py
from .base import BaseChunker

class NewChunker(BaseChunker):
    """New chunking strategy."""

    def chunk(self, text, document_id, metadata=None):
        # Implement
        pass
```

### 4. Document Processor

```python
# src/socratic_rag/processors/new_processor.py
from .base import BaseDocumentProcessor

class NewProcessor(BaseDocumentProcessor):
    """New document processor."""

    def process(self, file_path):
        # Implement
        pass
```

## Documentation

### Update README.md

- Document new features
- Add usage examples
- Update API reference

### Create/Update Docs

- `docs/quickstart.md` - Getting started
- `docs/vector-stores.md` - Vector store guide
- `docs/embeddings.md` - Embeddings guide
- `docs/api-reference.md` - API docs

### Docstring Format

```python
def method(self, param: str) -> str:
    """Brief description.

    Longer description if needed.

    Args:
        param: Parameter description.

    Returns:
        Return value description.

    Raises:
        ExceptionType: When this exception is raised.
    """
    pass
```

## Release Process

1. **Version Bump**: Update `src/socratic_rag/__init__.py`
2. **Changelog**: Update `CHANGELOG.md`
3. **Tag**: Create git tag: `git tag v0.1.0`
4. **Push**: `git push origin main --tags`
5. **Release**: Create GitHub release

## Reporting Issues

### Bug Report

Include:
- Python version
- OS and version
- Minimal code to reproduce
- Error traceback
- Expected vs actual behavior

### Feature Request

Include:
- Clear description
- Use cases
- Proposed API/interface
- Related issues

## Getting Help

- **Issues**: Ask on GitHub Issues
- **Discussions**: Use GitHub Discussions
- **Email**: [TBD contact email]

## Acknowledgments

Thank you for contributing to Socratic RAG! Your work helps make RAG more accessible to everyone.

---

**Need help?** Check existing issues or start a discussion on GitHub.
