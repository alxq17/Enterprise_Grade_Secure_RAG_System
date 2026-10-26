import sys
import argparse
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tabulate import tabulate
from src.core.logging import app_logger
from src.retrieval.hybrid_search import HybridRetriever
from src.retrieval.reranker import DocumentReranker
from src.config.settings import settings


def main():
    parser = argparse.ArgumentParser(description="VeriRAG Retrieval & Reranker CLI Diagnostic Tool")
    parser.add_argument("--query", "-q", type=str, required=True, help="Search query string")
    parser.add_argument("--top-k", "-k", type=int, default=3, help="Top K results after reranking")
    args = parser.parse_args()

    app_logger.info(f"Query: '{args.query}'")
    retriever = HybridRetriever()
    reranker = DocumentReranker()

    # Step 1: Hybrid Search
    raw_chunks = retriever.search(args.query, top_k=10)
    app_logger.info(f"Hybrid search retrieved {len(raw_chunks)} candidate chunks.")

    if not raw_chunks:
        print("\nNo candidates retrieved.")
        return

    # Step 2: Rerank
    reranked = reranker.rerank(args.query, raw_chunks, top_k=args.top_k)

    table_data = []
    threshold = settings.DOMAIN_SIMILARITY_THRESHOLD
    for rank, doc in enumerate(reranked, 1):
        score = doc.get("rerank_score", 0.0)
        status = "IN-DOMAIN" if score >= threshold else f"BELOW_GATE (< {threshold})"
        source = doc.get("metadata", {}).get("source_file") or doc.get("source_file", "unknown")
        snippet = doc.get("text", "").replace("\n", " ")[:90] + "..."
        table_data.append([rank, f"{score:.4f}", status, source, snippet])

    print("\n" + "=" * 90)
    print(f"  RETRIEVAL & RERANK RESULTS for: '{args.query}'")
    print("=" * 90)
    print(tabulate(table_data, headers=["Rank", "Score", "Domain Status", "Source", "Chunk Snippet"], tablefmt="grid"))
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
