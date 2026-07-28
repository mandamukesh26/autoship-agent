from agents.self_reviewer import review_fixes


def test_review_fixes_returns_fallback_when_ai_fails(monkeypatch):
    def raise_error(*args, **kwargs):
        raise RuntimeError("AI request failed")

    monkeypatch.setattr("agents.self_reviewer.ai.ask", raise_error)

    bugs_found = {"bugs": [{"file": "app.py", "description": "Null pointer"}]}
    fixes_generated = {"fixes": [{"file": "app.py", "fixed_code": "print('hello')", "explanation": "simple"}]}
    repo_data = {"files": {"app.py": "print('hello')"}}

    result = review_fixes(bugs_found, fixes_generated, repo_data)

    assert result["review_score"] == 0
    assert result["fixes_validated"] == []
    assert result["confidence_level"] == "low"
    assert "manual review required" in result["recommendations"][0].lower()


def test_review_fixes_coerces_invalid_json_to_fallback(monkeypatch):
    def fake_ask(*args, **kwargs):
        return "not valid json"

    monkeypatch.setattr("agents.self_reviewer.ai.ask", fake_ask)

    bugs_found = {"bugs": [{"file": "app.py", "description": "Null pointer"}]}
    fixes_generated = {"fixes": [{"file": "app.py", "fixed_code": "print('hello')", "explanation": "simple"}]}
    repo_data = {"files": {"app.py": "print('hello')"}}

    result = review_fixes(bugs_found, fixes_generated, repo_data)

    assert result["review_score"] == 0
    assert result["fixes_validated"] == []
    assert result["confidence_level"] == "low"
