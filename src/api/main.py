from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware import TraceAndLoggingMiddleware
from src.api.routes import health, metrics, query
from src.core.logging import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("[Startup] Starting VeriRAG API Server...")
    try:
        query.get_pipeline()
    except Exception as e:
        app_logger.warning(f"[Startup] Pipeline warm-up deferred: {e}")
    yield
    app_logger.info("[Shutdown] Shutting down VeriRAG API Server...")


app = FastAPI(
    title="VeriRAG Enterprise API",
    description="Enterprise-grade, secure RAG system with source verification and metrics",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(TraceAndLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(query.router)
app.include_router(metrics.router)
