#!/usr/bin/env python3
"""
Q&A Discussion System Backend API Testing for Squiz Platform
Tests all the NEW Q&A functionality that was just implemented
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import base64

class QADiscussionSystemTester:
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
        
        # Q&A specific test data
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

    def test_user_registration(self):
        """Test user registration"""
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
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", User: {data.get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Registration", success, details)
        except Exception as e:
            return self.log_test("User Registration", False, f"Error: {str(e)}")

    def test_user_login(self):
        """Test user login"""
        login_data = {
            "email": f"qauser{self.test_user_id}@example.com",
            "password": "testpass123"
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
                self.user_token = data.get('access_token')
                user_info = data.get('user', {})
                details += f", Role: {user_info.get('role', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User Login", success, details)
        except Exception as e:
            return self.log_test("User Login", False, f"Error: {str(e)}")

    def test_user2_registration_and_login(self):
        """Test second user registration and login for voting tests"""
        # Register second user
        user_data = {
            "name": f"QA Test User 2 {self.test_user2_id}",
            "email": f"qauser2{self.test_user2_id}@example.com",
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
                return self.log_test("User 2 Registration & Login", False, f"Registration failed: {response.status_code}")
            
            # Login second user
            login_data = {
                "email": f"qauser2{self.test_user2_id}@example.com",
                "password": "testpass123"
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
                self.user2_token = data.get('access_token')
                details += f", User 2 logged in successfully"
            else:
                details += f", Login failed: {response.text[:200]}"
                
            return self.log_test("User 2 Registration & Login", success, details)
        except Exception as e:
            return self.log_test("User 2 Registration & Login", False, f"Error: {str(e)}")

    # ===== QUESTIONS MANAGEMENT TESTS =====

    def test_create_question_authenticated(self):
        """Test creating a question (authenticated users only)"""
        if not self.user_token:
            return self.log_test("Create Question (Authenticated)", False, "No user token available")
            
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
                details += f", Tags: {len(question.get('tags', []))}"
                details += f", Subject: {question.get('subject', 'Unknown')}"
                details += f", Status: {question.get('status', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Question (Authenticated)", success, details)
        except Exception as e:
            return self.log_test("Create Question (Authenticated)", False, f"Error: {str(e)}")

    def test_create_question_unauthenticated(self):
        """Test creating a question without authentication (should fail)"""
        question_data = {
            "title": "Test Question",
            "content": "This should fail",
            "subject": "Test",
            "tags": ["test"]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions",
                json=question_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 401  # Should be unauthorized
            details = f"Status: {response.status_code} (Expected 401)"
            return self.log_test("Create Question (Unauthenticated)", success, details)
        except Exception as e:
            return self.log_test("Create Question (Unauthenticated)", False, f"Error: {str(e)}")

    def test_get_questions_list(self):
        """Test getting list of questions with filtering"""
        try:
            # Test basic list
            response = requests.get(f"{self.api_url}/questions", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                questions = response.json()
                details += f", Questions Count: {len(questions)}"
                if len(questions) > 0:
                    first_q = questions[0]
                    details += f", First Q: {first_q.get('title', 'Unknown')[:30]}..."
                    details += f", Upvotes: {first_q.get('upvotes', 0)}"
                    details += f", Status: {first_q.get('status', 'Unknown')}"
                
                # Test filtering by subject
                if len(questions) > 0:
                    subject_filter_response = requests.get(
                        f"{self.api_url}/questions?subject=Computer Science", 
                        timeout=10
                    )
                    if subject_filter_response.status_code == 200:
                        filtered_questions = subject_filter_response.json()
                        details += f", Filtered by Subject: {len(filtered_questions)}"
                
                # Test filtering by status
                status_filter_response = requests.get(
                    f"{self.api_url}/questions?status=open", 
                    timeout=10
                )
                if status_filter_response.status_code == 200:
                    status_filtered = status_filter_response.json()
                    details += f", Filtered by Status: {len(status_filtered)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Questions List", success, details)
        except Exception as e:
            return self.log_test("Get Questions List", False, f"Error: {str(e)}")

    def test_get_question_detail(self):
        """Test getting question detail with answers and discussions"""
        if not self.created_question_id:
            return self.log_test("Get Question Detail", False, "No question ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/questions/{self.created_question_id}",
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                question = response.json()
                details += f", Title: {question.get('title', 'Unknown')[:30]}..."
                details += f", Content Length: {len(question.get('content', ''))}"
                details += f", Upvotes: {question.get('upvotes', 0)}"
                details += f", Downvotes: {question.get('downvotes', 0)}"
                details += f", Answer Count: {question.get('answer_count', 0)}"
                details += f", Has Image: {bool(question.get('image'))}"
                details += f", Tags: {len(question.get('tags', []))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Question Detail", success, details)
        except Exception as e:
            return self.log_test("Get Question Detail", False, f"Error: {str(e)}")

    def test_update_question_author(self):
        """Test updating question (author only)"""
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
        """Test updating question by non-author (should fail)"""
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

    # ===== ANSWERS MANAGEMENT TESTS =====

    def test_add_answer_to_question(self):
        """Test adding answer to question"""
        if not self.user2_token or not self.created_question_id:
            return self.log_test("Add Answer to Question", False, "No user2 token or question ID available")
            
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
                
            return self.log_test("Add Answer to Question", success, details)
        except Exception as e:
            return self.log_test("Add Answer to Question", False, f"Error: {str(e)}")

    def test_update_answer_accept(self):
        """Test updating answer (including accept/unaccept)"""
        if not self.user_token or not self.created_question_id or not self.created_answer_id:
            return self.log_test("Update Answer (Accept)", False, "Missing tokens or IDs")
            
        # Question author accepts the answer
        update_data = {
            "is_accepted": True
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/questions/{self.created_question_id}/answers/{self.created_answer_id}",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                answer = response.json()
                details += f", Is Accepted: {answer.get('is_accepted', False)}"
                details += f", Updated At: {answer.get('updated_at', 'Unknown')[:19]}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Update Answer (Accept)", success, details)
        except Exception as e:
            return self.log_test("Update Answer (Accept)", False, f"Error: {str(e)}")

    def test_update_answer_content(self):
        """Test updating answer content by answer author"""
        if not self.user2_token or not self.created_question_id or not self.created_answer_id:
            return self.log_test("Update Answer Content", False, "Missing tokens or IDs")
            
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
                
            return self.log_test("Update Answer Content", success, details)
        except Exception as e:
            return self.log_test("Update Answer Content", False, f"Error: {str(e)}")

    # ===== DISCUSSIONS MANAGEMENT TESTS =====

    def test_get_question_discussions(self):
        """Test getting discussion messages for a question"""
        if not self.created_question_id:
            return self.log_test("Get Question Discussions", False, "No question ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/questions/{self.created_question_id}/discussions",
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                discussions = response.json()
                details += f", Discussions Count: {len(discussions)}"
                if len(discussions) > 0:
                    first_discussion = discussions[0]
                    details += f", First Message: {first_discussion.get('message', 'Unknown')[:30]}..."
                    details += f", Upvotes: {first_discussion.get('upvotes', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Question Discussions", success, details)
        except Exception as e:
            return self.log_test("Get Question Discussions", False, f"Error: {str(e)}")

    def test_add_discussion_message(self):
        """Test adding discussion message"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Add Discussion Message", False, "No user token or question ID available")
            
        discussion_data = {
            "message": "Great question! I had the same issue when I was learning algorithms. The key insight is understanding how the search space gets divided in half with each iteration.",
            "image": None,
            "reply_to_id": None
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/discussions",
                json=discussion_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                discussion = response.json()
                self.created_discussion_id = discussion.get('id')
                details += f", Discussion ID: {self.created_discussion_id}"
                details += f", Message Length: {len(discussion.get('message', ''))}"
                details += f", Upvotes: {discussion.get('upvotes', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Add Discussion Message", success, details)
        except Exception as e:
            return self.log_test("Add Discussion Message", False, f"Error: {str(e)}")

    def test_add_threaded_discussion_reply(self):
        """Test adding threaded discussion reply"""
        if not self.user2_token or not self.created_question_id or not self.created_discussion_id:
            return self.log_test("Add Threaded Discussion Reply", False, "Missing tokens or IDs")
            
        reply_data = {
            "message": "Exactly! And don't forget that the array needs to be sorted for binary search to work correctly. That's a common mistake beginners make.",
            "reply_to_id": self.created_discussion_id
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/discussions",
                json=reply_data,
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                reply = response.json()
                details += f", Reply ID: {reply.get('id')}"
                details += f", Reply To: {reply.get('reply_to_id')}"
                details += f", Message Length: {len(reply.get('message', ''))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Add Threaded Discussion Reply", success, details)
        except Exception as e:
            return self.log_test("Add Threaded Discussion Reply", False, f"Error: {str(e)}")

    def test_update_discussion(self):
        """Test updating discussion message"""
        if not self.user_token or not self.created_question_id or not self.created_discussion_id:
            return self.log_test("Update Discussion", False, "Missing tokens or IDs")
            
        update_data = {
            "message": "Great question! I had the same issue when I was learning algorithms. The key insight is understanding how the search space gets divided in half with each iteration. Also, make sure your array is sorted first!"
        }
        
        try:
            response = requests.put(
                f"{self.api_url}/questions/{self.created_question_id}/discussions/{self.created_discussion_id}",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                discussion = response.json()
                details += f", Updated Message Length: {len(discussion.get('message', ''))}"
                details += f", Updated At: {discussion.get('updated_at', 'Unknown')[:19]}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Update Discussion", success, details)
        except Exception as e:
            return self.log_test("Update Discussion", False, f"Error: {str(e)}")

    # ===== VOTING SYSTEM TESTS =====

    def test_vote_on_question(self):
        """Test voting on questions (upvote/downvote/remove)"""
        if not self.user2_token or not self.created_question_id:
            return self.log_test("Vote on Question", False, "No user2 token or question ID available")
            
        try:
            # Test upvote
            vote_data = {"vote_type": "upvote"}
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/vote",
                json=vote_data,
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Vote on Question", False, f"Upvote failed: {response.status_code}")
            
            upvote_result = response.json()
            
            # Test changing to downvote
            vote_data = {"vote_type": "downvote"}
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/vote",
                json=vote_data,
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("Vote on Question", False, f"Downvote failed: {response.status_code}")
            
            downvote_result = response.json()
            
            # Test removing vote
            vote_data = {"vote_type": "remove"}
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/vote",
                json=vote_data,
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                remove_result = response.json()
                details += f", Final Upvotes: {remove_result.get('upvotes', 0)}"
                details += f", Final Downvotes: {remove_result.get('downvotes', 0)}"
                details += f", Vote Changes: Upvote→Downvote→Remove"
            else:
                details += f", Remove vote failed: {response.text[:200]}"
                
            return self.log_test("Vote on Question", success, details)
        except Exception as e:
            return self.log_test("Vote on Question", False, f"Error: {str(e)}")

    def test_vote_on_answer(self):
        """Test voting on answers"""
        if not self.user_token or not self.created_answer_id:
            return self.log_test("Vote on Answer", False, "No user token or answer ID available")
            
        try:
            # Test upvote on answer
            vote_data = {"vote_type": "upvote"}
            response = requests.post(
                f"{self.api_url}/answers/{self.created_answer_id}/vote",
                json=vote_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Upvotes: {result.get('upvotes', 0)}"
                details += f", Downvotes: {result.get('downvotes', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Vote on Answer", success, details)
        except Exception as e:
            return self.log_test("Vote on Answer", False, f"Error: {str(e)}")

    def test_vote_on_discussion(self):
        """Test voting on discussion messages"""
        if not self.user2_token or not self.created_discussion_id:
            return self.log_test("Vote on Discussion", False, "No user2 token or discussion ID available")
            
        try:
            # Test upvote on discussion
            vote_data = {"vote_type": "upvote"}
            response = requests.post(
                f"{self.api_url}/discussions/{self.created_discussion_id}/vote",
                json=vote_data,
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Upvotes: {result.get('upvotes', 0)}"
                details += f", Downvotes: {result.get('downvotes', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Vote on Discussion", success, details)
        except Exception as e:
            return self.log_test("Vote on Discussion", False, f"Error: {str(e)}")

    def test_prevent_self_voting(self):
        """Test that users cannot vote on their own content"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Prevent Self-Voting", False, "No user token or question ID available")
            
        try:
            # User tries to vote on their own question (should fail)
            vote_data = {"vote_type": "upvote"}
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/vote",
                json=vote_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 400  # Should be bad request
            details = f"Status: {response.status_code} (Expected 400)"
            
            if success:
                details += ", Self-voting correctly prevented"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Prevent Self-Voting", success, details)
        except Exception as e:
            return self.log_test("Prevent Self-Voting", False, f"Error: {str(e)}")

    # ===== ADMIN MANAGEMENT TESTS =====

    def test_admin_qa_stats(self):
        """Test admin getting Q&A system statistics"""
        if not self.admin_token:
            return self.log_test("Admin Q&A Stats", False, "No admin token available")
            
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
                
            return self.log_test("Admin Q&A Stats", success, details)
        except Exception as e:
            return self.log_test("Admin Q&A Stats", False, f"Error: {str(e)}")

    def test_admin_pin_question(self):
        """Test admin pinning/unpinning questions"""
        if not self.admin_token or not self.created_question_id:
            return self.log_test("Admin Pin Question", False, "No admin token or question ID available")
            
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
                return self.log_test("Admin Pin Question", False, f"Pin failed: {response.status_code}")
            
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
                
            return self.log_test("Admin Pin Question", success, details)
        except Exception as e:
            return self.log_test("Admin Pin Question", False, f"Error: {str(e)}")

    def test_non_admin_pin_question(self):
        """Test non-admin trying to pin question (should fail)"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Non-Admin Pin Question", False, "No user token or question ID available")
            
        try:
            pin_data = {"is_pinned": True}
            response = requests.put(
                f"{self.api_url}/admin/questions/{self.created_question_id}/pin",
                json=pin_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403)"
            return self.log_test("Non-Admin Pin Question", success, details)
        except Exception as e:
            return self.log_test("Non-Admin Pin Question", False, f"Error: {str(e)}")

    # ===== UTILITY ENDPOINTS TESTS =====

    def test_subjects_available(self):
        """Test getting available subjects from both quizzes and questions"""
        try:
            response = requests.get(f"{self.api_url}/subjects-available", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                subjects = response.json()
                details += f", Total Subjects: {len(subjects)}"
                if len(subjects) > 0:
                    details += f", First Subject: {subjects[0]}"
                    # Check if our test subject is included
                    if "Computer Science" in subjects:
                        details += ", Test Subject Found"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Subjects Available", success, details)
        except Exception as e:
            return self.log_test("Subjects Available", False, f"Error: {str(e)}")

    # ===== CLEANUP AND DELETION TESTS =====

    def test_delete_discussion(self):
        """Test deleting discussion message"""
        if not self.user_token or not self.created_question_id or not self.created_discussion_id:
            return self.log_test("Delete Discussion", False, "Missing tokens or IDs")
            
        try:
            response = requests.delete(
                f"{self.api_url}/questions/{self.created_question_id}/discussions/{self.created_discussion_id}",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                details += f", Message: {result.get('message', 'No message')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Delete Discussion", success, details)
        except Exception as e:
            return self.log_test("Delete Discussion", False, f"Error: {str(e)}")

    def test_delete_answer(self):
        """Test deleting answer"""
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
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Delete Answer", success, details)
        except Exception as e:
            return self.log_test("Delete Answer", False, f"Error: {str(e)}")

    def test_delete_question(self):
        """Test deleting question (author or admin only)"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Delete Question", False, "No user token or question ID available")
            
        try:
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
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Delete Question", success, details)
        except Exception as e:
            return self.log_test("Delete Question", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all Q&A Discussion System tests"""
        print("🚀 Starting Q&A Discussion System Backend API Testing")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Basic setup tests
        self.test_health_check()
        self.test_admin_login()
        self.test_user_registration()
        self.test_user_login()
        self.test_user2_registration_and_login()
        
        print("\n📝 QUESTIONS MANAGEMENT TESTS")
        print("-" * 40)
        self.test_create_question_authenticated()
        self.test_create_question_unauthenticated()
        self.test_get_questions_list()
        self.test_get_question_detail()
        self.test_update_question_author()
        self.test_update_question_non_author()
        
        print("\n💬 ANSWERS MANAGEMENT TESTS")
        print("-" * 40)
        self.test_add_answer_to_question()
        self.test_update_answer_accept()
        self.test_update_answer_content()
        
        print("\n🗨️ DISCUSSIONS MANAGEMENT TESTS")
        print("-" * 40)
        self.test_get_question_discussions()
        self.test_add_discussion_message()
        self.test_add_threaded_discussion_reply()
        self.test_update_discussion()
        
        print("\n👍 VOTING SYSTEM TESTS")
        print("-" * 40)
        self.test_vote_on_question()
        self.test_vote_on_answer()
        self.test_vote_on_discussion()
        self.test_prevent_self_voting()
        
        print("\n🔧 ADMIN MANAGEMENT TESTS")
        print("-" * 40)
        self.test_admin_qa_stats()
        self.test_admin_pin_question()
        self.test_non_admin_pin_question()
        
        print("\n🔍 UTILITY ENDPOINTS TESTS")
        print("-" * 40)
        self.test_subjects_available()
        
        print("\n🗑️ CLEANUP AND DELETION TESTS")
        print("-" * 40)
        self.test_delete_discussion()
        self.test_delete_answer()
        self.test_delete_question()
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎯 Q&A DISCUSSION SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📊 Total Tests: {self.tests_run}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL Q&A DISCUSSION SYSTEM TESTS PASSED!")
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed - check implementation")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = QADiscussionSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)