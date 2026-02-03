import os

import requests
from github import Auth, Github

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PR_NUMBER = int(os.environ["PR_NUMBER"])
REPO_NAME = os.environ["REPO"]

# Get changed files in PR
g = Github(auth=Auth.Token(GITHUB_TOKEN))
repo = g.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUMBER)
files = pr.get_files()

# Read code changes
code_snippets = ""
for file in files:
    if file.filename.endswith(".py"):
        patch = file.patch or ""
        code_snippets += f"\nFile: {file.filename}\n{patch}\n"

if not code_snippets:
    print("No Python code changes detected.")
    exit(0)

# Prepare prompt for AI
prompt = f"""
You are a senior Python developer.
Review the following Flask code changes for:

- Bugs
- Best practices
- Security issues
- Readability improvements

Provide comments in bullet points and suggest improvements where necessary.

Code changes:
{code_snippets}
"""

# Call OpenAI API
response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
    },
)

print("Ai-response ==>", response.json())
review_text = response.json()["choices"][0]["message"]["content"]

# Post review comments on GitHub PR
pr.create_issue_comment(f"### 🤖 AI Code Review\n{review_text}")
print("AI review posted successfully!")
