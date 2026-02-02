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
        MODEL_NAME = "gemini-3-flash-preview"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"
        
        # In 2026, it is safer to pass the API key in the headers
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,  # Lower temperature is better for code reviews
                "topP": 0.95,
                "maxOutputTokens": 4096, # Increased for larger PR diffs
            }
        }

        # Adding a longer timeout (60s) because Gemini 3 handles much larger context
        response = requests.post(url, headers=headers, json=payload, timeout=60)
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