# Contributing Tutorial

A step-by-step guide for first-time contributors to Socratic RAG.

## Welcome!

Thank you for considering contributing to Socratic RAG! This guide will walk you through everything you need to know to make your first contribution.

---

## Prerequisites

Before you start, make sure you have:

- **Git**: https://git-scm.com/downloads
- **Python 3.8+**: https://www.python.org/downloads/
- **GitHub account**: https://github.com/signup
- **Text editor**: VSCode, PyCharm, or your favorite
- **Basic Git knowledge**: (Don't worry, we'll explain the steps!)

---

## Step 1: Fork the Repository

Forking creates your own copy of the project that you can freely experiment with.

1. Go to https://github.com/Nireus79/Socratic-rag
2. Click the **"Fork"** button in the top-right
3. This creates your copy at `https://github.com/YOUR_USERNAME/Socratic-rag`

---

## Step 2: Clone Your Fork

Get the code on your computer:

```bash
# Clone your fork (replace YOUR_USERNAME)
git clone https://github.com/YOUR_USERNAME/Socratic-rag.git
cd Socratic-rag

# Add upstream remote to stay synced with original
git remote add upstream https://github.com/Nireus79/Socratic-rag.git

# Verify remotes
git remote -v
# Output should show:
# origin    https://github.com/YOUR_USERNAME/Socratic-rag.git (your fork)
# upstream  https://github.com/Nireus79/Socratic-rag.git (original)
```

---

## Step 3: Set Up Development Environment

Create a clean Python environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate      # Linux/macOS
# or
venv\Scripts\activate          # Windows

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

**What this does**:
- `venv`: Isolated Python environment for this project
- `pip install -e ".[dev]"`: Installs package + all dev tools (pytest, black, ruff, etc.)
- `pre-commit install`: Auto-runs code quality checks before each commit

---

## Step 4: Create a Feature Branch

Never work directly on `main`. Create a branch for your changes:

```bash
# Sync with latest upstream code
git fetch upstream
git rebase upstream/main

# Create a feature branch (use descriptive name)
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/issue-description

# Verify you're on the new branch
git branch
```

**Branch naming conventions**:
- `feature/` - New features (e.g., `feature/hybrid-search`)
- `fix/` - Bug fixes (e.g., `fix/memory-leak-in-cache`)
- `docs/` - Documentation (e.g., `docs/add-quickstart`)
- `test/` - Tests (e.g., `test/edge-cases`)
- `refactor/` - Refactoring (e.g., `refactor/vector-store-api`)

---

## Step 5: Make Your Changes

Edit files and test your changes:

### Example: Add a New Feature

Let's say you want to add a new embedder provider.

```python
# Create file: src/socratic_rag/embeddings/custom.py
from socratic_rag.embeddings import BaseEmbedder

class CustomEmbedder(BaseEmbedder):
    """Your custom embedder implementation."""

    def embed_text(self, text: str) -> List[float]:
        # Your implementation
        pass

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Your implementation
        pass

    @property
    def dimension(self) -> int:
        return 384  # Your dimension
```

### Example: Fix a Bug

```python
# Edit existing file
# Make minimal changes focused on the fix
# Add comment explaining the fix if non-obvious
```

---

## Step 6: Test Your Changes

Always test before submitting:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_embeddings.py -v

# Run specific test
pytest tests/test_embeddings.py::test_embed_text -v

# Run with coverage
pytest tests/ --cov=socratic_rag --cov-report=html

# Check coverage report
open htmlcov/index.html  # or view in browser
```

**Target**: 70%+ code coverage (ideally 80%+)

---

## Step 7: Add Tests for Your Changes

Add tests in the appropriate test file:

```python
# In tests/test_embeddings.py (for embeddings)
# or tests/test_vector_stores.py (for vector stores)
# etc.

def test_your_feature():
    """Test description."""
    # Arrange: Set up test data
    data = "Test input"

    # Act: Call your function
    result = your_function(data)

    # Assert: Check the result
    assert result is not None
    assert len(result) == 384  # Your embedder dimension
```

---

## Step 8: Code Quality Checks

Ensure your code meets quality standards:

```bash
# Run code formatter (fixes issues automatically)
black src/socratic_rag/

# Run linter
ruff check src/socratic_rag/ --fix

# Run type checker
mypy src/socratic_rag/

# Run all pre-commit hooks
pre-commit run --all-files
```

**If pre-commit is installed**, these run automatically on commit!

---

## Step 9: Commit Your Changes

Write clear commit messages:

```bash
# See what changed
git status

# Stage changes
git add src/socratic_rag/embeddings/custom.py
git add tests/test_embeddings.py

# Commit with clear message
git commit -m "Add custom embedder provider with tests

- Implement CustomEmbedder class
- Add 5 unit tests for custom embedder
- Update embeddings module exports
- Tested with 100% coverage"

