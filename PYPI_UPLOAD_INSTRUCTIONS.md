# PyPI Upload Instructions for Socratic RAG v0.1.0

## Status

✅ **GitHub**: Code pushed to main branch with v0.1.0 tag
✅ **Build**: Package built successfully in `dist/` directory

## Distribution Files Built

```
dist/
├── socratic_rag-0.1.0.tar.gz          (21 KB - Source distribution)
└── socratic_rag-0.1.0-py3-none-any.whl (12 KB - Wheel distribution)
```

## PyPI Upload Steps

### Step 1: Get PyPI API Token

1. Go to https://pypi.org/
2. Create an account or log in
3. Go to Account Settings → API tokens
4. Create a new token with "Entire repository" scope
5. Copy the token (format: `pypi-AgEIcHlwaS5vcmc...`)

### Step 2: Upload to PyPI

**Option A: Using environment variable (recommended)**

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...
twine upload dist/*
```

**Option B: Using .pypirc file**

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...
```

Then run:
```bash
twine upload dist/*
```

**Option C: Interactive (will prompt for credentials)**

```bash
twine upload dist/*
```

### Step 3: Verify Upload

Once uploaded, verify at:
- https://pypi.org/project/socratic-rag/

## Installation After Upload

Users will be able to install with:

```bash
pip install socratic-rag
```

## Automatic CI/CD Upload

The `.github/workflows/publish.yml` workflow can be used to automatically upload to PyPI on release creation:

1. Set up PyPI API token as GitHub secret:
   - Go to Repository Settings → Secrets and variables → Actions
   - Add `PYPI_API_TOKEN` with your PyPI token

2. Create a GitHub release:
   - Go to Releases → Draft a new release
   - Select tag: `v0.1.0`
   - Title: `Socratic RAG v0.1.0 - Foundation Release`
   - Publish the release

The workflow will automatically build and upload to PyPI!

## Troubleshooting

### "Invalid distribution"

```bash
# Validate before uploading
twine check dist/*
```

### "Repository at ... 404 Not Found"

The index might be rate-limited. Try:
```bash
twine upload --skip-existing dist/*
```

### "File already exists"

Version already uploaded. Need to bump version:
- Edit `src/socratic_rag/__init__.py`: Change `__version__ = "0.1.1"`
- Rebuild: `python -m build`
- Upload new version

## After Upload

1. **Announce**: Share the PyPI link
   - https://pypi.org/project/socratic-rag/

2. **Update README**: Add badge
   ```markdown
   [![PyPI version](https://badge.fury.io/py/socratic-rag.svg)](https://badge.fury.io/py/socratic-rag)
   ```

3. **Create Release Notes**: On GitHub
   - https://github.com/Nireus79/Socratic-rag/releases/tag/v0.1.0

## Support

- GitHub Issues: https://github.com/Nireus79/Socratic-rag/issues
- PyPI Project: https://pypi.org/project/socratic-rag/
- Documentation: https://github.com/Nireus79/Socratic-rag#readme

---

**Ready to publish Socratic RAG to PyPI!** 🚀
