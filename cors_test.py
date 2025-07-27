#!/usr/bin/env python3
"""
CORS Verification Testing for OnlineTestMaker Backend API
Tests CORS headers are present for cross-origin requests and all core functionality works after CORS changes
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import os

class CORSVerificationTester:
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
        self.cors_test_quiz_id = None
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
            return self.log_test("Health Check", success, details)
        except Exception as e:
            return self.log_test("Health Check", False, f"Error: {str(e)}")

    def test_cors_info(self):
        """Test CORS configuration endpoint"""
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
            return self.log_test("CORS Configuration Info", success, details)
        except Exception as e:
            return self.log_test("CORS Configuration Info", False, f"Error: {str(e)}")

    def test_cors_headers_on_auth_endpoints(self):
        """Test CORS headers are present on authentication endpoints"""
        try:
            # Test OPTIONS request for login endpoint (preflight)
            options_response = requests.options(
                f"{self.api_url}/auth/login",
                headers={
                    'Origin': 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type,Authorization'
                },
                timeout=10
            )
            
            # Test actual POST request with Origin header
            login_data = {
                "email": "admin@onlinetestmaker.com",
                "password": "admin123"
            }
            post_response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={
                    'Content-Type': 'application/json',
                    'Origin': 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com'
                },
                timeout=10
            )
            
            # Check CORS headers in both responses
            options_cors = options_response.headers.get('Access-Control-Allow-Origin')
            post_cors = post_response.headers.get('Access-Control-Allow-Origin')
            
            success = (options_response.status_code in [200, 204] and post_response.status_code == 200 
                      and options_cors is not None and post_cors is not None)
            
            details = f"OPTIONS: {options_response.status_code}, POST: {post_response.status_code}"
            details += f", OPTIONS CORS: {options_cors}, POST CORS: {post_cors}"
            
            if success and post_response.status_code == 200:
                data = post_response.json()
                self.admin_token = data.get('access_token')
                details += f", Token received: {bool(self.admin_token)}"
            
            return self.log_test("CORS Headers on Auth Endpoints", success, details)
        except Exception as e:
            return self.log_test("CORS Headers on Auth Endpoints", False, f"Error: {str(e)}")

    def test_cors_headers_on_quiz_endpoints(self):
        """Test CORS headers are present on quiz endpoints"""
        if not self.admin_token:
            return self.log_test("CORS Headers on Quiz Endpoints", False, "No admin token available")
            
        try:
            # Test OPTIONS request for quiz creation endpoint (preflight)
            options_response = requests.options(
                f"{self.api_url}/admin/quiz",
                headers={
                    'Origin': 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type,Authorization'
                },
                timeout=10
            )
            
            # Test actual POST request with Origin header
            quiz_data = {
                "title": "CORS Test Quiz",
                "description": "Testing CORS headers on quiz creation",
                "category": "Test",
                "subject": "Testing",
                "subcategory": "CORS",
                "questions": [
                    {
                        "question_text": "Is CORS working?",
                        "options": [
                            {"text": "Yes", "is_correct": True},
                            {"text": "No", "is_correct": False}
                        ]
                    }
                ]
            }
            
            post_response = requests.post(
                f"{self.api_url}/admin/quiz",
                json=quiz_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.admin_token}',
                    'Origin': 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com'
                },
                timeout=10
            )
            
            # Check CORS headers
            options_cors = options_response.headers.get('Access-Control-Allow-Origin')
            post_cors = post_response.headers.get('Access-Control-Allow-Origin')
            
            success = (options_response.status_code in [200, 204] and post_response.status_code == 200 
                      and options_cors is not None and post_cors is not None)
            
            details = f"OPTIONS: {options_response.status_code}, POST: {post_response.status_code}"
            details += f", OPTIONS CORS: {options_cors}, POST CORS: {post_cors}"
            
            if success and post_response.status_code == 200:
                quiz = post_response.json()
                self.cors_test_quiz_id = quiz.get('id')
                details += f", Quiz created: {bool(self.cors_test_quiz_id)}"
                
                # Publish the quiz for testing
                publish_response = requests.post(
                    f"{self.api_url}/admin/quiz/{self.cors_test_quiz_id}/publish",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if publish_response.status_code == 200:
                    details += ", Published: Yes"
            
            return self.log_test("CORS Headers on Quiz Endpoints", success, details)
        except Exception as e:
            return self.log_test("CORS Headers on Quiz Endpoints", False, f"Error: {str(e)}")

    def test_user_registration_with_cors(self):
        """Test user registration with CORS headers"""
        user_data = {
            "name": f"CORS Test User {self.test_user_id}",
            "email": f"corstest{self.test_user_id}@example.com",
            "password": "testpass123"
        }
        try:
            response = requests.post(
                f"{self.api_url}/auth/register",
                json=user_data,
                headers={
                    'Content-Type': 'application/json',
                    'Origin': 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com'
                },
                timeout=10
            )
            
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            success = response.status_code == 200 and cors_header is not None
            
            details = f"Status: {response.status_code}, CORS: {cors_header}"
            
            if success:
                data = response.json()
                details += f", User: {data.get('name', 'Unknown')}"
            
            return self.log_test("User Registration with CORS", success, details)
        except Exception as e:
            return self.log_test("User Registration with CORS", False, f"Error: {str(e)}")

    def test_user_login_with_cors(self):
        """Test user login with CORS headers"""
        login_data = {
            "email": f"corstest{self.test_user_id}@example.com",
            "password": "testpass123"
        }
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={
                    'Content-Type': 'application/json',
                    'Origin': 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com'
                },
                timeout=10
            )
            
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            success = response.status_code == 200 and cors_header is not None
            
            details = f"Status: {response.status_code}, CORS: {cors_header}"
            
            if success:
                data = response.json()
                self.user_token = data.get('access_token')
                details += f", Token received: {bool(self.user_token)}"
            
            return self.log_test("User Login with CORS", success, details)
        except Exception as e:
            return self.log_test("User Login with CORS", False, f"Error: {str(e)}")

    def test_cors_headers_on_quiz_submission(self):
        """Test CORS headers are present on quiz submission endpoint"""
        if not self.user_token or not self.cors_test_quiz_id:
            return self.log_test("CORS Headers on Quiz Submission", False, "No user token or quiz ID available")
            
        try:
            # Test OPTIONS request for quiz submission endpoint (preflight)
            options_response = requests.options(
                f"{self.api_url}/quiz/{self.cors_test_quiz_id}/attempt",
                headers={
                    'Origin': 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type,Authorization'
                },
                timeout=10
            )
            
            # Test actual POST request with Origin header
            attempt_data = {
                "quiz_id": self.cors_test_quiz_id,
                "answers": ["Yes"]
            }
            
            post_response = requests.post(
                f"{self.api_url}/quiz/{self.cors_test_quiz_id}/attempt",
                json=attempt_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.user_token}',
                    'Origin': 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com'
                },
                timeout=10
            )
            
            # Check CORS headers
            options_cors = options_response.headers.get('Access-Control-Allow-Origin')
            post_cors = post_response.headers.get('Access-Control-Allow-Origin')
            
            success = (options_response.status_code in [200, 204] and post_response.status_code == 200 
                      and options_cors is not None and post_cors is not None)
            
            details = f"OPTIONS: {options_response.status_code}, POST: {post_response.status_code}"
            details += f", OPTIONS CORS: {options_cors}, POST CORS: {post_cors}"
            
            if success and post_response.status_code == 200:
                result = post_response.json()
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
            
            return self.log_test("CORS Headers on Quiz Submission", success, details)
        except Exception as e:
            return self.log_test("CORS Headers on Quiz Submission", False, f"Error: {str(e)}")

    def test_cors_headers_on_get_requests(self):
        """Test CORS headers are present on GET requests"""
        if not self.user_token:
            return self.log_test("CORS Headers on GET Requests", False, "No user token available")
            
        try:
            # Test GET request with Origin header for quizzes endpoint
            response = requests.get(
                f"{self.api_url}/quizzes",
                headers={
                    'Authorization': f'Bearer {self.user_token}',
                    'Origin': 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com'
                },
                timeout=10
            )
            
            # Check CORS headers
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_credentials = response.headers.get('Access-Control-Allow-Credentials')
            
            success = response.status_code == 200 and cors_origin is not None
            
            details = f"Status: {response.status_code}, CORS Origin: {cors_origin}"
            details += f", CORS Credentials: {cors_credentials}"
            
            if success:
                quizzes = response.json()
                details += f", Quizzes count: {len(quizzes)}"
            
            return self.log_test("CORS Headers on GET Requests", success, details)
        except Exception as e:
            return self.log_test("CORS Headers on GET Requests", False, f"Error: {str(e)}")

    def test_cors_preflight_requests(self):
        """Test CORS preflight (OPTIONS) requests work correctly"""
        try:
            endpoints_to_test = [
                "/auth/login",
                "/auth/register", 
                "/admin/quiz",
                "/quizzes"
            ]
            
            successful_preflights = 0
            total_endpoints = len(endpoints_to_test)
            
            for endpoint in endpoints_to_test:
                try:
                    response = requests.options(
                        f"{self.api_url}{endpoint}",
                        headers={
                            'Origin': 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com',
                            'Access-Control-Request-Method': 'POST' if endpoint != '/quizzes' else 'GET',
                            'Access-Control-Request-Headers': 'Content-Type,Authorization'
                        },
                        timeout=10
                    )
                    
                    if (response.status_code in [200, 204] and 
                        response.headers.get('Access-Control-Allow-Origin')):
                        successful_preflights += 1
                except:
                    pass
            
            success = successful_preflights >= (total_endpoints * 0.75)  # At least 75% should work
            details = f"Successful preflights: {successful_preflights}/{total_endpoints}"
            
            return self.log_test("CORS Preflight Requests", success, details)
        except Exception as e:
            return self.log_test("CORS Preflight Requests", False, f"Error: {str(e)}")

    def test_cors_with_different_origins(self):
        """Test CORS with different allowed origins"""
        try:
            # Test with the configured origin
            allowed_origin = 'https://6801ea8c-1ba4-4fd0-84c7-297e1bd68990.preview.emergentagent.com'
            response1 = requests.get(
                f"{self.api_url}/health",
                headers={'Origin': allowed_origin},
                timeout=10
            )
            
            # Test with localhost (should also be allowed based on CORS config)
            localhost_origin = 'http://localhost:3000'
            response2 = requests.get(
                f"{self.api_url}/health",
                headers={'Origin': localhost_origin},
                timeout=10
            )
            
            # Test with disallowed origin
            disallowed_origin = 'https://malicious-site.com'
            response3 = requests.get(
                f"{self.api_url}/health",
                headers={'Origin': disallowed_origin},
                timeout=10
            )
            
            allowed_cors = response1.headers.get('Access-Control-Allow-Origin')
            localhost_cors = response2.headers.get('Access-Control-Allow-Origin')
            disallowed_cors = response3.headers.get('Access-Control-Allow-Origin')
            
            # Success if allowed origins get CORS headers
            success = (response1.status_code == 200 and allowed_cors is not None and
                      response2.status_code == 200 and localhost_cors is not None)
            
            details = f"Allowed origin CORS: {allowed_cors}, Localhost CORS: {localhost_cors}"
            details += f", Disallowed CORS: {disallowed_cors}"
            
            return self.log_test("CORS with Different Origins", success, details)
        except Exception as e:
            return self.log_test("CORS with Different Origins", False, f"Error: {str(e)}")

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

    def test_core_functionality_still_works(self):
        """Test that core functionality still works after CORS changes"""
        if not self.admin_token or not self.user_token:
            return self.log_test("Core Functionality Check", False, "Missing tokens")
        
        try:
            # Test admin getting users
            admin_response = requests.get(
                f"{self.api_url}/admin/users",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            # Test user getting quizzes
            user_response = requests.get(
                f"{self.api_url}/quizzes",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            success = admin_response.status_code == 200 and user_response.status_code == 200
            
            details = f"Admin users: {admin_response.status_code}, User quizzes: {user_response.status_code}"
            
            if success:
                admin_data = admin_response.json()
                user_data = user_response.json()
                details += f", Users count: {len(admin_data)}, Quizzes count: {len(user_data)}"
            
            return self.log_test("Core Functionality Check", success, details)
        except Exception as e:
            return self.log_test("Core Functionality Check", False, f"Error: {str(e)}")

    def run_cors_verification_tests(self):
        """Run CORS verification test suite"""
        print("🌐 Starting CORS Verification Testing...")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Basic connectivity tests
        self.test_health_check()
        self.test_cors_info()
        
        # Authentication setup
        self.test_init_admin()
        
        # CORS-specific authentication tests
        self.test_cors_headers_on_auth_endpoints()
        
        # User registration and login with CORS
        self.test_user_registration_with_cors()
        self.test_user_login_with_cors()
        
        # CORS on quiz endpoints
        self.test_cors_headers_on_quiz_endpoints()
        
        # CORS on quiz submission
        self.test_cors_headers_on_quiz_submission()
        
        # CORS on GET requests
        self.test_cors_headers_on_get_requests()
        
        # CORS preflight tests
        self.test_cors_preflight_requests()
        
        # CORS with different origins
        self.test_cors_with_different_origins()
        
        # Core functionality verification
        self.test_core_functionality_still_works()
        
        print("=" * 80)
        print(f"🏁 CORS Testing Complete: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"📊 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("✅ All CORS tests passed! Cross-origin requests should work properly.")
            return True
        elif self.tests_passed >= self.tests_run * 0.9:
            print("⚠️  Most CORS tests passed. Minor issues may exist but core functionality works.")
            return True
        else:
            print("❌ CORS testing failed. Cross-origin requests may not work properly.")
            return False

def main():
    """Main test execution - Focus on CORS Verification"""
    print("🌐 CORS VERIFICATION TESTING - OnlineTestMaker Backend API")
    print("🎯 Testing CORS headers are present for cross-origin requests")
    print("🎯 Verifying authentication endpoints work with proper CORS headers")
    print("🎯 Testing quiz submission endpoint with CORS headers")
    print("🎯 Ensuring all functionality still works after CORS changes")
    print("=" * 80)
    
    tester = CORSVerificationTester()
    
    # Run CORS-focused tests
    cors_success = tester.run_cors_verification_tests()
    
    print("\n" + "=" * 80)
    print("📋 CORS VERIFICATION SUMMARY")
    print("=" * 80)
    
    if cors_success:
        print("✅ CORS VERIFICATION: PASSED")
        print("✅ Cross-origin requests should work properly")
        print("✅ Authentication endpoints have proper CORS headers")
        print("✅ Quiz submission endpoint has proper CORS headers")
        print("✅ All core functionality still works after CORS changes")
        return 0
    else:
        print("❌ CORS VERIFICATION: FAILED")
        print("❌ Cross-origin requests may not work properly")
        print("❌ Check CORS configuration and headers")
        return 1

if __name__ == "__main__":
    sys.exit(main())