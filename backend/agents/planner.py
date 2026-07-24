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
                "content": "You are a senior software architect. Analyze this repository and return a JSON object with: project_type (string), complexity (low/medium/high), main_files (array of strings), expected_issues (array of strings), and plan_steps (array of strings describing the review process)."
            },
            {
                "role": "user",
                "content": f"Repository: {repo_data['owner']}/{repo_data['repo']}\nTotal Files: {repo_data['total_files']}\nFile List: {files}\n\nCreate a comprehensive review plan."
            }
        ],
        response_format={"type": "json_object"}
    )
    
    return {
        "agent": "Planner",
        "status": "completed",
        "result": json.loads(response.choices[0].message.content)
    }
