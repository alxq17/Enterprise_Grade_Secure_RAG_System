import pytest
from src.guardrails.domain_guard import DomainGuard


def test_domain_guard_in_domain():
    guard = DomainGuard(threshold=0.35)
    chunks = [
        {"chunk_id": "1", "rerank_score": 0.85, "text": "Password policy"},
        {"chunk_id": "2", "rerank_score": 0.20, "text": "Other"},
    ]
    assert guard.is_in_domain(chunks) is True


def test_domain_guard_out_of_domain():
    guard = DomainGuard(threshold=0.35)
    chunks = [
        {"chunk_id": "1", "rerank_score": 0.12, "text": "Unrelated topic"},
        {"chunk_id": "2", "rerank_score": 0.05, "text": "Other"},
    ]
    assert guard.is_in_domain(chunks) is False


def test_domain_guard_empty_chunks():
    guard = DomainGuard(threshold=0.35)
    assert guard.is_in_domain([]) is False
    assert guard.is_in_domain(None) is False
