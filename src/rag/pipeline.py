import time
from typing import Any

from src.core.interfaces import BaseLLMClient
from src.core.logging import app_logger
from src.guardrails import (
    DomainGuard,
    InputGuard,
    OutputGuard,
    PIIMasker,
    PromptInjectionError,
)
from src.llm.gemini_client import GeminiClient
from src.retrieval.context_builder import ContextBuilder
from src.retrieval.hybrid_search import HybridRetriever
from src.retrieval.reranker import DocumentReranker


class RAGPipeline:
    def __init__(self, llm: BaseLLMClient | None = None):
        self.input_guard = InputGuard()
        self.pii_masker = PIIMasker()
        self.domain_guard = DomainGuard()
        self.output_guard = OutputGuard()
        self.retriever = HybridRetriever()
        self.reranker = DocumentReranker()
        self.context_builder = ContextBuilder()
        self.llm = llm or GeminiClient()
        app_logger.info(
            f"[RAGPipeline] RAG Pipeline initialized with {self.llm.__class__.__name__}"
        )

    def run(self, query: str, top_k: int = 3) -> dict[str, Any]:
        t_start = time.time()
        timings = {"search_ms": 0.0, "rerank_ms": 0.0, "llm_ms": 0.0, "total_ms": 0.0}

        # Layer 1: INPUT GUARD (Prompt Injection & Jailbreak Defense)
        is_safe, error_msg = self.input_guard.validate(query)
        if not is_safe:
            raise PromptInjectionError(error_msg or "Prompt injection detected.")

        # Layer 2: PII MASKING
        masked_query, pii_map = self.pii_masker.mask(query)
        if pii_map:
            app_logger.info(
                f"[PIIMasker] Anonymized {len(pii_map)} PII entities before external processing."
            )

        # Layer 3: HYBRID RETRIEVAL AND RERANKING
        t_search = time.time()
        initial_chunks = self.retriever.search(masked_query, top_k=10)
        timings["search_ms"] = round((time.time() - t_search) * 1000, 2)

        t_rerank = time.time()
        top_chunks = self.reranker.rerank(masked_query, initial_chunks, top_k=top_k)
        timings["rerank_ms"] = round((time.time() - t_rerank) * 1000, 2)

        # Layer 4: DOMAIN GUARD
        if not self.domain_guard.is_in_domain(top_chunks):
            timings["total_ms"] = round((time.time() - t_start) * 1000, 2)
            return {
                "question": query,
                "answer": "The current internal documentation does not contain information relevant to this question.",
                "sources": [],
                "retrieved_chunks": [],
                "contexts": [],
                "tokens": {"input": 0, "output": 0},
                "timings_ms": timings,
            }

        # Layer 5: CONTEXT PACKING AND LLM GENERATION
        context_str, sources = self.context_builder.build(top_chunks)

        t_llm = time.time()
        # MUST send masked_query to Gemini to prevent PII leakage to external LLM
        llm_response = self.llm.generate_answer(masked_query, context_str)
        timings["llm_ms"] = round((time.time() - t_llm) * 1000, 2)

        # Layer 6: OUTPUT GUARD AND PII UNMASKING
        raw_answer = llm_response["answer"]
        self.output_guard.validate(raw_answer, context_str)
        final_answer = self.pii_masker.unmask(raw_answer, pii_map)

        total_latency_ms = round((time.time() - t_start) * 1000, 2)
        timings["total_ms"] = total_latency_ms

        retrieved_meta = [
            {
                "chunk_id": c["chunk_id"],
                "rerank_score": c.get("rerank_score", 0.0),
                "source_file": c["metadata"].get("source_file"),
                "page_number": c["metadata"].get("page_number"),
            }
            for c in top_chunks
        ]

        return {
            "question": query,
            "answer": final_answer,
            "sources": sources,
            "retrieved_chunks": retrieved_meta,
            "contexts": [c.get("text", "") for c in top_chunks],
            "tokens": {
                "input": llm_response["input_tokens"],
                "output": llm_response["output_tokens"],
            },
            "timings_ms": timings,
        }
