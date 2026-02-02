import os
import sys
import requests
from github import Github, Auth
from github.GithubException import GithubException

def extract_changed_lines(patch: str) -> str:
    """
    Extract only added (+) and removed (-) lines from a unified diff.
    """
    lines = []
    for line in patch.splitlines():
        if line.startswith(("+++", "---", "@@")):
            continue
        if line.startswith("+") or line.startswith("-"):
            lines.append(line)
    return "\n".join(lines)

def main():
    try:
        # ========== 1. ENV CONFIG ==========
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
        GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
        PR_NUMBER = os.environ.get("PR_NUMBER")
        REPO = os.environ.get("REPO")

        if not all([GEMINI_API_KEY, GITHUB_TOKEN, PR_NUMBER, REPO]):
            missing = [k for k, v in {"GEMINI_API_KEY": GEMINI_API_KEY, "GITHUB_TOKEN": GITHUB_TOKEN, 
                                      "PR_NUMBER": PR_NUMBER, "REPO": REPO}.items() if not v]
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

        # ========== 2. GITHUB SETUP ==========
        auth = Auth.Token(GITHUB_TOKEN)
        gh = Github(auth=auth)
        repo = gh.get_repo(REPO)
        pr = repo.get_pull(int(PR_NUMBER))

        # ========== 3. COLLECT DIFFS ==========
        diffs = ""
        total_changed_lines = 0

        for file in pr.get_files():
            if not file.filename.endswith(".py") or not file.patch:
                continue

            # Context Check: If the file change is small, send the full patch.
            # Large files get trimmed to save tokens and prevent timeouts.
            patch_lines = file.patch.splitlines()
            if len(patch_lines) < 20:
                content_to_review = file.patch
            else:
                content_to_review = extract_changed_lines(file.patch)

            diffs += f"\n--- File: {file.filename} ---\n{content_to_review}\n"
            total_changed_lines += len(patch_lines)

        if not diffs:
            print("No Python changes found.")
            return

        # ========== 4. GEMINI API (2026 STABLE) ==========
        # gemini-1.5-flash is retired. gemini-3-flash-preview is the 2026 standard.
        MODEL_NAME = "gemini-3-flash-preview"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY,
        }

        prompt = f"""You are a Senior Python/Flask Developer. 
Review the following code changes for bugs, security vulnerabilities (like SQL injection or hardcoded secrets), and Flask best practices.

Review only the provided diffs. Be concise.

Code Diffs:
{diffs}
"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048,
                # 'minimal' thinking ensures fast response and prevents timeouts
                "thinking_config": { "thinking_level": "minimal" } 
            },
        }

        # Use a longer timeout for AI generation (10s connect, 120s read)
        response = requests.post(url, headers=headers, json=payload, timeout=(10, 120))
        response.raise_for_status()
        
        result = response.json()

        # Safer parsing for 2026 API structure
        try:
            review_text = result['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            reason = result.get("candidates", [{}])[0].get("finishReason", "UNKNOWN")
            raise RuntimeError(f"API Error: Model did not return text. Reason: {reason}")

        # ========== 5. POST COMMENT ==========
        comment_body = f"## 🤖 Gemini 3 AI Review\n\n{review_text}"
        pr.create_issue_comment(comment_body)

        print(f"✅ Review posted successfully using {MODEL_NAME}")

    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()