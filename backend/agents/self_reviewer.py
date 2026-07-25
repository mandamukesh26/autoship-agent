import json
from utils.ai_client import ai

def review_fixes(bugs_found, fixes_generated, repo_data):
    """
    Agent: Reviews the quality of generated fixes and validates they solve the problems
    """
    
    # Prepare context
    bug_list = json.dumps(bugs_found.get("bugs", [])[:3], indent=2)
    fix_list = json.dumps(fixes_generated.get("fixes", [])[:3], indent=2)
    
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
        print("🧐 Self-Reviewing fixes...")
        response = ai.ask(messages, response_format={"type": "json_object"})
        return json.loads(response)
    except Exception as e:
        print(f"⚠️  Self-review failed: {e}")
        return {
            "review_score": 0,
            "fixes_validated": [],
            "overall_assessment": "Review failed",
            "confidence_level": "low",
            "recommendations": ["Manual review required"]
        }
