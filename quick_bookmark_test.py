#!/usr/bin/env python3
"""
Quick test for bookmarks endpoint
"""

import requests
import json

BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Get admin token
response = requests.post(f"{API_BASE}/auth/login", json={
    "email": "admin@squiz.com",
    "password": "admin123"
})

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ Got token: {token[:50]}...")
    
    # Test bookmarks endpoint
    headers = {"Authorization": f"Bearer {token}"}
    bookmarks_response = requests.get(f"{API_BASE}/bookmarks", headers=headers, timeout=10)
    
    print(f"Status: {bookmarks_response.status_code}")
    print(f"Response: {bookmarks_response.text}")
    
else:
    print(f"❌ Login failed: {response.text}")