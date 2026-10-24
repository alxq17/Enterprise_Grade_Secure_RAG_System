import argparse
import sys
import time
from src.core.logging import app_logger
from src.retrieval.context_builder import ContextBuilder
from src.retrieval.hybrid_search import HybridRetriever
from src.retrieval.reranker import DocumentReranker


def run_test(query: str):
    app_logger.info(f"Searching for query: '{query}'")
    t0 = time.time()
    retriever = HybridRetriever()
    reranker = DocumentReranker()

    # 1. Hybrid Search (Dense + Sparse + RRF)
    t_search = time.time()
    initial_chunks = retriever.search(query, top_k=10)
    search_latency = time.time() - t_search

    if not initial_chunks:
        app_logger.warning("No relevant documents found in Qdrant.")
        return
    app_logger.info(f"Qdrant RRF returned {len(initial_chunks)} chunks " f"in {search_latency:.2f}s")

    # 2. Rerank using Cross-Encoder
    t_rerank = time.time()
    top_chunks = reranker.rerank(query, initial_chunks, top_k=3)
    rerank_latency = time.time() - t_rerank

    app_logger.info(f"Reranking completed in {rerank_latency:.2f}s. " f"Total time: {time.time() - t0:.2f}s\n")

    # 3. Display the Top-3 Results
    print("=" * 80)
    print(f"TOP-{len(top_chunks)} MOST RELEVANT CHUNKS")
    print("=" * 80)

    for i, c in enumerate(top_chunks, 1):
        meta = c["metadata"]
        print(f"\n[#{i}] Rerank Score: {c['rerank_score']:.4f} " f"| RRF Score: {c['score']:.4f}")
        print(f"    Source: {meta['source_file']} " f"(Page {meta['page_number']})")
        print(f"    Content: {c['text'][:250]}...")
        print("-" * 80)

    # 4. Inspect the Context Builder
    context_str, sources = ContextBuilder.build(top_chunks)
    print("\n[Preview of the Context Sent to Gemini]:")
    print(context_str[:300] + "...\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Hybrid Search and Reranking")
    parser.add_argument(
        "query",
        nargs="?",
        default="What is the password security policy?",
        help="Test query",
    )
    args = parser.parse_args()
    run_test(args.query)