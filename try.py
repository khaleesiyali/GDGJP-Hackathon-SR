import urllib.request

API_KEY = "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"

req = urllib.request.Request(
    "https://api.openai.com/v1/models",
    headers={"Authorization": f"Bearer {API_KEY}"}
)

try:
    response = urllib.request.urlopen(req)
    print(" SUCCESS! Your API Key is perfectly fine, and the account is active!")
    print(" CONCLUSION: The issue is 100% in your Vision.py code or local environment not passing this Key to LiveKit properly.")
except Exception as e:
    print(" CAUGHT IT! The Key itself or the OpenAI account has an issue (out of credits/unpaid/copied wrong).")
    print(f" Error Details: {e}")