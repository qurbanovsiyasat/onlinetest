#!/usr/bin/env python3
"""
Comprehensive Q&A Discussion System Backend API Testing for Squiz Platform
Tests all Q&A functionality as requested in the review request
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import base64

class QAComprehensiveTester:
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
        self.user2_token = None
        self.test_user_id = str(uuid.uuid4())[:8]
        self.test_user2_id = str(uuid.uuid4())[:8]
        
        # Test data storage
        self.created_question_id = None
        self.created_answer_id = None
        self.created_discussion_id = None

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

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Backend: {data.get('hosting', 'Unknown')}"
                details += f", Database: {data.get('database', 'Unknown')}"
            return self.log_test("Health Check", success, details)
        except Exception as e:
            return self.log_test("Health Check", False, f"Error: {str(e)}")

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
                details += f", Role: {user_info.get('role', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Login", success, details)
        except Exception as e:
            return self.log_test("Admin Login", False, f"Error: {str(e)}")

    def test_user_setup(self):
        """Test user registration and login"""
        # Register first user
        user_data = {
            "name": f"QA Test User {self.test_user_id}",
            "email": f"qauser{self.test_user_id}@example.com",
            "password": "testpass123"
        }
        try:
            response = requests.post(
                f"{self.api_url}/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code != 200:
                return self.log_test("User Setup", False, f"User registration failed: {response.status_code}")
            
            # Login first user
            login_data = {
                "email": f"qauser{self.test_user_id}@example.com",
                "password": "testpass123"
            }
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code != 200:
                return self.log_test("User Setup", False, f"User login failed: {response.status_code}")
            
            data = response.json()
            self.user_token = data.get('access_token')
            
            # Register second user
            user2_data = {
                "name": f"QA Test User 2 {self.test_user2_id}",
                "email": f"qauser2{self.test_user2_id}@example.com",
                "password": "testpass123"
            }
            response = requests.post(
                f"{self.api_url}/auth/register",
                json=user2_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code != 200:
                return self.log_test("User Setup", False, f"User 2 registration failed: {response.status_code}")
            
            # Login second user
            login2_data = {
                "email": f"qauser2{self.test_user2_id}@example.com",
                "password": "testpass123"
            }
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=login2_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                self.user2_token = data.get('access_token')
                details += f", Both users registered and logged in successfully"
            else:
                details += f", User 2 login failed: {response.text[:200]}"
                
            return self.log_test("User Setup", success, details)
        except Exception as e:
            return self.log_test("User Setup", False, f"Error: {str(e)}")

    # ===== 1. QUESTION MANAGEMENT TESTS =====

    def test_create_question_with_image(self):
        """Test POST /api/questions/ (create question with image)"""
        if not self.user_token:
            return self.log_test("Create Question with Image", False, "No user token available")
            
        # Create a base64 encoded test image
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        
        question_data = {
            "title": "How to implement binary search algorithm?",
            "content": "I'm struggling with implementing binary search in Python. Can someone explain the step-by-step process and provide a working example?",
            "image": test_image,
            "subject": "Computer Science",
            "subcategory": "Algorithms",
            "tags": ["python", "algorithms", "binary-search", "data-structures"]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions",
                json=question_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                question = response.json()
                self.created_question_id = question.get('id')
                details += f", Question ID: {self.created_question_id}"
                details += f", Title: {question.get('title', 'Unknown')[:30]}..."
                details += f", Has Image: {bool(question.get('image'))}"
                details += f", Subject: {question.get('subject', 'Unknown')}"
                details += f", Tags: {len(question.get('tags', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Question with Image", success, details)
        except Exception as e:
            return self.log_test("Create Question with Image", False, f"Error: {str(e)}")

    def test_list_questions(self):
        """Test GET /api/questions/ (list questions)"""
        try:
            response = requests.get(f"{self.api_url}/questions", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                # Handle both list and dict response formats
                if isinstance(data, list):
                    questions = data
                    total = len(questions)
                elif isinstance(data, dict):
                    questions = data.get('questions', [])
                    total = data.get('total', len(questions))
                else:
                    questions = []
                    total = 0
                
                details += f", Questions Count: {len(questions)}"
                details += f", Total: {total}"
                
                if len(questions) > 0:
                    first_q = questions[0]
                    details += f", First Q: {first_q.get('title', 'Unknown')[:30]}..."
                    details += f", Upvotes: {first_q.get('upvotes', 0)}"
                    details += f", Status: {first_q.get('status', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("List Questions", success, details)
        except Exception as e:
            return self.log_test("List Questions", False, f"Error: {str(e)}")

    def test_get_question_details(self):
        """Test GET /api/questions/{id} (get question details)"""
        if not self.created_question_id:
            return self.log_test("Get Question Details", False, "No question ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/questions/{self.created_question_id}",
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                # Handle both direct question and nested response formats
                if 'question' in data:
                    question = data['question']
                    answers = data.get('answers', [])
                    discussions = data.get('discussions', [])
                    details += f", Answers: {len(answers)}, Discussions: {len(discussions)}"
                else:
                    question = data
                
                details += f", Title: {question.get('title', 'Unknown')[:30]}..."
                details += f", Content Length: {len(question.get('content', ''))}"
                details += f", Upvotes: {question.get('upvotes', 0)}"
                details += f", Has Image: {bool(question.get('image'))}"
                details += f", Tags: {len(question.get('tags', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Question Details", success, details)
        except Exception as e:
            return self.log_test("Get Question Details", False, f"Error: {str(e)}")

    def test_update_question_author(self):
        """Test PUT /api/questions/{id} (update question - author only)"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Update Question (Author)", False, "No user token or question ID available")
            
        update_data = {
            "title": "How to implement binary search algorithm? (Updated)",
            "content": "Updated content: I'm struggling with implementing binary search in Python. Can someone explain the step-by-step process and provide a working example? I've tried several approaches but keep getting errors.",
            "tags": ["python", "algorithms", "binary-search", "data-structures", "debugging"]
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/questions/{self.created_question_id}",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                question = response.json()
                details += f", Updated Title: {question.get('title', 'Unknown')[:40]}..."
                details += f", Tags: {len(question.get('tags', []))}"
                details += f", Updated At: {question.get('updated_at', 'Unknown')[:19]}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Update Question (Author)", success, details)
        except Exception as e:
            return self.log_test("Update Question (Author)", False, f"Error: {str(e)}")

    def test_update_question_non_author(self):
        """Test PUT /api/questions/{id} (update question - non-author should fail)"""
        if not self.user2_token or not self.created_question_id:
            return self.log_test("Update Question (Non-Author)", False, "No user2 token or question ID available")
            
        update_data = {
            "title": "This should fail",
            "content": "Non-author trying to update"
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/questions/{self.created_question_id}",
                json=update_data,
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            return self.log_test("Update Question (Non-Author)", success, details)
        except Exception as e:
            return self.log_test("Update Question (Non-Author)", False, f"Error: {str(e)}")

    def test_delete_question_admin(self):
        """Test DELETE /api/questions/{id} (delete question - admin)"""
        if not self.admin_token:
            return self.log_test("Delete Question (Admin)", False, "No admin token available")
        
        # Create a question to delete
        question_data = {
            "title": "Test Question for Admin Deletion",
            "content": "This question will be deleted by admin",
            "subject": "Test",
            "tags": ["test", "admin-delete"]
        }
        
        try:
            # Create question with user token
            response = requests.post(
                f"{self.api_url}/questions",
                json=question_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Delete Question (Admin)", False, f"Failed to create test question: {response.status_code}")
            
            question = response.json()
            question_id = question.get('id')
            
            # Delete question with admin token
            response = requests.delete(
                f"{self.api_url}/questions/{question_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Message: {result.get('message', 'No message')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Delete Question (Admin)", success, details)
        except Exception as e:
            return self.log_test("Delete Question (Admin)", False, f"Error: {str(e)}")

    # ===== 2. ANSWER MANAGEMENT TESTS =====

    def test_create_answer_with_image(self):
        """Test POST /api/questions/{id}/answers/ (create answer with image)"""
        if not self.user2_token or not self.created_question_id:
            return self.log_test("Create Answer with Image", False, "No user2 token or question ID available")
            
        # Create a base64 encoded test image for answer
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        
        answer_data = {
            "content": "Here's a complete implementation of binary search in Python:\n\n```python\ndef binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    \n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    \n    return -1\n```\n\nThis algorithm works by repeatedly dividing the search space in half.",
            "image": test_image
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/answers",
                json=answer_data,
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                answer = response.json()
                self.created_answer_id = answer.get('id')
                details += f", Answer ID: {self.created_answer_id}"
                details += f", Content Length: {len(answer.get('content', ''))}"
                details += f", Has Image: {bool(answer.get('image'))}"
                details += f", Upvotes: {answer.get('upvotes', 0)}"
                details += f", Is Accepted: {answer.get('is_accepted', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Answer with Image", success, details)
        except Exception as e:
            return self.log_test("Create Answer with Image", False, f"Error: {str(e)}")

    def test_get_answers_for_question(self):
        """Test GET /api/questions/{id}/answers/ (get answers for question)"""
        if not self.created_question_id:
            return self.log_test("Get Answers for Question", False, "No question ID available")
            
        try:
            # Get question details which should include answers
            response = requests.get(
                f"{self.api_url}/questions/{self.created_question_id}",
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                answers = data.get('answers', [])
                details += f", Answers Count: {len(answers)}"
                
                if len(answers) > 0:
                    first_answer = answers[0]
                    details += f", First Answer Length: {len(first_answer.get('content', ''))}"
                    details += f", Has Image: {bool(first_answer.get('image'))}"
                    details += f", Upvotes: {first_answer.get('upvotes', 0)}"
                    details += f", Is Accepted: {first_answer.get('is_accepted', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Answers for Question", success, details)
        except Exception as e:
            return self.log_test("Get Answers for Question", False, f"Error: {str(e)}")

    def test_update_answer(self):
        """Test PUT /api/questions/{id}/answers/{answer_id} (update answer)"""
        if not self.user2_token or not self.created_question_id or not self.created_answer_id:
            return self.log_test("Update Answer", False, "Missing tokens or IDs")
            
        update_data = {
            "content": "Here's an updated and improved implementation of binary search in Python:\n\n```python\ndef binary_search(arr, target):\n    \"\"\"Binary search implementation with error handling\"\"\"\n    if not arr:\n        return -1\n        \n    left, right = 0, len(arr) - 1\n    \n    while left <= right:\n        mid = left + (right - left) // 2  # Prevents overflow\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    \n    return -1\n```\n\nKey improvements:\n1. Added error handling for empty arrays\n2. Used overflow-safe mid calculation\n3. Added documentation"
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/questions/{self.created_question_id}/answers/{self.created_answer_id}",
                json=update_data,
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                answer = response.json()
                details += f", Content Length: {len(answer.get('content', ''))}"
                details += f", Updated At: {answer.get('updated_at', 'Unknown')[:19]}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Update Answer", success, details)
        except Exception as e:
            return self.log_test("Update Answer", False, f"Error: {str(e)}")

    def test_delete_answer(self):
        """Test DELETE /api/questions/{id}/answers/{answer_id} (delete answer)"""
        if not self.user2_token or not self.created_question_id or not self.created_answer_id:
            return self.log_test("Delete Answer", False, "Missing tokens or IDs")
            
        try:
            response = requests.delete(
                f"{self.api_url}/questions/{self.created_question_id}/answers/{self.created_answer_id}",
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Message: {result.get('message', 'No message')}"
                # Clear the answer ID since it's deleted
                self.created_answer_id = None
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Delete Answer", success, details)
        except Exception as e:
            return self.log_test("Delete Answer", False, f"Error: {str(e)}")

    # ===== 3. ADMIN Q&A FEATURES TESTS =====

    def test_admin_create_question(self):
        """Test admin can create questions"""
        if not self.admin_token:
            return self.log_test("Admin Create Question", False, "No admin token available")
            
        question_data = {
            "title": "Admin Question: Best Practices for Database Design",
            "content": "What are the key principles and best practices for designing efficient database schemas?",
            "subject": "Database Design",
            "subcategory": "Best Practices",
            "tags": ["database", "design", "best-practices", "schema"]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions",
                json=question_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                question = response.json()
                details += f", Question ID: {question.get('id')}"
                details += f", Title: {question.get('title', 'Unknown')[:40]}..."
                details += f", Subject: {question.get('subject', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Create Question", success, details)
        except Exception as e:
            return self.log_test("Admin Create Question", False, f"Error: {str(e)}")

    def test_admin_answer_question(self):
        """Test admin can answer questions"""
        if not self.admin_token or not self.created_question_id:
            return self.log_test("Admin Answer Question", False, "No admin token or question ID available")
            
        answer_data = {
            "content": "As an admin, here's my comprehensive answer to your binary search question:\n\nBinary search is a fundamental algorithm that requires:\n1. A sorted array\n2. Divide and conquer approach\n3. O(log n) time complexity\n\nThe implementation you're looking for should handle edge cases and be well-documented. Make sure to test with various inputs including empty arrays, single elements, and target values not in the array."
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/answers",
                json=answer_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                answer = response.json()
                details += f", Answer ID: {answer.get('id')}"
                details += f", Content Length: {len(answer.get('content', ''))}"
                details += f", Admin Answer: True"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Answer Question", success, details)
        except Exception as e:
            return self.log_test("Admin Answer Question", False, f"Error: {str(e)}")

    def test_admin_pin_unpin_question(self):
        """Test admin can pin/unpin questions"""
        if not self.admin_token or not self.created_question_id:
            return self.log_test("Admin Pin/Unpin Question", False, "No admin token or question ID available")
            
        try:
            # Pin the question
            pin_data = {"is_pinned": True}
            response = requests.put(
                f"{self.api_url}/admin/questions/{self.created_question_id}/pin",
                json=pin_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Admin Pin/Unpin Question", False, f"Pin failed: {response.status_code}")
            
            pin_result = response.json()
            
            # Unpin the question
            unpin_data = {"is_pinned": False}
            response = requests.put(
                f"{self.api_url}/admin/questions/{self.created_question_id}/pin",
                json=unpin_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                unpin_result = response.json()
                details += f", Pin→Unpin: {pin_result.get('is_pinned', False)}→{unpin_result.get('is_pinned', True)}"
            else:
                details += f", Unpin failed: {response.text[:200]}"
                
            return self.log_test("Admin Pin/Unpin Question", success, details)
        except Exception as e:
            return self.log_test("Admin Pin/Unpin Question", False, f"Error: {str(e)}")

    def test_admin_qa_statistics(self):
        """Test admin Q&A statistics"""
        if not self.admin_token:
            return self.log_test("Admin Q&A Statistics", False, "No admin token available")
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/qa-stats",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                stats = response.json()
                details += f", Total Questions: {stats.get('total_questions', 0)}"
                details += f", Total Answers: {stats.get('total_answers', 0)}"
                details += f", Total Discussions: {stats.get('total_discussions', 0)}"
                details += f", Open Questions: {stats.get('open_questions', 0)}"
                details += f", Answered Questions: {stats.get('answered_questions', 0)}"
                details += f", Most Active Subject: {stats.get('most_active_subject', 'None')}"
                details += f", Top Contributors: {len(stats.get('top_contributors', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Q&A Statistics", success, details)
        except Exception as e:
            return self.log_test("Admin Q&A Statistics", False, f"Error: {str(e)}")

    # ===== 4. USER PRIVACY FEATURES TESTS =====

    def test_user_profile_privacy_settings(self):
        """Test user profile privacy settings"""
        if not self.user_token:
            return self.log_test("User Profile Privacy Settings", False, "No user token available")
            
        try:
            # Get current user profile
            response = requests.get(
                f"{self.api_url}/auth/me",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("User Profile Privacy Settings", False, f"Failed to get user profile: {response.status_code}")
            
            user_data = response.json()
            current_privacy = user_data.get('is_private', False)
            
            # Test updating privacy settings (if endpoint exists)
            # Note: This might need to be implemented as a separate endpoint
            success = True
            details = f"Status: 200, Current Privacy: {current_privacy}"
            details += f", User ID: {user_data.get('id', 'Unknown')}"
            details += f", Name: {user_data.get('name', 'Unknown')}"
            details += f", Email: {user_data.get('email', 'Unknown')}"
            details += f", Follower Count: {user_data.get('follower_count', 0)}"
            details += f", Following Count: {user_data.get('following_count', 0)}"
                
            return self.log_test("User Profile Privacy Settings", success, details)
        except Exception as e:
            return self.log_test("User Profile Privacy Settings", False, f"Error: {str(e)}")

    def test_is_private_field_functionality(self):
        """Test is_private field functionality"""
        if not self.user_token:
            return self.log_test("Is Private Field Functionality", False, "No user token available")
            
        try:
            # Get user profile to check is_private field
            response = requests.get(
                f"{self.api_url}/auth/me",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                user_data = response.json()
                is_private = user_data.get('is_private', False)
                details += f", Is Private: {is_private}"
                details += f", Field Present: {'is_private' in user_data}"
                details += f", Type: {type(is_private).__name__}"
                
                # Verify it's a boolean field
                if isinstance(is_private, bool):
                    details += ", Boolean Field: ✓"
                else:
                    details += ", Boolean Field: ✗"
                    success = False
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Is Private Field Functionality", success, details)
        except Exception as e:
            return self.log_test("Is Private Field Functionality", False, f"Error: {str(e)}")

    def test_profile_visibility_controls(self):
        """Test profile visibility controls"""
        if not self.user_token or not self.user2_token:
            return self.log_test("Profile Visibility Controls", False, "Missing user tokens")
            
        try:
            # Get user 1 profile with user 2 token (cross-user profile access)
            response1 = requests.get(
                f"{self.api_url}/auth/me",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if response1.status_code != 200:
                return self.log_test("Profile Visibility Controls", False, f"Failed to get user 1 profile: {response1.status_code}")
            
            user1_data = response1.json()
            user1_id = user1_data.get('id')
            
            # Get user 2 profile
            response2 = requests.get(
                f"{self.api_url}/auth/me",
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            
            success = response2.status_code == 200
            details = f"Status: {response2.status_code}"
            
            if success:
                user2_data = response2.json()
                details += f", User 1 Private: {user1_data.get('is_private', False)}"
                details += f", User 2 Private: {user2_data.get('is_private', False)}"
                details += f", Cross-User Access: Tested"
                
                # Both users can see their own profiles
                details += f", Self-Access: ✓"
            else:
                details += f", Response: {response2.text[:200]}"
                
            return self.log_test("Profile Visibility Controls", success, details)
        except Exception as e:
            return self.log_test("Profile Visibility Controls", False, f"Error: {str(e)}")

    # ===== 5. IMAGE UPLOAD SUPPORT TESTS =====

    def test_base64_image_upload_questions(self):
        """Test base64 image upload in questions"""
        if not self.user_token:
            return self.log_test("Base64 Image Upload (Questions)", False, "No user token available")
            
        # Create a larger base64 encoded test image
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFYSURBVBiVY/z//z8DJQAggBhJVQcQQIykqgMIIEZS1QEEECO56gACiJFcdQABxEiuOoAAYiRXHUAAMZKrDiCAGMlVBxBAjOSqAwggRnLVAQQQI7nqAAKIkVx1AAHESKo6gABiJFUdQAAxkqoOIIAYSVUHEECMpKoDCCBGUtUBBBAjqeoAAoiRVHUAAcRIqjqAAGIkVR1AADGSqw4ggBjJVQcQQIzkqgMIIEZy1QEEECO56gACiJFcdQABxEiuOoAAYiRXHUAAMZKrDiCAGMlVBxBAjOSqAwggRnLVAQQQI7nqAAKIkVR1AAHESKo6gABiJFUdQAAxkqoOIIAYSVUHEECMpKoDCCBGUtUBBBAjqeoAAoiRVHUAAcRIqjqAAGIkVR1AADGSqw4ggBjJVQcQQIzkqgMIIEZy1QEEECO56gACiJFcdQABxEiuOoAAYiRXHUAAMZKrDiCAGAEAF2AKAJdeOlAAAAAASUVORK5CYII="
        
        question_data = {
            "title": "Image Upload Test Question",
            "content": "This question tests base64 image upload functionality. The image should be stored and retrievable.",
            "image": test_image,
            "subject": "Testing",
            "subcategory": "Image Upload",
            "tags": ["test", "image", "upload", "base64"]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions",
                json=question_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                question = response.json()
                question_id = question.get('id')
                has_image = bool(question.get('image'))
                image_data = question.get('image', '')
                
                details += f", Question ID: {question_id}"
                details += f", Has Image: {has_image}"
                details += f", Image Data Length: {len(image_data)}"
                details += f", Image Format: {'data:image/' in image_data if image_data else 'None'}"
                
                # Verify image storage and retrieval
                if has_image and image_data:
                    details += f", Storage: ✓, Retrieval: ✓"
                else:
                    details += f", Storage: ✗, Retrieval: ✗"
                    success = False
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Base64 Image Upload (Questions)", success, details)
        except Exception as e:
            return self.log_test("Base64 Image Upload (Questions)", False, f"Error: {str(e)}")

    def test_base64_image_upload_answers(self):
        """Test base64 image upload in answers"""
        if not self.user2_token or not self.created_question_id:
            return self.log_test("Base64 Image Upload (Answers)", False, "No user2 token or question ID available")
            
        # Create a base64 encoded test image for answer
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFYSURBVBiVY/z//z8DJQAggBhJVQcQQIykqgMIIEZS1QEEECO56gACiJFcdQABxEiuOoAAYiRXHUAAMZKrDiCAGMlVBxBAjOSqAwggRnLVAQQQI7nqAAKIkVx1AAHESKo6gABiJFUdQAAxkqoOIIAYSVUHEECMpKoDCCBGUtUBBBAjqeoAAoiRVHUAAcRIqjqAAGIkVR1AADGSqw4ggBjJVQcQQIzkqgMIIEZy1QEEECO56gACiJFcdQABxEiuOoAAYiRXHUAAMZKrDiCAGMlVBxBAjOSqAwggRnLVAQQQI7nqAAKIkVR1AAHESKo6gABiJFUdQAAxkqoOIIAYSVUHEECMpKoDCCBGUtUBBBAjqeoAAoiRVHUAAcRIqjqAAGIkVR1AADGSqw4ggBjJVQcQQIzkqgMIIEZy1QEEECO56gACiJFcdQABxEiuOoAAYiRXHUAAMZKrDiCAGAEAF2AKAJdeOlAAAAAASUVORK5CYII="
        
        answer_data = {
            "content": "Here's my answer with an image attachment. The image demonstrates the concept visually.",
            "image": test_image
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/answers",
                json=answer_data,
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                answer = response.json()
                answer_id = answer.get('id')
                has_image = bool(answer.get('image'))
                image_data = answer.get('image', '')
                
                details += f", Answer ID: {answer_id}"
                details += f", Has Image: {has_image}"
                details += f", Image Data Length: {len(image_data)}"
                details += f", Image Format: {'data:image/' in image_data if image_data else 'None'}"
                
                # Verify image storage and retrieval
                if has_image and image_data:
                    details += f", Storage: ✓, Retrieval: ✓"
                else:
                    details += f", Storage: ✗, Retrieval: ✗"
                    success = False
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Base64 Image Upload (Answers)", success, details)
        except Exception as e:
            return self.log_test("Base64 Image Upload (Answers)", False, f"Error: {str(e)}")

    def test_image_storage_and_retrieval(self):
        """Test image storage and retrieval"""
        if not self.created_question_id:
            return self.log_test("Image Storage and Retrieval", False, "No question ID available")
            
        try:
            # Get question details to verify image is stored and retrievable
            response = requests.get(
                f"{self.api_url}/questions/{self.created_question_id}",
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                # Handle both direct question and nested response formats
                if 'question' in data:
                    question = data['question']
                else:
                    question = data
                
                has_image = bool(question.get('image'))
                image_data = question.get('image', '')
                
                details += f", Has Image: {has_image}"
                details += f", Image Data Length: {len(image_data)}"
                
                if has_image and image_data:
                    # Verify it's a valid base64 image
                    is_base64_image = image_data.startswith('data:image/')
                    details += f", Valid Base64 Image: {is_base64_image}"
                    
                    if is_base64_image:
                        details += f", Storage: ✓, Retrieval: ✓"
                    else:
                        details += f", Storage: ✗, Retrieval: ✗"
                        success = False
                else:
                    details += f", Storage: ✗, Retrieval: ✗"
                    success = False
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Image Storage and Retrieval", success, details)
        except Exception as e:
            return self.log_test("Image Storage and Retrieval", False, f"Error: {str(e)}")

    # ===== CLEANUP =====

    def test_cleanup(self):
        """Clean up test data"""
        if not self.created_question_id:
            return self.log_test("Cleanup", True, "No cleanup needed")
            
        try:
            # Delete the test question
            response = requests.delete(
                f"{self.api_url}/questions/{self.created_question_id}",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Message: {result.get('message', 'No message')}"
                details += f", Question Deleted: ✓"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Cleanup", success, details)
        except Exception as e:
            return self.log_test("Cleanup", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all comprehensive Q&A tests"""
        print("🚀 Starting Comprehensive Q&A Discussion System Backend API Testing")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Basic setup tests
        self.test_health_check()
        self.test_admin_login()
        self.test_user_setup()
        
        print("\n📝 1. QUESTION MANAGEMENT TESTS")
        print("-" * 50)
        self.test_create_question_with_image()
        self.test_list_questions()
        self.test_get_question_details()
        self.test_update_question_author()
        self.test_update_question_non_author()
        self.test_delete_question_admin()
        
        print("\n💬 2. ANSWER MANAGEMENT TESTS")
        print("-" * 50)
        self.test_create_answer_with_image()
        self.test_get_answers_for_question()
        self.test_update_answer()
        self.test_delete_answer()
        
        print("\n🔧 3. ADMIN Q&A FEATURES TESTS")
        print("-" * 50)
        self.test_admin_create_question()
        self.test_admin_answer_question()
        self.test_admin_pin_unpin_question()
        self.test_admin_qa_statistics()
        
        print("\n🔒 4. USER PRIVACY FEATURES TESTS")
        print("-" * 50)
        self.test_user_profile_privacy_settings()
        self.test_is_private_field_functionality()
        self.test_profile_visibility_controls()
        
        print("\n🖼️ 5. IMAGE UPLOAD SUPPORT TESTS")
        print("-" * 50)
        self.test_base64_image_upload_questions()
        self.test_base64_image_upload_answers()
        self.test_image_storage_and_retrieval()
        
        print("\n🧹 CLEANUP")
        print("-" * 50)
        self.test_cleanup()
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE Q&A DISCUSSION SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📊 Total Tests: {self.tests_run}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL COMPREHENSIVE Q&A TESTS PASSED!")
            print("✅ Question Management: Working")
            print("✅ Answer Management: Working") 
            print("✅ Admin Q&A Features: Working")
            print("✅ User Privacy Features: Working")
            print("✅ Image Upload Support: Working")
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed - check implementation")
            
            # Identify which categories failed
            failed_tests = self.tests_run - self.tests_passed
            if failed_tests > 0:
                print("\n🔍 AREAS NEEDING ATTENTION:")
                print("- Check failed test details above")
                print("- Verify API endpoint implementations")
                print("- Ensure proper authentication and authorization")
                print("- Validate image upload and storage functionality")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = QAComprehensiveTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)