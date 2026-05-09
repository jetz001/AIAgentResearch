import requests
import json
import sys

print("Connecting to Ollama...")
url = "http://localhost:11434/api/generate"
payload = {
    "model": "gemma2:2b",
    "prompt": "Hi",
    "stream": False
}
try:
    print("Sending request...")
    response = requests.post(url, json=payload, timeout=120)
    print("Response received!")
    print(response.json().get("response"))
except Exception as e:
    print(f"Error: {e}")
