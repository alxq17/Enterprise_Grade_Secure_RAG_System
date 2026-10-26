from typing import List, Dict, Any, Optional
from src.core.logging import app_logger
from src.retrieval.hybrid_search import HybridRetriever
from src.retrieval.reranker import DocumentReranker


class RetrievalEvaluator:
    """
    Algorithmic evaluation of retrieval quality:
    - Recall@K: proportion of test cases where relevant chunk is in top K
    - MRR (Mean Reciprocal Rank): 1 / rank of first relevant chunk
    Requires no external LLM API calls.
    """

    def __init__(self, retriever: Optional[HybridRetriever] = None, reranker: Optional[DocumentReranker] = None):
        self.retriever = retriever or HybridRetriever()
        self.reranker = reranker or DocumentReranker()

    def evaluate_item(self, query: str, expected_source: str, top_k: int = 5) -> Dict[str, float]:
        """Evaluate retrieval performance for a single query."""
        initial_chunks = self.retriever.search(query, top_k=10)
        ranked_chunks = self.reranker.rerank(query, initial_chunks, top_k=top_k)

        hit_at_3 = False
        hit_at_5 = False
        reciprocal_rank = 0.0

        for rank, chunk in enumerate(ranked_chunks, start=1):
            source_file = chunk.get("metadata", {}).get("source_file", "")
            # Check if source matches expected
            if expected_source.lower() in source_file.lower() or source_file.lower() in expected_source.lower():
                if rank <= 3:
                    hit_at_3 = True
                if rank <= 5:
                    hit_at_5 = True
                if reciprocal_rank == 0.0:
                    reciprocal_rank = 1.0 / rank

        return {
            "recall@3": 1.0 if hit_at_3 else 0.0,
            "recall@5": 1.0 if hit_at_5 else 0.0,
            f"recall@{top_k}": 1.0 if (hit_at_5 if top_k >= 5 else hit_at_3) else 0.0,
            "mrr": reciprocal_rank,
        }

    def evaluate_dataset(self, dataset: List[Dict[str, Any]], top_k: int = 5) -> Dict[str, float]:
        """Evaluate entire dataset and compute mean metrics."""
        # Only evaluate in-domain questions that have expected source
        in_domain_items = [
            item for item in dataset
            if item.get("is_in_domain", True) and item.get("source_file")
        ]

        count = len(in_domain_items)
        if count == 0:
            return {"mean_recall@3": 0.0, "mean_recall@5": 0.0, "mean_mrr": 0.0}

        total_recall_3 = 0.0
        total_recall_5 = 0.0
        total_mrr = 0.0

        for idx, item in enumerate(in_domain_items, 1):
            res = self.evaluate_item(item["question"], item["source_file"], top_k=top_k)
            total_recall_3 += res["recall@3"]
            total_recall_5 += res["recall@5"]
            total_mrr += res["mrr"]

        mean_recall_3 = round(total_recall_3 / count, 4)
        mean_recall_5 = round(total_recall_5 / count, 4)
        mean_mrr = round(total_mrr / count, 4)

        app_logger.info(
            f"[RetrievalEval] ({count} items) Recall@3: {mean_recall_3} | Recall@5: {mean_recall_5} | MRR: {mean_mrr}"
        )

        return {
            "mean_recall@3": mean_recall_3,
            "mean_recall@5": mean_recall_5,
            "mean_mrr": mean_mrr,
        }