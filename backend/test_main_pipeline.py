from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_analyze_repo_returns_fallback_on_bad_input():
    response = client.post("/analyze", json={"repo_url": ""})
    assert response.status_code == 400


def test_analyze_repo_handles_invalid_repo_url(monkeypatch):
    def raise_error(*args, **kwargs):
        raise RuntimeError("fetch failed")

    monkeypatch.setattr("main.get_repo_content", raise_error)

    response = client.post("/analyze", json={"repo_url": "https://example.com/repo"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "fallback"
    assert payload["analysis"]["review_score"] == 0
