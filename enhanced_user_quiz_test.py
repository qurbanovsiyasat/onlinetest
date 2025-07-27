#!/usr/bin/env python3
"""
Enhanced User Quiz Management System Testing
Tests the new user quiz creation and management capabilities with ownership model
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import os

class EnhancedUserQuizTester:
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
        self.test_user_id = str(uuid.uuid4())[:8]
        self.created_global_subject_id = None
        self.created_personal_subject_id = None
        self.created_user_quiz_id = None
        self.created_admin_quiz_id = None

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
        """Test admin login with Squiz credentials"""
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
                
            return self.log_test("Admin Login (Squiz)", success, details)
        except Exception as e:
            return self.log_test("Admin Login (Squiz)", False, f"Error: {str(e)}")

    def test_user_registration_and_login(self):
        """Test user registration and login"""
        user_data = {
            "name": f"Test User {self.test_user_id}",
            "email": f"testuser{self.test_user_id}@example.com",
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
                details += f", Role: {user_info.get('role', 'Unknown')}, Name: {user_info.get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Registration and Login", success, details)
        except Exception as e:
            return self.log_test("User Registration and Login", False, f"Error: {str(e)}")

    def test_admin_create_global_subject(self):
        """Test admin creating global subject with subfolders"""
        if not self.admin_token:
            return self.log_test("Admin Create Global Subject", False, "No admin token available")
            
        subject_data = {
            "name": "Advanced Mathematics",
            "description": "Advanced mathematical concepts and theories",
            "subfolders": ["Calculus", "Linear Algebra", "Statistics", "Geometry"]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin/global-subject",
                json=subject_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                subject = response.json()
                self.created_global_subject_id = subject.get('id')
                details += f", Subject ID: {self.created_global_subject_id}"
                details += f", Name: {subject.get('name', 'Unknown')}"
                details += f", Subfolders: {len(subject.get('subfolders', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Global Subject", success, details)
        except Exception as e:
            return self.log_test("Admin Create Global Subject", False, f"Error: {str(e)}")

    def test_user_create_personal_subject(self):
        """Test user creating personal subject with subfolders"""
        if not self.user_token:
            return self.log_test("User Create Personal Subject", False, "No user token available")
            
        subject_data = {
            "name": "My Programming Studies",
            "description": "Personal programming learning journey",
            "subfolders": ["Python", "JavaScript", "React", "FastAPI"]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/user/personal-subject",
                json=subject_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                subject = response.json()
                self.created_personal_subject_id = subject.get('id')
                details += f", Subject ID: {self.created_personal_subject_id}"
                details += f", Name: {subject.get('name', 'Unknown')}"
                details += f", Subfolders: {len(subject.get('subfolders', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Create Personal Subject", success, details)
        except Exception as e:
            return self.log_test("User Create Personal Subject", False, f"Error: {str(e)}")

    def test_user_available_subjects_api(self):
        """Test GET /user/available-subjects to get combined global and personal subjects"""
        if not self.user_token:
            return self.log_test("User Available Subjects API", False, "No user token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/user/available-subjects",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                global_subjects = data.get('global_subjects', [])
                personal_subjects = data.get('personal_subjects', [])
                combined = data.get('combined', [])
                
                details += f", Global: {len(global_subjects)}, Personal: {len(personal_subjects)}, Combined: {len(combined)}"
                
                # Check for our created subjects
                global_found = any(s.get('name') == 'Advanced Mathematics' for s in global_subjects)
                personal_found = any(s.get('name') == 'My Programming Studies' for s in personal_subjects)
                details += f", Global Found: {global_found}, Personal Found: {personal_found}"
                
                # Check formatting (icons)
                if global_subjects:
                    first_global = global_subjects[0]
                    details += f", Global Icon: {first_global.get('name', '').startswith('🌐')}"
                if personal_subjects:
                    first_personal = personal_subjects[0]
                    details += f", Personal Icon: {first_personal.get('name', '').startswith('👤')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Available Subjects API", success, details)
        except Exception as e:
            return self.log_test("User Available Subjects API", False, f"Error: {str(e)}")

    def test_user_create_quiz(self):
        """Test POST /user/quiz to create user-owned quiz"""
        if not self.user_token:
            return self.log_test("User Create Quiz", False, "No user token available")
            
        quiz_data = {
            "title": "User Created Quiz - Python Basics",
            "description": "A quiz about Python programming basics created by a user",
            "category": "Programming",
            "subject": "My Programming Studies",
            "subcategory": "Python",
            "questions": [
                {
                    "question_text": "What is the correct way to create a list in Python?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "list = []", "is_correct": True},
                        {"text": "list = {}", "is_correct": False},
                        {"text": "list = ()", "is_correct": False},
                        {"text": "list = <>", "is_correct": False}
                    ],
                    "points": 1
                },
                {
                    "question_text": "What does 'len()' function do in Python?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "Returns the length of an object", "is_correct": True},
                        {"text": "Creates a new list", "is_correct": False},
                        {"text": "Sorts a list", "is_correct": False},
                        {"text": "Deletes an object", "is_correct": False}
                    ],
                    "points": 1
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/user/quiz",
                json=quiz_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quiz = response.json()
                self.created_user_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.created_user_quiz_id}"
                details += f", Title: {quiz.get('title', 'Unknown')}"
                details += f", Owner Type: {quiz.get('quiz_owner_type', 'Unknown')}"
                details += f", Is Draft: {quiz.get('is_draft', 'Unknown')}"
                details += f", Questions: {quiz.get('total_questions', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Create Quiz", success, details)
        except Exception as e:
            return self.log_test("User Create Quiz", False, f"Error: {str(e)}")

    def test_user_get_my_quizzes(self):
        """Test GET /user/my-quizzes to retrieve user's created quizzes"""
        if not self.user_token:
            return self.log_test("User Get My Quizzes", False, "No user token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/user/my-quizzes",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quizzes = response.json()
                details += f", My Quizzes Count: {len(quizzes)}"
                
                # Check if our created quiz is there
                user_quiz_found = any(q.get('id') == self.created_user_quiz_id for q in quizzes)
                details += f", User Quiz Found: {user_quiz_found}"
                
                if quizzes:
                    first_quiz = quizzes[0]
                    details += f", First Quiz: {first_quiz.get('title', 'Unknown')}"
                    details += f", Owner Type: {first_quiz.get('quiz_owner_type', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Get My Quizzes", success, details)
        except Exception as e:
            return self.log_test("User Get My Quizzes", False, f"Error: {str(e)}")

    def test_user_update_quiz(self):
        """Test PUT /user/quiz/{id} to update user's quiz"""
        if not self.user_token or not self.created_user_quiz_id:
            return self.log_test("User Update Quiz", False, "No user token or quiz ID available")
            
        update_data = {
            "title": "Updated User Quiz - Python Advanced",
            "description": "Updated description for advanced Python concepts",
            "category": "Advanced Programming"
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/user/quiz/{self.created_user_quiz_id}",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quiz = response.json()
                details += f", Updated Title: {quiz.get('title', 'Unknown')}"
                details += f", Updated Category: {quiz.get('category', 'Unknown')}"
                details += f", Owner Type: {quiz.get('quiz_owner_type', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Update Quiz", success, details)
        except Exception as e:
            return self.log_test("User Update Quiz", False, f"Error: {str(e)}")

    def test_user_publish_quiz(self):
        """Test POST /user/quiz/{id}/publish to publish user's draft quiz"""
        if not self.user_token or not self.created_user_quiz_id:
            return self.log_test("User Publish Quiz", False, "No user token or quiz ID available")
            
        try:
            response = requests.post(
                f"{self.api_url}/user/quiz/{self.created_user_quiz_id}/publish",
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
                
            return self.log_test("User Publish Quiz", success, details)
        except Exception as e:
            return self.log_test("User Publish Quiz", False, f"Error: {str(e)}")

    def test_admin_create_quiz_with_ownership(self):
        """Test admin creating quiz with proper ownership fields"""
        if not self.admin_token:
            return self.log_test("Admin Create Quiz with Ownership", False, "No admin token available")
            
        quiz_data = {
            "title": "Admin Created Quiz - Mathematics",
            "description": "A mathematics quiz created by admin with ownership tracking",
            "category": "Mathematics",
            "subject": "Advanced Mathematics",
            "subcategory": "Calculus",
            "questions": [
                {
                    "question_text": "What is the derivative of x²?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "x", "is_correct": False},
                        {"text": "2x", "is_correct": True},
                        {"text": "x²", "is_correct": False},
                        {"text": "2x²", "is_correct": False}
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
                self.created_admin_quiz_id = quiz.get('id')
                details += f", Quiz ID: {self.created_admin_quiz_id}"
                details += f", Owner Type: {quiz.get('quiz_owner_type', 'Unknown')}"
                details += f", Owner ID: {quiz.get('quiz_owner_id', 'Unknown')}"
                details += f", Is Draft: {quiz.get('is_draft', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Quiz with Ownership", success, details)
        except Exception as e:
            return self.log_test("Admin Create Quiz with Ownership", False, f"Error: {str(e)}")

    def test_enhanced_public_quiz_access(self):
        """Test GET /api/quizzes shows both admin and published user quizzes while filtering drafts"""
        if not self.user_token:
            return self.log_test("Enhanced Public Quiz Access", False, "No user token available")
            
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
                details += f", Total Quizzes: {len(quizzes)}"
                
                # Count by ownership type
                admin_quizzes = [q for q in quizzes if q.get('quiz_owner_type') == 'admin']
                user_quizzes = [q for q in quizzes if q.get('quiz_owner_type') == 'user']
                draft_quizzes = [q for q in quizzes if q.get('is_draft') == True]
                
                details += f", Admin Quizzes: {len(admin_quizzes)}"
                details += f", User Quizzes: {len(user_quizzes)}"
                details += f", Draft Quizzes: {len(draft_quizzes)}"  # Should be 0
                
                # Check if our published user quiz is visible
                user_quiz_visible = any(q.get('id') == self.created_user_quiz_id for q in quizzes)
                details += f", User Quiz Visible: {user_quiz_visible}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Enhanced Public Quiz Access", success, details)
        except Exception as e:
            return self.log_test("Enhanced Public Quiz Access", False, f"Error: {str(e)}")

    def test_admin_get_all_quizzes_with_ownership(self):
        """Test GET /api/admin/quizzes shows all quizzes with ownership information"""
        if not self.admin_token:
            return self.log_test("Admin Get All Quizzes with Ownership", False, "No admin token available")
            
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
                details += f", Total Quizzes: {len(quizzes)}"
                
                # Count by ownership type and status
                admin_quizzes = [q for q in quizzes if q.get('quiz_owner_type') == 'admin']
                user_quizzes = [q for q in quizzes if q.get('quiz_owner_type') == 'user']
                draft_quizzes = [q for q in quizzes if q.get('is_draft') == True]
                published_quizzes = [q for q in quizzes if q.get('is_draft') == False]
                
                details += f", Admin Quizzes: {len(admin_quizzes)}"
                details += f", User Quizzes: {len(user_quizzes)}"
                details += f", Draft: {len(draft_quizzes)}"
                details += f", Published: {len(published_quizzes)}"
                
                # Check if both our quizzes are visible
                admin_quiz_found = any(q.get('id') == self.created_admin_quiz_id for q in quizzes)
                user_quiz_found = any(q.get('id') == self.created_user_quiz_id for q in quizzes)
                details += f", Admin Quiz Found: {admin_quiz_found}, User Quiz Found: {user_quiz_found}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Get All Quizzes with Ownership", success, details)
        except Exception as e:
            return self.log_test("Admin Get All Quizzes with Ownership", False, f"Error: {str(e)}")

    def test_ownership_access_control(self):
        """Test that users can only manage their own quizzes"""
        if not self.user_token or not self.created_admin_quiz_id:
            return self.log_test("Ownership Access Control", False, "No user token or admin quiz ID available")
            
        # Try to update admin's quiz as user (should fail)
        update_data = {
            "title": "Trying to hack admin quiz"
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/user/quiz/{self.created_admin_quiz_id}",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 404  # Should return 404 (not found) for security
            details = f"Status: {response.status_code} (Expected 404)"
            
            if not success:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Ownership Access Control", success, details)
        except Exception as e:
            return self.log_test("Ownership Access Control", False, f"Error: {str(e)}")

    def test_user_cannot_access_admin_global_subjects(self):
        """Test that users cannot access admin global subject endpoints"""
        if not self.user_token:
            return self.log_test("User Cannot Access Admin Global Subjects", False, "No user token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/global-subjects",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            
            return self.log_test("User Cannot Access Admin Global Subjects", success, details)
        except Exception as e:
            return self.log_test("User Cannot Access Admin Global Subjects", False, f"Error: {str(e)}")

    def test_user_delete_own_quiz(self):
        """Test DELETE /user/quiz/{id} to delete user's own quiz"""
        if not self.user_token or not self.created_user_quiz_id:
            return self.log_test("User Delete Own Quiz", False, "No user token or quiz ID available")
            
        try:
            response = requests.delete(
                f"{self.api_url}/user/quiz/{self.created_user_quiz_id}",
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
                
            return self.log_test("User Delete Own Quiz", success, details)
        except Exception as e:
            return self.log_test("User Delete Own Quiz", False, f"Error: {str(e)}")

    def test_draft_quiz_filtering_verification(self):
        """Test that draft quizzes are properly filtered from public access"""
        if not self.admin_token:
            return self.log_test("Draft Quiz Filtering Verification", False, "No admin token available")
            
        # Create a draft quiz
        draft_quiz_data = {
            "title": "Draft Quiz - Should Not Be Accessible",
            "description": "This quiz should not be visible to regular users",
            "category": "Test",
            "subject": "Test Subject",
            "subcategory": "Test",
            "questions": [
                {
                    "question_text": "This is a draft question",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "Option 1", "is_correct": True},
                        {"text": "Option 2", "is_correct": False}
                    ],
                    "points": 1
                }
            ]
        }
        
        try:
            # Create draft quiz
            response = requests.post(
                f"{self.api_url}/admin/quiz",
                json=draft_quiz_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Draft Quiz Filtering Verification", False, f"Failed to create draft quiz: {response.status_code}")
            
            draft_quiz = response.json()
            draft_quiz_id = draft_quiz.get('id')
            
            # Verify it's a draft
            is_draft = draft_quiz.get('is_draft', False)
            if not is_draft:
                return self.log_test("Draft Quiz Filtering Verification", False, "Quiz was not created as draft")
            
            # Now check if it's visible in public quiz list (should not be)
            public_response = requests.get(
                f"{self.api_url}/quizzes",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if public_response.status_code != 200:
                return self.log_test("Draft Quiz Filtering Verification", False, f"Failed to get public quizzes: {public_response.status_code}")
            
            public_quizzes = public_response.json()
            draft_visible = any(q.get('id') == draft_quiz_id for q in public_quizzes)
            
            # Try to access draft quiz directly (should fail)
            direct_response = requests.get(
                f"{self.api_url}/quiz/{draft_quiz_id}",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            direct_access_blocked = direct_response.status_code == 404
            
            success = not draft_visible and direct_access_blocked
            details = f"Draft Visible in Public List: {draft_visible}, Direct Access Blocked: {direct_access_blocked}"
            
            return self.log_test("Draft Quiz Filtering Verification", success, details)
        except Exception as e:
            return self.log_test("Draft Quiz Filtering Verification", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all enhanced user quiz management tests"""
        print("🚀 Starting Enhanced User Quiz Management System Testing")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Authentication tests
        self.test_admin_login()
        self.test_user_registration_and_login()
        
        # Global subject management (admin)
        self.test_admin_create_global_subject()
        
        # Personal subject management (user)
        self.test_user_create_personal_subject()
        self.test_user_available_subjects_api()
        
        # User quiz creation and management
        self.test_user_create_quiz()
        self.test_user_get_my_quizzes()
        self.test_user_update_quiz()
        self.test_user_publish_quiz()
        
        # Admin quiz creation with ownership
        self.test_admin_create_quiz_with_ownership()
        
        # Enhanced public quiz access
        self.test_enhanced_public_quiz_access()
        self.test_admin_get_all_quizzes_with_ownership()
        
        # Access control and security
        self.test_ownership_access_control()
        self.test_user_cannot_access_admin_global_subjects()
        self.test_draft_quiz_filtering_verification()
        
        # Cleanup
        self.test_user_delete_own_quiz()
        
        print("=" * 80)
        print(f"🏁 Testing Complete: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Enhanced user quiz management system is working perfectly.")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Please check the issues above.")
            return False

if __name__ == "__main__":
    tester = EnhancedUserQuizTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)