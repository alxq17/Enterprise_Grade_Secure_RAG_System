import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import Counter, Histogram
from src.core.logging import app_logger

HTTP_REQUESTS_TOTAL = Counter(
    "rag_http_requests_total",
    "Total number of HTTP requests received",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "rag_http_request_duration_seconds",
    "Distribution of HTTP request processing durations in seconds",
    ["method", "endpoint"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

GUARDRAIL_BLOCKED_TOTAL = Counter(
    "rag_guardrail_blocked_total",
    "Total number of queries blocked by guardrails",
    ["guardrail_type"],
)

GEMINI_TOKENS_TOTAL = Counter(
    "rag_gemini_tokens_total",
    "Total Gemini tokens consumed by type",
    ["token_type"],
)


class TraceAndLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()
        endpoint = request.url.path

        try:
            response = await call_next(request)
            process_time_s = time.time() - start_time
            process_time_ms = round(process_time_s * 1000, 2)

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = str(process_time_ms)

            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code,
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                endpoint=endpoint,
            ).observe(process_time_s)

            # Record Prompt Injection blocks
            if response.status_code == 400 and endpoint == "/api/v1/query":
                GUARDRAIL_BLOCKED_TOTAL.labels(guardrail_type="prompt_injection").inc()

            return response

        except Exception as e:
            process_time_s = time.time() - start_time
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=500,
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                endpoint=endpoint,
            ).observe(process_time_s)
            app_logger.error(f"[{request_id}] Processing error in Middleware: {e}")
            raise e