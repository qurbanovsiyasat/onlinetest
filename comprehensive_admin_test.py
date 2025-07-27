#!/usr/bin/env python3
"""
Comprehensive Admin Quiz Access Control Testing
Tests various scenarios to ensure the fix is robust
"""

import requests
import json
import sys
from datetime import datetime
import uuid

class ComprehensiveAdminTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        base_url = line.split('=')[1].strip()
                        break
        except:
            base_url = "http://localhost:8001"
        
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.user_token = None
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

    def setup_users(self):
        """Setup admin and regular user"""
        # Admin login
        login_data = {"email": "admin@onlinetestmaker.com", "password": "admin123"}
        response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            self.admin_token = response.json().get('access_token')
        
        # Create and login regular user
        user_data = {
            "name": f"Test User {self.test_user_id}",
            "email": f"testuser{self.test_user_id}@example.com",
            "password": "testpass123"
        }
        requests.post(f"{self.api_url}/auth/register", json=user_data, timeout=10)
        
        login_data = {"email": f"testuser{self.test_user_id}@example.com", "password": "testpass123"}
        response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            self.user_token = response.json().get('access_token')
            self.user_id = response.json().get('user', {}).get('id')

    def test_scenario_1_public_quiz_empty_allowed_users(self):
        """Test Scenario 1: Public quiz with empty allowed_users list"""
        quiz_data = {
            "title": "Scenario 1: Public Quiz Empty Allowed Users",
            "description": "Testing public quiz with empty allowed_users list for admin access",
            "category": "Test", "subject": "Math", "subcategory": "General",
            "is_public": True, "allowed_users": [],
            "questions": [{
                "question_text": "What is 1 + 1?", 
                "options": [
                    {"text": "1", "is_correct": False}, 
                    {"text": "2", "is_correct": True},
                    {"text": "3", "is_correct": False}
                ]
            }]
        }
        
        # Create quiz
        response = requests.post(f"{self.api_url}/admin/quiz", json=quiz_data, 
                               headers=self.get_auth_headers(self.admin_token), timeout=10)
        if response.status_code != 200:
            return self.log_test("Scenario 1: Create Quiz", False, f"Failed to create: {response.status_code}")
        
        quiz_id = response.json().get('id')
        
        # Publish quiz
        requests.post(f"{self.api_url}/admin/quiz/{quiz_id}/publish", 
                     headers=self.get_auth_headers(self.admin_token), timeout=10)
        
        # Admin takes quiz
        attempt_data = {"quiz_id": quiz_id, "answers": ["2"]}
        response = requests.post(f"{self.api_url}/quiz/{quiz_id}/attempt", json=attempt_data,
                               headers=self.get_auth_headers(self.admin_token), timeout=10)
        admin_success = response.status_code == 200
        
        # Regular user takes quiz (should also work for public quiz with empty allowed_users)
        response = requests.post(f"{self.api_url}/quiz/{quiz_id}/attempt", json=attempt_data,
                               headers=self.get_auth_headers(self.user_token), timeout=10)
        user_success = response.status_code == 200
        
        return self.log_test("Scenario 1: Public Quiz Empty Allowed Users", 
                           admin_success and user_success,
                           f"Admin: {admin_success}, User: {user_success}")

    def test_scenario_2_public_quiz_with_allowed_users(self):
        """Test Scenario 2: Public quiz with specific allowed_users"""
        quiz_data = {
            "title": "Scenario 2: Public Quiz With Allowed Users",
            "description": "Testing public quiz with specific allowed_users list",
            "category": "Test", "subject": "Math", "subcategory": "General",
            "is_public": True, "allowed_users": [self.user_id],
            "questions": [{
                "question_text": "What is 2 + 2?", 
                "options": [
                    {"text": "3", "is_correct": False}, 
                    {"text": "4", "is_correct": True},
                    {"text": "5", "is_correct": False}
                ]
            }]
        }
        
        # Create and publish quiz
        response = requests.post(f"{self.api_url}/admin/quiz", json=quiz_data, 
                               headers=self.get_auth_headers(self.admin_token), timeout=10)
        if response.status_code != 200:
            return self.log_test("Scenario 2: Create Quiz", False, f"Failed to create: {response.status_code}")
        
        quiz_id = response.json().get('id')
        requests.post(f"{self.api_url}/admin/quiz/{quiz_id}/publish", 
                     headers=self.get_auth_headers(self.admin_token), timeout=10)
        
        # Admin takes quiz (should work - creator can always take)
        attempt_data = {"quiz_id": quiz_id, "answers": ["4"]}
        response = requests.post(f"{self.api_url}/quiz/{quiz_id}/attempt", json=attempt_data,
                               headers=self.get_auth_headers(self.admin_token), timeout=10)
        admin_success = response.status_code == 200
        
        # User takes quiz (should work - user is in allowed_users)
        response = requests.post(f"{self.api_url}/quiz/{quiz_id}/attempt", json=attempt_data,
                               headers=self.get_auth_headers(self.user_token), timeout=10)
        user_success = response.status_code == 200
        
        return self.log_test("Scenario 2: Public Quiz With Allowed Users", 
                           admin_success and user_success,
                           f"Admin: {admin_success}, User: {user_success}")

    def test_scenario_3_private_quiz(self):
        """Test Scenario 3: Private quiz (non-public)"""
        quiz_data = {
            "title": "Scenario 3: Private Quiz",
            "description": "Testing private quiz",
            "category": "Test", "subject": "Math", "subcategory": "General",
            "is_public": False, "allowed_users": [],
            "questions": [{"question_text": "Test?", "options": [{"text": "A", "is_correct": True}]}]
        }
        
        # Create and publish quiz
        response = requests.post(f"{self.api_url}/admin/quiz", json=quiz_data, 
                               headers=self.get_auth_headers(self.admin_token), timeout=10)
        if response.status_code != 200:
            return self.log_test("Scenario 3: Create Quiz", False, f"Failed to create: {response.status_code}")
        
        quiz_id = response.json().get('id')
        requests.post(f"{self.api_url}/admin/quiz/{quiz_id}/publish", 
                     headers=self.get_auth_headers(self.admin_token), timeout=10)
        
        # Admin takes quiz (should work - creator can take private quiz)
        attempt_data = {"quiz_id": quiz_id, "answers": ["A"]}
        response = requests.post(f"{self.api_url}/quiz/{quiz_id}/attempt", json=attempt_data,
                               headers=self.get_auth_headers(self.admin_token), timeout=10)
        admin_success = response.status_code == 200
        
        # User tries to take quiz (should fail - private quiz, user not creator)
        response = requests.post(f"{self.api_url}/quiz/{quiz_id}/attempt", json=attempt_data,
                               headers=self.get_auth_headers(self.user_token), timeout=10)
        user_blocked = response.status_code == 403
        
        return self.log_test("Scenario 3: Private Quiz", 
                           admin_success and user_blocked,
                           f"Admin: {admin_success}, User blocked: {user_blocked}")

    def test_leaderboard_access_scenarios(self):
        """Test leaderboard access for different scenarios"""
        # Create a quiz and take it
        quiz_data = {
            "title": "Leaderboard Test Quiz",
            "description": "Testing leaderboard access",
            "category": "Test", "subject": "Math", "subcategory": "General",
            "is_public": True, "allowed_users": [],
            "questions": [{"question_text": "Test?", "options": [{"text": "A", "is_correct": True}]}]
        }
        
        response = requests.post(f"{self.api_url}/admin/quiz", json=quiz_data, 
                               headers=self.get_auth_headers(self.admin_token), timeout=10)
        if response.status_code != 200:
            return self.log_test("Leaderboard Test: Create Quiz", False, "Failed to create quiz")
        
        quiz_id = response.json().get('id')
        requests.post(f"{self.api_url}/admin/quiz/{quiz_id}/publish", 
                     headers=self.get_auth_headers(self.admin_token), timeout=10)
        
        # Admin takes quiz
        attempt_data = {"quiz_id": quiz_id, "answers": ["A"]}
        requests.post(f"{self.api_url}/quiz/{quiz_id}/attempt", json=attempt_data,
                     headers=self.get_auth_headers(self.admin_token), timeout=10)
        
        # Test admin leaderboard access
        response = requests.get(f"{self.api_url}/admin/quiz/{quiz_id}/leaderboard",
                              headers=self.get_auth_headers(self.admin_token), timeout=10)
        admin_leaderboard = response.status_code == 200
        
        # Test public leaderboard access for admin
        response = requests.get(f"{self.api_url}/quiz/{quiz_id}/leaderboard",
                              headers=self.get_auth_headers(self.admin_token), timeout=10)
        public_leaderboard = response.status_code == 200
        
        # Test results ranking access for admin
        response = requests.get(f"{self.api_url}/quiz/{quiz_id}/results-ranking",
                              headers=self.get_auth_headers(self.admin_token), timeout=10)
        results_ranking = response.status_code == 200
        
        return self.log_test("Leaderboard Access Scenarios", 
                           admin_leaderboard and public_leaderboard and results_ranking,
                           f"Admin LB: {admin_leaderboard}, Public LB: {public_leaderboard}, Ranking: {results_ranking}")

    def test_admin_results_view(self):
        """Test admin can view all results"""
        response = requests.get(f"{self.api_url}/admin/quiz-results",
                              headers=self.get_auth_headers(self.admin_token), timeout=10)
        success = response.status_code == 200
        
        if success:
            results = response.json()
            details = f"Total results: {len(results)}"
        else:
            details = f"Failed: {response.status_code}"
        
        return self.log_test("Admin Results View", success, details)

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("=" * 80)
        print("COMPREHENSIVE ADMIN QUIZ ACCESS CONTROL TESTING")
        print("=" * 80)
        
        # Setup
        self.setup_users()
        if not self.admin_token or not self.user_token:
            print("❌ Failed to setup users")
            return False
        
        # Run tests
        tests = [
            self.test_scenario_1_public_quiz_empty_allowed_users,
            self.test_scenario_2_public_quiz_with_allowed_users,
            self.test_scenario_3_private_quiz,
            self.test_leaderboard_access_scenarios,
            self.test_admin_results_view
        ]
        
        for test in tests:
            test()
            print()
        
        # Summary
        print("=" * 80)
        print(f"COMPREHENSIVE TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        print("=" * 80)
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = ComprehensiveAdminTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)