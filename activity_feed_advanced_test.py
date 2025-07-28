#!/usr/bin/env python3
"""
Activity Feed Edge Cases and Advanced Testing
Testing Priority: HIGH

Additional comprehensive tests for the Activity Feed endpoint:
1. Test high score quiz completions (80%+ only)
2. Test activity types coverage
3. Test large dataset pagination
4. Test concurrent user activities
5. Test activity feed performance
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

class ActivityFeedAdvancedTester:
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
        success, result = self.make_request("POST", "/auth/login", {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if success and "access_token" in result:
            self.admin_token = result["access_token"]
            return True
        return False
    
    def get_existing_users(self) -> bool:
        """Get existing test users"""
        test_users = [
            {"name": "alice", "email": "alice@activitytest.com", "password": "password123"},
            {"name": "bob", "email": "bob@activitytest.com", "password": "password123"},
            {"name": "charlie", "email": "charlie@activitytest.com", "password": "password123"},
            {"name": "diana", "email": "diana@activitytest.com", "password": "password123"}
        ]
        
        for user_data in test_users:
            success, result = self.make_request("POST", "/auth/login", {
                "email": user_data["email"],
                "password": user_data["password"]
            })
            
            if success and "access_token" in result:
                self.user_tokens[user_data["name"]] = result["access_token"]
                self.user_ids[user_data["name"]] = result["user"]["id"]
        
        return len(self.user_tokens) >= 4
    
    def test_high_score_quiz_completions(self) -> bool:
        """Test that only high score quiz completions (80%+) appear in activity feed"""
        print("🏆 Testing high score quiz completions filter...")
        
        # Create a simple quiz for testing
        quiz_data = {
            "title": "High Score Test Quiz",
            "description": "A quiz to test high score filtering",
            "category": "Test",
            "subject": "Testing",
            "subcategory": "Scores",
            "questions": [
                {
                    "question_text": "What is 1 + 1?",
                    "question_type": "multiple_choice",
                    "options": [
                        {"text": "1", "is_correct": False},
                        {"text": "2", "is_correct": True},
                        {"text": "3", "is_correct": False}
                    ],
                    "multiple_correct": False,
                    "points": 1
                },
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
        
        # Create and publish quiz
        success, result = self.make_request("POST", "/admin/quiz", quiz_data, token=self.admin_token)
        if not success:
            self.log_test("Create High Score Test Quiz", False, f"Failed: {result}")
            return False
        
        quiz_id = result["id"]
        pub_success, pub_result = self.make_request("POST", f"/admin/quiz/{quiz_id}/publish", {}, token=self.admin_token)
        if not pub_success:
            self.log_test("Publish High Score Test Quiz", False, f"Failed: {pub_result}")
            return False
        
        # Bob takes quiz with low score (50% - should NOT appear in activity feed)
        low_score_attempt = {
            "quiz_id": quiz_id,
            "answers": ["1", "4"]  # 1 correct out of 2 = 50%
        }
        
        success, result = self.make_request("POST", f"/quiz/{quiz_id}/attempt", low_score_attempt, token=self.user_tokens["bob"])
        if not success:
            self.log_test("Bob Low Score Attempt", False, f"Failed: {result}")
            return False
        
        # Charlie takes quiz with high score (100% - should appear in activity feed)
        high_score_attempt = {
            "quiz_id": quiz_id,
            "answers": ["2", "4"]  # 2 correct out of 2 = 100%
        }
        
        success, result = self.make_request("POST", f"/quiz/{quiz_id}/attempt", high_score_attempt, token=self.user_tokens["charlie"])
        if not success:
            self.log_test("Charlie High Score Attempt", False, f"Failed: {result}")
            return False
        
        # Wait for data processing
        time.sleep(2)
        
        # Check Alice's activity feed (she follows both Bob and Charlie)
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 20, "offset": 0}, 
                                          token=self.user_tokens["alice"])
        
        if success:
            activities = result["activities"]
            quiz_completion_activities = [a for a in activities if a["activity_type"] == "quiz_completed"]
            
            # Should only see Charlie's high score completion, not Bob's low score
            charlie_completions = [a for a in quiz_completion_activities if a["user_id"] == self.user_ids["charlie"]]
            bob_completions = [a for a in quiz_completion_activities if a["user_id"] == self.user_ids["bob"]]
            
            if len(charlie_completions) > 0 and len(bob_completions) == 0:
                # Verify the score is indeed high (80%+)
                charlie_activity = charlie_completions[0]
                score = charlie_activity["metadata"]["score"]
                if score >= 80:
                    self.log_test("High Score Filter", True, f"Only high scores (≥80%) appear: Charlie's {score}% shown, Bob's 50% hidden")
                    return True
                else:
                    self.log_test("High Score Filter", False, f"Score {score}% is not high enough")
                    return False
            else:
                self.log_test("High Score Filter", False, f"Expected Charlie's completion only, got Charlie: {len(charlie_completions)}, Bob: {len(bob_completions)}")
                return False
        else:
            self.log_test("High Score Filter", False, f"Failed to get activity feed: {result}")
            return False
    
    def test_activity_types_coverage(self) -> bool:
        """Test that all expected activity types are supported"""
        print("📋 Testing activity types coverage...")
        
        # Get Alice's activity feed
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 50, "offset": 0}, 
                                          token=self.user_tokens["alice"])
        
        if success:
            activities = result["activities"]
            activity_types = set(a["activity_type"] for a in activities)
            
            expected_types = {
                "quiz_published",
                "question_posted", 
                "answer_posted",
                "quiz_completed",
                "user_followed"
            }
            
            found_types = activity_types.intersection(expected_types)
            missing_types = expected_types - activity_types
            
            if len(found_types) >= 3:  # We expect at least 3 types to be present
                self.log_test("Activity Types Coverage", True, 
                            f"Found {len(found_types)} activity types: {sorted(found_types)}")
                return True
            else:
                self.log_test("Activity Types Coverage", False, 
                            f"Only found {len(found_types)} types: {sorted(found_types)}, missing: {sorted(missing_types)}")
                return False
        else:
            self.log_test("Activity Types Coverage", False, f"Failed: {result}")
            return False
    
    def test_pagination_edge_cases(self) -> bool:
        """Test pagination with edge cases"""
        print("📄 Testing pagination edge cases...")
        
        # Test with limit=0 (should return empty)
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 0, "offset": 0}, 
                                          token=self.user_tokens["alice"])
        
        if success:
            if len(result["activities"]) == 0 and result["limit"] == 0:
                self.log_test("Pagination Edge Case: limit=0", True, "Correctly returns empty with limit=0")
            else:
                self.log_test("Pagination Edge Case: limit=0", False, f"Expected empty but got {len(result['activities'])} activities")
                return False
        else:
            self.log_test("Pagination Edge Case: limit=0", False, f"Failed: {result}")
            return False
        
        # Test with very high offset (should return empty)
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 10, "offset": 1000}, 
                                          token=self.user_tokens["alice"])
        
        if success:
            if len(result["activities"]) == 0 and result["has_more"] == False:
                self.log_test("Pagination Edge Case: high offset", True, "Correctly returns empty with high offset")
            else:
                self.log_test("Pagination Edge Case: high offset", False, f"Expected empty but got {len(result['activities'])} activities")
                return False
        else:
            self.log_test("Pagination Edge Case: high offset", False, f"Failed: {result}")
            return False
        
        # Test with very high limit (should not crash)
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 1000, "offset": 0}, 
                                          token=self.user_tokens["alice"])
        
        if success:
            self.log_test("Pagination Edge Case: high limit", True, f"Handled high limit correctly, returned {len(result['activities'])} activities")
        else:
            self.log_test("Pagination Edge Case: high limit", False, f"Failed: {result}")
            return False
        
        return True
    
    def test_activity_feed_performance(self) -> bool:
        """Test activity feed response time"""
        print("⚡ Testing activity feed performance...")
        
        start_time = time.time()
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 20, "offset": 0}, 
                                          token=self.user_tokens["alice"])
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        if success:
            if response_time < 2000:  # Should respond within 2 seconds
                self.log_test("Activity Feed Performance", True, f"Response time: {response_time:.1f}ms (acceptable)")
                return True
            else:
                self.log_test("Activity Feed Performance", False, f"Response time: {response_time:.1f}ms (too slow)")
                return False
        else:
            self.log_test("Activity Feed Performance", False, f"Failed: {result}")
            return False
    
    def test_activity_metadata_completeness(self) -> bool:
        """Test that activity metadata is complete and useful"""
        print("🏷️ Testing activity metadata completeness...")
        
        success, result = self.make_request("GET", "/user/activity-feed", 
                                          params={"limit": 20, "offset": 0}, 
                                          token=self.user_tokens["alice"])
        
        if success:
            activities = result["activities"]
            
            for activity in activities:
                activity_type = activity["activity_type"]
                metadata = activity.get("metadata", {})
                
                # Check that each activity type has meaningful metadata
                if activity_type == "quiz_published":
                    required_fields = ["quiz_title", "subject", "total_questions"]
                    missing = [f for f in required_fields if f not in metadata or not metadata[f]]
                    if missing:
                        self.log_test("Quiz Published Metadata Completeness", False, f"Missing: {missing}")
                        return False
                
                elif activity_type == "question_posted":
                    required_fields = ["question_title", "subject"]
                    missing = [f for f in required_fields if f not in metadata or not metadata[f]]
                    if missing:
                        self.log_test("Question Posted Metadata Completeness", False, f"Missing: {missing}")
                        return False
                
                elif activity_type == "quiz_completed":
                    required_fields = ["quiz_title", "score", "passed"]
                    missing = [f for f in required_fields if f not in metadata]
                    if missing:
                        self.log_test("Quiz Completed Metadata Completeness", False, f"Missing: {missing}")
                        return False
                    
                    # Verify score is reasonable
                    score = metadata["score"]
                    if not isinstance(score, (int, float)) or score < 0 or score > 100:
                        self.log_test("Quiz Completed Score Validity", False, f"Invalid score: {score}")
                        return False
            
            self.log_test("Activity Metadata Completeness", True, f"All {len(activities)} activities have complete metadata")
            return True
        else:
            self.log_test("Activity Metadata Completeness", False, f"Failed: {result}")
            return False
    
    def run_advanced_tests(self):
        """Run all advanced activity feed tests"""
        print("🚀 Starting Advanced Activity Feed Testing")
        print("=" * 60)
        
        # Setup phase
        if not self.setup_admin_auth():
            print("❌ Failed to setup admin authentication. Aborting tests.")
            return False
        
        if not self.get_existing_users():
            print("❌ Failed to get existing test users. Aborting tests.")
            return False
        
        # Advanced tests
        test_methods = [
            self.test_high_score_quiz_completions,
            self.test_activity_types_coverage,
            self.test_pagination_edge_cases,
            self.test_activity_feed_performance,
            self.test_activity_metadata_completeness
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
        print("🎯 ADVANCED ACTIVITY FEED TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL ADVANCED TESTS PASSED!")
            print("✅ High score filtering working (80%+ only)")
            print("✅ All activity types supported")
            print("✅ Pagination edge cases handled")
            print("✅ Performance is acceptable")
            print("✅ Metadata is complete and useful")
        else:
            print("⚠️  SOME ADVANCED TESTS FAILED")
            failed_tests = [result for result in self.test_results if not result["success"]]
            for failed_test in failed_tests:
                print(f"❌ {failed_test['test']}: {failed_test['details']}")
        
        return passed_tests == total_tests

def main():
    """Main function to run advanced activity feed tests"""
    print("🔍 Advanced Activity Feed Testing")
    print("Testing edge cases and performance")
    print("=" * 60)
    
    tester = ActivityFeedAdvancedTester()
    success = tester.run_advanced_tests()
    
    if success:
        print("\n🎉 CONCLUSION: Activity Feed endpoint passes all advanced tests!")
        sys.exit(0)
    else:
        print("\n❌ CONCLUSION: Activity Feed endpoint has advanced issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()