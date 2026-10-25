from typing import List, Dict, Any
from src.core.logging import app_logger
from src.config.settings import settings

class DomainGuard:
     def __init__(self, threshold: float | None = None):
          self.threshold = threshold if threshold is not None else settings.DOMAIN_SIMILARITY_THRESHOLD
     
     def is_in_domain(self, top_chunks: List[Dict[str, Any]]) -> bool:
          # Check the relevance of search results to the query
          if not top_chunks or len(top_chunks) == 0:
               app_logger.warning("[DomainGuard] No chunks were returned from the Retrieval layer")
               return False
          
          # Get points rerank_score from highest chunk
          top_score = float(top_chunks[0].get("rerank_score", 0.0))
          if top_score < self.threshold:
               app_logger.warning(f"[DomainGuard] Question outside the scope of the document (Top Score: {top_score:.4f} < Threshold: {self.threshold})")
               return False
          app_logger.debug(f"[DomainGuard] Relevance threshold met (Top Score: {top_score:.4f} >= Threshold: {self.threshold})")
          return True 
     