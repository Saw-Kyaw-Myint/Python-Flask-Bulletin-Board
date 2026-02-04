import os
import re
import sys
from typing import Dict, List

import requests
from github import Auth, Github
from github.GithubException import GithubException


def extract_changed_lines_with_numbers(patch: str) -> List[Dict]:
    """
    Extract added lines (+) with their NEW file line numbers.
    """
    results = []

    new_line_no = None

    for line in patch.splitlines():
        # HUNK HEADER: @@ -a,b +c,d @@
        hunk = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", line)
        if hunk:
            new_line_no = int(hunk.group(1))
            continue

        if line.startswith("+") and not line.startswith("+++"):
            results.append({"line": new_line_no, "code": line[1:]})
            new_line_no += 1

        elif line.startswith("-") and not line.startswith("---"):
            # removed line → does NOT increase new_line_no
            continue

        else:
            # context line
            if new_line_no is not None:
                new_line_no += 1

    return results


def is_reviewable(file, source_dir, allowed_extensions):
    if not file.patch:
        return False

    if source_dir and not file.filename.startswith(source_dir):
        return False

    return file.filename.endswith(allowed_extensions)


def main():
    try:
        # ========== 1. ENV CONFIG ==========
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
        GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
        PR_NUMBER = os.environ.get("PR_NUMBER")
        REPO = os.environ.get("REPO")
        AI_REVIEW_SOURCE_DIR = os.environ.get("AI_REVIEW_SOURCE_DIR", "")
        AI_REVIEW_EXTENSIONS = tuple(
            ext.strip()
            for ext in os.environ.get("AI_REVIEW_EXTENSIONS", ".py").split(",")
        )

        if not all([GEMINI_API_KEY, GITHUB_TOKEN, PR_NUMBER, REPO]):
            missing = [
                k
                for k, v in {
                    "GEMINI_API_KEY": GEMINI_API_KEY,
                    "GITHUB_TOKEN": GITHUB_TOKEN,
                    "PR_NUMBER": PR_NUMBER,
                    "REPO": REPO,
                }.items()
                if not v
            ]
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

        # ========== 2. GITHUB SETUP ==========
        auth = Auth.Token(GITHUB_TOKEN)
        gh = Github(auth=auth)
        repo = gh.get_repo(REPO)
        pr = repo.get_pull(int(PR_NUMBER))

        # ========== 3. COLLECT DIFFS ==========
        diffs = ""

        for file in pr.get_files():
            if not is_reviewable(file, AI_REVIEW_SOURCE_DIR, AI_REVIEW_EXTENSIONS):
                continue

            changed_lines = extract_changed_lines_with_numbers(file.patch)

            if not changed_lines:
                continue

            diffs += f"\n{file.filename}\n"
            diffs += "```diff\n"

            for item in changed_lines:
                diffs += f"+ L{item['line']}: {item['code']}\n"

            diffs += "```\n"

        if not diffs:
            print("No Python changes found.")
            return

        # ========== 4. GEMINI API (2026 STABLE) ==========
        MODEL_NAME = "gemini-2.5-flash-lite"
        URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY,
        }

        # Markdown diff style prompt
        prompt = f"""
You are a STRICT Senior Python/Flask Code Reviewer.

MANDATORY RULES (DO NOT VIOLATE):
- DO NOT include diff metadata such as --- , +++ , @@
- DO NOT praise, compliment, or mention good practices
- DO NOT describe what the code does
- ONLY point out bugs, security issues, or concrete improvements
- If there are NO problems, output NOTHING (empty response)
- Any output not matching the required format is INVALID

OUTPUT FORMAT (STRICT):
- If multiple files are present, repeat the format below per file
- File name must be shown as <a href="#"><b>filename.py</b></a> text with bold font on its own line
- Then show ONE diff block
- Then ONE **bold** explanation (1–4 sentences max)
- Horizontal line (---) under explanation

You MUST follow the output format exactly.
Do NOT add extra text, headings, or explanations outside this structure.
VALID OUTPUT STRUCTURE:
<a href="#"><b><i>filename.py</i></b></a>
```diff
-L23: existing line

+ suggestion line
```
**Short explanation of the problem and fix.**

---



DO NOT add anything else.
INVALID OUTPUT EXAMPLES (NEVER DO THESE):
"This is good practice"
"The code looks fine"
Explanations without a diff
Diff blocks containing --- , +++ , @@
Paragraphs or summaries

CODE CHANGES TO REVIEW:
{diffs}
"""
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            response = requests.post(URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            review_text = result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            print("API Error: Model did not return text. Reason:", reason)
            reason = result.get("candidates", [{}])[0].get("finishReason", "UNKNOWN")
            raise RuntimeError(
                f"API Error: Model did not return text. Reason: {reason}"
            )

        # ========== 5. POST COMMENT IN MARKDOWN DIFF ==========
        comment_body = f"## 🤖 AI PR Overall Review \n\n {review_text}"
        pr.create_issue_comment(comment_body)

        print(f"..Review posted successfully using {MODEL_NAME}..")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        if "response" in locals():
            print(f"Response Body: {response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()
