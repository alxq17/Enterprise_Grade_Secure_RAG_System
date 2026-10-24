from typing import Any, Dict, List
from FlagEmbedding import FlagReranker
from src.core.logging import app_logger
from src.config.settings import settings

class DocumentReranker:
     _instance = None
     def __new__(cls, *args, **kwargs):
          if cls._instance is None:
               cls._instance = super().__new__(cls)
               cls._instance._initialized = False
          return cls._instance
     def __init__(self, model_name: str | None = None, use_fp16:bool=False):
          if self._initialized:
               return
          self.model_name = model_name or settings.RERANKER_MODEL
          app_logger.info(f"[Reranker] Loading {self.model_name} (Cross-Encoder CPU-only)...")
          
          #flagReranker automatique with support bge-reranker-v2-m3
          self.model = FlagReranker(self.model_name, use_fp16=use_fp16)
          self._initialized = True
          app_logger.info(f"[Reranker] Model ready")

     def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
          """rescore the list of documents and sort them in descending order of relevance"""
          if not documents:
               return []
          pairs = [[query, doc["text"]] for doc in documents]
          # score with use Cross-Encoder
          scores = self.model.compute_score(pairs, normalize=True)
          # if there is only one document, the returned score is a float, we standardize this into a list
          if isinstance(scores, float):
               scores = [scores]
          for doc, score in zip(documents, scores):
               doc["rerank_score"] = float(score)
          # sort in descending order by rerank_score and get top_k
          ranked_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
          selected_docs = ranked_docs[:top_k]
          app_logger.debug(f"[Reranker] Reranked {len(documents)} -> {len(selected_docs)} chunks.")
          return selected_docs