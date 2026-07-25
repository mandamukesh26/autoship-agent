import json
from utils.ai_client import ai

def generate_fixes(bugs_found, repo_data):
    """
    Agent: Takes bugs detected and generates specific code fixes
    """
    
    fixes = []
    
    for bug in bugs_found.get("bugs", []):
        # Get the file content if available
        file_path = bug.get("file", "")
        original_code = repo_data["files"].get(file_path, "Code not available")[:3000]
        
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
                "content": f"""Bug: {bug.get('description')}
File: {file_path}
Severity: {bug.get('severity')}

Original Code:
```{original_code}```

Generate the fix."""
            }
        ]
        
        try:
            response = ai.ask(messages, response_format={"type": "json_object"})
            fix_data = json.loads(response)
            fixes.append(fix_data)
            print(f"✅ Generated fix for: {file_path}")
        except Exception as e:
            print(f"⚠️  Could not generate fix for {file_path}: {e}")
            fixes.append({
                "file": file_path,
                "original_issue": bug.get("description"),
                "fixed_code": "Error generating fix",
                "explanation": str(e)
            })
    
    return {
        "total_bugs": len(bugs_found.get("bugs", [])),
        "fixes_generated": len(fixes),
        "fixes": fixes
    }
