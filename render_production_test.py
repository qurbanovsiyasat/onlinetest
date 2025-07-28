#!/usr/bin/env python3
"""
Render Production Readiness Testing for Squiz Backend
Focus: Health check, admin auth, basic quiz operations, CORS, database connectivity
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import time

class SquizProductionTester:
    def __init__(self, base_url=None):
        # Use the production URL from frontend/.env
        if base_url is None:
            try:
                with open('/app/frontend/.env', 'r') as f:
                    for line in f:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            base_url = line.split('=')[1].strip()
                            break
                if not base_url:
                    base_url = "http://localhost:8001"
            except:
                base_url = "http://localhost:8001"
        
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

    def test_health_check_render_ready(self):
        """Test health check endpoint - CRITICAL for Render deployment"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                status = data.get('status', 'Unknown')
                hosting = data.get('hosting', 'Unknown')
                database = data.get('database', 'Unknown')
                message = data.get('message', 'No message')
                
                details += f", Status: {status}, Hosting: {hosting}, Database: {database}"
                details += f", Message: '{message}'"
                
                # Verify critical fields for Render
                if status != 'healthy':
                    success = False
                    details += " - CRITICAL: Status not healthy"
                if database != 'connected':
                    success = False
                    details += " - CRITICAL: Database not connected"
                    
            return self.log_test("Health Check (Render Critical)", success, details)
        except Exception as e:
            return self.log_test("Health Check (Render Critical)", False, f"Error: {str(e)}")

    def test_cors_configuration(self):
        """Test CORS configuration for production deployment"""
        try:
            response = requests.get(f"{self.api_url}/cors-info", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                allowed_origins = data.get('allowed_origins', [])
                allowed_methods = data.get('allowed_methods', [])
                credentials_allowed = data.get('credentials_allowed', False)
                
                details += f", Origins: {len(allowed_origins)}, Methods: {len(allowed_methods)}"
                details += f", Credentials: {credentials_allowed}"
                
                # Check for localhost support (development)
                localhost_allowed = any('localhost' in origin for origin in allowed_origins)
                details += f", Localhost: {localhost_allowed}"
                
                # Check for production origins
                render_origins = any('onrender.com' in origin for origin in allowed_origins)
                details += f", Render domains: {render_origins}"
                
            return self.log_test("CORS Configuration", success, details)
        except Exception as e:
            return self.log_test("CORS Configuration", False, f"Error: {str(e)}")

    def test_database_connectivity(self):
        """Test database connectivity through API endpoints"""
        try:
            # Test database through a simple endpoint that requires DB access
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code != 200:
                return self.log_test("Database Connectivity", False, "Health check failed")
            
            data = response.json()
            db_status = data.get('database', 'Unknown')
            success = db_status == 'connected'
            
            details = f"Database Status: {db_status}"
            if success:
                details += ", MongoDB connection verified"
            else:
                details += " - CRITICAL: Database connection failed"
                
            return self.log_test("Database Connectivity", success, details)
        except Exception as e:
            return self.log_test("Database Connectivity", False, f"Error: {str(e)}")

    def test_admin_authentication_squiz(self):
        """Test admin authentication with Squiz credentials"""
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
                role = user_info.get('role', 'Unknown')
                name = user_info.get('name', 'Unknown')
                email = user_info.get('email', 'Unknown')
                
                details += f", Role: {role}, Name: {name}, Email: {email}"
                
                # Verify admin role
                if role != 'admin':
                    success = False
                    details += " - CRITICAL: User is not admin"
                    
                # Verify correct email
                if email != 'admin@squiz.com':
                    success = False
                    details += " - CRITICAL: Wrong admin email"
                    
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Authentication (admin@squiz.com)", success, details)
        except Exception as e:
            return self.log_test("Admin Authentication (admin@squiz.com)", False, f"Error: {str(e)}")

    def test_auth_me_endpoint(self):
        """Test /auth/me endpoint for frontend authentication checks"""
        if not self.admin_token:
            return self.log_test("Auth Me Endpoint", False, "No admin token available")
            
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
                details += f", User ID: {data.get('id', 'Unknown')[:8]}..."
                details += f", Role: {data.get('role', 'Unknown')}"
                details += f", Email: {data.get('email', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Auth Me Endpoint", success, details)
        except Exception as e:
            return self.log_test("Auth Me Endpoint", False, f"Error: {str(e)}")

    def test_basic_quiz_creation(self):
        """Test basic quiz creation functionality"""
        if not self.admin_token:
            return self.log_test("Basic Quiz Creation", False, "No admin token available")
            
        quiz_data = {
            "title": "Production Test Quiz",
            "description": "A test quiz for production readiness verification",
            "category": "Production Testing",
            "subject": "System Verification",
            "subcategory": "Backend Testing",
            "questions": [
                {
                    "question_text": "What is the primary purpose of this quiz?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "Entertainment", "is_correct": False},
                        {"text": "Production Testing", "is_correct": True},
                        {"text": "User Training", "is_correct": False},
                        {"text": "Data Collection", "is_correct": False}
                    ],
                    "points": 1
                },
                {
                    "question_text": "Which backend framework is being tested?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "Django", "is_correct": False},
                        {"text": "Flask", "is_correct": False},
                        {"text": "FastAPI", "is_correct": True},
                        {"text": "Express", "is_correct": False}
                    ],
                    "points": 1
                }
            ],
            "min_pass_percentage": 60.0,
            "is_public": False
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
                details += f", Quiz ID: {self.created_quiz_id[:8]}..."
                details += f", Questions: {quiz.get('total_questions', 0)}"
                details += f", Points: {quiz.get('total_points', 0)}"
                details += f", Draft: {quiz.get('is_draft', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Basic Quiz Creation", success, details)
        except Exception as e:
            return self.log_test("Basic Quiz Creation", False, f"Error: {str(e)}")

    def test_quiz_publishing(self):
        """Test quiz publishing functionality"""
        if not self.admin_token or not self.created_quiz_id:
            return self.log_test("Quiz Publishing", False, "No admin token or quiz ID available")
            
        try:
            response = requests.post(
                f"{self.api_url}/admin/quiz/{self.created_quiz_id}/publish",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Quiz Publishing", success, details)
        except Exception as e:
            return self.log_test("Quiz Publishing", False, f"Error: {str(e)}")

    def test_quiz_retrieval(self):
        """Test quiz retrieval functionality"""
        if not self.admin_token:
            return self.log_test("Quiz Retrieval", False, "No admin token available")
            
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
                details += f", Total Quizzes: {len(quizzes)}"
                
                # Find our created quiz
                created_quiz = None
                for quiz in quizzes:
                    if quiz.get('id') == self.created_quiz_id:
                        created_quiz = quiz
                        break
                
                if created_quiz:
                    details += f", Created Quiz Found: Yes"
                    details += f", Title: {created_quiz.get('title', 'Unknown')}"
                    details += f", Published: {not created_quiz.get('is_draft', True)}"
                else:
                    details += f", Created Quiz Found: No"
                    
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Quiz Retrieval", success, details)
        except Exception as e:
            return self.log_test("Quiz Retrieval", False, f"Error: {str(e)}")

    def test_user_registration_and_login(self):
        """Test user registration and login functionality"""
        # Test user registration
        user_data = {
            "name": f"Production Test User {self.test_user_id}",
            "email": f"testuser{self.test_user_id}@squiz.test",
            "password": "testpass123"
        }
        
        try:
            # Register user
            reg_response = requests.post(
                f"{self.api_url}/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if reg_response.status_code != 200:
                error_details = f"Registration failed: {reg_response.status_code}"
                try:
                    error_data = reg_response.json()
                    error_details += f", Error: {error_data}"
                except:
                    error_details += f", Response: {reg_response.text[:200]}"
                return self.log_test("User Registration & Login", False, error_details)
            
            # Login user
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
            details = f"Registration: 200, Login: {login_response.status_code}"
            
            if success:
                data = login_response.json()
                self.user_token = data.get('access_token')
                user_info = data.get('user', {})
                details += f", Role: {user_info.get('role', 'Unknown')}"
                details += f", Name: {user_info.get('name', 'Unknown')}"
            else:
                details += f", Response: {login_response.text[:200]}"
                
            return self.log_test("User Registration & Login", success, details)
        except Exception as e:
            return self.log_test("User Registration & Login", False, f"Error: {str(e)}")

    def test_user_quiz_access(self):
        """Test user access to published quizzes"""
        if not self.user_token:
            return self.log_test("User Quiz Access", False, "No user token available")
            
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
                details += f", Available Quizzes: {len(quizzes)}"
                
                # Check if our published quiz is visible to users
                published_quiz_visible = any(
                    quiz.get('id') == self.created_quiz_id 
                    for quiz in quizzes
                )
                details += f", Our Quiz Visible: {published_quiz_visible}"
                
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Quiz Access", success, details)
        except Exception as e:
            return self.log_test("User Quiz Access", False, f"Error: {str(e)}")

    def test_quiz_attempt_submission(self):
        """Test quiz attempt submission"""
        if not self.user_token or not self.created_quiz_id:
            return self.log_test("Quiz Attempt Submission", False, "No user token or quiz ID available")

        attempt_data = {
            "quiz_id": self.created_quiz_id,
            "answers": ["Production Testing", "FastAPI"]  # Correct answers
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
                score = result.get('score', 0)
                total = result.get('total_questions', 0)
                percentage = result.get('percentage', 0)
                passed = result.get('passed', False)
                
                details += f", Score: {score}/{total}"
                details += f", Percentage: {percentage:.1f}%"
                details += f", Passed: {passed}"
                
                # Verify expected results
                if score == 2 and total == 2:
                    details += ", Results: Expected"
                else:
                    details += ", Results: Unexpected"
                    
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Quiz Attempt Submission", success, details)
        except Exception as e:
            return self.log_test("Quiz Attempt Submission", False, f"Error: {str(e)}")

    def test_admin_results_access(self):
        """Test admin access to quiz results"""
        if not self.admin_token:
            return self.log_test("Admin Results Access", False, "No admin token available")
            
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
                details += f", Total Results: {len(results)}"
                
                if len(results) > 0:
                    latest_result = results[-1]  # Assuming latest is last
                    details += f", Latest Score: {latest_result.get('score', 0)}"
                    details += f", User: {latest_result.get('user', {}).get('name', 'Unknown')}"
                    
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Results Access", success, details)
        except Exception as e:
            return self.log_test("Admin Results Access", False, f"Error: {str(e)}")

    def test_role_based_access_control(self):
        """Test role-based access control"""
        if not self.user_token:
            return self.log_test("Role-Based Access Control", False, "No user token available")
            
        try:
            # User should NOT be able to access admin endpoints
            response = requests.get(
                f"{self.api_url}/admin/users",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            # Should return 403 Forbidden
            success = response.status_code == 403
            details = f"User->Admin Access: {response.status_code} (Expected 403)"
            
            if not success:
                details += " - CRITICAL: User can access admin endpoints"
                
            return self.log_test("Role-Based Access Control", success, details)
        except Exception as e:
            return self.log_test("Role-Based Access Control", False, f"Error: {str(e)}")

    def test_api_response_times(self):
        """Test API response times for performance"""
        endpoints_to_test = [
            ("/health", None),
            ("/auth/me", self.admin_token),
            ("/admin/quizzes", self.admin_token),
            ("/quizzes", self.user_token)
        ]
        
        response_times = []
        all_fast = True
        
        for endpoint, token in endpoints_to_test:
            if token is None and endpoint != "/health":
                continue
                
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.api_url}{endpoint}",
                    headers=self.get_auth_headers(token),
                    timeout=10
                )
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                response_times.append(response_time)
                
                if response_time > 2000:  # More than 2 seconds is concerning
                    all_fast = False
                    
            except Exception:
                all_fast = False
                response_times.append(999999)  # Mark as very slow
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        details = f"Average: {avg_response_time:.0f}ms, Max: {max(response_times):.0f}ms"
        
        success = all_fast and avg_response_time < 1000  # Average should be under 1 second
        
        return self.log_test("API Response Times", success, details)

    def run_production_tests(self):
        """Run all production readiness tests"""
        print("🚀 Starting Squiz Backend Production Readiness Tests")
        print(f"📍 Testing Backend URL: {self.base_url}")
        print("=" * 70)
        
        # Critical production tests
        self.test_health_check_render_ready()
        self.test_database_connectivity()
        self.test_cors_configuration()
        
        # Authentication tests
        self.test_admin_authentication_squiz()
        self.test_auth_me_endpoint()
        
        # Core functionality tests
        self.test_basic_quiz_creation()
        self.test_quiz_publishing()
        self.test_quiz_retrieval()
        
        # User functionality tests
        self.test_user_registration_and_login()
        self.test_user_quiz_access()
        self.test_quiz_attempt_submission()
        
        # Admin functionality tests
        self.test_admin_results_access()
        self.test_role_based_access_control()
        
        # Performance tests
        self.test_api_response_times()
        
        # Summary
        print("=" * 70)
        print(f"🎯 Production Readiness Test Results:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("✅ ALL TESTS PASSED - Backend is READY for Render deployment!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"❌ {failed_tests} TESTS FAILED - Backend needs fixes before deployment")
            return False

if __name__ == "__main__":
    tester = SquizProductionTester()
    success = tester.run_production_tests()
    sys.exit(0 if success else 1)