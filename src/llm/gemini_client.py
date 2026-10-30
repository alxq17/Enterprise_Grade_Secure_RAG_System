import time
from typing import Any

from google import genai
from google.genai import types
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config.settings import settings
from src.core.exceptions import VeriRAGException
from src.core.interfaces import BaseLLMClient
from src.core.logging import app_logger


class LLMError(VeriRAGException):
    """Exception raised for errors during LLM generation."""

    pass


class GeminiClient(BaseLLMClient):
    """
    Google Gemini Client implementing BaseLLMClient with:
    - Robust exponential backoff retry (tenacity)
    - Request timeout configuration
    - Accurate token counting and cumulative usage tracking
    - Detailed structured logging
    - Easy provider swap via BaseLLMClient interface
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout_seconds: int | None = None,
        max_retries: int | None = None,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            app_logger.warning("[GeminiClient] GEMINI_API_KEY is not configured in environment!")

        self.model_name = model_name or settings.GEMINI_MODEL or "gemini-1.5-flash"
        self.timeout_seconds = timeout_seconds or getattr(settings, "LLM_TIMEOUT_SECONDS", 30)
        self.max_retries = max_retries or getattr(settings, "LLM_MAX_RETRIES", 3)

        # Cumulative token statistics
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.total_requests: int = 0

        # Initialize genai client with timeout in milliseconds
        http_options = types.HttpOptions(timeout=int(self.timeout_seconds * 1000))
        self.client = genai.Client(api_key=self.api_key, http_options=http_options)

        app_logger.info(
            f"[GeminiClient] Initialized with model='{self.model_name}', "
            f"timeout={self.timeout_seconds}s, max_retries={self.max_retries}"
        )

    def _execute_with_retry(self, prompt: str, system_instruction: str) -> Any:
        """Helper to invoke generate_content with tenacity exponential backoff retry."""
        retry_decorator = retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type(Exception),
            before_sleep=lambda retry_state: app_logger.warning(
                f"[GeminiClient] Retry attempt {retry_state.attempt_number}/{self.max_retries} "
                f"after error: {retry_state.outcome.exception()}"
            ),
            reraise=True,
        )

        @retry_decorator
        def _call():
            return self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                ),
            )

        return _call()

    def generate_answer(self, query: str, context: str) -> dict[str, Any]:
        """
        Generate answer based strictly on retrieved context.
        Returns dict: answer, input_tokens, output_tokens, latency_ms.
        """
        if not context.strip():
            app_logger.warning(
                f"[GeminiClient] Empty context received for query: '{query[:60]}...'"
            )
            return {
                "answer": "I cannot find relevant information in the internal documentation to answer this question.",
                "input_tokens": 0,
                "output_tokens": 0,
                "latency_ms": 0.0,
            }

        system_instruction = (
            "You are a professional AI assistant designed to query a company's internal documents (VeriRAG).\n"
            "MANDATORY PRINCIPLES:\n"
            "1. Base your answers solely on the information provided in the 'DOCUMENT CONTEXT' section.\n"
            "2. Do not speculate or add any information outside of the provided documents.\n"
            "3. If the context does not contain the information needed to answer, state exactly: "
            "'The provided documents do not contain information regarding this question.'\n"
            "4. At the end of each point, cite the source clearly using the format: [File_name - Page X]."
        )

        prompt = f"DOCUMENT CONTEXT:\n{context}\n\n---\nUSER QUESTION: {query}\nANSWER:"

        app_logger.info(
            f"[GeminiClient] Dispatching request (query='{query[:50]}...', "
            f"context_length={len(context)} chars)"
        )

        t0 = time.time()
        try:
            response = self._execute_with_retry(
                prompt=prompt, system_instruction=system_instruction
            )
            latency_ms = round((time.time() - t0) * 1000, 2)

            # Token tracking & extraction
            usage = getattr(response, "usage_metadata", None)
            if usage:
                input_tokens = getattr(usage, "prompt_token_count", 0) or 0
                output_tokens = getattr(usage, "candidates_token_count", 0) or 0
            else:
                # Fallback token counting if usage_metadata not available
                try:
                    count_resp = self.client.models.count_tokens(
                        model=self.model_name, contents=prompt
                    )
                    input_tokens = count_resp.total_tokens
                except Exception:
                    input_tokens = len(prompt.split())  # approximate heuristic
                output_tokens = len(getattr(response, "text", "").split())

            # Accumulate metrics
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_requests += 1

            raw_text = getattr(response, "text", "") or ""
            clean_answer = raw_text.strip()

            app_logger.info(
                f"[GeminiClient] Answer generated in {latency_ms}ms | "
                f"Tokens: {input_tokens} in, {output_tokens} out | "
                f"Cumulative: {self.total_input_tokens} in, {self.total_output_tokens} out"
            )

            return {
                "answer": clean_answer,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
            }

        except Exception as e:
            latency_ms = round((time.time() - t0) * 1000, 2)
            app_logger.error(f"[GeminiClient] Generation failed after {latency_ms}ms: {e}")
            raise LLMError(f"Error connecting to the Gemini model: {e}") from e

    def get_token_usage(self) -> dict[str, int]:
        """Return cumulative token usage statistics for telemetry and cost tracking."""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_requests": self.total_requests,
        }
