#!/usr/bin/env python3
"""
Comprehensive Backend Testing for User Profile and Notification System
Testing Priority: HIGH

This script tests the newly implemented backend features:
1. User Profile System Testing
2. Notification System Testing  
3. Notification Triggers Testing
4. Profile Statistics Testing
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
TEST_USER_EMAIL = "testprofile@example.com"
TEST_USER_PASSWORD = "password123"

class BackendTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.admin_user_id = None
        self.test_user_id = None
    
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
    
    def create_test_user(self) -> bool:
        """Create and authenticate test user"""
        print("\n👤 Creating test user...")
        
        # Register test user
        register_data = {
            "email": TEST_USER_EMAIL,
            "name": "Test Profile User",
            "password": TEST_USER_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/register", register_data)
        if not response:
            # User might already exist, try to login
            print("   User might already exist, trying to login...")
        
        # Login test user
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and "access_token" in response:
            self.user_token = response["access_token"]
            self.test_user_id = response["user"]["id"]
            self.log_test("Test User Authentication", True, f"User ID: {self.test_user_id}")
            return True
        
        self.log_test("Test User Authentication", False, "Failed to authenticate test user")
        return False
    
    def test_user_profile_endpoints(self):
        """Test User Profile System endpoints"""
        print("\n📋 Testing User Profile System...")
        
        # Test 1: Get current user profile
        response = self.make_request("GET", "/profile", token=self.user_token)
        if response and "id" in response:
            self.log_test("GET /api/profile", True, f"Profile loaded for user: {response['name']}")
            
            # Verify profile structure
            required_fields = ["id", "email", "name", "role", "questions_count", "answers_count", "quizzes_taken"]
            missing_fields = [field for field in required_fields if field not in response]
            if not missing_fields:
                self.log_test("Profile Structure Validation", True, "All required fields present")
            else:
                self.log_test("Profile Structure Validation", False, f"Missing fields: {missing_fields}")
        else:
            self.log_test("GET /api/profile", False, "Failed to get current user profile")
        
        # Test 2: Update user profile
        update_data = {
            "name": "Updated Test Profile User",
            "bio": "This is a test bio for profile testing",
            "location": "Test City, Test Country",
            "website": "https://test-website.com"
        }
        
        response = self.make_request("PUT", "/profile", update_data, token=self.user_token)
        if response and response.get("name") == update_data["name"]:
            self.log_test("PUT /api/profile", True, "Profile updated successfully")
            
            # Verify update persisted
            response = self.make_request("GET", "/profile", token=self.user_token)
            if response and response.get("bio") == update_data["bio"]:
                self.log_test("Profile Update Persistence", True, "Updated data persisted correctly")
            else:
                self.log_test("Profile Update Persistence", False, "Updated data not persisted")
        else:
            self.log_test("PUT /api/profile", False, "Failed to update profile")
        
        # Test 3: Get public user profile
        response = self.make_request("GET", f"/users/{self.test_user_id}/profile")
        if response and "id" in response:
            self.log_test("GET /api/users/{user_id}/profile", True, "Public profile accessible")
        else:
            self.log_test("GET /api/users/{user_id}/profile", False, "Failed to get public profile")
        
        # Test 4: Get user questions
        response = self.make_request("GET", f"/users/{self.test_user_id}/questions")
        if response is not None and "questions" in response:
            self.log_test("GET /api/users/{user_id}/questions", True, f"Found {len(response['questions'])} questions")
        else:
            self.log_test("GET /api/users/{user_id}/questions", False, "Failed to get user questions")
        
        # Test 5: Get user answers
        response = self.make_request("GET", f"/users/{self.test_user_id}/answers")
        if response is not None and "answers" in response:
            self.log_test("GET /api/users/{user_id}/answers", True, f"Found {len(response['answers'])} answers")
        else:
            self.log_test("GET /api/users/{user_id}/answers", False, "Failed to get user answers")
        
        # Test 6: Get user quiz attempts
        response = self.make_request("GET", f"/users/{self.test_user_id}/quiz-attempts")
        if response is not None and "quiz_attempts" in response:
            self.log_test("GET /api/users/{user_id}/quiz-attempts", True, f"Found {len(response['quiz_attempts'])} quiz attempts")
        else:
            self.log_test("GET /api/users/{user_id}/quiz-attempts", False, "Failed to get user quiz attempts")
    
    def test_notification_endpoints(self):
        """Test Notification System endpoints"""
        print("\n🔔 Testing Notification System...")
        
        # Test 1: Get user notifications
        response = self.make_request("GET", "/notifications", token=self.user_token)
        if response is not None:
            self.log_test("GET /api/notifications", True, f"Found {len(response)} notifications")
        else:
            self.log_test("GET /api/notifications", False, "Failed to get notifications")
        
        # Test 2: Get notification counts
        response = self.make_request("GET", "/notifications/count", token=self.user_token)
        if response and "total_count" in response and "unread_count" in response:
            self.log_test("GET /api/notifications/count", True, 
                         f"Total: {response['total_count']}, Unread: {response['unread_count']}")
        else:
            self.log_test("GET /api/notifications/count", False, "Failed to get notification counts")
        
        # Test 3: Create a test notification (via helper function)
        # We'll create this by triggering a quiz result notification
        self.create_test_quiz_for_notifications()
        
        # Test 4: Mark all notifications as read
        response = self.make_request("PUT", "/notifications/mark-all-read", token=self.user_token)
        if response and "message" in response:
            self.log_test("PUT /api/notifications/mark-all-read", True, "All notifications marked as read")
        else:
            self.log_test("PUT /api/notifications/mark-all-read", False, "Failed to mark all notifications as read")
    
    def create_test_quiz_for_notifications(self):
        """Create a test quiz and take it to generate notifications"""
        print("\n📝 Creating test quiz for notification testing...")
        
        # Create a simple quiz as admin
        quiz_data = {
            "title": "Notification Test Quiz",
            "description": "A simple quiz to test notification system",
            "category": "Test",
            "subject": "Testing",
            "subcategory": "Notifications",
            "questions": [
                {
                    "question_text": "What is 2 + 2?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True},
                        {"text": "5", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
                }
            ],
            "min_pass_percentage": 60.0
        }
        
        # Create quiz as admin
        response = self.make_request("POST", "/admin/quiz", quiz_data, token=self.admin_token)
        if not response or "id" not in response:
            self.log_test("Quiz Creation for Notifications", False, "Failed to create test quiz")
            return
        
        quiz_id = response["id"]
        
        # Publish the quiz
        response = self.make_request("POST", f"/admin/quiz/{quiz_id}/publish", token=self.admin_token)
        if not response:
            self.log_test("Quiz Publishing for Notifications", False, "Failed to publish test quiz")
            return
        
        # Take the quiz as test user to generate notification
        attempt_data = {
            "quiz_id": quiz_id,
            "answers": ["4"]  # Correct answer
        }
        
        response = self.make_request("POST", f"/quiz/{quiz_id}/attempt", attempt_data, token=self.user_token)
        if response and "id" in response:
            self.log_test("Quiz Attempt for Notifications", True, f"Quiz completed with {response['percentage']}% score")
            
            # Check if notification was created
            time.sleep(1)  # Give time for notification to be created
            notifications = self.make_request("GET", "/notifications", token=self.user_token)
            if notifications:
                quiz_notifications = [n for n in notifications if n.get("type") == "quiz_result"]
                if quiz_notifications:
                    self.log_test("Quiz Result Notification Creation", True, "Quiz result notification created")
                    
                    # Test marking specific notification as read
                    notification_id = quiz_notifications[0]["id"]
                    response = self.make_request("PUT", f"/notifications/{notification_id}/read", token=self.user_token)
                    if response and "message" in response:
                        self.log_test("PUT /api/notifications/{id}/read", True, "Notification marked as read")
                    else:
                        self.log_test("PUT /api/notifications/{id}/read", False, "Failed to mark notification as read")
                    
                    # Test deleting notification
                    response = self.make_request("DELETE", f"/notifications/{notification_id}", token=self.user_token)
                    if response and "message" in response:
                        self.log_test("DELETE /api/notifications/{id}", True, "Notification deleted")
                    else:
                        self.log_test("DELETE /api/notifications/{id}", False, "Failed to delete notification")
                else:
                    self.log_test("Quiz Result Notification Creation", False, "No quiz result notification found")
        else:
            self.log_test("Quiz Attempt for Notifications", False, "Failed to complete quiz")
        
        # Clean up - delete test quiz
        self.make_request("DELETE", f"/admin/quiz/{quiz_id}", token=self.admin_token)
    
    def test_notification_triggers(self):
        """Test automatic notification creation triggers"""
        print("\n🎯 Testing Notification Triggers...")
        
        # We'll test Q&A related notifications by creating questions and answers
        self.test_qa_notifications()
    
    def test_qa_notifications(self):
        """Test Q&A related notification triggers"""
        print("\n❓ Testing Q&A Notification Triggers...")
        
        # Create a question as test user
        question_data = {
            "title": "Test Question for Notifications",
            "content": "This is a test question to verify notification triggers",
            "subject": "Testing",
            "tags": ["test", "notifications"]
        }
        
        response = self.make_request("POST", "/questions", question_data, token=self.user_token)
        if not response or "id" not in response:
            self.log_test("Question Creation for Notifications", False, "Failed to create test question")
            return
        
        question_id = response["id"]
        
        # Answer the question as admin to trigger notification
        answer_data = {
            "content": "This is a test answer to trigger a notification"
        }
        
        response = self.make_request("POST", f"/questions/{question_id}/answers", answer_data, token=self.admin_token)
        if response and "id" in response:
            self.log_test("Answer Creation for Notifications", True, "Answer created successfully")
            answer_id = response["id"]
            
            # Check if notification was created for question author
            time.sleep(1)  # Give time for notification to be created
            notifications = self.make_request("GET", "/notifications", token=self.user_token)
            if notifications:
                answer_notifications = [n for n in notifications if n.get("type") == "new_answer"]
                if answer_notifications:
                    self.log_test("New Answer Notification Trigger", True, "New answer notification created")
                else:
                    self.log_test("New Answer Notification Trigger", False, "No new answer notification found")
            
            # Accept the answer to trigger acceptance notification
            response = self.make_request("PUT", f"/answers/{answer_id}/accept", token=self.user_token)
            if response:
                self.log_test("Answer Acceptance", True, "Answer accepted successfully")
                
                # Check if acceptance notification was created for answer author (admin)
                time.sleep(1)
                admin_notifications = self.make_request("GET", "/notifications", token=self.admin_token)
                if admin_notifications:
                    accept_notifications = [n for n in admin_notifications if n.get("type") == "answer_accepted"]
                    if accept_notifications:
                        self.log_test("Answer Accepted Notification Trigger", True, "Answer accepted notification created")
                    else:
                        self.log_test("Answer Accepted Notification Trigger", False, "No answer accepted notification found")
        else:
            self.log_test("Answer Creation for Notifications", False, "Failed to create test answer")
        
        # Clean up - delete test question
        self.make_request("DELETE", f"/questions/{question_id}", token=self.user_token)
    
    def test_profile_statistics(self):
        """Test profile statistics calculation"""
        print("\n📊 Testing Profile Statistics...")
        
        # Get current profile to check statistics
        profile = self.make_request("GET", "/profile", token=self.user_token)
        if profile:
            stats_fields = ["questions_count", "answers_count", "quizzes_taken", "avg_quiz_score", "accepted_answers"]
            
            # Verify all statistics fields are present
            missing_stats = [field for field in stats_fields if field not in profile]
            if not missing_stats:
                self.log_test("Profile Statistics Fields", True, "All statistics fields present")
                
                # Log current statistics
                stats_summary = {
                    "questions": profile["questions_count"],
                    "answers": profile["answers_count"], 
                    "quizzes_taken": profile["quizzes_taken"],
                    "avg_score": profile["avg_quiz_score"],
                    "accepted_answers": profile["accepted_answers"]
                }
                self.log_test("Profile Statistics Values", True, f"Stats: {stats_summary}")
                
                # Verify statistics are numeric
                numeric_fields = ["questions_count", "answers_count", "quizzes_taken", "avg_quiz_score", "accepted_answers"]
                non_numeric = []
                for field in numeric_fields:
                    if not isinstance(profile[field], (int, float)):
                        non_numeric.append(field)
                
                if not non_numeric:
                    self.log_test("Profile Statistics Data Types", True, "All statistics are numeric")
                else:
                    self.log_test("Profile Statistics Data Types", False, f"Non-numeric fields: {non_numeric}")
            else:
                self.log_test("Profile Statistics Fields", False, f"Missing statistics: {missing_stats}")
        else:
            self.log_test("Profile Statistics Access", False, "Failed to get profile for statistics testing")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive Backend Testing for User Profile and Notification System")
        print("=" * 80)
        
        # Authentication setup
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        if not self.create_test_user():
            print("❌ Cannot proceed without test user")
            return False
        
        # Run all test suites
        self.test_user_profile_endpoints()
        self.test_notification_endpoints()
        self.test_notification_triggers()
        self.test_profile_statistics()
        
        # Print summary
        self.print_test_summary()
        
        return True
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"   • {result['test']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: User Profile and Notification System is working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: User Profile and Notification System is working well with minor issues")
        elif success_rate >= 50:
            print("⚠️  MODERATE: User Profile and Notification System has some issues that need attention")
        else:
            print("❌ CRITICAL: User Profile and Notification System has major issues requiring immediate attention")

def main():
    """Main test execution function"""
    try:
        tester = BackendTester()
        success = tester.run_comprehensive_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)