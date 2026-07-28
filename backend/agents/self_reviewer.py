import json
import logging

from utils.ai_client import get_groq_response  # Updated import

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

def _build_fallback_review(reason):
    return {
        "review_score": 0,
        "fixes_validated": [],
        "overall_assessment": f"Review failed: {reason}",
        "confidence_level": "low",
        "recommendations": ["Manual review required"],
    }

def _normalize_review_response(raw_response):
    if not isinstance(raw_response, dict):
        return _build_fallback_review("AI returned an invalid response format")

    normalized = {
        "review_score": raw_response.get("review_score", 0),
        "fixes_validated": raw_response.get("fixes_validated", []) or [],
        "overall_assessment": raw_response.get("overall_assessment", "No assessment provided."),
        "confidence_level": raw_response.get("confidence_level", "low"),
        "recommendations": raw_response.get("recommendations", ["Manual review required"]) or ["Manual review required"],
    }

    if not isinstance(normalized["review_score"], (int, float)):
        normalized["review_score"] = 0
    if not isinstance(normalized["fixes_validated"], list):
        normalized["fixes_validated"] = []
    if not isinstance(normalized["recommendations"], list):
        normalized["recommendations"] = ["Manual review required"]
    if not isinstance(normalized["overall_assessment"], str):
        normalized["overall_assessment"] = str(normalized["overall_assessment"])
    if not isinstance(normalized["confidence_level"], str):
        normalized["confidence_level"] = "low"

    return normalized

def review_fixes(bugs_found, fixes_generated, repo_data):
    """
    Agent: Reviews the quality of generated fixes and validates they solve the problems.
    Validates inputs, logs failures, and ensures JSON-safe output.
    """
    if not isinstance(bugs_found, dict):
        logger.error("Invalid bugs_found input: expected dict, got %s", type(bugs_found).__name__)
        return _build_fallback_review("Invalid bugs input")

    if not isinstance(fixes_generated, dict):
        logger.error("Invalid fixes_generated input: expected dict, got %s", type(fixes_generated).__name__)
        return _build_fallback_review("Invalid fixes input")

    if not isinstance(repo_data, dict):
        logger.error("Invalid repo_data input: expected dict, got %s", type(repo_data).__name__)
        return _build_fallback_review("Invalid repository input")

    bugs = bugs_found.get("bugs", [])
    fixes = fixes_generated.get("fixes", [])

    if not isinstance(bugs, list):
        logger.error("Invalid bugs payload: expected list, got %s", type(bugs).__name__)
        bugs = []
    if not isinstance(fixes, list):
        logger.error("Invalid fixes payload: expected list, got %s", type(fixes).__name__)
        fixes = []

    # Prepare context
    bug_list = json.dumps(bugs[:3], indent=2)
    fix_list = json.dumps(fixes[:3], indent=2)

    messages = [
        {
            "role": "system",
            "content": """You are a senior code reviewer. Review the fixes generated for the bugs found.

Evaluate:
1. Do the fixes actually solve the reported bugs?
2. Is the code quality good?
3. Are there any side effects or new issues introduced?

Return STRICT JSON:
{
    "review_score": 0-100,
    "fixes_validated": [{"file": "path", "valid": true/false, "notes": "explanation"}],
    "overall_assessment": "detailed review",
    "confidence_level": "high/medium/low",
    "recommendations": ["list of improvements"]
}"""
        },
        {
            "role": "user",
            "content": f"""Original Bugs:
{bug_list}

Generated Fixes:
{fix_list}

Review these fixes critically."""
        }
    ]

    try:
        logger.info("Starting self-review for %d bugs and %d fixes", len(bugs), len(fixes))
        # Updated AI call for Groq
        response = get_groq_response(json.dumps(messages), model="llama3-8b-8192")
        if not isinstance(response, str):
            raise ValueError("AI response was not a string")

        parsed_response = json.loads(response)
        return _normalize_review_response(parsed_response)
    except json.JSONDecodeError as exc:
        logger.exception("Could not parse self-review response as JSON: %s", exc)
        return _build_fallback_review("AI returned invalid JSON")
    except Exception as exc:
        logger.exception("Self-review failed: %s", exc)
        return _build_fallback_review(f"AI failure: {exc}")