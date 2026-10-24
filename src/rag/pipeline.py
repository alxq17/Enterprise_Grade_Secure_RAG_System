# query -> search -> rerank -> context -> LLM -> response
import time
from typing import Dict, Any, List, Optional
from src.core.logging import app_logger
from src.core.interfaces import BaseLLMClient
from src.retrieval.hybrid_search import HybridRetriever
from src.retrieval.reranker import DocumentReranker
from src.retrieval.context_builder import ContextBuilder
from src.llm.gemini_client import GeminiClient

class RAGPipeline:
     def __init__(self, llm: Optional[BaseLLMClient] = None):
          self.retriever = HybridRetriever()
          self.reranker = DocumentReranker()
          self.context_builder = ContextBuilder()
          self.llm = llm or GeminiClient()
          app_logger.info(f"[RAGPipeline] RAG Pipeline successfully initialized with {self.llm.__class__.__name__}")
     def run(self, query:str, top_k: int=3) -> Dict[str, Any]:
          t_start = time.time()
          timings = {}

          # 1 Hybrid Search
          t0 = time.time()
          initial_chunks = self.retriever.search(query, top_k=10)
          timings["search_ms"] = round((time.time() - t0)*1000, 2)

          # 2 Cross Encoder reranking
          t0 = time.time()
          top_chunks = self.reranker.rerank(query, initial_chunks, top_k=top_k)
          timings["rerank_ms"] = round((time.time() - t0) * 1000, 2)

          # 3 Pack Context
          context_str, sources = self.context_builder.build(top_chunks)

          # 4 LLM Generation
          t0 = time.time()
          llm_response = self.llm.generate_answer(query, context_str)
          timings["llm_ms"] = round((time.time() - t0) * 1000, 2)

          total_latency_ms = round((time.time() - t_start) * 1000, 2)

          return {
               "question": query,
               "answer": llm_response["answer"],
               "sources": sources,
               "retrieved_chunks": [
                    {
                         "chunk_id": c["chunk_id"],
                         "rerank_score": c.get("rerank_score", 0.0),
                         "source_file": c["metadata"]["source_file"],
                         "page_number": c["metadata"]["page_number"],
                    }
                    for c in top_chunks
               ],
               "tokens": {
                    "input": llm_response["input_tokens"],
                    "output": llm_response["output_tokens"]
               },
               "timings_ms": {
                    **timings,
                    "total_ms": total_latency_ms
               }
          }