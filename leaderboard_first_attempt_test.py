#!/usr/bin/env python3
"""
Leaderboard First Attempt Testing - Squiz Backend
Tests the updated leaderboard functionality to ensure it shows only users' FIRST quiz attempts instead of their best attempts.

Test Scenarios:
1. Create a quiz and have multiple users take it
2. Have at least one user retake the same quiz with a different score 
3. Verify that the leaderboard endpoints show only the FIRST attempt from each user, not their best attempt
4. Verify that the results ranking endpoint also follows the same logic
5. Check that the response includes the new is_first_attempt field
6. Test the countdown timer functionality to make sure it's still working correctly during quiz sessions
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import time

class LeaderboardFirstAttemptTester:
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
        self.user_tokens = {}  # Store multiple user tokens
        self.created_quiz_id = None
        self.test_session_id = str(uuid.uuid4())[:8]

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

    def test_create_multiple_users(self):
        """Create multiple test users for leaderboard testing"""
        users_data = [
            {"name": f"Alice Johnson {self.test_session_id}", "email": f"alice{self.test_session_id}@test.com", "password": "testpass123"},
            {"name": f"Bob Smith {self.test_session_id}", "email": f"bob{self.test_session_id}@test.com", "password": "testpass123"},
            {"name": f"Charlie Brown {self.test_session_id}", "email": f"charlie{self.test_session_id}@test.com", "password": "testpass123"},
            {"name": f"Diana Prince {self.test_session_id}", "email": f"diana{self.test_session_id}@test.com", "password": "testpass123"}
        ]
        
        success_count = 0
        for i, user_data in enumerate(users_data):
            try:
                response = requests.post(
                    f"{self.api_url}/auth/register",
                    json=user_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                if response.status_code == 200:
                    success_count += 1
                    # Login the user to get token
                    login_response = requests.post(
                        f"{self.api_url}/auth/login",
                        json={"email": user_data["email"], "password": user_data["password"]},
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    if login_response.status_code == 200:
                        login_data = login_response.json()
                        self.user_tokens[f"user_{i+1}"] = login_data.get('access_token')
                        
            except Exception as e:
                print(f"Error creating user {i+1}: {str(e)}")
        
        success = success_count == len(users_data)
        details = f"Created {success_count}/{len(users_data)} users successfully"
        return self.log_test("Create Multiple Test Users", success, details)

    def test_create_leaderboard_test_quiz(self):
        """Create a quiz specifically for leaderboard testing"""
        if not self.admin_token:
            return self.log_test("Create Leaderboard Test Quiz", False, "No admin token available")
            
        quiz_data = {
            "title": f"Leaderboard Test Quiz {self.test_session_id}",
            "description": "A quiz to test first attempt leaderboard functionality",
            "category": "Testing",
            "subject": "Mathematics",
            "subcategory": "General",
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
                    "question_text": "What is 10 - 4?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "5", "is_correct": False},
                        {"text": "6", "is_correct": True},
                        {"text": "7", "is_correct": False},
                        {"text": "8", "is_correct": False}
                    ],
                    "points": 1
                },
                {
                    "question_text": "What is 3 × 4?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "10", "is_correct": False},
                        {"text": "11", "is_correct": False},
                        {"text": "12", "is_correct": True},
                        {"text": "13", "is_correct": False}
                    ],
                    "points": 1
                },
                {
                    "question_text": "What is 15 ÷ 3?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "4", "is_correct": False},
                        {"text": "5", "is_correct": True},
                        {"text": "6", "is_correct": False},
                        {"text": "7", "is_correct": False}
                    ],
                    "points": 1
                }
            ],
            "time_limit_minutes": 5  # Add time limit for timer testing
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
                
                # Publish the quiz immediately
                publish_response = requests.post(
                    f"{self.api_url}/admin/quiz/{self.created_quiz_id}/publish",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if publish_response.status_code == 200:
                    details += ", Published: Yes"
                else:
                    details += ", Published: Failed"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Leaderboard Test Quiz", success, details)
        except Exception as e:
            return self.log_test("Create Leaderboard Test Quiz", False, f"Error: {str(e)}")

    def test_users_first_attempts(self):
        """Test multiple users taking the quiz for the first time with different scores"""
        if not self.created_quiz_id or not self.user_tokens:
            return self.log_test("Users First Attempts", False, "No quiz ID or user tokens available")

        # Define different answer patterns for different scores
        attempt_patterns = {
            "user_1": ["8", "6", "12", "5"],  # All correct (100%)
            "user_2": ["8", "6", "12", "4"],  # 3/4 correct (75%)
            "user_3": ["8", "6", "10", "4"],  # 2/4 correct (50%)
            "user_4": ["6", "5", "10", "4"]   # 0/4 correct (0%)
        }
        
        success_count = 0
        attempt_results = {}
        
        for user_key, answers in attempt_patterns.items():
            if user_key not in self.user_tokens:
                continue
                
            attempt_data = {
                "quiz_id": self.created_quiz_id,
                "answers": answers
            }

            try:
                response = requests.post(
                    f"{self.api_url}/quiz/{self.created_quiz_id}/attempt",
                    json=attempt_data,
                    headers=self.get_auth_headers(self.user_tokens[user_key]),
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    success_count += 1
                    attempt_results[user_key] = {
                        "score": result.get('score', 0),
                        "percentage": result.get('percentage', 0),
                        "attempt_id": result.get('id'),
                        "attempted_at": result.get('attempted_at')
                    }
                    
            except Exception as e:
                print(f"Error with {user_key} first attempt: {str(e)}")
        
        success = success_count == len(attempt_patterns)
        details = f"Completed {success_count}/{len(attempt_patterns)} first attempts"
        if success:
            score_list = [f'{k}={v["percentage"]}%' for k, v in attempt_results.items()]
            details += f", Scores: {score_list}"
        
        self.first_attempt_results = attempt_results
        return self.log_test("Users First Attempts", success, details)

    def test_user_retakes_quiz_with_different_score(self):
        """Test one user retaking the quiz with a different (better) score"""
        if not self.created_quiz_id or "user_2" not in self.user_tokens:
            return self.log_test("User Retakes Quiz", False, "No quiz ID or user_2 token available")

        # User 2 originally got 75%, now let's make them get 100% (better score)
        better_answers = ["8", "6", "12", "5"]  # All correct answers
        
        attempt_data = {
            "quiz_id": self.created_quiz_id,
            "answers": better_answers
        }

        try:
            # Wait a moment to ensure different timestamp
            time.sleep(1)
            
            response = requests.post(
                f"{self.api_url}/quiz/{self.created_quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.user_tokens["user_2"]),
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Second Attempt Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
                details += f", Percentage: {result.get('percentage', 0)}%"
                details += f", (First was {self.first_attempt_results.get('user_2', {}).get('percentage', 0)}%)"
                
                self.second_attempt_result = {
                    "score": result.get('score', 0),
                    "percentage": result.get('percentage', 0),
                    "attempt_id": result.get('id'),
                    "attempted_at": result.get('attempted_at')
                }
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Retakes Quiz", success, details)
        except Exception as e:
            return self.log_test("User Retakes Quiz", False, f"Error: {str(e)}")

    def test_admin_leaderboard_shows_first_attempts_only(self):
        """Test admin leaderboard endpoint shows only first attempts"""
        if not self.admin_token or not self.created_quiz_id:
            return self.log_test("Admin Leaderboard First Attempts Only", False, "No admin token or quiz ID available")
            
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
                details += f", Entries: {len(leaderboard)}"
                
                # Verify is_first_attempt field is present
                has_first_attempt_field = all('is_first_attempt' in entry for entry in leaderboard)
                details += f", Has is_first_attempt field: {has_first_attempt_field}"
                
                # Verify all entries show is_first_attempt: True
                all_first_attempts = all(entry.get('is_first_attempt') == True for entry in leaderboard)
                details += f", All first attempts: {all_first_attempts}"
                
                # Find user_2 in leaderboard and verify it shows their FIRST attempt (75%), not second (100%)
                user_2_entry = None
                for entry in leaderboard:
                    if "Johnson" in entry.get('user_name', ''):  # user_1 is Alice Johnson
                        continue
                    elif "Smith" in entry.get('user_name', ''):  # user_2 is Bob Smith
                        user_2_entry = entry
                        break
                
                if user_2_entry:
                    user_2_percentage = user_2_entry.get('percentage', 0)
                    expected_first_percentage = self.first_attempt_results.get('user_2', {}).get('percentage', 0)
                    shows_first_attempt = user_2_percentage == expected_first_percentage
                    details += f", User_2 shows first attempt ({expected_first_percentage}%): {shows_first_attempt}"
                    
                    if not shows_first_attempt:
                        details += f", ERROR: Shows {user_2_percentage}% instead of first attempt {expected_first_percentage}%"
                        success = False
                else:
                    details += ", User_2 not found in leaderboard"
                    success = False
                
                # Verify leaderboard is sorted by percentage (highest first)
                if len(leaderboard) > 1:
                    is_sorted = all(leaderboard[i]['percentage'] >= leaderboard[i+1]['percentage'] 
                                  for i in range(len(leaderboard)-1))
                    details += f", Properly sorted: {is_sorted}"
                    if not is_sorted:
                        success = False
                        
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Leaderboard First Attempts Only", success, details)
        except Exception as e:
            return self.log_test("Admin Leaderboard First Attempts Only", False, f"Error: {str(e)}")

    def test_public_leaderboard_shows_first_attempts_only(self):
        """Test public leaderboard endpoint shows only first attempts"""
        if not self.user_tokens.get("user_1") or not self.created_quiz_id:
            return self.log_test("Public Leaderboard First Attempts Only", False, "No user token or quiz ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/quiz/{self.created_quiz_id}/leaderboard",
                headers=self.get_auth_headers(self.user_tokens["user_1"]),
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                leaderboard = response.json()
                details += f", Entries: {len(leaderboard)}"
                
                # Verify is_first_attempt field is present
                has_first_attempt_field = all('is_first_attempt' in entry for entry in leaderboard)
                details += f", Has is_first_attempt field: {has_first_attempt_field}"
                
                # Verify all entries show is_first_attempt: True
                all_first_attempts = all(entry.get('is_first_attempt') == True for entry in leaderboard)
                details += f", All first attempts: {all_first_attempts}"
                
                # Verify user names are anonymized (should show first name + last initial)
                has_anonymized_names = any('.' in entry.get('user_name', '') for entry in leaderboard)
                details += f", Names anonymized: {has_anonymized_names}"
                
                # Find user_2 and verify it shows their FIRST attempt (75%), not second (100%)
                user_2_found = False
                for entry in leaderboard:
                    if "B." in entry.get('user_name', ''):  # Bob Smith should show as "Bob S."
                        user_2_found = True
                        user_2_percentage = entry.get('percentage', 0)
                        expected_first_percentage = self.first_attempt_results.get('user_2', {}).get('percentage', 0)
                        shows_first_attempt = user_2_percentage == expected_first_percentage
                        details += f", User_2 shows first attempt ({expected_first_percentage}%): {shows_first_attempt}"
                        
                        if not shows_first_attempt:
                            details += f", ERROR: Shows {user_2_percentage}% instead of first attempt {expected_first_percentage}%"
                            success = False
                        break
                
                if not user_2_found:
                    details += ", User_2 not found in public leaderboard"
                    success = False
                        
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Public Leaderboard First Attempts Only", success, details)
        except Exception as e:
            return self.log_test("Public Leaderboard First Attempts Only", False, f"Error: {str(e)}")

    def test_results_ranking_shows_first_attempts_only(self):
        """Test results ranking endpoint shows only first attempts"""
        if not self.user_tokens.get("user_1") or not self.created_quiz_id:
            return self.log_test("Results Ranking First Attempts Only", False, "No user token or quiz ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/quiz/{self.created_quiz_id}/results-ranking",
                headers=self.get_auth_headers(self.user_tokens["user_1"]),
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Total Participants: {data.get('total_participants', 0)}"
                
                # Check ranking note
                ranking_note = data.get('ranking_note', '')
                has_first_attempt_note = 'first' in ranking_note.lower()
                details += f", Has first attempt note: {has_first_attempt_note}"
                
                # Check full ranking
                full_ranking = data.get('full_ranking', [])
                details += f", Full ranking entries: {len(full_ranking)}"
                
                # Verify is_first_attempt field is present in ranking
                has_first_attempt_field = all('is_first_attempt' in entry for entry in full_ranking)
                details += f", Has is_first_attempt field: {has_first_attempt_field}"
                
                # Verify all entries show is_first_attempt: True
                all_first_attempts = all(entry.get('is_first_attempt') == True for entry in full_ranking)
                details += f", All first attempts: {all_first_attempts}"
                
                # Find user_2 and verify it shows their FIRST attempt (75%), not second (100%)
                user_2_found = False
                for entry in full_ranking:
                    if "Smith" in entry.get('user_name', ''):  # Bob Smith
                        user_2_found = True
                        user_2_percentage = entry.get('percentage', 0)
                        expected_first_percentage = self.first_attempt_results.get('user_2', {}).get('percentage', 0)
                        shows_first_attempt = user_2_percentage == expected_first_percentage
                        details += f", User_2 shows first attempt ({expected_first_percentage}%): {shows_first_attempt}"
                        
                        if not shows_first_attempt:
                            details += f", ERROR: Shows {user_2_percentage}% instead of first attempt {expected_first_percentage}%"
                            success = False
                        break
                
                if not user_2_found:
                    details += ", User_2 not found in results ranking"
                    success = False
                        
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Results Ranking First Attempts Only", success, details)
        except Exception as e:
            return self.log_test("Results Ranking First Attempts Only", False, f"Error: {str(e)}")

    def test_quiz_session_timer_functionality(self):
        """Test countdown timer functionality during quiz sessions"""
        if not self.user_tokens.get("user_3") or not self.created_quiz_id:
            return self.log_test("Quiz Session Timer Functionality", False, "No user token or quiz ID available")
            
        try:
            # Start a quiz session
            session_data = {"quiz_id": self.created_quiz_id}
            
            response = requests.post(
                f"{self.api_url}/quiz-session/start",
                json=session_data,
                headers=self.get_auth_headers(self.user_tokens["user_3"]),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Quiz Session Timer Functionality", False, f"Failed to start session: {response.status_code}")
            
            session_info = response.json()
            session_id = session_info.get('id')
            details = f"Session created: {session_id}"
            
            # Activate the session (start timer)
            activate_response = requests.post(
                f"{self.api_url}/quiz-session/{session_id}/activate",
                headers=self.get_auth_headers(self.user_tokens["user_3"]),
                timeout=10
            )
            
            if activate_response.status_code != 200:
                return self.log_test("Quiz Session Timer Functionality", False, f"Failed to activate session: {activate_response.status_code}")
            
            details += ", Session activated"
            
            # Check session status immediately after activation
            status_response = requests.get(
                f"{self.api_url}/quiz-session/{session_id}/status",
                headers=self.get_auth_headers(self.user_tokens["user_3"]),
                timeout=10
            )
            
            if status_response.status_code != 200:
                return self.log_test("Quiz Session Timer Functionality", False, f"Failed to get session status: {status_response.status_code}")
            
            status_data = status_response.json()
            initial_time_remaining = status_data.get('time_remaining_seconds', 0)
            details += f", Initial time: {initial_time_remaining}s"
            
            # Wait 3 seconds and check again
            time.sleep(3)
            
            status_response2 = requests.get(
                f"{self.api_url}/quiz-session/{session_id}/status",
                headers=self.get_auth_headers(self.user_tokens["user_3"]),
                timeout=10
            )
            
            if status_response2.status_code == 200:
                status_data2 = status_response2.json()
                later_time_remaining = status_data2.get('time_remaining_seconds', 0)
                details += f", After 3s: {later_time_remaining}s"
                
                # Timer should have decreased
                timer_working = later_time_remaining < initial_time_remaining
                details += f", Timer working: {timer_working}"
                
                if not timer_working:
                    return self.log_test("Quiz Session Timer Functionality", False, details + " - Timer not decreasing")
            
            # Submit the session to clean up
            submit_response = requests.post(
                f"{self.api_url}/quiz-session/{session_id}/submit",
                headers=self.get_auth_headers(self.user_tokens["user_3"]),
                timeout=10
            )
            
            success = submit_response.status_code == 200
            details += f", Session submitted: {success}"
                
            return self.log_test("Quiz Session Timer Functionality", success, details)
        except Exception as e:
            return self.log_test("Quiz Session Timer Functionality", False, f"Error: {str(e)}")

    def test_verify_database_has_multiple_attempts_for_user2(self):
        """Verify that user_2 actually has multiple attempts in the database"""
        if not self.admin_token or not self.created_quiz_id:
            return self.log_test("Verify Multiple Attempts in Database", False, "No admin token or quiz ID available")
            
        try:
            # Get all quiz results to see if user_2 has multiple attempts
            response = requests.get(
                f"{self.api_url}/admin/quiz-results",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                results = response.json()
                
                # Filter results for our test quiz and user_2
                user_2_attempts = []
                for result in results:
                    if (result.get('quiz_id') == self.created_quiz_id and 
                        'Smith' in result.get('user', {}).get('name', '')):
                        user_2_attempts.append(result)
                
                details += f", User_2 attempts found: {len(user_2_attempts)}"
                
                if len(user_2_attempts) >= 2:
                    # Sort by attempted_at to see chronological order
                    user_2_attempts.sort(key=lambda x: x.get('attempted_at', ''))
                    
                    first_attempt = user_2_attempts[0]
                    second_attempt = user_2_attempts[1]
                    
                    details += f", First: {first_attempt.get('percentage', 0)}%"
                    details += f", Second: {second_attempt.get('percentage', 0)}%"
                    
                    # Verify second attempt has better score
                    second_is_better = second_attempt.get('percentage', 0) > first_attempt.get('percentage', 0)
                    details += f", Second is better: {second_is_better}"
                    
                    if not second_is_better:
                        success = False
                        details += " - ERROR: Second attempt should be better than first"
                else:
                    success = False
                    details += " - ERROR: User_2 should have at least 2 attempts"
                        
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Verify Multiple Attempts in Database", success, details)
        except Exception as e:
            return self.log_test("Verify Multiple Attempts in Database", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all leaderboard first attempt tests"""
        print("🎯 LEADERBOARD FIRST ATTEMPT TESTING - SQUIZ BACKEND")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Test Session ID: {self.test_session_id}")
        print("=" * 80)
        
        # Test sequence
        tests = [
            self.test_admin_login,
            self.test_create_multiple_users,
            self.test_create_leaderboard_test_quiz,
            self.test_users_first_attempts,
            self.test_user_retakes_quiz_with_different_score,
            self.test_verify_database_has_multiple_attempts_for_user2,
            self.test_admin_leaderboard_shows_first_attempts_only,
            self.test_public_leaderboard_shows_first_attempts_only,
            self.test_results_ranking_shows_first_attempts_only,
            self.test_quiz_session_timer_functionality
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print(f"LEADERBOARD FIRST ATTEMPT TESTING COMPLETE")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Leaderboard shows FIRST attempts only!")
        else:
            print("❌ SOME TESTS FAILED - Leaderboard functionality needs attention")
        
        print("=" * 80)
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = LeaderboardFirstAttemptTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)