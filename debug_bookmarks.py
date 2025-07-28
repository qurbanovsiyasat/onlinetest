#!/usr/bin/env python3
"""
Debug the Get Bookmarks issue
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Register a user
timestamp = int(time.time())
user_data = {
    "email": f"debuguser_{timestamp}@test.com",
    "name": "Debug User",
    "password": "testpass123"
}

print("1. Registering user...")
response = requests.post(f"{API_BASE}/auth/register", json=user_data, timeout=10)
print(f"Register status: {response.status_code}")

# Login user
print("2. Logging in user...")
login_response = requests.post(f"{API_BASE}/auth/login", json={
    "email": user_data["email"],
    "password": user_data["password"]
}, timeout=10)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✅ Got token: {token[:50]}...")
    
    # Test bookmarks endpoint
    print("3. Testing bookmarks endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        bookmarks_response = requests.get(f"{API_BASE}/bookmarks", headers=headers, timeout=10)
        print(f"Status: {bookmarks_response.status_code}")
        print(f"Response: {bookmarks_response.text}")
        
        if bookmarks_response.status_code == 200:
            data = bookmarks_response.json()
            print(f"Bookmarks data: {data}")
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
else:
    print(f"❌ Login failed: {login_response.text}")