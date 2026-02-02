import os
import sys
import requests
import json
from github import Github, Auth

def get_github_context():
    """GitHub context ရယူခြင်း"""
    # GitHub Actions ကနေ environment variables ယူခြင်း
    github_token = os.environ.get("GITHUB_TOKEN")
    
    if not github_token:
        print("❌ Error: GITHUB_TOKEN not found in environment")
        sys.exit(1)
    
    # GitHub event data ကိုဖတ်ခြင်း
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path and os.path.exists(event_path):
        try:
            with open(event_path, 'r') as f:
                event_data = json.load(f)
            
            repo_name = event_data.get("repository", {}).get("full_name")
            pr_number = event_data.get("pull_request", {}).get("number")
            
            return github_token, repo_name, pr_number
        except Exception as e:
            print(f"⚠️ Warning: Could not read event data: {e}")
    
    # Fallback: environment variables ကနေယူခြင်း
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    pr_number = os.environ.get("PR_NUMBER") or os.environ.get("GITHUB_EVENT_NUMBER")
    
    return github_token, repo_name, pr_number

def validate_inputs(github_token, repo_name, pr_number):
    """Input validation"""
    errors = []
    
    if not github_token:
        errors.append("GITHUB_TOKEN is required")
    
    if not repo_name:
        errors.append("Repository name is required")
    
    if not pr_number:
        errors.append("PR number is required")
    else:
        try:
            pr_number = int(pr_number)
        except ValueError:
            errors.append(f"PR number must be integer, got: {pr_number}")
    
    return errors

def main():
    print("🚀 Starting DeepSeek AI Code Review...")
    
    # 1. Get GitHub context
    github_token, repo_name, pr_number = get_github_context()
    
    # 2. Validate inputs
    errors = validate_inputs(github_token, repo_name, pr_number)
    if errors:
        for error in errors:
            print(f"❌ {error}")
        sys.exit(1)
    
    pr_number = int(pr_number)
    print(f"📝 Repository: {repo_name}")
    print(f"🔢 PR Number: {pr_number}")
    
    # 3. Get DeepSeek API Key
    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        print("❌ Error: DEEPSEEK_API_KEY not found in environment")
        sys.exit(1)
    
    # 4. Initialize GitHub client
    try:
        g = Github(auth=Auth.Token(github_token))
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        print("✅ GitHub client initialized successfully")
    except Exception as e:
        print(f"❌ GitHub API error: {e}")
        sys.exit(1)
    
    # 5. Collect Python diffs
    print("📂 Collecting file changes...")
    code_snippets = []
    python_files = []
    
    try:
        for f in pr.get_files():
            if f.filename.endswith(".py"):
                python_files.append(f.filename)
                if f.patch:
                    code_snippets.append(f"File: {f.filename}\n{f.patch}\n")
                else:
                    code_snippets.append(f"File: {f.filename}\n(New file or binary changes)\n")
    except Exception as e:
        print(f"⚠️ Warning: Could not get all files: {e}")
    
    if not python_files:
        print("📭 No Python files changed")
        try:
            comment = pr.create_issue_comment(
                "### 🤖 DeepSeek AI Review\n\nNo Python changes detected in this PR."
            )
            print("✅ Posted comment about no Python changes")
        except Exception as e:
            print(f"❌ Failed to post comment: {e}")
        sys.exit(0)
    
    print(f"🐍 Found {len(python_files)} Python file(s): {', '.join(python_files)}")
    
    # Combine diffs (limit size to avoid API limits)
    combined_diff = "\n".join(code_snippets)
    if len(combined_diff) > 8000:
        combined_diff = combined_diff[:8000] + "\n...(truncated due to length)"
    
    # 6. Create prompt for DeepSeek
    prompt = f"""
မင်္ဂလာပါ! ကျေးဇူးပြု၍ ဒီ Python Flask pull request changes တွေကို ပြန်လှန်သုံးသပ်ပေးပါ။

**ရှုထောင့်များ:**
1. ဘယ်လိုမှားနေမှုတွေရှိလဲ (Bugs/Errors)
2. လုံခြုံရေး ပြဿနာများ (Security issues)
3. Flask best practices နဲ့ ကိုက်ညီမှု
4. ကုဒ်အရည်အသွေး (Code quality)
5. Performance ဆိုင်ရာအကြံပြုချက်များ

**ကျေးဇူးပြု၍ မြန်မာလိုဖြေပေးပါ။** စာပိုဒ်တိုတိုနဲ့ ရှင်းလင်းတဲ့ပုံစံဖြစ်ပါစေ။

**Code changes:**
{combined_diff}
"""
    
    print("🤖 Calling DeepSeek API...")
    
    # 7. Call DeepSeek API
    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",  # ✅ Correct endpoint
            headers={
                "Authorization": f"Bearer {deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",  # or "deepseek-coder" for coding tasks
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1500,  # ✅ Increase token limit
            },
            timeout=45,
        )
        
        response.raise_for_status()
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            review_text = data["choices"][0]["message"]["content"].strip()
            print("✅ DeepSeek API response received")
        else:
            review_text = "🤖 DeepSeek review skipped (API response format error)"
            print(f"⚠️ Unexpected API response: {data}")
            
    except requests.exceptions.Timeout:
        review_text = "🤖 DeepSeek review timed out (API took too long to respond)"
        print("❌ API timeout")
    except requests.exceptions.RequestException as e:
        review_text = f"🤖 DeepSeek review failed: API error ({str(e)})"
        print(f"❌ API request error: {e}")
    except Exception as e:
        review_text = f"🤖 DeepSeek review error: {str(e)}"
        print(f"❌ Unexpected error: {e}")
    
    # 8. Format the review comment
    comment_body = f"""### 🤖 DeepSeek AI Code Review

**Reviewed {len(python_files)} Python file(s):** `{', '.join(python_files)}`

---

{review_text}

---

*Review generated by DeepSeek AI • [Feedback?](https://github.com/your-repo/issues)*"""
    
    # 9. Post PR comment
    print("💬 Posting review comment...")
    try:
        # Try using issue comment endpoint (more reliable)
        issue = repo.get_issue(pr_number)
        comment = issue.create_comment(comment_body)
        print(f"✅ Review posted successfully! Comment URL: {comment.html_url}")
    except Exception as e:
        print(f"❌ Failed to post comment via GitHub API: {e}")
        
        # Fallback: Try direct REST API
        try:
            comment_url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            data = {"body": comment_body}
            
            fallback_response = requests.post(comment_url, headers=headers, json=data)
            if fallback_response.status_code == 201:
                print("✅ Comment posted via REST API fallback")
            else:
                print(f"❌ Fallback also failed: {fallback_response.status_code}")
                print(f"Response: {fallback_response.text}")
        except Exception as fallback_error:
            print(f"❌ All posting methods failed: {fallback_error}")
    
    print("🎉 DeepSeek PR review process completed!")

if __name__ == "__main__":
    main()