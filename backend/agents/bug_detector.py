import json
from utils.ai_client import ai

def detect_bugs(repo_data):
    """
    Agent: Analyzes code for bugs, security issues, and performance problems
    """
    
    # Get sample files (first 5)
    sample_files = list(repo_data["files"].items())[:5]
    
    # Build context
    context = ""
    for path, content in sample_files:
        context += f"\n\nFILE: {path}\n```{content[:2000]}```"
    
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
    
    response = ai.ask(messages, response_format={"type": "json_object"})
    return json.loads(response)
