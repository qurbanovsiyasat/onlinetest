#!/usr/bin/env python3
"""
Real-time Quiz Session Testing for Squiz Platform
Tests the NEW real-time quiz session functionality including:
- Session creation, activation, status tracking
- Timer functionality and auto-expiry
- Session updates, pause/resume
- Session submission and final attempt creation
"""

import requests
import json
import sys
import time
from datetime import datetime
import uuid
import os

class RealTimeQuizSessionTester:
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
        self.test_quiz_id = None
        self.timed_quiz_id = None
        self.test_session_id = None
        self.timed_session_id = None
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

    def setup_admin_auth(self):
        """Setup admin authentication"""
        # Initialize admin if needed
        try:
            requests.post(f"{self.api_url}/init-admin", timeout=10)
        except:
            pass
        
        # Login as admin
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
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                return self.log_test("Admin Authentication Setup", True, f"Role: {data.get('user', {}).get('role', 'Unknown')}")
            else:
                return self.log_test("Admin Authentication Setup", False, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Admin Authentication Setup", False, f"Error: {str(e)}")

    def setup_user_auth(self):
        """Setup user authentication"""
        # Register test user
        user_data = {
            "name": f"Test User {self.test_user_id}",
            "email": f"testuser{self.test_user_id}@example.com",
            "password": "testpass123"
        }
        try:
            requests.post(
                f"{self.api_url}/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
        except:
            pass  # User might already exist
        
        # Login as user
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
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('access_token')
                return self.log_test("User Authentication Setup", True, f"Role: {data.get('user', {}).get('role', 'Unknown')}")
            else:
                return self.log_test("User Authentication Setup", False, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("User Authentication Setup", False, f"Error: {str(e)}")

    def create_test_quiz(self):
        """Create a test quiz for session testing"""
        if not self.admin_token:
            return self.log_test("Create Test Quiz", False, "No admin token available")
            
        quiz_data = {
            "title": "Real-time Session Test Quiz",
            "description": "A quiz for testing real-time session functionality",
            "category": "Testing",
            "subject": "Computer Science",
            "subcategory": "Testing",
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
                    "points": 1
                },
                {
                    "question_text": "Explain object-oriented programming",
                    "question_type": "open_ended",
                    "open_ended_answer": {
                        "expected_answers": ["Programming paradigm based on objects and classes"],
                        "keywords": ["object", "class", "programming"],
                        "case_sensitive": False,
                        "partial_credit": True
                    },
                    "points": 2
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
                self.test_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.test_quiz_id}, Questions: {quiz.get('total_questions', 0)}"
                
                # Publish the quiz
                publish_response = requests.post(
                    f"{self.api_url}/admin/quiz/{self.test_quiz_id}/publish",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if publish_response.status_code == 200:
                    details += ", Published: Yes"
                else:
                    details += ", Published: Failed"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Test Quiz", success, details)
        except Exception as e:
            return self.log_test("Create Test Quiz", False, f"Error: {str(e)}")

    def create_timed_quiz(self):
        """Create a timed quiz for timer testing"""
        if not self.admin_token:
            return self.log_test("Create Timed Quiz", False, "No admin token available")
            
        quiz_data = {
            "title": "Timed Session Test Quiz",
            "description": "A timed quiz for testing session timer functionality",
            "category": "Testing",
            "subject": "Mathematics",
            "subcategory": "Testing",
            "time_limit_minutes": 2,  # 2 minute time limit for testing
            "questions": [
                {
                    "question_text": "What is 5 + 3?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "7", "is_correct": False},
                        {"text": "8", "is_correct": True},
                        {"text": "9", "is_correct": False},
                        {"text": "10", "is_correct": False}
                    ],
                    "points": 1
                },
                {
                    "question_text": "What is 10 - 4?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "5", "is_correct": False},
                        {"text": "6", "is_correct": True},
                        {"text": "7", "is_correct": False},
                        {"text": "8", "is_correct": False}
                    ],
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
                quiz = response.json()
                self.timed_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.timed_quiz_id}, Time Limit: {quiz.get('time_limit_minutes', 0)} min"
                
                # Publish the quiz
                publish_response = requests.post(
                    f"{self.api_url}/admin/quiz/{self.timed_quiz_id}/publish",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if publish_response.status_code == 200:
                    details += ", Published: Yes"
                else:
                    details += ", Published: Failed"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Timed Quiz", success, details)
        except Exception as e:
            return self.log_test("Create Timed Quiz", False, f"Error: {str(e)}")

    def test_start_quiz_session(self):
        """Test POST /api/quiz-session/start - Start a new real-time quiz session"""
        if not self.user_token or not self.test_quiz_id:
            return self.log_test("Start Quiz Session", False, "No user token or quiz ID available")

        session_data = {
            "quiz_id": self.test_quiz_id
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
                self.test_session_id = session.get('id')
                details += f", Session ID: {self.test_session_id}"
                details += f", Status: {session.get('status', 'Unknown')}"
                details += f", Quiz Title: {session.get('quiz_title', 'Unknown')}"
                details += f", Total Questions: {session.get('total_questions', 0)}"
                details += f", Auto Submit: {session.get('is_auto_submit', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Start Quiz Session", success, details)
        except Exception as e:
            return self.log_test("Start Quiz Session", False, f"Error: {str(e)}")

    def test_start_timed_quiz_session(self):
        """Test starting a timed quiz session"""
        if not self.user_token or not self.timed_quiz_id:
            return self.log_test("Start Timed Quiz Session", False, "No user token or timed quiz ID available")

        session_data = {
            "quiz_id": self.timed_quiz_id,
            "time_limit_minutes": 1  # Override to 1 minute for faster testing
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
                self.timed_session_id = session.get('id')
                details += f", Session ID: {self.timed_session_id}"
                details += f", Status: {session.get('status', 'Unknown')}"
                details += f", Time Limit: {session.get('time_limit_minutes', 0)} min"
                details += f", Time Remaining: {session.get('time_remaining_seconds', 0)} sec"
                details += f", Auto Submit: {session.get('is_auto_submit', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Start Timed Quiz Session", success, details)
        except Exception as e:
            return self.log_test("Start Timed Quiz Session", False, f"Error: {str(e)}")

    def test_activate_quiz_session(self):
        """Test POST /api/quiz-session/{session_id}/activate - Activate pending session"""
        if not self.user_token or not self.test_session_id:
            return self.log_test("Activate Quiz Session", False, "No user token or session ID available")

        try:
            response = requests.post(
                f"{self.api_url}/quiz-session/{self.test_session_id}/activate",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                session = response.json()
                details += f", Status: {session.get('status', 'Unknown')}"
                details += f", Start Time: {session.get('start_time', 'None')[:19] if session.get('start_time') else 'None'}"
                details += f", Current Question: {session.get('current_question_index', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Activate Quiz Session", success, details)
        except Exception as e:
            return self.log_test("Activate Quiz Session", False, f"Error: {str(e)}")

    def test_activate_timed_session(self):
        """Test activating timed session (starts timer)"""
        if not self.user_token or not self.timed_session_id:
            return self.log_test("Activate Timed Session", False, "No user token or timed session ID available")

        try:
            response = requests.post(
                f"{self.api_url}/quiz-session/{self.timed_session_id}/activate",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                session = response.json()
                details += f", Status: {session.get('status', 'Unknown')}"
                details += f", Start Time: {session.get('start_time', 'None')[:19] if session.get('start_time') else 'None'}"
                details += f", Time Remaining: {session.get('time_remaining_seconds', 0)} sec"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Activate Timed Session", success, details)
        except Exception as e:
            return self.log_test("Activate Timed Session", False, f"Error: {str(e)}")

    def test_get_session_status(self):
        """Test GET /api/quiz-session/{session_id}/status - Get real-time session status"""
        if not self.user_token or not self.test_session_id:
            return self.log_test("Get Session Status", False, "No user token or session ID available")

        try:
            response = requests.get(
                f"{self.api_url}/quiz-session/{self.test_session_id}/status",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                session = response.json()
                details += f", Session Status: {session.get('status', 'Unknown')}"
                details += f", Current Question: {session.get('current_question_index', 0)}"
                details += f", Total Questions: {session.get('total_questions', 0)}"
                details += f", Answers Count: {len(session.get('answers', []))}"
                details += f", Last Activity: {session.get('last_activity', 'None')[:19] if session.get('last_activity') else 'None'}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Session Status", success, details)
        except Exception as e:
            return self.log_test("Get Session Status", False, f"Error: {str(e)}")

    def test_get_timed_session_status(self):
        """Test getting timed session status with timer updates"""
        if not self.user_token or not self.timed_session_id:
            return self.log_test("Get Timed Session Status", False, "No user token or timed session ID available")

        try:
            response = requests.get(
                f"{self.api_url}/quiz-session/{self.timed_session_id}/status",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                session = response.json()
                details += f", Session Status: {session.get('status', 'Unknown')}"
                details += f", Time Remaining: {session.get('time_remaining_seconds', 0)} sec"
                details += f", Time Limit: {session.get('time_limit_minutes', 0)} min"
                details += f", Auto Submit: {session.get('is_auto_submit', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Timed Session Status", success, details)
        except Exception as e:
            return self.log_test("Get Timed Session Status", False, f"Error: {str(e)}")

    def test_update_session_progress(self):
        """Test PUT /api/quiz-session/{session_id}/update - Update session progress"""
        if not self.user_token or not self.test_session_id:
            return self.log_test("Update Session Progress", False, "No user token or session ID available")

        update_data = {
            "current_question_index": 1,
            "answers": ["4", "Paris"]  # Answers for first two questions
        }

        try:
            response = requests.put(
                f"{self.api_url}/quiz-session/{self.test_session_id}/update",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                
                # Verify update by checking status
                status_response = requests.get(
                    f"{self.api_url}/quiz-session/{self.test_session_id}/status",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                if status_response.status_code == 200:
                    session = status_response.json()
                    details += f", Current Q: {session.get('current_question_index', 0)}"
                    details += f", Answers: {len(session.get('answers', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Update Session Progress", success, details)
        except Exception as e:
            return self.log_test("Update Session Progress", False, f"Error: {str(e)}")

    def test_pause_session(self):
        """Test GET /api/quiz-session/{session_id}/pause - Pause active session"""
        if not self.user_token or not self.test_session_id:
            return self.log_test("Pause Session", False, "No user token or session ID available")

        try:
            response = requests.get(
                f"{self.api_url}/quiz-session/{self.test_session_id}/pause",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                
                # Verify pause by checking status
                status_response = requests.get(
                    f"{self.api_url}/quiz-session/{self.test_session_id}/status",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                if status_response.status_code == 200:
                    session = status_response.json()
                    details += f", Status: {session.get('status', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Pause Session", success, details)
        except Exception as e:
            return self.log_test("Pause Session", False, f"Error: {str(e)}")

    def test_resume_session(self):
        """Test GET /api/quiz-session/{session_id}/resume - Resume paused session"""
        if not self.user_token or not self.test_session_id:
            return self.log_test("Resume Session", False, "No user token or session ID available")

        try:
            response = requests.get(
                f"{self.api_url}/quiz-session/{self.test_session_id}/resume",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                
                # Verify resume by checking status
                status_response = requests.get(
                    f"{self.api_url}/quiz-session/{self.test_session_id}/status",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                if status_response.status_code == 200:
                    session = status_response.json()
                    details += f", Status: {session.get('status', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Resume Session", success, details)
        except Exception as e:
            return self.log_test("Resume Session", False, f"Error: {str(e)}")

    def test_submit_session(self):
        """Test POST /api/quiz-session/{session_id}/submit - Submit quiz session"""
        if not self.user_token or not self.test_session_id:
            return self.log_test("Submit Session", False, "No user token or session ID available")

        # First update with final answers
        update_data = {
            "answers": ["4", "Paris", "Object-oriented programming uses classes and objects"]
        }
        
        try:
            # Update with final answers
            requests.put(
                f"{self.api_url}/quiz-session/{self.test_session_id}/update",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            # Submit session
            response = requests.post(
                f"{self.api_url}/quiz-session/{self.test_session_id}/submit",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                attempt = response.json()
                details += f", Score: {attempt.get('score', 0)}/{attempt.get('total_questions', 0)}"
                details += f", Points: {attempt.get('earned_points', 0)}/{attempt.get('total_possible_points', 0)}"
                details += f", Percentage: {attempt.get('percentage', 0):.1f}%"
                details += f", Passed: {attempt.get('passed', False)}"
                details += f", Time Taken: {attempt.get('time_taken_minutes', 0)} min"
                
                # Verify session is completed
                status_response = requests.get(
                    f"{self.api_url}/quiz-session/{self.test_session_id}/status",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                if status_response.status_code == 200:
                    session = status_response.json()
                    details += f", Final Status: {session.get('status', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Submit Session", success, details)
        except Exception as e:
            return self.log_test("Submit Session", False, f"Error: {str(e)}")

    def test_get_my_quiz_sessions(self):
        """Test GET /api/my-quiz-sessions - Get all quiz sessions for current user"""
        if not self.user_token:
            return self.log_test("Get My Quiz Sessions", False, "No user token available")

        try:
            response = requests.get(
                f"{self.api_url}/my-quiz-sessions",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                sessions = response.json()
                details += f", Sessions Count: {len(sessions)}"
                
                if len(sessions) > 0:
                    # Count by status
                    status_counts = {}
                    for session in sessions:
                        status = session.get('status', 'unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    details += f", Status Breakdown: {status_counts}"
                    
                    # Show latest session
                    latest = sessions[-1]
                    details += f", Latest: {latest.get('quiz_title', 'Unknown')[:20]}..."
                    details += f", Status: {latest.get('status', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get My Quiz Sessions", success, details)
        except Exception as e:
            return self.log_test("Get My Quiz Sessions", False, f"Error: {str(e)}")

    def test_admin_cannot_create_session(self):
        """Test that admin cannot create quiz sessions"""
        if not self.admin_token or not self.test_quiz_id:
            return self.log_test("Admin Cannot Create Session", False, "No admin token or quiz ID available")

        session_data = {
            "quiz_id": self.test_quiz_id
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz-session/start",
                json=session_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            
            if not success:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Cannot Create Session", success, details)
        except Exception as e:
            return self.log_test("Admin Cannot Create Session", False, f"Error: {str(e)}")

    def test_session_with_invalid_quiz(self):
        """Test creating session with invalid quiz ID"""
        if not self.user_token:
            return self.log_test("Session with Invalid Quiz", False, "No user token available")

        session_data = {
            "quiz_id": "invalid-quiz-id-12345"
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz-session/start",
                json=session_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 404  # Should be not found
            details = f"Status: {response.status_code} (Expected 404)"
            
            if not success:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Session with Invalid Quiz", success, details)
        except Exception as e:
            return self.log_test("Session with Invalid Quiz", False, f"Error: {str(e)}")

    def test_duplicate_session_prevention(self):
        """Test that users cannot create duplicate active sessions"""
        if not self.user_token or not self.test_quiz_id:
            return self.log_test("Duplicate Session Prevention", False, "No user token or quiz ID available")

        # Create first session
        session_data = {
            "quiz_id": self.test_quiz_id
        }

        try:
            # First session should succeed
            response1 = requests.post(
                f"{self.api_url}/quiz-session/start",
                json=session_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response1.status_code != 200:
                return self.log_test("Duplicate Session Prevention", False, "Could not create first session")
            
            # Second session should fail
            response2 = requests.post(
                f"{self.api_url}/quiz-session/start",
                json=session_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            success = response2.status_code == 400  # Should be bad request
            details = f"First: {response1.status_code}, Second: {response2.status_code} (Expected 400)"
            
            if not success:
                details += f", Response: {response2.text[:200]}"
                
            return self.log_test("Duplicate Session Prevention", success, details)
        except Exception as e:
            return self.log_test("Duplicate Session Prevention", False, f"Error: {str(e)}")

    def test_timer_countdown_functionality(self):
        """Test timer countdown and real-time updates"""
        if not self.user_token or not self.timed_session_id:
            return self.log_test("Timer Countdown Functionality", False, "No user token or timed session ID available")

        try:
            # Get initial time
            response1 = requests.get(
                f"{self.api_url}/quiz-session/{self.timed_session_id}/status",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response1.status_code != 200:
                return self.log_test("Timer Countdown Functionality", False, "Could not get initial status")
            
            initial_time = response1.json().get('time_remaining_seconds', 0)
            
            # Wait 3 seconds
            time.sleep(3)
            
            # Get updated time
            response2 = requests.get(
                f"{self.api_url}/quiz-session/{self.timed_session_id}/status",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response2.status_code != 200:
                return self.log_test("Timer Countdown Functionality", False, "Could not get updated status")
            
            updated_time = response2.json().get('time_remaining_seconds', 0)
            time_diff = initial_time - updated_time
            
            # Timer should have decreased by approximately 3 seconds (allow 1-5 second range)
            success = 1 <= time_diff <= 5
            details = f"Initial: {initial_time}s, After 3s: {updated_time}s, Diff: {time_diff}s"
            
            return self.log_test("Timer Countdown Functionality", success, details)
        except Exception as e:
            return self.log_test("Timer Countdown Functionality", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all real-time quiz session tests"""
        print("🚀 Starting Real-time Quiz Session Testing...")
        print(f"🔗 Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Setup
        if not self.setup_admin_auth():
            print("❌ Admin authentication failed - stopping tests")
            return
        
        if not self.setup_user_auth():
            print("❌ User authentication failed - stopping tests")
            return
        
        if not self.create_test_quiz():
            print("❌ Test quiz creation failed - stopping tests")
            return
            
        if not self.create_timed_quiz():
            print("❌ Timed quiz creation failed - stopping tests")
            return
        
        print("\n📋 Testing Real-time Quiz Session Endpoints...")
        print("-" * 50)
        
        # Core session functionality tests
        self.test_start_quiz_session()
        self.test_start_timed_quiz_session()
        self.test_activate_quiz_session()
        self.test_activate_timed_session()
        self.test_get_session_status()
        self.test_get_timed_session_status()
        self.test_update_session_progress()
        self.test_pause_session()
        self.test_resume_session()
        self.test_submit_session()
        self.test_get_my_quiz_sessions()
        
        # Error handling and edge cases
        self.test_admin_cannot_create_session()
        self.test_session_with_invalid_quiz()
        self.test_duplicate_session_prevention()
        
        # Timer functionality
        self.test_timer_countdown_functionality()
        
        # Summary
        print("\n" + "=" * 80)
        print(f"🏁 Real-time Quiz Session Testing Complete!")
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All real-time quiz session tests PASSED!")
            return True
        else:
            print("⚠️  Some real-time quiz session tests FAILED!")
            return False

if __name__ == "__main__":
    tester = RealTimeQuizSessionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)