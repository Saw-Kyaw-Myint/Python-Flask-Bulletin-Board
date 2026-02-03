import requests
import os

key = key
res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}")
models = [m['name'] for m in res.json().get('models', [])]
print("Available models:", models)