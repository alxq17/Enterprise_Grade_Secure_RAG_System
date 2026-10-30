import argparse
import json
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.logging import app_logger
from src.eval.mini_eval import run_mini_evaluation
from src.eval.ragas_runner import RagasRunner
from src.eval.reporter import EvaluationReporter
from src.eval.retrieval_eval import RetrievalEvaluator
from src.rag.pipeline import RAGPipeline


def load_golden_dataset(path: str, limit: int | None = None):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if limit:
        return data[:limit]
    return data


def run_full_evaluation(golden_path: str, output_dir: str = "reports") -> bool:
    dataset = load_golden_dataset(golden_path)
    app_logger.info(f"Starting Full Evaluation on {len(dataset)} questions...")

    # 1. Retrieval evaluation (pure algorithmic, no LLM required)
    retrieval_evaluator = RetrievalEvaluator()
    retrieval_metrics = retrieval_evaluator.evaluate_dataset(dataset, top_k=5)

    # 2. RAG pipeline execution
    rag_pipeline = RAGPipeline()
    records_for_ragas = []
    details = []

    for item in dataset:
        q = item["question"]
        gt = item.get("ground_truth", "")
        is_in_domain = item.get("is_in_domain", True)

        result = rag_pipeline.run(query=q, top_k=3)
        answer = result["answer"]
        contexts = result.get("contexts", [])

        # Only evaluate faithfulness on in-domain queries where context was retrieved
        if is_in_domain and contexts:
            records_for_ragas.append(
                {
                    "question": q,
                    "contexts": contexts,
                    "answer": answer,
                    "ground_truth": gt,
                }
            )

        details.append(
            {
                "question": q,
                "answer": answer,
                "ground_truth": gt,
                "is_in_domain": is_in_domain,
                "sources_count": len(result.get("sources", [])),
                "latency_total_ms": result["timings_ms"]["total_ms"],
            }
        )

    # 3. Ragas generation evaluation
    ragas_runner = RagasRunner()
    ragas_metrics = ragas_runner.run_evaluation(records_for_ragas)

    # 4. Report & Regression Quality Gate
    summary_metrics = {**retrieval_metrics, **ragas_metrics}
    reporter = EvaluationReporter(output_dir=output_dir)

    gates = {
        "mean_recall@5": 0.70,
        "mean_mrr": 0.65,
        "faithfulness": 0.80,
        "answer_relevancy": 0.75,
    }

    report_path, is_passed = reporter.export_summary(
        metrics=summary_metrics,
        details=details,
        gate_thresholds=gates,
    )
    return is_passed


def main():
    parser = argparse.ArgumentParser(description="VeriRAG Quantitative Evaluation Runner")
    parser.add_argument(
        "--mini",
        action="store_true",
        help="Run fast CI canary evaluation (10 fixed questions, < 2 minutes)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run complete baseline evaluation on entire golden dataset",
    )
    parser.add_argument(
        "--golden",
        default="data/golden/golden_dataset.json",
        help="Path to Golden Dataset file",
    )
    parser.add_argument(
        "--output",
        default="reports",
        help="Output directory for CSV reports and baseline metrics",
    )

    args = parser.parse_args()

    # Default to mini if neither is specified
    if args.mini or (not args.full and not args.mini):
        app_logger.info("Running in MINI mode (Canary CI gate)...")
        passed = run_mini_evaluation(output_dir=args.output)
    else:
        app_logger.info("Running in FULL mode (Complete Dataset)...")
        passed = run_full_evaluation(golden_path=args.golden, output_dir=args.output)

    if not passed:
        app_logger.error("Evaluation quality gates breached! Exiting with code 1.")
        sys.exit(1)
    else:
        app_logger.info("Evaluation completed successfully with all gates passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
