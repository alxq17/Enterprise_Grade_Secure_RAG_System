import pytest
from unittest.mock import patch, MagicMock
from src.eval.ragas_runner import RagasRunner


def test_ragas_runner_empty_records():
    runner = RagasRunner()
    scores = runner.run_evaluation([])
    assert scores == {"faithfulness": 0.0, "answer_relevancy": 0.0}


@patch("src.eval.ragas_runner.evaluate")
def test_ragas_runner_mocked_success(mock_evaluate):
    # Mock EvaluationResult returned by evaluate
    mock_res = MagicMock()
    mock_res._repr_dict = {"faithfulness": 0.95, "answer_relevancy": 0.88}
    mock_evaluate.return_value = mock_res

    runner = RagasRunner()
    records = [
        {
            "question": "What is MFA?",
            "contexts": ["MFA is required for VPN."],
            "answer": "MFA is required for VPN access.",
            "ground_truth": "MFA is required for VPN."
        }
    ]
    scores = runner.run_evaluation(records)
    assert scores["faithfulness"] == 0.95
    assert scores["answer_relevancy"] == 0.88


@patch("src.eval.ragas_runner.evaluate")
def test_ragas_runner_handles_exception_gracefully(mock_evaluate):
    mock_evaluate.side_effect = RuntimeError("Evaluation timeout")

    runner = RagasRunner()
    records = [{"question": "Q?", "contexts": ["C"], "answer": "A", "ground_truth": "GT"}]
    scores = runner.run_evaluation(records)
    assert scores["faithfulness"] == 0.0
    assert scores["answer_relevancy"] == 0.0
