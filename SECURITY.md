# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Socratic RAG, please report it responsibly and privately.

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

Instead, email your findings to: **info@socratic-rag.dev**

Include the following information in your report:

1. **Description**: Clear description of the vulnerability
2. **Location**: Specific file(s), class(es), or function(s) affected
3. **Reproduction Steps**: Step-by-step instructions to reproduce the issue
4. **Impact**: Potential impact or severity of the vulnerability
5. **Suggested Fix**: If you have a suggestion for a fix (optional but helpful)

## Response Timeline

We take security seriously and will:

- Acknowledge receipt of your report within **48 hours**
- Provide an estimated timeline for addressing the vulnerability
- Keep you informed of progress
- Credit you in the security patch (unless you prefer anonymity)

## Security Update Process

When a security vulnerability is confirmed:

1. We create a fix in a private branch
2. We test the fix thoroughly
3. We release a patch version (e.g., v0.1.1)
4. We publish a security advisory
5. We notify users of the update

## Supported Versions

Security updates will be provided for:

| Version | Status | Support Until |
|---------|--------|---------------|
| 0.1.x   | Active | v0.2.0 release |
| 0.0.x   | Deprecated | Not supported |

## Security Best Practices

When using Socratic RAG:

### API Keys and Credentials
- Never commit API keys or credentials to version control
- Use environment variables for sensitive data
- Rotate credentials regularly
- Use `.gitignore` to exclude credential files

```python
import os
from socrates_nexus import LLMClient

# Load credentials from environment
api_key = os.getenv('ANTHROPIC_API_KEY')
llm = LLMClient(api_key=api_key)
```

### Data Security
- Sanitize user input before adding to knowledge base
- Be careful with sensitive/PII data in documents
- Use appropriate access controls for vector stores
- Consider encryption for sensitive data at rest

### Dependencies
- Keep Python and dependencies up to date
- Review security advisories for dependencies
- Use `pip-audit` to check for known vulnerabilities

```bash
pip install pip-audit
pip-audit  # Check for vulnerabilities
```

### Vector Store Security
- Secure Qdrant instances with authentication
- Use encrypted connections (TLS/SSL)
- Restrict network access to vector stores
- Regular backups of data

### Deployment Security
- Use HTTPS for API endpoints
- Implement rate limiting
- Use authentication/authorization
- Monitor for suspicious activity
- Keep servers patched and updated

## Known Security Considerations

### Current Limitations (v0.1.0)

1. **No Built-in Encryption**
   - Data is stored unencrypted in vector stores
   - Use encryption at the application level if needed

2. **No Authentication in Library**
   - Library itself has no auth mechanism
   - Implement auth in your application

3. **No Input Sanitization**
   - Validate and sanitize user input before passing to RAG
   - Prevent injection attacks

4. **No Rate Limiting**
   - Implement rate limiting in your application

## Dependency Security

Socratic RAG depends on:

- **numpy** - Numerical computing (widely used, actively maintained)
- **sentence-transformers** - ML embeddings (from Hugging Face, well-maintained)
- **chromadb** (optional) - Vector store (actively maintained)
- **qdrant-client** (optional) - Vector store (actively maintained)
- **faiss-cpu** (optional) - Vector search (from Facebook Research, actively maintained)

All core dependencies are from reputable sources and actively maintained.

## Security Scanning

We use:

- **GitHub Security Scanning** - Dependency vulnerability alerts
- **Type Checking (MyPy)** - Catch potential type-related issues
- **Code Review** - Manual review of changes
- **Testing** - Comprehensive test suite

## Future Security Improvements (v0.2.0+)

- [ ] Input validation utilities
- [ ] Rate limiting examples
- [ ] Encryption at rest support
- [ ] Authentication framework
- [ ] Security audit logging

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [pip-audit](https://github.com/pypa/pip-audit)
- [Bandit](https://github.com/PyCQA/bandit) - Python security linter

## Questions?

For security questions (non-vulnerability):
- Email: info@socratic-rag.dev
- GitHub Discussions: https://github.com/Nireus79/Socratic-rag/discussions

---

**Last Updated**: March 10, 2024

Thank you for helping keep Socratic RAG secure!
