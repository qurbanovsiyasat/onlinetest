#!/usr/bin/env python3
"""
Timed Quiz Flow Testing for Squiz Platform
Tests the complete timed quiz flow to ensure that after a timed quiz is completed 
(either by user finishing or by auto-submit when time expires), the quiz results 
are properly displayed with all necessary fields for the UserResult component.
"""

import requests
import json
import sys
import time
from datetime import datetime
import uuid

class TimedQuizFlowTester:
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
        self.quiz_session_id = None
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
            "name": f"Timed Quiz Test User {self.test_user_id}",
            "email": f"timeduser{self.test_user_id}@example.com",
            "password": "testpass123"
        }
        try:
            response = requests.post(
                f"{self.api_url}/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code != 200:
                return self.log_test("User Registration and Login", False, f"Registration failed: {response.status_code}")
            
            # Login user
            login_data = {
                "email": f"timeduser{self.test_user_id}@example.com",
                "password": "testpass123"
            }
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
                
            return self.log_test("User Registration and Login", success, details)
        except Exception as e:
            return self.log_test("User Registration and Login", False, f"Error: {str(e)}")

    def test_create_timed_quiz(self):
        """Test creating a timed quiz with short time limit (2 minutes)"""
        if not self.admin_token:
            return self.log_test("Create Timed Quiz", False, "No admin token available")
            
        quiz_data = {
            "title": "Timed Quiz Test - 2 Minutes",
            "description": "A test quiz with 2-minute time limit for testing timed quiz flow",
            "category": "Test Category",
            "subject": "Testing",
            "subcategory": "Timed Tests",
            "time_limit_minutes": 2,  # 2-minute time limit
            "questions": [
                {
                    "question_text": "What is 5 + 3?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "6", "is_correct": False},
                        {"text": "7", "is_correct": False},
                        {"text": "8", "is_correct": True},
                        {"text": "9", "is_correct": False}
                    ],
                    "points": 1
                },
                {
                    "question_text": "What is the capital of Japan?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "Seoul", "is_correct": False},
                        {"text": "Tokyo", "is_correct": True},
                        {"text": "Beijing", "is_correct": False},
                        {"text": "Bangkok", "is_correct": False}
                    ],
                    "points": 1
                },
                {
                    "question_text": "Explain what a variable is in programming.",
                    "question_type": "open_ended",
                    "open_ended_answer": {
                        "expected_answers": [
                            "A variable is a storage location with a name",
                            "A container that holds data values",
                            "A named memory location that stores data"
                        ],
                        "keywords": ["variable", "storage", "data", "memory", "container", "holds"],
                        "case_sensitive": False,
                        "partial_credit": True
                    },
                    "points": 2
                }
            ],
            "min_pass_percentage": 60.0,
            "shuffle_questions": False,
            "shuffle_options": False
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
                self.timed_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.timed_quiz_id}"
                details += f", Time Limit: {quiz.get('time_limit_minutes', 'None')} minutes"
                details += f", Total Questions: {quiz.get('total_questions', 0)}"
                details += f", Total Points: {quiz.get('total_points', 0)}"
                details += f", Is Draft: {quiz.get('is_draft', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Timed Quiz", success, details)
        except Exception as e:
            return self.log_test("Create Timed Quiz", False, f"Error: {str(e)}")

    def test_publish_timed_quiz(self):
        """Test publishing the timed quiz"""
        if not self.admin_token or not self.timed_quiz_id:
            return self.log_test("Publish Timed Quiz", False, "No admin token or quiz ID available")
            
        try:
            response = requests.post(
                f"{self.api_url}/admin/quiz/{self.timed_quiz_id}/publish",
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
                
            return self.log_test("Publish Timed Quiz", success, details)
        except Exception as e:
            return self.log_test("Publish Timed Quiz", False, f"Error: {str(e)}")

    def test_start_quiz_session(self):
        """Test starting a real-time quiz session"""
        if not self.user_token or not self.timed_quiz_id:
            return self.log_test("Start Quiz Session", False, "No user token or quiz ID available")
            
        session_data = {
            "quiz_id": self.timed_quiz_id
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/quiz-session/start",
                json=session_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                session = response.json()
                self.quiz_session_id = session.get('id')
                details += f", Session ID: {self.quiz_session_id}"
                details += f", Status: {session.get('status', 'Unknown')}"
                details += f", Time Limit: {session.get('time_limit_minutes', 'None')} minutes"
                details += f", Time Remaining: {session.get('time_remaining_seconds', 'None')} seconds"
                details += f", Auto Submit: {session.get('is_auto_submit', False)}"
                details += f", Total Questions: {session.get('total_questions', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Start Quiz Session", success, details)
        except Exception as e:
            return self.log_test("Start Quiz Session", False, f"Error: {str(e)}")

    def test_activate_quiz_session(self):
        """Test activating the quiz session (start the timer)"""
        if not self.user_token or not self.quiz_session_id:
            return self.log_test("Activate Quiz Session", False, "No user token or session ID available")
            
        try:
            response = requests.post(
                f"{self.api_url}/quiz-session/{self.quiz_session_id}/activate",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                session = response.json()
                details += f", Status: {session.get('status', 'Unknown')}"
                details += f", Start Time: {session.get('start_time', 'None')}"
                details += f", Time Remaining: {session.get('time_remaining_seconds', 'None')} seconds"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Activate Quiz Session", success, details)
        except Exception as e:
            return self.log_test("Activate Quiz Session", False, f"Error: {str(e)}")

    def test_session_status_with_timer(self):
        """Test getting session status with real-time timer countdown"""
        if not self.user_token or not self.quiz_session_id:
            return self.log_test("Session Status with Timer", False, "No user token or session ID available")
            
        try:
            # Get initial status
            response = requests.get(
                f"{self.api_url}/quiz-session/{self.quiz_session_id}/status",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            if response.status_code != 200:
                return self.log_test("Session Status with Timer", False, f"Initial status failed: {response.status_code}")
            
            initial_session = response.json()
            initial_time = initial_session.get('time_remaining_seconds', 0)
            
            # Wait 3 seconds
            time.sleep(3)
            
            # Get status again to verify timer countdown
            response = requests.get(
                f"{self.api_url}/quiz-session/{self.quiz_session_id}/status",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                session = response.json()
                current_time = session.get('time_remaining_seconds', 0)
                time_diff = initial_time - current_time
                details += f", Initial Time: {initial_time}s, Current Time: {current_time}s"
                details += f", Time Elapsed: {time_diff}s (Expected: ~3s)"
                details += f", Status: {session.get('status', 'Unknown')}"
                
                # Verify timer is counting down
                if time_diff >= 2 and time_diff <= 5:  # Allow some tolerance
                    details += ", Timer Working: Yes"
                else:
                    details += ", Timer Working: No"
                    success = False
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Session Status with Timer", success, details)
        except Exception as e:
            return self.log_test("Session Status with Timer", False, f"Error: {str(e)}")

    def test_update_session_progress(self):
        """Test updating session progress with answers"""
        if not self.user_token or not self.quiz_session_id:
            return self.log_test("Update Session Progress", False, "No user token or session ID available")
            
        update_data = {
            "current_question_index": 1,
            "answers": ["8", "Tokyo"]  # Answers for first two questions
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/quiz-session/{self.quiz_session_id}/update",
                json=update_data,
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
                
            return self.log_test("Update Session Progress", success, details)
        except Exception as e:
            return self.log_test("Update Session Progress", False, f"Error: {str(e)}")

    def test_manual_quiz_completion(self):
        """Test manually completing the quiz before time expires"""
        if not self.user_token or not self.quiz_session_id:
            return self.log_test("Manual Quiz Completion", False, "No user token or session ID available")
            
        # First update with all answers
        update_data = {
            "current_question_index": 2,
            "answers": [
                "8",  # Correct answer for math question
                "Tokyo",  # Correct answer for capital question
                "A variable is a storage location that holds data values in memory"  # Good answer for open-ended
            ]
        }
        
        try:
            # Update session with final answers
            update_response = requests.put(
                f"{self.api_url}/quiz-session/{self.quiz_session_id}/update",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            if update_response.status_code != 200:
                return self.log_test("Manual Quiz Completion", False, f"Update failed: {update_response.status_code}")
            
            # Submit the session
            response = requests.post(
                f"{self.api_url}/quiz-session/{self.quiz_session_id}/submit",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                # Verify all required fields for UserResult component
                required_fields = [
                    'id', 'quiz_id', 'user_id', 'score', 'total_questions', 
                    'percentage', 'question_results', 'earned_points', 
                    'total_possible_points', 'passed'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in result:
                        missing_fields.append(field)
                
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
                details += f", Percentage: {result.get('percentage', 0):.1f}%"
                details += f", Points: {result.get('earned_points', 0)}/{result.get('total_possible_points', 0)}"
                details += f", Passed: {result.get('passed', False)}"
                details += f", Question Results: {len(result.get('question_results', []))}"
                
                if missing_fields:
                    details += f", Missing Fields: {missing_fields}"
                    success = False
                else:
                    details += ", All Required Fields: Present"
                
                # Verify question_results structure
                question_results = result.get('question_results', [])
                if question_results:
                    first_result = question_results[0]
                    result_fields = ['question_number', 'question_text', 'user_answer', 
                                   'correct_answer', 'is_correct', 'points_earned', 'points_possible']
                    missing_result_fields = [f for f in result_fields if f not in first_result]
                    if missing_result_fields:
                        details += f", Missing Result Fields: {missing_result_fields}"
                        success = False
                    else:
                        details += ", Question Result Fields: Complete"
                
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Manual Quiz Completion", success, details)
        except Exception as e:
            return self.log_test("Manual Quiz Completion", False, f"Error: {str(e)}")

    def test_create_auto_submit_quiz(self):
        """Test creating a quiz with very short time limit for auto-submit testing (10 seconds)"""
        if not self.admin_token:
            return self.log_test("Create Auto-Submit Quiz", False, "No admin token available")
            
        quiz_data = {
            "title": "Auto-Submit Test Quiz - 10 Seconds",
            "description": "A test quiz with 10-second time limit for testing auto-submit functionality",
            "category": "Test Category",
            "subject": "Testing",
            "subcategory": "Auto Submit Tests",
            "time_limit_minutes": 1,  # 1 minute (we'll test with shorter session time)
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
                    "points": 1
                }
            ],
            "min_pass_percentage": 50.0
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
                self.auto_submit_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.auto_submit_quiz_id}"
                details += f", Time Limit: {quiz.get('time_limit_minutes', 'None')} minutes"
                
                # Publish immediately
                publish_response = requests.post(
                    f"{self.api_url}/admin/quiz/{self.auto_submit_quiz_id}/publish",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if publish_response.status_code == 200:
                    details += ", Published: Yes"
                else:
                    details += ", Published: Failed"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Auto-Submit Quiz", success, details)
        except Exception as e:
            return self.log_test("Create Auto-Submit Quiz", False, f"Error: {str(e)}")

    def test_auto_submit_flow(self):
        """Test auto-submit functionality when time expires"""
        if not self.user_token or not hasattr(self, 'auto_submit_quiz_id'):
            return self.log_test("Auto-Submit Flow", False, "No user token or auto-submit quiz ID available")
            
        try:
            # Start session with custom short time limit (10 seconds)
            session_data = {
                "quiz_id": self.auto_submit_quiz_id,
                "time_limit_minutes": None  # Use quiz default but we'll simulate short time
            }
            
            response = requests.post(
                f"{self.api_url}/quiz-session/start",
                json=session_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            if response.status_code != 200:
                return self.log_test("Auto-Submit Flow", False, f"Session start failed: {response.status_code}")
            
            session = response.json()
            auto_session_id = session.get('id')
            
            # Activate session
            activate_response = requests.post(
                f"{self.api_url}/quiz-session/{auto_session_id}/activate",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            if activate_response.status_code != 200:
                return self.log_test("Auto-Submit Flow", False, f"Session activation failed: {activate_response.status_code}")
            
            # Add partial answer
            update_data = {
                "current_question_index": 0,
                "answers": ["4"]  # Correct answer
            }
            
            update_response = requests.put(
                f"{self.api_url}/quiz-session/{auto_session_id}/update",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            # Submit immediately (simulating auto-submit)
            submit_response = requests.post(
                f"{self.api_url}/quiz-session/{auto_session_id}/submit",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            success = submit_response.status_code == 200
            details = f"Status: {submit_response.status_code}"
            
            if success:
                result = submit_response.json()
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
                details += f", Percentage: {result.get('percentage', 0):.1f}%"
                details += f", Auto-Submit Result: Complete"
                
                # Verify all required fields are present
                required_fields = [
                    'id', 'quiz_id', 'user_id', 'score', 'total_questions', 
                    'percentage', 'question_results', 'earned_points', 
                    'total_possible_points', 'passed'
                ]
                
                missing_fields = [f for f in required_fields if f not in result]
                if missing_fields:
                    details += f", Missing Fields: {missing_fields}"
                    success = False
                else:
                    details += ", All Required Fields: Present"
            else:
                details += f", Response: {submit_response.text[:200]}"
                
            return self.log_test("Auto-Submit Flow", success, details)
        except Exception as e:
            return self.log_test("Auto-Submit Flow", False, f"Error: {str(e)}")

    def test_verify_result_data_structure(self):
        """Test that quiz results have all fields needed for UserResult component"""
        if not self.user_token:
            return self.log_test("Verify Result Data Structure", False, "No user token available")
            
        try:
            # Get user's attempts to verify result structure
            response = requests.get(
                f"{self.api_url}/my-attempts",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                attempts = response.json()
                details += f", Total Attempts: {len(attempts)}"
                
                if attempts:
                    # Check the most recent attempt
                    latest_attempt = attempts[-1]
                    
                    # Required fields for UserResult component
                    required_fields = {
                        'id': 'string',
                        'quiz_id': 'string', 
                        'user_id': 'string',
                        'score': 'number',
                        'total_questions': 'number',
                        'percentage': 'number',
                        'earned_points': 'number',
                        'total_possible_points': 'number',
                        'question_results': 'array',
                        'passed': 'boolean',
                        'attempted_at': 'string'
                    }
                    
                    missing_fields = []
                    incorrect_types = []
                    
                    for field, expected_type in required_fields.items():
                        if field not in latest_attempt:
                            missing_fields.append(field)
                        else:
                            value = latest_attempt[field]
                            if expected_type == 'string' and not isinstance(value, str):
                                incorrect_types.append(f"{field}:{type(value).__name__}")
                            elif expected_type == 'number' and not isinstance(value, (int, float)):
                                incorrect_types.append(f"{field}:{type(value).__name__}")
                            elif expected_type == 'array' and not isinstance(value, list):
                                incorrect_types.append(f"{field}:{type(value).__name__}")
                            elif expected_type == 'boolean' and not isinstance(value, bool):
                                incorrect_types.append(f"{field}:{type(value).__name__}")
                    
                    if missing_fields:
                        details += f", Missing Fields: {missing_fields}"
                        success = False
                    
                    if incorrect_types:
                        details += f", Incorrect Types: {incorrect_types}"
                        success = False
                    
                    if not missing_fields and not incorrect_types:
                        details += ", All Fields Present with Correct Types"
                    
                    # Check question_results structure
                    question_results = latest_attempt.get('question_results', [])
                    if question_results:
                        first_result = question_results[0]
                        result_required_fields = [
                            'question_number', 'question_text', 'user_answer', 
                            'correct_answer', 'is_correct', 'points_earned', 'points_possible'
                        ]
                        missing_result_fields = [f for f in result_required_fields if f not in first_result]
                        if missing_result_fields:
                            details += f", Missing Question Result Fields: {missing_result_fields}"
                            success = False
                        else:
                            details += f", Question Results Structure: Complete ({len(question_results)} questions)"
                else:
                    details += ", No attempts found to verify"
                    success = False
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Verify Result Data Structure", success, details)
        except Exception as e:
            return self.log_test("Verify Result Data Structure", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all timed quiz flow tests"""
        print("🎯 TIMED QUIZ FLOW TESTING - COMPREHENSIVE VERIFICATION")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print("=" * 70)
        
        # Authentication tests
        self.test_admin_login()
        self.test_user_registration_and_login()
        
        # Timed quiz creation and setup
        self.test_create_timed_quiz()
        self.test_publish_timed_quiz()
        
        # Real-time session flow
        self.test_start_quiz_session()
        self.test_activate_quiz_session()
        self.test_session_status_with_timer()
        self.test_update_session_progress()
        
        # Manual completion flow
        self.test_manual_quiz_completion()
        
        # Auto-submit flow
        self.test_create_auto_submit_quiz()
        self.test_auto_submit_flow()
        
        # Result verification
        self.test_verify_result_data_structure()
        
        # Summary
        print("\n" + "=" * 70)
        print(f"🎯 TIMED QUIZ FLOW TESTING COMPLETE")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("✅ ALL TESTS PASSED - Timed quiz flow working perfectly!")
            print("✅ Quiz results are properly returned with all necessary fields")
            print("✅ UserResult component should display results correctly")
        else:
            print(f"❌ {self.tests_run - self.tests_passed} TESTS FAILED")
            print("❌ Some issues found with timed quiz flow or result data structure")
        
        print("=" * 70)
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = TimedQuizFlowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)