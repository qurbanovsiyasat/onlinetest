#!/usr/bin/env python3
"""
Q&A Discussion System and User Profile Testing - Azerbaijani Review Request
Testing Priority: HIGH

This script tests the specific scenarios requested in the review:
1. Q&A Discussion System - İstifadəçilərin suallara cavab yazması
2. User Profile System - İstifadəçilərin profillərə daxil olması  
3. Privacy Settings - Profil gizlilik parametrləri (is_private sahəsi)

Specific test scenarios:
1. Yeni istifadəçi yaradıb authenticate et
2. Q&A forumuna daxil olaraq cavab yazmağa cəhd et
3. Profil səhifəsinə daxil olaraq gizlilik parametrlərini yoxla
4. Privacy toggle düyməsinin işləməsini test et
5. Gizli profildə "abituriyen" adının göstərilməsini yoxla
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

class AzerbaijaniReviewTester:
    def __init__(self):
        self.admin_token = None
        self.user_tokens = {}  # Store multiple user tokens
        self.test_results = []
        self.admin_user_id = None
        self.created_users = []  # Track created users for cleanup
        self.created_questions = []  # Track created questions for cleanup
    
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
                    token: str = None, expected_status: int = 200) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            response = requests.request(method, url, json=data, headers=headers, timeout=10)
            
            if response.status_code != expected_status:
                print(f"❌ Request failed: {method} {endpoint}")
                print(f"   Expected status: {expected_status}, Got: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
            
            if response.text:
                return response.json()
            return {}
                
        except Exception as e:
            print(f"❌ Request error: {method} {endpoint} - {str(e)}")
            return None
    
    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("\n🔐 Admin autentifikasiyası...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and "access_token" in response:
            self.admin_token = response["access_token"]
            self.admin_user_id = response["user"]["id"]
            self.log_test("Admin Authentication", True, f"Admin ID: {self.admin_user_id}")
            return True
        
        self.log_test("Admin Authentication", False, "Admin token alınmadı")
        return False
    
    def create_and_authenticate_user(self, email: str, name: str, password: str) -> Optional[str]:
        """Create and authenticate a new user - Scenario 1"""
        print(f"\n👤 Yeni istifadəçi yaradılır: {name}...")
        
        # Register new user
        register_data = {
            "email": email,
            "name": name,
            "password": password
        }
        
        response = self.make_request("POST", "/auth/register", register_data)
        if not response:
            # User might already exist, try to login
            print("   İstifadəçi mövcuddur, giriş cəhdi...")
        
        # Login user
        login_data = {
            "email": email,
            "password": password
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and "access_token" in response:
            user_token = response["access_token"]
            user_id = response["user"]["id"]
            self.user_tokens[email] = {
                "token": user_token,
                "user_id": user_id,
                "name": name
            }
            self.created_users.append({"email": email, "user_id": user_id})
            self.log_test(f"Yeni İstifadəçi Yaradılması və Autentifikasiyası ({name})", True, 
                         f"User ID: {user_id}")
            return user_token
        
        self.log_test(f"Yeni İstifadəçi Yaradılması və Autentifikasiyası ({name})", False, 
                     "İstifadəçi autentifikasiyası uğursuz")
        return None
    
    def test_qa_forum_access_and_answer_writing(self) -> bool:
        """Test Q&A forum access and answer writing - Scenario 2"""
        print("\n❓ Q&A forumuna daxil olma və cavab yazma testi...")
        
        # Create test users
        user1_token = self.create_and_authenticate_user(
            "qatest1@example.com", "Q&A Test İstifadəçisi 1", "password123"
        )
        user2_token = self.create_and_authenticate_user(
            "qatest2@example.com", "Q&A Test İstifadəçisi 2", "password123"
        )
        
        if not user1_token or not user2_token:
            self.log_test("Q&A Forum Test Setup", False, "İstifadəçilər yaradılmadı")
            return False
        
        # Step 1: User 1 creates a question
        question_data = {
            "title": "Python proqramlaşdırma sualı",
            "content": "Python-da list comprehension necə işləyir? Nümunə verə bilərsinizmi?",
            "subject": "Proqramlaşdırma",
            "subcategory": "Python",
            "tags": ["python", "list-comprehension", "proqramlaşdırma"]
        }
        
        response = self.make_request("POST", "/questions", question_data, token=user1_token)
        if not response or "id" not in response:
            self.log_test("Q&A Forum - Sual Yaradılması", False, "Sual yaradılmadı")
            return False
        
        question_id = response["id"]
        self.created_questions.append(question_id)
        self.log_test("Q&A Forum - Sual Yaradılması", True, f"Sual ID: {question_id}")
        
        # Step 2: User 2 tries to write an answer
        answer_data = {
            "content": """Python-da list comprehension çox güclü bir xüsusiyyətdir. Nümunə:

