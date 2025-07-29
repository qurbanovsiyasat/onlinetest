#!/usr/bin/env python3
"""
Phase 2 Admin Visual Distinction Backend Testing
Testing Priority: HIGH

This script tests the backend APIs to ensure all functionality is working correctly 
after Phase 2 admin visual distinction enhancements, focusing on:

1. Authentication system (login/register) with proper role information
2. Q&A system with admin and user roles
3. Quiz management and taking functionality
4. Activity feed system
5. User profile management
6. Admin vs user role distinctions in data responses

The backend should return proper user role information so the frontend can display 
admin badges and enhanced visual distinctions.
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
TEST_USER_EMAIL = "phase2test@example.com"
TEST_USER_PASSWORD = "password123"

class Phase2AdminBackendTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.admin_user_id = None
        self.test_user_id = None
        self.created_quiz_id = None
        self.created_question_id = None
    
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
    
    def test_authentication_system(self):
        """Test authentication system with proper role information"""
        print("\n🔐 Testing Authentication System with Role Information...")
        
        # Test 1: Admin Login
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and "access_token" in response and "user" in response:
            self.admin_token = response["access_token"]
            admin_user = response["user"]
            self.admin_user_id = admin_user["id"]
            
            # Verify admin role information
            if admin_user.get("role") == "admin":
                self.log_test("Admin Login with Role Info", True, 
                             f"Admin authenticated successfully. Role: {admin_user['role']}, ID: {self.admin_user_id}")
            else:
                self.log_test("Admin Login with Role Info", False, 
                             f"Admin role not properly returned. Got: {admin_user.get('role')}")
        else:
            self.log_test("Admin Login with Role Info", False, "Failed to authenticate admin")
            return False
        
        # Test 2: User Registration
        register_data = {
            "email": TEST_USER_EMAIL,
            "name": "Phase 2 Test User",
            "password": TEST_USER_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/register", register_data)
        if response and "role" in response:
            if response.get("role") == "user":
                self.log_test("User Registration with Role Info", True, 
                             f"User registered successfully. Role: {response['role']}")
            else:
                self.log_test("User Registration with Role Info", False, 
                             f"User role not properly set. Got: {response.get('role')}")
        else:
            # User might already exist, try login
            print("   User might already exist, trying login...")
        
        # Test 3: User Login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and "access_token" in response and "user" in response:
            self.user_token = response["access_token"]
            user_data = response["user"]
            self.test_user_id = user_data["id"]
            
            # Verify user role information
            if user_data.get("role") == "user":
                self.log_test("User Login with Role Info", True, 
                             f"User authenticated successfully. Role: {user_data['role']}, ID: {self.test_user_id}")
            else:
                self.log_test("User Login with Role Info", False, 
                             f"User role not properly returned. Got: {user_data.get('role')}")
        else:
            self.log_test("User Login with Role Info", False, "Failed to authenticate user")
            return False
        
        # Test 4: Auth Me Endpoint for Admin
        response = self.make_request("GET", "/auth/me", token=self.admin_token)
        if response and response.get("role") == "admin":
            self.log_test("Admin Auth Me Endpoint", True, 
                         f"Admin role properly returned: {response['role']}")
        else:
            self.log_test("Admin Auth Me Endpoint", False, 
                         f"Admin role not properly returned. Got: {response.get('role') if response else 'No response'}")
        
        # Test 5: Auth Me Endpoint for User
        response = self.make_request("GET", "/auth/me", token=self.user_token)
        if response and response.get("role") == "user":
            self.log_test("User Auth Me Endpoint", True, 
                         f"User role properly returned: {response['role']}")
        else:
            self.log_test("User Auth Me Endpoint", False, 
                         f"User role not properly returned. Got: {response.get('role') if response else 'No response'}")
        
        return True
    
    def test_quiz_management_with_roles(self):
        """Test quiz management functionality with admin/user role distinctions"""
        print("\n📝 Testing Quiz Management with Role Distinctions...")
        
        # Test 1: Admin Quiz Creation
        quiz_data = {
            "title": "Phase 2 Admin Test Quiz",
            "description": "Testing admin quiz creation with role distinctions",
            "category": "Testing",
            "subject": "Phase2Testing",
            "subcategory": "AdminRoles",
            "questions": [
                {
                    "question_text": "What is the role of an admin?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "Manage quizzes", "is_correct": True},
                        {"text": "Take quizzes", "is_correct": False},
                        {"text": "Only view content", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
                }
            ],
            "min_pass_percentage": 60.0
        }
        
        response = self.make_request("POST", "/admin/quiz", quiz_data, token=self.admin_token)
        if response and "id" in response:
            self.created_quiz_id = response["id"]
            
            # Verify admin ownership fields
            if (response.get("quiz_owner_type") == "admin" and 
                response.get("quiz_owner_id") == self.admin_user_id and
                response.get("created_by") == self.admin_user_id):
                self.log_test("Admin Quiz Creation with Ownership", True, 
                             f"Quiz created with proper admin ownership. ID: {self.created_quiz_id}")
            else:
                self.log_test("Admin Quiz Creation with Ownership", False, 
                             f"Admin ownership not properly set. Owner type: {response.get('quiz_owner_type')}")
        else:
            self.log_test("Admin Quiz Creation with Ownership", False, "Failed to create admin quiz")
            return False
        
        # Test 2: Admin Quiz List (should show all quizzes with ownership info)
        response = self.make_request("GET", "/admin/quizzes", token=self.admin_token)
        if response and isinstance(response, list):
            admin_quizzes = [q for q in response if q.get("quiz_owner_type") == "admin"]
            user_quizzes = [q for q in response if q.get("quiz_owner_type") == "user"]
            
            self.log_test("Admin Quiz List with Ownership Info", True, 
                         f"Found {len(admin_quizzes)} admin quizzes, {len(user_quizzes)} user quizzes")
            
            # Verify our created quiz is in the list
            our_quiz = next((q for q in response if q.get("id") == self.created_quiz_id), None)
            if our_quiz and our_quiz.get("quiz_owner_type") == "admin":
                self.log_test("Created Quiz in Admin List", True, "Created quiz found with admin ownership")
            else:
                self.log_test("Created Quiz in Admin List", False, "Created quiz not found or ownership incorrect")
        else:
            self.log_test("Admin Quiz List with Ownership Info", False, "Failed to get admin quiz list")
        
        # Test 3: Publish Quiz (Admin only)
        response = self.make_request("POST", f"/admin/quiz/{self.created_quiz_id}/publish", token=self.admin_token)
        if response and "message" in response:
            self.log_test("Admin Quiz Publishing", True, "Quiz published successfully by admin")
        else:
            self.log_test("Admin Quiz Publishing", False, "Failed to publish quiz as admin")
        
        # Test 4: User Quiz List (should only show published quizzes, no ownership details for security)
        response = self.make_request("GET", "/quizzes", token=self.user_token)
        if response and isinstance(response, list):
            # Find our published quiz
            our_quiz = next((q for q in response if q.get("id") == self.created_quiz_id), None)
            if our_quiz:
                # Verify quiz is accessible to users but ownership info is present for frontend admin badges
                if "quiz_owner_type" in our_quiz:
                    self.log_test("User Quiz List with Admin Indicators", True, 
                                 f"Quiz accessible to users with admin indicator: {our_quiz.get('quiz_owner_type')}")
                else:
                    self.log_test("User Quiz List with Admin Indicators", False, 
                                 "Quiz accessible but missing admin indicator for frontend badges")
            else:
                self.log_test("User Quiz List Access", False, "Published quiz not accessible to users")
        else:
            self.log_test("User Quiz List Access", False, "Failed to get user quiz list")
        
        # Test 5: User Cannot Access Admin Quiz Management
        response = self.make_request("GET", "/admin/quizzes", token=self.user_token, expected_status=403)
        if response is None:  # Expected 403 error
            self.log_test("User Admin Access Restriction", True, "User properly blocked from admin quiz management")
        else:
            self.log_test("User Admin Access Restriction", False, "User incorrectly allowed admin access")
        
        return True
    
    def test_qa_system_with_roles(self):
        """Test Q&A system with admin and user role distinctions"""
        print("\n❓ Testing Q&A System with Role Distinctions...")
        
        # Test 1: User Creates Question
        question_data = {
            "title": "Phase 2 Role Testing Question",
            "content": "How do admin badges work in the frontend?",
            "subject": "Phase2Testing",
            "tags": ["admin", "roles", "testing"]
        }
        
        response = self.make_request("POST", "/questions", question_data, token=self.user_token)
        if response and "id" in response:
            self.created_question_id = response["id"]
            
            # Verify question creation with user info
            if response.get("user_id") == self.test_user_id:
                self.log_test("User Question Creation", True, 
                             f"Question created by user. ID: {self.created_question_id}")
            else:
                self.log_test("User Question Creation", False, 
                             f"Question user_id incorrect. Expected: {self.test_user_id}, Got: {response.get('user_id')}")
        else:
            self.log_test("User Question Creation", False, "Failed to create question as user")
            return False
        
        # Test 2: Get Questions List with User Role Info
        response = self.make_request("GET", "/questions", token=self.admin_token)
        if response and "questions" in response:
            questions = response["questions"]
            our_question = next((q for q in questions if q.get("id") == self.created_question_id), None)
            
            if our_question:
                # Check if user information is available for admin to see role distinctions
                if "user_id" in our_question:
                    self.log_test("Questions List with User Info", True, 
                                 "Questions include user information for role distinctions")
                else:
                    self.log_test("Questions List with User Info", False, 
                                 "Questions missing user information for role distinctions")
            else:
                self.log_test("Questions List Access", False, "Created question not found in list")
        else:
            self.log_test("Questions List Access", False, "Failed to get questions list")
        
        # Test 3: Admin Answers Question
        answer_data = {
            "content": "Admin badges are displayed based on the user role information returned by the backend APIs."
        }
        
        response = self.make_request("POST", f"/questions/{self.created_question_id}/answers", 
                                   answer_data, token=self.admin_token)
        if response and "id" in response:
            answer_id = response["id"]
            
            # Verify admin answer with role info
            if response.get("user_id") == self.admin_user_id:
                self.log_test("Admin Answer Creation", True, 
                             f"Answer created by admin. ID: {answer_id}")
            else:
                self.log_test("Admin Answer Creation", False, 
                             f"Answer user_id incorrect. Expected: {self.admin_user_id}, Got: {response.get('user_id')}")
        else:
            self.log_test("Admin Answer Creation", False, "Failed to create answer as admin")
        
        # Test 4: Get Question Details with Answer Role Info
        response = self.make_request("GET", f"/questions/{self.created_question_id}", token=self.user_token)
        if response and "answers" in response:
            answers = response["answers"]
            if answers:
                admin_answer = answers[0]  # Should be our admin answer
                
                # Verify answer includes user info for role distinction
                if "user_id" in admin_answer:
                    self.log_test("Question Details with Answer Role Info", True, 
                                 "Question details include answer user info for role distinctions")
                else:
                    self.log_test("Question Details with Answer Role Info", False, 
                                 "Question details missing answer user info for role distinctions")
            else:
                self.log_test("Question Answers Access", False, "No answers found for question")
        else:
            self.log_test("Question Details Access", False, "Failed to get question details")
        
        # Test 5: Admin Pin Question (Admin-only feature)
        response = self.make_request("PUT", f"/admin/questions/{self.created_question_id}/pin", 
                                   token=self.admin_token)
        if response and "message" in response:
            self.log_test("Admin Pin Question", True, "Admin successfully pinned question")
        else:
            self.log_test("Admin Pin Question", False, "Failed to pin question as admin")
        
        # Test 6: User Cannot Pin Question
        response = self.make_request("PUT", f"/admin/questions/{self.created_question_id}/pin", 
                                   token=self.user_token, expected_status=403)
        if response is None:  # Expected 403 error
            self.log_test("User Pin Question Restriction", True, "User properly blocked from pinning questions")
        else:
            self.log_test("User Pin Question Restriction", False, "User incorrectly allowed to pin questions")
        
        return True
    
    def test_activity_feed_with_roles(self):
        """Test activity feed system with role distinctions"""
        print("\n📱 Testing Activity Feed with Role Distinctions...")
        
        # Test 1: Get Activity Feed
        response = self.make_request("GET", "/user/activity-feed", token=self.user_token)
        if response and "activities" in response:
            activities = response["activities"]
            
            # Check if activities include user role information for frontend badges
            if activities:
                sample_activity = activities[0]
                # Activities should include user information for role distinctions
                if "user_id" in sample_activity or "from_user_id" in sample_activity:
                    self.log_test("Activity Feed with User Info", True, 
                                 f"Activity feed includes user info for role distinctions. Found {len(activities)} activities")
                else:
                    self.log_test("Activity Feed with User Info", False, 
                                 "Activity feed missing user info for role distinctions")
            else:
                self.log_test("Activity Feed Access", True, "Activity feed accessible (empty)")
        else:
            self.log_test("Activity Feed Access", False, "Failed to get activity feed")
        
        # Test 2: Admin Activity Feed Access
        response = self.make_request("GET", "/user/activity-feed", token=self.admin_token)
        if response and "activities" in response:
            self.log_test("Admin Activity Feed Access", True, 
                         f"Admin can access activity feed. Found {len(response['activities'])} activities")
        else:
            self.log_test("Admin Activity Feed Access", False, "Admin failed to access activity feed")
        
        return True
    
    def test_user_profile_with_roles(self):
        """Test user profile management with role distinctions"""
        print("\n👤 Testing User Profile with Role Distinctions...")
        
        # Test 1: Get User Profile (should include role info)
        response = self.make_request("GET", "/profile", token=self.user_token)
        if response and "role" in response:
            if response.get("role") == "user":
                self.log_test("User Profile with Role Info", True, 
                             f"User profile includes role: {response['role']}")
            else:
                self.log_test("User Profile with Role Info", False, 
                             f"User profile role incorrect. Expected: user, Got: {response.get('role')}")
        else:
            self.log_test("User Profile with Role Info", False, "User profile missing role information")
        
        # Test 2: Get Admin Profile (should include admin role)
        response = self.make_request("GET", "/profile", token=self.admin_token)
        if response and "role" in response:
            if response.get("role") == "admin":
                self.log_test("Admin Profile with Role Info", True, 
                             f"Admin profile includes role: {response['role']}")
            else:
                self.log_test("Admin Profile with Role Info", False, 
                             f"Admin profile role incorrect. Expected: admin, Got: {response.get('role')}")
        else:
            self.log_test("Admin Profile with Role Info", False, "Admin profile missing role information")
        
        # Test 3: Get Public User Profile (should include role for admin badges)
        response = self.make_request("GET", f"/users/{self.test_user_id}/profile", token=self.admin_token)
        if response and "role" in response:
            self.log_test("Public Profile with Role Info", True, 
                         f"Public profile includes role info for badges: {response['role']}")
        else:
            self.log_test("Public Profile with Role Info", False, 
                         "Public profile missing role info for admin badges")
        
        # Test 4: Admin Users List (should show all users with roles)
        response = self.make_request("GET", "/admin/users", token=self.admin_token)
        if response and isinstance(response, list):
            admin_users = [u for u in response if u.get("role") == "admin"]
            regular_users = [u for u in response if u.get("role") == "user"]
            
            self.log_test("Admin Users List with Roles", True, 
                         f"Found {len(admin_users)} admins, {len(regular_users)} users")
        else:
            self.log_test("Admin Users List with Roles", False, "Failed to get admin users list")
        
        # Test 5: User Cannot Access Admin Users List
        response = self.make_request("GET", "/admin/users", token=self.user_token, expected_status=403)
        if response is None:  # Expected 403 error
            self.log_test("User Admin Users Access Restriction", True, "User properly blocked from admin users list")
        else:
            self.log_test("User Admin Users Access Restriction", False, "User incorrectly allowed admin users access")
        
        return True
    
    def test_quiz_taking_with_role_restrictions(self):
        """Test quiz taking functionality with role restrictions"""
        print("\n🎯 Testing Quiz Taking with Role Restrictions...")
        
        if not self.created_quiz_id:
            self.log_test("Quiz Taking Test Setup", False, "No quiz available for testing")
            return False
        
        # Test 1: User Can Take Quiz
        attempt_data = {
            "quiz_id": self.created_quiz_id,
            "answers": ["Manage quizzes"]  # Correct answer
        }
        
        response = self.make_request("POST", f"/quiz/{self.created_quiz_id}/attempt", 
                                   attempt_data, token=self.user_token)
        if response and "id" in response:
            attempt_id = response["id"]
            
            # Verify attempt includes user info
            if response.get("user_id") == self.test_user_id:
                self.log_test("User Quiz Attempt", True, 
                             f"User successfully took quiz. Score: {response.get('percentage', 0)}%")
            else:
                self.log_test("User Quiz Attempt", False, 
                             f"Quiz attempt user_id incorrect. Expected: {self.test_user_id}")
        else:
            self.log_test("User Quiz Attempt", False, "User failed to take quiz")
        
        # Test 2: Admin Cannot Take Quiz (should be restricted)
        response = self.make_request("POST", f"/quiz/{self.created_quiz_id}/attempt", 
                                   attempt_data, token=self.admin_token, expected_status=403)
        if response is None:  # Expected 403 error
            self.log_test("Admin Quiz Taking Restriction", True, "Admin properly blocked from taking quizzes")
        else:
            self.log_test("Admin Quiz Taking Restriction", False, "Admin incorrectly allowed to take quizzes")
        
        # Test 3: Admin Can View Quiz Results with User Role Info
        response = self.make_request("GET", f"/admin/quiz-results", token=self.admin_token)
        if response and isinstance(response, list):
            if response:
                result = response[0]
                # Verify results include user info for admin to see role distinctions
                if "user_id" in result:
                    self.log_test("Admin Quiz Results with User Info", True, 
                                 "Quiz results include user info for role distinctions")
                else:
                    self.log_test("Admin Quiz Results with User Info", False, 
                                 "Quiz results missing user info for role distinctions")
            else:
                self.log_test("Admin Quiz Results Access", True, "Admin can access quiz results (empty)")
        else:
            self.log_test("Admin Quiz Results Access", False, "Admin failed to access quiz results")
        
        return True
    
    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete created quiz
        if self.created_quiz_id:
            response = self.make_request("DELETE", f"/admin/quiz/{self.created_quiz_id}", 
                                       token=self.admin_token)
            if response:
                self.log_test("Quiz Cleanup", True, "Test quiz deleted successfully")
            else:
                self.log_test("Quiz Cleanup", False, "Failed to delete test quiz")
        
        # Delete created question
        if self.created_question_id:
            response = self.make_request("DELETE", f"/questions/{self.created_question_id}", 
                                       token=self.user_token)
            if response:
                self.log_test("Question Cleanup", True, "Test question deleted successfully")
            else:
                self.log_test("Question Cleanup", False, "Failed to delete test question")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive Phase 2 admin backend tests"""
        print("🚀 Starting Phase 2 Admin Visual Distinction Backend Testing")
        print("=" * 80)
        
        # Test authentication first
        if not self.test_authentication_system():
            print("❌ Cannot proceed without proper authentication")
            return False
        
        # Run all test suites
        self.test_quiz_management_with_roles()
        self.test_qa_system_with_roles()
        self.test_activity_feed_with_roles()
        self.test_user_profile_with_roles()
        self.test_quiz_taking_with_role_restrictions()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print summary
        self.print_test_summary()
        
        return True
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 PHASE 2 ADMIN BACKEND TEST SUMMARY")
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
            print("🎉 EXCELLENT: Phase 2 Admin Backend APIs are working excellently!")
            print("   All functionality working correctly with proper admin role distinctions.")
        elif success_rate >= 75:
            print("✅ GOOD: Phase 2 Admin Backend APIs are working well with minor issues")
            print("   Most functionality working with proper role distinctions.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Phase 2 Admin Backend APIs have some issues that need attention")
            print("   Some role distinction features may not be working properly.")
        else:
            print("❌ CRITICAL: Phase 2 Admin Backend APIs have major issues requiring immediate attention")
            print("   Admin role distinctions may not be working correctly.")

def main():
    """Main test execution function"""
    try:
        tester = Phase2AdminBackendTester()
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