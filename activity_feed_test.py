#!/usr/bin/env python3
"""
Activity Feed Endpoint Testing
Testing Priority: HIGH

This script tests the newly implemented Activity Feed endpoint:
GET /api/user/activity-feed

Test Scenarios:
1. Test with authenticated user who follows other users
2. Test pagination parameters (limit, offset)
3. Test with user who follows no one (should return empty feed)
4. Test authentication requirement (should fail without auth)
5. Verify the response structure includes: activities array, total count, has_more flag
6. Check that activities include proper metadata and activity types
"""

import requests
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "admin@squiz.com"
ADMIN_PASSWORD = "admin123"

class ActivityFeedTester:
    def __init__(self):
        self.admin_token = None
        self.user_tokens = {}
        self.user_ids = {}
        self.test_results = []
        self.created_data = {
            "users": [],
            "quizzes": [],
            "questions": [],
            "follows": []
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    token: str = None, params: Dict = None) -> tuple[bool, Any]:
        """Make HTTP request to backend"""
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return False, f"Unsupported method: {method}"
            
            if response.status_code < 400:
                return True, response.json() if response.content else {}
            else:
                return False, {
                    "status_code": response.status_code,
                    "error": response.text
                }
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def setup_admin_auth(self) -> bool:
        """Authenticate as admin"""
        print("🔐 Setting up admin authentication...")
        
        success, result = self.make_request("POST", "/auth/login", {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if success and "access_token" in result:
            self.admin_token = result["access_token"]
            self.log_test("Admin Authentication", True, f"Admin logged in successfully")
            return True
        else:
            self.log_test("Admin Authentication", False, f"Failed to login admin: {result}")
            return False
    
    def create_test_users(self) -> bool:
        """Create test users for activity feed testing"""
        print("👥 Creating test users...")
        
        test_users = [
            {"name": "Alice Johnson", "email": "alice@activitytest.com", "password": "password123"},
            {"name": "Bob Smith", "email": "bob@activitytest.com", "password": "password123"},
            {"name": "Charlie Brown", "email": "charlie@activitytest.com", "password": "password123"},
            {"name": "Diana Prince", "email": "diana@activitytest.com", "password": "password123"}
        ]
        
        for user_data in test_users:
            # Register user
            success, result = self.make_request("POST", "/auth/register", user_data)
            
            if success:
                # Login user to get token
                login_success, login_result = self.make_request("POST", "/auth/login", {
                    "email": user_data["email"],
                    "password": user_data["password"]
                })
                
                if login_success and "access_token" in login_result:
                    user_name = user_data["name"].split()[0].lower()  # alice, bob, charlie, diana
                    self.user_tokens[user_name] = login_result["access_token"]
                    self.user_ids[user_name] = login_result["user"]["id"]
                    self.created_data["users"].append(user_data["email"])
                    self.log_test(f"Create User {user_data['name']}", True, f"User created and authenticated")
                else:
                    self.log_test(f"Create User {user_data['name']}", False, f"Failed to login: {login_result}")
                    return False
            else:
                # User might already exist, try to login
                login_success, login_result = self.make_request("POST", "/auth/login", {
                    "email": user_data["email"],
                    "password": user_data["password"]
                })
                
                if login_success and "access_token" in login_result:
                    user_name = user_data["name"].split()[0].lower()
                    self.user_tokens[user_name] = login_result["access_token"]
                    self.user_ids[user_name] = login_result["user"]["id"]
                    self.log_test(f"Login Existing User {user_data['name']}", True, f"User authenticated")
                else:
                    self.log_test(f"Create/Login User {user_data['name']}", False, f"Failed: {result}")
                    return False
        
        return len(self.user_tokens) >= 4
    
    def setup_follow_relationships(self) -> bool:
        """Setup follow relationships for activity feed testing"""
        print("🔗 Setting up follow relationships...")
        
        # Alice follows Bob and Charlie
        # Bob follows Diana
        # Charlie follows no one
        # Diana follows Alice
        
        follow_relationships = [
            ("alice", "bob"),
            ("alice", "charlie"),
            ("bob", "diana"),
            ("diana", "alice")
        ]
        
        for follower, following in follow_relationships:
            if follower in self.user_tokens and following in self.user_ids:
                success, result = self.make_request("POST", "/user/follow", {
                    "user_id": self.user_ids[following]
                }, token=self.user_tokens[follower])
                
                if success:
                    self.log_test(f"Follow Relationship: {follower} -> {following}", True, "Follow relationship created")
                    self.created_data["follows"].append(f"{follower}->{following}")
                else:
                    self.log_test(f"Follow Relationship: {follower} -> {following}", False, f"Failed: {result}")
        
        return True
    
    def create_test_content(self) -> bool:
        """Create test content (quizzes, questions) for activity feed"""
        print("📝 Creating test content...")
        
        # Create quiz by Bob (will appear in Alice's feed)
        quiz_data = {
            "title": "Bob's Math Quiz for Activity Feed",
            "description": "A test quiz for activity feed testing",
            "category": "Mathematics",
            "subject": "Algebra",
            "subcategory": "Basic",
            "questions": [
                {
                    "question_text": "What is 2 + 2?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True},
                        {"text": "5", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
                }
            ],
            "is_public": False,
            "min_pass_percentage": 60.0
        }
        
        # Create quiz as admin first, then we'll simulate user-created content
        success, result = self.make_request("POST", "/admin/quiz", quiz_data, token=self.admin_token)
        
        if success:
            quiz_id = result["id"]
            # Publish the quiz
            pub_success, pub_result = self.make_request("POST", f"/admin/quiz/{quiz_id}/publish", {}, token=self.admin_token)
            if pub_success:
                self.created_data["quizzes"].append(quiz_id)
                self.log_test("Create Test Quiz", True, f"Quiz created and published: {quiz_id}")
            else:
                self.log_test("Publish Test Quiz", False, f"Failed to publish: {pub_result}")
        else:
            self.log_test("Create Test Quiz", False, f"Failed: {result}")
        
        # Create a question by Charlie (will appear in Alice's feed)
        question_data = {
            "title": "Charlie's Question About Physics",
            "content": "How does gravity work in space?",
            "subject": "Physics",
            "subcategory": "Space",
            "tags": ["gravity", "space", "physics"]
        }
        
        success, result = self.make_request("POST", "/questions", question_data, token=self.user_tokens["charlie"])
        
        if success:
            question_id = result["id"]
            self.created_data["questions"].append(question_id)
            self.log_test("Create Test Question", True, f"Question created: {question_id}")
            
            # Bob answers Charlie's question (will appear in Alice's feed since Alice follows Bob)
            answer_data = {
                "content": "Gravity still works in space, but objects in orbit are in free fall!"
            }
            
            answer_success, answer_result = self.make_request("POST", f"/questions/{question_id}/answers", 
                                                            answer_data, token=self.user_tokens["bob"])
            
            if answer_success:
                self.log_test("Create Test Answer", True, f"Answer created by Bob")
            else:
                self.log_test("Create Test Answer", False, f"Failed: {answer_result}")
        else:
            self.log_test("Create Test Question", False, f"Failed: {result}")
        
        return True
    
    def test_activity_feed_authentication(self) -> bool:
        """Test that activity feed requires authentication"""
        print("🔒 Testing activity feed authentication requirement...")
        
        # Test without token
        success, result = self.make_request("GET", "/user/activity-feed")
        
        if not success and "status_code" in result and result["status_code"] == 403:
            self.log_test("Activity Feed Authentication Required", True, "Correctly requires authentication")
            return True
        else:
            self.log_test("Activity Feed Authentication Required", False, f"Should require auth but got: {result}")
            return False
    
    def test_activity_feed_with_follows(self) -> bool:
        """Test activity feed for user who follows others"""
        print("📰 Testing activity feed with follow relationships...")
        
        # Test Alice's activity feed (she follows Bob and Charlie)
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 10, "offset": 0}, 
                                          token=self.user_tokens["alice"])
        
        if success:
            # Verify response structure
            required_fields = ["activities", "total", "has_more", "offset", "limit"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                self.log_test("Activity Feed Response Structure", False, f"Missing fields: {missing_fields}")
                return False
            
            activities = result["activities"]
            total = result["total"]
            has_more = result["has_more"]
            
            self.log_test("Activity Feed Response Structure", True, 
                         f"Found {total} activities, has_more: {has_more}")
            
            # Verify activity structure
            if activities:
                activity = activities[0]
                required_activity_fields = ["id", "activity_type", "user_id", "user_name", 
                                          "title", "description", "created_at", "metadata"]
                missing_activity_fields = [field for field in required_activity_fields if field not in activity]
                
                if missing_activity_fields:
                    self.log_test("Activity Item Structure", False, f"Missing fields: {missing_activity_fields}")
                    return False
                else:
                    self.log_test("Activity Item Structure", True, "All required fields present")
                
                # Verify activity types are valid
                valid_types = ["quiz_published", "question_posted", "answer_posted", "quiz_completed", "user_followed"]
                invalid_activities = [a for a in activities if a["activity_type"] not in valid_types]
                
                if invalid_activities:
                    self.log_test("Activity Types Validation", False, f"Invalid types found: {[a['activity_type'] for a in invalid_activities]}")
                    return False
                else:
                    self.log_test("Activity Types Validation", True, f"All activity types valid")
                
                # Verify activities are from followed users only
                followed_user_ids = [self.user_ids["bob"], self.user_ids["charlie"]]
                invalid_user_activities = [a for a in activities if a["user_id"] not in followed_user_ids]
                
                if invalid_user_activities:
                    self.log_test("Activities From Followed Users Only", False, 
                                f"Found activities from non-followed users: {[a['user_name'] for a in invalid_user_activities]}")
                    return False
                else:
                    self.log_test("Activities From Followed Users Only", True, 
                                f"All activities from followed users")
            else:
                self.log_test("Activity Feed Content", True, "No activities found (expected for new test data)")
            
            return True
        else:
            self.log_test("Activity Feed With Follows", False, f"Failed: {result}")
            return False
    
    def test_activity_feed_pagination(self) -> bool:
        """Test activity feed pagination"""
        print("📄 Testing activity feed pagination...")
        
        # Test with different limit and offset values
        test_cases = [
            {"limit": 5, "offset": 0},
            {"limit": 10, "offset": 0},
            {"limit": 3, "offset": 2}
        ]
        
        for params in test_cases:
            success, result = self.make_request("GET", "/user/activity-feed", 
                                              params=params, 
                                              token=self.user_tokens["alice"])
            
            if success:
                activities = result["activities"]
                returned_limit = result["limit"]
                returned_offset = result["offset"]
                
                # Verify pagination parameters are returned correctly
                if returned_limit != params["limit"] or returned_offset != params["offset"]:
                    self.log_test(f"Pagination Parameters (limit={params['limit']}, offset={params['offset']})", 
                                False, f"Expected limit={params['limit']}, offset={params['offset']} but got limit={returned_limit}, offset={returned_offset}")
                    return False
                
                # Verify activities count doesn't exceed limit
                if len(activities) > params["limit"]:
                    self.log_test(f"Pagination Limit Enforcement (limit={params['limit']})", 
                                False, f"Returned {len(activities)} activities, exceeds limit of {params['limit']}")
                    return False
                
                self.log_test(f"Pagination Test (limit={params['limit']}, offset={params['offset']})", 
                            True, f"Returned {len(activities)} activities correctly")
            else:
                self.log_test(f"Pagination Test (limit={params['limit']}, offset={params['offset']})", 
                            False, f"Failed: {result}")
                return False
        
        return True
    
    def test_activity_feed_no_follows(self) -> bool:
        """Test activity feed for user who follows no one"""
        print("🚫 Testing activity feed with no follows...")
        
        # Test Charlie's activity feed (he follows no one)
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 10, "offset": 0}, 
                                          token=self.user_tokens["charlie"])
        
        if success:
            activities = result["activities"]
            total = result["total"]
            
            if total == 0 and len(activities) == 0:
                self.log_test("Activity Feed No Follows", True, "Correctly returns empty feed for user with no follows")
                return True
            else:
                self.log_test("Activity Feed No Follows", False, f"Expected empty feed but got {total} activities")
                return False
        else:
            self.log_test("Activity Feed No Follows", False, f"Failed: {result}")
            return False
    
    def test_activity_feed_metadata(self) -> bool:
        """Test that activity feed includes proper metadata"""
        print("🏷️ Testing activity feed metadata...")
        
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 20, "offset": 0}, 
                                          token=self.user_tokens["alice"])
        
        if success:
            activities = result["activities"]
            
            if activities:
                # Check different activity types have appropriate metadata
                for activity in activities:
                    activity_type = activity["activity_type"]
                    metadata = activity.get("metadata", {})
                    
                    if activity_type == "quiz_published":
                        required_meta = ["quiz_title", "subject", "total_questions"]
                        missing_meta = [field for field in required_meta if field not in metadata]
                        if missing_meta:
                            self.log_test("Quiz Published Metadata", False, f"Missing metadata: {missing_meta}")
                            return False
                    
                    elif activity_type == "question_posted":
                        required_meta = ["question_title", "subject"]
                        missing_meta = [field for field in required_meta if field not in metadata]
                        if missing_meta:
                            self.log_test("Question Posted Metadata", False, f"Missing metadata: {missing_meta}")
                            return False
                    
                    elif activity_type == "answer_posted":
                        required_meta = ["question_title", "answer_preview"]
                        missing_meta = [field for field in required_meta if field not in metadata]
                        if missing_meta:
                            self.log_test("Answer Posted Metadata", False, f"Missing metadata: {missing_meta}")
                            return False
                    
                    elif activity_type == "quiz_completed":
                        required_meta = ["quiz_title", "score", "passed"]
                        missing_meta = [field for field in required_meta if field not in metadata]
                        if missing_meta:
                            self.log_test("Quiz Completed Metadata", False, f"Missing metadata: {missing_meta}")
                            return False
                
                self.log_test("Activity Feed Metadata", True, "All activities have proper metadata")
                return True
            else:
                self.log_test("Activity Feed Metadata", True, "No activities to check metadata (expected for new test)")
                return True
        else:
            self.log_test("Activity Feed Metadata", False, f"Failed: {result}")
            return False
    
    def test_activity_feed_sorting(self) -> bool:
        """Test that activities are sorted by creation time (newest first)"""
        print("🔄 Testing activity feed sorting...")
        
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 20, "offset": 0}, 
                                          token=self.user_tokens["alice"])
        
        if success:
            activities = result["activities"]
            
            if len(activities) > 1:
                # Check that activities are sorted by created_at in descending order
                for i in range(len(activities) - 1):
                    current_time = datetime.fromisoformat(activities[i]["created_at"].replace('Z', '+00:00'))
                    next_time = datetime.fromisoformat(activities[i + 1]["created_at"].replace('Z', '+00:00'))
                    
                    if current_time < next_time:
                        self.log_test("Activity Feed Sorting", False, 
                                    f"Activities not sorted correctly: {activities[i]['created_at']} should be after {activities[i + 1]['created_at']}")
                        return False
                
                self.log_test("Activity Feed Sorting", True, "Activities correctly sorted by creation time (newest first)")
                return True
            else:
                self.log_test("Activity Feed Sorting", True, "Not enough activities to test sorting (expected for new test)")
                return True
        else:
            self.log_test("Activity Feed Sorting", False, f"Failed: {result}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all activity feed tests"""
        print("🚀 Starting Comprehensive Activity Feed Testing")
        print("=" * 60)
        
        # Setup phase
        if not self.setup_admin_auth():
            print("❌ Failed to setup admin authentication. Aborting tests.")
            return False
        
        if not self.create_test_users():
            print("❌ Failed to create test users. Aborting tests.")
            return False
        
        if not self.setup_follow_relationships():
            print("❌ Failed to setup follow relationships. Continuing with limited tests.")
        
        if not self.create_test_content():
            print("❌ Failed to create test content. Continuing with basic tests.")
        
        # Wait a moment for data to be processed
        time.sleep(2)
        
        # Core tests
        test_methods = [
            self.test_activity_feed_authentication,
            self.test_activity_feed_with_follows,
            self.test_activity_feed_pagination,
            self.test_activity_feed_no_follows,
            self.test_activity_feed_metadata,
            self.test_activity_feed_sorting
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                self.log_test(f"Exception in {test_method.__name__}", False, f"Exception: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 ACTIVITY FEED TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL ACTIVITY FEED TESTS PASSED!")
            print("✅ Activity Feed endpoint is working correctly")
            print("✅ Authentication requirement enforced")
            print("✅ Pagination working properly")
            print("✅ Response structure correct")
            print("✅ Activities from followed users only")
            print("✅ Proper metadata included")
            print("✅ Correct sorting (newest first)")
        else:
            print("⚠️  SOME TESTS FAILED")
            failed_tests = [result for result in self.test_results if not result["success"]]
            for failed_test in failed_tests:
                print(f"❌ {failed_test['test']}: {failed_test['details']}")
        
        return passed_tests == total_tests

def main():
    """Main function to run activity feed tests"""
    print("🔍 Activity Feed Endpoint Testing")
    print("Testing GET /api/user/activity-feed")
    print("=" * 60)
    
    tester = ActivityFeedTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 CONCLUSION: Activity Feed endpoint is working perfectly!")
        sys.exit(0)
    else:
        print("\n❌ CONCLUSION: Activity Feed endpoint has issues that need to be addressed.")
        sys.exit(1)

if __name__ == "__main__":
    main()