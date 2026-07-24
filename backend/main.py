from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.github_fetcher import get_repo_content
from agents.planner import plan_tasks

app = FastAPI(
    title="AutoShip Agent",
    description="AI Agent that reviews and fixes code",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RepoRequest(BaseModel):
    repo_url: str

@app.get("/")
def root():
    return {
        "status": "AutoShip Agent Running ✅",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy ✅"}

@app.post("/analyze")
async def analyze_repo(request: RepoRequest):
    print(f"\n🚀 Analyzing: {request.repo_url}")
    
    # Step 1: Fetch repo
    repo_data = get_repo_content(request.repo_url)
    
    if "error" in repo_data and repo_data["error"]:
        return {"status": "error", "message": repo_data["error"]}
    
    if repo_data["total_files"] == 0:
        return {"status": "error", "message": "No code files found"}
    
    print(f"📁 Found {repo_data['total_files']} files")
    
    # Step 2: AI Planning
    plan = plan_tasks(repo_data)
    
    print("✅ Analysis complete!\n")
    
    return {
        "status": "success",
        "repo": f"{repo_data['owner']}/{repo_data['repo']}",
        "files_analyzed": repo_data["total_files"],
        "plan": plan
    }
