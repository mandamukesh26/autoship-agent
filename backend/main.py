import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.github_fetcher import get_repo_content
from agents.bug_detector import detect_bugs
from agents.fix_generator import generate_fixes
from agents.self_reviewer import review_fixes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

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

def _normalize_agent_result(result, default=None):
    if isinstance(result, dict):
        return result
    if default is None:
        return {}
    return default


def _build_fallback_response(reason, repo_url):
    return {
        "status": "fallback",
        "repository": repo_url,
        "analysis": {
            "code_quality_score": 0,
            "bugs_found": 0,
            "security_issues": 0,
            "performance_issues": 0,
            "fixes_generated": 0,
            "review_score": 0,
            "confidence": "low",
            "approved": False,
            "error": reason,
        },
        "details": {
            "bugs": {},
            "fixes": {"total_bugs": 0, "fixes_generated": 0, "fixes": []},
            "review": {
                "review_score": 0,
                "fixes_validated": [],
                "overall_assessment": "Review failed",
                "confidence_level": "low",
                "recommendations": ["Manual review required"],
            },
        },
    }


@app.post("/analyze")
def analyze_repo(request: AnalyzeRequest):
    """
    Full agentic pipeline: Detect → Fix → Review
    """
    repo_url = (request.repo_url or "").strip()
    if not repo_url:
        logger.error("Analyze request rejected: empty repo_url")
        raise HTTPException(status_code=400, detail="repo_url is required")

    if not repo_url.startswith(("http://", "https://")):
        logger.error("Analyze request rejected: invalid repo_url %s", repo_url)
        raise HTTPException(status_code=400, detail="repo_url must start with http:// or https://")

    try:
        logger.info("Starting analysis for %s", repo_url)

        # Step 1: Fetch
        repo = get_repo_content(repo_url)
        if not isinstance(repo, dict):
            raise ValueError("Repository fetch returned an invalid payload")

        logger.info("Repository fetched successfully for %s", repo_url)

        # Step 2: Detect
        bugs = _normalize_agent_result(detect_bugs(repo), {
            "bugs": [],
            "security_issues": [],
            "performance_issues": [],
            "overall_score": 0,
            "summary": "Bug detection failed",
        })
        logger.info("Bug detection completed for %s", repo_url)

        # Step 3: Fix
        fixes = _normalize_agent_result(generate_fixes(bugs, repo), {
            "total_bugs": 0,
            "fixes_generated": 0,
            "fixes": [],
        })
        logger.info("Fix generation completed for %s", repo_url)

        # Step 4: Review
        review = _normalize_agent_result(review_fixes(bugs, fixes, repo), {
            "review_score": 0,
            "fixes_validated": [],
            "overall_assessment": "Review failed",
            "confidence_level": "low",
            "recommendations": ["Manual review required"],
        })
        logger.info("Self-review completed for %s", repo_url)

        repository_name = repo.get("owner", "unknown") + "/" + repo.get("repo", "unknown") if isinstance(repo, dict) else repo_url

        return {
            "status": "success",
            "repository": repository_name,
            "analysis": {
                "code_quality_score": bugs.get("overall_score", 0),
                "bugs_found": len(bugs.get("bugs", []) or []),
                "security_issues": len(bugs.get("security_issues", []) or []),
                "performance_issues": len(bugs.get("performance_issues", []) or []),
                "fixes_generated": fixes.get("fixes_generated", 0),
                "review_score": review.get("review_score", 0),
                "confidence": review.get("confidence_level", "low"),
                "approved": review.get("review_score", 0) > 70,
            },
            "details": {
                "bugs": bugs,
                "fixes": fixes,
                "review": review,
            },
        }

    except Exception as exc:
        logger.exception("Pipeline failure for %s: %s", repo_url, exc)
        return _build_fallback_response(str(exc), repo_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
