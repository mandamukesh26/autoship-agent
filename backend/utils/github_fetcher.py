import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_repo_content(repo_url: str):
    try:
        # Parse URL
        repo_url = repo_url.replace("https://github.com/", "").strip()
        parts = repo_url.split("/")
        if len(parts) < 2:
            return {"error": "Invalid GitHub URL", "files": {}}
        
        owner, repo = parts[0], parts[1]
        print(f"Fetching: {owner}/{repo}")
        
        # Setup headers
        headers = {}
        if GITHUB_TOKEN and len(GITHUB_TOKEN) > 20 and "your" not in GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
            print("✓ Using GitHub token")
        else:
            print("⚠ No valid token, using public access (rate limited)")
        
        # Try to get file tree
        for branch in ["main", "master"]:
            tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            r = requests.get(tree_url, headers=headers)
            print(f"Branch '{branch}': Status {r.status_code}")
            if r.status_code == 200:
                break
        
        if r.status_code != 200:
            error_msg = f"GitHub API error: {r.status_code}"
            if r.status_code == 404:
                error_msg = "Repository not found (check if it's public)"
            elif r.status_code == 403:
                error_msg = "API rate limit exceeded or authentication required"
            print(f"✗ {error_msg}")
            return {"error": error_msg, "files": {}}
        
        tree_data = r.json()
        all_items = tree_data.get("tree", [])
        print(f"Found {len(all_items)} total items in tree")
        
        # Filter for code files
        code_extensions = (".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".php")
        files = {}
        count = 0
        
        for item in all_items:
            if count >= 15:  # Limit to 15 files
                break
            if item["type"] == "blob" and item["path"].endswith(code_extensions):
                try:
                    content_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{item['path']}"
                    c = requests.get(content_url, headers=headers)
                    if c.status_code == 200:
                        data = c.json()
                        if "content" in data:
                            content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                            if len(content) > 0:
                                files[item["path"]] = content
                                count += 1
                                print(f"✓ Read: {item['path']}")
                except Exception as e:
                    print(f"✗ Error reading {item['path']}: {str(e)}")
        
        print(f"Successfully loaded {len(files)} code files")
        
        if len(files) == 0:
            return {"error": "No code files found (repo might be empty or contain no supported file types)", "files": {}}
        
        return {
            "owner": owner,
            "repo": repo,
            "files": files,
            "total_files": len(files)
        }
        
    except Exception as e:
        print(f"Critical error: {str(e)}")
        return {"error": str(e), "files": {}}