# Verify commit
git log -1
```

**Commit message guidelines**:
- First line: Short description (imperative: "Add", "Fix", "Update")
- Blank line
- Body: Detailed explanation of changes
- Reference issues if applicable: "Fixes #123"

---

## Step 10: Push to Your Fork

Send your changes to your GitHub fork:

```bash
# Push your branch
git push origin feature/your-feature-name

# You should see output like:
# remote: Create a pull request for 'feature/your-feature-name' on GitHub by visiting:
# remote: https://github.com/YOUR_USERNAME/Socratic-rag/pull/new/feature/your-feature-name
```

---

## Step 11: Create a Pull Request

Submit your changes for review:

1. Go to https://github.com/Nireus79/Socratic-rag
2. Click **"Pull Requests"** tab
3. Click **"New Pull Request"**
4. Select your fork and branch
5. Fill in the PR template with:
   - **Description**: What you changed and why
   - **Type**: Bug fix, Feature, Documentation, etc.
   - **Testing**: How you tested it
   - **Checklist**: Mark completed items

**PR Template Sections**:
```markdown
## Description
Brief explanation of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update

## Testing
How did you test this?
```

---

## Step 12: Respond to Reviews

Maintainers may request changes:

```bash
# Make requested changes
# Edit files as needed

# Stage and commit
git add .
git commit -m "Address review feedback: [specific changes]"

# Push updates (automatically updates PR)
git push origin feature/your-feature-name
```

**Tips**:
- Be respectful of feedback
- Ask for clarification if unclear
- Update tests if behavior changes
- Re-run tests after changes

---

## Step 13: Celebrate Your Contribution!

Once approved, your PR will be merged! 🎉

You'll be:
- Added to contributors list
- Mentioned in release notes
- Acknowledged in the community

---

## Common Contribution Types

### Adding a New Vector Store

```
1. Create src/socratic_rag/vector_stores/your_store.py
2. Implement BaseVectorStore interface
3. Add tests in tests/test_vector_stores.py
4. Update __init__.py exports
5. Add example in examples/
6. Update docs/vector-stores.md
7. Test with RAGClient: config = RAGConfig(vector_store="your_store")
```

### Adding a New Document Processor

```
1. Create src/socratic_rag/processors/your_processor.py
2. Implement BaseDocumentProcessor interface
3. Add tests in tests/test_processors.py
4. Update __init__.py exports
5. Add example usage
```

### Improving Documentation

```
1. Edit .md files in root or docs/
2. Use clear markdown formatting
3. Include code examples where applicable
4. Test links are valid
5. Run markdown linter: pre-commit run --all-files
```

### Adding Tests

```
1. Add tests to appropriate test file
2. Use descriptive test names: test_<function>_<scenario>
3. Include docstrings
4. Achieve 70%+ coverage
5. Run: pytest tests/ -v --cov
```

---

## Troubleshooting

### I cloned the wrong fork!
```bash
# Add upstream as origin
git remote rename origin old-origin
git remote add origin https://github.com/YOUR_USERNAME/Socratic-rag.git
# Or just start over - it's faster!
```

### Pre-commit hook is blocking my commit
```bash
# See what failed
pre-commit run --all-files

# Fix automatically (most issues)
black src/socratic_rag/
ruff check src/socratic_rag/ --fix

# Try commit again
git commit -m "Your message"

# If you need to bypass (not recommended)
git commit --no-verify
```

### Tests are failing
```bash
# Run just your changes
pytest tests/test_your_file.py -v

# Get more details
pytest tests/test_your_file.py -vv

# Run with print statements
pytest tests/test_your_file.py -s

# Debug a specific test
pytest tests/test_your_file.py::test_specific -vv -s
```

### My branch is outdated
```bash
# Fetch latest
git fetch upstream

# Rebase on main
git rebase upstream/main

# Force push to your fork (only for your branch!)
git push --force-with-lease origin feature/your-feature-name
```

---

## Getting Help

- **GitHub Issues**: Post questions in the discussion section
- **Documentation**: See [README.md](../README.md) and [docs/](../docs/)
- **Community**: Join [GitHub Discussions](https://github.com/Nireus79/Socratic-rag/discussions)

---

## Code of Conduct

Please follow our [Code of Conduct](../CODE_OF_CONDUCT.md). We're committed to making this a welcoming community for everyone.

---

## What Happens After You Contribute?

Your contribution helps make Socratic RAG better for everyone!

- Your code is reviewed for quality and correctness
- Your tests ensure reliability
- Your documentation helps other users
- You're recognized as a contributor

**Thank you for contributing!** 🙏

---

## Quick Reference

```bash
# Complete workflow in one go
git clone https://github.com/YOUR_USERNAME/Socratic-rag.git
cd Socratic-rag
git remote add upstream https://github.com/Nireus79/Socratic-rag.git

python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install

git fetch upstream
git checkout -b feature/my-feature

# Make changes...
pytest tests/ -v --cov
pre-commit run --all-files

git add .
git commit -m "Add my feature"
git push origin feature/my-feature

# Then create PR on GitHub!
```

---

**Last Updated**: March 10, 2024
**Version**: 0.1.0

Happy contributing! 🚀
