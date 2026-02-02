import os
import sys
import requests
from github import Github, GithubException,Auth

def main():
    try:
        # ========== ENV ==========
        # In GitHub Actions, repo is usually 'owner/repo'
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
        GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
        PR_NUMBER = os.environ.get("PR_NUMBER")
        REPO = os.environ.get("REPO")

        if not all([GEMINI_API_KEY, GITHUB_TOKEN, PR_NUMBER, REPO]):
            missing = [k for k, v in {"GEMINI_API_KEY": GEMINI_API_KEY, "GITHUB_TOKEN": GITHUB_TOKEN, 
                                      "PR_NUMBER": PR_NUMBER, "REPO": REPO}.items() if not v]
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

        # ========== GitHub ==========
        auth = Auth.Token(GITHUB_TOKEN)
        gh = Github(auth=auth)
        repo = gh.get_repo(REPO)
        pr = repo.get_pull(int(PR_NUMBER))

        # ========== Collect Diffs ==========
        diffs = ""
        for file in pr.get_files():
            # Include .py files; skip deleted files (no patch)
            if file.filename.endswith(".py") and file.patch:
                diffs += f"\n--- File: {file.filename} ---\n{file.patch}\n"

        if not diffs:
            print("No Python changes to review.")
            return

        # ========== Prompt ==========
        prompt = f"""You are a senior Python Flask developer. Review these PR changes.
Focus on: Bugs, Flask best practices, Security, and Performance.
Return concise bullet points.

PR Diffs:
{diffs}
"""

        # ========== Gemini API (v1beta or v1) ==========
        # Using 1.5-flash: it's optimized for high-volume tasks like this
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2, # Lower temperature for more consistent reviews
                "topP": 0.8,
                "maxOutputTokens": 2048,
            }
        }

        response = requests.post(url, json=payload, timeout=45)
        response.raise_for_status()
        
        result = response.json()

        # Safer parsing: Gemini can return 'finishReason' as SAFETY if it dislikes the code
        try:
            review = result['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            feedback = result.get("candidates", [{}])[0].get("finishReason", "UNKNOWN")
            raise RuntimeError(f"Gemini failed to generate review. Reason: {feedback}")

        # ========== Post PR Comment ==========
        comment_header = "## 🤖 Gemini AI Code Review\n\n"
        pr.create_issue_comment(comment_header + review)

        print("✅ Gemini review posted successfully")

    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()