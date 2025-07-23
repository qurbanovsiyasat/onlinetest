#!/usr/bin/env python3
"""
Backend API Testing for OnlineTestMaker - Admin-Centered Authentication System
Tests all API endpoints with JWT authentication and role-based access control
"""

import requests
import json
import sys
from datetime import datetime
import uuid

class OnlineTestMakerAPITester:
    def __init__(self, base_url="https://f938a643-c3aa-424f-83ea-f4da56ce8f65.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.user_token = None
        self.created_quiz_id = None
        self.test_user_id = str(uuid.uuid4())[:8]

    def log_test(self, test_name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED {details}")
        else:
            print(f"❌ {test_name} - FAILED {details}")
        return success

    def get_auth_headers(self, token):
        """Get authorization headers"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        } if token else {'Content-Type': 'application/json'}

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            return self.log_test("API Root", success, details)
        except Exception as e:
            return self.log_test("API Root", False, f"Error: {str(e)}")

    def test_init_admin(self):
        """Test admin initialization"""
        try:
            response = requests.post(f"{self.api_url}/init-admin", timeout=10)
            # Should succeed (200) or fail if admin exists (400)
            success = response.status_code in [200, 400]
            details = f"Status: {response.status_code}"
            if response.status_code == 200:
                data = response.json()
                details += f", Admin created: {data.get('email', 'Unknown')}"
            elif response.status_code == 400:
                details += ", Admin already exists"
            return self.log_test("Initialize Admin", success, details)
        except Exception as e:
            return self.log_test("Initialize Admin", False, f"Error: {str(e)}")

    def test_admin_login(self):
        """Test admin login"""
        login_data = {
            "email": "admin@onlinetestmaker.com",
            "password": "admin123"
        }
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                self.admin_token = data.get('access_token')
                user_info = data.get('user', {})
                details += f", Role: {user_info.get('role', 'Unknown')}, Name: {user_info.get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Login", success, details)
        except Exception as e:
            return self.log_test("Admin Login", False, f"Error: {str(e)}")

    def test_user_registration(self):
        """Test user registration"""
        user_data = {
            "name": f"Test User {self.test_user_id}",
            "email": f"testuser{self.test_user_id}@example.com",
            "password": "testpass123"
        }
        try:
            response = requests.post(
                f"{self.api_url}/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", User: {data.get('name', 'Unknown')}, Role: {data.get('role', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Registration", success, details)
        except Exception as e:
            return self.log_test("User Registration", False, f"Error: {str(e)}")

    def test_user_login(self):
        """Test user login"""
        login_data = {
            "email": f"testuser{self.test_user_id}@example.com",
            "password": "testpass123"
        }
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                self.user_token = data.get('access_token')
                user_info = data.get('user', {})
                details += f", Role: {user_info.get('role', 'Unknown')}, Name: {user_info.get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Login", success, details)
        except Exception as e:
            return self.log_test("User Login", False, f"Error: {str(e)}")

    def test_auth_me_admin(self):
        """Test /auth/me endpoint with admin token"""
        if not self.admin_token:
            return self.log_test("Auth Me (Admin)", False, "No admin token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/auth/me",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Role: {data.get('role', 'Unknown')}, Email: {data.get('email', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Auth Me (Admin)", success, details)
        except Exception as e:
            return self.log_test("Auth Me (Admin)", False, f"Error: {str(e)}")

    def test_auth_me_user(self):
        """Test /auth/me endpoint with user token"""
        if not self.user_token:
            return self.log_test("Auth Me (User)", False, "No user token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/auth/me",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Role: {data.get('role', 'Unknown')}, Email: {data.get('email', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Auth Me (User)", success, details)
        except Exception as e:
            return self.log_test("Auth Me (User)", False, f"Error: {str(e)}")

    def test_admin_get_users(self):
        """Test admin getting all users"""
        if not self.admin_token:
            return self.log_test("Admin Get Users", False, "No admin token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/users",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                users = response.json()
                details += f", Users Count: {len(users)}"
                admin_count = sum(1 for user in users if user.get('role') == 'admin')
                user_count = sum(1 for user in users if user.get('role') == 'user')
                details += f", Admins: {admin_count}, Users: {user_count}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Get Users", success, details)
        except Exception as e:
            return self.log_test("Admin Get Users", False, f"Error: {str(e)}")

    def test_user_access_admin_endpoint(self):
        """Test user trying to access admin endpoint (should fail)"""
        if not self.user_token:
            return self.log_test("User Access Admin Endpoint", False, "No user token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/users",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            return self.log_test("User Access Admin Endpoint", success, details)
        except Exception as e:
            return self.log_test("User Access Admin Endpoint", False, f"Error: {str(e)}")

    def test_admin_create_category(self):
        """Test admin creating a category"""
        if not self.admin_token:
            return self.log_test("Admin Create Category", False, "No admin token available")
            
        try:
            response = requests.post(
                f"{self.api_url}/admin/category?category_name=Test Category&description=A test category",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Category: {data.get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Category", success, details)
        except Exception as e:
            return self.log_test("Admin Create Category", False, f"Error: {str(e)}")

    def test_admin_create_quiz(self):
        """Test admin creating a quiz"""
        if not self.admin_token:
            return self.log_test("Admin Create Quiz", False, "No admin token available")
            
        quiz_data = {
            "title": "Test Quiz - Admin Created",
            "description": "A test quiz created by admin for testing",
            "category": "Test Category",
            "questions": [
                {
                    "question_text": "What is 2 + 2?",
                    "options": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True},
                        {"text": "5", "is_correct": False},
                        {"text": "6", "is_correct": False}
                    ]
                },
                {
                    "question_text": "What is the capital of France?",
                    "options": [
                        {"text": "London", "is_correct": False},
                        {"text": "Berlin", "is_correct": False},
                        {"text": "Paris", "is_correct": True},
                        {"text": "Madrid", "is_correct": False}
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                f"{self.api_url}/admin/quiz",
                json=quiz_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quiz = response.json()
                self.created_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.created_quiz_id}, Questions: {quiz.get('total_questions', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Quiz", success, details)
        except Exception as e:
            return self.log_test("Admin Create Quiz", False, f"Error: {str(e)}")

    def test_user_create_quiz_forbidden(self):
        """Test user trying to create quiz (should fail)"""
        if not self.user_token:
            return self.log_test("User Create Quiz (Forbidden)", False, "No user token available")
            
        quiz_data = {
            "title": "User Quiz",
            "description": "Should not be allowed",
            "category": "Test",
            "questions": []
        }

        try:
            response = requests.post(
                f"{self.api_url}/admin/quiz",
                json=quiz_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            return self.log_test("User Create Quiz (Forbidden)", success, details)
        except Exception as e:
            return self.log_test("User Create Quiz (Forbidden)", False, f"Error: {str(e)}")

    def test_user_get_quizzes(self):
        """Test user getting available quizzes"""
        if not self.user_token:
            return self.log_test("User Get Quizzes", False, "No user token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/quizzes",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quizzes = response.json()
                details += f", Quizzes Count: {len(quizzes)}"
                if len(quizzes) > 0:
                    details += f", First Quiz: {quizzes[0].get('title', 'No title')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Get Quizzes", success, details)
        except Exception as e:
            return self.log_test("User Get Quizzes", False, f"Error: {str(e)}")

    def test_user_take_quiz(self):
        """Test user taking a quiz"""
        if not self.user_token or not self.created_quiz_id:
            return self.log_test("User Take Quiz", False, "No user token or quiz ID available")

        attempt_data = {
            "quiz_id": self.created_quiz_id,
            "answers": ["4", "Paris"]  # Correct answers
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz/{self.created_quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}, Percentage: {result.get('percentage', 0):.1f}%"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Take Quiz", success, details)
        except Exception as e:
            return self.log_test("User Take Quiz", False, f"Error: {str(e)}")

    def test_admin_take_quiz_forbidden(self):
        """Test admin trying to take quiz (should fail)"""
        if not self.admin_token or not self.created_quiz_id:
            return self.log_test("Admin Take Quiz (Forbidden)", False, "No admin token or quiz ID available")

        attempt_data = {
            "quiz_id": self.created_quiz_id,
            "answers": ["4", "Paris"]
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz/{self.created_quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            return self.log_test("Admin Take Quiz (Forbidden)", success, details)
        except Exception as e:
            return self.log_test("Admin Take Quiz (Forbidden)", False, f"Error: {str(e)}")

    def test_user_get_attempts(self):
        """Test user getting their quiz attempts"""
        if not self.user_token:
            return self.log_test("User Get Attempts", False, "No user token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/my-attempts",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                attempts = response.json()
                details += f", Attempts Count: {len(attempts)}"
                if len(attempts) > 0:
                    details += f", Latest Score: {attempts[-1].get('score', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Get Attempts", success, details)
        except Exception as e:
            return self.log_test("User Get Attempts", False, f"Error: {str(e)}")

    def test_unauthorized_access(self):
        """Test accessing protected endpoints without token"""
        try:
            response = requests.get(f"{self.api_url}/auth/me", timeout=10)
            success = response.status_code == 401  # Should be unauthorized
            details = f"Status: {response.status_code} (Expected 401)"
            return self.log_test("Unauthorized Access", success, details)
        except Exception as e:
            return self.log_test("Unauthorized Access", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting OnlineTestMaker API Tests - Admin-Centered Authentication")
        print(f"🌐 Testing against: {self.api_url}")
        print("=" * 80)

        # Basic connectivity
        self.test_api_root()
        
        # Admin initialization and authentication
        self.test_init_admin()
        self.test_admin_login()
        
        # User registration and authentication
        self.test_user_registration()
        self.test_user_login()
        
        # Authentication verification
        self.test_auth_me_admin()
        self.test_auth_me_user()
        
        # Role-based access control
        self.test_admin_get_users()
        self.test_user_access_admin_endpoint()
        
        # Admin operations
        self.test_admin_create_category()
        self.test_admin_create_quiz()
        self.test_user_create_quiz_forbidden()
        
        # User operations
        self.test_user_get_quizzes()
        self.test_user_take_quiz()
        self.test_admin_take_quiz_forbidden()
        self.test_user_get_attempts()
        
        # Security tests
        self.test_unauthorized_access()

        # Summary
        print("=" * 80)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API with authentication is working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the issues above.")
            return 1

def main():
    """Main test execution"""
    tester = OnlineTestMakerAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())