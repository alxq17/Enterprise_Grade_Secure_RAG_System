from fastapi import APIRouter, Request, HTTPException
from src.api.schemas import QueryRequest, QueryResponse
from src.rag.pipeline import RAGPipeline
from src.core.logging import app_logger
from src.guardrails.input_guard import PromptInjectionError

router = APIRouter(prefix="/api/v1", tags=["RAG Query"])
rag_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    global rag_pipeline
    if rag_pipeline is None:
        rag_pipeline = RAGPipeline()
    return rag_pipeline


@router.post("/query", response_model=QueryResponse)
def handle_query(payload: QueryRequest, request: Request):
    try:
        pipeline = get_pipeline()
        result = pipeline.run(query=payload.question, top_k=payload.top_k)
        result["request_id"] = getattr(request.state, "request_id", None)
        return result
    except PromptInjectionError as e:
        app_logger.warning(f"[API] Query rejected due to InputGuard violation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        app_logger.error(f"Error during processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))