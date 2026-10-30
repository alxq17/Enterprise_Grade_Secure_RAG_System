from unittest.mock import MagicMock

import pytest

from src.eval.retrieval_eval import RetrievalEvaluator


@pytest.fixture
def mock_retrieval_evaluator():
    mock_retriever = MagicMock()
    mock_reranker = MagicMock()

    mock_retriever.search.return_value = [
        {"chunk_id": "c1", "metadata": {"source_file": "company_security_policy.md"}},
        {"chunk_id": "c2", "metadata": {"source_file": "other_doc.md"}},
        {"chunk_id": "c3", "metadata": {"source_file": "unrelated.md"}},
    ]

    mock_reranker.rerank.return_value = [
        {"chunk_id": "c1", "metadata": {"source_file": "company_security_policy.md"}},
        {"chunk_id": "c2", "metadata": {"source_file": "other_doc.md"}},
        {"chunk_id": "c3", "metadata": {"source_file": "unrelated.md"}},
    ]

    return RetrievalEvaluator(retriever=mock_retriever, reranker=mock_reranker)


def test_evaluate_item_hit_rank_1(mock_retrieval_evaluator):
    res = mock_retrieval_evaluator.evaluate_item(
        query="password requirements",
        expected_source="company_security_policy.md",
        top_k=5,
    )
    assert res["recall@3"] == 1.0
    assert res["recall@5"] == 1.0
    assert res["mrr"] == 1.0


def test_evaluate_item_miss(mock_retrieval_evaluator):
    res = mock_retrieval_evaluator.evaluate_item(
        query="arbitrary query",
        expected_source="non_existent_policy.md",
        top_k=5,
    )
    assert res["recall@3"] == 0.0
    assert res["recall@5"] == 0.0
    assert res["mrr"] == 0.0


def test_evaluate_dataset(mock_retrieval_evaluator):
    dataset = [
        {"question": "q1", "source_file": "company_security_policy.md", "is_in_domain": True},
        {"question": "q2", "source_file": "non_existent.md", "is_in_domain": True},
        {"question": "q3", "source_file": "", "is_in_domain": False},  # Out of domain ignored
    ]
    metrics = mock_retrieval_evaluator.evaluate_dataset(dataset, top_k=5)
    assert "mean_recall@5" in metrics
    assert "mean_mrr" in metrics
    assert metrics["mean_recall@5"] == 0.5  # 1 hit out of 2 in-domain questions
    assert metrics["mean_mrr"] == 0.5
