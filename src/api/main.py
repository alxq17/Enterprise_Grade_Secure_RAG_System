from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from src.api.middleware import TraceAndLoggingMiddleware
from src.api.routes import health, query


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[Startup] Starting VeriRAG API Server...")
    query.get_pipeline()  
    yield
    logger.info("[Shutdown] Shutting down VeriRAG API Server...")

app = FastAPI(
    title="VeriRAG Enterprise API",
    description="Enterprise-grade, secure RAG system with source verification and metrics",
    version="0.1.0",
    lifespan=lifespan
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