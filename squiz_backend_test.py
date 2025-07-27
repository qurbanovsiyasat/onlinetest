#!/usr/bin/env python3
"""
Backend API Testing for Squiz - Rebranded Application Testing
Tests the specific functionality after rebranding from OnlineTestMaker to Squiz:
- Authentication with new admin credentials (admin@squiz.com/admin123)
- Quiz visibility logic (draft/publish functionality)
- Subject folder management
- API health check with Squiz branding
- Core quiz functionality
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import os

class SquizAPITester:
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
        self.draft_quiz_id = None
        self.published_quiz_id = None
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

    def test_health_check_squiz_branding(self):
        """Test health check endpoint to verify Squiz branding"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                message = data.get('message', '')
                # Check if message contains "Squiz" branding
                has_squiz_branding = 'Squiz' in message
                details += f", Message: {message}"
                details += f", Has Squiz Branding: {has_squiz_branding}"
                details += f", Status: {data.get('status', 'Unknown')}"
                details += f", Hosting: {data.get('hosting', 'Unknown')}"
                details += f", Database: {data.get('database', 'Unknown')}"
                success = success and has_squiz_branding
            return self.log_test("Health Check (Squiz Branding)", success, details)
        except Exception as e:
            return self.log_test("Health Check (Squiz Branding)", False, f"Error: {str(e)}")

    def test_api_root_squiz_branding(self):
        """Test API root endpoint for Squiz branding"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                message = data.get('message', '')
                # Check if message contains "Squiz" branding
                has_squiz_branding = 'Squiz' in message
                details += f", Message: {message}"
                details += f", Has Squiz Branding: {has_squiz_branding}"
                success = success and has_squiz_branding
            return self.log_test("API Root (Squiz Branding)", success, details)
        except Exception as e:
            return self.log_test("API Root (Squiz Branding)", False, f"Error: {str(e)}")

    def test_init_admin_squiz(self):
        """Test admin initialization for Squiz"""
        try:
            response = requests.post(f"{self.api_url}/init-admin", timeout=10)
            # Should succeed (200) or fail if admin exists (400)
            success = response.status_code in [200, 400]
            details = f"Status: {response.status_code}"
            if response.status_code == 200:
                data = response.json()
                email = data.get('email', '')
                # Check if admin email is the new Squiz email
                has_squiz_email = 'admin@squiz.com' in email
                details += f", Admin created: {email}"
                details += f", Has Squiz Email: {has_squiz_email}"
                success = success and has_squiz_email
            elif response.status_code == 400:
                details += ", Admin already exists"
            return self.log_test("Initialize Admin (Squiz)", success, details)
        except Exception as e:
            return self.log_test("Initialize Admin (Squiz)", False, f"Error: {str(e)}")

    def test_admin_login_squiz_credentials(self):
        """Test admin login with new Squiz credentials"""
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
                details += f", Role: {user_info.get('role', 'Unknown')}"
                details += f", Name: {user_info.get('name', 'Unknown')}"
                details += f", Email: {user_info.get('email', 'Unknown')}"
                # Verify it's the Squiz admin account
                is_squiz_admin = user_info.get('email') == 'admin@squiz.com'
                details += f", Is Squiz Admin: {is_squiz_admin}"
                success = success and is_squiz_admin
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Login (Squiz Credentials)", success, details)
        except Exception as e:
            return self.log_test("Admin Login (Squiz Credentials)", False, f"Error: {str(e)}")

    def test_jwt_authentication_working(self):
        """Test JWT authentication is working properly"""
        if not self.admin_token:
            return self.log_test("JWT Authentication", False, "No admin token available")
            
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
                
            return self.log_test("JWT Authentication", success, details)
        except Exception as e:
            return self.log_test("JWT Authentication", False, f"Error: {str(e)}")

    def test_user_registration_and_login(self):
        """Test user registration and login functionality"""
        # First register a user
        user_data = {
            "name": f"Test User {self.test_user_id}",
            "email": f"testuser{self.test_user_id}@squiz.com",
            "password": "testpass123"
        }
        try:
            # Register user
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
                "email": user_data["email"],
                "password": user_data["password"]
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
                details += f", Role: {user_info.get('role', 'Unknown')}"
                details += f", Name: {user_info.get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Registration and Login", success, details)
        except Exception as e:
            return self.log_test("User Registration and Login", False, f"Error: {str(e)}")

    def test_quiz_created_in_draft_mode(self):
        """Test that quizzes are created in draft mode by default"""
        if not self.admin_token:
            return self.log_test("Quiz Created in Draft Mode", False, "No admin token available")
            
        quiz_data = {
            "title": "Draft Mode Test Quiz",
            "description": "Testing that quizzes are created in draft mode by default",
            "category": "Test Category",
            "subject": "Mathematics",
            "subcategory": "General",
            "questions": [
                {
                    "question_text": "What is 2 + 2?",
                    "options": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True},
                        {"text": "5", "is_correct": False}
                    ]
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
                self.draft_quiz_id = quiz.get('id')
                is_draft = quiz.get('is_draft', False)
                details += f", Quiz ID: {self.draft_quiz_id}"
                details += f", Is Draft: {is_draft}"
                details += f", Title: {quiz.get('title', 'Unknown')}"
                success = success and is_draft  # Must be in draft mode
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Quiz Created in Draft Mode", success, details)
        except Exception as e:
            return self.log_test("Quiz Created in Draft Mode", False, f"Error: {str(e)}")

    def test_quiz_publish_functionality(self):
        """Test quiz publish functionality"""
        if not self.admin_token or not self.draft_quiz_id:
            return self.log_test("Quiz Publish Functionality", False, "No admin token or draft quiz ID available")
            
        try:
            response = requests.post(
                f"{self.api_url}/admin/quiz/{self.draft_quiz_id}/publish",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                
                # Verify quiz is now published by getting quiz details
                quiz_response = requests.get(
                    f"{self.api_url}/admin/quizzes",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if quiz_response.status_code == 200:
                    quizzes = quiz_response.json()
                    published_quiz = next((q for q in quizzes if q.get('id') == self.draft_quiz_id), None)
                    if published_quiz:
                        is_draft = published_quiz.get('is_draft', True)
                        details += f", Now Draft: {is_draft}"
                        success = success and not is_draft  # Should no longer be draft
                        self.published_quiz_id = self.draft_quiz_id
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Quiz Publish Functionality", success, details)
        except Exception as e:
            return self.log_test("Quiz Publish Functionality", False, f"Error: {str(e)}")

    def test_users_can_only_access_published_quizzes(self):
        """Test that users can only access published quizzes, not drafts"""
        if not self.user_token:
            return self.log_test("Users Access Published Quizzes Only", False, "No user token available")
        
        # Create a draft quiz first
        if not self.admin_token:
            return self.log_test("Users Access Published Quizzes Only", False, "No admin token available")
            
        draft_quiz_data = {
            "title": "Draft Quiz - Should Not Be Accessible",
            "description": "This quiz should not be accessible to users",
            "category": "Test Category",
            "subject": "Science",
            "subcategory": "General",
            "questions": [
                {
                    "question_text": "This is a draft question",
                    "options": [
                        {"text": "Option 1", "is_correct": True},
                        {"text": "Option 2", "is_correct": False}
                    ]
                }
            ]
        }

        try:
            # Create draft quiz
            draft_response = requests.post(
                f"{self.api_url}/admin/quiz",
                json=draft_quiz_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if draft_response.status_code != 200:
                return self.log_test("Users Access Published Quizzes Only", False, "Could not create draft quiz")
            
            draft_quiz = draft_response.json()
            draft_quiz_id = draft_quiz.get('id')
            
            # Try to access draft quiz as user (should fail)
            user_quiz_response = requests.post(
                f"{self.api_url}/quiz/{draft_quiz_id}/attempt",
                json={"quiz_id": draft_quiz_id, "answers": ["Option 1"]},
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            # Should get 404 because draft quizzes are not accessible
            draft_access_blocked = user_quiz_response.status_code == 404
            
            # Now test access to published quiz
            published_access_allowed = False
            if self.published_quiz_id:
                published_quiz_response = requests.post(
                    f"{self.api_url}/quiz/{self.published_quiz_id}/attempt",
                    json={"quiz_id": self.published_quiz_id, "answers": ["4"]},
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                published_access_allowed = published_quiz_response.status_code == 200
            
            success = draft_access_blocked and published_access_allowed
            details = f"Draft Access Blocked: {draft_access_blocked}, Published Access Allowed: {published_access_allowed}"
            details += f", Draft Response: {user_quiz_response.status_code}"
            if self.published_quiz_id:
                details += f", Published Response: {published_quiz_response.status_code}"
                
            return self.log_test("Users Access Published Quizzes Only", success, details)
        except Exception as e:
            return self.log_test("Users Access Published Quizzes Only", False, f"Error: {str(e)}")

    def test_subject_folder_creation(self):
        """Test creating subject folders"""
        if not self.admin_token:
            return self.log_test("Subject Folder Creation", False, "No admin token available")
            
        folder_data = {
            "name": "Advanced Mathematics",
            "description": "Advanced mathematics topics and concepts",
            "subcategories": ["Calculus", "Linear Algebra", "Statistics"],
            "is_public": True,
            "allowed_users": []
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin/subject-folder",
                json=folder_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                folder = response.json()
                self.created_folder_id = folder.get('id')
                details += f", Folder ID: {self.created_folder_id}"
                details += f", Name: {folder.get('name', 'Unknown')}"
                details += f", Subcategories: {len(folder.get('subcategories', []))}"
                details += f", Is Public: {folder.get('is_public', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Subject Folder Creation", success, details)
        except Exception as e:
            return self.log_test("Subject Folder Creation", False, f"Error: {str(e)}")

    def test_quiz_organization_within_folders(self):
        """Test quiz organization within subject folders"""
        if not self.admin_token:
            return self.log_test("Quiz Organization Within Folders", False, "No admin token available")
            
        # Create quiz in specific subject/subcategory
        quiz_data = {
            "title": "Calculus Quiz",
            "description": "A quiz about calculus concepts",
            "category": "Mathematics",
            "subject": "Advanced Mathematics",
            "subcategory": "Calculus",
            "questions": [
                {
                    "question_text": "What is the derivative of x²?",
                    "options": [
                        {"text": "x", "is_correct": False},
                        {"text": "2x", "is_correct": True},
                        {"text": "x²", "is_correct": False}
                    ]
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
                details += f", Quiz ID: {quiz.get('id')}"
                details += f", Subject: {quiz.get('subject', 'Unknown')}"
                details += f", Subcategory: {quiz.get('subcategory', 'Unknown')}"
                details += f", Category: {quiz.get('category', 'Unknown')}"
                
                # Verify organization by checking subjects structure
                structure_response = requests.get(
                    f"{self.api_url}/admin/subjects-structure",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if structure_response.status_code == 200:
                    structure = structure_response.json()
                    subject_exists = "Advanced Mathematics" in structure
                    details += f", Subject in Structure: {subject_exists}"
                    if subject_exists:
                        subcategories = structure["Advanced Mathematics"].get("subcategories", {})
                        calculus_exists = "Calculus" in subcategories
                        details += f", Calculus Subcategory: {calculus_exists}"
                        success = success and calculus_exists
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Quiz Organization Within Folders", success, details)
        except Exception as e:
            return self.log_test("Quiz Organization Within Folders", False, f"Error: {str(e)}")

    def test_moving_quizzes_between_subjects(self):
        """Test moving quizzes between subjects/subcategories"""
        if not self.admin_token or not self.published_quiz_id:
            return self.log_test("Moving Quizzes Between Subjects", False, "No admin token or published quiz ID available")
            
        # Update quiz to move it to different subject/subcategory
        update_data = {
            "subject": "Physics",
            "subcategory": "Mechanics"
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/admin/quiz/{self.published_quiz_id}",
                json=update_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quiz = response.json()
                details += f", New Subject: {quiz.get('subject', 'Unknown')}"
                details += f", New Subcategory: {quiz.get('subcategory', 'Unknown')}"
                details += f", Updated At: {quiz.get('updated_at', 'Unknown')[:19]}"
                
                # Verify the move was successful
                moved_correctly = (quiz.get('subject') == 'Physics' and 
                                 quiz.get('subcategory') == 'Mechanics')
                details += f", Moved Correctly: {moved_correctly}"
                success = success and moved_correctly
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Moving Quizzes Between Subjects", success, details)
        except Exception as e:
            return self.log_test("Moving Quizzes Between Subjects", False, f"Error: {str(e)}")

    def test_core_quiz_functionality(self):
        """Test core quiz functionality: creation, publishing, taking, grading, results"""
        if not self.admin_token or not self.user_token:
            return self.log_test("Core Quiz Functionality", False, "Missing admin or user token")
            
        # Create a comprehensive quiz
        quiz_data = {
            "title": "Comprehensive Test Quiz",
            "description": "Testing complete quiz functionality",
            "category": "Testing",
            "subject": "Computer Science",
            "subcategory": "Testing",
            "questions": [
                {
                    "question_text": "What is 5 + 3?",
                    "options": [
                        {"text": "7", "is_correct": False},
                        {"text": "8", "is_correct": True},
                        {"text": "9", "is_correct": False}
                    ],
                    "points": 2
                },
                {
                    "question_text": "Which are programming languages? (Select all)",
                    "question_type": "multiple_choice",
                    "multiple_correct": True,
                    "options": [
                        {"text": "Python", "is_correct": True},
                        {"text": "Java", "is_correct": True},
                        {"text": "HTML", "is_correct": False}
                    ],
                    "points": 3
                }
            ],
            "min_pass_percentage": 60.0
        }

        try:
            # 1. Create quiz
            create_response = requests.post(
                f"{self.api_url}/admin/quiz",
                json=quiz_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if create_response.status_code != 200:
                return self.log_test("Core Quiz Functionality", False, f"Quiz creation failed: {create_response.status_code}")
            
            quiz = create_response.json()
            quiz_id = quiz.get('id')
            
            # 2. Publish quiz
            publish_response = requests.post(
                f"{self.api_url}/admin/quiz/{quiz_id}/publish",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if publish_response.status_code != 200:
                return self.log_test("Core Quiz Functionality", False, f"Quiz publishing failed: {publish_response.status_code}")
            
            # 3. User takes quiz
            attempt_data = {
                "quiz_id": quiz_id,
                "answers": ["8", "Python,Java"]  # Correct answers
            }
            
            attempt_response = requests.post(
                f"{self.api_url}/quiz/{quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if attempt_response.status_code != 200:
                return self.log_test("Core Quiz Functionality", False, f"Quiz attempt failed: {attempt_response.status_code}")
            
            result = attempt_response.json()
            
            # 4. Check results recording
            results_response = requests.get(
                f"{self.api_url}/admin/quiz-results",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            success = results_response.status_code == 200
            details = f"Creation: ✓, Publishing: ✓, Taking: ✓, Results: {'✓' if success else '✗'}"
            details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
            details += f", Points: {result.get('earned_points', 0)}/{result.get('total_possible_points', 0)}"
            details += f", Percentage: {result.get('percentage', 0):.1f}%"
            details += f", Passed: {result.get('passed', False)}"
            
            if success:
                results = results_response.json()
                details += f", Results Count: {len(results)}"
                
            return self.log_test("Core Quiz Functionality", success, details)
        except Exception as e:
            return self.log_test("Core Quiz Functionality", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all Squiz backend tests"""
        print("🚀 Starting Squiz Backend API Testing")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Test sequence focusing on review request requirements
        test_methods = [
            # 1. API Health Check with Squiz branding
            self.test_health_check_squiz_branding,
            self.test_api_root_squiz_branding,
            
            # 2. Authentication Testing with new credentials
            self.test_init_admin_squiz,
            self.test_admin_login_squiz_credentials,
            self.test_jwt_authentication_working,
            self.test_user_registration_and_login,
            
            # 3. Quiz Visibility Logic (draft/publish)
            self.test_quiz_created_in_draft_mode,
            self.test_quiz_publish_functionality,
            self.test_users_can_only_access_published_quizzes,
            
            # 4. Subject Folder Management
            self.test_subject_folder_creation,
            self.test_quiz_organization_within_folders,
            self.test_moving_quizzes_between_subjects,
            
            # 5. Core Quiz Functionality
            self.test_core_quiz_functionality,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(test_method.__name__, False, f"Unexpected error: {str(e)}")
        
        print("=" * 80)
        print(f"🏁 Testing Complete: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Squiz backend is working correctly.")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} test(s) failed. Please review the issues above.")
            return False

def main():
    """Main function to run the tests"""
    tester = SquizAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()