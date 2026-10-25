# query -> search -> rerank -> context -> LLM -> response
import time
from typing import Dict, Any, List, Optional
from src.core.logging import app_logger
from src.core.interfaces import BaseLLMClient
from src.retrieval.hybrid_search import HybridRetriever
from src.retrieval.reranker import DocumentReranker
from src.retrieval.context_builder import ContextBuilder
from src.llm.gemini_client import GeminiClient
from src.guardrails.input_guard import InputGuard, PromptInjectionError
from src.guardrails.pii_masker import PIIMasker
from src.guardrails.domain_gurad import DomainGuard

class RAGPipeline:
     def __init__(self, llm: Optional[BaseLLMClient] = None):
          self.input_guard = InputGuard()
          self.pii_masker = PIIMasker()
          self.domain_gurad = DomainGuard()
          self.retriever = HybridRetriever()
          self.reranker = DocumentReranker()
          self.context_builder = ContextBuilder()
          self.llm = llm or GeminiClient()
          app_logger.info(f"[RAGPipeline] RAG Pipeline successfully initialized with {self.llm.__class__.__name__}")
     
     def run(self, query:str, top_k: int=3) -> Dict[str, Any]:
          t_start = time.time()
          timings = {"search_ms": 0.0, "rerank_ms": 0.0, "llm_ms": 0.0, "total_ms": 0.0}
          
          """Layer 1 INPUT GUARD (Avoid Prompt Injection & Jailbreak)"""
          is_safe, error_msg = self.input_guard.validate(query)
          if not is_safe:
               raise PromptInjectionError(error_msg or "Detect Prompt Injection.")

          """Layer 2 PII MASKING """
          masked_query, pii_map = self.pii_masker.mask(query)
          if pii_map:
               app_logger.info(f"[PIIMasker] Anonymized {len(pii_map)} PII entities before processing.")

          # 1 Hybrid Search
          t_search = time.time()
          initial_chunks = self.retriever.search(query, top_k=10)
          timings["search_ms"] = round((time.time() - t_search)*1000, 2)

          # 2 Cross Encoder reranking
          t_rerank = time.time()
          top_chunks = self.reranker.rerank(query, initial_chunks, top_k=top_k)
          timings["rerank_ms"] = round((time.time() - t_rerank) * 1000, 2)
          
          """Layer 3 DOMAIN GUARd"""
          if not self.domain_gurad.is_in_domain(top_chunks):
               timings["total_ms"] = round((time.time() - t_start) * 1000, 2)
               return {
                    "question": query,
                    "answer": "The current internal documentation does not contain information relevant to this question.",
                    "sources": [],
                    "retrieved_chunks": [],
                    "tokens": {"input": 0, "output": 0},
                    "timings_ms": timings,
               }

          """Layer 4 Generation and pii masking"""

          # 3 Pack Context
          context_str, sources = self.context_builder.build(top_chunks)

          # 4 LLM Generation
          t_llm = time.time()
          llm_response = self.llm.generate_answer(query, context_str)
          timings["llm_ms"] = round((time.time() - t_llm) * 1000, 2)

          total_latency_ms = round((time.time() - t_start) * 1000, 2)
          final_answer = self.pii_masker.unmask(llm_response["answer"], pii_map)
          
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
               "tokens": {
                    "input": llm_response["input_tokens"],
                    "output": llm_response["output_tokens"]
               },
               "timings_ms": {
                    **timings,
                    "total_ms": total_latency_ms
               }
          }