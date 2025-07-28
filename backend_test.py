#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Q&A Forum System
Tests all endpoints with realistic data and proper authentication flow
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://2180ff4f-7fe0-4fa0-bcfc-6732a8fa0698.preview.emergentagent.com/api"

class QAForumTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.regular_user_id = None
        self.question_id = None
        self.answer_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
    def test_health_check(self):
        """Test basic API health check"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"API is running: {data.get('message', '')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration - both admin and regular user"""
        # Test admin registration
        admin_data = {
            "username": "admin_sarah",
            "email": "admin@squiz.com",
            "full_name": "Sarah Johnson",
            "password": "SecurePass123!"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/register", json=admin_data)
            if response.status_code == 200:
                data = response.json()
                self.admin_user_id = data["id"]
                is_admin = data.get("is_admin", False)
                self.log_test("Admin Registration", True, 
                            f"Admin user created with ID: {self.admin_user_id}, is_admin: {is_admin}")
            elif response.status_code == 400 and "already registered" in response.text:
                # User already exists, that's fine for testing
                self.log_test("Admin Registration", True, 
                            "Admin user already exists (from previous test run)")
            else:
                self.log_test("Admin Registration", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Registration", False, f"Error: {str(e)}")
            return False
        
        # Test regular user registration
        user_data = {
            "username": "student_mike",
            "email": "mike.chen@university.edu",
            "full_name": "Mike Chen",
            "password": "StudentPass456!"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 200:
                data = response.json()
                self.regular_user_id = data["id"]
                is_admin = data.get("is_admin", False)
                self.log_test("Regular User Registration", True, 
                            f"Regular user created with ID: {self.regular_user_id}, is_admin: {is_admin}")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                # User already exists, that's fine for testing
                self.log_test("Regular User Registration", True, 
                            "Regular user already exists (from previous test run)")
                return True
            else:
                self.log_test("Regular User Registration", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Regular User Registration", False, f"Error: {str(e)}")
            return False
    
    def test_user_login(self):
        """Test user login and JWT token generation"""
        # Test admin login
        admin_login = {
            "email": "admin@squiz.com",
            "password": "SecurePass123!"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=admin_login)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                token_type = data.get("token_type", "")
                self.log_test("Admin Login", True, f"Admin token received, type: {token_type}")
                
                # Get admin user ID from /auth/me
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                me_response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    self.admin_user_id = me_data["id"]
            else:
                self.log_test("Admin Login", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, f"Error: {str(e)}")
            return False
        
        # Test regular user login
        user_login = {
            "email": "mike.chen@university.edu",
            "password": "StudentPass456!"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=user_login)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["access_token"]
                token_type = data.get("token_type", "")
                self.log_test("Regular User Login", True, f"User token received, type: {token_type}")
                
                # Get regular user ID from /auth/me
                headers = {"Authorization": f"Bearer {self.user_token}"}
                me_response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    self.regular_user_id = me_data["id"]
                return True
            else:
                self.log_test("Regular User Login", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Regular User Login", False, f"Error: {str(e)}")
            return False
    
    def test_get_current_user(self):
        """Test getting current user info with JWT token"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
            if response.status_code == 200:
                data = response.json()
                username = data.get("username", "")
                is_admin = data.get("is_admin", False)
                self.log_test("Get Current User", True, 
                            f"User info retrieved: {username}, is_admin: {is_admin}")
                return True
            else:
                self.log_test("Get Current User", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Current User", False, f"Error: {str(e)}")
            return False
    
    def test_user_profile_operations(self):
        """Test user profile viewing and updating"""
        # Test getting user profile (public profile should work without auth)
        try:
            response = self.session.get(f"{BASE_URL}/users/{self.admin_user_id}")
            if response.status_code == 200:
                data = response.json()
                username = data.get("username", "")
                self.log_test("Get User Profile", True, f"Profile retrieved for: {username}")
            elif response.status_code == 403:
                # If it requires auth, test with auth
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.get(f"{BASE_URL}/users/{self.admin_user_id}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    username = data.get("username", "")
                    self.log_test("Get User Profile", True, f"Profile retrieved with auth for: {username}")
                else:
                    self.log_test("Get User Profile", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    return False
            else:
                self.log_test("Get User Profile", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get User Profile", False, f"Error: {str(e)}")
            return False
        
        # Test updating user profile
        headers = {"Authorization": f"Bearer {self.user_token}"}
        update_data = {
            "full_name": "Michael Chen",
            "is_private": True
        }
        
        try:
            response = self.session.put(f"{BASE_URL}/users/me", json=update_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                full_name = data.get("full_name", "")
                is_private = data.get("is_private", False)
                self.log_test("Update User Profile", True, 
                            f"Profile updated: {full_name}, private: {is_private}")
                return True
            else:
                self.log_test("Update User Profile", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Update User Profile", False, f"Error: {str(e)}")
            return False
    
    def test_question_operations(self):
        """Test question creation and retrieval"""
        # Test creating a question
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        question_data = {
            "title": "What are the fundamental principles of quantum mechanics?",
            "content": "I'm studying quantum physics and would like to understand the core principles that govern quantum mechanical systems. Can someone explain the key concepts like superposition, entanglement, and wave-particle duality?",
            "category": "Science"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/questions", json=question_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.question_id = data["id"]
                title = data.get("title", "")
                category = data.get("category", "")
                author_is_admin = data.get("author_is_admin", False)
                self.log_test("Create Question", True, 
                            f"Question created: {title[:50]}..., category: {category}, admin: {author_is_admin}")
            else:
                self.log_test("Create Question", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Question", False, f"Error: {str(e)}")
            return False
        
        # Test getting all questions (should work without auth)
        try:
            response = self.session.get(f"{BASE_URL}/questions")
            if response.status_code == 200:
                data = response.json()
                question_count = len(data)
                self.log_test("Get All Questions", True, f"Retrieved {question_count} questions")
            elif response.status_code == 403:
                # If it requires auth, test with auth
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.get(f"{BASE_URL}/questions", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    question_count = len(data)
                    self.log_test("Get All Questions", True, f"Retrieved {question_count} questions with auth")
                else:
                    self.log_test("Get All Questions", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    return False
            else:
                self.log_test("Get All Questions", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get All Questions", False, f"Error: {str(e)}")
            return False
        
        # Test getting specific question (should work without auth)
        try:
            response = self.session.get(f"{BASE_URL}/questions/{self.question_id}")
            if response.status_code == 200:
                data = response.json()
                title = data.get("title", "")
                self.log_test("Get Specific Question", True, f"Question retrieved: {title[:50]}...")
                return True
            elif response.status_code == 403:
                # If it requires auth, test with auth
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.get(f"{BASE_URL}/questions/{self.question_id}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    title = data.get("title", "")
                    self.log_test("Get Specific Question", True, f"Question retrieved with auth: {title[:50]}...")
                    return True
                else:
                    self.log_test("Get Specific Question", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    return False
            else:
                self.log_test("Get Specific Question", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Specific Question", False, f"Error: {str(e)}")
            return False
    
    def test_answer_operations(self):
        """Test answer creation and retrieval"""
        # Test creating an answer
        headers = {"Authorization": f"Bearer {self.user_token}"}
        answer_data = {
            "content": "Quantum mechanics is built on several fundamental principles: 1) Superposition - particles can exist in multiple states simultaneously until measured, 2) Wave-particle duality - matter exhibits both wave and particle properties, 3) Uncertainty principle - you cannot precisely know both position and momentum of a particle, 4) Entanglement - particles can be correlated in ways that seem to defy classical physics. These principles form the foundation of our understanding of the quantum world."
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/questions/{self.question_id}/answers", 
                                       json=answer_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.answer_id = data["id"]
                content = data.get("content", "")
                author_name = data.get("author_name", "")
                self.log_test("Create Answer", True, 
                            f"Answer created by {author_name}: {content[:50]}...")
            else:
                self.log_test("Create Answer", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Answer", False, f"Error: {str(e)}")
            return False
        
        # Test getting answers for a question (should work without auth)
        try:
            response = self.session.get(f"{BASE_URL}/questions/{self.question_id}/answers")
            if response.status_code == 200:
                data = response.json()
                answer_count = len(data)
                self.log_test("Get Question Answers", True, f"Retrieved {answer_count} answers")
                return True
            elif response.status_code == 403:
                # If it requires auth, test with auth
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.get(f"{BASE_URL}/questions/{self.question_id}/answers", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    answer_count = len(data)
                    self.log_test("Get Question Answers", True, f"Retrieved {answer_count} answers with auth")
                    return True
                else:
                    self.log_test("Get Question Answers", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    return False
            else:
                self.log_test("Get Question Answers", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Question Answers", False, f"Error: {str(e)}")
            return False
    
    def test_like_system(self):
        """Test like/unlike functionality for questions and answers"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test liking a question
        try:
            response = self.session.post(f"{BASE_URL}/questions/{self.question_id}/like", headers=headers)
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                self.log_test("Like Question", True, f"Question like result: {message}")
            else:
                self.log_test("Like Question", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Like Question", False, f"Error: {str(e)}")
            return False
        
        # Test liking an answer
        try:
            response = self.session.post(f"{BASE_URL}/answers/{self.answer_id}/like", headers=headers)
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                self.log_test("Like Answer", True, f"Answer like result: {message}")
                return True
            else:
                self.log_test("Like Answer", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Like Answer", False, f"Error: {str(e)}")
            return False
    
    def test_follow_system(self):
        """Test follow/unfollow functionality"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test following the admin user
        try:
            response = self.session.post(f"{BASE_URL}/users/{self.admin_user_id}/follow", headers=headers)
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                self.log_test("Follow User", True, f"Follow result: {message}")
                return True
            else:
                self.log_test("Follow User", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Follow User", False, f"Error: {str(e)}")
            return False
    
    def test_categories(self):
        """Test getting question categories"""
        try:
            response = self.session.get(f"{BASE_URL}/categories")
            if response.status_code == 200:
                data = response.json()
                category_count = len(data)
                categories = [cat.get("name", "") for cat in data]
                self.log_test("Get Categories", True, 
                            f"Retrieved {category_count} categories: {', '.join(categories)}")
                return True
            else:
                self.log_test("Get Categories", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Categories", False, f"Error: {str(e)}")
            return False
    
    def test_user_activity(self):
        """Test getting user's questions and answers"""
        # Test getting user's questions (may require auth for private profiles)
        try:
            response = self.session.get(f"{BASE_URL}/users/{self.admin_user_id}/questions")
            if response.status_code == 200:
                data = response.json()
                question_count = len(data)
                self.log_test("Get User Questions", True, f"User has {question_count} questions")
            elif response.status_code == 403:
                # If it requires auth, test with auth
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.get(f"{BASE_URL}/users/{self.admin_user_id}/questions", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    question_count = len(data)
                    self.log_test("Get User Questions", True, f"User has {question_count} questions with auth")
                else:
                    self.log_test("Get User Questions", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    return False
            else:
                self.log_test("Get User Questions", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get User Questions", False, f"Error: {str(e)}")
            return False
        
        # Test getting user's answers (may require auth for private profiles)
        try:
            response = self.session.get(f"{BASE_URL}/users/{self.regular_user_id}/answers")
            if response.status_code == 200:
                data = response.json()
                answer_count = len(data)
                self.log_test("Get User Answers", True, f"User has {answer_count} answers")
                return True
            elif response.status_code == 403:
                # If it requires auth, test with auth
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BASE_URL}/users/{self.regular_user_id}/answers", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    answer_count = len(data)
                    self.log_test("Get User Answers", True, f"User has {answer_count} answers with auth")
                    return True
                else:
                    self.log_test("Get User Answers", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    return False
            else:
                self.log_test("Get User Answers", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get User Answers", False, f"Error: {str(e)}")
            return False
    
    def test_private_profile_restrictions(self):
        """Test private profile access restrictions"""
        # Try to access private profile without authentication
        try:
            response = self.session.get(f"{BASE_URL}/users/{self.regular_user_id}")
            if response.status_code == 403:
                self.log_test("Private Profile Restriction", True, 
                            "Private profile correctly blocked for unauthenticated access")
                return True
            else:
                self.log_test("Private Profile Restriction", False, 
                            f"Expected 403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Private Profile Restriction", False, f"Error: {str(e)}")
            return False
    
    def test_authentication_required_endpoints(self):
        """Test that protected endpoints require authentication"""
        # Test creating question without auth
        question_data = {
            "title": "Test Question",
            "content": "This should fail",
            "category": "Test"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/questions", json=question_data)
            if response.status_code in [401, 403]:
                self.log_test("Auth Required - Create Question", True, 
                            f"Question creation correctly requires authentication (status: {response.status_code})")
                return True
            else:
                self.log_test("Auth Required - Create Question", False, 
                            f"Expected 401 or 403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Auth Required - Create Question", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 80)
        print("Q&A FORUM BACKEND API TESTING")
        print("=" * 80)
        print(f"Testing against: {BASE_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Run tests in logical order
        tests = [
            self.test_health_check,
            self.test_user_registration,
            self.test_user_login,
            self.test_get_current_user,
            self.test_user_profile_operations,
            self.test_question_operations,
            self.test_answer_operations,
            self.test_like_system,
            self.test_follow_system,
            self.test_categories,
            self.test_user_activity,
            self.test_private_profile_restrictions,
            self.test_authentication_required_endpoints
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Unexpected error: {str(e)}")
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['message']}")
        
        print("=" * 80)
        return passed == total

if __name__ == "__main__":
    tester = QAForumTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)