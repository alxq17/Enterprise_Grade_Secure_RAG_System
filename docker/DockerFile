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

# install PyTorch for version CPU-only 
RUN pip install --no-cache-dir --prefix=/install \
        torch --index-url https://download.pytorch.org/whl/cpu

# install dependencies 
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Run time image
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
    && useradd -m -u 1001 -s /bin/bash appuser

COPY --from=builder /install /usr/local
RUN mkdir -p /app/.cache/huggingface && chown -R appuser:appuser /app/.cache
COPY --chown=appuser:appuser src/ /app/src/
USER appuser
EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=10s --retries=5 --start-period=90s \
    CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]