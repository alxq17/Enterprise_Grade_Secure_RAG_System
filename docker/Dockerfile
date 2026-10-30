# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU-only first for smaller footprint
RUN pip install --no-cache-dir --prefix=/install \
        torch --index-url https://download.pytorch.org/whl/cpu

# Install production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Production Runtime Stage
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/local/bin:${PATH}" \
    PYTHONPATH="/app" \
    HF_HOME="/app/.cache/huggingface"

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1001 -s /bin/bash verirag

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Setup cache directory with non-root ownership
RUN mkdir -p /app/.cache/huggingface && chown -R verirag:verirag /app/.cache

# Copy application code
COPY --chown=verirag:verirag src/ /app/src/

# Setup entrypoint script (strip CRLF line endings and set execution permissions)
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh \
    && chown verirag:verirag /app/entrypoint.sh

# Switch to non-root user
USER verirag
EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=10s --retries=5 --start-period=90s \
    CMD curl -f http://localhost:8000/healthz || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]