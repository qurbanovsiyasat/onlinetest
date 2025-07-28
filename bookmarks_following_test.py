#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Bookmarks & Following System
Testing all endpoints as requested in the review.
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class BookmarksFollowingTester:
    def __init__(self):
        self.admin_token = None
        self.user1_token = None
        self.user2_token = None
        self.user1_id = None
        self.user2_id = None
        self.test_quiz_id = None
        self.test_question_id = None
        self.results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method, endpoint, data=None, token=None, params=None):
        """Make HTTP request with proper headers"""
        url = f"{API_BASE}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None
    
    def test_admin_authentication(self):
        """Test admin login"""
        print("\n🔐 Testing Admin Authentication...")
        
        response = self.make_request("POST", "/auth/login", {
            "email": "admin@squiz.com",
            "password": "admin123"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data["access_token"]
            self.log_result("Admin Authentication", True, "Admin login successful")
            return True
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Admin Authentication", False, f"Admin login failed: {error_msg}")
            return False
    
    def test_user_registration_and_login(self):
        """Test user registration and login for two test users"""
        print("\n👥 Testing User Registration and Login...")
        
        # Register User 1
        user1_data = {
            "email": "bookmarkuser1@test.com",
            "name": "Bookmark Test User 1",
            "password": "testpass123"
        }
        
        response = self.make_request("POST", "/auth/register", user1_data)
        if response and response.status_code == 200:
            self.log_result("User 1 Registration", True, "User 1 registered successfully")
            
            # Login User 1
            login_response = self.make_request("POST", "/auth/login", {
                "email": user1_data["email"],
                "password": user1_data["password"]
            })
            
            if login_response and login_response.status_code == 200:
                data = login_response.json()
                self.user1_token = data["access_token"]
                self.user1_id = data["user"]["id"]
                self.log_result("User 1 Login", True, "User 1 login successful")
            else:
                self.log_result("User 1 Login", False, "User 1 login failed")
                return False
        else:
            self.log_result("User 1 Registration", False, "User 1 registration failed")
            return False
        
        # Register User 2
        user2_data = {
            "email": "bookmarkuser2@test.com",
            "name": "Bookmark Test User 2",
            "password": "testpass123"
        }
        
        response = self.make_request("POST", "/auth/register", user2_data)
        if response and response.status_code == 200:
            self.log_result("User 2 Registration", True, "User 2 registered successfully")
            
            # Login User 2
            login_response = self.make_request("POST", "/auth/login", {
                "email": user2_data["email"],
                "password": user2_data["password"]
            })
            
            if login_response and login_response.status_code == 200:
                data = login_response.json()
                self.user2_token = data["access_token"]
                self.user2_id = data["user"]["id"]
                self.log_result("User 2 Login", True, "User 2 login successful")
                return True
            else:
                self.log_result("User 2 Login", False, "User 2 login failed")
                return False
        else:
            self.log_result("User 2 Registration", False, "User 2 registration failed")
            return False
    
    def setup_test_content(self):
        """Create test quiz and question for bookmarking"""
        print("\n📝 Setting up Test Content...")
        
        # Create a test quiz (admin)
        quiz_data = {
            "title": "Bookmarks Test Quiz",
            "description": "A quiz for testing bookmark functionality",
            "category": "Test",
            "subject": "Testing",
            "subcategory": "Bookmarks",
            "questions": [
                {
                    "question_text": "What is 2 + 2?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True},
                        {"text": "5", "is_correct": False}
                    ],
                    "points": 1
                }
            ]
        }
        
        response = self.make_request("POST", "/admin/quiz", quiz_data, self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            self.test_quiz_id = data["id"]
            
            # Publish the quiz
            publish_response = self.make_request("POST", f"/admin/quiz/{self.test_quiz_id}/publish", {}, self.admin_token)
            if publish_response and publish_response.status_code == 200:
                self.log_result("Test Quiz Creation", True, "Test quiz created and published")
            else:
                self.log_result("Test Quiz Publishing", False, "Failed to publish test quiz")
                return False
        else:
            self.log_result("Test Quiz Creation", False, "Failed to create test quiz")
            return False
        
        # Create a test question (user)
        question_data = {
            "title": "Bookmarks Test Question",
            "content": "How do bookmarks work in this system?",
            "subject": "Testing",
            "subcategory": "Bookmarks",
            "tags": ["bookmarks", "testing"]
        }
        
        response = self.make_request("POST", "/questions", question_data, self.user1_token)
        if response and response.status_code == 200:
            data = response.json()
            self.test_question_id = data["id"]
            self.log_result("Test Question Creation", True, "Test question created")
            return True
        else:
            self.log_result("Test Question Creation", False, "Failed to create test question")
            return False
    
    def test_bookmarks_system(self):
        """Test all bookmark endpoints"""
        print("\n🔖 Testing Bookmarks System...")
        
        # Test 1: Bookmark a quiz
        bookmark_quiz_data = {
            "item_id": self.test_quiz_id,
            "item_type": "quiz"
        }
        
        response = self.make_request("POST", "/bookmarks", bookmark_quiz_data, self.user1_token)
        if response and response.status_code == 200:
            self.log_result("Bookmark Quiz", True, "Successfully bookmarked quiz")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Bookmark Quiz", False, f"Failed to bookmark quiz: {error_msg}")
        
        # Test 2: Bookmark a question
        bookmark_question_data = {
            "item_id": self.test_question_id,
            "item_type": "question"
        }
        
        response = self.make_request("POST", "/bookmarks", bookmark_question_data, self.user1_token)
        if response and response.status_code == 200:
            self.log_result("Bookmark Question", True, "Successfully bookmarked question")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Bookmark Question", False, f"Failed to bookmark question: {error_msg}")
        
        # Test 3: Get user's bookmarks
        response = self.make_request("GET", "/bookmarks", token=self.user1_token)
        if response and response.status_code == 200:
            data = response.json()
            bookmarks = data.get("bookmarks", [])
            if len(bookmarks) >= 2:
                self.log_result("Get Bookmarks", True, f"Retrieved {len(bookmarks)} bookmarks successfully")
            else:
                self.log_result("Get Bookmarks", False, f"Expected at least 2 bookmarks, got {len(bookmarks)}")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Get Bookmarks", False, f"Failed to get bookmarks: {error_msg}")
        
        # Test 4: Check bookmark status for quiz
        params = {"item_type": "quiz"}
        response = self.make_request("GET", f"/bookmarks/check/{self.test_quiz_id}", token=self.user1_token, params=params)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("is_bookmarked") == True:
                self.log_result("Check Quiz Bookmark Status", True, "Quiz bookmark status correctly returned as bookmarked")
            else:
                self.log_result("Check Quiz Bookmark Status", False, "Quiz should be bookmarked but status shows not bookmarked")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Check Quiz Bookmark Status", False, f"Failed to check quiz bookmark status: {error_msg}")
        
        # Test 5: Check bookmark status for question
        params = {"item_type": "question"}
        response = self.make_request("GET", f"/bookmarks/check/{self.test_question_id}", token=self.user1_token, params=params)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("is_bookmarked") == True:
                self.log_result("Check Question Bookmark Status", True, "Question bookmark status correctly returned as bookmarked")
            else:
                self.log_result("Check Question Bookmark Status", False, "Question should be bookmarked but status shows not bookmarked")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Check Question Bookmark Status", False, f"Failed to check question bookmark status: {error_msg}")
        
        # Test 6: Remove quiz bookmark
        params = {"item_type": "quiz"}
        response = self.make_request("DELETE", f"/bookmarks/{self.test_quiz_id}", token=self.user1_token, params=params)
        if response and response.status_code == 200:
            self.log_result("Remove Quiz Bookmark", True, "Successfully removed quiz bookmark")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Remove Quiz Bookmark", False, f"Failed to remove quiz bookmark: {error_msg}")
        
        # Test 7: Verify quiz bookmark is removed
        params = {"item_type": "quiz"}
        response = self.make_request("GET", f"/bookmarks/check/{self.test_quiz_id}", token=self.user1_token, params=params)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("is_bookmarked") == False:
                self.log_result("Verify Quiz Bookmark Removal", True, "Quiz bookmark correctly removed")
            else:
                self.log_result("Verify Quiz Bookmark Removal", False, "Quiz bookmark should be removed but still shows as bookmarked")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Verify Quiz Bookmark Removal", False, f"Failed to verify quiz bookmark removal: {error_msg}")
    
    def test_following_system(self):
        """Test all following endpoints"""
        print("\n👥 Testing Following System...")
        
        # Test 1: User 1 follows User 2
        follow_data = {
            "user_id": self.user2_id
        }
        
        response = self.make_request("POST", "/follow", follow_data, self.user1_token)
        if response and response.status_code == 200:
            self.log_result("Follow User", True, "User 1 successfully followed User 2")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Follow User", False, f"Failed to follow user: {error_msg}")
        
        # Test 2: Get follow statistics for User 2
        response = self.make_request("GET", f"/users/{self.user2_id}/follow-stats", token=self.user1_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("followers_count") >= 1 and data.get("is_following") == True:
                self.log_result("Get Follow Stats", True, f"Follow stats correct: {data['followers_count']} followers, is_following: {data['is_following']}")
            else:
                self.log_result("Get Follow Stats", False, f"Follow stats incorrect: {data}")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Get Follow Stats", False, f"Failed to get follow stats: {error_msg}")
        
        # Test 3: Get who User 1 is following
        response = self.make_request("GET", "/following", token=self.user1_token)
        if response and response.status_code == 200:
            data = response.json()
            following = data.get("following", [])
            if len(following) >= 1:
                self.log_result("Get Following List", True, f"User 1 is following {len(following)} users")
            else:
                self.log_result("Get Following List", False, f"Expected at least 1 following, got {len(following)}")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Get Following List", False, f"Failed to get following list: {error_msg}")
        
        # Test 4: Get User 2's followers
        response = self.make_request("GET", "/followers", token=self.user2_token)
        if response and response.status_code == 200:
            data = response.json()
            followers = data.get("followers", [])
            if len(followers) >= 1:
                self.log_result("Get Followers List", True, f"User 2 has {len(followers)} followers")
            else:
                self.log_result("Get Followers List", False, f"Expected at least 1 follower, got {len(followers)}")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Get Followers List", False, f"Failed to get followers list: {error_msg}")
        
        # Test 5: User 1 unfollows User 2
        response = self.make_request("DELETE", f"/follow/{self.user2_id}", token=self.user1_token)
        if response and response.status_code == 200:
            self.log_result("Unfollow User", True, "User 1 successfully unfollowed User 2")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Unfollow User", False, f"Failed to unfollow user: {error_msg}")
        
        # Test 6: Verify unfollow worked
        response = self.make_request("GET", f"/users/{self.user2_id}/follow-stats", token=self.user1_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("is_following") == False:
                self.log_result("Verify Unfollow", True, "Unfollow verified - is_following is now False")
            else:
                self.log_result("Verify Unfollow", False, "Unfollow failed - is_following is still True")
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_result("Verify Unfollow", False, f"Failed to verify unfollow: {error_msg}")
    
    def test_error_cases(self):
        """Test error cases as requested"""
        print("\n🚫 Testing Error Cases...")
        
        # Test 1: Try to follow yourself
        follow_self_data = {
            "user_id": self.user1_id
        }
        
        response = self.make_request("POST", "/follow", follow_self_data, self.user1_token)
        if response and response.status_code == 400:
            self.log_result("Follow Self Error", True, "Correctly prevented user from following themselves")
        else:
            self.log_result("Follow Self Error", False, "Should have prevented self-following with 400 error")
        
        # Test 2: Try to bookmark non-existent quiz
        fake_bookmark_data = {
            "item_id": "non-existent-quiz-id",
            "item_type": "quiz"
        }
        
        response = self.make_request("POST", "/bookmarks", fake_bookmark_data, self.user1_token)
        if response and response.status_code == 404:
            self.log_result("Bookmark Non-existent Quiz", True, "Correctly returned 404 for non-existent quiz")
        else:
            self.log_result("Bookmark Non-existent Quiz", False, "Should have returned 404 for non-existent quiz")
        
        # Test 3: Try to bookmark non-existent question
        fake_question_bookmark_data = {
            "item_id": "non-existent-question-id",
            "item_type": "question"
        }
        
        response = self.make_request("POST", "/bookmarks", fake_question_bookmark_data, self.user1_token)
        if response and response.status_code == 404:
            self.log_result("Bookmark Non-existent Question", True, "Correctly returned 404 for non-existent question")
        else:
            self.log_result("Bookmark Non-existent Question", False, "Should have returned 404 for non-existent question")
        
        # Test 4: Try duplicate bookmark
        # First bookmark the quiz again
        bookmark_quiz_data = {
            "item_id": self.test_quiz_id,
            "item_type": "quiz"
        }
        
        self.make_request("POST", "/bookmarks", bookmark_quiz_data, self.user1_token)  # Create bookmark
        
        # Try to bookmark again
        response = self.make_request("POST", "/bookmarks", bookmark_quiz_data, self.user1_token)
        if response and response.status_code == 400:
            self.log_result("Duplicate Bookmark Error", True, "Correctly prevented duplicate bookmark")
        else:
            self.log_result("Duplicate Bookmark Error", False, "Should have prevented duplicate bookmark with 400 error")
        
        # Test 5: Try duplicate follow
        # First follow User 2 again
        follow_data = {
            "user_id": self.user2_id
        }
        
        self.make_request("POST", "/follow", follow_data, self.user1_token)  # Create follow
        
        # Try to follow again
        response = self.make_request("POST", "/follow", follow_data, self.user1_token)
        if response and response.status_code == 400:
            self.log_result("Duplicate Follow Error", True, "Correctly prevented duplicate follow")
        else:
            self.log_result("Duplicate Follow Error", False, "Should have prevented duplicate follow with 400 error")
        
        # Test 6: Try to follow non-existent user
        fake_follow_data = {
            "user_id": "non-existent-user-id"
        }
        
        response = self.make_request("POST", "/follow", fake_follow_data, self.user1_token)
        if response and response.status_code == 404:
            self.log_result("Follow Non-existent User", True, "Correctly returned 404 for non-existent user")
        else:
            self.log_result("Follow Non-existent User", False, "Should have returned 404 for non-existent user")
    
    def test_integration_with_existing_systems(self):
        """Test integration with existing quiz and question systems"""
        print("\n🔗 Testing Integration with Existing Systems...")
        
        # Test 1: Verify quiz creation works (already tested in setup)
        if self.test_quiz_id:
            self.log_result("Quiz Creation Integration", True, "Quiz creation working correctly")
        else:
            self.log_result("Quiz Creation Integration", False, "Quiz creation failed")
        
        # Test 2: Verify question creation works (already tested in setup)
        if self.test_question_id:
            self.log_result("Question Creation Integration", True, "Question creation working correctly")
        else:
            self.log_result("Question Creation Integration", False, "Question creation failed")
        
        # Test 3: Test bookmarking works with created content
        # This was already tested in bookmark system tests
        bookmark_quiz_data = {
            "item_id": self.test_quiz_id,
            "item_type": "quiz"
        }
        
        response = self.make_request("POST", "/bookmarks", bookmark_quiz_data, self.user2_token)
        if response and response.status_code == 200:
            self.log_result("Bookmark Created Content", True, "Bookmarking works with created quiz content")
        else:
            self.log_result("Bookmark Created Content", False, "Bookmarking failed with created content")
        
        # Test 4: Test notifications system for followers (check if notification was created)
        # Follow User 2 with User 1 to trigger notification
        follow_data = {
            "user_id": self.user2_id
        }
        
        response = self.make_request("POST", "/follow", follow_data, self.user1_token)
        if response and response.status_code == 200:
            # Check if notification endpoint exists and works
            notification_response = self.make_request("GET", "/notifications", token=self.user2_token)
            if notification_response and notification_response.status_code == 200:
                notifications = notification_response.json().get("notifications", [])
                follower_notifications = [n for n in notifications if n.get("type") == "new_follower"]
                if len(follower_notifications) > 0:
                    self.log_result("Notifications Integration", True, "Follower notifications working correctly")
                else:
                    self.log_result("Notifications Integration", False, "No follower notifications found")
            else:
                self.log_result("Notifications Integration", False, "Notifications endpoint not accessible or not working")
        else:
            self.log_result("Notifications Integration", False, "Follow action failed, cannot test notifications")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 BOOKMARKS & FOLLOWING SYSTEM TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        print("\n📊 DETAILED RESULTS:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test']}: {result['message']}")
        
        return passed_tests, failed_tests
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Bookmarks & Following System Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        
        # Authentication tests
        if not self.test_admin_authentication():
            print("❌ Admin authentication failed. Cannot continue.")
            return False
        
        if not self.test_user_registration_and_login():
            print("❌ User authentication failed. Cannot continue.")
            return False
        
        # Setup test content
        if not self.setup_test_content():
            print("❌ Test content setup failed. Cannot continue.")
            return False
        
        # Core functionality tests
        self.test_bookmarks_system()
        self.test_following_system()
        self.test_error_cases()
        self.test_integration_with_existing_systems()
        
        # Print summary
        passed, failed = self.print_summary()
        
        return failed == 0

def main():
    """Main function"""
    tester = BookmarksFollowingTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Bookmarks & Following System is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED. Please check the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()