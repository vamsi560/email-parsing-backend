import requests
import json

# Test the API endpoints
base_url = "http://127.0.0.1:8000"

print("Testing API endpoints...")

# Test 1: Health check
try:
    response = requests.get(f"{base_url}/health")
    print(f"Health check: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"Health check failed: {e}")

# Test 2: List endpoints
try:
    response = requests.get(f"{base_url}/")
    print(f"Root endpoint: {response.status_code}")
except Exception as e:
    print(f"Root endpoint failed: {e}")

# Test 3: OpenAPI docs
try:
    response = requests.get(f"{base_url}/docs")
    print(f"Docs endpoint: {response.status_code}")
except Exception as e:
    print(f"Docs endpoint failed: {e}")

# Test 4: List drafts
try:
    response = requests.get(f"{base_url}/api/submissions/draft")
    print(f"List drafts: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"List drafts failed: {e}")

print("\nAvailable endpoints should be:")
print("- GET /health")
print("- POST /api/email/intake")
print("- GET /api/submissions/draft/{id}")
print("- POST /api/submissions/confirm/{id}")
print("- GET /api/submissions/draft")
print("- GET /api/submissions")
print("- GET /api/work-items")