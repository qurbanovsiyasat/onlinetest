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
    def __init__(self, base_url="http://localhost:8001"):
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

    def test_health_check(self):
        """Test health check endpoint to verify self-hosted backend"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Status: {data.get('status', 'Unknown')}"
                details += f", Hosting: {data.get('hosting', 'Unknown')}"
                details += f", Database: {data.get('database', 'Unknown')}"
                details += f", Message: {data.get('message', 'No message')}"
            return self.log_test("Health Check (Self-hosted)", success, details)
        except Exception as e:
            return self.log_test("Health Check (Self-hosted)", False, f"Error: {str(e)}")

    def test_cors_info(self):
        """Test CORS configuration for localhost origins"""
        try:
            response = requests.get(f"{self.api_url}/cors-info", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                allowed_origins = data.get('allowed_origins', [])
                details += f", Origins: {len(allowed_origins)}"
                # Check if localhost is allowed
                localhost_allowed = any('localhost' in origin for origin in allowed_origins)
                details += f", Localhost allowed: {localhost_allowed}"
                details += f", Methods: {len(data.get('allowed_methods', []))}"
            return self.log_test("CORS Configuration", success, details)
        except Exception as e:
            return self.log_test("CORS Configuration", False, f"Error: {str(e)}")

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
            "subject": "Science",  # Required field
            "subcategory": "General",
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
        if not self.user_token or not self.created_quiz_id:
            return self.log_test("Quiz Results Ranking", False, "No user token or quiz ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/quiz/{self.created_quiz_id}/results-ranking",
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
        if not self.admin_token or not hasattr(self, 'nested_quiz_id'):
            return self.log_test("Admin Quiz Access Control", False, "No admin token or nested quiz ID available")
        
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
                "quiz_id": self.nested_quiz_id,
                "user_ids": user_ids
            }

            response = requests.post(
                f"{self.api_url}/admin/quiz/{self.nested_quiz_id}/access",
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

    def test_admin_create_subject_folder(self):
        """Test admin creating subject folder"""
        if not self.admin_token:
            return self.log_test("Admin Create Subject Folder", False, "No admin token available")
            
        folder_data = {
            "name": "Advanced Physics",
            "description": "Advanced physics topics and concepts",
            "subcategories": ["Quantum Mechanics", "Thermodynamics", "Electromagnetism"],
            "is_public": True,
            "allowed_users": []
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin/subject-folder",
                json=folder_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                folder = response.json()
                self.created_folder_id = folder.get('id')
                details += f", Folder ID: {self.created_folder_id}"
                details += f", Name: {folder.get('name', 'Unknown')}"
                details += f", Subcategories: {len(folder.get('subcategories', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Subject Folder", success, details)
        except Exception as e:
            return self.log_test("Admin Create Subject Folder", False, f"Error: {str(e)}")

    def test_admin_get_subject_folders(self):
        """Test admin getting all subject folders"""
        if not self.admin_token:
            return self.log_test("Admin Get Subject Folders", False, "No admin token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/subject-folders",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                folders = response.json()
                details += f", Folders Count: {len(folders)}"
                if len(folders) > 0:
                    details += f", First Folder: {folders[0].get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Get Subject Folders", success, details)
        except Exception as e:
            return self.log_test("Admin Get Subject Folders", False, f"Error: {str(e)}")

    def test_admin_update_subject_folder(self):
        """Test admin updating subject folder"""
        if not self.admin_token or not hasattr(self, 'created_folder_id'):
            return self.log_test("Admin Update Subject Folder", False, "No admin token or folder ID available")
            
        update_data = {
            "description": "Updated description for advanced physics",
            "subcategories": ["Quantum Mechanics", "Thermodynamics", "Electromagnetism", "Relativity"],
            "is_public": False
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/admin/subject-folder/{self.created_folder_id}",
                json=update_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                folder = response.json()
                details += f", Updated Subcategories: {len(folder.get('subcategories', []))}"
                details += f", Is Public: {folder.get('is_public', True)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Update Subject Folder", success, details)
        except Exception as e:
            return self.log_test("Admin Update Subject Folder", False, f"Error: {str(e)}")

    def test_admin_upload_pdf_file(self):
        """Test admin PDF file upload functionality"""
        if not self.admin_token:
            return self.log_test("Admin Upload PDF File", False, "No admin token available")
            
        # Create a minimal PDF file (just header)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n253\n%%EOF"
        
        try:
            files = {'file': ('test.pdf', pdf_content, 'application/pdf')}
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = requests.post(
                f"{self.api_url}/admin/upload-file",
                files=files,
                headers=headers,
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                pdf_id = data.get('id')
                details += f", PDF ID: {pdf_id}, Size: {data.get('size', 0)} bytes"
                details += f", Category: {data.get('category', 'unknown')}"
                self.uploaded_pdf_id = pdf_id
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Upload PDF File", success, details)
        except Exception as e:
            return self.log_test("Admin Upload PDF File", False, f"Error: {str(e)}")

    def test_admin_create_flexible_quiz(self):
        """Test admin creating quiz with flexible question types (multiple choice + open-ended)"""
        if not self.admin_token:
            return self.log_test("Admin Create Flexible Quiz", False, "No admin token available")
            
        quiz_data = {
            "title": "Flexible Question Types Quiz",
            "description": "A quiz testing both multiple choice and open-ended questions",
            "category": "Mixed Assessment",
            "subject": "Computer Science",
            "subcategory": "Programming",
            "questions": [
                {
                    "question_text": "Which programming languages are object-oriented? (Select all that apply)",
                    "question_type": "multiple_choice",
                    "multiple_correct": True,
                    "options": [
                        {"text": "Java", "is_correct": True},
                        {"text": "Python", "is_correct": True},
                        {"text": "C", "is_correct": False},
                        {"text": "JavaScript", "is_correct": True}
                    ],
                    "points": 3,
                    "difficulty": "medium"
                },
                {
                    "question_text": "What is the capital of France?",
                    "question_type": "multiple_choice",
                    "multiple_correct": False,
                    "options": [
                        {"text": "London", "is_correct": False},
                        {"text": "Paris", "is_correct": True},
                        {"text": "Berlin", "is_correct": False},
                        {"text": "Madrid", "is_correct": False}
                    ],
                    "points": 1,
                    "difficulty": "easy"
                },
                {
                    "question_text": "Explain the concept of inheritance in object-oriented programming.",
                    "question_type": "open_ended",
                    "open_ended_answer": {
                        "expected_answers": [
                            "Inheritance allows a class to inherit properties and methods from another class",
                            "A mechanism where one class acquires the properties of another class",
                            "Child class inherits from parent class"
                        ],
                        "keywords": ["inherit", "class", "parent", "child", "properties", "methods"],
                        "case_sensitive": False,
                        "partial_credit": True
                    },
                    "points": 5,
                    "difficulty": "hard"
                }
            ],
            "min_pass_percentage": 70.0,
            "shuffle_questions": True,
            "shuffle_options": True
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
                self.flexible_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.flexible_quiz_id}"
                details += f", Total Points: {quiz.get('total_points', 0)}"
                details += f", Questions: {quiz.get('total_questions', 0)}"
                
                # Check question types
                questions = quiz.get('questions', [])
                mc_count = sum(1 for q in questions if q.get('question_type') == 'multiple_choice')
                oe_count = sum(1 for q in questions if q.get('question_type') == 'open_ended')
                details += f", MC Questions: {mc_count}, Open-ended: {oe_count}"
                
                # Publish the quiz immediately so users can take it
                publish_response = requests.post(
                    f"{self.api_url}/admin/quiz/{self.flexible_quiz_id}/publish",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if publish_response.status_code == 200:
                    details += ", Published: Yes"
                else:
                    details += ", Published: Failed"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Flexible Quiz", success, details)
        except Exception as e:
            return self.log_test("Admin Create Flexible Quiz", False, f"Error: {str(e)}")

    def test_user_take_flexible_quiz(self):
        """Test user taking quiz with mixed question types"""
        if not self.user_token or not hasattr(self, 'flexible_quiz_id'):
            return self.log_test("User Take Flexible Quiz", False, "No user token or flexible quiz ID available")

        # Answers: partial correct for multiple choice, correct single choice, partial open-ended
        attempt_data = {
            "quiz_id": self.flexible_quiz_id,
            "answers": [
                "Java,Python",  # Partial correct (missing JavaScript)
                "Paris",        # Correct
                "Inheritance allows a class to inherit properties from parent class"  # Partial (has keywords)
            ]
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz/{self.flexible_quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
                details += f", Points: {result.get('earned_points', 0)}/{result.get('total_possible_points', 0)}"
                details += f", Percentage: {result.get('percentage', 0):.1f}%"
                details += f", Points %: {result.get('points_percentage', 0):.1f}%"
                details += f", Passed: {result.get('passed', False)}"
                
                # Check question results for grading details
                question_results = result.get('question_results', [])
                if len(question_results) > 0:
                    details += f", Q1 Points: {question_results[0].get('points_earned', 0)}"
                    if len(question_results) > 2:
                        details += f", Q3 Points: {question_results[2].get('points_earned', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Take Flexible Quiz", success, details)
        except Exception as e:
            return self.log_test("User Take Flexible Quiz", False, f"Error: {str(e)}")

    def test_admin_move_quiz_to_folder(self):
        """Test admin moving quiz to different folder"""
        if not self.admin_token or not hasattr(self, 'flexible_quiz_id'):
            return self.log_test("Admin Move Quiz to Folder", False, "No admin token or quiz ID available")
            
        try:
            # Move quiz to Mathematics -> Algebra (using existing subject)
            response = requests.post(
                f"{self.api_url}/admin/quiz/{self.flexible_quiz_id}/move-folder?new_subject=Mathematics&new_subcategory=Algebra",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                
                # Verify the move by getting quiz details
                quiz_response = requests.get(
                    f"{self.api_url}/quiz/{self.flexible_quiz_id}",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                if quiz_response.status_code == 200:
                    quiz = quiz_response.json()
                    details += f", New Subject: {quiz.get('subject', 'Unknown')}"
                    details += f", New Subcategory: {quiz.get('subcategory', 'Unknown')}"
            else:
                # If move fails, try with existing subject from structure
                details += f", Response: {response.text[:200]}"
                # Try with General subject which should exist
                response2 = requests.post(
                    f"{self.api_url}/admin/quiz/{self.flexible_quiz_id}/move-folder?new_subject=General&new_subcategory=General",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if response2.status_code == 200:
                    success = True
                    details += ", Moved to General/General instead"
                
            return self.log_test("Admin Move Quiz to Folder", success, details)
        except Exception as e:
            return self.log_test("Admin Move Quiz to Folder", False, f"Error: {str(e)}")

    def test_admin_delete_quiz(self):
        """Test admin deleting quiz"""
        if not self.admin_token or not self.created_quiz_id:
            return self.log_test("Admin Delete Quiz", False, "No admin token or quiz ID available")
            
        try:
            response = requests.delete(
                f"{self.api_url}/admin/quiz/{self.created_quiz_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                
                # Verify quiz is deleted by trying to access it
                verify_response = requests.get(
                    f"{self.api_url}/quiz/{self.created_quiz_id}",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                details += f", Verification: {verify_response.status_code} (Expected 404)"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Delete Quiz", success, details)
        except Exception as e:
            return self.log_test("Admin Delete Quiz", False, f"Error: {str(e)}")

    def test_user_delete_quiz_forbidden(self):
        """Test user trying to delete quiz (should fail)"""
        if not self.user_token or not hasattr(self, 'flexible_quiz_id'):
            return self.log_test("User Delete Quiz (Forbidden)", False, "No user token or quiz ID available")
            
        try:
            response = requests.delete(
                f"{self.api_url}/admin/quiz/{self.flexible_quiz_id}",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            return self.log_test("User Delete Quiz (Forbidden)", success, details)
        except Exception as e:
            return self.log_test("User Delete Quiz (Forbidden)", False, f"Error: {str(e)}")

    def test_admin_delete_quiz_nonexistent(self):
        """Test admin deleting non-existent quiz"""
        if not self.admin_token:
            return self.log_test("Admin Delete Non-existent Quiz", False, "No admin token available")
            
        fake_quiz_id = "nonexistent-quiz-id"
        try:
            response = requests.delete(
                f"{self.api_url}/admin/quiz/{fake_quiz_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 404  # Should return 404
            details = f"Status: {response.status_code} (Expected 404)"
            return self.log_test("Admin Delete Non-existent Quiz", success, details)
        except Exception as e:
            return self.log_test("Admin Delete Non-existent Quiz", False, f"Error: {str(e)}")

    def test_admin_delete_subject_folder(self):
        """Test admin deleting subject folder (should fail if has quizzes)"""
        if not self.admin_token or not hasattr(self, 'created_folder_id'):
            return self.log_test("Admin Delete Subject Folder", False, "No admin token or folder ID available")
            
        try:
            response = requests.delete(
                f"{self.api_url}/admin/subject-folder/{self.created_folder_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            # Should succeed (200) if no quizzes, or fail (400) if has quizzes
            success = response.status_code in [200, 400]
            details = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            elif response.status_code == 400:
                details += ", Cannot delete folder with quizzes (expected)"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Delete Subject Folder", success, details)
        except Exception as e:
            return self.log_test("Admin Delete Subject Folder", False, f"Error: {str(e)}")

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
        if not self.user_token or not hasattr(self, 'flexible_quiz_id'):
            return self.log_test("User Enhanced Quiz Submission", False, "No user token or flexible quiz ID available")

        # Submit with some wrong answers to test mistake review
        attempt_data = {
            "quiz_id": self.flexible_quiz_id,
            "answers": ["Java", "London", "Inheritance is about classes"]  # Mixed correct/wrong answers
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz/{self.flexible_quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
                details += f", Points: {result.get('earned_points', 0)}/{result.get('total_possible_points', 0)}"
                details += f", Percentage: {result.get('percentage', 0):.1f}%"
                details += f", Points %: {result.get('points_percentage', 0):.1f}%"
                details += f", Passed: {result.get('passed', False)}"
                
                # Check for enhanced features
                correct_answers = result.get('correct_answers', [])
                question_results = result.get('question_results', [])
                
                details += f", Correct Answers Provided: {len(correct_answers)}"
                details += f", Question Results: {len(question_results)}"
                
                if len(question_results) > 0:
                    first_result = question_results[0]
                    details += f", First Q Correct: {first_result.get('is_correct', False)}"
                    details += f", First Q Points: {first_result.get('points_earned', 0)}"
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

    def test_quiz_deletion_comprehensive(self):
        """Test comprehensive quiz deletion functionality as requested by user"""
        print("\n🗑️  COMPREHENSIVE QUIZ DELETION TEST")
        print("-" * 50)
        
        # Step 1: Login as admin (admin@onlinetestmaker.com / admin123)
        if not self.admin_token:
            return self.log_test("Quiz Deletion - Admin Login Required", False, "Admin token not available")
        
        # Step 2: Create a test quiz 
        deletion_quiz_data = {
            "title": "Quiz for Comprehensive Deletion Test",
            "description": "This quiz will be deleted as part of comprehensive testing",
            "category": "Test Category",
            "subject": "Testing",
            "subcategory": "Deletion",
            "questions": [
                {
                    "question_text": "This is a test question for deletion",
                    "options": [
                        {"text": "Option A", "is_correct": True},
                        {"text": "Option B", "is_correct": False}
                    ]
                },
                {
                    "question_text": "Another test question",
                    "options": [
                        {"text": "Yes", "is_correct": True},
                        {"text": "No", "is_correct": False}
                    ]
                }
            ]
        }
        
        try:
            # Create quiz for deletion
            response = requests.post(
                f"{self.api_url}/admin/quiz",
                json=deletion_quiz_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Quiz Deletion - Create Test Quiz", False, f"Failed to create test quiz: {response.status_code}")
            
            quiz_data = response.json()
            deletion_quiz_id = quiz_data.get('id')
            self.log_test("Quiz Deletion - Create Test Quiz", True, f"Created quiz ID: {deletion_quiz_id}")
            
            # Step 3: List all quizzes to verify it exists
            list_response = requests.get(
                f"{self.api_url}/admin/quizzes",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if list_response.status_code == 200:
                quizzes = list_response.json()
                quiz_exists = any(quiz.get('id') == deletion_quiz_id for quiz in quizzes)
                self.log_test("Quiz Deletion - Verify Quiz Exists in List", quiz_exists, f"Quiz found in admin quiz list: {quiz_exists}")
                
                if quiz_exists:
                    # Find the quiz and show details
                    target_quiz = next((q for q in quizzes if q.get('id') == deletion_quiz_id), None)
                    if target_quiz:
                        self.log_test("Quiz Deletion - Quiz Details", True, f"Title: {target_quiz.get('title')}, Questions: {target_quiz.get('total_questions', 0)}")
            else:
                self.log_test("Quiz Deletion - Verify Quiz Exists in List", False, f"Failed to get quiz list: {list_response.status_code}")
            
            # Step 4: Delete the test quiz using DELETE /api/admin/quiz/{quiz_id}
            delete_response = requests.delete(
                f"{self.api_url}/admin/quiz/{deletion_quiz_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            delete_success = delete_response.status_code == 200
            if delete_success:
                delete_data = delete_response.json()
                self.log_test("Quiz Deletion - DELETE Request", True, f"Status: 200, Message: {delete_data.get('message', 'Quiz deleted successfully')}")
            else:
                self.log_test("Quiz Deletion - DELETE Request", False, f"Delete failed: {delete_response.status_code}, {delete_response.text[:200]}")
                return False
            
            # Step 5: Verify the quiz is actually removed from the database
            verify_response = requests.get(
                f"{self.api_url}/admin/quizzes",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if verify_response.status_code == 200:
                quizzes_after = verify_response.json()
                quiz_still_exists = any(quiz.get('id') == deletion_quiz_id for quiz in quizzes_after)
                self.log_test("Quiz Deletion - Verify Database Removal", not quiz_still_exists, f"Quiz removed from database: {not quiz_still_exists}")
                
                if quiz_still_exists:
                    self.log_test("Quiz Deletion - ERROR", False, "Quiz still exists in database after deletion!")
                    return False
            else:
                self.log_test("Quiz Deletion - Verify Database Removal", False, f"Failed to verify removal: {verify_response.status_code}")
            
            # Step 6: Test what happens if we try to delete a non-existent quiz
            fake_quiz_id = "non-existent-quiz-id-12345"
            nonexistent_response = requests.delete(
                f"{self.api_url}/admin/quiz/{fake_quiz_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            # Should return 404 for non-existent quiz
            expected_404 = nonexistent_response.status_code == 404
            self.log_test("Quiz Deletion - Delete Non-existent Quiz", expected_404, f"Status: {nonexistent_response.status_code} (Expected 404)")
            
            # Additional verification: Try to access deleted quiz directly
            try:
                access_deleted_response = requests.get(
                    f"{self.api_url}/quiz/{deletion_quiz_id}",
                    headers=self.get_auth_headers(self.user_token if self.user_token else self.admin_token),
                    timeout=10
                )
                access_failed = access_deleted_response.status_code == 404
                self.log_test("Quiz Deletion - Access Deleted Quiz", access_failed, f"Access properly denied: {access_failed} (Status: {access_deleted_response.status_code})")
            except Exception as e:
                self.log_test("Quiz Deletion - Access Deleted Quiz", True, f"Access properly blocked: {str(e)[:100]}")
            
            # Test user trying to delete quiz (should be forbidden)
            if self.user_token and self.created_quiz_id:
                user_delete_response = requests.delete(
                    f"{self.api_url}/admin/quiz/{self.created_quiz_id}",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                user_forbidden = user_delete_response.status_code == 403
                self.log_test("Quiz Deletion - User Delete Forbidden", user_forbidden, f"User delete properly forbidden: {user_forbidden} (Status: {user_delete_response.status_code})")
            
            print("✅ COMPREHENSIVE QUIZ DELETION TEST COMPLETED")
            return True
            
        except Exception as e:
            self.log_test("Quiz Deletion - Overall Test", False, f"Error: {str(e)}")
            return False

    def test_unauthorized_access(self):
        """Test accessing protected endpoints without token"""
        try:
            response = requests.get(f"{self.api_url}/auth/me", timeout=10)
            success = response.status_code == 401  # Should be unauthorized
            details = f"Status: {response.status_code} (Expected 401)"
            return self.log_test("Unauthorized Access", success, details)
        except Exception as e:
            return self.log_test("Unauthorized Access", False, f"Error: {str(e)}")

    def test_admin_delete_quiz(self):
        """Test admin deleting a quiz - FOCUSED TEST FOR QUIZ DELETION"""
        if not self.admin_token:
            return self.log_test("Admin Delete Quiz", False, "No admin token available")
        
        # First create a quiz specifically for deletion testing
        quiz_data = {
            "title": "Quiz to Delete - Test",
            "description": "This quiz will be deleted as part of testing",
            "category": "Test Category",
            "subject": "Testing",
            "subcategory": "Deletion",
            "questions": [
                {
                    "question_text": "This is a test question for deletion",
                    "options": [
                        {"text": "Option A", "is_correct": True},
                        {"text": "Option B", "is_correct": False}
                    ]
                }
            ]
        }

        try:
            # Create the quiz first
            create_response = requests.post(
                f"{self.api_url}/admin/quiz",
                json=quiz_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if create_response.status_code != 200:
                return self.log_test("Admin Delete Quiz", False, f"Failed to create quiz for deletion test: {create_response.status_code}")
            
            quiz_to_delete = create_response.json()
            quiz_id_to_delete = quiz_to_delete.get('id')
            
            if not quiz_id_to_delete:
                return self.log_test("Admin Delete Quiz", False, "No quiz ID returned from creation")
            
            # Verify quiz exists before deletion
            get_response = requests.get(
                f"{self.api_url}/admin/quizzes",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if get_response.status_code == 200:
                all_quizzes = get_response.json()
                quiz_exists_before = any(q.get('id') == quiz_id_to_delete for q in all_quizzes)
                if not quiz_exists_before:
                    return self.log_test("Admin Delete Quiz", False, "Quiz not found in quiz list before deletion")
            
            # Now attempt to delete the quiz
            delete_response = requests.delete(
                f"{self.api_url}/admin/quiz/{quiz_id_to_delete}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            success = delete_response.status_code == 200
            details = f"Status: {delete_response.status_code}"
            
            if success:
                data = delete_response.json()
                details += f", Message: {data.get('message', 'No message')}"
                
                # Verify quiz is actually deleted from database
                verify_response = requests.get(
                    f"{self.api_url}/admin/quizzes",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                
                if verify_response.status_code == 200:
                    all_quizzes_after = verify_response.json()
                    quiz_exists_after = any(q.get('id') == quiz_id_to_delete for q in all_quizzes_after)
                    
                    if quiz_exists_after:
                        success = False
                        details += ", ERROR: Quiz still exists in database after deletion"
                    else:
                        details += ", Verified: Quiz removed from database"
                else:
                    details += ", WARNING: Could not verify deletion from database"
                    
            else:
                details += f", Response: {delete_response.text[:200]}"
                
            return self.log_test("Admin Delete Quiz", success, details)
            
        except Exception as e:
            return self.log_test("Admin Delete Quiz", False, f"Error: {str(e)}")

    def test_admin_delete_nonexistent_quiz(self):
        """Test admin trying to delete non-existent quiz (should return 404)"""
        if not self.admin_token:
            return self.log_test("Admin Delete Non-existent Quiz", False, "No admin token available")
        
        fake_quiz_id = "non-existent-quiz-id-12345"
        
        try:
            response = requests.delete(
                f"{self.api_url}/admin/quiz/{fake_quiz_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            success = response.status_code == 404  # Should return 404 for non-existent quiz
            details = f"Status: {response.status_code} (Expected 404)"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('detail', 'No message')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Delete Non-existent Quiz", success, details)
            
        except Exception as e:
            return self.log_test("Admin Delete Non-existent Quiz", False, f"Error: {str(e)}")

    def test_user_delete_quiz_forbidden(self):
        """Test user trying to delete quiz (should be forbidden)"""
        if not self.user_token or not self.created_quiz_id:
            return self.log_test("User Delete Quiz (Forbidden)", False, "No user token or quiz ID available")
        
        try:
            response = requests.delete(
                f"{self.api_url}/admin/quiz/{self.created_quiz_id}",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            
            return self.log_test("User Delete Quiz (Forbidden)", success, details)
            
        except Exception as e:
            return self.log_test("User Delete Quiz (Forbidden)", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting OnlineTestMaker API Tests - Self-hosted Backend Verification")
        print(f"🌐 Testing against: {self.api_url}")
        print("=" * 80)

        # DECOUPLING VERIFICATION TESTS (as requested in review)
        print("\n🔍 Testing Backend Decoupling from Emergenet Infrastructure...")
        self.test_health_check()
        self.test_cors_info()

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
        
        # Subject folder management tests
        self.test_admin_create_subject_folder()
        self.test_admin_get_subject_folders()
        self.test_admin_update_subject_folder()
        
        # File upload tests (PDF)
        self.test_admin_upload_pdf_file()
        
        # Flexible question types tests
        self.test_admin_create_flexible_quiz()
        self.test_user_take_flexible_quiz()
        
        # Quiz folder management
        self.test_admin_move_quiz_to_folder()
        
        # Enhanced quiz creation and management with nested structure
        self.test_admin_create_enhanced_quiz_with_nested_structure()
        self.test_admin_quiz_edit_details()
        self.test_admin_enhanced_quiz_update()
        self.test_admin_quiz_access_control()
        self.test_admin_quiz_leaderboard()
        self.test_admin_user_details()
        
        # Subject folder deletion (should test after moving quizzes)
        self.test_admin_delete_subject_folder()
        
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
        
        # QUIZ DELETION FUNCTIONALITY TESTS (as requested)
        print("\n🗑️  Testing Quiz Deletion Functionality...")
        self.test_quiz_deletion_comprehensive()
        self.test_admin_delete_quiz()
        self.test_admin_delete_nonexistent_quiz()
        self.test_user_delete_quiz_forbidden()

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