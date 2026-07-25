from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.github_fetcher import get_repo_content
from agents.bug_detector import detect_bugs
from agents.fix_generator import generate_fixes
from agents.self_reviewer import review_fixes

app = FastAPI(
    title="AutoShip Agent",
    description="AI-powered code review with autonomous bug detection, fixing, and self-review",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    repo_url: str

@app.get("/")
def root():
    return {
        "status": "AutoShip Agent Online",
        "version": "2.0.0",
        "agents": ["bug_detector", "fix_generator", "self_reviewer"],
        "endpoints": ["/analyze", "/health"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "agents_ready": True}

@app.post("/analyze")
def analyze_repo(request: AnalyzeRequest):
    """
    Full agentic pipeline: Detect → Fix → Review
    """
    try:
        print(f"🔍 Analyzing: {request.repo_url}")
        
        # Step 1: Fetch
        repo = get_repo_content(request.repo_url)
        
        # Step 2: Detect
        bugs = detect_bugs(repo)
        
        # Step 3: Fix
        fixes = generate_fixes(bugs, repo)
        
        # Step 4: Review
        review = review_fixes(bugs, fixes, repo)
        
        return {
            "status": "success",
            "repository": f"{repo['owner']}/{repo['repo']}",
            "analysis": {
                "code_quality_score": bugs["overall_score"],
                "bugs_found": len(bugs["bugs"]),
                "security_issues": len(bugs["security_issues"]),
                "performance_issues": len(bugs["performance_issues"]),
                "fixes_generated": fixes["fixes_generated"],
                "review_score": review["review_score"],
                "confidence": review["confidence_level"],
                "approved": review["review_score"] > 70
            },
            "details": {
                "bugs": bugs,
                "fixes": fixes,
                "review": review
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
