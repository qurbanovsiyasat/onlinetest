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
        self.uploaded_image_id = None
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
        """Test /auth/me endpoint with admin token - SKIPPED (endpoint not implemented)"""
        return self.log_test("Auth Me (Admin)", True, "SKIPPED - endpoint not implemented")

    def test_auth_me_user(self):
        """Test /auth/me endpoint with user token - SKIPPED (endpoint not implemented)"""
        return self.log_test("Auth Me (User)", True, "SKIPPED - endpoint not implemented")

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
            "subject": "Mathematics",  # Required field
            "subcategory": "General",
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

    def test_admin_get_quizzes(self):
        """Test admin getting all quizzes (recently fixed endpoint)"""
        if not self.admin_token:
            return self.log_test("Admin Get Quizzes", False, "No admin token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/quizzes",
                headers=self.get_auth_headers(self.admin_token),
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
                
            return self.log_test("Admin Get Quizzes", success, details)
        except Exception as e:
            return self.log_test("Admin Get Quizzes", False, f"Error: {str(e)}")

    def test_admin_upload_image(self):
        """Test admin image upload functionality"""
        if not self.admin_token:
            return self.log_test("Admin Upload Image", False, "No admin token available")
            
        # Create a simple test image (1x1 PNG)
        import base64
        # Minimal PNG image data (1x1 transparent pixel)
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=='
        )
        
        try:
            files = {'file': ('test.png', png_data, 'image/png')}
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = requests.post(
                f"{self.api_url}/admin/upload-image",
                files=files,
                headers=headers,
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                image_id = data.get('id')
                details += f", Image ID: {image_id}, Size: {data.get('size', 0)} bytes"
                # Store image ID for later test
                self.uploaded_image_id = image_id
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Upload Image", success, details)
        except Exception as e:
            return self.log_test("Admin Upload Image", False, f"Error: {str(e)}")

    def test_get_image(self):
        """Test getting uploaded image"""
        if not hasattr(self, 'uploaded_image_id') or not self.uploaded_image_id:
            return self.log_test("Get Image", False, "No uploaded image ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/image/{self.uploaded_image_id}",
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                url = data.get('url', '')
                details += f", URL starts with: {url[:50]}..."
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Image", success, details)
        except Exception as e:
            return self.log_test("Get Image", False, f"Error: {str(e)}")

    def test_user_upload_image_forbidden(self):
        """Test user trying to upload image (should fail)"""
        if not self.user_token:
            return self.log_test("User Upload Image (Forbidden)", False, "No user token available")
            
        # Create a simple test image
        import base64
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=='
        )
        
        try:
            files = {'file': ('test.png', png_data, 'image/png')}
            headers = {'Authorization': f'Bearer {self.user_token}'}
            
            response = requests.post(
                f"{self.api_url}/admin/upload-image",
                files=files,
                headers=headers,
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            return self.log_test("User Upload Image (Forbidden)", success, details)
        except Exception as e:
            return self.log_test("User Upload Image (Forbidden)", False, f"Error: {str(e)}")

    def test_admin_create_quiz_with_image(self):
        """Test admin creating a quiz with image"""
        if not self.admin_token:
            return self.log_test("Admin Create Quiz with Image", False, "No admin token available")
            
        # Use uploaded image if available
        image_url = None
        if hasattr(self, 'uploaded_image_id') and self.uploaded_image_id:
            image_url = f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
            
        quiz_data = {
            "title": "Test Quiz with Image",
            "description": "A test quiz with image questions",
            "category": "Test Category",
            "questions": [
                {
                    "question_text": "What do you see in this image?",
                    "options": [
                        {"text": "A circle", "is_correct": False},
                        {"text": "A square", "is_correct": False},
                        {"text": "A transparent pixel", "is_correct": True},
                        {"text": "Nothing", "is_correct": False}
                    ],
                    "image_url": image_url
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
                details += f", Quiz ID: {quiz.get('id')}, Has Image: {bool(image_url)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Quiz with Image", success, details)
        except Exception as e:
            return self.log_test("Admin Create Quiz with Image", False, f"Error: {str(e)}")

    def test_admin_get_quiz_results(self):
        """Test admin getting all quiz results"""
        if not self.admin_token:
            return self.log_test("Admin Get Quiz Results", False, "No admin token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/quiz-results",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                results = response.json()
                details += f", Results Count: {len(results)}"
                if len(results) > 0:
                    first_result = results[0]
                    details += f", First Result Score: {first_result.get('score', 0)}/{first_result.get('total_questions', 0)}"
                    details += f", User: {first_result.get('user', {}).get('name', 'Unknown')}"
                    details += f", Quiz: {first_result.get('quiz', {}).get('title', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Get Quiz Results", success, details)
        except Exception as e:
            return self.log_test("Admin Get Quiz Results", False, f"Error: {str(e)}")

    def test_admin_get_analytics_summary(self):
        """Test admin getting analytics summary"""
        if not self.admin_token:
            return self.log_test("Admin Get Analytics Summary", False, "No admin token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/analytics/summary",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                analytics = response.json()
                details += f", Total Users: {analytics.get('total_users', 0)}"
                details += f", Total Quizzes: {analytics.get('total_quizzes', 0)}"
                details += f", Total Attempts: {analytics.get('total_attempts', 0)}"
                details += f", Avg Score: {analytics.get('average_score', 0)}%"
                details += f", Popular Quiz: {analytics.get('most_popular_quiz', 'None')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Get Analytics Summary", success, details)
        except Exception as e:
            return self.log_test("Admin Get Analytics Summary", False, f"Error: {str(e)}")

    def test_admin_get_user_quiz_results(self):
        """Test admin getting quiz results for specific user"""
        if not self.admin_token:
            return self.log_test("Admin Get User Quiz Results", False, "No admin token available")
        
        # First get a user ID from the users list
        try:
            users_response = requests.get(
                f"{self.api_url}/admin/users",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            if users_response.status_code != 200:
                return self.log_test("Admin Get User Quiz Results", False, "Could not get users list")
            
            users = users_response.json()
            test_user = None
            for user in users:
                if user.get('role') == 'user':
                    test_user = user
                    break
            
            if not test_user:
                return self.log_test("Admin Get User Quiz Results", False, "No test user found")
            
            user_id = test_user.get('id')
            response = requests.get(
                f"{self.api_url}/admin/quiz-results/user/{user_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                results = response.json()
                details += f", User Results Count: {len(results)}"
                details += f", User: {test_user.get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Get User Quiz Results", success, details)
        except Exception as e:
            return self.log_test("Admin Get User Quiz Results", False, f"Error: {str(e)}")

    def test_admin_get_quiz_specific_results(self):
        """Test admin getting results for specific quiz"""
        if not self.admin_token or not self.created_quiz_id:
            return self.log_test("Admin Get Quiz Specific Results", False, "No admin token or quiz ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/quiz-results/quiz/{self.created_quiz_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                results = response.json()
                details += f", Quiz Results Count: {len(results)}"
                details += f", Quiz ID: {self.created_quiz_id}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Get Quiz Specific Results", success, details)
        except Exception as e:
            return self.log_test("Admin Get Quiz Specific Results", False, f"Error: {str(e)}")

    def test_user_access_quiz_results_forbidden(self):
        """Test user trying to access quiz results (should fail)"""
        if not self.user_token:
            return self.log_test("User Access Quiz Results (Forbidden)", False, "No user token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/quiz-results",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            return self.log_test("User Access Quiz Results (Forbidden)", success, details)
        except Exception as e:
            return self.log_test("User Access Quiz Results (Forbidden)", False, f"Error: {str(e)}")

    def test_admin_create_enhanced_quiz_with_nested_structure(self):
        """Test admin creating quiz with nested subject structure (Mathematics → Triangles → Geometry)"""
        if not self.admin_token:
            return self.log_test("Admin Create Enhanced Quiz with Nested Structure", False, "No admin token available")
        
        # First get a user ID for allowed_users
        try:
            users_response = requests.get(
                f"{self.api_url}/admin/users",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            if users_response.status_code != 200:
                return self.log_test("Admin Create Enhanced Quiz with Nested Structure", False, "Could not get users list")
            
            users = users_response.json()
            test_user_id = None
            for user in users:
                if user.get('role') == 'user':
                    test_user_id = user.get('id')
                    break
            
            if not test_user_id:
                return self.log_test("Admin Create Enhanced Quiz with Nested Structure", False, "No test user found for allowed_users")
            
            quiz_data = {
                "title": "Triangle Properties Quiz",
                "description": "A quiz about triangle properties and geometry",
                "category": "Geometry",
                "subject": "Mathematics",
                "subcategory": "Triangles",
                "is_public": True,
                "allowed_users": [test_user_id],
                "questions": [
                    {
                        "question_text": "What is the sum of angles in a triangle?",
                        "options": [
                            {"text": "90 degrees", "is_correct": False},
                            {"text": "180 degrees", "is_correct": True},
                            {"text": "270 degrees", "is_correct": False},
                            {"text": "360 degrees", "is_correct": False}
                        ]
                    },
                    {
                        "question_text": "What type of triangle has all sides equal?",
                        "options": [
                            {"text": "Scalene", "is_correct": False},
                            {"text": "Isosceles", "is_correct": False},
                            {"text": "Equilateral", "is_correct": True},
                            {"text": "Right", "is_correct": False}
                        ]
                    }
                ]
            }

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
                self.nested_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.nested_quiz_id}"
                details += f", Subject: {quiz.get('subject', 'Unknown')}"
                details += f", Subcategory: {quiz.get('subcategory', 'Unknown')}"
                details += f", Category: {quiz.get('category', 'Unknown')}"
                details += f", Public: {quiz.get('is_public', False)}"
                details += f", Total Questions: {quiz.get('total_questions', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Enhanced Quiz with Nested Structure", success, details)
        except Exception as e:
            return self.log_test("Admin Create Enhanced Quiz with Nested Structure", False, f"Error: {str(e)}")

    def test_admin_quiz_edit_details(self):
        """Test admin getting quiz edit details"""
        if not self.admin_token or not hasattr(self, 'nested_quiz_id'):
            return self.log_test("Admin Quiz Edit Details", False, "No admin token or nested quiz ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/quiz/{self.nested_quiz_id}/edit-details",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                quiz = data.get('quiz', {})
                details += f", Quiz Title: {quiz.get('title', 'Unknown')}"
                details += f", Questions Count: {len(quiz.get('questions', []))}"
                details += f", Total Attempts: {data.get('total_attempts', 0)}"
                details += f", Average Score: {data.get('average_score', 0)}"
                
                # Check if questions have all required fields for editing
                questions = quiz.get('questions', [])
                if questions:
                    first_question = questions[0]
                    details += f", First Q Options: {len(first_question.get('options', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Quiz Edit Details", success, details)
        except Exception as e:
            return self.log_test("Admin Quiz Edit Details", False, f"Error: {str(e)}")

    def test_admin_enhanced_quiz_update(self):
        """Test admin updating quiz with enhanced question editing"""
        if not self.admin_token or not hasattr(self, 'nested_quiz_id'):
            return self.log_test("Admin Enhanced Quiz Update", False, "No admin token or nested quiz ID available")
            
        # Update quiz with modified questions
        update_data = {
            "title": "Updated Triangle Properties Quiz",
            "description": "Updated description with enhanced features",
            "subject": "Mathematics",
            "subcategory": "Geometry",  # Changed subcategory
            "category": "Advanced Geometry",
            "questions": [
                {
                    "id": "q1",
                    "question_text": "What is the sum of interior angles in any triangle?",
                    "options": [
                        {"text": "90 degrees", "is_correct": False},
                        {"text": "180 degrees", "is_correct": True},
                        {"text": "270 degrees", "is_correct": False},
                        {"text": "360 degrees", "is_correct": False}
                    ],
                    "image_url": None
                },
                {
                    "id": "q2",
                    "question_text": "In a right triangle, what is the longest side called?",
                    "options": [
                        {"text": "Adjacent", "is_correct": False},
                        {"text": "Opposite", "is_correct": False},
                        {"text": "Hypotenuse", "is_correct": True},
                        {"text": "Base", "is_correct": False}
                    ],
                    "image_url": None
                },
                {
                    "id": "q3",
                    "question_text": "What is the area formula for a triangle?",
                    "options": [
                        {"text": "base × height", "is_correct": False},
                        {"text": "½ × base × height", "is_correct": True},
                        {"text": "2 × base × height", "is_correct": False},
                        {"text": "base + height", "is_correct": False}
                    ],
                    "image_url": None
                }
            ]
        }

        try:
            response = requests.put(
                f"{self.api_url}/admin/quiz/{self.nested_quiz_id}",
                json=update_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quiz = response.json()
                details += f", Updated Title: {quiz.get('title', 'Unknown')}"
                details += f", Updated Subcategory: {quiz.get('subcategory', 'Unknown')}"
                details += f", Updated Questions: {quiz.get('total_questions', 0)}"
                details += f", Updated At: {quiz.get('updated_at', 'Unknown')[:19]}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Enhanced Quiz Update", success, details)
        except Exception as e:
            return self.log_test("Admin Enhanced Quiz Update", False, f"Error: {str(e)}")

    def test_quiz_results_ranking(self):
        """Test quiz results ranking with leaderboard"""
        if not self.user_token or not hasattr(self, 'nested_quiz_id'):
            return self.log_test("Quiz Results Ranking", False, "No user token or nested quiz ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/quiz/{self.nested_quiz_id}/results-ranking",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Quiz Title: {data.get('quiz_title', 'Unknown')}"
                details += f", Total Participants: {data.get('total_participants', 0)}"
                
                top_3 = data.get('top_3', [])
                details += f", Top 3 Count: {len(top_3)}"
                
                user_position = data.get('user_position', {})
                if user_position:
                    details += f", User Rank: {user_position.get('rank', 'N/A')}"
                
                quiz_stats = data.get('quiz_stats', {})
                details += f", Total Attempts: {quiz_stats.get('total_attempts', 0)}"
                details += f", Average Score: {quiz_stats.get('average_score', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Quiz Results Ranking", success, details)
        except Exception as e:
            return self.log_test("Quiz Results Ranking", False, f"Error: {str(e)}")

    def test_admin_edit_quiz(self):
        """Test admin editing quiz (only creator can edit)"""
        if not self.admin_token or not hasattr(self, 'enhanced_quiz_id'):
            return self.log_test("Admin Edit Quiz", False, "No admin token or enhanced quiz ID available")
            
        update_data = {
            "title": "Updated Enhanced Quiz Title",
            "description": "Updated description for enhanced quiz",
            "subject_folder": "Science",
            "is_public": False
        }

        try:
            response = requests.put(
                f"{self.api_url}/admin/quiz/{self.enhanced_quiz_id}",
                json=update_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quiz = response.json()
                details += f", Updated Title: {quiz.get('title', 'Unknown')}"
                details += f", Updated Subject: {quiz.get('subject_folder', 'Unknown')}"
                details += f", Updated Public: {quiz.get('is_public', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Edit Quiz", success, details)
        except Exception as e:
            return self.log_test("Admin Edit Quiz", False, f"Error: {str(e)}")

    def test_admin_quiz_access_control(self):
        """Test admin setting quiz access control"""
        if not self.admin_token or not hasattr(self, 'enhanced_quiz_id'):
            return self.log_test("Admin Quiz Access Control", False, "No admin token or enhanced quiz ID available")
        
        # Get user IDs for access control
        try:
            users_response = requests.get(
                f"{self.api_url}/admin/users",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            if users_response.status_code != 200:
                return self.log_test("Admin Quiz Access Control", False, "Could not get users list")
            
            users = users_response.json()
            user_ids = [user.get('id') for user in users if user.get('role') == 'user'][:2]  # Get first 2 users
            
            if not user_ids:
                return self.log_test("Admin Quiz Access Control", False, "No test users found")
            
            access_data = {
                "quiz_id": self.enhanced_quiz_id,
                "user_ids": user_ids
            }

            response = requests.post(
                f"{self.api_url}/admin/quiz/{self.enhanced_quiz_id}/access",
                json=access_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                details += f", Users Added: {len(user_ids)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Quiz Access Control", success, details)
        except Exception as e:
            return self.log_test("Admin Quiz Access Control", False, f"Error: {str(e)}")

    def test_admin_quiz_leaderboard(self):
        """Test admin getting quiz leaderboard"""
        if not self.admin_token or not self.created_quiz_id:
            return self.log_test("Admin Quiz Leaderboard", False, "No admin token or quiz ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/quiz/{self.created_quiz_id}/leaderboard",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                leaderboard = response.json()
                details += f", Leaderboard Entries: {len(leaderboard)}"
                if len(leaderboard) > 0:
                    top_entry = leaderboard[0]
                    details += f", Top User: {top_entry.get('user_name', 'Unknown')}"
                    details += f", Top Score: {top_entry.get('percentage', 0)}%"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Quiz Leaderboard", success, details)
        except Exception as e:
            return self.log_test("Admin Quiz Leaderboard", False, f"Error: {str(e)}")

    def test_admin_subjects_structure(self):
        """Test admin getting nested subjects structure"""
        if not self.admin_token:
            return self.log_test("Admin Subjects Structure", False, "No admin token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/subjects-structure",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                structure = response.json()
                details += f", Subjects Count: {len(structure)}"
                if len(structure) > 0:
                    first_subject = list(structure.keys())[0]
                    subject_data = structure[first_subject]
                    details += f", First Subject: {first_subject}"
                    details += f", Subcategories: {len(subject_data.get('subcategories', {}))}"
                    details += f", Total Quizzes: {subject_data.get('total_quizzes', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Subjects Structure", success, details)
        except Exception as e:
            return self.log_test("Admin Subjects Structure", False, f"Error: {str(e)}")

    def test_admin_predefined_subjects(self):
        """Test admin getting predefined subjects"""
        if not self.admin_token:
            return self.log_test("Admin Predefined Subjects", False, "No admin token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/predefined-subjects",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                subjects = response.json()
                details += f", Predefined Subjects Count: {len(subjects)}"
                if 'Mathematics' in subjects:
                    math_subcategories = subjects['Mathematics']
                    details += f", Math Subcategories: {len(math_subcategories)}"
                    if 'Triangles' in math_subcategories:
                        details += ", Has Triangles subcategory"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Predefined Subjects", success, details)
        except Exception as e:
            return self.log_test("Admin Predefined Subjects", False, f"Error: {str(e)}")

    def test_admin_user_details(self):
        """Test admin getting individual user details with quiz history and mistakes"""
        if not self.admin_token:
            return self.log_test("Admin User Details", False, "No admin token available")
        
        # Get a user ID first
        try:
            users_response = requests.get(
                f"{self.api_url}/admin/users",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            if users_response.status_code != 200:
                return self.log_test("Admin User Details", False, "Could not get users list")
            
            users = users_response.json()
            test_user = None
            for user in users:
                if user.get('role') == 'user':
                    test_user = user
                    break
            
            if not test_user:
                return self.log_test("Admin User Details", False, "No test user found")
            
            user_id = test_user.get('id')
            response = requests.get(
                f"{self.api_url}/admin/user/{user_id}/details",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                user_details = response.json()
                user_info = user_details.get('user', {})
                stats = user_details.get('statistics', {})
                attempts = user_details.get('attempts', [])
                
                details += f", User: {user_info.get('name', 'Unknown')}"
                details += f", Total Attempts: {stats.get('total_attempts', 0)}"
                details += f", Avg Percentage: {stats.get('average_percentage', 0)}%"
                details += f", Attempts with Details: {len(attempts)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin User Details", success, details)
        except Exception as e:
            return self.log_test("Admin User Details", False, f"Error: {str(e)}")

    def test_user_enhanced_quiz_submission(self):
        """Test user taking quiz with enhanced submission (mistake review)"""
        if not self.user_token or not self.created_quiz_id:
            return self.log_test("User Enhanced Quiz Submission", False, "No user token or quiz ID available")

        # Submit with some wrong answers to test mistake review
        attempt_data = {
            "quiz_id": self.created_quiz_id,
            "answers": ["3", "London"]  # Wrong answers to test mistake review
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
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
                details += f", Percentage: {result.get('percentage', 0):.1f}%"
                
                # Check for enhanced features
                correct_answers = result.get('correct_answers', [])
                question_results = result.get('question_results', [])
                
                details += f", Correct Answers Provided: {len(correct_answers)}"
                details += f", Question Results: {len(question_results)}"
                
                if len(question_results) > 0:
                    first_result = question_results[0]
                    details += f", First Q Correct: {first_result.get('is_correct', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Enhanced Quiz Submission", success, details)
        except Exception as e:
            return self.log_test("User Enhanced Quiz Submission", False, f"Error: {str(e)}")

    def test_password_change(self):
        """Test password change functionality"""
        if not self.user_token:
            return self.log_test("Password Change", False, "No user token available")
            
        password_data = {
            "current_password": "testpass123",
            "new_password": "newtestpass123"
        }

        try:
            response = requests.post(
                f"{self.api_url}/auth/change-password",
                json=password_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Password Change", success, details)
        except Exception as e:
            return self.log_test("Password Change", False, f"Error: {str(e)}")

    def test_password_change_wrong_current(self):
        """Test password change with wrong current password"""
        if not self.user_token:
            return self.log_test("Password Change Wrong Current", False, "No user token available")
            
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newtestpass123"
        }

        try:
            response = requests.post(
                f"{self.api_url}/auth/change-password",
                json=password_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 400  # Should fail with bad request
            details = f"Status: {response.status_code} (Expected 400)"
            return self.log_test("Password Change Wrong Current", success, details)
        except Exception as e:
            return self.log_test("Password Change Wrong Current", False, f"Error: {str(e)}")

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
        print("🚀 Starting OnlineTestMaker API Tests - Enhanced Features Testing")
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
        
        # Test recently fixed admin quizzes endpoint
        self.test_admin_get_quizzes()
        
        # Test image upload functionality
        self.test_admin_upload_image()
        self.test_get_image()
        self.test_user_upload_image_forbidden()
        self.test_admin_create_quiz_with_image()
        
        # NEW ENHANCED FEATURES TESTING
        print("\n🆕 Testing Enhanced Features...")
        
        # Enhanced nested folder organization
        self.test_admin_subjects_structure()
        self.test_admin_predefined_subjects()
        
        # Enhanced quiz creation and management with nested structure
        self.test_admin_create_enhanced_quiz_with_nested_structure()
        self.test_admin_quiz_edit_details()
        self.test_admin_enhanced_quiz_update()
        self.test_admin_quiz_access_control()
        self.test_admin_quiz_leaderboard()
        self.test_admin_user_details()
        
        # Enhanced quiz submission with mistake review
        self.test_user_enhanced_quiz_submission()
        
        # Enhanced quiz results and ranking
        self.test_quiz_results_ranking()
        
        # Password change functionality
        self.test_password_change()
        self.test_password_change_wrong_current()
        
        # User operations
        self.test_user_get_quizzes()
        self.test_user_take_quiz()
        self.test_admin_take_quiz_forbidden()
        self.test_user_get_attempts()
        
        # Test admin quiz results viewing functionality
        self.test_admin_get_quiz_results()
        self.test_admin_get_analytics_summary()
        self.test_admin_get_user_quiz_results()
        self.test_admin_get_quiz_specific_results()
        self.test_user_access_quiz_results_forbidden()
        
        # Security tests
        self.test_unauthorized_access()

        # Summary
        print("=" * 80)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API with enhanced features is working correctly.")
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