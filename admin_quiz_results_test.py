#!/usr/bin/env python3
"""
Test script to investigate admin quiz results issue
"""

import requests
import json

# Configuration
BACKEND_URL = "https://107f15dd-a281-4a7c-9f3c-785d2a7cee3f.preview.emergentagent.com"
ADMIN_EMAIL = "admin@onlinetestmaker.com"
ADMIN_PASSWORD = "admin123"

def test_admin_quiz_results():
    """Test admin quiz creation and result submission"""
    
    print("🔍 Testing Admin Quiz Results Issue")
    print("=" * 50)
    
    # Step 1: Admin Login
    print("\n1. Admin Login")
    login_response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if login_response.status_code == 200:
        admin_token = login_response.json()["access_token"]
        print(f"✅ Admin login successful")
        print(f"   Token: {admin_token[:50]}...")
    else:
        print(f"❌ Admin login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Step 2: Create a test quiz
    print("\n2. Creating Test Quiz")
    quiz_data = {
        "title": "Admin Quiz Results Test",
        "description": "Test quiz to check admin-created quiz results",
        "questions": [
            {
                "question_text": "What is 2 + 2?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "3", "is_correct": False},
                    {"text": "4", "is_correct": True},
                    {"text": "5", "is_correct": False}
                ],
                "points": 10,
                "difficulty": "easy"
            },
            {
                "question_text": "What is the capital of France?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "London", "is_correct": False},
                    {"text": "Paris", "is_correct": True},
                    {"text": "Berlin", "is_correct": False}
                ],
                "points": 10,
                "difficulty": "easy"
            }
        ],
        "category": "Test",
        "subject": "Test",
        "subcategory": "Debug",
        "time_limit": 60,
        "is_public": True,
        "is_draft": False
    }
    
    quiz_response = requests.post(
        f"{BACKEND_URL}/api/admin/quiz",
        headers=headers,
        json=quiz_data
    )
    
    if quiz_response.status_code == 200:
        quiz_id = quiz_response.json()["id"]
        print(f"✅ Quiz created successfully")
        print(f"   Quiz ID: {quiz_id}")
        print(f"   Quiz Title: {quiz_response.json()['title']}")
        print(f"   Created By: {quiz_response.json().get('created_by', 'Unknown')}")
        print(f"   Is Draft: {quiz_response.json().get('is_draft', 'Unknown')}")
        
        # Publish the quiz
        if quiz_response.json().get('is_draft', True):
            print("   Publishing quiz...")
            publish_response = requests.post(
                f"{BACKEND_URL}/api/admin/quiz/{quiz_id}/publish",
                headers=headers
            )
            
            if publish_response.status_code == 200:
                print("✅ Quiz published successfully")
            else:
                print(f"❌ Quiz publish failed: {publish_response.status_code}")
                print(f"   Response: {publish_response.text}")
                return
    else:
        print(f"❌ Quiz creation failed: {quiz_response.status_code}")
        print(f"   Response: {quiz_response.text}")
        return
    
    # Step 3: Admin submits their own quiz
    print("\n3. Admin Taking Their Own Quiz")
    
    # First, check if admin can access the quiz
    quiz_access_response = requests.get(
        f"{BACKEND_URL}/api/quiz/{quiz_id}",
        headers=headers
    )
    
    if quiz_access_response.status_code == 200:
        print("✅ Admin can access their own quiz")
    else:
        print(f"❌ Admin cannot access their own quiz: {quiz_access_response.status_code}")
        print(f"   Response: {quiz_access_response.text}")
        return
    
    # Submit quiz attempt
    quiz_answers = ["4", "Paris"]  # Correct answers
    
    attempt_response = requests.post(
        f"{BACKEND_URL}/api/quiz/{quiz_id}/attempt",
        headers=headers,
        json={"quiz_id": quiz_id, "answers": quiz_answers}
    )
    
    if attempt_response.status_code == 200:
        result = attempt_response.json()
        print(f"✅ Quiz submission successful")
        print(f"   Result ID: {result.get('id')}")
        print(f"   Score: {result.get('score', 'N/A')}")
        print(f"   Total Questions: {result.get('total_questions', 'N/A')}")
        print(f"   Percentage: {result.get('percentage', 'N/A'):.1f}%")
        print(f"   Earned Points: {result.get('earned_points', 'N/A')}")
        print(f"   Total Possible Points: {result.get('total_possible_points', 'N/A')}")
        print(f"   Question Results: {len(result.get('question_results', []))} items")
        
        # Check if all expected fields are present
        expected_fields = ['id', 'score', 'total_questions', 'percentage', 'earned_points', 'total_possible_points', 'question_results']
        missing_fields = [field for field in expected_fields if field not in result]
        
        if missing_fields:
            print(f"⚠️  Missing fields in result: {missing_fields}")
        else:
            print("✅ All expected fields present in result")
            
    else:
        print(f"❌ Quiz submission failed: {attempt_response.status_code}")
        print(f"   Response: {attempt_response.text}")
        return
    
    # Step 4: Check quiz statistics
    print("\n4. Checking Quiz Statistics")
    
    # Get quiz details to check updated statistics
    quiz_details_response = requests.get(
        f"{BACKEND_URL}/api/admin/quiz/{quiz_id}",
        headers=headers
    )
    
    if quiz_details_response.status_code == 200:
        quiz_details = quiz_details_response.json()
        print(f"✅ Quiz details retrieved")
        print(f"   Total Attempts: {quiz_details.get('total_attempts', 'N/A')}")
        print(f"   Average Score: {quiz_details.get('average_score', 'N/A')}")
    else:
        print(f"❌ Could not retrieve quiz details: {quiz_details_response.status_code}")
    
    # Step 5: Check admin results view
    print("\n5. Checking Admin Results View")
    
    admin_results_response = requests.get(
        f"{BACKEND_URL}/api/admin/quiz-results",
        headers=headers
    )
    
    if admin_results_response.status_code == 200:
        admin_results = admin_results_response.json()
        print(f"✅ Admin results retrieved")
        print(f"   Total Results: {len(admin_results)}")
        
        # Print first few results for debugging
        for i, result in enumerate(admin_results[:3]):
            print(f"   Result {i+1}:")
            print(f"     Attempt ID: {result.get('attempt_id', 'N/A')}")
            print(f"     User: {result.get('user', {})}")
            print(f"     Quiz: {result.get('quiz', {})}")
            print(f"     Score: {result.get('score', 'N/A')}")
            print(f"     Percentage: {result.get('percentage', 'N/A')}")
            print(f"     Total Questions: {result.get('total_questions', 'N/A')}")
        
        # Find our test result by checking the quiz title
        test_result = None
        for result in admin_results:
            if result.get('quiz', {}).get('title') == 'Admin Quiz Results Test':
                test_result = result
                break
        
        if test_result:
            print(f"✅ Test result found in admin results")
            print(f"   Score: {test_result.get('score', 'N/A')}")
            print(f"   Percentage: {test_result.get('percentage', 'N/A'):.1f}%")
            print(f"   User: {test_result.get('user', {}).get('name', 'N/A')}")
            print(f"   Quiz: {test_result.get('quiz', {}).get('title', 'N/A')}")
        else:
            print(f"❌ Test result NOT found in admin results")
            print(f"   Looking for quiz title: Admin Quiz Results Test")
    else:
        print(f"❌ Could not retrieve admin results: {admin_results_response.status_code}")
        print(f"   Response: {admin_results_response.text}")
    
    # Step 6: Check leaderboard
    print("\n6. Checking Quiz Leaderboard")
    
    leaderboard_response = requests.get(
        f"{BACKEND_URL}/api/quiz/{quiz_id}/results-ranking",
        headers=headers
    )
    
    if leaderboard_response.status_code == 200:
        leaderboard = leaderboard_response.json()
        print(f"✅ Leaderboard retrieved")
        print(f"   Quiz ID being checked: {quiz_id}")
        print(f"   Total Entries: {len(leaderboard.get('ranking', []))}")
        
        # Debug: Show full leaderboard response
        print(f"   Raw leaderboard response: {leaderboard}")
        
        if leaderboard.get('ranking'):
            for idx, entry in enumerate(leaderboard['ranking'][:3]):
                print(f"   #{idx+1}: {entry.get('user_name', 'N/A')} - {entry.get('percentage', 'N/A'):.1f}%")
        
        # Check user's position
        user_position = leaderboard.get('user_position')
        if user_position:
            print(f"   Admin Position: #{user_position.get('position', 'N/A')}")
            percentage = user_position.get('percentage', 'N/A')
            if percentage != 'N/A':
                print(f"   Admin Score: {percentage:.1f}%")
            else:
                print(f"   Admin Score: {percentage}")
        else:
            print("   ❌ Admin position not found in leaderboard")
    else:
        print(f"❌ Could not retrieve leaderboard: {leaderboard_response.status_code}")
        print(f"   Response: {leaderboard_response.text}")
    
    print("\n" + "=" * 50)
    print("🔍 Test Complete")

if __name__ == "__main__":
    test_admin_quiz_results()