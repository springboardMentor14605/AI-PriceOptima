import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}, Body: {response.json()}")

def test_recommendation():
    print("\nTesting /recommend-price...")
    payload = {
        "category": "Electronics",
        "region": "South",
        "inventory_level": 15,
        "price": 450.0
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/recommend-price", data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed! Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    try:
        test_health()
        test_recommendation()
    except Exception as e:
        print(f"Error: {e}")
