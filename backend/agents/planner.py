import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenRouter uses OpenAI library
# This makes it Codex compatible!
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def plan_tasks(repo_data: dict):
    print("🧠 Planner Agent: Creating plan...")
    
    files = list(repo_data["files"].keys())
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        messages=[
            {
                "role": "system",
                "content": """You are an autonomous Codex-style 
                code review agent with agentic reasoning.
                
                Follow this exact process:
                STEP 1: Analyze repository structure
                STEP 2: Identify project type and complexity
                STEP 3: Plan systematic review approach
                STEP 4: List expected issues to find
                STEP 5: Self-review your plan
                
                Return ONLY valid JSON:
                {
                    "project_type": "string",
                    "complexity": "low/medium/high",
                    "main_files": ["file1", "file2"],
                    "expected_issues": ["issue1", "issue2"],
                    "plan_steps": ["step1", "step2"],
                    "confidence_score": 85
                }"""
            },
            {
                "role": "user",
                "content": f"""Repository: {repo_data['owner']}/{repo_data['repo']}
                Total Files: {repo_data['total_files']}
                File List: {files}
                
                Execute agentic review planning now."""
            }
        ]
    )
    
    result_text = response.choices[0].message.content
    
    try:
        # Clean response if needed
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
            
        result = json.loads(result_text)
    except:
        result = {"raw_plan": result_text}
    
    print("✅ Planner Agent: Plan created!")
    
    return {
        "agent": "Planner",
        "status": "completed",
        "result": result
    }
