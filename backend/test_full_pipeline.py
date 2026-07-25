from utils.github_fetcher import get_repo_content
from agents.bug_detector import detect_bugs
from agents.fix_generator import generate_fixes
from agents.self_reviewer import review_fixes

print("=" * 70)
print("🤖 AUTOSHIP AGENT: FULL 3-AGENT PIPELINE")
print("Detect → Fix → Review (Self-Correction Loop)")
print("=" * 70)

print("\n1️⃣ FETCHING REPO...")
repo = get_repo_content("https://github.com/tiangolo/fastapi")
print(f"✅ Loaded {repo['total_files']} files")

print("\n2️⃣ BUG DETECTOR AGENT...")
bugs = detect_bugs(repo)
print(f"✅ Score: {bugs['overall_score']}/100")
print(f"   Bugs: {len(bugs['bugs'])} | Security: {len(bugs['security_issues'])} | Performance: {len(bugs['performance_issues'])}")

print("\n3️⃣ FIX GENERATOR AGENT...")
fixes = generate_fixes(bugs, repo)
print(f"✅ Generated {fixes['fixes_generated']} fixes")

print("\n4️⃣ SELF-REVIEWER AGENT...")
review = review_fixes(bugs, fixes, repo)
print(f"✅ Review Score: {review['review_score']}/100")
print(f"   Confidence: {review['confidence_level']}")
print(f"   Validated: {len(review['fixes_validated'])} fixes")

print("\n" + "=" * 70)
print("📊 FINAL REPORT")
print("=" * 70)
print(f"Repository: {repo['owner']}/{repo['repo']}")
print(f"Code Quality Score: {bugs['overall_score']}/100")
print(f"Fixes Generated: {fixes['fixes_generated']}")
print(f"Review Confidence: {review['confidence_level']}")
print(f"Overall Status: {'✅ APPROVED' if review['review_score'] > 70 else '⚠️ NEEDS WORK'}")

print("\n✅ FULL AGENTIC PIPELINE COMPLETE!")
print("Next: API Endpoint Integration")
