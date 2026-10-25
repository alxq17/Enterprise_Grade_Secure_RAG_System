from fastapi import APIRouter
from starlette.responses import JSONResponse
from qdrant_client import QdrantClient
from src.config.settings import settings

router = APIRouter(tags=["Health"])


@router.get("/healthz")
def health_check():
    return {"status": "ok"}


@router.get("/readyz")
def readiness_check():
    """Check connectivity to dependent services (Qdrant and Gemini)."""
    try:
        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=3)
        client.get_collections()
        gemini_configured = bool(settings.GEMINI_API_KEY)
        return {
            "status": "ready" if gemini_configured else "degraded",
            "database": "qdrant_connected",
            "llm": "gemini_configured" if gemini_configured else "gemini_api_key_missing",
        }
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})