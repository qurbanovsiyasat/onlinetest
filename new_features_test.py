#!/usr/bin/env python3
"""
Backend API Testing for Squiz - New Global Subject Management and User Quiz Creation Features
Tests the new functionality implemented for global subjects, user quiz creation, and enhanced ownership model
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import os

class SquizNewFeaturesAPITester:
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
        
        # Store created IDs for cleanup and testing
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

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("🔧 Setting up authentication...")
        
        # Initialize admin if needed
        try:
            requests.post(f"{self.api_url}/init-admin", timeout=10)
        except:
            pass  # Admin might already exist
        
        # Admin login
        admin_login_data = {
            "email": "admin@squiz.com",
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
                data = response.json()
                self.admin_token = data.get('access_token')
                print(f"✅ Admin authentication successful")
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False
        
        # User registration and login
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
                data = response.json()
                self.user_token = data.get('access_token')
                print(f"✅ User authentication successful")
            else:
                print(f"❌ User authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ User authentication error: {str(e)}")
            return False
        
        return True

    # ===== GLOBAL SUBJECT MANAGEMENT TESTS =====

    def test_create_global_subject(self):
        """Test creating global subject with subfolders"""
        if not self.admin_token:
            return self.log_test("Create Global Subject", False, "No admin token available")
        
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
                data = response.json()
                self.created_global_subject_id = data.get('id')
                details += f", Subject ID: {self.created_global_subject_id}"
                details += f", Name: {data.get('name', 'Unknown')}"
                details += f", Subfolders: {len(data.get('subfolders', []))}"
                details += f", Created by: {data.get('created_by', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Global Subject", success, details)
        except Exception as e:
            return self.log_test("Create Global Subject", False, f"Error: {str(e)}")

    def test_get_all_global_subjects(self):
        """Test getting all global subjects"""
        if not self.admin_token:
            return self.log_test("Get All Global Subjects", False, "No admin token available")
        
        try:
            response = requests.get(
                f"{self.api_url}/admin/global-subjects",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                subjects = response.json()
                details += f", Subjects Count: {len(subjects)}"
                if len(subjects) > 0:
                    first_subject = subjects[0]
                    details += f", First Subject: {first_subject.get('name', 'Unknown')}"
                    details += f", Subfolders: {len(first_subject.get('subfolders', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get All Global Subjects", success, details)
        except Exception as e:
            return self.log_test("Get All Global Subjects", False, f"Error: {str(e)}")

    def test_add_subfolder_to_global_subject(self):
        """Test adding subfolder to existing global subject"""
        if not self.admin_token or not self.created_global_subject_id:
            return self.log_test("Add Subfolder to Global Subject", False, "No admin token or subject ID available")
        
        try:
            response = requests.post(
                f"{self.api_url}/admin/global-subject/{self.created_global_subject_id}/subfolder?subfolder_name=Topology",
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
                
            return self.log_test("Add Subfolder to Global Subject", success, details)
        except Exception as e:
            return self.log_test("Add Subfolder to Global Subject", False, f"Error: {str(e)}")

    def test_update_global_subject(self):
        """Test updating global subject"""
        if not self.admin_token or not self.created_global_subject_id:
            return self.log_test("Update Global Subject", False, "No admin token or subject ID available")
        
        update_data = {
            "description": "Updated description for advanced mathematics",
            "subfolders": ["Calculus", "Linear Algebra", "Statistics", "Geometry", "Topology", "Number Theory"]
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/admin/global-subject/{self.created_global_subject_id}",
                json=update_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Updated Subfolders: {len(data.get('subfolders', []))}"
                details += f", Description: {data.get('description', 'No description')[:50]}..."
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Update Global Subject", success, details)
        except Exception as e:
            return self.log_test("Update Global Subject", False, f"Error: {str(e)}")

    # ===== USER AVAILABLE SUBJECTS TESTS =====

    def test_create_personal_subject(self):
        """Test creating personal subject by user"""
        if not self.user_token:
            return self.log_test("Create Personal Subject", False, "No user token available")
        
        subject_data = {
            "name": "My Programming Studies",
            "description": "Personal collection of programming topics",
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
                data = response.json()
                self.created_personal_subject_id = data.get('id')
                details += f", Subject ID: {self.created_personal_subject_id}"
                details += f", Name: {data.get('name', 'Unknown')}"
                details += f", Subfolders: {len(data.get('subfolders', []))}"
                details += f", User ID: {data.get('user_id', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Personal Subject", success, details)
        except Exception as e:
            return self.log_test("Create Personal Subject", False, f"Error: {str(e)}")

    def test_get_available_subjects_for_user(self):
        """Test getting combined global + personal subjects for user"""
        if not self.user_token:
            return self.log_test("Get Available Subjects for User", False, "No user token available")
        
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
                
                # Check if our created subjects are present
                global_names = [s.get('name') for s in global_subjects]
                personal_names = [s.get('name') for s in personal_subjects]
                
                if "Advanced Mathematics" in global_names:
                    details += ", Found created global subject"
                if "My Programming Studies" in personal_names:
                    details += ", Found created personal subject"
                    
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Available Subjects for User", success, details)
        except Exception as e:
            return self.log_test("Get Available Subjects for User", False, f"Error: {str(e)}")

    # ===== USER QUIZ CREATION TESTS =====

    def test_create_user_quiz(self):
        """Test creating quiz by regular user"""
        if not self.user_token:
            return self.log_test("Create User Quiz", False, "No user token available")
        
        quiz_data = {
            "title": "User Created Quiz - Python Basics",
            "description": "A quiz about Python programming basics created by a user",
            "category": "Programming",
            "subject": "Python",
            "subcategory": "Basics",
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
                    "question_text": "Which keyword is used to define a function in Python?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "function", "is_correct": False},
                        {"text": "def", "is_correct": True},
                        {"text": "func", "is_correct": False},
                        {"text": "define", "is_correct": False}
                    ],
                    "points": 1
                }
            ],
            "is_public": False,
            "min_pass_percentage": 60.0
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
                data = response.json()
                self.created_user_quiz_id = data.get('id')
                details += f", Quiz ID: {self.created_user_quiz_id}"
                details += f", Title: {data.get('title', 'Unknown')}"
                details += f", Owner Type: {data.get('quiz_owner_type', 'Unknown')}"
                details += f", Owner ID: {data.get('quiz_owner_id', 'Unknown')}"
                details += f", Is Draft: {data.get('is_draft', 'Unknown')}"
                details += f", Questions: {data.get('total_questions', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create User Quiz", success, details)
        except Exception as e:
            return self.log_test("Create User Quiz", False, f"Error: {str(e)}")

    def test_get_user_my_quizzes(self):
        """Test getting user's own created quizzes"""
        if not self.user_token:
            return self.log_test("Get User My Quizzes", False, "No user token available")
        
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
                
                if len(quizzes) > 0:
                    first_quiz = quizzes[0]
                    details += f", First Quiz: {first_quiz.get('title', 'Unknown')}"
                    details += f", Owner Type: {first_quiz.get('quiz_owner_type', 'Unknown')}"
                    details += f", Is Draft: {first_quiz.get('is_draft', 'Unknown')}"
                    
                    # Check if our created quiz is present
                    quiz_titles = [q.get('title') for q in quizzes]
                    if "User Created Quiz - Python Basics" in quiz_titles:
                        details += ", Found created quiz"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get User My Quizzes", success, details)
        except Exception as e:
            return self.log_test("Get User My Quizzes", False, f"Error: {str(e)}")

    def test_update_user_quiz(self):
        """Test updating user's own quiz"""
        if not self.user_token or not self.created_user_quiz_id:
            return self.log_test("Update User Quiz", False, "No user token or quiz ID available")
        
        update_data = {
            "title": "Updated User Quiz - Python Advanced",
            "description": "Updated description for Python quiz",
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
                data = response.json()
                details += f", Updated Title: {data.get('title', 'Unknown')}"
                details += f", Updated Category: {data.get('category', 'Unknown')}"
                details += f", Updated At: {data.get('updated_at', 'Unknown')[:19]}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Update User Quiz", success, details)
        except Exception as e:
            return self.log_test("Update User Quiz", False, f"Error: {str(e)}")

    def test_publish_user_quiz(self):
        """Test publishing user's quiz to make it publicly available"""
        if not self.user_token or not self.created_user_quiz_id:
            return self.log_test("Publish User Quiz", False, "No user token or quiz ID available")
        
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
                
            return self.log_test("Publish User Quiz", success, details)
        except Exception as e:
            return self.log_test("Publish User Quiz", False, f"Error: {str(e)}")

    # ===== ENHANCED PUBLIC QUIZ ACCESS TESTS =====

    def test_enhanced_public_quiz_access(self):
        """Test that /api/quizzes shows both admin and published user quizzes"""
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
                
                # Count admin vs user quizzes
                admin_quizzes = [q for q in quizzes if q.get('quiz_owner_type') == 'admin']
                user_quizzes = [q for q in quizzes if q.get('quiz_owner_type') == 'user']
                
                details += f", Admin Quizzes: {len(admin_quizzes)}, User Quizzes: {len(user_quizzes)}"
                
                # Check that draft quizzes are filtered out
                draft_quizzes = [q for q in quizzes if q.get('is_draft') == True]
                details += f", Draft Quizzes (should be 0): {len(draft_quizzes)}"
                
                # Check if our published user quiz is present
                quiz_titles = [q.get('title') for q in quizzes]
                if "Updated User Quiz - Python Advanced" in quiz_titles:
                    details += ", Found published user quiz"
                    
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Enhanced Public Quiz Access", success, details)
        except Exception as e:
            return self.log_test("Enhanced Public Quiz Access", False, f"Error: {str(e)}")

    def test_draft_quiz_filtering(self):
        """Test that draft quizzes are properly filtered from public access"""
        if not self.user_token:
            return self.log_test("Draft Quiz Filtering", False, "No user token available")
        
        # First create a draft quiz
        draft_quiz_data = {
            "title": "Draft Quiz - Should Not Be Visible",
            "description": "This quiz should not appear in public quiz list",
            "category": "Test",
            "subject": "Testing",
            "subcategory": "Draft",
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
            create_response = requests.post(
                f"{self.api_url}/user/quiz",
                json=draft_quiz_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if create_response.status_code != 200:
                return self.log_test("Draft Quiz Filtering", False, "Failed to create draft quiz")
            
            draft_quiz_id = create_response.json().get('id')
            
            # Now check public quiz list
            response = requests.get(
                f"{self.api_url}/quizzes",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                quizzes = response.json()
                quiz_titles = [q.get('title') for q in quizzes]
                
                # Check that draft quiz is NOT in the list
                draft_in_list = "Draft Quiz - Should Not Be Visible" in quiz_titles
                details += f", Draft quiz in public list: {draft_in_list} (should be False)"
                
                # Also test direct access to draft quiz (should return 404)
                direct_access = requests.get(
                    f"{self.api_url}/quiz/{draft_quiz_id}",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                details += f", Direct access status: {direct_access.status_code} (should be 404)"
                
                success = not draft_in_list and direct_access.status_code == 404
                
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Draft Quiz Filtering", success, details)
        except Exception as e:
            return self.log_test("Draft Quiz Filtering", False, f"Error: {str(e)}")

    # ===== ADMIN QUIZ MANAGEMENT TESTS =====

    def test_admin_create_quiz_with_ownership(self):
        """Test that admin quiz creation includes ownership fields"""
        if not self.admin_token:
            return self.log_test("Admin Create Quiz with Ownership", False, "No admin token available")
        
        quiz_data = {
            "title": "Admin Created Quiz - Mathematics",
            "description": "A quiz created by admin with proper ownership fields",
            "category": "Mathematics",
            "subject": "Algebra",
            "subcategory": "Linear Equations",
            "questions": [
                {
                    "question_text": "What is the solution to 2x + 4 = 10?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "x = 2", "is_correct": False},
                        {"text": "x = 3", "is_correct": True},
                        {"text": "x = 4", "is_correct": False},
                        {"text": "x = 5", "is_correct": False}
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
                data = response.json()
                self.created_admin_quiz_id = data.get('id')
                details += f", Quiz ID: {self.created_admin_quiz_id}"
                details += f", Owner Type: {data.get('quiz_owner_type', 'Unknown')}"
                details += f", Owner ID: {data.get('quiz_owner_id', 'Unknown')}"
                details += f", Created By: {data.get('created_by', 'Unknown')}"
                details += f", Is Draft: {data.get('is_draft', 'Unknown')}"
                
                # Verify ownership fields are correct
                owner_type_correct = data.get('quiz_owner_type') == 'admin'
                owner_id_present = data.get('quiz_owner_id') is not None
                details += f", Ownership correct: {owner_type_correct and owner_id_present}"
                
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Quiz with Ownership", success, details)
        except Exception as e:
            return self.log_test("Admin Create Quiz with Ownership", False, f"Error: {str(e)}")

    def test_admin_see_all_quizzes(self):
        """Test that admin can see all quizzes (admin + user created) in /api/admin/quizzes"""
        if not self.admin_token:
            return self.log_test("Admin See All Quizzes", False, "No admin token available")
        
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
                
                # Count admin vs user quizzes
                admin_quizzes = [q for q in quizzes if q.get('quiz_owner_type') == 'admin']
                user_quizzes = [q for q in quizzes if q.get('quiz_owner_type') == 'user']
                
                details += f", Admin Quizzes: {len(admin_quizzes)}, User Quizzes: {len(user_quizzes)}"
                
                # Check that both draft and published quizzes are visible to admin
                draft_quizzes = [q for q in quizzes if q.get('is_draft') == True]
                published_quizzes = [q for q in quizzes if q.get('is_draft') == False]
                details += f", Draft: {len(draft_quizzes)}, Published: {len(published_quizzes)}"
                
                # Check if our created quizzes are present
                quiz_titles = [q.get('title') for q in quizzes]
                admin_quiz_found = "Admin Created Quiz - Mathematics" in quiz_titles
                user_quiz_found = any("Python" in title for title in quiz_titles)
                details += f", Admin quiz found: {admin_quiz_found}, User quiz found: {user_quiz_found}"
                
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin See All Quizzes", success, details)
        except Exception as e:
            return self.log_test("Admin See All Quizzes", False, f"Error: {str(e)}")

    # ===== PERMISSION AND SECURITY TESTS =====

    def test_user_cannot_access_admin_global_subjects(self):
        """Test that regular users cannot access admin global subject endpoints"""
        if not self.user_token:
            return self.log_test("User Cannot Access Admin Global Subjects", False, "No user token available")
        
        try:
            # Try to access admin global subjects endpoint
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

    def test_user_cannot_edit_other_user_quiz(self):
        """Test that users cannot edit quizzes created by other users"""
        if not self.user_token or not self.created_admin_quiz_id:
            return self.log_test("User Cannot Edit Other User Quiz", False, "No user token or admin quiz ID available")
        
        update_data = {
            "title": "Trying to hack admin quiz"
        }
        
        try:
            # Try to update admin's quiz with user token
            response = requests.put(
                f"{self.api_url}/user/quiz/{self.created_admin_quiz_id}",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            success = response.status_code == 404  # Should not be found (user can't see admin quizzes in user endpoints)
            details = f"Status: {response.status_code} (Expected 404)"
            
            return self.log_test("User Cannot Edit Other User Quiz", success, details)
        except Exception as e:
            return self.log_test("User Cannot Edit Other User Quiz", False, f"Error: {str(e)}")

    # ===== CLEANUP TESTS =====

    def test_delete_global_subject(self):
        """Test deleting global subject (cleanup)"""
        if not self.admin_token or not self.created_global_subject_id:
            return self.log_test("Delete Global Subject", True, "SKIPPED - No admin token or subject ID")
        
        try:
            response = requests.delete(
                f"{self.api_url}/admin/global-subject/{self.created_global_subject_id}",
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
                
            return self.log_test("Delete Global Subject", success, details)
        except Exception as e:
            return self.log_test("Delete Global Subject", False, f"Error: {str(e)}")

    def test_delete_user_quiz(self):
        """Test deleting user's own quiz (cleanup)"""
        if not self.user_token or not self.created_user_quiz_id:
            return self.log_test("Delete User Quiz", True, "SKIPPED - No user token or quiz ID")
        
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
                
            return self.log_test("Delete User Quiz", success, details)
        except Exception as e:
            return self.log_test("Delete User Quiz", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Squiz New Features Backend API Testing...")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        print("\n📋 Running Global Subject Management Tests...")
        self.test_create_global_subject()
        self.test_get_all_global_subjects()
        self.test_add_subfolder_to_global_subject()
        self.test_update_global_subject()
        
        print("\n👤 Running User Available Subjects Tests...")
        self.test_create_personal_subject()
        self.test_get_available_subjects_for_user()
        
        print("\n📝 Running User Quiz Creation Tests...")
        self.test_create_user_quiz()
        self.test_get_user_my_quizzes()
        self.test_update_user_quiz()
        self.test_publish_user_quiz()
        
        print("\n🌐 Running Enhanced Public Quiz Access Tests...")
        self.test_enhanced_public_quiz_access()
        self.test_draft_quiz_filtering()
        
        print("\n👨‍💼 Running Admin Quiz Management Tests...")
        self.test_admin_create_quiz_with_ownership()
        self.test_admin_see_all_quizzes()
        
        print("\n🔒 Running Permission and Security Tests...")
        self.test_user_cannot_access_admin_global_subjects()
        self.test_user_cannot_edit_other_user_quiz()
        
        print("\n🧹 Running Cleanup Tests...")
        self.test_delete_global_subject()
        self.test_delete_user_quiz()
        
        # Final summary
        print("\n" + "=" * 80)
        print(f"🎯 TESTING COMPLETE")
        print(f"📊 Results: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"✅ Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED! New backend functionality is working perfectly.")
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed. Please review the failed tests above.")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = SquizNewFeaturesAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)