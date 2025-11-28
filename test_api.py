import requests
import json

url = "http://localhost:8000/api/chat"
payload = {
    "message": "What caused the 2024 global tech outage?",
    "conversation_history": []
}

print("Sending request to:", url)
print("Payload:", json.dumps(payload, indent=2))
print("\n" + "="*50)

response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print("\n" + "="*50)

if response.status_code == 200:
    data = response.json()
    print("\nRESPONSE:")
    print(data.get("response", "No response"))
    print("\n" + "="*50)
    print(f"\nSOURCES ({len(data.get('sources', []))}):")
    for i, source in enumerate(data.get("sources", []), 1):
        print(f"{i}. {source.get('title', 'No title')}")
        print(f"   {source.get('url', 'No URL')[:80]}...")
else:
    print("ERROR:", response.text)
