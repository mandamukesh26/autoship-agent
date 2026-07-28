from agents.bug_detector import detect_bugs


def test_detect_bugs_returns_fallback_on_ai_error(monkeypatch):
    def raise_error(*args, **kwargs):
        raise RuntimeError("AI request failed")

    monkeypatch.setattr("agents.bug_detector.ai.ask", raise_error)

    result = detect_bugs({"files": {"app.py": "print('hello')"}})

    assert result["overall_score"] == 0
    assert result["bugs"] == []
    assert result["security_issues"] == []
    assert result["performance_issues"] == []
    assert "could not be completed" in result["summary"].lower()
