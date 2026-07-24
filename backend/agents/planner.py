import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def plan_tasks(repo_data: dict):
    files = list(repo_data["files"].keys())
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are an autonomous code review agent
                using Codex-style agentic reasoning.
                
                STEP 1: Analyze repository structure
                STEP 2: Identify project type and complexity
                STEP 3: Plan systematic review approach
                STEP 4: List expected issues to find
                STEP 5: Review your plan for completeness
                
                Return JSON with: project_type, complexity,
                main_files, expected_issues, plan_steps, 
                confidence_score"""
            },
            {
                "role": "user",
                "content": f"""Repository: {repo_data['owner']}/{repo_data['repo']}
                Total Files: {repo_data['total_files']}
                File List: {files}
                
                Execute your agentic review planning now."""
            }
        ],
        response_format={"type": "json_object"}
    )
    
    return {
        "agent": "Planner",
        "status": "completed",
        "result": json.loads(response.choices[0].message.content)
    }
