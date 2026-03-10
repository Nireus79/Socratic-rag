# Multi-stage build for Socratic RAG

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /tmp/build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . .

# Build distribution packages
RUN pip install --upgrade pip setuptools wheel && \
    python -m pip wheel --no-cache-dir --no-deps --wheel-dir /tmp/build/wheels .

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy wheels from builder
COPY --from=builder /tmp/build/wheels /tmp/wheels

# Install Python packages from wheels
RUN pip install --no-cache /tmp/wheels/* && \
    rm -rf /tmp/wheels

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port for API (if using REST API)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health 2>/dev/null || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "uvicorn", "examples.06_rest_api:app", "--host", "0.0.0.0", "--port", "8000"]
