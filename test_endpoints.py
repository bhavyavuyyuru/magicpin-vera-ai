import requests
import json

# Test health endpoint
print("Testing health endpoint...")
response = requests.get("https://bhavyavuyyuru-magicpin-vera-ai.onrender.com/v1/healthz")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test metadata endpoint
print("Testing metadata endpoint...")
response = requests.get("https://bhavyavuyyuru-magicpin-vera-ai.onrender.com/v1/metadata")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test context endpoint
print("Testing context endpoint...")
data = {
    "scope": "category",
    "context_id": "dentists",
    "version": 1,
    "delivered_at": "2026-05-02T09:00:00Z",
    "payload": {
        "slug": "dentists",
        "display_name": "Dentists"
    }
}
response = requests.post("https://bhavyavuyyuru-magicpin-vera-ai.onrender.com/v1/context", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

# Test reply endpoint
print("Testing reply endpoint...")
data = {
    "conversation_id": "test_conv",
    "message": "Hello bot"
}
response = requests.post("https://bhavyavuyyuru-magicpin-vera-ai.onrender.com/v1/reply", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test tick endpoint (might fail if no contexts loaded)
print("Testing tick endpoint...")
data = {
    "now": "2026-05-02T10:00:00Z",
    "available_triggers": ["trg_013_corporate_thali_planning"]
}
response = requests.post("https://bhavyavuyyuru-magicpin-vera-ai.onrender.com/v1/tick", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")