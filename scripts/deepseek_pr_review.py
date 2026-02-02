import os
import requests
from github import Github, Auth

DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PR_NUMBER = int(os.environ["PR_NUMBER"])
REPO_NAME = os.environ["REPO"]

# GitHub client
g = Github(auth=Auth.Token(GITHUB_TOKEN))
repo = g.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUMBER)

# Collect Python diffs
code_snippets = ""
for f in pr.get_files():
    if f.filename.endswith(".py"):
        code_snippets += f"\nFile: {f.filename}\n{f.patch or ''}\n"

if not code_snippets:
    pr.create_issue_comment(
        "### 🤖 DeepSeek AI Review\nNo Python changes detected."
    )
    exit(0)

prompt = f"""
You are a senior Python Flask developer.
Review the following pull request changes and provide:

- Possible bugs
- Security issues
- Flask best practices
- Code readability improvements

Use bullet points.

Code diff:
{code_snippets}
"""

# Call DeepSeek API
response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "deepseek-chat",  # or deepseek-coder
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 300,
    },
    timeout=30,
)

data = response.json()

if "choices" not in data:
    review_text = "🤖 DeepSeek review skipped (API error)"
else:
    review_text = data["choices"][0]["message"]["content"]

# Post PR comment
pr.create_issue_comment(f"### 🤖 DeepSeek AI Code Review\n{review_text}")

print("✅ DeepSeek PR review posted")
