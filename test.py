import requests
import os

# 1. Configuration
API_KEY = "AIzaSyAukg06C0Cxz2m0HvExLYbKq2eurzyHwig"  # Or use os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-3-flash-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# 2. Test Payload (A simple Python bug for Gemini to find)
sample_code = """
def calculate_total(price, tax):
    return price + tax  # Needs to handle if tax is None!
"""

prompt = f"Review this Python snippet for bugs:\n{sample_code}"

payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY
}

# 3. Execution
print(f"🚀 Testing {MODEL}...")
try:
    response = requests.post(URL, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print("\n✨ Gemini's Review:")
    print(data['candidates'][0]['content']['parts'][0]['text'])

except Exception as e:
    print(f"❌ Failed: {e}")
    if 'response' in locals():
        print(f"Response Body: {response.text}")