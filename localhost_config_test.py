#!/usr/bin/env python3
"""
Localhost Configuration Testing for Squiz Quiz Platform
Tests the localhost setup to ensure CORS errors are resolved and app works completely on localhost
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import os

class LocalhostConfigTester:
    def __init__(self):
        # Read backend URL from frontend/.env
        self.backend_url = self.get_backend_url()
        self.api_url = f"{self.backend_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.user_token = None
        self.test_user_id = str(uuid.uuid4())[:8]
        
        print(f"🔧 Testing Localhost Configuration")
        print(f"Backend URL: {self.backend_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 80)

    def get_backend_url(self):
        """Get backend URL from frontend/.env"""
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        return line.split('=')[1].strip()
        except:
            pass
        return "http://localhost:8001"  # fallback

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

    def test_backend_health_check(self):
        """Test backend health check endpoint"""
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
                
                # Verify it's self-hosted
                if data.get('hosting') == 'self-hosted':
                    details += " ✓ Self-hosted confirmed"
                else:
                    details += " ⚠️ Not self-hosted"
                    
            return self.log_test("Backend Health Check", success, details)
        except Exception as e:
            return self.log_test("Backend Health Check", False, f"Error: {str(e)}")

    def test_cors_configuration(self):
        """Test CORS configuration for localhost origins"""
        try:
            response = requests.get(f"{self.api_url}/cors-info", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                allowed_origins = data.get('allowed_origins', [])
                details += f", Origins configured: {len(allowed_origins)}"
                
                # Check if localhost is allowed
                localhost_allowed = any('localhost' in str(origin) for origin in allowed_origins)
                details += f", Localhost allowed: {localhost_allowed}"
                
                if localhost_allowed:
                    details += " ✓ CORS properly configured"
                else:
                    details += " ⚠️ Localhost not in CORS origins"
                    success = False
                    
                details += f", Methods: {len(data.get('allowed_methods', []))}"
                details += f", Credentials: {data.get('credentials_allowed', False)}"
                
            return self.log_test("CORS Configuration", success, details)
        except Exception as e:
            return self.log_test("CORS Configuration", False, f"Error: {str(e)}")

    def test_database_connectivity(self):
        """Test database connectivity through health check"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                db_status = data.get('database', 'Unknown')
                details += f", Database: {db_status}"
                
                if db_status == 'connected':
                    details += " ✓ MongoDB connected"
                else:
                    details += " ⚠️ Database connection issue"
                    success = False
                    
            return self.log_test("Database Connectivity", success, details)
        except Exception as e:
            return self.log_test("Database Connectivity", False, f"Error: {str(e)}")

    def test_admin_authentication(self):
        """Test admin authentication with admin@squiz.com/admin123"""
        login_data = {
            "email": "admin@squiz.com",
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
                details += f", Role: {user_info.get('role', 'Unknown')}"
                details += f", Name: {user_info.get('name', 'Unknown')}"
                details += f", Email: {user_info.get('email', 'Unknown')}"
                
                if user_info.get('role') == 'admin':
                    details += " ✓ Admin role confirmed"
                else:
                    details += " ⚠️ Not admin role"
                    success = False
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Authentication", success, details)
        except Exception as e:
            return self.log_test("Admin Authentication", False, f"Error: {str(e)}")

    def test_user_registration_and_login(self):
        """Test user registration and login flow"""
        # Register user
        user_data = {
            "name": f"Test User {self.test_user_id}",
            "email": f"testuser{self.test_user_id}@example.com",
            "password": "testpass123"
        }
        
        try:
            # Registration
            reg_response = requests.post(
                f"{self.api_url}/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if reg_response.status_code != 200:
                return self.log_test("User Registration & Login", False, f"Registration failed: {reg_response.status_code}")
            
            # Login
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            login_response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = login_response.status_code == 200
            details = f"Reg: {reg_response.status_code}, Login: {login_response.status_code}"
            
            if success:
                data = login_response.json()
                self.user_token = data.get('access_token')
                user_info = data.get('user', {})
                details += f", Role: {user_info.get('role', 'Unknown')}"
                details += f", Name: {user_info.get('name', 'Unknown')}"
                
                if user_info.get('role') == 'user':
                    details += " ✓ User role confirmed"
                else:
                    details += " ⚠️ Incorrect role"
                    success = False
            else:
                details += f", Response: {login_response.text[:200]}"
                
            return self.log_test("User Registration & Login", success, details)
        except Exception as e:
            return self.log_test("User Registration & Login", False, f"Error: {str(e)}")

    def test_auth_me_endpoint(self):
        """Test /auth/me endpoint for both admin and user"""
        if not self.admin_token:
            return self.log_test("Auth Me Endpoint", False, "No admin token available")
            
        try:
            # Test admin /auth/me
            admin_response = requests.get(
                f"{self.api_url}/auth/me",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            admin_success = admin_response.status_code == 200
            details = f"Admin: {admin_response.status_code}"
            
            if admin_success:
                admin_data = admin_response.json()
                details += f", Role: {admin_data.get('role', 'Unknown')}"
                details += f", Email: {admin_data.get('email', 'Unknown')}"
            
            # Test user /auth/me if user token available
            user_success = True
            if self.user_token:
                user_response = requests.get(
                    f"{self.api_url}/auth/me",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                user_success = user_response.status_code == 200
                details += f", User: {user_response.status_code}"
                
                if user_success:
                    user_data = user_response.json()
                    details += f", User Role: {user_data.get('role', 'Unknown')}"
            
            success = admin_success and user_success
            return self.log_test("Auth Me Endpoint", success, details)
        except Exception as e:
            return self.log_test("Auth Me Endpoint", False, f"Error: {str(e)}")

    def test_basic_api_endpoints(self):
        """Test basic API endpoints are responding"""
        if not self.admin_token:
            return self.log_test("Basic API Endpoints", False, "No admin token available")
            
        endpoints_to_test = [
            ("/admin/users", "GET", "Admin Users"),
            ("/admin/quizzes", "GET", "Admin Quizzes"),
            ("/admin/categories", "GET", "Categories"),
            ("/quizzes", "GET", "Public Quizzes")
        ]
        
        results = []
        for endpoint, method, name in endpoints_to_test:
            try:
                if method == "GET":
                    # Use admin token for admin endpoints, user token for public endpoints
                    token = self.admin_token if endpoint.startswith("/admin") else (self.user_token or self.admin_token)
                    response = requests.get(
                        f"{self.api_url}{endpoint}",
                        headers=self.get_auth_headers(token),
                        timeout=10
                    )
                    results.append((name, response.status_code == 200, response.status_code))
                else:
                    results.append((name, False, "Method not implemented"))
            except Exception as e:
                results.append((name, False, f"Error: {str(e)}"))
        
        success_count = sum(1 for _, success, _ in results)
        total_count = len(results)
        overall_success = success_count == total_count
        
        details = f"Passed: {success_count}/{total_count}"
        for name, success, status in results:
            status_symbol = "✓" if success else "✗"
            details += f", {name}: {status_symbol}{status}"
        
        return self.log_test("Basic API Endpoints", overall_success, details)

    def test_admin_quiz_creation(self):
        """Test admin can create a quiz"""
        if not self.admin_token:
            return self.log_test("Admin Quiz Creation", False, "No admin token available")
            
        quiz_data = {
            "title": "Localhost Test Quiz",
            "description": "A test quiz to verify localhost configuration",
            "category": "Test Category",
            "subject": "Testing",
            "subcategory": "Localhost",
            "questions": [
                {
                    "question_text": "Is the localhost configuration working?",
                    "options": [
                        {"text": "Yes", "is_correct": True},
                        {"text": "No", "is_correct": False},
                        {"text": "Maybe", "is_correct": False},
                        {"text": "Unknown", "is_correct": False}
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
                details += f", Quiz ID: {self.created_quiz_id}"
                details += f", Questions: {quiz.get('total_questions', 0)}"
                details += f", Draft: {quiz.get('is_draft', 'Unknown')}"
                
                # Publish the quiz for user testing
                publish_response = requests.post(
                    f"{self.api_url}/admin/quiz/{self.created_quiz_id}/publish",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if publish_response.status_code == 200:
                    details += ", Published: ✓"
                else:
                    details += f", Publish failed: {publish_response.status_code}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Quiz Creation", success, details)
        except Exception as e:
            return self.log_test("Admin Quiz Creation", False, f"Error: {str(e)}")

    def test_user_quiz_access(self):
        """Test user can access and take quiz"""
        if not self.user_token or not hasattr(self, 'created_quiz_id'):
            return self.log_test("User Quiz Access", False, "No user token or quiz ID available")
            
        try:
            # First, get available quizzes
            quizzes_response = requests.get(
                f"{self.api_url}/quizzes",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if quizzes_response.status_code != 200:
                return self.log_test("User Quiz Access", False, f"Cannot get quizzes: {quizzes_response.status_code}")
            
            quizzes = quizzes_response.json()
            quiz_found = any(quiz.get('id') == self.created_quiz_id for quiz in quizzes)
            
            details = f"Quizzes available: {len(quizzes)}, Test quiz found: {quiz_found}"
            
            if not quiz_found:
                return self.log_test("User Quiz Access", False, f"{details}, Quiz not accessible to user")
            
            # Try to take the quiz
            attempt_data = {
                "quiz_id": self.created_quiz_id,
                "answers": ["Yes"]  # Correct answer
            }
            
            attempt_response = requests.post(
                f"{self.api_url}/quiz/{self.created_quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            success = attempt_response.status_code == 200
            details += f", Attempt: {attempt_response.status_code}"
            
            if success:
                result = attempt_response.json()
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
                details += f", Percentage: {result.get('percentage', 0):.1f}%"
            else:
                details += f", Response: {attempt_response.text[:200]}"
                
            return self.log_test("User Quiz Access", success, details)
        except Exception as e:
            return self.log_test("User Quiz Access", False, f"Error: {str(e)}")

    def test_frontend_backend_connection(self):
        """Test that frontend can connect to local backend"""
        try:
            # Test a simple endpoint that frontend would use
            response = requests.get(f"{self.api_url}/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Backend accessible: ✓"
                details += f", Response time: {response.elapsed.total_seconds():.3f}s"
                
                # Check if this is the expected localhost backend
                if self.backend_url == "http://localhost:8001":
                    details += ", Localhost backend: ✓"
                else:
                    details += f", Backend URL: {self.backend_url}"
            else:
                details += ", Backend not accessible"
                
            return self.log_test("Frontend-Backend Connection", success, details)
        except Exception as e:
            return self.log_test("Frontend-Backend Connection", False, f"Error: {str(e)}")

    def test_role_based_access_control(self):
        """Test role-based access control is working"""
        if not self.admin_token or not self.user_token:
            return self.log_test("Role-Based Access Control", False, "Missing tokens")
            
        try:
            # Test user trying to access admin endpoint (should fail)
            user_admin_response = requests.get(
                f"{self.api_url}/admin/users",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            # Test admin accessing admin endpoint (should succeed)
            admin_admin_response = requests.get(
                f"{self.api_url}/admin/users",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            # Test admin trying to take quiz (should fail)
            if hasattr(self, 'created_quiz_id'):
                admin_quiz_response = requests.post(
                    f"{self.api_url}/quiz/{self.created_quiz_id}/attempt",
                    json={"quiz_id": self.created_quiz_id, "answers": ["Yes"]},
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                admin_quiz_blocked = admin_quiz_response.status_code == 403
            else:
                admin_quiz_blocked = True  # Skip if no quiz
            
            user_blocked = user_admin_response.status_code == 403
            admin_allowed = admin_admin_response.status_code == 200
            
            success = user_blocked and admin_allowed and admin_quiz_blocked
            details = f"User blocked from admin: {user_blocked}"
            details += f", Admin allowed: {admin_allowed}"
            details += f", Admin blocked from quiz: {admin_quiz_blocked}"
            
            if success:
                details += " ✓ RBAC working correctly"
            else:
                details += " ⚠️ RBAC issues detected"
                
            return self.log_test("Role-Based Access Control", success, details)
        except Exception as e:
            return self.log_test("Role-Based Access Control", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all localhost configuration tests"""
        print("🚀 Starting Localhost Configuration Tests...")
        print()
        
        # Core infrastructure tests
        self.test_backend_health_check()
        self.test_cors_configuration()
        self.test_database_connectivity()
        self.test_frontend_backend_connection()
        
        print()
        
        # Authentication tests
        self.test_admin_authentication()
        self.test_user_registration_and_login()
        self.test_auth_me_endpoint()
        
        print()
        
        # API functionality tests
        self.test_basic_api_endpoints()
        self.test_admin_quiz_creation()
        self.test_user_quiz_access()
        self.test_role_based_access_control()
        
        print()
        print("=" * 80)
        print(f"🏁 LOCALHOST CONFIGURATION TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Localhost configuration is working perfectly!")
            print("✅ CORS errors should be resolved")
            print("✅ App is working completely on localhost")
        else:
            print("⚠️  Some tests failed - localhost configuration needs attention")
            
        print("=" * 80)
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = LocalhostConfigTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)