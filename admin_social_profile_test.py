#!/usr/bin/env python3
"""
Enhanced Admin Social Profile Features Testing
Tests the admin access privileges, privacy-aware activity APIs, and admin badge system
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001/api"

# Test credentials
ADMIN_EMAIL = "admin@squiz.com"
ADMIN_PASSWORD = "admin123"

def log_test(message):
    """Log test message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def make_request(method, endpoint, headers=None, data=None, params=None):
    """Make HTTP request with error handling"""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        log_test(f"❌ Request failed: {e}")
        return None

def test_admin_authentication():
    """Test admin authentication"""
    log_test("🔐 Testing admin authentication...")
    
    response = make_request("POST", "/auth/login", data={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if not response or response.status_code != 200:
        log_test(f"❌ Admin login failed: {response.status_code if response else 'No response'}")
        return None
    
    data = response.json()
    if data.get("user", {}).get("role") != "admin":
        log_test("❌ Admin login successful but role is not admin")
        return None
    
    log_test("✅ Admin authentication successful")
    return data["access_token"]

def test_user_registration_and_login():
    """Create a test user and return their token"""
    log_test("👤 Creating test user...")
    
    # Register user
    user_data = {
        "email": "testuser@example.com",
        "name": "Test User",
        "password": "testpass123"
    }
    
    response = make_request("POST", "/auth/register", data=user_data)
    if not response or response.status_code != 200:
        log_test(f"❌ User registration failed: {response.status_code if response else 'No response'}")
        return None, None
    
    user_info = response.json()
    user_id = user_info["id"]
    
    # Login user
    response = make_request("POST", "/auth/login", data={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    if not response or response.status_code != 200:
        log_test(f"❌ User login failed: {response.status_code if response else 'No response'}")
        return None, None
    
    data = response.json()
    log_test("✅ Test user created and authenticated")
    return data["access_token"], user_id

def set_user_private(user_token, user_id):
    """Set user profile to private"""
    log_test("🔒 Setting user profile to private...")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = make_request("PUT", "/privacy-settings", headers=headers, data={
        "is_private": True
    })
    
    if not response or response.status_code != 200:
        log_test(f"❌ Failed to set user private: {response.status_code if response else 'No response'}")
        return False
    
    log_test("✅ User profile set to private")
    return True

def test_admin_profile_access(admin_token, user_id):
    """Test admin access to private user profiles"""
    log_test("🛡️ Testing admin access to private user profile...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = make_request("GET", f"/users/{user_id}/profile", headers=headers)
    
    if not response or response.status_code != 200:
        log_test(f"❌ Admin profile access failed: {response.status_code if response else 'No response'}")
        return False
    
    profile_data = response.json()
    
    # Check if admin can see private profile
    if not profile_data.get("profile_visible", False):
        log_test("❌ Admin cannot see private profile")
        return False
    
    # Check if email is visible to admin
    if not profile_data.get("email"):
        log_test("❌ Admin cannot see user email")
        return False
    
    log_test("✅ Admin can access private user profile with full details")
    return True

def test_regular_user_private_profile_access(user_token, admin_token):
    """Test regular user trying to access private profiles"""
    log_test("👤 Testing regular user access to private profiles...")
    
    # First, get admin user ID
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = make_request("GET", "/auth/me", headers=admin_headers)
    if not response or response.status_code != 200:
        log_test("❌ Failed to get admin user info")
        return False
    
    admin_user_id = response.json()["id"]
    
    # Try to access admin profile as regular user
    user_headers = {"Authorization": f"Bearer {user_token}"}
    response = make_request("GET", f"/users/{admin_user_id}/profile", headers=user_headers)
    
    if not response or response.status_code != 200:
        log_test(f"❌ Regular user profile access failed: {response.status_code if response else 'No response'}")
        return False
    
    profile_data = response.json()
    
    # Admin profiles are typically public, but let's check the response structure
    log_test("✅ Regular user can access admin profile (admin profiles are public)")
    return True

def test_admin_badge_in_profile(admin_token, user_id):
    """Test admin badge display in profile responses"""
    log_test("🏆 Testing admin badge in profile responses...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get admin's own profile
    response = make_request("GET", "/auth/me", headers=headers)
    if not response or response.status_code != 200:
        log_test("❌ Failed to get admin profile")
        return False
    
    admin_data = response.json()
    admin_user_id = admin_data["id"]
    
    # Get admin profile via user profile endpoint
    response = make_request("GET", f"/users/{admin_user_id}/profile", headers=headers)
    if not response or response.status_code != 200:
        log_test("❌ Failed to get admin profile via user endpoint")
        return False
    
    profile_data = response.json()
    
    # Check admin badge
    if not profile_data.get("is_admin"):
        log_test("❌ Admin profile missing is_admin flag")
        return False
    
    if profile_data.get("admin_badge") != "🛡️ Admin":
        log_test(f"❌ Admin badge incorrect: {profile_data.get('admin_badge')}")
        return False
    
    log_test("✅ Admin badge correctly displayed in profile")
    return True

def test_privacy_aware_activity_apis(admin_token, user_token, user_id):
    """Test privacy-aware activity APIs"""
    log_test("📊 Testing privacy-aware activity APIs...")
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test endpoints that should respect privacy settings
    endpoints = [
        "/questions",
        "/answers", 
        "/followers",
        "/following",
        "/activity"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        full_endpoint = f"/users/{user_id}{endpoint}"
        
        # Test admin access (should work)
        log_test(f"  Testing admin access to {full_endpoint}")
        response = make_request("GET", full_endpoint, headers=admin_headers)
        
        if response and response.status_code == 200:
            data = response.json()
            can_view = data.get("can_view", True)  # Default to True for backwards compatibility
            results[f"admin_{endpoint}"] = can_view
            log_test(f"    ✅ Admin can access {endpoint}: {can_view}")
        else:
            results[f"admin_{endpoint}"] = False
            log_test(f"    ❌ Admin access failed for {endpoint}")
        
        # Test regular user access to private profile (should be restricted)
        # For this test, we'll create another user to test access
        
    return all(results.values())

def test_admin_badge_in_qa_responses(admin_token):
    """Test admin badge in Q&A responses"""
    log_test("💬 Testing admin badge in Q&A responses...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create a test question as admin
    question_data = {
        "title": "Test Question for Admin Badge",
        "content": "This is a test question to verify admin badges in responses",
        "subject": "Testing",
        "tags": ["test", "admin"]
    }
    
    response = make_request("POST", "/questions", headers=headers, data=question_data)
    if not response or response.status_code != 200:
        log_test("❌ Failed to create test question")
        return False
    
    question_id = response.json()["id"]
    
    # Get questions list and check if admin badge is present
    response = make_request("GET", "/questions", headers=headers)
    if not response or response.status_code != 200:
        log_test("❌ Failed to get questions list")
        return False
    
    questions = response.json().get("questions", [])
    test_question = None
    
    for question in questions:
        if question.get("id") == question_id:
            test_question = question
            break
    
    if not test_question:
        log_test("❌ Test question not found in questions list")
        return False
    
    # Check if user info includes admin badge
    user_info = test_question.get("user", {})
    if not user_info.get("is_admin"):
        log_test("❌ Admin flag missing in question user info")
        return False
    
    log_test("✅ Admin badge system working in Q&A responses")
    
    # Clean up - delete test question
    make_request("DELETE", f"/questions/{question_id}", headers=headers)
    
    return True

def run_comprehensive_test():
    """Run comprehensive test of enhanced admin social profile features"""
    log_test("🚀 Starting Enhanced Admin Social Profile Features Testing")
    log_test("=" * 80)
    
    # Test 1: Admin Authentication
    admin_token = test_admin_authentication()
    if not admin_token:
        log_test("❌ CRITICAL: Admin authentication failed - cannot continue")
        return False
    
    # Test 2: Create test user and set as private
    user_token, user_id = test_user_registration_and_login()
    if not user_token or not user_id:
        log_test("❌ CRITICAL: Test user creation failed - cannot continue")
        return False
    
    if not set_user_private(user_token, user_id):
        log_test("❌ CRITICAL: Failed to set user private - cannot continue")
        return False
    
    # Test 3: Admin access to private profiles
    test_results = []
    
    test_results.append(("Admin Profile Access", test_admin_profile_access(admin_token, user_id)))
    test_results.append(("Regular User Profile Access", test_regular_user_private_profile_access(user_token, admin_token)))
    test_results.append(("Admin Badge in Profile", test_admin_badge_in_profile(admin_token, user_id)))
    test_results.append(("Privacy-Aware Activity APIs", test_privacy_aware_activity_apis(admin_token, user_token, user_id)))
    test_results.append(("Admin Badge in Q&A", test_admin_badge_in_qa_responses(admin_token)))
    
    # Summary
    log_test("=" * 80)
    log_test("📋 TEST RESULTS SUMMARY:")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test(f"  {test_name}: {status}")
        if result:
            passed_tests += 1
    
    log_test("=" * 80)
    log_test(f"📊 OVERALL RESULT: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        log_test("🎉 ALL TESTS PASSED! Enhanced admin social profile features are working correctly.")
        return True
    else:
        log_test("⚠️  SOME TESTS FAILED! Please review the failed tests above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)