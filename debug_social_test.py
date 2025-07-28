#!/usr/bin/env python3
"""
Debug Social Features - Simple Test
"""

import requests
import json

BACKEND_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "admin@squiz.com"
ADMIN_PASSWORD = "admin123"

def make_request(method, endpoint, data=None, token=None):
    url = f"{BACKEND_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.request(method, url, json=data, headers=headers, timeout=10)
        print(f"{method} {endpoint} -> {response.status_code}")
        if response.text:
            print(f"Response: {response.text[:200]}...")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("🔍 Debug Social Features")
    
    # 1. Login as admin
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = make_request("POST", "/auth/login", login_data)
    if response and response.status_code == 200:
        admin_token = response.json()["access_token"]
        print("✅ Admin login successful")
    else:
        print("❌ Admin login failed")
        return
    
    # 2. Create two test users
    user1_data = {"email": "debuguser1@test.com", "name": "Debug User 1", "password": "test123"}
    user2_data = {"email": "debuguser2@test.com", "name": "Debug User 2", "password": "test123"}
    
    # Register users
    make_request("POST", "/auth/register", user1_data)
    make_request("POST", "/auth/register", user2_data)
    
    # Login users
    user1_login = make_request("POST", "/auth/login", {"email": user1_data["email"], "password": user1_data["password"]})
    user2_login = make_request("POST", "/auth/login", {"email": user2_data["email"], "password": user2_data["password"]})
    
    if user1_login and user1_login.status_code == 200:
        user1_token = user1_login.json()["access_token"]
        user1_id = user1_login.json()["user"]["id"]
        print(f"✅ User1 login successful: {user1_id}")
    else:
        print("❌ User1 login failed")
        return
        
    if user2_login and user2_login.status_code == 200:
        user2_token = user2_login.json()["access_token"]
        user2_id = user2_login.json()["user"]["id"]
        print(f"✅ User2 login successful: {user2_id}")
    else:
        print("❌ User2 login failed")
        return
    
    # 3. Test basic endpoints
    print("\n🧪 Testing endpoints...")
    
    # Test privacy settings
    make_request("GET", "/privacy-settings", token=user1_token)
    
    # Test follow
    follow_data = {"user_id": user2_id}
    make_request("POST", "/follow", follow_data, token=user1_token)
    
    # Test profile
    make_request("GET", f"/users/{user2_id}/profile", token=user1_token)
    
    # Test admin social overview
    make_request("GET", "/admin/social-overview", token=admin_token)
    
    # Test admin followers
    make_request("GET", f"/admin/users/{user2_id}/followers", token=admin_token)

if __name__ == "__main__":
    main()