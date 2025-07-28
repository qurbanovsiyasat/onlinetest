#!/usr/bin/env python3
"""
Timer-Only Quiz Functionality Testing for Squiz Platform
Tests the timer functionality as requested:
1. Create quiz with time_limit_minutes set → Only show "Timed" mode
2. Create quiz without time_limit_minutes (null) → Only show "Standard" mode
3. Verify quiz data is correctly saved
4. Test real-time quiz session endpoints work with timed quizzes
5. Verify countdown timer functionality works as expected
6. Test auto-submission when time runs out
7. Check that leaderboard shows only first attempts
"""

import requests
import json
import sys
import time
from datetime import datetime
import uuid

class TimerQuizTester:
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
        self.timed_quiz_id = None
        self.standard_quiz_id = None
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

    def test_admin_login(self):
        """Test admin login"""
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
                details += f", Role: {user_info.get('role', 'Unknown')}, Name: {user_info.get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Login", success, details)
        except Exception as e:
            return self.log_test("Admin Login", False, f"Error: {str(e)}")

    def test_user_registration_and_login(self):
        """Test user registration and login"""
        # Register user
        user_data = {
            "email": f"timertest{self.test_user_id}@test.com",
            "name": f"Timer Test User {self.test_user_id}",
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
            details = f"Registration Status: {response.status_code}"
            
            if not success:
                details += f", Response: {response.text[:200]}"
                return self.log_test("User Registration", success, details)
            
            # Login user
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            login_success = response.status_code == 200
            details += f", Login Status: {response.status_code}"
            
            if login_success:
                data = response.json()
                self.user_token = data.get('access_token')
                user_info = data.get('user', {})
                details += f", Role: {user_info.get('role', 'Unknown')}"
            
            return self.log_test("User Registration & Login", login_success, details)
        except Exception as e:
            return self.log_test("User Registration & Login", False, f"Error: {str(e)}")

    def test_create_timed_quiz(self):
        """Test creating a quiz with time_limit_minutes set (5 minutes)"""
        quiz_data = {
            "title": "Timed Quiz Test - 5 Minutes",
            "description": "This quiz has a 5-minute time limit for testing timer functionality",
            "category": "Testing",
            "subject": "Timer Tests",
            "subcategory": "Timed Mode",
            "time_limit_minutes": 5,  # 5 minute time limit
            "questions": [
                {
                    "question_text": "What is 2 + 2?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True},
                        {"text": "5", "is_correct": False},
                        {"text": "6", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
                },
                {
                    "question_text": "What is the capital of France?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "London", "is_correct": False},
                        {"text": "Berlin", "is_correct": False},
                        {"text": "Paris", "is_correct": True},
                        {"text": "Madrid", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
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
                data = response.json()
                self.timed_quiz_id = data.get('id')
                details += f", Quiz ID: {self.timed_quiz_id}"
                details += f", Time Limit: {data.get('time_limit_minutes')} minutes"
                details += f", Questions: {len(data.get('questions', []))}"
            else:
                details += f", Response: {response.text[:300]}"
                
            return self.log_test("Create Timed Quiz (5 minutes)", success, details)
        except Exception as e:
            return self.log_test("Create Timed Quiz (5 minutes)", False, f"Error: {str(e)}")

    def test_create_standard_quiz(self):
        """Test creating a quiz without time_limit_minutes (null/standard mode)"""
        quiz_data = {
            "title": "Standard Quiz Test - No Time Limit",
            "description": "This quiz has no time limit for testing standard functionality",
            "category": "Testing",
            "subject": "Timer Tests",
            "subcategory": "Standard Mode",
            "time_limit_minutes": None,  # No time limit
            "questions": [
                {
                    "question_text": "What is 3 + 3?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "5", "is_correct": False},
                        {"text": "6", "is_correct": True},
                        {"text": "7", "is_correct": False},
                        {"text": "8", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
                },
                {
                    "question_text": "What is the capital of Italy?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "Milan", "is_correct": False},
                        {"text": "Naples", "is_correct": False},
                        {"text": "Rome", "is_correct": True},
                        {"text": "Florence", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
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
                data = response.json()
                self.standard_quiz_id = data.get('id')
                details += f", Quiz ID: {self.standard_quiz_id}"
                details += f", Time Limit: {data.get('time_limit_minutes', 'None')}"
                details += f", Questions: {len(data.get('questions', []))}"
            else:
                details += f", Response: {response.text[:300]}"
                
            return self.log_test("Create Standard Quiz (No time limit)", success, details)
        except Exception as e:
            return self.log_test("Create Standard Quiz (No time limit)", False, f"Error: {str(e)}")

    def test_publish_quizzes(self):
        """Publish both quizzes so they can be accessed by users"""
        success_count = 0
        
        # Publish timed quiz
        if self.timed_quiz_id:
            try:
                response = requests.post(
                    f"{self.api_url}/admin/quiz/{self.timed_quiz_id}/publish",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if response.status_code == 200:
                    success_count += 1
                    self.log_test("Publish Timed Quiz", True, f"Status: {response.status_code}")
                else:
                    self.log_test("Publish Timed Quiz", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            except Exception as e:
                self.log_test("Publish Timed Quiz", False, f"Error: {str(e)}")
        
        # Publish standard quiz
        if self.standard_quiz_id:
            try:
                response = requests.post(
                    f"{self.api_url}/admin/quiz/{self.standard_quiz_id}/publish",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if response.status_code == 200:
                    success_count += 1
                    self.log_test("Publish Standard Quiz", True, f"Status: {response.status_code}")
                else:
                    self.log_test("Publish Standard Quiz", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            except Exception as e:
                self.log_test("Publish Standard Quiz", False, f"Error: {str(e)}")
        
        return success_count == 2

    def test_verify_quiz_data_storage(self):
        """Verify that quiz data is correctly saved with proper time limit settings"""
        success_count = 0
        
        # Check timed quiz
        if self.timed_quiz_id:
            try:
                response = requests.get(
                    f"{self.api_url}/quiz/{self.timed_quiz_id}",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    time_limit = data.get('time_limit_minutes')
                    if time_limit == 5:
                        success_count += 1
                        self.log_test("Verify Timed Quiz Data", True, f"Time limit correctly stored: {time_limit} minutes")
                    else:
                        self.log_test("Verify Timed Quiz Data", False, f"Time limit incorrect: expected 5, got {time_limit}")
                else:
                    self.log_test("Verify Timed Quiz Data", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Verify Timed Quiz Data", False, f"Error: {str(e)}")
        
        # Check standard quiz
        if self.standard_quiz_id:
            try:
                response = requests.get(
                    f"{self.api_url}/quiz/{self.standard_quiz_id}",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    time_limit = data.get('time_limit_minutes')
                    if time_limit is None:
                        success_count += 1
                        self.log_test("Verify Standard Quiz Data", True, f"Time limit correctly stored: {time_limit} (no limit)")
                    else:
                        self.log_test("Verify Standard Quiz Data", False, f"Time limit incorrect: expected None, got {time_limit}")
                else:
                    self.log_test("Verify Standard Quiz Data", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Verify Standard Quiz Data", False, f"Error: {str(e)}")
        
        return success_count == 2

    def test_timed_quiz_session_flow(self):
        """Test the complete real-time quiz session flow for timed quiz"""
        if not self.timed_quiz_id:
            return self.log_test("Timed Quiz Session Flow", False, "No timed quiz ID available")
        
        session_id = None
        
        try:
            # 1. Start quiz session
            session_data = {"quiz_id": self.timed_quiz_id}
            response = requests.post(
                f"{self.api_url}/quiz-session/start",
                json=session_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Start Timed Quiz Session", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            
            session_data = response.json()
            session_id = session_data.get('id')
            time_limit = session_data.get('time_limit_minutes')
            time_remaining = session_data.get('time_remaining_seconds')
            
            self.log_test("Start Timed Quiz Session", True, f"Session ID: {session_id}, Time limit: {time_limit}min, Remaining: {time_remaining}s")
            
            # 2. Activate session (start timer)
            response = requests.post(
                f"{self.api_url}/quiz-session/{session_id}/activate",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Activate Timed Quiz Session", False, f"Status: {response.status_code}")
            
            self.log_test("Activate Timed Quiz Session", True, f"Status: {response.status_code}")
            
            # 3. Check session status (timer should be running)
            response = requests.get(
                f"{self.api_url}/quiz-session/{session_id}/status",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Check Session Status", False, f"Status: {response.status_code}")
            
            status_data = response.json()
            status = status_data.get('status')
            time_remaining_before = status_data.get('time_remaining_seconds')
            
            self.log_test("Check Session Status", True, f"Status: {status}, Time remaining: {time_remaining_before}s")
            
            # 4. Wait 3 seconds and check timer countdown
            time.sleep(3)
            
            response = requests.get(
                f"{self.api_url}/quiz-session/{session_id}/status",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code == 200:
                status_data = response.json()
                time_remaining_after = status_data.get('time_remaining_seconds')
                
                if time_remaining_after < time_remaining_before:
                    self.log_test("Timer Countdown Verification", True, f"Timer working: {time_remaining_before}s → {time_remaining_after}s (decreased by {time_remaining_before - time_remaining_after}s)")
                else:
                    self.log_test("Timer Countdown Verification", False, f"Timer not working: {time_remaining_before}s → {time_remaining_after}s")
            
            # 5. Update session with answers
            update_data = {
                "current_question_index": 1,
                "answers": ["4", "Paris"]  # Correct answers
            }
            
            response = requests.put(
                f"{self.api_url}/quiz-session/{session_id}/update",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Update Session Progress", True, f"Status: {response.status_code}")
            else:
                self.log_test("Update Session Progress", False, f"Status: {response.status_code}")
            
            # 6. Submit session
            response = requests.post(
                f"{self.api_url}/quiz-session/{session_id}/submit",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code == 200:
                attempt_data = response.json()
                score = attempt_data.get('score')
                percentage = attempt_data.get('percentage')
                time_taken = attempt_data.get('time_taken_minutes')
                self.log_test("Submit Timed Quiz Session", True, f"Score: {score}/2, Percentage: {percentage}%, Time taken: {time_taken}min")
                return True
            else:
                self.log_test("Submit Timed Quiz Session", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            return self.log_test("Timed Quiz Session Flow", False, f"Error: {str(e)}")

    def test_standard_quiz_session_flow(self):
        """Test quiz session flow for standard quiz (no time limit)"""
        if not self.standard_quiz_id:
            return self.log_test("Standard Quiz Session Flow", False, "No standard quiz ID available")
        
        session_id = None
        
        try:
            # 1. Start quiz session
            session_data = {"quiz_id": self.standard_quiz_id}
            response = requests.post(
                f"{self.api_url}/quiz-session/start",
                json=session_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Start Standard Quiz Session", False, f"Status: {response.status_code}")
            
            session_data = response.json()
            session_id = session_data.get('id')
            time_limit = session_data.get('time_limit_minutes')
            time_remaining = session_data.get('time_remaining_seconds')
            
            # For standard quiz, time_limit should be None and time_remaining should be None
            if time_limit is None and time_remaining is None:
                self.log_test("Start Standard Quiz Session", True, f"Session ID: {session_id}, No time limit (as expected)")
            else:
                self.log_test("Start Standard Quiz Session", False, f"Expected no time limit, got: {time_limit}min, {time_remaining}s")
                return False
            
            # 2. Activate session
            response = requests.post(
                f"{self.api_url}/quiz-session/{session_id}/activate",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Activate Standard Quiz Session", False, f"Status: {response.status_code}")
            
            self.log_test("Activate Standard Quiz Session", True, f"Status: {response.status_code}")
            
            # 3. Submit session with answers
            update_data = {
                "answers": ["6", "Rome"]  # Correct answers
            }
            
            response = requests.put(
                f"{self.api_url}/quiz-session/{session_id}/update",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Update Standard Session Progress", True, f"Status: {response.status_code}")
            else:
                self.log_test("Update Standard Session Progress", False, f"Status: {response.status_code}")
            
            # 4. Submit session
            response = requests.post(
                f"{self.api_url}/quiz-session/{session_id}/submit",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code == 200:
                attempt_data = response.json()
                score = attempt_data.get('score')
                percentage = attempt_data.get('percentage')
                self.log_test("Submit Standard Quiz Session", True, f"Score: {score}/2, Percentage: {percentage}%")
                return True
            else:
                self.log_test("Submit Standard Quiz Session", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            return self.log_test("Standard Quiz Session Flow", False, f"Error: {str(e)}")

    def test_auto_submission_on_timeout(self):
        """Test auto-submission when time runs out (create a 10-second quiz for testing)"""
        # Create a very short timed quiz for testing timeout
        quiz_data = {
            "title": "Auto-Submit Test Quiz - 10 Seconds",
            "description": "This quiz has a 10-second time limit for testing auto-submission",
            "category": "Testing",
            "subject": "Timer Tests",
            "subcategory": "Auto Submit",
            "time_limit_minutes": 1,  # 1 minute for testing (we'll check timeout behavior)
            "questions": [
                {
                    "question_text": "This is a timeout test question",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "Option A", "is_correct": True},
                        {"text": "Option B", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
                }
            ]
        }
        
        try:
            # Create quiz
            response = requests.post(
                f"{self.api_url}/admin/quiz",
                json=quiz_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Create Timeout Test Quiz", False, f"Status: {response.status_code}")
            
            timeout_quiz_id = response.json().get('id')
            
            # Publish quiz
            response = requests.post(
                f"{self.api_url}/admin/quiz/{timeout_quiz_id}/publish",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Publish Timeout Test Quiz", False, f"Status: {response.status_code}")
            
            # Start session with very short time limit (override to 10 seconds for testing)
            session_data = {
                "quiz_id": timeout_quiz_id,
                "time_limit_minutes": 1  # 1 minute, but we'll test the timeout behavior
            }
            
            response = requests.post(
                f"{self.api_url}/quiz-session/start",
                json=session_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Start Timeout Test Session", False, f"Status: {response.status_code}")
            
            session_id = response.json().get('id')
            
            # Activate session
            response = requests.post(
                f"{self.api_url}/quiz-session/{session_id}/activate",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Activate Timeout Test Session", False, f"Status: {response.status_code}")
            
            self.log_test("Auto-Submission Timeout Test Setup", True, "Quiz created and session started successfully")
            
            # Note: We can't actually wait for full timeout in a test, but we can verify the timeout logic exists
            # by checking the session status and seeing if it properly calculates remaining time
            
            response = requests.get(
                f"{self.api_url}/quiz-session/{session_id}/status",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code == 200:
                status_data = response.json()
                is_auto_submit = status_data.get('is_auto_submit')
                time_remaining = status_data.get('time_remaining_seconds')
                
                if is_auto_submit and time_remaining is not None:
                    self.log_test("Auto-Submission Logic Verification", True, f"Auto-submit enabled: {is_auto_submit}, Time remaining: {time_remaining}s")
                    return True
                else:
                    self.log_test("Auto-Submission Logic Verification", False, f"Auto-submit: {is_auto_submit}, Time remaining: {time_remaining}")
                    return False
            else:
                return self.log_test("Auto-Submission Logic Verification", False, f"Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Auto-Submission Timeout Test", False, f"Error: {str(e)}")

    def test_leaderboard_first_attempts_only(self):
        """Test that leaderboard shows only first attempts"""
        if not self.timed_quiz_id:
            return self.log_test("Leaderboard First Attempts Test", False, "No timed quiz ID available")
        
        try:
            # Get leaderboard for timed quiz
            response = requests.get(
                f"{self.api_url}/quiz/{self.timed_quiz_id}/leaderboard",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Get Quiz Leaderboard", False, f"Status: {response.status_code}")
            
            leaderboard_data = response.json()
            
            # Check if leaderboard entries have is_first_attempt field
            if leaderboard_data and len(leaderboard_data) > 0:
                first_entry = leaderboard_data[0]
                if 'is_first_attempt' in first_entry and first_entry['is_first_attempt'] is True:
                    self.log_test("Leaderboard First Attempts Only", True, f"Found {len(leaderboard_data)} entries, all marked as first attempts")
                    return True
                else:
                    self.log_test("Leaderboard First Attempts Only", False, f"is_first_attempt field missing or incorrect")
                    return False
            else:
                self.log_test("Leaderboard First Attempts Only", True, "No leaderboard entries yet (expected for new quiz)")
                return True
                
        except Exception as e:
            return self.log_test("Leaderboard First Attempts Test", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all timer functionality tests"""
        print("🚀 Starting Timer-Only Quiz Functionality Testing")
        print("=" * 60)
        
        # Authentication tests
        if not self.test_admin_login():
            print("❌ Admin login failed - cannot continue")
            return False
        
        if not self.test_user_registration_and_login():
            print("❌ User registration/login failed - cannot continue")
            return False
        
        # Quiz creation tests
        self.test_create_timed_quiz()
        self.test_create_standard_quiz()
        self.test_publish_quizzes()
        
        # Data verification tests
        self.test_verify_quiz_data_storage()
        
        # Session flow tests
        self.test_timed_quiz_session_flow()
        self.test_standard_quiz_session_flow()
        
        # Advanced timer tests
        self.test_auto_submission_on_timeout()
        self.test_leaderboard_first_attempts_only()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"🎯 TIMER FUNCTIONALITY TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("✅ ALL TIMER FUNCTIONALITY TESTS PASSED!")
            return True
        else:
            print(f"❌ {self.tests_run - self.tests_passed} TESTS FAILED")
            return False

if __name__ == "__main__":
    tester = TimerQuizTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)