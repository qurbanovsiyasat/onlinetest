#!/usr/bin/env python3
"""
Quiz Publishing Functionality Testing for OnlineTestMaker
Tests the enhanced quiz publishing workflow as requested:
1. Test existing quiz publish endpoint
2. Test quiz creation as drafts
3. Test quiz access control for draft vs published
4. Test bulk publishing workflow
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import os

class QuizPublishingTester:
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
        self.draft_quiz_ids = []
        self.published_quiz_ids = []
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

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("🔧 Setting up authentication...")
        
        # Initialize admin if needed
        try:
            requests.post(f"{self.api_url}/init-admin", timeout=10)
        except:
            pass
        
        # Admin login
        admin_login_data = {
            "email": "admin@onlinetestmaker.com",
            "password": "admin123"
        }
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=admin_login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                self.admin_token = response.json().get('access_token')
                print("✅ Admin authentication successful")
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False

        # User registration and login
        user_data = {
            "name": f"Test User {self.test_user_id}",
            "email": f"testuser{self.test_user_id}@example.com",
            "password": "testpass123"
        }
        try:
            # Register user
            requests.post(
                f"{self.api_url}/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
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
            if response.status_code == 200:
                self.user_token = response.json().get('access_token')
                print("✅ User authentication successful")
            else:
                print(f"❌ User login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ User setup error: {str(e)}")
            return False
        
        return True

    def test_quiz_creation_as_draft(self):
        """Test that POST /api/admin/quiz creates quizzes as drafts (is_draft: true)"""
        if not self.admin_token:
            return self.log_test("Quiz Creation as Draft", False, "No admin token available")
            
        quiz_data = {
            "title": "Draft Quiz Test 1",
            "description": "This quiz should be created as a draft",
            "category": "Test Category",
            "subject": "Mathematics",
            "subcategory": "General",
            "questions": [
                {
                    "question_text": "What is 5 + 3?",
                    "options": [
                        {"text": "7", "is_correct": False},
                        {"text": "8", "is_correct": True},
                        {"text": "9", "is_correct": False},
                        {"text": "10", "is_correct": False}
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
                quiz_id = quiz.get('id')
                is_draft = quiz.get('is_draft', False)
                self.draft_quiz_ids.append(quiz_id)
                
                details += f", Quiz ID: {quiz_id}, is_draft: {is_draft}"
                
                # Verify it's actually a draft
                if is_draft:
                    details += " ✓ Created as draft"
                else:
                    success = False
                    details += " ✗ NOT created as draft"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Quiz Creation as Draft", success, details)
        except Exception as e:
            return self.log_test("Quiz Creation as Draft", False, f"Error: {str(e)}")

    def test_draft_quiz_access_control(self):
        """Test that draft quizzes return 404 when users try to access them via GET /api/quiz/{quiz_id}"""
        if not self.user_token or not self.draft_quiz_ids:
            return self.log_test("Draft Quiz Access Control", False, "No user token or draft quiz IDs available")
            
        quiz_id = self.draft_quiz_ids[0]
        
        try:
            response = requests.get(
                f"{self.api_url}/quiz/{quiz_id}",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            # Should return 404 for draft quizzes
            success = response.status_code == 404
            details = f"Status: {response.status_code} (Expected 404 for draft quiz)"
            
            if success:
                details += " ✓ Draft quiz properly blocked"
            else:
                details += f" ✗ Draft quiz accessible, Response: {response.text[:200]}"
                
            return self.log_test("Draft Quiz Access Control", success, details)
        except Exception as e:
            return self.log_test("Draft Quiz Access Control", False, f"Error: {str(e)}")

    def test_quiz_publish_endpoint(self):
        """Test the existing quiz publish endpoint POST /api/admin/quiz/{quiz_id}/publish"""
        if not self.admin_token or not self.draft_quiz_ids:
            return self.log_test("Quiz Publish Endpoint", False, "No admin token or draft quiz IDs available")
            
        quiz_id = self.draft_quiz_ids[0]
        
        try:
            response = requests.post(
                f"{self.api_url}/admin/quiz/{quiz_id}/publish",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                self.published_quiz_ids.append(quiz_id)
                
                # Verify quiz is now published by checking its status
                quiz_response = requests.get(
                    f"{self.api_url}/admin/quizzes",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if quiz_response.status_code == 200:
                    quizzes = quiz_response.json()
                    published_quiz = next((q for q in quizzes if q.get('id') == quiz_id), None)
                    if published_quiz:
                        is_draft = published_quiz.get('is_draft', True)
                        details += f", is_draft after publish: {is_draft}"
                        if not is_draft:
                            details += " ✓ Successfully published"
                        else:
                            success = False
                            details += " ✗ Still marked as draft"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Quiz Publish Endpoint", success, details)
        except Exception as e:
            return self.log_test("Quiz Publish Endpoint", False, f"Error: {str(e)}")

    def test_published_quiz_access(self):
        """Test that published quizzes can be accessed by users"""
        if not self.user_token or not self.published_quiz_ids:
            return self.log_test("Published Quiz Access", False, "No user token or published quiz IDs available")
            
        quiz_id = self.published_quiz_ids[0]
        
        try:
            response = requests.get(
                f"{self.api_url}/quiz/{quiz_id}",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quiz = response.json()
                details += f", Quiz Title: {quiz.get('title', 'Unknown')}"
                details += f", is_draft: {quiz.get('is_draft', 'Unknown')}"
                details += " ✓ Published quiz accessible to users"
            else:
                details += f" ✗ Published quiz not accessible, Response: {response.text[:200]}"
                
            return self.log_test("Published Quiz Access", success, details)
        except Exception as e:
            return self.log_test("Published Quiz Access", False, f"Error: {str(e)}")

    def test_user_quiz_submission_on_published(self):
        """Test that users can submit attempts on published quizzes"""
        if not self.user_token or not self.published_quiz_ids:
            return self.log_test("User Quiz Submission on Published", False, "No user token or published quiz IDs available")
            
        quiz_id = self.published_quiz_ids[0]
        
        attempt_data = {
            "quiz_id": quiz_id,
            "answers": ["8"]  # Correct answer for "What is 5 + 3?"
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz/{quiz_id}/attempt",
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
                details += " ✓ Quiz submission successful on published quiz"
            else:
                details += f" ✗ Quiz submission failed, Response: {response.text[:200]}"
                
            return self.log_test("User Quiz Submission on Published", success, details)
        except Exception as e:
            return self.log_test("User Quiz Submission on Published", False, f"Error: {str(e)}")

    def test_user_quiz_submission_on_draft_blocked(self):
        """Test that users cannot submit attempts on draft quizzes"""
        if not self.user_token or len(self.draft_quiz_ids) < 2:
            return self.log_test("User Quiz Submission on Draft Blocked", False, "No user token or insufficient draft quiz IDs available")
            
        # Use a different draft quiz (not the one we published)
        quiz_id = self.draft_quiz_ids[1] if len(self.draft_quiz_ids) > 1 else self.draft_quiz_ids[0]
        
        attempt_data = {
            "quiz_id": quiz_id,
            "answers": ["8"]
        }

        try:
            response = requests.post(
                f"{self.api_url}/quiz/{quiz_id}/attempt",
                json=attempt_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            # Should return 404 for draft quizzes
            success = response.status_code == 404
            details = f"Status: {response.status_code} (Expected 404 for draft quiz submission)"
            
            if success:
                details += " ✓ Draft quiz submission properly blocked"
            else:
                details += f" ✗ Draft quiz submission allowed, Response: {response.text[:200]}"
                
            return self.log_test("User Quiz Submission on Draft Blocked", success, details)
        except Exception as e:
            return self.log_test("User Quiz Submission on Draft Blocked", False, f"Error: {str(e)}")

    def create_multiple_draft_quizzes(self):
        """Create multiple draft quizzes for bulk publishing test"""
        if not self.admin_token:
            return False
            
        quiz_templates = [
            {
                "title": "Draft Quiz for Bulk Test 1",
                "description": "First quiz for bulk publishing test",
                "category": "Bulk Test",
                "subject": "Science",
                "subcategory": "General",
                "questions": [
                    {
                        "question_text": "What is H2O?",
                        "options": [
                            {"text": "Hydrogen", "is_correct": False},
                            {"text": "Water", "is_correct": True},
                            {"text": "Oxygen", "is_correct": False},
                            {"text": "Carbon", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "title": "Draft Quiz for Bulk Test 2",
                "description": "Second quiz for bulk publishing test",
                "category": "Bulk Test",
                "subject": "History",
                "subcategory": "General",
                "questions": [
                    {
                        "question_text": "Who was the first president of the USA?",
                        "options": [
                            {"text": "Thomas Jefferson", "is_correct": False},
                            {"text": "George Washington", "is_correct": True},
                            {"text": "John Adams", "is_correct": False},
                            {"text": "Benjamin Franklin", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "title": "Draft Quiz for Bulk Test 3",
                "description": "Third quiz for bulk publishing test",
                "category": "Bulk Test",
                "subject": "Geography",
                "subcategory": "General",
                "questions": [
                    {
                        "question_text": "What is the capital of Japan?",
                        "options": [
                            {"text": "Seoul", "is_correct": False},
                            {"text": "Beijing", "is_correct": False},
                            {"text": "Tokyo", "is_correct": True},
                            {"text": "Bangkok", "is_correct": False}
                        ]
                    }
                ]
            }
        ]
        
        created_count = 0
        for quiz_data in quiz_templates:
            try:
                response = requests.post(
                    f"{self.api_url}/admin/quiz",
                    json=quiz_data,
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if response.status_code == 200:
                    quiz = response.json()
                    self.draft_quiz_ids.append(quiz.get('id'))
                    created_count += 1
            except:
                continue
        
        return created_count >= 2  # Need at least 2 for bulk test

    def test_bulk_publishing_workflow(self):
        """Test bulk publishing workflow - create multiple draft quizzes and verify they can be published individually"""
        print("🔧 Creating multiple draft quizzes for bulk publishing test...")
        
        if not self.create_multiple_draft_quizzes():
            return self.log_test("Bulk Publishing Workflow", False, "Failed to create multiple draft quizzes")
        
        # Get the last 3 draft quizzes for bulk publishing
        bulk_quiz_ids = self.draft_quiz_ids[-3:] if len(self.draft_quiz_ids) >= 3 else self.draft_quiz_ids[-2:]
        
        if len(bulk_quiz_ids) < 2:
            return self.log_test("Bulk Publishing Workflow", False, "Insufficient draft quizzes for bulk test")
        
        published_count = 0
        failed_count = 0
        
        try:
            for i, quiz_id in enumerate(bulk_quiz_ids):
                # Publish each quiz individually
                response = requests.post(
                    f"{self.api_url}/admin/quiz/{quiz_id}/publish",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                
                if response.status_code == 200:
                    published_count += 1
                    self.published_quiz_ids.append(quiz_id)
                else:
                    failed_count += 1
            
            success = published_count >= 2 and failed_count == 0
            details = f"Published: {published_count}, Failed: {failed_count}, Total Attempted: {len(bulk_quiz_ids)}"
            
            if success:
                details += " ✓ Bulk publishing workflow successful"
                
                # Verify published quizzes are accessible
                accessible_count = 0
                for quiz_id in bulk_quiz_ids:
                    try:
                        response = requests.get(
                            f"{self.api_url}/quiz/{quiz_id}",
                            headers=self.get_auth_headers(self.user_token),
                            timeout=10
                        )
                        if response.status_code == 200:
                            accessible_count += 1
                    except:
                        continue
                
                details += f", Accessible to users: {accessible_count}/{len(bulk_quiz_ids)}"
            else:
                details += " ✗ Bulk publishing workflow failed"
                
            return self.log_test("Bulk Publishing Workflow", success, details)
        except Exception as e:
            return self.log_test("Bulk Publishing Workflow", False, f"Error: {str(e)}")

    def test_admin_get_draft_vs_published_quizzes(self):
        """Test admin can distinguish between draft and published quizzes"""
        if not self.admin_token:
            return self.log_test("Admin Get Draft vs Published Quizzes", False, "No admin token available")
            
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
                draft_count = sum(1 for q in quizzes if q.get('is_draft', False))
                published_count = sum(1 for q in quizzes if not q.get('is_draft', True))
                
                details += f", Total Quizzes: {len(quizzes)}, Drafts: {draft_count}, Published: {published_count}"
                
                # Verify we have both draft and published quizzes
                if draft_count > 0 and published_count > 0:
                    details += " ✓ Both draft and published quizzes present"
                else:
                    details += f" ⚠ Limited quiz types (Drafts: {draft_count}, Published: {published_count})"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Get Draft vs Published Quizzes", success, details)
        except Exception as e:
            return self.log_test("Admin Get Draft vs Published Quizzes", False, f"Error: {str(e)}")

    def test_publish_nonexistent_quiz(self):
        """Test publishing a non-existent quiz returns proper error"""
        if not self.admin_token:
            return self.log_test("Publish Nonexistent Quiz", False, "No admin token available")
            
        fake_quiz_id = str(uuid.uuid4())
        
        try:
            response = requests.post(
                f"{self.api_url}/admin/quiz/{fake_quiz_id}/publish",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            # Should return 404 for non-existent quiz
            success = response.status_code == 404
            details = f"Status: {response.status_code} (Expected 404 for non-existent quiz)"
            
            if success:
                details += " ✓ Proper error handling for non-existent quiz"
            else:
                details += f" ✗ Unexpected response, Response: {response.text[:200]}"
                
            return self.log_test("Publish Nonexistent Quiz", success, details)
        except Exception as e:
            return self.log_test("Publish Nonexistent Quiz", False, f"Error: {str(e)}")

    def test_user_cannot_publish_quiz(self):
        """Test that regular users cannot publish quizzes"""
        if not self.user_token or not self.draft_quiz_ids:
            return self.log_test("User Cannot Publish Quiz", False, "No user token or draft quiz IDs available")
            
        quiz_id = self.draft_quiz_ids[-1]  # Use last draft quiz
        
        try:
            response = requests.post(
                f"{self.api_url}/admin/quiz/{quiz_id}/publish",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            # Should return 403 for regular users
            success = response.status_code == 403
            details = f"Status: {response.status_code} (Expected 403 for user trying to publish)"
            
            if success:
                details += " ✓ User properly blocked from publishing"
            else:
                details += f" ✗ User allowed to publish, Response: {response.text[:200]}"
                
            return self.log_test("User Cannot Publish Quiz", success, details)
        except Exception as e:
            return self.log_test("User Cannot Publish Quiz", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all quiz publishing tests"""
        print("🚀 Starting Quiz Publishing Functionality Tests")
        print("=" * 60)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Aborting tests.")
            return
        
        # Test 1: Quiz creation as drafts
        self.test_quiz_creation_as_draft()
        
        # Create another draft quiz for more comprehensive testing
        self.test_quiz_creation_as_draft()
        
        # Test 2: Draft quiz access control
        self.test_draft_quiz_access_control()
        
        # Test 3: Quiz publish endpoint
        self.test_quiz_publish_endpoint()
        
        # Test 4: Published quiz access
        self.test_published_quiz_access()
        
        # Test 5: User quiz submission on published quiz
        self.test_user_quiz_submission_on_published()
        
        # Test 6: User quiz submission blocked on draft
        self.test_user_quiz_submission_on_draft_blocked()
        
        # Test 7: Bulk publishing workflow
        self.test_bulk_publishing_workflow()
        
        # Test 8: Admin can distinguish draft vs published
        self.test_admin_get_draft_vs_published_quizzes()
        
        # Test 9: Error handling - publish nonexistent quiz
        self.test_publish_nonexistent_quiz()
        
        # Test 10: User cannot publish quiz
        self.test_user_cannot_publish_quiz()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"🏁 Quiz Publishing Tests Complete")
        print(f"📊 Results: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All quiz publishing functionality tests PASSED!")
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} test(s) FAILED")
        
        print(f"📝 Created {len(self.draft_quiz_ids)} draft quizzes")
        print(f"🚀 Published {len(self.published_quiz_ids)} quizzes")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = QuizPublishingTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)