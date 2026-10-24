from typing import Any, Dict, List
from src.core.logging import app_logger
from qdrant_client import QdrantClient
from qdrant_client.models import Fusion, FusionQuery, Prefetch, SparseVector
from src.config.settings import settings
from src.ingestion.embedder import BGEM3Embedder

class HybridRetriever:
  def __init__(self):
    self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, api_key=settings.QDRANT_API_KEY or None,  timeout=30,)
    self.collection_name = settings.COLLECTION_NAME
    self.embedder = BGEM3Embedder()  
    app_logger.info(f"[Retriever] Create HybridRetriever for collection '{self.collection_name}'")

  @staticmethod
  def _to_sparse_vector(lexical_weights: Dict[str, float]) -> SparseVector:
    """converting a dictionary of lexical weights to a Qdrant SparseVector."""
    pairs = []
    for token_str, weight in lexical_weights.items():
      if weight <= 0:
        continue
      try:
        token_id = int(token_str)
        weight = float(weight)
        pairs.append((token_id, weight))
      except ValueError:
        continue
    pairs.sort(key=lambda item: item[0])
    indices = [idx for idx, _ in pairs]
    values = [val for _,val in pairs]
    return SparseVector(indices=indices, values=values)

  def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """ Search (Dense + Sparse) with RRF into Qdrant."""
    if not query.strip():
      return []
    # 1 embed query to Dense + Sparse
    query_emb = self.embedder.embed_query(query)
    dense_vec = query_emb["dense_vecs"][0]
    sparse_vec = self._to_sparse_vector(query_emb["lexical_weights"][0])

    # 2 query Qdrant with Prefetch + RRF Fusion
    prefetch_limit = max(top_k * 2, 20)
    response = self.client.query_points(
        collection_name=self.collection_name,
        prefetch=[
            Prefetch(query=dense_vec, using="dense", limit=prefetch_limit,),
            Prefetch(query=sparse_vec, using="sparse", limit=prefetch_limit,),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
    )

    results = []
    for point in response.points:
      payload = point.payload or {}
      results.append({
          "chunk_id": str(point.id),
          "score": point.score,
          "text": payload.get("text", ""),
          "metadata": {
              "source_file": payload.get("source_file", "unknown"),
              "page_number": payload.get("page_number", 1),
              "chunk_index": payload.get("chunk_index", 0),
              "char_count": payload.get("char_count", 0),
          },
      })

    app_logger.debug(f"[Retriever] Query: '{query[:30]}...' Obtained {len(results)} chunks from Qdrant (RRF)")
    return results