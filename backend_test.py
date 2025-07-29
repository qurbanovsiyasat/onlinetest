#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Squiz Platform
Tests all critical backend functionality including authentication, quiz management, and admin features.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "admin@squiz.com"
ADMIN_PASSWORD = "admin123"
TEST_USER_EMAIL = "sarah.johnson@example.com"
TEST_USER_PASSWORD = "SecurePass123!"
TEST_USER_NAME = "Sarah Johnson"

class SquizAPITester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_quiz_id = None
        self.test_question_id = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED - {message}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    token: str = None, expected_status: int = 200) -> tuple:
        """Make HTTP request with error handling"""
        url = f"{API_BASE}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            else:
                return False, f"Unsupported method: {method}"
            
            if response.status_code == expected_status:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                return False, f"Expected {expected_status}, got {response.status_code}: {response.text}"
                
        except requests.exceptions.ConnectionError:
            return False, "Connection refused - Backend server not running"
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except Exception as e:
            return False, f"Request error: {str(e)}"
    
    def test_health_check(self):
        """Test /api/health endpoint"""
        print("\n🔍 Testing Health Check...")
        
        success, response = self.make_request("GET", "/health")
        if success and isinstance(response, dict):
            if response.get("status") == "healthy" and response.get("database") == "connected":
                self.log_result("Health Check", True, "Server and database healthy")
            else:
                self.log_result("Health Check", False, f"Unhealthy status: {response}")
        else:
            self.log_result("Health Check", False, str(response))
    
    def test_user_registration(self):
        """Test user registration"""
        print("\n🔍 Testing User Registration...")
        
        user_data = {
            "email": TEST_USER_EMAIL,
            "name": TEST_USER_NAME,
            "password": TEST_USER_PASSWORD
        }
        
        success, response = self.make_request("POST", "/auth/register", user_data, expected_status=200)
        if success and isinstance(response, dict):
            if response.get("email") == TEST_USER_EMAIL and response.get("name") == TEST_USER_NAME:
                self.log_result("User Registration", True, f"User {TEST_USER_NAME} registered successfully")
            else:
                self.log_result("User Registration", False, f"Invalid response: {response}")
        else:
            # Check if user already exists
            if "already registered" in str(response):
                self.log_result("User Registration", True, "User already exists (expected)")
            else:
                self.log_result("User Registration", False, str(response))
    
    def test_admin_login(self):
        """Test admin login"""
        print("\n🔍 Testing Admin Login...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        success, response = self.make_request("POST", "/auth/login", login_data)
        if success and isinstance(response, dict):
            if response.get("access_token") and response.get("user", {}).get("role") == "admin":
                self.admin_token = response["access_token"]
                self.log_result("Admin Login", True, "Admin authenticated successfully")
            else:
                self.log_result("Admin Login", False, f"Invalid login response: {response}")
        else:
            self.log_result("Admin Login", False, str(response))
    
    def test_user_login(self):
        """Test regular user login"""
        print("\n🔍 Testing User Login...")
        
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        success, response = self.make_request("POST", "/auth/login", login_data)
        if success and isinstance(response, dict):
            if response.get("access_token") and response.get("user", {}).get("role") == "user":
                self.user_token = response["access_token"]
                self.log_result("User Login", True, "User authenticated successfully")
            else:
                self.log_result("User Login", False, f"Invalid login response: {response}")
        else:
            self.log_result("User Login", False, str(response))
    
    def test_auth_me_endpoint(self):
        """Test /api/auth/me endpoint"""
        print("\n🔍 Testing Auth Me Endpoint...")
        
        if not self.admin_token:
            self.log_result("Auth Me Endpoint", False, "No admin token available")
            return
        
        success, response = self.make_request("GET", "/auth/me", token=self.admin_token)
        if success and isinstance(response, dict):
            if response.get("email") == ADMIN_EMAIL and response.get("role") == "admin":
                self.log_result("Auth Me Endpoint", True, "User info retrieved successfully")
            else:
                self.log_result("Auth Me Endpoint", False, f"Invalid user info: {response}")
        else:
            self.log_result("Auth Me Endpoint", False, str(response))
    
    def test_jwt_token_validation(self):
        """Test JWT token validation with invalid token"""
        print("\n🔍 Testing JWT Token Validation...")
        
        success, response = self.make_request("GET", "/auth/me", token="invalid_token", expected_status=401)
        if success:
            self.log_result("JWT Token Validation", True, "Invalid token properly rejected")
        else:
            self.log_result("JWT Token Validation", False, str(response))
    
    def test_get_available_quizzes(self):
        """Test getting available quizzes"""
        print("\n🔍 Testing Get Available Quizzes...")
        
        success, response = self.make_request("GET", "/quizzes")
        if success and isinstance(response, list):
            self.log_result("Get Available Quizzes", True, f"Retrieved {len(response)} quizzes")
        else:
            self.log_result("Get Available Quizzes", False, str(response))
    
    def test_quiz_creation(self):
        """Test quiz creation (admin only)"""
        print("\n🔍 Testing Quiz Creation...")
        
        if not self.admin_token:
            self.log_result("Quiz Creation", False, "No admin token available")
            return
        
        quiz_data = {
            "title": "Python Programming Fundamentals",
            "description": "Test your knowledge of Python programming basics",
            "category": "Programming",
            "subject": "Computer Science",
            "subcategory": "Python",
            "is_public": True,
            "min_pass_percentage": 70.0,
            "time_limit_minutes": 30,
            "shuffle_questions": False,
            "shuffle_options": False,
            "questions": [
                {
                    "question_text": "What is the output of print('Hello World')?",
                    "question_type": "multiple_choice",
                    "difficulty": "easy",
                    "points": 1,
                    "options": [
                        {"text": "Hello World", "is_correct": True},
                        {"text": "'Hello World'", "is_correct": False},
                        {"text": "Error", "is_correct": False},
                        {"text": "None", "is_correct": False}
                    ],
                    "explanation": "print() function outputs the string without quotes"
                },
                {
                    "question_text": "Explain the difference between a list and a tuple in Python.",
                    "question_type": "open_ended",
                    "difficulty": "medium",
                    "points": 2,
                    "open_ended_answer": {
                        "expected_answers": [
                            "Lists are mutable, tuples are immutable",
                            "Lists use square brackets, tuples use parentheses"
                        ],
                        "keywords": ["mutable", "immutable", "list", "tuple", "brackets", "parentheses"],
                        "case_sensitive": False,
                        "partial_credit": True
                    },
                    "explanation": "Lists can be modified after creation, tuples cannot"
                }
            ]
        }
        
        success, response = self.make_request("POST", "/admin/quiz", quiz_data, token=self.admin_token)
        if success and isinstance(response, dict):
            if response.get("id") and response.get("title") == quiz_data["title"]:
                self.test_quiz_id = response["id"]
                self.log_result("Quiz Creation", True, f"Quiz created with ID: {self.test_quiz_id}")
            else:
                self.log_result("Quiz Creation", False, f"Invalid quiz creation response: {response}")
        else:
            self.log_result("Quiz Creation", False, str(response))
    
    def test_quiz_publishing(self):
        """Test quiz publishing"""
        print("\n🔍 Testing Quiz Publishing...")
        
        if not self.admin_token or not self.test_quiz_id:
            self.log_result("Quiz Publishing", False, "No admin token or quiz ID available")
            return
        
        success, response = self.make_request("POST", f"/admin/quiz/{self.test_quiz_id}/publish", 
                                            token=self.admin_token)
        if success:
            self.log_result("Quiz Publishing", True, "Quiz published successfully")
        else:
            self.log_result("Quiz Publishing", False, str(response))
    
    def test_quiz_attempt_submission(self):
        """Test quiz attempt submission"""
        print("\n🔍 Testing Quiz Attempt Submission...")
        
        if not self.user_token or not self.test_quiz_id:
            self.log_result("Quiz Attempt Submission", False, "No user token or quiz ID available")
            return
        
        # First get the quiz to see its questions
        success, quiz_response = self.make_request("GET", f"/quiz/{self.test_quiz_id}")
        if not success:
            self.log_result("Quiz Attempt Submission", False, f"Could not retrieve quiz: {quiz_response}")
            return
        
        # Submit answers
        attempt_data = {
            "answers": [
                "Hello World",  # Correct answer for multiple choice
                "Lists are mutable and use square brackets, tuples are immutable and use parentheses"  # Open-ended answer
            ]
        }
        
        success, response = self.make_request("POST", f"/quiz/{self.test_quiz_id}/attempt", 
                                            attempt_data, token=self.user_token)
        if success and isinstance(response, dict):
            if "score" in response and "percentage" in response:
                score = response.get("score", 0)
                percentage = response.get("percentage", 0)
                self.log_result("Quiz Attempt Submission", True, 
                              f"Quiz completed - Score: {score}, Percentage: {percentage:.1f}%")
            else:
                self.log_result("Quiz Attempt Submission", False, f"Invalid attempt response: {response}")
        else:
            self.log_result("Quiz Attempt Submission", False, str(response))
    
    def test_quiz_statistics(self):
        """Test quiz statistics retrieval"""
        print("\n🔍 Testing Quiz Statistics...")
        
        if not self.admin_token:
            self.log_result("Quiz Statistics", False, "No admin token available")
            return
        
        success, response = self.make_request("GET", "/admin/quiz-results", token=self.admin_token)
        if success and isinstance(response, list):
            self.log_result("Quiz Statistics", True, f"Retrieved {len(response)} quiz results")
        else:
            self.log_result("Quiz Statistics", False, str(response))
    
    def test_create_question(self):
        """Test creating a Q&A forum question"""
        print("\n🔍 Testing Q&A Question Creation...")
        
        if not self.user_token:
            self.log_result("Q&A Question Creation", False, "No user token available")
            return
        
        question_data = {
            "title": "How to implement binary search in Python?",
            "content": "I'm struggling with implementing an efficient binary search algorithm. Can someone provide a clear explanation with code examples?",
            "subject": "Computer Science",
            "subcategory": "Algorithms",
            "tags": ["python", "algorithms", "binary-search", "data-structures"]
        }
        
        success, response = self.make_request("POST", "/questions", question_data, token=self.user_token)
        if success and isinstance(response, dict):
            if response.get("id") and response.get("title") == question_data["title"]:
                self.test_question_id = response["id"]
                self.log_result("Q&A Question Creation", True, f"Question created with ID: {self.test_question_id}")
            else:
                self.log_result("Q&A Question Creation", False, f"Invalid question response: {response}")
        else:
            self.log_result("Q&A Question Creation", False, str(response))
    
    def test_get_questions(self):
        """Test getting Q&A forum questions"""
        print("\n🔍 Testing Get Q&A Questions...")
        
        success, response = self.make_request("GET", "/questions")
        if success and isinstance(response, dict):
            if "questions" in response and isinstance(response["questions"], list):
                question_count = len(response["questions"])
                self.log_result("Get Q&A Questions", True, f"Retrieved {question_count} questions")
            else:
                self.log_result("Get Q&A Questions", False, f"Invalid questions response: {response}")
        else:
            self.log_result("Get Q&A Questions", False, str(response))
    
    def test_answer_question(self):
        """Test answering a Q&A forum question"""
        print("\n🔍 Testing Q&A Answer Creation...")
        
        if not self.user_token or not self.test_question_id:
            self.log_result("Q&A Answer Creation", False, "No user token or question ID available")
            return
        
        answer_data = {
            "content": """Here's a clean implementation of binary search in Python:

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Target not found
```

The key points are:
1. Array must be sorted
2. Compare with middle element
3. Narrow search space by half each iteration
4. Time complexity: O(log n)"""
        }
        
        success, response = self.make_request("POST", f"/questions/{self.test_question_id}/answers", 
                                            answer_data, token=self.user_token)
        if success and isinstance(response, dict):
            if response.get("id") and response.get("content"):
                self.log_result("Q&A Answer Creation", True, "Answer created successfully")
            else:
                self.log_result("Q&A Answer Creation", False, f"Invalid answer response: {response}")
        else:
            self.log_result("Q&A Answer Creation", False, str(response))
    
    def test_admin_get_users(self):
        """Test admin endpoint to get all users"""
        print("\n🔍 Testing Admin Get Users...")
        
        if not self.admin_token:
            self.log_result("Admin Get Users", False, "No admin token available")
            return
        
        success, response = self.make_request("GET", "/admin/users", token=self.admin_token)
        if success and isinstance(response, list):
            user_count = len(response)
            admin_users = [u for u in response if u.get("role") == "admin"]
            regular_users = [u for u in response if u.get("role") == "user"]
            self.log_result("Admin Get Users", True, 
                          f"Retrieved {user_count} users ({len(admin_users)} admin, {len(regular_users)} regular)")
        else:
            self.log_result("Admin Get Users", False, str(response))
    
    def test_admin_analytics(self):
        """Test admin analytics endpoint"""
        print("\n🔍 Testing Admin Analytics...")
        
        if not self.admin_token:
            self.log_result("Admin Analytics", False, "No admin token available")
            return
        
        success, response = self.make_request("GET", "/admin/analytics", token=self.admin_token)
        if success and isinstance(response, dict):
            required_fields = ["total_users", "total_quizzes", "total_attempts", "average_score"]
            if all(field in response for field in required_fields):
                self.log_result("Admin Analytics", True, 
                              f"Analytics: {response['total_users']} users, {response['total_quizzes']} quizzes, "
                              f"{response['total_attempts']} attempts, {response['average_score']}% avg score")
            else:
                self.log_result("Admin Analytics", False, f"Missing analytics fields: {response}")
        else:
            self.log_result("Admin Analytics", False, str(response))
    
    def test_admin_dashboard_data(self):
        """Test admin dashboard data endpoints"""
        print("\n🔍 Testing Admin Dashboard Data...")
        
        if not self.admin_token:
            self.log_result("Admin Dashboard Data", False, "No admin token available")
            return
        
        # Test getting all quizzes for admin
        success, response = self.make_request("GET", "/admin/quizzes", token=self.admin_token)
        if success and isinstance(response, list):
            self.log_result("Admin Dashboard Data", True, f"Retrieved {len(response)} admin quizzes")
        else:
            self.log_result("Admin Dashboard Data", False, str(response))
    
    def test_unauthorized_access(self):
        """Test that admin endpoints reject non-admin users"""
        print("\n🔍 Testing Unauthorized Access Protection...")
        
        if not self.user_token:
            self.log_result("Unauthorized Access Protection", False, "No user token available")
            return
        
        # Try to access admin endpoint with regular user token
        success, response = self.make_request("GET", "/admin/users", token=self.user_token, expected_status=403)
        if success:
            self.log_result("Unauthorized Access Protection", True, "Admin endpoint properly protected")
        else:
            self.log_result("Unauthorized Access Protection", False, str(response))
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Squiz Platform Backend API Tests")
        print("=" * 60)
        
        # Health and basic connectivity
        self.test_health_check()
        
        # Authentication tests
        self.test_user_registration()
        self.test_admin_login()
        self.test_user_login()
        self.test_auth_me_endpoint()
        self.test_jwt_token_validation()
        
        # Quiz management tests
        self.test_get_available_quizzes()
        self.test_quiz_creation()
        self.test_quiz_publishing()
        self.test_quiz_attempt_submission()
        self.test_quiz_statistics()
        
        # Q&A Forum tests
        self.test_create_question()
        self.test_get_questions()
        self.test_answer_question()
        
        # Admin tests
        self.test_admin_get_users()
        self.test_admin_analytics()
        self.test_admin_dashboard_data()
        
        # Security tests
        self.test_unauthorized_access()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print(f"\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 Excellent! Backend API is working well.")
        elif success_rate >= 75:
            print("✅ Good! Most functionality is working.")
        elif success_rate >= 50:
            print("⚠️  Warning! Several issues need attention.")
        else:
            print("🚨 Critical! Major issues found.")
        
        return self.results

if __name__ == "__main__":
    tester = SquizAPITester()
    results = tester.run_all_tests()