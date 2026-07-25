from utils.github_fetcher import get_repo_content
from agents.bug_detector import detect_bugs
from agents.fix_generator import generate_fixes

print("=" * 60)
print("🚀 AUTOSHIP AGENT: BUG DETECT → FIX GENERATE PIPELINE")
print("=" * 60)

print("\n1️⃣ Fetching repository...")
repo = get_repo_content("https://github.com/tiangolo/fastapi")
print(f"✅ Loaded {repo['total_files']} files")

print("\n2️⃣ Running Bug Detector...")
bugs = detect_bugs(repo)
print(f"✅ Found {bugs['overall_score']}/100 score")
print(f"   - Bugs: {len(bugs['bugs'])}")
print(f"   - Security: {len(bugs['security_issues'])}")
print(f"   - Performance: {len(bugs['performance_issues'])}")

print("\n3️⃣ Generating Fixes...")
fixes = generate_fixes(bugs, repo)
print(f"✅ Generated {fixes['fixes_generated']} fixes")

print("\n" + "=" * 60)
print("🔧 SAMPLE FIX:")
print("=" * 60)
if fixes['fixes']:
    sample = fixes['fixes'][0]
    print(f"File: {sample['file']}")
    print(f"Issue: {sample['original_issue'][:100]}...")
    print(f"Fix Preview: {sample['fixed_code'][:200]}...")

print("\n✅ PIPELINE COMPLETE!")
print("Next: Self-Reviewer Agent")
