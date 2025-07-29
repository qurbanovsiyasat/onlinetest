#!/usr/bin/env python3
"""
Q&A Discussion System Backend API Testing - Review Request
Tests the specific Q&A endpoints requested in the review:

1. GET /api/questions/ - sualları almaq
2. POST /api/questions/ - sual yaratmaq  
3. GET /api/admin/qa-stats - Q&A statistikalarını almaq
4. GET /api/questions/{id} - sual detallarını almaq
5. POST /api/questions/{id}/answers/ - cavab yaratmaq
6. PUT /api/admin/questions/{id}/pin - sual pin etmək

Admin credentials: admin@squiz.com / admin123
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import base64

class QAReviewTester:
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
        
        # Test data storage
        self.created_question_id = None
        self.created_answer_id = None

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

    def test_admin_authentication(self):
        """Test admin login with provided credentials"""
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
                details += f", Email: {user_info.get('email', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("Admin Authentication (admin@squiz.com)", success, details)
        except Exception as e:
            return self.log_test("Admin Authentication (admin@squiz.com)", False, f"Error: {str(e)}")

    def test_user_registration_and_login(self):
        """Test user registration and login for testing user functionality"""
        # Register user
        user_data = {
            "name": f"QA Review User {self.test_user_id}",
            "email": f"qareview{self.test_user_id}@example.com",
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
                return self.log_test("User Registration & Login", False, f"Registration failed: {response.status_code}")
            
            # Login user
            login_data = {
                "email": f"qareview{self.test_user_id}@example.com",
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
                self.user_token = data.get('access_token')
                user_info = data.get('user', {})
                details += f", Role: {user_info.get('role', 'Unknown')}"
                details += f", Name: {user_info.get('name', 'Unknown')}"
            else:
                details += f", Login failed: {response.text[:200]}"
                
            return self.log_test("User Registration & Login", success, details)
        except Exception as e:
            return self.log_test("User Registration & Login", False, f"Error: {str(e)}")

    def test_post_questions_create(self):
        """Test POST /api/questions/ - sual yaratmaq (create question)"""
        if not self.user_token:
            return self.log_test("POST /api/questions/ (Create Question)", False, "No user token available")
            
        # Create a base64 encoded test image
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        
        question_data = {
            "title": "Python-da list comprehension necə işləyir?",
            "content": "Python-da list comprehension istifadə edərək siyahı yaratmaq haqqında ətraflı məlumat verə bilərsinizmi? Nümunələrlə izah edin.",
            "image": test_image,
            "subject": "Proqramlaşdırma",
            "subcategory": "Python",
            "tags": ["python", "list-comprehension", "programming", "basics"]
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
                details += f", Title: {question.get('title', 'Unknown')[:40]}..."
                details += f", Subject: {question.get('subject', 'Unknown')}"
                details += f", Tags: {len(question.get('tags', []))}"
                details += f", Status: {question.get('status', 'Unknown')}"
                details += f", Has Image: {bool(question.get('image'))}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("POST /api/questions/ (Create Question)", success, details)
        except Exception as e:
            return self.log_test("POST /api/questions/ (Create Question)", False, f"Error: {str(e)}")

    def test_get_questions_list(self):
        """Test GET /api/questions/ - sualları almaq (get questions)"""
        try:
            response = requests.get(f"{self.api_url}/questions", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                questions = data.get('questions', [])
                details += f", Questions Count: {len(questions)}"
                details += f", Total: {data.get('total', 0)}"
                details += f", Page: {data.get('page', 1)}"
                if len(questions) > 0:
                    first_q = questions[0]
                    details += f", First Q: {first_q.get('title', 'Unknown')[:30]}..."
                    details += f", Upvotes: {first_q.get('upvotes', 0)}"
                    details += f", Status: {first_q.get('status', 'Unknown')}"
                    details += f", Answer Count: {first_q.get('answer_count', 0)}"
                
                # Test filtering by subject
                if len(questions) > 0:
                    subject_response = requests.get(
                        f"{self.api_url}/questions?subject=Proqramlaşdırma", 
                        timeout=10
                    )
                    if subject_response.status_code == 200:
                        filtered_data = subject_response.json()
                        filtered = filtered_data.get('questions', [])
                        details += f", Filtered by Subject: {len(filtered)}"
                
                # Test filtering by status
                status_response = requests.get(
                    f"{self.api_url}/questions?status=open", 
                    timeout=10
                )
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status_filtered = status_data.get('questions', [])
                    details += f", Filtered by Status: {len(status_filtered)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("GET /api/questions/ (Get Questions)", success, details)
        except Exception as e:
            return self.log_test("GET /api/questions/ (Get Questions)", False, f"Error: {str(e)}")

    def test_get_question_details(self):
        """Test GET /api/questions/{id} - sual detallarını almaq (get question details)"""
        if not self.created_question_id:
            return self.log_test("GET /api/questions/{id} (Question Details)", False, "No question ID available")
            
        try:
            response = requests.get(
                f"{self.api_url}/questions/{self.created_question_id}",
                timeout=10
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                question = response.json()
                details += f", Title: {question.get('title', 'Unknown')[:40]}..."
                details += f", Content Length: {len(question.get('content', ''))}"
                details += f", Upvotes: {question.get('upvotes', 0)}"
                details += f", Downvotes: {question.get('downvotes', 0)}"
                details += f", Answer Count: {question.get('answer_count', 0)}"
                details += f", Has Image: {bool(question.get('image'))}"
                details += f", Tags: {len(question.get('tags', []))}"
                details += f", Subject: {question.get('subject', 'Unknown')}"
                details += f", Status: {question.get('status', 'Unknown')}"
                details += f", Is Pinned: {question.get('is_pinned', False)}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("GET /api/questions/{id} (Question Details)", success, details)
        except Exception as e:
            return self.log_test("GET /api/questions/{id} (Question Details)", False, f"Error: {str(e)}")

    def test_post_question_answers(self):
        """Test POST /api/questions/{id}/answers/ - cavab yaratmaq (create answer)"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("POST /api/questions/{id}/answers/ (Create Answer)", False, "No user token or question ID available")
            
        # Create a base64 encoded test image for answer
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        
        answer_data = {
            "content": "Python-da list comprehension çox güclü bir xüsusiyyətdir. Budur əsas sintaksis:\n\n```python\n# Əsas sintaksis\nnew_list = [expression for item in iterable if condition]\n\n# Nümunə 1: Sadə list comprehension\nnumbers = [1, 2, 3, 4, 5]\nsquares = [x**2 for x in numbers]\nprint(squares)  # [1, 4, 9, 16, 25]\n\n# Nümunə 2: Şərtli list comprehension\neven_squares = [x**2 for x in numbers if x % 2 == 0]\nprint(even_squares)  # [4, 16]\n\n# Nümunə 3: String ilə işləmək\nwords = ['hello', 'world', 'python']\ncapitalized = [word.upper() for word in words]\nprint(capitalized)  # ['HELLO', 'WORLD', 'PYTHON']\n```\n\nList comprehension ənənəvi for döngüsündən daha qısa və oxunaqlıdır.",
            "image": test_image
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/questions/{self.created_question_id}/answers",
                json=answer_data,
                headers=self.get_auth_headers(self.user_token),
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
                details += f", Question ID: {answer.get('question_id', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("POST /api/questions/{id}/answers/ (Create Answer)", success, details)
        except Exception as e:
            return self.log_test("POST /api/questions/{id}/answers/ (Create Answer)", False, f"Error: {str(e)}")

    def test_get_admin_qa_stats(self):
        """Test GET /api/admin/qa-stats - Q&A statistikalarını almaq (get Q&A statistics)"""
        if not self.admin_token:
            return self.log_test("GET /api/admin/qa-stats (Q&A Statistics)", False, "No admin token available")
            
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
                details += f", Contributors: {stats.get('total_contributors', 0)}"
                details += f", Most Active Subject: {stats.get('most_active_subject', 'None')}"
                
                # Check if top contributors are included
                top_contributors = stats.get('top_contributors', [])
                details += f", Top Contributors Count: {len(top_contributors)}"
                if len(top_contributors) > 0:
                    details += f", First Contributor: {top_contributors[0].get('name', 'Unknown')}"
            else:
                details += f", Response: {response.text[:200]}"
                
            return self.log_test("GET /api/admin/qa-stats (Q&A Statistics)", success, details)
        except Exception as e:
            return self.log_test("GET /api/admin/qa-stats (Q&A Statistics)", False, f"Error: {str(e)}")

    def test_put_admin_question_pin(self):
        """Test PUT /api/admin/questions/{id}/pin - sual pin etmək (pin question)"""
        if not self.admin_token or not self.created_question_id:
            return self.log_test("PUT /api/admin/questions/{id}/pin (Pin Question)", False, "No admin token or question ID available")
            
        try:
            # First, pin the question
            pin_data = {"is_pinned": True}
            response = requests.put(
                f"{self.api_url}/admin/questions/{self.created_question_id}/pin",
                json=pin_data,
                headers=self.get_auth_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code != 200:
                return self.log_test("PUT /api/admin/questions/{id}/pin (Pin Question)", False, f"Pin failed: {response.status_code}, Response: {response.text[:200]}")
            
            pin_result = response.json()
            
            # Then, unpin the question to test both operations
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
                details += f", Question Title: {unpin_result.get('title', 'Unknown')[:30]}..."
                details += f", Updated At: {unpin_result.get('updated_at', 'Unknown')[:19]}"
            else:
                details += f", Unpin failed: {response.text[:200]}"
                
            return self.log_test("PUT /api/admin/questions/{id}/pin (Pin Question)", success, details)
        except Exception as e:
            return self.log_test("PUT /api/admin/questions/{id}/pin (Pin Question)", False, f"Error: {str(e)}")

    def test_non_admin_pin_access(self):
        """Test that non-admin users cannot pin questions"""
        if not self.user_token or not self.created_question_id:
            return self.log_test("Non-Admin Pin Access (Security Test)", False, "No user token or question ID available")
            
        try:
            pin_data = {"is_pinned": True}
            response = requests.put(
                f"{self.api_url}/admin/questions/{self.created_question_id}/pin",
                json=pin_data,
                headers=self.get_auth_headers(self.user_token),
                timeout=10
            )
            success = response.status_code == 403  # Should be forbidden
            details = f"Status: {response.status_code} (Expected 403 Forbidden)"
            
            if success:
                details += ", Non-admin access correctly blocked"
            else:
                details += f", Unexpected response: {response.text[:200]}"
                
            return self.log_test("Non-Admin Pin Access (Security Test)", success, details)
        except Exception as e:
            return self.log_test("Non-Admin Pin Access (Security Test)", False, f"Error: {str(e)}")

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints"""
        try:
            # Test creating question without auth
            question_data = {
                "title": "Test Question",
                "content": "This should fail",
                "subject": "Test"
            }
            response = requests.post(
                f"{self.api_url}/questions",
                json=question_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            create_success = response.status_code == 401 or response.status_code == 403
            
            # Test admin stats without auth
            response = requests.get(f"{self.api_url}/admin/qa-stats", timeout=10)
            stats_success = response.status_code == 401 or response.status_code == 403
            
            success = create_success and stats_success
            details = f"Create Question: {response.status_code}, Admin Stats: {response.status_code}"
            details += " (Expected 401/403 for both)"
            
            return self.log_test("Unauthenticated Access (Security Test)", success, details)
        except Exception as e:
            return self.log_test("Unauthenticated Access (Security Test)", False, f"Error: {str(e)}")

    def run_review_tests(self):
        """Run all requested Q&A endpoints tests"""
        print("🚀 Starting Q&A Discussion System Review Testing")
        print(f"🔗 Testing against: {self.base_url}")
        print("📋 Testing specific endpoints requested in review:")
        print("   1. GET /api/questions/ - sualları almaq")
        print("   2. POST /api/questions/ - sual yaratmaq")
        print("   3. GET /api/admin/qa-stats - Q&A statistikalarını almaq")
        print("   4. GET /api/questions/{id} - sual detallarını almaq")
        print("   5. POST /api/questions/{id}/answers/ - cavab yaratmaq")
        print("   6. PUT /api/admin/questions/{id}/pin - sual pin etmək")
        print("=" * 80)
        
        # Authentication setup
        print("\n🔐 AUTHENTICATION SETUP")
        print("-" * 40)
        self.test_admin_authentication()
        self.test_user_registration_and_login()
        
        # Core Q&A endpoints testing
        print("\n📝 Q&A ENDPOINTS TESTING")
        print("-" * 40)
        
        # Test 2: POST /api/questions/ - sual yaratmaq
        self.test_post_questions_create()
        
        # Test 1: GET /api/questions/ - sualları almaq
        self.test_get_questions_list()
        
        # Test 4: GET /api/questions/{id} - sual detallarını almaq
        self.test_get_question_details()
        
        # Test 5: POST /api/questions/{id}/answers/ - cavab yaratmaq
        self.test_post_question_answers()
        
        # Test 3: GET /api/admin/qa-stats - Q&A statistikalarını almaq
        self.test_get_admin_qa_stats()
        
        # Test 6: PUT /api/admin/questions/{id}/pin - sual pin etmək
        self.test_put_admin_question_pin()
        
        # Security tests
        print("\n🔒 SECURITY TESTS")
        print("-" * 40)
        self.test_non_admin_pin_access()
        self.test_unauthenticated_access()
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎯 Q&A REVIEW TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📊 Total Tests: {self.tests_run}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Detailed endpoint results
        print("\n📋 REQUESTED ENDPOINTS RESULTS:")
        print("1. GET /api/questions/ - ✅ TESTED")
        print("2. POST /api/questions/ - ✅ TESTED")
        print("3. GET /api/admin/qa-stats - ✅ TESTED")
        print("4. GET /api/questions/{id} - ✅ TESTED")
        print("5. POST /api/questions/{id}/answers/ - ✅ TESTED")
        print("6. PUT /api/admin/questions/{id}/pin - ✅ TESTED")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL REQUESTED Q&A ENDPOINTS ARE WORKING PERFECTLY!")
            print("✅ Admin credentials (admin@squiz.com/admin123) working")
            print("✅ User registration and login working")
            print("✅ Question creation and retrieval working")
            print("✅ Answer creation working")
            print("✅ Admin Q&A statistics working")
            print("✅ Question pinning functionality working")
            print("✅ Security controls working (authentication required)")
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} tests failed - check implementation")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = QAReviewTester()
    success = tester.run_review_tests()
    sys.exit(0 if success else 1)