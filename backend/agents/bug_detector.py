import json
import logging

from utils.ai_client import ai

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def detect_bugs(repo_data):
    """
    Agent: Analyzes code for bugs, security issues, and performance problems.
    Returns a structured result or a safe fallback when analysis fails.
    """
    fallback_result = {
        "bugs": [],
        "security_issues": [],
        "performance_issues": [],
        "overall_score": 0,
        "summary": "Bug detection could not be completed due to an internal error.",
    }

    if not isinstance(repo_data, dict):
        logger.error("Invalid repository data provided to detect_bugs: expected dict, got %s", type(repo_data).__name__)
        return fallback_result

    files = repo_data.get("files")
    if not isinstance(files, dict) or not files:
        logger.warning("No repository files were provided for bug detection.")
        return fallback_result

    try:
        # Get sample files (first 5)
        sample_files = list(files.items())[:5]
        logger.info("Starting bug detection on %d sample files", len(sample_files))

        # Build context
        context = ""
        for path, content in sample_files:
            if not isinstance(content, str):
                logger.warning("Skipping non-string content for %s", path)
                continue
            context += f"\n\nFILE: {path}\n```{content[:2000]}```"

        if not context.strip():
            logger.warning("No usable file content available for analysis.")
            return fallback_result

        messages = [
            {
                "role": "system",
                "content": """You are a senior code auditor. Analyze code for bugs, security vulnerabilities, and performance issues.

Return STRICT JSON format:
{
    "bugs": [{"severity": "high/medium/low", "file": "path", "line": "number", "description": "details"}],
    "security_issues": [{"severity": "high/medium/low", "file": "path", "description": "details"}],
    "performance_issues": [{"severity": "high/medium/low", "file": "path", "description": "details"}],
    "overall_score": 0-100,
    "summary": "brief assessment"
}"""
            },
            {
                "role": "user",
                "content": f"Analyze this repository:\n{context}"
            }
        ]

        # Updated AI call (Groq)
        from utils.ai_client import get_groq_response
        response = get_groq_response(json.dumps(messages), model="llama3-8b-8192")

        parsed_response = json.loads(response)

        if not isinstance(parsed_response, dict):
            raise ValueError("AI response was not a JSON object")

        return {
            "bugs": parsed_response.get("bugs", []) or [],
            "security_issues": parsed_response.get("security_issues", []) or [],
            "performance_issues": parsed_response.get("performance_issues", []) or [],
            "overall_score": parsed_response.get("overall_score", 0),
            "summary": parsed_response.get("summary", "Bug detection completed with a missing summary."),
        }
    except json.JSONDecodeError as exc:
        logger.exception("Failed to parse bug detection response as JSON: %s", exc)
        return fallback_result
    except Exception as exc:
        logger.exception("Bug detection failed: %s", exc)
        return fallback_result