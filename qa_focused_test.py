#!/usr/bin/env python3
"""
Focused test for the failing Q&A endpoints
"""

import requests
import json

def test_questions_list():
    """Test the questions list endpoint"""
    try:
        response = requests.get("http://localhost:8001/api/questions", timeout=10)
        print(f"Questions List - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_subjects_available():
    """Test the subjects available endpoint"""
    try:
        response = requests.get("http://localhost:8001/api/subjects-available", timeout=10)
        print(f"Subjects Available - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_unauthenticated_question_creation():
    """Test creating question without auth"""
    question_data = {
        "title": "Test Question",
        "content": "This should fail",
        "subject": "Test",
        "tags": ["test"]
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/api/questions",
            json=question_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"Unauthenticated Question Creation - Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code in [401, 403]  # Either is acceptable
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing specific Q&A endpoints...")
    print("=" * 50)
    
    print("\n1. Testing Questions List:")
    test_questions_list()
    
    print("\n2. Testing Subjects Available:")
    test_subjects_available()
    
    print("\n3. Testing Unauthenticated Question Creation:")
    test_unauthenticated_question_creation()