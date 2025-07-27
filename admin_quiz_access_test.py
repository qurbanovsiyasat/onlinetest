#!/usr/bin/env python3
"""
Admin Quiz Access Control Testing - Specific Test for the Reported Issue
Tests the scenario: "admin hesabda yaradilan quizler islenende bu neticeler gelmir"
(when quizzes created in admin account are processed, these results do not come/appear)
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import os

class AdminQuizAccessTester:
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
        self.admin_created_quiz_id = None
        self.quiz_attempt_id = None

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
        """Test admin login (admin@onlinetestmaker.com/admin123)"""
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
                details += f", Email: {user_info.get('email', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("1. Admin Login", success, details)
        except Exception as e:
            return self.log_test("1. Admin Login", False, f"Error: {str(e)}")

    def test_admin_create_public_quiz_empty_allowed_users(self):
        """Test admin creating a quiz with public access and empty allowed_users list"""
        if not self.admin_token:
            return self.log_test("2. Admin Create Public Quiz (Empty Allowed Users)", False, "No admin token available")
            
        quiz_data = {
            "title": "Admin Quiz Access Test - Public with Empty Allowed Users",
            "description": "Testing the specific scenario where admin creates public quiz with empty allowed_users list",
            "category": "Access Control Test",
            "subject": "Mathematics",
            "subcategory": "General",
            "is_public": True,
            "allowed_users": [],  # Empty list - this was causing the issue
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
                self.admin_created_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.admin_created_quiz_id}"
                details += f", Is Public: {quiz.get('is_public', False)}"
                details += f", Allowed Users Count: {len(quiz.get('allowed_users', []))}"
                details += f", Created By: {quiz.get('created_by', 'Unknown')}"
                details += f", Questions: {quiz.get('total_questions', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("2. Admin Create Public Quiz (Empty Allowed Users)", success, details)
        except Exception as e:
            return self.log_test("2. Admin Create Public Quiz (Empty Allowed Users)", False, f"Error: {str(e)}")

    def test_publish_quiz(self):
        """Test publishing the quiz so it can be taken"""
        if not self.admin_token or not self.admin_created_quiz_id:
            return self.log_test("3. Publish Quiz", False, "No admin token or quiz ID available")
            
        try:
            response = requests.post(
                f"{self.api_url}/admin/quiz/{self.admin_created_quiz_id}/publish",
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
                
            return self.log_test("3. Publish Quiz", success, details)
        except Exception as e:
            return self.log_test("3. Publish Quiz", False, f"Error: {str(e)}")

    def test_admin_take_own_quiz(self):
        """Test admin taking their own quiz (this was failing before the fix)"""
        if not self.admin_token or not self.admin_created_quiz_id:
            return self.log_test("4. Admin Take Own Quiz", False, "No admin token or quiz ID available")

        attempt_data = {
            "quiz_id": self.admin_created_quiz_id,
            "answers": ["8", "6"]  # Correct answers
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz/{self.admin_created_quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                self.quiz_attempt_id = result.get('id')
                details += f", Attempt ID: {self.quiz_attempt_id}"
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
                details += f", Percentage: {result.get('percentage', 0):.1f}%"
                details += f", Points: {result.get('earned_points', 0)}/{result.get('total_possible_points', 0)}"
                details += f", Passed: {result.get('passed', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("4. Admin Take Own Quiz", success, details)
        except Exception as e:
            return self.log_test("4. Admin Take Own Quiz", False, f"Error: {str(e)}")

    def test_verify_quiz_results_in_database(self):
        """Test verifying quiz results are recorded in database"""
        if not self.admin_token or not self.quiz_attempt_id:
            return self.log_test("5. Verify Quiz Results in Database", False, "No admin token or attempt ID available")
            
        try:
            # Get all quiz results to verify our attempt is recorded
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
                
                # Look for our specific attempt
                our_attempt = None
                for result in results:
                    if result.get('attempt_id') == self.quiz_attempt_id:
                        our_attempt = result
                        break
                
                if our_attempt:
                    details += f", Our Attempt Found: Yes"
                    details += f", User: {our_attempt.get('user', {}).get('name', 'Unknown')}"
                    details += f", Quiz: {our_attempt.get('quiz', {}).get('title', 'Unknown')}"
                    details += f", Score: {our_attempt.get('score', 0)}/{our_attempt.get('total_questions', 0)}"
                    details += f", Percentage: {our_attempt.get('percentage', 0):.1f}%"
                else:
                    success = False
                    details += f", Our Attempt Found: No (ID: {self.quiz_attempt_id})"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("5. Verify Quiz Results in Database", success, details)
        except Exception as e:
            return self.log_test("5. Verify Quiz Results in Database", False, f"Error: {str(e)}")

    def test_admin_view_results_in_admin_view(self):
        """Test admin can view results in admin results view"""
        if not self.admin_token or not self.admin_created_quiz_id:
            return self.log_test("6. Admin View Results in Admin View", False, "No admin token or quiz ID available")
            
        try:
            # Get results for our specific quiz
            response = requests.get(
                f"{self.api_url}/admin/quiz-results/quiz/{self.admin_created_quiz_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                results = response.json()
                details += f", Quiz Results Count: {len(results)}"
                
                if len(results) > 0:
                    first_result = results[0]
                    details += f", First Result User: {first_result.get('user', {}).get('name', 'Unknown')}"
                    details += f", Score: {first_result.get('score', 0)}/{first_result.get('total_questions', 0)}"
                    details += f", Percentage: {first_result.get('percentage', 0):.1f}%"
                    details += f", Attempt Time: {first_result.get('attempted_at', 'Unknown')[:19]}"
                else:
                    success = False
                    details += ", No results found for this quiz"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("6. Admin View Results in Admin View", success, details)
        except Exception as e:
            return self.log_test("6. Admin View Results in Admin View", False, f"Error: {str(e)}")

    def test_admin_leaderboard_access(self):
        """Test admin can access leaderboard for their quiz"""
        if not self.admin_token or not self.admin_created_quiz_id:
            return self.log_test("7. Admin Leaderboard Access", False, "No admin token or quiz ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/quiz/{self.admin_created_quiz_id}/leaderboard",
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
                    details += f", Top Score: {top_entry.get('percentage', 0):.1f}%"
                    details += f", Rank: {top_entry.get('rank', 'Unknown')}"
                else:
                    details += ", No leaderboard entries (expected if only admin took quiz)"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("7. Admin Leaderboard Access", success, details)
        except Exception as e:
            return self.log_test("7. Admin Leaderboard Access", False, f"Error: {str(e)}")

    def test_public_leaderboard_access_for_admin(self):
        """Test admin can access public leaderboard view for their quiz"""
        if not self.admin_token or not self.admin_created_quiz_id:
            return self.log_test("8. Public Leaderboard Access for Admin", False, "No admin token or quiz ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/quiz/{self.admin_created_quiz_id}/leaderboard",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                leaderboard = response.json()
                details += f", Public Leaderboard Entries: {len(leaderboard)}"
                
                if len(leaderboard) > 0:
                    top_entry = leaderboard[0]
                    details += f", Top User: {top_entry.get('user_name', 'Unknown')}"
                    details += f", Top Score: {top_entry.get('percentage', 0):.1f}%"
                    details += f", Rank: {top_entry.get('rank', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("8. Public Leaderboard Access for Admin", success, details)
        except Exception as e:
            return self.log_test("8. Public Leaderboard Access for Admin", False, f"Error: {str(e)}")

    def test_quiz_results_ranking_for_admin(self):
        """Test admin can access quiz results ranking for their quiz"""
        if not self.admin_token or not self.admin_created_quiz_id:
            return self.log_test("9. Quiz Results Ranking for Admin", False, "No admin token or quiz ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/quiz/{self.admin_created_quiz_id}/results-ranking",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Quiz Title: {data.get('quiz_title', 'Unknown')}"
                details += f", Total Participants: {data.get('total_participants', 0)}"
                
                user_position = data.get('user_position', {})
                if user_position and user_position.get('rank'):
                    details += f", Admin Rank: {user_position.get('rank', 'N/A')}"
                    entry = user_position.get('entry', {})
                    details += f", Admin Score: {entry.get('percentage', 0):.1f}%"
                
                quiz_stats = data.get('quiz_stats', {})
                details += f", Total Attempts: {quiz_stats.get('total_attempts', 0)}"
                details += f", Average Score: {quiz_stats.get('average_score', 0):.1f}%"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("9. Quiz Results Ranking for Admin", success, details)
        except Exception as e:
            return self.log_test("9. Quiz Results Ranking for Admin", False, f"Error: {str(e)}")

    def test_analytics_summary_includes_admin_attempt(self):
        """Test analytics summary includes admin's quiz attempt"""
        if not self.admin_token:
            return self.log_test("10. Analytics Summary Includes Admin Attempt", False, "No admin token available")
            
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
                details += f", Average Score: {analytics.get('average_score', 0):.1f}%"
                details += f", Most Popular Quiz: {analytics.get('most_popular_quiz', 'None')}"
                
                # Check if our attempt is counted
                if analytics.get('total_attempts', 0) > 0:
                    details += " (Admin attempt counted)"
                else:
                    success = False
                    details += " (Admin attempt NOT counted)"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("10. Analytics Summary Includes Admin Attempt", success, details)
        except Exception as e:
            return self.log_test("10. Analytics Summary Includes Admin Attempt", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all admin quiz access control tests"""
        print("=" * 80)
        print("ADMIN QUIZ ACCESS CONTROL TESTING")
        print("Testing scenario: 'admin hesabda yaradilan quizler islenende bu neticeler gelmir'")
        print("(when quizzes created in admin account are processed, these results do not come/appear)")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Run tests in sequence
        tests = [
            self.test_admin_login,
            self.test_admin_create_public_quiz_empty_allowed_users,
            self.test_publish_quiz,
            self.test_admin_take_own_quiz,
            self.test_verify_quiz_results_in_database,
            self.test_admin_view_results_in_admin_view,
            self.test_admin_leaderboard_access,
            self.test_public_leaderboard_access_for_admin,
            self.test_quiz_results_ranking_for_admin,
            self.test_analytics_summary_includes_admin_attempt
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print(f"ADMIN QUIZ ACCESS CONTROL TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Admin quiz access control issue is FIXED!")
        else:
            print("⚠️  SOME TESTS FAILED - Admin quiz access control issue may still exist")
        
        print("=" * 80)
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = AdminQuizAccessTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)