from agents.fix_generator import generate_fixes


def test_generate_fixes_returns_valid_fallback_when_ai_fails(monkeypatch):
    def raise_error(*args, **kwargs):
        raise RuntimeError("AI request failed")

    monkeypatch.setattr("agents.fix_generator.ai.ask", raise_error)

    bugs_found = {"bugs": [{"file": "app.py", "description": "Null pointer", "severity": "high"}]}
    repo_data = {"files": {"app.py": "print('hello')"}}

    result = generate_fixes(bugs_found, repo_data)

    assert result["total_bugs"] == 1
    assert result["fixes_generated"] == 1
    assert result["fixes"][0]["file"] == "app.py"
    assert result["fixes"][0]["fixed_code"] == ""
    assert result["fixes"][0]["explanation"].startswith("Fallback")


def test_generate_fixes_coerces_invalid_json_to_fallback(monkeypatch):
    def fake_ask(*args, **kwargs):
        return "not valid json"

    monkeypatch.setattr("agents.fix_generator.ai.ask", fake_ask)

    bugs_found = {"bugs": [{"file": "app.py", "description": "Null pointer", "severity": "high"}]}
    repo_data = {"files": {"app.py": "print('hello')"}}

    result = generate_fixes(bugs_found, repo_data)

    assert result["fixes"][0]["fixed_code"] == ""
    assert result["fixes"][0]["explanation"].startswith("Fallback")