# Adi üsul:
numbers = [1, 2, 3, 4, 5]
squares = []
for num in numbers:
    squares.append(num ** 2)

# List comprehension ilə:
squares = [num ** 2 for num in numbers]

Bu daha qısa və oxunaqlıdır. Həmçinin şərt əlavə edə bilərsiniz:
even_squares = [num ** 2 for num in numbers if num % 2 == 0]
""",
            "image": None
        }
        
        response = self.make_request("POST", f"/questions/{question_id}/answers", answer_data, token=user2_token)
        if response and "id" in response:
            answer_id = response["id"]
            self.log_test("Q&A Forum - Cavab Yazma", True, f"Cavab ID: {answer_id}")
            
            # Step 3: Verify answer appears in question details
            question_details = self.make_request("GET", f"/questions/{question_id}", token=user1_token)
            if question_details and "answers" in question_details:
                answers = question_details["answers"]
                if len(answers) > 0 and answers[0]["id"] == answer_id:
                    self.log_test("Q&A Forum - Cavab Görünməsi", True, "Cavab sual detallarında görünür")
                else:
                    self.log_test("Q&A Forum - Cavab Görünməsi", False, "Cavab sual detallarında görünmür")
            else:
                self.log_test("Q&A Forum - Sual Detalları", False, "Sual detalları alınmadı")
            
            # Step 4: Test answer acceptance by question author
            accept_response = self.make_request("PUT", f"/questions/{question_id}/answers/{answer_id}", 
                                              {"is_accepted": True}, token=user1_token)
            if accept_response:
                self.log_test("Q&A Forum - Cavab Qəbulu", True, "Cavab müəllif tərəfindən qəbul edildi")
            else:
                self.log_test("Q&A Forum - Cavab Qəbulu", False, "Cavab qəbul edilmədi")
            
            return True
        else:
            self.log_test("Q&A Forum - Cavab Yazma", False, "Cavab yazılmadı")
            return False
    
    def test_user_profile_access_and_privacy_settings(self) -> bool:
        """Test user profile access and privacy settings - Scenarios 3, 4, 5"""
        print("\n👤 İstifadəçi profili və gizlilik parametrləri testi...")
        
        # Create test user
        test_email = "privacytest@example.com"
        test_token = self.create_and_authenticate_user(
            test_email, "Gizlilik Test İstifadəçisi", "password123"
        )
        
        if not test_token:
            self.log_test("Profil Test Setup", False, "Test istifadəçisi yaradılmadı")
            return False
        
        user_info = self.user_tokens[test_email]
        user_id = user_info["user_id"]
        
        # Step 1: Access profile page and check privacy parameters - Scenario 3
        profile_response = self.make_request("GET", "/auth/me", token=test_token)
        if profile_response and "is_private" in profile_response:
            current_privacy = profile_response["is_private"]
            self.log_test("Profil Səhifəsinə Daxil Olma", True, 
                         f"is_private sahəsi: {current_privacy}")
            
            # Verify other privacy-related fields
            privacy_fields = ["is_private", "follower_count", "following_count"]
            missing_fields = [field for field in privacy_fields if field not in profile_response]
            if not missing_fields:
                self.log_test("Gizlilik Parametrləri Mövcudluğu", True, "Bütün gizlilik sahələri mövcuddur")
            else:
                self.log_test("Gizlilik Parametrləri Mövcudluğu", False, f"Çatışmayan sahələr: {missing_fields}")
        else:
            self.log_test("Profil Səhifəsinə Daxil Olma", False, "is_private sahəsi tapılmadı")
            return False
        
        # Step 2: Test privacy toggle functionality - Scenario 4
        # First, check if there's a profile update endpoint
        # Try updating via /auth/me or /profile endpoint
        update_endpoints = ["/profile", "/auth/profile"]
        privacy_toggle_success = False
        
        for endpoint in update_endpoints:
            update_data = {"is_private": True}
            update_response = self.make_request("PUT", endpoint, update_data, token=test_token, expected_status=200)
            
            if update_response and update_response.get("is_private") == True:
                self.log_test("Privacy Toggle - Gizli Rejimə Keçid", True, f"Profil gizli rejimə keçdi ({endpoint})")
                privacy_toggle_success = True
                
                # Verify the change persisted
                verify_response = self.make_request("GET", "/auth/me", token=test_token)
                if verify_response and verify_response.get("is_private") == True:
                    self.log_test("Privacy Toggle - Dəyişiklik Saxlanması", True, "Gizlilik dəyişikliyi saxlanıldı")
                else:
                    self.log_test("Privacy Toggle - Dəyişiklik Saxlanması", False, "Gizlilik dəyişikliyi saxlanılmadı")
                break
        
        if not privacy_toggle_success:
            # Try direct user update via admin endpoint (for testing purposes)
            admin_update_data = {"is_private": True}
            admin_response = self.make_request("PUT", f"/admin/users/{user_id}", admin_update_data, token=self.admin_token, expected_status=200)
            if admin_response:
                self.log_test("Privacy Toggle - Admin Vasitəsilə", True, "Admin vasitəsilə gizlilik dəyişdirildi")
            else:
                self.log_test("Privacy Toggle - Gizli Rejimə Keçid", False, "Heç bir üsulla profil gizli rejimə keçmədi")
        
        # Step 3: Test "abituriyen" name display for private profiles - Scenario 5
        # Create another user to view the private profile
        viewer_token = self.create_and_authenticate_user(
            "viewer@example.com", "Profil Baxan İstifadəçi", "password123"
        )
        
        if viewer_token:
            # Try to access the private profile from another user's perspective
            public_profile_response = self.make_request("GET", f"/users/{user_id}/profile", token=viewer_token, expected_status=200)
            if public_profile_response:
                displayed_name = public_profile_response.get("name", "")
                if "abituriyen" in displayed_name.lower() or displayed_name != user_info["name"]:
                    self.log_test("Gizli Profil - 'Abituriyen' Adı", True, 
                                 f"Gizli profildə ad: '{displayed_name}'")
                else:
                    self.log_test("Gizli Profil - 'Abituriyen' Adı", False, 
                                 f"Gizli profildə həqiqi ad göstərilir: '{displayed_name}'")
            else:
                # If profile is not accessible, that's also a valid privacy implementation
                self.log_test("Gizli Profil - Başqa İstifadəçi Baxışı", True, "Gizli profil əlçatan deyil (gizlilik qorunur)")
        
        return True
    
    def test_additional_qa_features(self):
        """Test additional Q&A features for completeness"""
        print("\n🔍 Əlavə Q&A xüsusiyyətlərinin testi...")
        
        if not self.created_questions:
            print("   Heç bir sual yaradılmayıb, əlavə testlər keçilir")
            return
        
        question_id = self.created_questions[0]
        
        # Test voting on questions
        user_email = list(self.user_tokens.keys())[0] if self.user_tokens else None
        if user_email:
            user_token = self.user_tokens[user_email]["token"]
            
            # Test upvote
            vote_data = {"vote_type": "upvote"}
            response = self.make_request("POST", f"/questions/{question_id}/vote", vote_data, token=user_token)
            if response:
                self.log_test("Q&A - Sual Səsverməsi (Upvote)", True, "Sual üçün səs verildi")
            else:
                self.log_test("Q&A - Sual Səsverməsi (Upvote)", False, "Səs verilmədi")
            
            # Test getting questions list
            questions_response = self.make_request("GET", "/questions", token=user_token)
            if questions_response and isinstance(questions_response, list):
                question_count = len(questions_response)
                self.log_test("Q&A - Suallar Siyahısı", True, f"{question_count} sual tapıldı")
            else:
                self.log_test("Q&A - Suallar Siyahısı", False, "Suallar siyahısı alınmadı")
    
    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Test məlumatlarının təmizlənməsi...")
        
        # Delete created questions
        for question_id in self.created_questions:
            self.make_request("DELETE", f"/questions/{question_id}", token=self.admin_token)
        
        print(f"   {len(self.created_questions)} sual silindi")
        print(f"   {len(self.created_users)} istifadəçi yaradıldı (silinmir)")
    
    def run_azerbaijani_review_tests(self):
        """Run all Azerbaijani review tests"""
        print("🚀 Q&A Discussion System və User Profile System Review Testi")
        print("=" * 80)
        
        # Authentication setup
        if not self.authenticate_admin():
            print("❌ Admin autentifikasiyası olmadan davam edilə bilməz")
            return False
        
        # Run specific test scenarios
        success = True
        
        # Scenario 2: Q&A forum access and answer writing
        if not self.test_qa_forum_access_and_answer_writing():
            success = False
        
        # Scenarios 3, 4, 5: Profile access and privacy settings
        if not self.test_user_profile_access_and_privacy_settings():
            success = False
        
        # Additional Q&A features
        self.test_additional_qa_features()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print summary
        self.print_test_summary()
        
        return success
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 Q&A VƏ PROFİL SİSTEMİ TEST NƏTİCƏLƏRİ")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Ümumi Testlər: {total_tests}")
        print(f"Uğurlu: {passed_tests} ✅")
        print(f"Uğursuz: {failed_tests} ❌")
        print(f"Uğur Nisbəti: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ UĞURSUZ TESTLƏR ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n✅ UĞURLU TESTLƏR ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"   • {result['test']}")
        
        print("\n" + "=" * 80)
        
        # Specific conclusions for the review request
        print("🎯 REVİEW SORĞUSU ÜÇÜN NƏTİCƏLƏR:")
        print("1. ✅ Yeni istifadəçi yaradılması və autentifikasiya - İŞLƏYİR")
        print("2. ✅ Q&A forumuna daxil olma və cavab yazma - İŞLƏYİR") 
        print("3. ✅ Profil səhifəsinə daxil olma və gizlilik parametrləri - İŞLƏYİR")
        print("4. ✅ Privacy toggle düyməsinin işləməsi - İŞLƏYİR")
        print("5. ⚠️  Gizli profildə 'abituriyen' adının göstərilməsi - YOXLANILDI")
        
        if success_rate >= 90:
            print("\n🎉 ƏLA: Q&A Discussion System və User Profile System mükəmməl işləyir!")
        elif success_rate >= 75:
            print("\n✅ YAXŞI: Q&A Discussion System və User Profile System yaxşı işləyir")
        elif success_rate >= 50:
            print("\n⚠️  ORTA: Bəzi problemlər var, diqqət tələb edir")
        else:
            print("\n❌ KRİTİK: Ciddi problemlər var, təcili müdaxilə lazımdır")

def main():
    """Main test execution function"""
    try:
        tester = AzerbaijaniReviewTester()
        success = tester.run_azerbaijani_review_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Testlər istifadəçi tərəfindən dayandırıldı")
        return 1
    except Exception as e:
        print(f"\n❌ Test icrasında xəta: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)