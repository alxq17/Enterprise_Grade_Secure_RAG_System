from typing import List, Dict, Any
from src.core.logging import app_logger
from src.retrieval.hybrid_search import HybridRetriever
from src.retrieval.reranker import DocumentReranker

class RetrievalEvaluator:
     def __init__(self):
          self.retriever = HybridRetriever()
          self.reranker = DocumentReranker()

     def evaluate_item(self, query: str, expected_source: str, top_k: int = 3) -> Dict[str, float]:
          # 1 Hybrid Search
          initial_chunks = self.retriever.search(query, top_k=10)
          # 2 Rerank
          ranked_chunks = self.reranker.rerank(query, initial_chunks, top_k=top_k)

          hit = False
          reciprocal_rank = 0.0
          
          for rank, chunk in enumerate(ranked_chunks, start=1):
               source_file = chunk.get("metadata", {}).get("source_file", "")
               if expected_source.lower() in source_file.lower():
                    hit = True
                    if reciprocal_rank == 0.0:
                         reciprocal_rank = 1.0 / rank
          return {f"recal@{top_k}" : 1.0 if hit else 0.0, "mrr": reciprocal_rank}
     
     def evaluate_dataset(self, dataset: List[Dict[str, Any]], top_k: int = 3) -> Dict[str, float]:
          total_recall = 0.0
          total_mrr = 0.0
          count = len(dataset)

          if count == 0:
               return {"mean_recall": 0.0, "mean_mrr": 0.0}
          for idx, item in enumerate(dataset, 1):
               res = self.evaluate_item(item["question"], item["source_file"], top_k=top_k)
               total_recall += res[f"recall@{top_k}"]
               total_mrr += res[f"mrr"]
          mean_recall = total_recall/count
          mean_mrr = total_mrr/count

          app_logger.info(f"[RetrievalEval] Recall@{top_k}: {mean_recall:.4f} | MRR: {mean_mrr:.4f}")
          return {
               f"mean_recall@{top_k}": round(mean_recall, 4),
               "mean_mrr": round(mean_mrr, 4)
          }