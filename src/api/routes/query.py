from fastapi import APIRouter, HTTPException, Request

from src.api.middleware import GEMINI_TOKENS_TOTAL, GUARDRAIL_BLOCKED_TOTAL
from src.api.schemas import QueryRequest, QueryResponse
from src.core.logging import app_logger
from src.guardrails.input_guard import PromptInjectionError
from src.rag.pipeline import RAGPipeline

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

        # Track Out-of-Domain Guardrail blocks
        if not result.get("sources") and "does not contain information" in result.get("answer", ""):
            GUARDRAIL_BLOCKED_TOTAL.labels(guardrail_type="out_of_domain").inc()

        # Track token consumption metrics
        tokens = result.get("tokens", {})
        inp = tokens.get("input", 0)
        out = tokens.get("output", 0)
        if inp > 0:
            GEMINI_TOKENS_TOTAL.labels(token_type="input").inc(inp)
        if out > 0:
            GEMINI_TOKENS_TOTAL.labels(token_type="output").inc(out)

        return result

    except PromptInjectionError as e:
        app_logger.warning(f"[API] Query rejected due to InputGuard violation: {e}")
        GUARDRAIL_BLOCKED_TOTAL.labels(guardrail_type="prompt_injection").inc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        app_logger.error(f"Error during processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
