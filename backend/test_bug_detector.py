from utils.github_fetcher import get_repo_content
from agents.bug_detector import detect_bugs

print("1️⃣ Fetching repo...")
repo = get_repo_content("https://github.com/tiangolo/fastapi")

print("2️⃣ Running Bug Detector Agent...")
result = detect_bugs(repo)

print("\n✅ BUG DETECTOR RESULTS:")
print(f"Overall Score: {result['overall_score']}/100")
print(f"Bugs Found: {len(result['bugs'])}")
print(f"Security Issues: {len(result['security_issues'])}")
print(f"Performance Issues: {len(result['performance_issues'])}")
print(f"\nSummary: {result['summary']}")
