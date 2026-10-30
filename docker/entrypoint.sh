#!/bin/bash
set -e
echo "[Entrypoint] Starting VeriRAG FastAPI Service..."

QDRANT_HOST="${QDRANT_HOST:-qdrant}"
QDRANT_PORT="${QDRANT_PORT:-6333}"

echo "[Entrypoint] Waiting for Qdrant service at http://${QDRANT_HOST}:${QDRANT_PORT}/readyz..."
until python -c "import urllib.request, os; urllib.request.urlopen(f'http://${QDRANT_HOST}:${QDRANT_PORT}/readyz', timeout=2)" > /dev/null 2>&1; do
    echo "[Entrypoint] Qdrant not ready yet. Retrying in 2 seconds..."
    sleep 2
done

echo "[Entrypoint] Qdrant is healthy and ready. Launching FastAPI server..."
if [ "$#" -gt 0 ]; then
    exec "$@"
else
    exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 1
fi