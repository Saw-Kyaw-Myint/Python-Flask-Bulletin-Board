import asyncio
import os
import sys

import httpx
from github import Auth, Github
from github.GithubException import GithubException


def extract_changed_lines(patch: str) -> str:
    lines = []
    for line in patch.splitlines():
        if line.startswith(("+++", "---", "@@")):
            continue
        if line.startswith("+"):
            lines.append(line)
    return "\n".join(lines)


async def review_with_gemini(api_key: str, filename: str, diffs: str) -> str:
    """
    Call Gemini API asynchronously for a single file review
    """
    MODEL_NAME = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    prompt = f"""
You are a Senior Python/Flask Developer.

Review the following code changes **ONLY for this file**:
File: {filename}

Rules:
- Use GitHub diff-style Markdown
- Show removed lines with '-'
- Show added lines with '+'
- Add short inline comments only if needed
- Focus on bugs, security issues, and bad practices
- Do NOT explain unchanged code

Code Diffs:
{diffs}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2048,
        },
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]


async def process_file(file, gemini_key: str, pr) -> None:
    if not file.filename.endswith(".py") or not file.patch:
        return

    patch_lines = file.patch.splitlines()
    content_to_review = (
        file.patch if len(patch_lines) < 20 else extract_changed_lines(file.patch)
    )

    if not content_to_review.strip():
        print(f"ℹ️ Skipping {file.filename} (no changes)")
        return

    print(f"⏳ Waiting for AI review of {file.filename}...")
    try:
        review_text = await review_with_gemini(
            gemini_key, file.filename, content_to_review
        )
        comment_body = f"""
                        ## 🤖 Gemini AI Review – `{file.filename}`

                        ```diff
                        {review_text}
                        """
        pr.create_issue_comment(comment_body)
        print(f"✅ Comment posted for {file.filename}")
    except Exception as e:
        print(f"❌ Error reviewing {file.filename}: {e}")


async def main_async():
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    PR_NUMBER = os.environ.get("PR_NUMBER")
    REPO = os.environ.get("REPO")
    if not all([GEMINI_API_KEY, GITHUB_TOKEN, PR_NUMBER, REPO]):
        raise ValueError("Missing required environment variables")

    auth = Auth.Token(GITHUB_TOKEN)
    gh = Github(auth=auth)
    repo = gh.get_repo(REPO)
    pr = repo.get_pull(int(PR_NUMBER))

    tasks = [process_file(file, GEMINI_API_KEY, pr) for file in pr.get_files()]
    await asyncio.gather(*tasks)


if __name__ == "main":
    try:
        asyncio.run(main_async())
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
