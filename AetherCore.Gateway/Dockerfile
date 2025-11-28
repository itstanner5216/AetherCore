# AetherCore Gateway - Production Dockerfile (Koyeb Compatible)
# Multi-stage build for optimized container size
# NOTE: Build this from the repository root with: docker build -f Aethercore.Gateway/Dockerfile .

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY Aethercore.Gateway/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Production stage
# ============================================================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy Gateway application code
COPY --chown=appuser:appuser Aethercore.Gateway/ ./Aethercore.Gateway/

# Copy skills directory and config
COPY --chown=appuser:appuser skills/ ./skills/
COPY --chown=appuser:appuser skills_config.json ./

# Switch to non-root user
USER appuser

# Add local Python packages to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Set working directory to Gateway
WORKDIR /app/Aethercore.Gateway

# Expose port (Koyeb will map this)
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Production command using uvicorn
CMD ["uvicorn", "gateway:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
