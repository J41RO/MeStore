#!/usr/bin/env python3
"""
Comprehensive Authentication Testing Suite
Tests both API direct calls and frontend login flow
"""
import asyncio
import json
import requests
import sqlite3
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

class AuthenticationTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.db_path = "/home/admin-jairo/MeStore/mestore_production.db"
        self.test_results = []

        # Test credentials from the request
        self.credentials = [
            {"email": "vendor@test.com", "password": "vendor123", "expected_role": "VENDEDOR"},
            {"email": "admin@test.com", "password": "admin123", "expected_role": "ADMIN"},
            {"email": "buyer@test.com", "password": "buyer123", "expected_role": "COMPRADOR"}
        ]

        # Alternative credentials from system file
        self.alt_credentials = [
            {"email": "vendor@mestore.com", "password": "123456", "expected_role": "VENDEDOR"},
            {"email": "admin@mestore.com", "password": "123456", "expected_role": "ADMIN"},
            {"email": "buyer@mestore.com", "password": "123456", "expected_role": "COMPRADOR"}
        ]

    def log_result(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"STATUS: {status}")
        print(f"DETAILS: {json.dumps(details, indent=2)}")
        print(f"{'='*60}")

    def check_database_users(self):
        """Check what users actually exist in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT email, user_type, is_active, is_verified
                FROM users
                ORDER BY user_type, email
            """)

            users = cursor.fetchall()
            conn.close()

            self.log_result(
                "DATABASE_USER_CHECK",
                "SUCCESS",
                {
                    "total_users": len(users),
                    "users": [
                        {
                            "email": user[0],
                            "type": user[1],
                            "active": bool(user[2]),
                            "verified": bool(user[3])
                        } for user in users
                    ]
                }
            )
            return users

        except Exception as e:
            self.log_result(
                "DATABASE_USER_CHECK",
                "FAILED",
                {"error": str(e)}
            )
            return []

    def test_backend_api_login(self, email: str, password: str, expected_role: str):
        """Test direct backend API login"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                headers={"Content-Type": "application/json"},
                json={"email": email, "password": password},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")

                # Get user data by making a call to /auth/me with the token
                user_data = {}
                if token:
                    try:
                        headers = {"Authorization": f"Bearer {token}"}
                        user_response = requests.get(
                            f"{self.backend_url}/api/v1/auth/me",
                            headers=headers,
                            timeout=10
                        )
                        if user_response.status_code == 200:
                            user_data = user_response.json()
                    except:
                        pass

                self.log_result(
                    f"API_LOGIN_{email}",
                    "SUCCESS",
                    {
                        "email": email,
                        "status_code": response.status_code,
                        "has_token": bool(token),
                        "token_preview": token[:50] + "..." if token else None,
                        "user_type": user_data.get("user_type"),
                        "user_id": user_data.get("id"),
                        "expected_role": expected_role,
                        "role_match": user_data.get("user_type") == expected_role,
                        "token_type": data.get("token_type"),
                        "expires_in": data.get("expires_in")
                    }
                )
                return token, user_data
            else:
                self.log_result(
                    f"API_LOGIN_{email}",
                    "FAILED",
                    {
                        "email": email,
                        "status_code": response.status_code,
                        "error": response.text,
                        "expected_role": expected_role
                    }
                )
                return None, None

        except Exception as e:
            self.log_result(
                f"API_LOGIN_{email}",
                "ERROR",
                {
                    "email": email,
                    "error": str(e),
                    "expected_role": expected_role
                }
            )
            return None, None

    def test_protected_endpoint(self, token: str, email: str):
        """Test accessing a protected endpoint with the token"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{self.backend_url}/api/v1/auth/me",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                user_data = response.json()
                self.log_result(
                    f"PROTECTED_ENDPOINT_{email}",
                    "SUCCESS",
                    {
                        "email": email,
                        "status_code": response.status_code,
                        "user_data": user_data
                    }
                )
                return True
            else:
                self.log_result(
                    f"PROTECTED_ENDPOINT_{email}",
                    "FAILED",
                    {
                        "email": email,
                        "status_code": response.status_code,
                        "error": response.text
                    }
                )
                return False

        except Exception as e:
            self.log_result(
                f"PROTECTED_ENDPOINT_{email}",
                "ERROR",
                {
                    "email": email,
                    "error": str(e)
                }
            )
            return False

    def test_frontend_availability(self):
        """Test if frontend is accessible"""
        try:
            response = requests.get(f"{self.frontend_url}/", timeout=10)
            self.log_result(
                "FRONTEND_AVAILABILITY",
                "SUCCESS" if response.status_code == 200 else "FAILED",
                {
                    "status_code": response.status_code,
                    "url": f"{self.frontend_url}/",
                    "accessible": response.status_code == 200
                }
            )
            return response.status_code == 200
        except Exception as e:
            self.log_result(
                "FRONTEND_AVAILABILITY",
                "ERROR",
                {"error": str(e), "url": f"{self.frontend_url}/"}
            )
            return False

    def test_backend_availability(self):
        """Test if backend is accessible"""
        try:
            response = requests.get(f"{self.backend_url}/", timeout=10)
            self.log_result(
                "BACKEND_AVAILABILITY",
                "SUCCESS" if response.status_code == 200 else "FAILED",
                {
                    "status_code": response.status_code,
                    "url": f"{self.backend_url}/",
                    "accessible": response.status_code == 200
                }
            )
            return response.status_code == 200
        except Exception as e:
            self.log_result(
                "BACKEND_AVAILABILITY",
                "ERROR",
                {"error": str(e), "url": f"{self.backend_url}/"}
            )
            return False

    def run_comprehensive_test(self):
        """Run all authentication tests"""
        print(f"\n🔐 COMPREHENSIVE AUTHENTICATION TESTING")
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Start Time: {datetime.now()}")

        # Check service availability
        backend_up = self.test_backend_availability()
        frontend_up = self.test_frontend_availability()

        if not backend_up:
            print("\n❌ Backend is not accessible - aborting tests")
            return False

        # Check database users
        db_users = self.check_database_users()

        # Test primary credentials
        print("\n🧪 Testing Primary Credentials...")
        primary_success = 0
        for cred in self.credentials:
            token, user_data = self.test_backend_api_login(
                cred["email"],
                cred["password"],
                cred["expected_role"]
            )
            if token:
                primary_success += 1
                self.test_protected_endpoint(token, cred["email"])

        # Test alternative credentials if primary failed
        if primary_success == 0:
            print("\n🔄 Primary credentials failed, testing alternative credentials...")
            for cred in self.alt_credentials:
                token, user_data = self.test_backend_api_login(
                    cred["email"],
                    cred["password"],
                    cred["expected_role"]
                )
                if token:
                    self.test_protected_endpoint(token, cred["email"])

        # Summary
        self.generate_summary()
        return True

    def generate_summary(self):
        """Generate test summary"""
        successful_tests = [r for r in self.test_results if r["status"] == "SUCCESS"]
        failed_tests = [r for r in self.test_results if r["status"] == "FAILED"]
        error_tests = [r for r in self.test_results if r["status"] == "ERROR"]

        summary = {
            "total_tests": len(self.test_results),
            "successful": len(successful_tests),
            "failed": len(failed_tests),
            "errors": len(error_tests),
            "success_rate": f"{(len(successful_tests)/len(self.test_results)*100):.1f}%" if self.test_results else "0%",
            "test_timestamp": datetime.now().isoformat()
        }

        print(f"\n{'='*80}")
        print(f"🎯 AUTHENTICATION TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Errors: {summary['errors']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"{'='*80}")

        # Save detailed results
        with open("/home/admin-jairo/MeStore/auth_test_results.json", "w") as f:
            json.dump({
                "summary": summary,
                "detailed_results": self.test_results
            }, f, indent=2)

        print(f"📝 Detailed results saved to: auth_test_results.json")

        return summary

def main():
    """Main test execution"""
    tester = AuthenticationTester()
    success = tester.run_comprehensive_test()

    if not success:
        sys.exit(1)

    # Check if any logins succeeded
    login_tests = [r for r in tester.test_results if "API_LOGIN_" in r["test"] and r["status"] == "SUCCESS"]
    if not login_tests:
        print("\n❌ NO SUCCESSFUL LOGINS - Authentication system may have issues")
        sys.exit(1)
    else:
        print(f"\n✅ {len(login_tests)} successful login(s) detected")

if __name__ == "__main__":
    main()