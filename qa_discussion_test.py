#!/usr/bin/env python3
"""
Q&A Discussion System Backend API Testing
Tests all Q&A functionality including questions, answers, discussions, voting, and admin features
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import base64

class QADiscussionAPITester:
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
        
        # Q&A specific IDs
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
                details += f", Role: {user_info.get('role', 'Unknown')}, Name: {user_info.get('name', 'Unknown')}"
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
                details += f", User: {data.get('name', 'Unknown')}, Role: {data.get('role', 'Unknown')}"
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
                details += f", Role: {user_info.get('role', 'Unknown')}, Name: {user_info.get('name', 'Unknown')}"
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
                user_info = data.get('user', {})
                details += f", User 2: {user_info.get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("User 2 Registration & Login", success, details)
        except Exception as e:
            return self.log_test("User 2 Registration & Login", False, f"Error: {str(e)}")

    def test_create_question(self):
        """Test creating a question with image"""
        if not self.user_token:
            return self.log_test("Create Question", False, "No user token available")
        
        # Create a simple base64 image
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        
        question_data = {
            "title": "How to implement binary search algorithm?",
            "content": "I'm struggling with implementing binary search in Python. Can someone explain the algorithm step by step with an example?",
            "image": image_data,
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
                data = response.json()
                self.created_question_id = data.get('id')
                details += f", Question ID: {self.created_question_id}"
                details += f", Title: {data.get('title', 'Unknown')[:30]}..."
                details += f", Subject: {data.get('subject', 'Unknown')}"
                details += f", Tags: {len(data.get('tags', []))}"
                details += f", Has Image: {bool(data.get('image'))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Create Question", success, details)
        except Exception as e:
            return self.log_test("Create Question", False, f"Error: {str(e)}")

    def test_get_questions_list(self):
        """Test getting questions list with filtering"""
        if not self.user_token:
            return self.log_test("Get Questions List", False, "No user token available")
        
        try:
            # Test basic questions list
            response = requests.get(
                f"{self.api_url}/questions",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Questions Count: {len(data)}"
                if len(data) > 0:
                    first_question = data[0]
                    details += f", First Q: {first_question.get('title', 'Unknown')[:20]}..."
                    details += f", Upvotes: {first_question.get('upvotes', 0)}"
                    details += f", Status: {first_question.get('status', 'Unknown')}"
                
                # Test filtering by subject
                filter_response = requests.get(
                    f"{self.api_url}/questions?subject=Computer Science",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                if filter_response.status_code == 200:
                    filtered_data = filter_response.json()
                    details += f", Filtered Count: {len(filtered_data)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Questions List", success, details)
        except Exception as e:
            return self.log_test("Get Questions List", False, f"Error: {str(e)}")

    def test_get_question_details(self):
        """Test getting specific question details"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Get Question Details", False, "No user token or question ID available")
        
        try:
            response = requests.get(
                f"{self.api_url}/questions/{self.created_question_id}",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Title: {data.get('title', 'Unknown')[:30]}..."
                details += f", Content Length: {len(data.get('content', ''))}"
                details += f", Answer Count: {data.get('answer_count', 0)}"
                details += f", Has Accepted Answer: {data.get('has_accepted_answer', False)}"
                details += f", Is Pinned: {data.get('is_pinned', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Question Details", success, details)
        except Exception as e:
            return self.log_test("Get Question Details", False, f"Error: {str(e)}")

    def test_update_question(self):
        """Test updating question (author only)"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Update Question", False, "No user token or question ID available")
        
        update_data = {
            "title": "How to implement binary search algorithm? (Updated)",
            "content": "I'm struggling with implementing binary search in Python. Can someone explain the algorithm step by step with an example? I've tried basic approaches but need optimization tips.",
            "tags": ["python", "algorithms", "binary-search", "data-structures", "optimization"]
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
                data = response.json()
                details += f", Updated Title: {data.get('title', 'Unknown')[-10:]}"
                details += f", Tags Count: {len(data.get('tags', []))}"
                details += f", Updated At: {data.get('updated_at', 'Unknown')[:19]}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Update Question", success, details)
        except Exception as e:
            return self.log_test("Update Question", False, f"Error: {str(e)}")

    def test_add_answer(self):
        """Test adding answer to question"""
        if not self.user2_token or not self.created_question_id:
            return self.log_test("Add Answer", False, "No user2 token or question ID available")
        
        # Create a simple base64 image for answer
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        
        answer_data = {
            "content": "Here's a step-by-step implementation of binary search in Python:\n\n```python\ndef binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    \n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    \n    return -1\n```\n\nThe key is to maintain sorted array and divide search space in half each iteration.",
            "image": image_data
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
                data = response.json()
                self.created_answer_id = data.get('id')
                details += f", Answer ID: {self.created_answer_id}"
                details += f", Content Length: {len(data.get('content', ''))}"
                details += f", Has Image: {bool(data.get('image'))}"
                details += f", Is Accepted: {data.get('is_accepted', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Add Answer", success, details)
        except Exception as e:
            return self.log_test("Add Answer", False, f"Error: {str(e)}")

    def test_get_question_answers(self):
        """Test getting answers for a question (via question details endpoint)"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Get Question Answers", False, "No user token or question ID available")
        
        try:
            # Get question details which includes answers
            response = requests.get(
                f"{self.api_url}/questions/{self.created_question_id}",
                headers=self.get_auth_headers(self.user_token),
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
                    details += f", Upvotes: {first_answer.get('upvotes', 0)}"
                    details += f", Is Accepted: {first_answer.get('is_accepted', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Question Answers", success, details)
        except Exception as e:
            return self.log_test("Get Question Answers", False, f"Error: {str(e)}")

    def test_accept_answer(self):
        """Test accepting answer (question author only) via PUT endpoint"""
        if not self.user_token or not self.created_answer_id or not self.created_question_id:
            return self.log_test("Accept Answer", False, "No user token, answer ID, or question ID available")
        
        try:
            # Accept answer via PUT endpoint
            update_data = {"is_accepted": True}
            response = requests.put(
                f"{self.api_url}/questions/{self.created_question_id}/answers/{self.created_answer_id}",
                json=update_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Is Accepted: {data.get('is_accepted', False)}"
                details += f", Answer ID: {data.get('id', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Accept Answer", success, details)
        except Exception as e:
            return self.log_test("Accept Answer", False, f"Error: {str(e)}")

    def test_add_discussion(self):
        """Test adding discussion message to question"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Add Discussion", False, "No user token or question ID available")
        
        discussion_data = {
            "message": "Great question! I had the same issue when learning algorithms. The binary search approach is very efficient with O(log n) complexity.",
            "reply_to_id": None  # Top-level discussion
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
                data = response.json()
                self.created_discussion_id = data.get('id')
                details += f", Discussion ID: {self.created_discussion_id}"
                details += f", Message Length: {len(data.get('message', ''))}"
                details += f", Reply To: {data.get('reply_to_id', 'None')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Add Discussion", success, details)
        except Exception as e:
            return self.log_test("Add Discussion", False, f"Error: {str(e)}")

    def test_add_threaded_discussion(self):
        """Test adding threaded reply to discussion"""
        if not self.user2_token or not self.created_question_id or not self.created_discussion_id:
            return self.log_test("Add Threaded Discussion", False, "Missing tokens or IDs")
        
        discussion_data = {
            "message": "I agree! Binary search is fundamental. Here's a tip: always remember the array must be sorted first.",
            "reply_to_id": self.created_discussion_id  # Reply to previous discussion
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/discussions",
                json=discussion_data,
                headers=self.get_auth_headers(self.user2_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Reply ID: {data.get('id')}"
                details += f", Reply To: {data.get('reply_to_id', 'None')}"
                details += f", Message: {data.get('message', '')[:30]}..."
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Add Threaded Discussion", success, details)
        except Exception as e:
            return self.log_test("Add Threaded Discussion", False, f"Error: {str(e)}")

    def test_get_question_discussions(self):
        """Test getting discussions for a question"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Get Question Discussions", False, "No user token or question ID available")
        
        try:
            response = requests.get(
                f"{self.api_url}/questions/{self.created_question_id}/discussions",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Discussions Count: {len(data)}"
                if len(data) > 0:
                    # Count top-level vs replies
                    top_level = sum(1 for d in data if not d.get('reply_to_id'))
                    replies = sum(1 for d in data if d.get('reply_to_id'))
                    details += f", Top-level: {top_level}, Replies: {replies}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Get Question Discussions", success, details)
        except Exception as e:
            return self.log_test("Get Question Discussions", False, f"Error: {str(e)}")

    def test_vote_on_question(self):
        """Test voting on question (upvote/downvote/remove)"""
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
            
            upvote_data = response.json()
            
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
            
            downvote_data = response.json()
            
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
                remove_data = response.json()
                details += f", Upvotes: {upvote_data.get('upvotes', 0)} -> {downvote_data.get('upvotes', 0)} -> {remove_data.get('upvotes', 0)}"
                details += f", Downvotes: {upvote_data.get('downvotes', 0)} -> {downvote_data.get('downvotes', 0)} -> {remove_data.get('downvotes', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Vote on Question", success, details)
        except Exception as e:
            return self.log_test("Vote on Question", False, f"Error: {str(e)}")

    def test_vote_on_answer(self):
        """Test voting on answer"""
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
                data = response.json()
                details += f", Upvotes: {data.get('upvotes', 0)}"
                details += f", Downvotes: {data.get('downvotes', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Vote on Answer", success, details)
        except Exception as e:
            return self.log_test("Vote on Answer", False, f"Error: {str(e)}")

    def test_vote_on_discussion(self):
        """Test voting on discussion"""
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
                data = response.json()
                details += f", Upvotes: {data.get('upvotes', 0)}"
                details += f", Downvotes: {data.get('downvotes', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Vote on Discussion", success, details)
        except Exception as e:
            return self.log_test("Vote on Discussion", False, f"Error: {str(e)}")

    def test_prevent_self_voting(self):
        """Test prevention of self-voting"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Prevent Self Voting", False, "No user token or question ID available")
        
        try:
            # Try to vote on own question (should fail)
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
                data = response.json()
                details += f", Message: {data.get('detail', 'No message')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Prevent Self Voting", success, details)
        except Exception as e:
            return self.log_test("Prevent Self Voting", False, f"Error: {str(e)}")

    def test_admin_qa_statistics(self):
        """Test admin Q&A statistics endpoint"""
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
                data = response.json()
                details += f", Total Questions: {data.get('total_questions', 0)}"
                details += f", Total Answers: {data.get('total_answers', 0)}"
                details += f", Total Discussions: {data.get('total_discussions', 0)}"
                details += f", Total Contributors: {data.get('total_contributors', 0)}"
                details += f", Open Questions: {data.get('open_questions', 0)}"
                details += f", Answered Questions: {data.get('answered_questions', 0)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Q&A Statistics", success, details)
        except Exception as e:
            return self.log_test("Admin Q&A Statistics", False, f"Error: {str(e)}")

    def test_admin_pin_question(self):
        """Test admin pinning question via PUT endpoint"""
        if not self.admin_token or not self.created_question_id:
            return self.log_test("Admin Pin Question", False, "No admin token or question ID available")
        
        try:
            # Pin the question (toggle endpoint)
            response = requests.put(
                f"{self.api_url}/admin/questions/{self.created_question_id}/pin",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                details += f", Is Pinned: {data.get('is_pinned', False)}"
                
                # Test unpinning (toggle again)
                unpin_response = requests.put(
                    f"{self.api_url}/admin/questions/{self.created_question_id}/pin",
                    headers=self.get_auth_headers(self.admin_token),
                    timeout=10
                )
                if unpin_response.status_code == 200:
                    unpin_data = unpin_response.json()
                    details += f", Unpinned: {not unpin_data.get('is_pinned', True)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Pin Question", success, details)
        except Exception as e:
            return self.log_test("Admin Pin Question", False, f"Error: {str(e)}")

    def test_admin_delete_content(self):
        """Test admin deleting Q&A content"""
        if not self.admin_token:
            return self.log_test("Admin Delete Content", False, "No admin token available")
        
        try:
            # Create a test question to delete
            question_data = {
                "title": "Test Question for Deletion",
                "content": "This question will be deleted by admin",
                "subject": "Test",
                "subcategory": "Admin Test",
                "tags": ["test", "admin"]
            }
            
            create_response = requests.post(
                f"{self.api_url}/questions",
                json=question_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            if create_response.status_code != 200:
                return self.log_test("Admin Delete Content", False, "Could not create test question")
            
            test_question_id = create_response.json().get('id')
            
            # Admin delete the question
            response = requests.delete(
                f"{self.api_url}/admin/questions/{test_question_id}",
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                
                # Verify question is deleted
                verify_response = requests.get(
                    f"{self.api_url}/questions/{test_question_id}",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                details += f", Verified Deleted: {verify_response.status_code == 404}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Delete Content", success, details)
        except Exception as e:
            return self.log_test("Admin Delete Content", False, f"Error: {str(e)}")

    def test_subjects_available_endpoint(self):
        """Test subjects available endpoint for Q&A filtering"""
        if not self.user_token:
            return self.log_test("Subjects Available Endpoint", False, "No user token available")
        
        try:
            response = requests.get(
                f"{self.api_url}/subjects-available",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Subjects Count: {len(data)}"
                if len(data) > 0:
                    details += f", First Subject: {data[0]}"
                    # Check if our test subject is included
                    if "Computer Science" in data:
                        details += ", Test Subject Found: Yes"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Subjects Available Endpoint", success, details)
        except Exception as e:
            return self.log_test("Subjects Available Endpoint", False, f"Error: {str(e)}")

    def test_non_admin_access_admin_endpoints(self):
        """Test non-admin users cannot access admin endpoints"""
        if not self.user_token:
            return self.log_test("Non-Admin Access Admin Endpoints", False, "No user token available")
        
        try:
            # Test Q&A stats (should fail)
            response = requests.get(
                f"{self.api_url}/admin/qa-stats",
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            
            stats_blocked = response.status_code == 403
            
            # Test pin question (should fail)
            if self.created_question_id:
                pin_response = requests.post(
                    f"{self.api_url}/admin/questions/{self.created_question_id}/pin",
                    headers=self.get_auth_headers(self.user_token),
                    timeout=10
                )
                pin_blocked = pin_response.status_code == 403
            else:
                pin_blocked = True  # Skip if no question ID
            
            success = stats_blocked and pin_blocked
            details = f"Stats Blocked: {stats_blocked}, Pin Blocked: {pin_blocked}"
            
            return self.log_test("Non-Admin Access Admin Endpoints", success, details)
        except Exception as e:
            return self.log_test("Non-Admin Access Admin Endpoints", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all Q&A Discussion System tests"""
        print("🎯 Q&A DISCUSSION SYSTEM BACKEND API TESTING")
        print("=" * 60)
        
        # Authentication tests
        self.test_admin_login()
        self.test_user_registration()
        self.test_user_login()
        self.test_user2_registration_and_login()
        
        # Questions CRUD tests
        self.test_create_question()
        self.test_get_questions_list()
        self.test_get_question_details()
        self.test_update_question()
        
        # Answers functionality tests
        self.test_add_answer()
        self.test_get_question_answers()
        self.test_accept_answer()
        
        # Discussions/threaded replies tests
        self.test_add_discussion()
        self.test_add_threaded_discussion()
        self.test_get_question_discussions()
        
        # Voting system tests
        self.test_vote_on_question()
        self.test_vote_on_answer()
        self.test_vote_on_discussion()
        self.test_prevent_self_voting()
        
        # Admin features tests
        self.test_admin_qa_statistics()
        self.test_admin_pin_question()
        self.test_admin_delete_content()
        
        # Utility and security tests
        self.test_subjects_available_endpoint()
        self.test_non_admin_access_admin_endpoints()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"🎯 Q&A DISCUSSION SYSTEM TESTING COMPLETE")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL Q&A DISCUSSION SYSTEM TESTS PASSED!")
            return True
        else:
            print("❌ Some Q&A tests failed. Check the details above.")
            return False

if __name__ == "__main__":
    tester = QADiscussionAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)