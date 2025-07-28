#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Social and Privacy Control Features
Testing Priority: HIGH

This script tests the newly implemented social and privacy features:
1. Enhanced User Model with privacy settings
2. Follow System with Privacy Controls
3. Privacy Settings Management
4. User Profile with Privacy Filtering
5. Admin Social Controls
"""

import requests
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "admin@squiz.com"
ADMIN_PASSWORD = "admin123"

class SocialBackendTester:
    def __init__(self):
        self.admin_token = None
        self.user1_token = None
        self.user2_token = None
        self.user3_token = None
        self.test_results = []
        self.admin_user_id = None
        self.user1_id = None
        self.user2_id = None
        self.user3_id = None
        self.created_users = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    token: str = None, expected_status: int = 200) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            response = requests.request(method, url, json=data, headers=headers, timeout=10)
            
            if response.status_code != expected_status:
                print(f"❌ Request failed: {method} {endpoint}")
                print(f"   Expected status: {expected_status}, Got: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
            
            if response.text:
                return response.json()
            return {}
                
        except Exception as e:
            print(f"❌ Request error: {method} {endpoint} - {str(e)}")
            return None
    
    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("\n🔐 Authenticating as admin...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and "access_token" in response:
            self.admin_token = response["access_token"]
            self.admin_user_id = response["user"]["id"]
            self.log_test("Admin Authentication", True, f"Admin ID: {self.admin_user_id}")
            return True
        
        self.log_test("Admin Authentication", False, "Failed to get admin token")
        return False
    
    def create_test_users(self) -> bool:
        """Create test users for social testing"""
        print("\n👥 Creating test users for social testing...")
        
        test_users = [
            {"email": "socialuser1@example.com", "name": "Social User 1", "password": "password123"},
            {"email": "socialuser2@example.com", "name": "Social User 2", "password": "password123"},
            {"email": "socialuser3@example.com", "name": "Social User 3", "password": "password123"}
        ]
        
        tokens = []
        user_ids = []
        
        for i, user_data in enumerate(test_users):
            # Try to register user
            response = self.make_request("POST", "/auth/register", user_data)
            if response:
                self.created_users.append(user_data["email"])
            
            # Login user
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            if response and "access_token" in response:
                tokens.append(response["access_token"])
                user_ids.append(response["user"]["id"])
                self.log_test(f"Test User {i+1} Authentication", True, f"User ID: {response['user']['id']}")
            else:
                self.log_test(f"Test User {i+1} Authentication", False, "Failed to authenticate")
                return False
        
        if len(tokens) == 3:
            self.user1_token, self.user2_token, self.user3_token = tokens
            self.user1_id, self.user2_id, self.user3_id = user_ids
            return True
        
        return False
    
    def test_enhanced_user_model(self):
        """Test Enhanced User Model with privacy settings"""
        print("\n👤 Testing Enhanced User Model...")
        
        # Test 1: Verify user model has privacy fields
        response = self.make_request("GET", "/auth/me", token=self.user1_token)
        if response:
            required_fields = ["is_private", "follower_count", "following_count"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                self.log_test("Enhanced User Model Fields", True, 
                            f"Privacy fields present: is_private={response.get('is_private')}, "
                            f"follower_count={response.get('follower_count')}, "
                            f"following_count={response.get('following_count')}")
            else:
                self.log_test("Enhanced User Model Fields", False, f"Missing fields: {missing_fields}")
        else:
            self.log_test("Enhanced User Model Fields", False, "Failed to get user info")
        
        # Test 2: Verify default privacy settings
        if response:
            is_private = response.get("is_private", None)
            follower_count = response.get("follower_count", None)
            following_count = response.get("following_count", None)
            
            if is_private is False and follower_count == 0 and following_count == 0:
                self.log_test("Default Privacy Settings", True, "Default values correct: public profile, 0 followers/following")
            else:
                self.log_test("Default Privacy Settings", False, 
                            f"Unexpected defaults: is_private={is_private}, "
                            f"follower_count={follower_count}, following_count={following_count}")
    
    def test_privacy_settings_management(self):
        """Test Privacy Settings Management"""
        print("\n🔒 Testing Privacy Settings Management...")
        
        # Test 1: Get current privacy settings
        response = self.make_request("GET", "/privacy-settings", token=self.user1_token)
        if response:
            self.log_test("GET Privacy Settings", True, f"Current settings: {response}")
        else:
            self.log_test("GET Privacy Settings", False, "Failed to get privacy settings")
        
        # Test 2: Update privacy settings to private
        update_data = {
            "is_private": True,
            "allow_followers_to_see_activity": False
        }
        
        response = self.make_request("PUT", "/privacy-settings", update_data, token=self.user1_token)
        if response:
            self.log_test("Update Privacy Settings to Private", True, "Successfully updated to private")
            
            # Verify the change
            verify_response = self.make_request("GET", "/auth/me", token=self.user1_token)
            if verify_response and verify_response.get("is_private") is True:
                self.log_test("Privacy Settings Verification", True, "User is now private")
            else:
                self.log_test("Privacy Settings Verification", False, "Privacy setting not reflected in user model")
        else:
            self.log_test("Update Privacy Settings to Private", False, "Failed to update privacy settings")
        
        # Test 3: Update privacy settings back to public
        update_data = {
            "is_private": False,
            "allow_followers_to_see_activity": True
        }
        
        response = self.make_request("PUT", "/privacy-settings", update_data, token=self.user1_token)
        if response:
            self.log_test("Update Privacy Settings to Public", True, "Successfully updated to public")
        else:
            self.log_test("Update Privacy Settings to Public", False, "Failed to update privacy settings")
    
    def test_follow_system_public_user(self):
        """Test Follow System with Public Users"""
        print("\n👥 Testing Follow System - Public Users...")
        
        # Ensure user2 is public
        self.make_request("PUT", "/privacy-settings", {"is_private": False}, token=self.user2_token)
        
        # Test 1: User1 follows User2 (public user)
        follow_data = {"user_id": self.user2_id}
        response = self.make_request("POST", "/follow", follow_data, token=self.user1_token)
        
        if response:
            expected_action = "followed"
            if response.get("action") == expected_action and response.get("is_following") is True:
                self.log_test("Follow Public User", True, f"Successfully followed public user: {response.get('message')}")
            else:
                self.log_test("Follow Public User", False, f"Unexpected response: {response}")
        else:
            self.log_test("Follow Public User", False, "Failed to follow public user")
        
        # Test 2: Verify follower/following counts updated
        user1_info = self.make_request("GET", "/auth/me", token=self.user1_token)
        user2_info = self.make_request("GET", "/auth/me", token=self.user2_token)
        
        if (user1_info and user2_info and 
            user1_info.get("following_count") == 1 and 
            user2_info.get("follower_count") == 1):
            self.log_test("Follow Counts Update", True, "Follower/following counts updated correctly")
        else:
            self.log_test("Follow Counts Update", False, 
                        f"Counts not updated: User1 following={user1_info.get('following_count') if user1_info else 'N/A'}, "
                        f"User2 followers={user2_info.get('follower_count') if user2_info else 'N/A'}")
        
        # Test 3: Test unfollow functionality
        response = self.make_request("DELETE", f"/follow/{self.user2_id}", token=self.user1_token)
        
        if response:
            expected_action = "unfollowed"
            if response.get("action") == expected_action and response.get("is_following") is False:
                self.log_test("Unfollow User", True, f"Successfully unfollowed user: {response.get('message')}")
            else:
                self.log_test("Unfollow User", False, f"Unexpected response: {response}")
        else:
            self.log_test("Unfollow User", False, "Failed to unfollow user")
    
    def test_follow_system_private_user(self):
        """Test Follow System with Private Users"""
        print("\n🔐 Testing Follow System - Private Users...")
        
        # Ensure user3 is private
        self.make_request("PUT", "/privacy-settings", {"is_private": True}, token=self.user3_token)
        
        # Test 1: User1 tries to follow User3 (private user) - should create pending request
        follow_data = {"user_id": self.user3_id}
        response = self.make_request("POST", "/follow", follow_data, token=self.user1_token)
        
        if response:
            expected_action = "request_sent"
            if response.get("action") == expected_action and response.get("is_pending") is True:
                self.log_test("Follow Private User - Request Sent", True, f"Follow request sent: {response.get('message')}")
            else:
                self.log_test("Follow Private User - Request Sent", False, f"Unexpected response: {response}")
        else:
            self.log_test("Follow Private User - Request Sent", False, "Failed to send follow request")
        
        # Test 2: Get pending follow requests for User3
        response = self.make_request("GET", "/follow-requests", token=self.user3_token)
        if response and "requests" in response and len(response["requests"]) > 0:
            request_found = any(req.get("follower_id") == self.user1_id for req in response["requests"])
            request_id = None
            for req in response["requests"]:
                if req.get("follower_id") == self.user1_id:
                    request_id = req.get("id")
                    break
            
            if request_found and request_id:
                self.log_test("Get Follow Requests", True, f"Found {len(response['requests'])} pending request(s)")
                
                # Test 3: User3 approves the follow request
                response = self.make_request("POST", f"/follow-requests/{request_id}/approve", token=self.user3_token)
                
                if response:
                    expected_action = "request_approved"
                    if response.get("action") == expected_action:
                        self.log_test("Approve Follow Request", True, f"Follow request approved: {response.get('message')}")
                    else:
                        self.log_test("Approve Follow Request", False, f"Unexpected response: {response}")
                else:
                    self.log_test("Approve Follow Request", False, "Failed to approve follow request")
            else:
                self.log_test("Get Follow Requests", False, "Follow request not found in pending requests")
        else:
            self.log_test("Get Follow Requests", False, "No pending requests found or failed to get requests")
        
        # Test 4: Verify follower/following counts updated after approval
        user1_info = self.make_request("GET", "/auth/me", token=self.user1_token)
        user3_info = self.make_request("GET", "/auth/me", token=self.user3_token)
        
        if (user1_info and user3_info and 
            user1_info.get("following_count") >= 1 and 
            user3_info.get("follower_count") >= 1):
            self.log_test("Follow Counts After Approval", True, "Follower/following counts updated after approval")
        else:
            self.log_test("Follow Counts After Approval", False, 
                        f"Counts not updated after approval: User1 following={user1_info.get('following_count') if user1_info else 'N/A'}, "
                        f"User3 followers={user3_info.get('follower_count') if user3_info else 'N/A'}")
    
    def test_follow_request_rejection(self):
        """Test Follow Request Rejection"""
        print("\n❌ Testing Follow Request Rejection...")
        
        # User2 tries to follow User3 (private user)
        follow_data = {"user_id": self.user3_id}
        response = self.make_request("POST", "/follow", follow_data, token=self.user2_token)
        
        if response and response.get("action") == "request_sent":
            self.log_test("Follow Request for Rejection Test", True, "Follow request sent successfully")
            
            # User3 rejects the follow request
            reject_data = {"user_id": self.user2_id}
            response = self.make_request("POST", "/follow-requests/reject", reject_data, token=self.user3_token)
            
            if response:
                expected_action = "request_rejected"
                if response.get("action") == expected_action:
                    self.log_test("Reject Follow Request", True, f"Follow request rejected: {response.get('message')}")
                else:
                    self.log_test("Reject Follow Request", False, f"Unexpected response: {response}")
            else:
                self.log_test("Reject Follow Request", False, "Failed to reject follow request")
        else:
            self.log_test("Follow Request for Rejection Test", False, "Failed to send follow request for rejection test")
    
    def test_user_profile_privacy_filtering(self):
        """Test User Profile with Privacy Filtering"""
        print("\n👁️ Testing User Profile Privacy Filtering...")
        
        # Test 1: View public user profile (User2)
        response = self.make_request("GET", f"/user/{self.user2_id}/profile", token=self.user1_token)
        if response:
            # Should see full profile for public user
            if "email" in response and "total_questions" in response:
                self.log_test("View Public User Profile", True, f"Full profile visible for public user: {response.get('name')}")
            else:
                self.log_test("View Public User Profile", False, "Public profile missing expected fields")
        else:
            self.log_test("View Public User Profile", False, "Failed to get public user profile")
        
        # Test 2: View private user profile (User3) as non-follower
        # First, ensure User1 is not following User3
        self.make_request("POST", "/unfollow", {"user_id": self.user3_id}, token=self.user1_token)
        
        response = self.make_request("GET", f"/user/{self.user3_id}/profile", token=self.user1_token)
        if response:
            # Should see limited profile for private user when not following
            if "email" not in response and response.get("can_view_activity") is False:
                self.log_test("View Private User Profile - Non-Follower", True, "Limited profile shown for private user")
            else:
                self.log_test("View Private User Profile - Non-Follower", False, "Private profile showing too much information")
        else:
            self.log_test("View Private User Profile - Non-Follower", False, "Failed to get private user profile")
        
        # Test 3: Admin can view any profile
        response = self.make_request("GET", f"/user/{self.user3_id}/profile", token=self.admin_token)
        if response:
            # Admin should see full profile regardless of privacy
            if "email" in response and response.get("can_view_activity") is True:
                self.log_test("Admin View Private Profile", True, "Admin can view full private profile")
            else:
                self.log_test("Admin View Private Profile", False, "Admin cannot see full private profile")
        else:
            self.log_test("Admin View Private Profile", False, "Admin failed to get private user profile")
    
    def test_admin_social_controls(self):
        """Test Admin Social Controls"""
        print("\n👑 Testing Admin Social Controls...")
        
        # Test 1: Admin social overview
        response = self.make_request("GET", "/admin/social-overview", token=self.admin_token)
        if response:
            required_fields = ["total_users", "total_follows", "total_pending_requests", "private_users_count"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                self.log_test("Admin Social Overview", True, 
                            f"Social stats: {response.get('total_users')} users, "
                            f"{response.get('total_follows')} follows, "
                            f"{response.get('total_pending_requests')} pending requests, "
                            f"{response.get('private_users_count')} private users")
            else:
                self.log_test("Admin Social Overview", False, f"Missing fields: {missing_fields}")
        else:
            self.log_test("Admin Social Overview", False, "Failed to get admin social overview")
        
        # Test 2: Admin can view any user's followers
        response = self.make_request("GET", f"/admin/user/{self.user3_id}/followers", token=self.admin_token)
        if response:
            if isinstance(response, list):
                self.log_test("Admin View User Followers", True, f"Admin can view followers: {len(response)} followers found")
            else:
                self.log_test("Admin View User Followers", False, "Unexpected response format for followers")
        else:
            self.log_test("Admin View User Followers", False, "Admin failed to get user followers")
        
        # Test 3: Admin can view any user's following list
        response = self.make_request("GET", f"/admin/user/{self.user1_id}/following", token=self.admin_token)
        if response:
            if isinstance(response, list):
                self.log_test("Admin View User Following", True, f"Admin can view following: {len(response)} following found")
            else:
                self.log_test("Admin View User Following", False, "Unexpected response format for following")
        else:
            self.log_test("Admin View User Following", False, "Admin failed to get user following list")
    
    def test_privacy_auto_approve_feature(self):
        """Test that changing to public auto-approves pending requests"""
        print("\n🔄 Testing Privacy Auto-Approve Feature...")
        
        # Setup: Make User3 private and create a pending request
        self.make_request("PUT", "/privacy-settings", {"is_private": True}, token=self.user3_token)
        
        # User2 sends follow request to User3
        follow_data = {"user_id": self.user3_id}
        response = self.make_request("POST", "/follow", follow_data, token=self.user2_token)
        
        if response and response.get("action") == "request_sent":
            self.log_test("Setup Pending Request", True, "Pending request created for auto-approve test")
            
            # User3 changes to public - should auto-approve pending requests
            response = self.make_request("PUT", "/privacy-settings", {"is_private": False}, token=self.user3_token)
            
            if response:
                self.log_test("Change to Public", True, "Successfully changed to public profile")
                
                # Check if the pending request was auto-approved
                # This would be reflected in the follower counts
                time.sleep(1)  # Brief delay for processing
                user2_info = self.make_request("GET", "/auth/me", token=self.user2_token)
                user3_info = self.make_request("GET", "/auth/me", token=self.user3_token)
                
                if (user2_info and user3_info and 
                    user2_info.get("following_count") >= 1 and 
                    user3_info.get("follower_count") >= 1):
                    self.log_test("Auto-Approve Pending Requests", True, "Pending requests auto-approved when changing to public")
                else:
                    self.log_test("Auto-Approve Pending Requests", False, "Pending requests not auto-approved")
            else:
                self.log_test("Change to Public", False, "Failed to change to public profile")
        else:
            self.log_test("Setup Pending Request", False, "Failed to create pending request for auto-approve test")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Unfollow all relationships
        if self.user1_token and self.user2_id:
            self.make_request("POST", "/unfollow", {"user_id": self.user2_id}, token=self.user1_token)
        if self.user1_token and self.user3_id:
            self.make_request("POST", "/unfollow", {"user_id": self.user3_id}, token=self.user1_token)
        if self.user2_token and self.user3_id:
            self.make_request("POST", "/unfollow", {"user_id": self.user3_id}, token=self.user2_token)
        
        self.log_test("Cleanup Test Data", True, "Test relationships cleaned up")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 SOCIAL AND PRIVACY FEATURES TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n🔍 KEY FINDINGS:")
        
        # Analyze results by category
        categories = {
            "Enhanced User Model": ["Enhanced User Model Fields", "Default Privacy Settings"],
            "Privacy Settings": ["GET Privacy Settings", "Update Privacy Settings to Private", "Update Privacy Settings to Public", "Privacy Settings Verification"],
            "Follow System": ["Follow Public User", "Follow Counts Update", "Unfollow User", "Follow Private User - Request Sent", "Get Follow Requests", "Approve Follow Request", "Follow Counts After Approval", "Reject Follow Request"],
            "Profile Privacy": ["View Public User Profile", "View Private User Profile - Non-Follower", "Admin View Private Profile"],
            "Admin Controls": ["Admin Social Overview", "Admin View User Followers", "Admin View User Following"],
            "Auto-Approve": ["Auto-Approve Pending Requests"]
        }
        
        for category, tests in categories.items():
            category_results = [r for r in self.test_results if r["test"] in tests]
            if category_results:
                category_passed = sum(1 for r in category_results if r["success"])
                category_total = len(category_results)
                status = "✅" if category_passed == category_total else "⚠️" if category_passed > 0 else "❌"
                print(f"   {status} {category}: {category_passed}/{category_total} tests passed")
        
        print("\n" + "="*80)
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    print("🚀 Starting Social and Privacy Features Backend Testing...")
    print("="*80)
    
    tester = SocialBackendTester()
    
    # Authentication
    if not tester.authenticate_admin():
        print("❌ Admin authentication failed. Exiting.")
        return False
    
    if not tester.create_test_users():
        print("❌ Test user creation failed. Exiting.")
        return False
    
    try:
        # Run all tests
        tester.test_enhanced_user_model()
        tester.test_privacy_settings_management()
        tester.test_follow_system_public_user()
        tester.test_follow_system_private_user()
        tester.test_follow_request_rejection()
        tester.test_user_profile_privacy_filtering()
        tester.test_admin_social_controls()
        tester.test_privacy_auto_approve_feature()
        
        # Cleanup
        tester.cleanup_test_data()
        
        # Print summary
        success = tester.print_summary()
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)