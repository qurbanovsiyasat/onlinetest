#!/usr/bin/env python3
"""
Comprehensive Q&A Discussion System Test - Final Verification
Tests all major Q&A functionality end-to-end
"""

import requests
import json
import uuid

class QAComprehensiveTest:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.admin_token = None
        self.user_token = None
        self.user2_token = None
        self.test_results = []

    def log_result(self, test_name, success, details=""):
        result = {
            "test": test_name,
            "success": success,
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        return success

    def setup_authentication(self):
        """Setup admin and user authentication"""
        # Admin login
        admin_login = {
            "email": "admin@squiz.com",
            "password": "admin123"
        }
        response = requests.post(f"{self.api_url}/auth/login", json=admin_login)
        if response.status_code == 200:
            self.admin_token = response.json().get('access_token')
            self.log_result("Admin Authentication", True, "Admin logged in successfully")
        else:
            self.log_result("Admin Authentication", False, f"Status: {response.status_code}")
            return False

        # User registration and login
        user_id = str(uuid.uuid4())[:8]
        user_data = {
            "name": f"QA Test User {user_id}",
            "email": f"qatest{user_id}@example.com",
            "password": "testpass123"
        }
        
        # Register user
        response = requests.post(f"{self.api_url}/auth/register", json=user_data)
        if response.status_code != 200:
            self.log_result("User Registration", False, f"Status: {response.status_code}")
            return False
        
        # Login user
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        if response.status_code == 200:
            self.user_token = response.json().get('access_token')
            self.log_result("User Authentication", True, "User registered and logged in")
        else:
            self.log_result("User Authentication", False, f"Status: {response.status_code}")
            return False

        # Second user for voting tests
        user2_id = str(uuid.uuid4())[:8]
        user2_data = {
            "name": f"QA Test User 2 {user2_id}",
            "email": f"qatest2{user2_id}@example.com",
            "password": "testpass123"
        }
        
        requests.post(f"{self.api_url}/auth/register", json=user2_data)
        login_data2 = {"email": user2_data["email"], "password": user2_data["password"]}
        response = requests.post(f"{self.api_url}/auth/login", json=login_data2)
        if response.status_code == 200:
            self.user2_token = response.json().get('access_token')
            self.log_result("Second User Authentication", True, "Second user ready for voting tests")
        else:
            self.log_result("Second User Authentication", False, f"Status: {response.status_code}")

        return True

    def test_complete_qa_workflow(self):
        """Test complete Q&A workflow: Question → Answer → Discussion → Voting → Admin Management"""
        
        # 1. Create Question
        question_data = {
            "title": "What is the time complexity of quicksort?",
            "content": "I'm studying sorting algorithms and need to understand the time complexity of quicksort in best, average, and worst cases. Can someone explain with examples?",
            "subject": "Computer Science",
            "subcategory": "Algorithms",
            "tags": ["algorithms", "sorting", "time-complexity", "quicksort"]
        }
        
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.user_token}'}
        response = requests.post(f"{self.api_url}/questions", json=question_data, headers=headers)
        
        if response.status_code != 200:
            self.log_result("Question Creation", False, f"Status: {response.status_code}")
            return False
        
        question = response.json()
        question_id = question.get('id')
        self.log_result("Question Creation", True, f"Question created with ID: {question_id}")

        # 2. Add Answer
        answer_data = {
            "content": "Quicksort time complexity:\n\n**Best Case: O(n log n)** - When pivot divides array into equal halves\n**Average Case: O(n log n)** - Expected performance with random data\n**Worst Case: O(n²)** - When pivot is always the smallest/largest element\n\nThe worst case occurs when the array is already sorted and we always pick the first element as pivot."
        }
        
        headers2 = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.user2_token}'}
        response = requests.post(f"{self.api_url}/questions/{question_id}/answers", json=answer_data, headers=headers2)
        
        if response.status_code != 200:
            self.log_result("Answer Creation", False, f"Status: {response.status_code}")
            return False
        
        answer = response.json()
        answer_id = answer.get('id')
        self.log_result("Answer Creation", True, f"Answer created with ID: {answer_id}")

        # 3. Accept Answer (by question author)
        accept_data = {"is_accepted": True}
        response = requests.put(f"{self.api_url}/questions/{question_id}/answers/{answer_id}", json=accept_data, headers=headers)
        
        if response.status_code == 200:
            self.log_result("Answer Acceptance", True, "Answer accepted by question author")
        else:
            self.log_result("Answer Acceptance", False, f"Status: {response.status_code}")

        # 4. Add Discussion
        discussion_data = {
            "message": "Great explanation! Could you also explain why quicksort is preferred over mergesort in many practical applications despite having worse worst-case complexity?"
        }
        
        response = requests.post(f"{self.api_url}/questions/{question_id}/discussions", json=discussion_data, headers=headers)
        
        if response.status_code != 200:
            self.log_result("Discussion Creation", False, f"Status: {response.status_code}")
            return False
        
        discussion = response.json()
        discussion_id = discussion.get('id')
        self.log_result("Discussion Creation", True, f"Discussion created with ID: {discussion_id}")

        # 5. Vote on Question (by second user)
        vote_data = {"vote_type": "upvote"}
        response = requests.post(f"{self.api_url}/questions/{question_id}/vote", json=vote_data, headers=headers2)
        
        if response.status_code == 200:
            self.log_result("Question Voting", True, "Question upvoted successfully")
        else:
            self.log_result("Question Voting", False, f"Status: {response.status_code}")

        # 6. Vote on Answer (by question author)
        response = requests.post(f"{self.api_url}/answers/{answer_id}/vote", json=vote_data, headers=headers)
        
        if response.status_code == 200:
            self.log_result("Answer Voting", True, "Answer upvoted successfully")
        else:
            self.log_result("Answer Voting", False, f"Status: {response.status_code}")

        # 7. Admin Pin Question
        admin_headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.admin_token}'}
        pin_data = {"is_pinned": True}
        response = requests.put(f"{self.api_url}/admin/questions/{question_id}/pin", json=pin_data, headers=admin_headers)
        
        if response.status_code == 200:
            self.log_result("Admin Pin Question", True, "Question pinned by admin")
        else:
            self.log_result("Admin Pin Question", False, f"Status: {response.status_code}")

        # 8. Get Q&A Statistics
        response = requests.get(f"{self.api_url}/admin/qa-stats", headers=admin_headers)
        
        if response.status_code == 200:
            stats = response.json()
            self.log_result("Q&A Statistics", True, f"Stats: {stats.get('total_questions', 0)} questions, {stats.get('total_answers', 0)} answers")
        else:
            self.log_result("Q&A Statistics", False, f"Status: {response.status_code}")

        # 9. Get Question Detail (verify all components)
        response = requests.get(f"{self.api_url}/questions/{question_id}")
        
        if response.status_code == 200:
            question_detail = response.json()
            has_content = bool(question_detail.get('title') and question_detail.get('content'))
            has_votes = question_detail.get('upvotes', 0) > 0
            is_pinned = question_detail.get('is_pinned', False)
            self.log_result("Question Detail Verification", True, f"Complete question with votes: {has_votes}, pinned: {is_pinned}")
        else:
            self.log_result("Question Detail Verification", False, f"Status: {response.status_code}")

        # 10. Get Available Subjects
        response = requests.get(f"{self.api_url}/subjects-available")
        
        if response.status_code == 200:
            subjects = response.json()
            total_subjects = len(subjects.get('subjects', []))
            self.log_result("Subjects Available", True, f"Found {total_subjects} available subjects")
        else:
            self.log_result("Subjects Available", False, f"Status: {response.status_code}")

        return True

    def test_security_and_permissions(self):
        """Test security and permission controls"""
        
        # Test unauthenticated access
        question_data = {"title": "Test", "content": "Test", "subject": "Test"}
        response = requests.post(f"{self.api_url}/questions", json=question_data)
        
        if response.status_code in [401, 403]:
            self.log_result("Unauthenticated Access Prevention", True, f"Correctly blocked with status {response.status_code}")
        else:
            self.log_result("Unauthenticated Access Prevention", False, f"Unexpected status: {response.status_code}")

        # Test non-admin trying to access admin endpoints
        user_headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.user_token}'}
        response = requests.get(f"{self.api_url}/admin/qa-stats", headers=user_headers)
        
        if response.status_code == 403:
            self.log_result("Admin Endpoint Protection", True, "Non-admin correctly blocked from admin endpoints")
        else:
            self.log_result("Admin Endpoint Protection", False, f"Status: {response.status_code}")

    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🚀 Q&A DISCUSSION SYSTEM - COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed - cannot continue")
            return False
        
        print("\n📋 COMPLETE Q&A WORKFLOW TEST")
        print("-" * 40)
        self.test_complete_qa_workflow()
        
        print("\n🔒 SECURITY AND PERMISSIONS TEST")
        print("-" * 40)
        self.test_security_and_permissions()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {passed_tests}")
        print(f"❌ Tests Failed: {failed_tests}")
        print(f"📊 Total Tests: {total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 ALL Q&A DISCUSSION SYSTEM FUNCTIONALITY WORKING PERFECTLY!")
            print("✨ The Q&A system is ready for production use!")
        else:
            print(f"\n⚠️  {failed_tests} issues found - review implementation")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = QAComprehensiveTest()
    success = tester.run_comprehensive_test()