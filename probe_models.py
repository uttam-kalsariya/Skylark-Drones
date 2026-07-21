import requests

key = "AIzaSyDxdXTk2I7BYOcNhazSrPclJfb6OgpeZrg"
models = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
]

payload = {"contents": [{"role": "user", "parts": [{"text": "Say OK"}]}]}
headers = {"Content-Type": "application/json"}

for model in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        if r.status_code == 200:
            parts = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
            text = parts[0].get("text", "")[:40] if parts else "no parts"
            print(f"[OK]  {model}: {text!r}")
        else:
            err = r.json().get("error", {}).get("message", "")[:100]
            print(f"[{r.status_code}] {model}: {err}")
    except Exception as e:
        print(f"[ERR] {model}: {e}")
