import sys
from pathlib import Path
from typing import Dict, Any, List

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.core.logging import app_logger
from src.rag.pipeline import RAGPipeline
from src.eval.retrieval_eval import RetrievalEvaluator
from src.eval.ragas_runner import RagasRunner
from src.eval.reporter import EvaluationReporter

# 10 Fixed Canary Questions for Rapid CI Quality Gates (< 2 mins runtime)
CANARY_QUESTIONS = [
    {
        "question": "What is the minimum required password length according to company policy?",
        "ground_truth": "Passwords must be at least 12 characters long.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "When is Multi-Factor Authentication (MFA) required for employees?",
        "ground_truth": "All employees are required to use Multi-Factor Authentication (MFA) when accessing the internal corporate VPN.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "How should customer Personally Identifiable Information (PII) be encrypted?",
        "ground_truth": "Customers' Personally Identifiable Information (PII) must be encrypted using the AES-256 standard both at-rest and in-transit.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "Is using public Wi-Fi networks allowed for remote work?",
        "ground_truth": "Using public Wi-Fi networks to access internal systems is strictly prohibited without corporate VPN connection.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "How often must corporate passwords be changed according to policy?",
        "ground_truth": "Passwords must be changed periodically every 90 days.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "Can PII data be shared via email or public chat channels?",
        "ground_truth": "Sharing files containing PII via public chat channels or unapproved personal email is strictly prohibited.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What software must be installed on personal devices used for work?",
        "ground_truth": "All personal devices used for work must have company-approved antivirus software and MDM installed.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What is the minimum unit test code coverage required before merging code?",
        "ground_truth": "Unit tests must achieve a minimum code coverage of 80% before merging into the main branch.",
        "source_file": "company_security_policy.md",
        "is_in_domain": True
    },
    {
        "question": "What is the best recipe for authentic Italian carbonara pasta?",
        "ground_truth": "The internal documentation does not contain cooking recipes.",
        "source_file": "",
        "is_in_domain": False
    },
    {
        "question": "Who won the FIFA World Cup in 2022?",
        "ground_truth": "The internal documentation does not contain sports tournament records.",
        "source_file": "",
        "is_in_domain": False
    }
]


def run_mini_evaluation(output_dir: str = "reports") -> bool:
    """
    Executes rapid canary evaluation (10 questions):
    1. Retrieval evaluation (Recall@5, MRR)
    2. Generation evaluation (Faithfulness, Answer Relevance)
    3. Enforces CI Quality Gate: Recall@5 >= 0.70, MRR >= 0.65, Faithfulness >= 0.80
    Returns True if quality gates passed, False otherwise.
    """
    app_logger.info(f"[MiniEval] Starting Canary evaluation on {len(CANARY_QUESTIONS)} questions...")

    # 1. Retrieval Eval
    retrieval_evaluator = RetrievalEvaluator()
    retrieval_metrics = retrieval_evaluator.evaluate_dataset(CANARY_QUESTIONS, top_k=5)

    # 2. RAG Generation
    rag_pipeline = RAGPipeline()
    records_for_ragas = []
    details = []

    for item in CANARY_QUESTIONS:
        q = item["question"]
        gt = item["ground_truth"]
        is_in_domain = item.get("is_in_domain", True)

        result = rag_pipeline.run(query=q, top_k=3)
        answer = result["answer"]
        contexts = result.get("contexts", [])

        # For in-domain questions, evaluate Ragas generation metrics
        if is_in_domain and contexts:
            records_for_ragas.append({
                "question": q,
                "contexts": contexts,
                "answer": answer,
                "ground_truth": gt,
            })

        details.append({
            "question": q,
            "answer": answer,
            "ground_truth": gt,
            "is_in_domain": is_in_domain,
            "sources_count": len(result.get("sources", [])),
            "latency_total_ms": result["timings_ms"]["total_ms"],
        })

    # 3. Ragas Generation Eval
    ragas_runner = RagasRunner()
    ragas_metrics = ragas_runner.run_evaluation(records_for_ragas)

    # 4. Summary & Quality Gates
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


if __name__ == "__main__":
    passed = run_mini_evaluation()
    sys.exit(0 if passed else 1)
