import os
import shutil
import tempfile

import pytest

from src.eval.reporter import EvaluationReporter


@pytest.fixture
def temp_reports_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_reporter_export_and_pass_gates(temp_reports_dir):
    reporter = EvaluationReporter(output_dir=temp_reports_dir)

    metrics = {
        "mean_recall@5": 0.85,
        "mean_mrr": 0.80,
        "faithfulness": 0.90,
        "answer_relevancy": 0.85,
    }
    details = [{"question": "Q1", "answer": "A1", "latency_total_ms": 150.0}]

    report_path, passed = reporter.export_summary(metrics, details)
    assert passed is True
    assert os.path.exists(report_path)


def test_reporter_fails_when_below_threshold(temp_reports_dir):
    reporter = EvaluationReporter(output_dir=temp_reports_dir)

    # Faithfulness below 0.80 threshold
    metrics = {
        "mean_recall@5": 0.85,
        "mean_mrr": 0.80,
        "faithfulness": 0.60,
        "answer_relevancy": 0.85,
    }
    details = []

    report_path, passed = reporter.export_summary(metrics, details)
    assert passed is False


def test_reporter_regression_detection(temp_reports_dir):
    reporter = EvaluationReporter(output_dir=temp_reports_dir)

    # First run establishes baseline
    baseline_metrics = {
        "mean_recall@5": 0.90,
        "mean_mrr": 0.85,
        "faithfulness": 0.95,
        "answer_relevancy": 0.90,
    }
    reporter.export_summary(baseline_metrics, [])

    # Second run has a drop > 5% on faithfulness (0.95 -> 0.85, drop of 0.10)
    second_run_metrics = {
        "mean_recall@5": 0.90,
        "mean_mrr": 0.85,
        "faithfulness": 0.85,  # Pass threshold >= 0.80, but regression > 0.05
        "answer_relevancy": 0.90,
    }
    _, passed = reporter.export_summary(second_run_metrics, [])
    assert passed is False
