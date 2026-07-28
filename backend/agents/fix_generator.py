import json
import logging

from utils.ai_client import ai

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def _build_fallback_fix(file_path, bug, reason):
    return {
        "file": file_path,
        "original_issue": bug.get("description") if isinstance(bug, dict) else None,
        "fixed_code": "",
        "explanation": f"Fallback: {reason}",
    }


def _normalize_fix_data(raw_fix, file_path, bug, reason):
    if isinstance(raw_fix, dict):
        normalized = {
            "file": raw_fix.get("file") or file_path,
            "original_issue": raw_fix.get("original_issue") or bug.get("description") if isinstance(bug, dict) else None,
            "fixed_code": raw_fix.get("fixed_code") or "",
            "explanation": raw_fix.get("explanation") or "No explanation provided.",
        }
        if not isinstance(normalized["fixed_code"], str):
            normalized["fixed_code"] = ""
        if not isinstance(normalized["explanation"], str):
            normalized["explanation"] = str(normalized["explanation"])
        return normalized

    return _build_fallback_fix(file_path, bug, reason)


import json
import logging

from utils.ai_client import get_groq_response  # Changed from 'ai' to 'get_groq_response'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

def _build_fallback_fix(file_path, bug, reason):
    return {
        "file": file_path,
        "original_issue": bug.get("description") if isinstance(bug, dict) else None,
        "fixed_code": "",
        "explanation": f"Fallback: {reason}",
    }

def _normalize_fix_data(raw_fix, file_path, bug, reason):
    if isinstance(raw_fix, dict):
        normalized = {
            "file": raw_fix.get("file") or file_path,
            "original_issue": raw_fix.get("original_issue") or bug.get("description") if isinstance(bug, dict) else None,
            "fixed_code": raw_fix.get("fixed_code") or "",
            "explanation": raw_fix.get("explanation") or "No explanation provided.",
        }
        if not isinstance(normalized["fixed_code"], str):
            normalized["fixed_code"] = ""
        if not isinstance(normalized["explanation"], str):
            normalized["explanation"] = str(normalized["explanation"])
        return normalized

    return _build_fallback_fix(file_path, bug, reason)

def generate_fixes(bugs_found, repo_data):
    """
    Agent: Takes bugs detected and generates specific code fixes.
    Validates inputs, logs failures, and ensures JSON-safe output.
    """
    if not isinstance(bugs_found, dict):
        logger.error("Invalid bugs_found input: expected dict, got %s", type(bugs_found).__name__)
        return {"total_bugs": 0, "fixes_generated": 0, "fixes": []}

    if not isinstance(repo_data, dict) or not isinstance(repo_data.get("files"), dict):
        logger.error("Invalid repo_data input: expected a dict with a 'files' mapping")
        return {"total_bugs": 0, "fixes_generated": 0, "fixes": []}

    bugs = bugs_found.get("bugs", [])
    if not isinstance(bugs, list):
        logger.error("Invalid bugs payload: expected list, got %s", type(bugs).__name__)
        bugs = []

    fixes = []

    for bug in bugs:
        if not isinstance(bug, dict):
            logger.warning("Skipping invalid bug entry: %r", bug)
            continue

        file_path = bug.get("file", "")
        description = bug.get("description", "No description provided")
        severity = bug.get("severity", "unknown")
        original_code = repo_data["files"].get(file_path, "Code not available")
        if not isinstance(original_code, str):
            original_code = str(original_code)
        original_code = original_code[:3000]

        logger.info("Generating fix for %s (%s)", file_path or "unknown file", severity)

        messages = [
            {
                "role": "system",
                "content": """You are an expert code fixer. Given a bug report and original code, generate a fixed version.

Return STRICT JSON:
{
    "file": "path/to/file",
    "original_issue": "description of the bug",
    "fixed_code": "the corrected code snippet",
    "explanation": "why this fix works"
}"""
            },
            {
                "role": "user",
                "content": f"""Bug: {description}
File: {file_path}
Severity: {severity}

Original Code:
```{original_code}```

Generate the fix."""
            }
        ]

        try:
            # Updated AI call for Groq
            response = get_groq_response(json.dumps(messages), model="llama3-8b-8192")
            if not isinstance(response, str):
                raise ValueError("AI response was not a string")

            fix_data = json.loads(response)
            normalized_fix = _normalize_fix_data(fix_data, file_path, bug, "AI returned an invalid payload")
            fixes.append(normalized_fix)
            logger.info("Successfully generated fix for %s", file_path or "unknown file")
        except json.JSONDecodeError as exc:
            logger.exception("Could not parse AI response as JSON for %s: %s", file_path or "unknown file", exc)
            fixes.append(_build_fallback_fix(file_path, bug, "AI returned invalid JSON"))
        except Exception as exc:
            logger.exception("Could not generate fix for %s: %s", file_path or "unknown file", exc)
            fixes.append(_build_fallback_fix(file_path, bug, f"AI failure: {exc}"))

    return {
        "total_bugs": len(bugs),
        "fixes_generated": len(fixes),
        "fixes": fixes,
    }