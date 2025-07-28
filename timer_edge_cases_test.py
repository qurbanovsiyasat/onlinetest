#!/usr/bin/env python3
"""
Timer Edge Cases Testing for Squiz Platform
Additional edge case tests for timer functionality
"""

import requests
import json
import sys
import time
from datetime import datetime
import uuid

class TimerEdgeCasesTester:
    def __init__(self, base_url=None):
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

    def setup_auth(self):
        """Setup authentication for tests"""
        # Admin login
        login_data = {"email": "admin@squiz.com", "password": "admin123"}
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                self.admin_token = response.json().get('access_token')
            else:
                return False
        except:
            return False

        # User registration and login
        user_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"edgetest{user_id}@test.com",
            "name": f"Edge Test User {user_id}",
            "password": "testpass123"
        }
        
        try:
            # Register
            response = requests.post(f"{self.api_url}/auth/register", json=user_data, timeout=10)
            if response.status_code != 200:
                return False
            
            # Login
            login_data = {"email": user_data["email"], "password": user_data["password"]}
            response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                self.user_token = response.json().get('access_token')
                return True
        except:
            return False
        
        return False

    def test_multiple_active_sessions_prevention(self):
        """Test that users cannot create multiple active sessions for the same quiz"""
        # Create a test quiz
        quiz_data = {
            "title": "Multiple Sessions Test Quiz",
            "description": "Testing multiple session prevention",
            "category": "Testing",
            "subject": "Edge Cases",
            "subcategory": "Sessions",
            "time_limit_minutes": 5,
            "questions": [
                {
                    "question_text": "Test question",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "A", "is_correct": True},
                        {"text": "B", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
                }
            ]
        }
        
        try:
            # Create and publish quiz
            response = requests.post(f"{self.api_url}/admin/quiz", json=quiz_data, headers=self.get_auth_headers(self.admin_token), timeout=10)
            if response.status_code != 200:
                return self.log_test("Create Multiple Sessions Test Quiz", False, f"Status: {response.status_code}")
            
            quiz_id = response.json().get('id')
            
            # Publish quiz
            response = requests.post(f"{self.api_url}/admin/quiz/{quiz_id}/publish", headers=self.get_auth_headers(self.admin_token), timeout=10)
            if response.status_code != 200:
                return self.log_test("Publish Multiple Sessions Test Quiz", False, f"Status: {response.status_code}")
            
            # Start first session
            session_data = {"quiz_id": quiz_id}
            response = requests.post(f"{self.api_url}/quiz-session/start", json=session_data, headers=self.get_auth_headers(self.user_token), timeout=10)
            if response.status_code != 200:
                return self.log_test("Start First Session", False, f"Status: {response.status_code}")
            
            first_session_id = response.json().get('id')
            
            # Try to start second session (should fail)
            response = requests.post(f"{self.api_url}/quiz-session/start", json=session_data, headers=self.get_auth_headers(self.user_token), timeout=10)
            if response.status_code == 400:
                return self.log_test("Multiple Active Sessions Prevention", True, f"Correctly prevented second session: {response.status_code}")
            else:
                return self.log_test("Multiple Active Sessions Prevention", False, f"Should have failed with 400, got: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Multiple Active Sessions Prevention", False, f"Error: {str(e)}")

    def test_session_pause_resume(self):
        """Test session pause and resume functionality"""
        # Create a test quiz
        quiz_data = {
            "title": "Pause Resume Test Quiz",
            "description": "Testing pause/resume functionality",
            "category": "Testing",
            "subject": "Edge Cases",
            "subcategory": "Pause Resume",
            "time_limit_minutes": 10,
            "questions": [
                {
                    "question_text": "Pause test question",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "A", "is_correct": True},
                        {"text": "B", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
                }
            ]
        }
        
        try:
            # Create and publish quiz
            response = requests.post(f"{self.api_url}/admin/quiz", json=quiz_data, headers=self.get_auth_headers(self.admin_token), timeout=10)
            if response.status_code != 200:
                return self.log_test("Create Pause Resume Test Quiz", False, f"Status: {response.status_code}")
            
            quiz_id = response.json().get('id')
            
            # Publish quiz
            response = requests.post(f"{self.api_url}/admin/quiz/{quiz_id}/publish", headers=self.get_auth_headers(self.admin_token), timeout=10)
            if response.status_code != 200:
                return self.log_test("Publish Pause Resume Test Quiz", False, f"Status: {response.status_code}")
            
            # Start and activate session
            session_data = {"quiz_id": quiz_id}
            response = requests.post(f"{self.api_url}/quiz-session/start", json=session_data, headers=self.get_auth_headers(self.user_token), timeout=10)
            if response.status_code != 200:
                return self.log_test("Start Pause Resume Session", False, f"Status: {response.status_code}")
            
            session_id = response.json().get('id')
            
            # Activate session
            response = requests.post(f"{self.api_url}/quiz-session/{session_id}/activate", headers=self.get_auth_headers(self.user_token), timeout=10)
            if response.status_code != 200:
                return self.log_test("Activate Pause Resume Session", False, f"Status: {response.status_code}")
            
            # Pause session
            response = requests.get(f"{self.api_url}/quiz-session/{session_id}/pause", headers=self.get_auth_headers(self.user_token), timeout=10)
            if response.status_code == 200:
                self.log_test("Pause Session", True, f"Status: {response.status_code}")
            else:
                self.log_test("Pause Session", False, f"Status: {response.status_code}")
            
            # Resume session
            response = requests.get(f"{self.api_url}/quiz-session/{session_id}/resume", headers=self.get_auth_headers(self.user_token), timeout=10)
            if response.status_code == 200:
                return self.log_test("Resume Session", True, f"Status: {response.status_code}")
            else:
                return self.log_test("Resume Session", False, f"Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Session Pause Resume", False, f"Error: {str(e)}")

    def test_user_quiz_sessions_list(self):
        """Test getting user's quiz sessions"""
        try:
            response = requests.get(f"{self.api_url}/my-quiz-sessions", headers=self.get_auth_headers(self.user_token), timeout=10)
            if response.status_code == 200:
                sessions = response.json()
                return self.log_test("Get User Quiz Sessions", True, f"Found {len(sessions)} sessions")
            else:
                return self.log_test("Get User Quiz Sessions", False, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Get User Quiz Sessions", False, f"Error: {str(e)}")

    def test_admin_cannot_take_quiz(self):
        """Test that admin users cannot take quizzes"""
        # Create a test quiz
        quiz_data = {
            "title": "Admin Block Test Quiz",
            "description": "Testing admin blocking from taking quizzes",
            "category": "Testing",
            "subject": "Edge Cases",
            "subcategory": "Admin Block",
            "time_limit_minutes": 5,
            "questions": [
                {
                    "question_text": "Admin block test question",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "A", "is_correct": True},
                        {"text": "B", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
                }
            ]
        }
        
        try:
            # Create and publish quiz
            response = requests.post(f"{self.api_url}/admin/quiz", json=quiz_data, headers=self.get_auth_headers(self.admin_token), timeout=10)
            if response.status_code != 200:
                return self.log_test("Create Admin Block Test Quiz", False, f"Status: {response.status_code}")
            
            quiz_id = response.json().get('id')
            
            # Publish quiz
            response = requests.post(f"{self.api_url}/admin/quiz/{quiz_id}/publish", headers=self.get_auth_headers(self.admin_token), timeout=10)
            if response.status_code != 200:
                return self.log_test("Publish Admin Block Test Quiz", False, f"Status: {response.status_code}")
            
            # Try to start session as admin (should fail)
            session_data = {"quiz_id": quiz_id}
            response = requests.post(f"{self.api_url}/quiz-session/start", json=session_data, headers=self.get_auth_headers(self.admin_token), timeout=10)
            if response.status_code == 403:
                return self.log_test("Admin Cannot Take Quiz", True, f"Correctly blocked admin: {response.status_code}")
            else:
                return self.log_test("Admin Cannot Take Quiz", False, f"Should have failed with 403, got: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Admin Cannot Take Quiz", False, f"Error: {str(e)}")

    def test_invalid_quiz_session_access(self):
        """Test accessing non-existent quiz sessions"""
        fake_session_id = str(uuid.uuid4())
        
        try:
            # Try to get status of non-existent session
            response = requests.get(f"{self.api_url}/quiz-session/{fake_session_id}/status", headers=self.get_auth_headers(self.user_token), timeout=10)
            if response.status_code == 404:
                return self.log_test("Invalid Quiz Session Access", True, f"Correctly returned 404 for non-existent session")
            else:
                return self.log_test("Invalid Quiz Session Access", False, f"Should have returned 404, got: {response.status_code}")
        except Exception as e:
            return self.log_test("Invalid Quiz Session Access", False, f"Error: {str(e)}")

    def run_edge_case_tests(self):
        """Run all edge case tests"""
        print("🧪 Starting Timer Edge Cases Testing")
        print("=" * 50)
        
        if not self.setup_auth():
            print("❌ Authentication setup failed - cannot continue")
            return False
        
        self.test_multiple_active_sessions_prevention()
        self.test_session_pause_resume()
        self.test_user_quiz_sessions_list()
        self.test_admin_cannot_take_quiz()
        self.test_invalid_quiz_session_access()
        
        # Summary
        print("\n" + "=" * 50)
        print(f"🎯 EDGE CASES TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("✅ ALL EDGE CASE TESTS PASSED!")
            return True
        else:
            print(f"❌ {self.tests_run - self.tests_passed} TESTS FAILED")
            return False

if __name__ == "__main__":
    tester = TimerEdgeCasesTester()
    success = tester.run_edge_case_tests()
    sys.exit(0 if success else 1)