from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "x-request-id" in response.headers


def test_readyz():
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "qdrant_connected"
    assert data["llm"] == "gemini_configured"


def test_query_validation_error():
    # Question too short (< 3 chars)
    response = client.post("/api/v1/query", json={"question": "hi"})
    assert response.status_code == 422


def test_query_e2e_success():
    payload = {"question": "What are the requirements regarding passwords and MFA?", "top_k": 3}
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "sources" in data
    assert len(data["sources"]) > 0
    assert "retrieved_chunks" in data
    assert len(data["retrieved_chunks"]) <= 3
    assert "tokens" in data
    assert "timings_ms" in data
    assert "request_id" in data
    assert "x-request-id" in response.headers
