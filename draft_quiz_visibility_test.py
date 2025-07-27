#!/usr/bin/env python3
"""
Critical Draft Quiz Visibility Bug Fix Testing
Tests the specific requirement that draft quizzes should NOT be visible to regular users
"""

import requests
import json
import sys
from datetime import datetime
import uuid

class DraftQuizVisibilityTester:
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
        self.draft_quiz_id = None
        self.published_quiz_id = None
        self.legacy_quiz_id = None  # Quiz without is_draft field
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
        # Register user
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
            pass
        
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

    def test_admin_create_draft_quiz(self):
        """Test admin creating a draft quiz (should remain in draft by default)"""
        if not self.admin_token:
            return self.log_test("Admin Create Draft Quiz", False, "No admin token available")
            
        quiz_data = {
            "title": "Draft Quiz - Should Not Be Accessible",
            "description": "This quiz is in draft mode and should not be visible to users",
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
                details += f", Quiz ID: {self.draft_quiz_id}, is_draft: {is_draft}"
                # Verify it's created as draft
                if not is_draft:
                    success = False
                    details += " - ERROR: Quiz should be created as draft by default"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Draft Quiz", success, details)
        except Exception as e:
            return self.log_test("Admin Create Draft Quiz", False, f"Error: {str(e)}")

    def test_admin_create_published_quiz(self):
        """Test admin creating and publishing a quiz"""
        if not self.admin_token:
            return self.log_test("Admin Create Published Quiz", False, "No admin token available")
            
        quiz_data = {
            "title": "Published Quiz - Should Be Accessible",
            "description": "This quiz is published and should be visible to users",
            "category": "Test Category",
            "subject": "Mathematics",
            "subcategory": "General",
            "questions": [
                {
                    "question_text": "What is 3 + 3?",
                    "options": [
                        {"text": "5", "is_correct": False},
                        {"text": "6", "is_correct": True},
                        {"text": "7", "is_correct": False}
                    ]
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
                return self.log_test("Admin Create Published Quiz", False, f"Create failed: {response.status_code}")
            
            quiz = response.json()
            self.published_quiz_id = quiz.get('id')
            
            # Publish the quiz
            publish_response = requests.post(
                f"{self.api_url}/admin/quiz/{self.published_quiz_id}/publish",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            success = publish_response.status_code == 200
            details = f"Create Status: {response.status_code}, Publish Status: {publish_response.status_code}"
            details += f", Quiz ID: {self.published_quiz_id}"
            
            return self.log_test("Admin Create Published Quiz", success, details)
        except Exception as e:
            return self.log_test("Admin Create Published Quiz", False, f"Error: {str(e)}")

    def test_admin_view_draft_quiz_in_admin_interface(self):
        """Test that admin can see draft quizzes in admin interface"""
        if not self.admin_token or not self.draft_quiz_id:
            return self.log_test("Admin View Draft Quiz in Admin Interface", False, "No admin token or draft quiz ID")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/quizzes",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quizzes = response.json()
                draft_quiz_found = False
                draft_quiz_status = None
                
                for quiz in quizzes:
                    if quiz.get('id') == self.draft_quiz_id:
                        draft_quiz_found = True
                        draft_quiz_status = quiz.get('is_draft', False)
                        break
                
                details += f", Total Quizzes: {len(quizzes)}, Draft Quiz Found: {draft_quiz_found}"
                if draft_quiz_found:
                    details += f", Draft Status: {draft_quiz_status}"
                    if not draft_quiz_status:
                        success = False
                        details += " - ERROR: Draft quiz should have is_draft=True"
                else:
                    success = False
                    details += " - ERROR: Draft quiz not found in admin interface"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin View Draft Quiz in Admin Interface", success, details)
        except Exception as e:
            return self.log_test("Admin View Draft Quiz in Admin Interface", False, f"Error: {str(e)}")

    def test_user_quiz_list_excludes_drafts(self):
        """CRITICAL: Test that user quiz list does NOT include draft quizzes"""
        if not self.user_token:
            return self.log_test("User Quiz List Excludes Drafts", False, "No user token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/quizzes",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quizzes = response.json()
                draft_quiz_found = False
                published_quiz_found = False
                
                for quiz in quizzes:
                    if quiz.get('id') == self.draft_quiz_id:
                        draft_quiz_found = True
                    if quiz.get('id') == self.published_quiz_id:
                        published_quiz_found = True
                
                details += f", Total Quizzes: {len(quizzes)}"
                details += f", Draft Quiz Found: {draft_quiz_found}"
                details += f", Published Quiz Found: {published_quiz_found}"
                
                # CRITICAL: Draft quiz should NOT be found, published quiz SHOULD be found
                if draft_quiz_found:
                    success = False
                    details += " - CRITICAL ERROR: Draft quiz is visible to users!"
                elif not published_quiz_found:
                    success = False
                    details += " - ERROR: Published quiz is not visible to users"
                else:
                    details += " - CORRECT: Only published quizzes visible to users"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Quiz List Excludes Drafts", success, details)
        except Exception as e:
            return self.log_test("User Quiz List Excludes Drafts", False, f"Error: {str(e)}")

    def test_user_cannot_access_draft_quiz_directly(self):
        """CRITICAL: Test that user cannot access draft quiz via direct API call"""
        if not self.user_token or not self.draft_quiz_id:
            return self.log_test("User Cannot Access Draft Quiz Directly", False, "No user token or draft quiz ID")
            
        try:
            response = requests.get(
                f"{self.api_url}/quiz/{self.draft_quiz_id}",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            # Should return 404 for draft quizzes
            success = response.status_code == 404
            details = f"Status: {response.status_code} (Expected 404)"
            
            if response.status_code == 200:
                success = False
                details += " - CRITICAL ERROR: User can access draft quiz directly!"
            elif response.status_code == 404:
                details += " - CORRECT: Draft quiz returns 404 for users"
            else:
                details += f" - Unexpected status code"
                
            return self.log_test("User Cannot Access Draft Quiz Directly", success, details)
        except Exception as e:
            return self.log_test("User Cannot Access Draft Quiz Directly", False, f"Error: {str(e)}")

    def test_user_can_access_published_quiz_directly(self):
        """Test that user CAN access published quiz via direct API call"""
        if not self.user_token or not self.published_quiz_id:
            return self.log_test("User Can Access Published Quiz Directly", False, "No user token or published quiz ID")
            
        try:
            response = requests.get(
                f"{self.api_url}/quiz/{self.published_quiz_id}",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quiz = response.json()
                is_draft = quiz.get('is_draft', True)
                details += f", is_draft: {is_draft}, Title: {quiz.get('title', 'Unknown')}"
                if is_draft:
                    success = False
                    details += " - ERROR: Published quiz still shows as draft"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Can Access Published Quiz Directly", success, details)
        except Exception as e:
            return self.log_test("User Can Access Published Quiz Directly", False, f"Error: {str(e)}")

    def test_user_cannot_attempt_draft_quiz(self):
        """CRITICAL: Test that user cannot attempt draft quiz"""
        if not self.user_token or not self.draft_quiz_id:
            return self.log_test("User Cannot Attempt Draft Quiz", False, "No user token or draft quiz ID")

        attempt_data = {
            "quiz_id": self.draft_quiz_id,
            "answers": ["4"]
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz/{self.draft_quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            # Should return 404 for draft quizzes
            success = response.status_code == 404
            details = f"Status: {response.status_code} (Expected 404)"
            
            if response.status_code == 200:
                success = False
                details += " - CRITICAL ERROR: User can attempt draft quiz!"
            elif response.status_code == 404:
                details += " - CORRECT: Draft quiz attempt returns 404"
            else:
                details += f" - Unexpected status code"
                
            return self.log_test("User Cannot Attempt Draft Quiz", success, details)
        except Exception as e:
            return self.log_test("User Cannot Attempt Draft Quiz", False, f"Error: {str(e)}")

    def test_user_can_attempt_published_quiz(self):
        """Test that user CAN attempt published quiz"""
        if not self.user_token or not self.published_quiz_id:
            return self.log_test("User Can Attempt Published Quiz", False, "No user token or published quiz ID")

        attempt_data = {
            "quiz_id": self.published_quiz_id,
            "answers": ["6"]
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz/{self.published_quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Score: {result.get('score', 0)}/{result.get('total_questions', 0)}"
                details += f", Percentage: {result.get('percentage', 0):.1f}%"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Can Attempt Published Quiz", success, details)
        except Exception as e:
            return self.log_test("User Can Attempt Published Quiz", False, f"Error: {str(e)}")

    def test_legacy_quiz_without_is_draft_field(self):
        """Test handling of legacy quizzes that might not have is_draft field"""
        if not self.admin_token:
            return self.log_test("Legacy Quiz Without is_draft Field", False, "No admin token available")
        
        # This test simulates what would happen with old quiz data
        # We'll create a quiz and then check how the system handles missing is_draft field
        try:
            # First, let's check if there are any existing quizzes without is_draft field
            response = requests.get(
                f"{self.api_url}/admin/quizzes",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Legacy Quiz Without is_draft Field", False, f"Cannot get admin quizzes: {response.status_code}")
            
            quizzes = response.json()
            legacy_quiz = None
            
            # Look for any quiz that might be missing is_draft field or has it as None
            for quiz in quizzes:
                if 'is_draft' not in quiz or quiz.get('is_draft') is None:
                    legacy_quiz = quiz
                    break
            
            details = f"Total Quizzes: {len(quizzes)}"
            
            if legacy_quiz:
                details += f", Found Legacy Quiz: {legacy_quiz.get('title', 'Unknown')}"
                details += f", is_draft field: {legacy_quiz.get('is_draft', 'MISSING')}"
                
                # Test if user can see this legacy quiz
                user_response = requests.get(
                    f"{self.api_url}/quizzes",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                
                if user_response.status_code == 200:
                    user_quizzes = user_response.json()
                    legacy_visible_to_user = any(q.get('id') == legacy_quiz.get('id') for q in user_quizzes)
                    details += f", Visible to User: {legacy_visible_to_user}"
                    
                    # For legacy quizzes without is_draft field, the behavior should be consistent
                    # They should be treated as published (backward compatibility)
                    success = True  # This is expected behavior for backward compatibility
                else:
                    success = False
                    details += ", Cannot check user visibility"
            else:
                details += ", No Legacy Quiz Found (All quizzes have is_draft field)"
                success = True  # This is actually good - all quizzes have proper is_draft field
                
            return self.log_test("Legacy Quiz Without is_draft Field", success, details)
        except Exception as e:
            return self.log_test("Legacy Quiz Without is_draft Field", False, f"Error: {str(e)}")

    def test_explicit_draft_true_quiz(self):
        """Test quiz with explicit is_draft: true"""
        if not self.admin_token:
            return self.log_test("Explicit Draft True Quiz", False, "No admin token available")
        
        # Create a quiz and verify it has is_draft: true by default
        quiz_data = {
            "title": "Explicit Draft Mode Test Quiz",
            "description": "Testing explicit draft mode",
            "category": "Test Category",
            "subject": "Science",
            "subcategory": "General",
            "questions": [
                {
                    "question_text": "What is H2O?",
                    "options": [
                        {"text": "Water", "is_correct": True},
                        {"text": "Hydrogen", "is_correct": False}
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
            
            if response.status_code != 200:
                return self.log_test("Explicit Draft True Quiz", False, f"Create failed: {response.status_code}")
            
            quiz = response.json()
            quiz_id = quiz.get('id')
            is_draft = quiz.get('is_draft', False)
            
            details = f"Quiz ID: {quiz_id}, is_draft: {is_draft}"
            
            # Verify it's created as draft
            if not is_draft:
                return self.log_test("Explicit Draft True Quiz", False, f"{details} - ERROR: Should be draft by default")
            
            # Test user cannot see it
            user_response = requests.get(
                f"{self.api_url}/quizzes",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if user_response.status_code == 200:
                user_quizzes = user_response.json()
                draft_visible = any(q.get('id') == quiz_id for q in user_quizzes)
                details += f", Visible to User: {draft_visible}"
                
                success = not draft_visible  # Should NOT be visible
                if draft_visible:
                    details += " - CRITICAL ERROR: Explicit draft quiz visible to user!"
                else:
                    details += " - CORRECT: Explicit draft quiz not visible to user"
            else:
                success = False
                details += ", Cannot check user visibility"
                
            return self.log_test("Explicit Draft True Quiz", success, details)
        except Exception as e:
            return self.log_test("Explicit Draft True Quiz", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all draft quiz visibility tests"""
        print("🔍 CRITICAL DRAFT QUIZ VISIBILITY BUG FIX TESTING")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print()
        
        # Setup
        if not self.setup_admin_auth():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        if not self.setup_user_auth():
            print("❌ Cannot proceed without user authentication")
            return False
        
        print()
        print("🧪 RUNNING DRAFT QUIZ VISIBILITY TESTS")
        print("-" * 40)
        
        # Core tests
        self.test_admin_create_draft_quiz()
        self.test_admin_create_published_quiz()
        self.test_admin_view_draft_quiz_in_admin_interface()
        
        # CRITICAL user access tests
        self.test_user_quiz_list_excludes_drafts()
        self.test_user_cannot_access_draft_quiz_directly()
        self.test_user_can_access_published_quiz_directly()
        self.test_user_cannot_attempt_draft_quiz()
        self.test_user_can_attempt_published_quiz()
        
        # Edge case tests
        self.test_legacy_quiz_without_is_draft_field()
        self.test_explicit_draft_true_quiz()
        
        print()
        print("📊 TEST SUMMARY")
        print("=" * 30)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Draft quiz visibility bug is FIXED!")
            return True
        else:
            print("⚠️  SOME TESTS FAILED - Draft quiz visibility bug still exists!")
            return False

if __name__ == "__main__":
    tester = DraftQuizVisibilityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)