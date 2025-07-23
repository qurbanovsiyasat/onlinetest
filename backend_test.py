#!/usr/bin/env python3
"""
Backend API Testing for OnlineTestMaker
Tests all API endpoints with comprehensive scenarios
"""

import requests
import json
import sys
from datetime import datetime
import uuid

class OnlineTestMakerAPITester:
    def __init__(self, base_url="https://f938a643-c3aa-424f-83ea-f4da56ce8f65.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_quiz_id = None

    def log_test(self, test_name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED {details}")
        else:
            print(f"❌ {test_name} - FAILED {details}")
        return success

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            return self.log_test("API Root", success, details)
        except Exception as e:
            return self.log_test("API Root", False, f"Error: {str(e)}")

    def test_get_empty_quizzes(self):
        """Test getting quizzes when none exist"""
        try:
            response = requests.get(f"{self.api_url}/quiz", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                quizzes = response.json()
                details += f", Count: {len(quizzes)}"
            return self.log_test("Get Empty Quizzes", success, details)
        except Exception as e:
            return self.log_test("Get Empty Quizzes", False, f"Error: {str(e)}")

    def test_create_quiz(self):
        """Test creating a new quiz"""
        quiz_data = {
            "title": "Test Quiz - Python Backend Test",
            "description": "A test quiz created by automated testing",
            "questions": [
                {
                    "question_text": "What is 2 + 2?",
                    "options": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True},
                        {"text": "5", "is_correct": False},
                        {"text": "6", "is_correct": False}
                    ]
                },
                {
                    "question_text": "What is the capital of France?",
                    "options": [
                        {"text": "London", "is_correct": False},
                        {"text": "Berlin", "is_correct": False},
                        {"text": "Paris", "is_correct": True},
                        {"text": "Madrid", "is_correct": False}
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz", 
                json=quiz_data, 
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quiz = response.json()
                self.created_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.created_quiz_id}, Questions: {quiz.get('total_questions', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Quiz", success, details)
        except Exception as e:
            return self.log_test("Create Quiz", False, f"Error: {str(e)}")

    def test_get_quizzes_after_creation(self):
        """Test getting quizzes after creating one"""
        try:
            response = requests.get(f"{self.api_url}/quiz", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quizzes = response.json()
                details += f", Count: {len(quizzes)}"
                if len(quizzes) > 0:
                    details += f", First Quiz: {quizzes[0].get('title', 'No title')}"
                    
            return self.log_test("Get Quizzes After Creation", success, details)
        except Exception as e:
            return self.log_test("Get Quizzes After Creation", False, f"Error: {str(e)}")

    def test_get_specific_quiz(self):
        """Test getting a specific quiz by ID"""
        if not self.created_quiz_id:
            return self.log_test("Get Specific Quiz", False, "No quiz ID available")

        try:
            response = requests.get(f"{self.api_url}/quiz/{self.created_quiz_id}", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quiz = response.json()
                details += f", Title: {quiz.get('title', 'No title')}, Questions: {len(quiz.get('questions', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Specific Quiz", success, details)
        except Exception as e:
            return self.log_test("Get Specific Quiz", False, f"Error: {str(e)}")

    def test_submit_quiz_attempt(self):
        """Test submitting a quiz attempt"""
        if not self.created_quiz_id:
            return self.log_test("Submit Quiz Attempt", False, "No quiz ID available")

        attempt_data = {
            "quiz_id": self.created_quiz_id,
            "answers": ["4", "Paris"]  # Correct answers for both questions
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz/{self.created_quiz_id}/attempt",
                json=attempt_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}, Percentage: {result.get('percentage', 0):.1f}%"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Submit Quiz Attempt", success, details)
        except Exception as e:
            return self.log_test("Submit Quiz Attempt", False, f"Error: {str(e)}")

    def test_get_quiz_attempts(self):
        """Test getting quiz attempts"""
        if not self.created_quiz_id:
            return self.log_test("Get Quiz Attempts", False, "No quiz ID available")

        try:
            response = requests.get(f"{self.api_url}/quiz/{self.created_quiz_id}/attempts", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                attempts = response.json()
                details += f", Attempts Count: {len(attempts)}"
                if len(attempts) > 0:
                    details += f", Latest Score: {attempts[-1].get('score', 0)}"
                    
            return self.log_test("Get Quiz Attempts", success, details)
        except Exception as e:
            return self.log_test("Get Quiz Attempts", False, f"Error: {str(e)}")

    def test_invalid_quiz_id(self):
        """Test accessing non-existent quiz"""
        fake_id = str(uuid.uuid4())
        try:
            response = requests.get(f"{self.api_url}/quiz/{fake_id}", timeout=10)
            success = response.status_code == 404
            details = f"Status: {response.status_code} (Expected 404)"
            return self.log_test("Invalid Quiz ID", success, details)
        except Exception as e:
            return self.log_test("Invalid Quiz ID", False, f"Error: {str(e)}")

    def test_invalid_quiz_creation(self):
        """Test creating quiz with invalid data"""
        invalid_quiz = {
            "title": "",  # Empty title
            "description": "Test",
            "questions": []  # No questions
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz",
                json=invalid_quiz,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            # Should fail validation (422) or succeed but create empty quiz
            success = response.status_code in [422, 200]
            details = f"Status: {response.status_code}"
            return self.log_test("Invalid Quiz Creation", success, details)
        except Exception as e:
            return self.log_test("Invalid Quiz Creation", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting OnlineTestMaker API Tests")
        print(f"🌐 Testing against: {self.api_url}")
        print("=" * 60)

        # Basic connectivity
        self.test_api_root()
        
        # Quiz CRUD operations
        self.test_get_empty_quizzes()
        self.test_create_quiz()
        self.test_get_quizzes_after_creation()
        self.test_get_specific_quiz()
        
        # Quiz attempt operations
        self.test_submit_quiz_attempt()
        self.test_get_quiz_attempts()
        
        # Error handling
        self.test_invalid_quiz_id()
        self.test_invalid_quiz_creation()

        # Summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the issues above.")
            return 1

def main():
    """Main test execution"""
    tester = OnlineTestMakerAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())