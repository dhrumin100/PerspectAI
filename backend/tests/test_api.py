import requests
import json

def test_api():
    url = "http://localhost:8000/api/chat"
    payload = {"query": "Is the earth flat?"}
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Error:", response.text)
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_api()
