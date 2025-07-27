#!/usr/bin/env python3
"""
Frontend-Backend Communication Test
Tests if the frontend can communicate with the backend properly
"""

import requests
import json
import sys
import os

def test_frontend_backend_communication():
    """Test frontend-backend communication"""
    print("🔗 Testing Frontend-Backend Communication")
    print("=" * 60)
    
    # Get backend URL from frontend .env
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.split('=')[1].strip()
                    break
            else:
                backend_url = "http://localhost:8001"
    except:
        backend_url = "http://localhost:8001"
    
    api_url = f"{backend_url}/api"
    
    print(f"📍 Frontend .env Backend URL: {backend_url}")
    print(f"📍 API URL: {api_url}")
    print()
    
    # Test 1: Health check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check successful: {data.get('status', 'Unknown')}")
            print(f"   📊 Database: {data.get('database', 'Unknown')}")
            print(f"   🏠 Hosting: {data.get('hosting', 'Unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {str(e)}")
        return False
    
    # Test 2: CORS check
    print("\\n2. Testing CORS Configuration...")
    try:
        response = requests.get(f"{api_url}/cors-info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            origins = data.get('allowed_origins', [])
            localhost_allowed = any('localhost' in origin for origin in origins)
            print(f"   ✅ CORS info retrieved: {len(origins)} origins configured")
            print(f"   🌐 Localhost allowed: {localhost_allowed}")
            print(f"   📋 Methods: {data.get('allowed_methods', [])}")
        else:
            print(f"   ❌ CORS check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ CORS check error: {str(e)}")
    
    # Test 3: Login endpoint
    print("\\n3. Testing Login Endpoint...")
    login_data = {
        "email": "admin@onlinetestmaker.com",
        "password": "admin123"
    }
    try:
        response = requests.post(
            f"{api_url}/auth/login",
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login successful: {data.get('user', {}).get('role', 'Unknown')} user")
            print(f"   🔑 Token received: {'Yes' if data.get('access_token') else 'No'}")
            token = data.get('access_token')
            
            # Test 4: Auth/me endpoint with token
            print("\\n4. Testing /auth/me endpoint...")
            try:
                auth_response = requests.get(
                    f"{api_url}/auth/me",
                    headers={'Authorization': f'Bearer {token}'},
                    timeout=10
                )
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    print(f"   ✅ Auth/me successful: {auth_data.get('name', 'Unknown')}")
                    print(f"   👤 Role: {auth_data.get('role', 'Unknown')}")
                    print(f"   📧 Email: {auth_data.get('email', 'Unknown')}")
                else:
                    print(f"   ❌ Auth/me failed: {auth_response.status_code}")
                    print(f"   📄 Response: {auth_response.text[:200]}")
            except Exception as e:
                print(f"   ❌ Auth/me error: {str(e)}")
                
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {str(e)}")
        return False
    
    # Test 5: Check if frontend can reach backend (simulate browser request)
    print("\\n5. Testing Browser-like Request...")
    try:
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3000',  # Simulate frontend origin
            'Referer': 'http://localhost:3000/',
            'User-Agent': 'Mozilla/5.0 (compatible; TestBot/1.0)'
        }
        response = requests.post(
            f"{api_url}/auth/login",
            json=login_data,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            print(f"   ✅ Browser-like request successful")
            print(f"   🔗 CORS headers present: {'Access-Control-Allow-Origin' in response.headers}")
        else:
            print(f"   ❌ Browser-like request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Browser-like request error: {str(e)}")
    
    print("\\n" + "=" * 60)
    print("✅ Frontend-Backend Communication Test Complete!")
    print("🎯 If all tests passed, the backend is working correctly.")
    print("🔍 If login still fails in frontend, check browser console for JavaScript errors.")
    return True

if __name__ == "__main__":
    success = test_frontend_backend_communication()
    sys.exit(0 if success else 1)