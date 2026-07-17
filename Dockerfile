# Stage 1: Builder
FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application config and install to a distinct directory for easy copy
COPY pyproject.toml .
# We just need dependencies installed. If there's no package, we can just pip install the standard ones.
# Assuming pyproject.toml defines dependencies.
RUN pip install --user --no-cache-dir .

# Stage 2: Production Runner
FROM python:3.10-slim

# Create a non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Install runtime dependencies (e.g., for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Ensure the local bin is on PATH
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app

# Copy application code
COPY backend/ ./backend/
COPY core/ ./core/
COPY pyproject.toml .

# Change ownership to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Add a native Docker healthcheck querying our health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port for FastAPI
EXPOSE 8000

# Entrypoint uses uvicorn directly
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"]
