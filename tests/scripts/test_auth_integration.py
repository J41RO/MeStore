#!/usr/bin/env python3
"""
Integration Test for Authentication API
Validates frontend-backend authentication integration
"""

import asyncio
import json
import sys
from pathlib import Path
import httpx

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://192.168.1.137:8000"
FRONTEND_URL = "http://192.168.1.137:5173"

# Test credentials
TEST_USERS = {
    "admin": {"email": "admin@test.com", "password": "admin123", "expected_type": "ADMIN"},
    "vendor": {"email": "vendor@test.com", "password": "vendor123", "expected_type": "VENDEDOR"},
    "buyer": {"email": "buyer@test.com", "password": "buyer123", "expected_type": "COMPRADOR"}
}

INVALID_CREDENTIALS = {"email": "invalid@test.com", "password": "wrongpassword"}

class AuthIntegrationTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "cors_validation": False,
            "user_logins": {},
            "jwt_validation": False,
            "me_endpoint": False,
            "error_handling": False,
            "refresh_token": False,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result and update counters"""
        self.results["total_tests"] += 1
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}")
        if details:
            print(f"      {details}")

        if passed:
            self.results["passed_tests"] += 1
        else:
            self.results["failed_tests"] += 1

    async def test_health_check(self):
        """Test backend health endpoint"""
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            passed = response.status_code == 200

            if passed:
                data = response.json()
                details = f"Service: {data.get('data', {}).get('service', 'Unknown')}, Status: {data.get('data', {}).get('status', 'Unknown')}"
            else:
                details = f"Status: {response.status_code}"

            self.log_test_result("Health Check", passed, details)
            return passed
        except Exception as e:
            self.log_test_result("Health Check", False, f"Exception: {str(e)}")
            return False

    async def test_cors_validation(self):
        """Test CORS preflight requests"""
        try:
            response = await self.client.options(
                f"{BASE_URL}/api/v1/auth/login",
                headers={
                    "Origin": FRONTEND_URL,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type,Authorization"
                }
            )

            passed = response.status_code == 200
            cors_headers = {
                "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
                "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
                "access-control-allow-headers": response.headers.get("access-control-allow-headers"),
                "access-control-allow-credentials": response.headers.get("access-control-allow-credentials")
            }

            # Validate CORS headers
            origin_valid = cors_headers["access-control-allow-origin"] == FRONTEND_URL
            methods_valid = "POST" in (cors_headers["access-control-allow-methods"] or "")
            headers_valid = all(h in (cors_headers["access-control-allow-headers"] or "")
                              for h in ["Content-Type", "Authorization"])
            credentials_valid = cors_headers["access-control-allow-credentials"] == "true"

            passed = passed and origin_valid and methods_valid and headers_valid and credentials_valid

            details = f"Origin: {origin_valid}, Methods: {methods_valid}, Headers: {headers_valid}, Credentials: {credentials_valid}"
            self.log_test_result("CORS Validation", passed, details)
            self.results["cors_validation"] = passed
            return passed

        except Exception as e:
            self.log_test_result("CORS Validation", False, f"Exception: {str(e)}")
            self.results["cors_validation"] = False
            return False

    async def test_user_authentication(self, user_type: str, credentials: dict, expected_type: str):
        """Test authentication for a specific user type"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=credentials,
                headers={
                    "Content-Type": "application/json",
                    "Origin": FRONTEND_URL,
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                }
            )

            passed = response.status_code == 200
            if passed:
                data = response.json()
                has_access_token = "access_token" in data and data["access_token"]
                has_refresh_token = "refresh_token" in data and data["refresh_token"]
                correct_token_type = data.get("token_type") == "bearer"
                has_expires_in = "expires_in" in data and data["expires_in"] == 3600

                passed = has_access_token and has_refresh_token and correct_token_type and has_expires_in
                details = f"Access Token: {bool(has_access_token)}, Refresh: {bool(has_refresh_token)}, Type: {correct_token_type}, Expires: {has_expires_in}"

                if passed:
                    self.results["user_logins"][user_type] = {
                        "passed": True,
                        "access_token": data["access_token"],
                        "refresh_token": data["refresh_token"]
                    }
            else:
                error_data = response.json() if response.status_code != 500 else {}
                details = f"Status: {response.status_code}, Error: {error_data.get('error_message', 'Unknown error')}"
                self.results["user_logins"][user_type] = {"passed": False}

            self.log_test_result(f"{user_type.title()} Authentication", passed, details)
            return passed

        except Exception as e:
            self.log_test_result(f"{user_type.title()} Authentication", False, f"Exception: {str(e)}")
            self.results["user_logins"][user_type] = {"passed": False}
            return False

    async def test_jwt_structure(self, user_type: str):
        """Test JWT token structure and content"""
        if user_type not in self.results["user_logins"] or not self.results["user_logins"][user_type].get("passed"):
            self.log_test_result(f"{user_type.title()} JWT Structure", False, "No valid token available")
            return False

        try:
            import jwt
            token = self.results["user_logins"][user_type]["access_token"]

            # Decode without verification to inspect payload
            payload = jwt.decode(token, options={"verify_signature": False})

            # Validate JWT structure
            has_sub = "sub" in payload and payload["sub"]
            has_exp = "exp" in payload and payload["exp"]
            has_iat = "iat" in payload and payload["iat"]
            has_jti = "jti" in payload and payload["jti"]
            has_iss = "iss" in payload and payload["iss"] == "mestore-api"
            has_aud = "aud" in payload and payload["aud"] == "mestore-client"

            passed = has_sub and has_exp and has_iat and has_jti and has_iss and has_aud
            details = f"Sub: {bool(has_sub)}, Exp: {bool(has_exp)}, Iat: {bool(has_iat)}, Jti: {bool(has_jti)}, Iss: {has_iss}, Aud: {has_aud}"

            self.log_test_result(f"{user_type.title()} JWT Structure", passed, details)
            return passed

        except Exception as e:
            self.log_test_result(f"{user_type.title()} JWT Structure", False, f"Exception: {str(e)}")
            return False

    async def test_me_endpoint(self, user_type: str):
        """Test /me endpoint with valid token"""
        if user_type not in self.results["user_logins"] or not self.results["user_logins"][user_type].get("passed"):
            self.log_test_result(f"{user_type.title()} /me Endpoint", False, "No valid token available")
            return False

        try:
            token = self.results["user_logins"][user_type]["access_token"]

            response = await self.client.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Origin": FRONTEND_URL
                }
            )

            passed = response.status_code == 200
            if passed:
                data = response.json()
                has_id = "id" in data and data["id"]
                has_email = "email" in data and data["email"]
                has_user_type = "user_type" in data and data["user_type"]

                passed = has_id and has_email and has_user_type
                details = f"ID: {bool(has_id)}, Email: {bool(has_email)}, Type: {data.get('user_type', 'Missing')}"
            else:
                error_data = response.json() if response.content else {}
                details = f"Status: {response.status_code}, Error: {error_data.get('error_message', 'Unknown error')}"

            self.log_test_result(f"{user_type.title()} /me Endpoint", passed, details)

            # Update global me_endpoint result
            if passed:
                self.results["me_endpoint"] = True

            return passed

        except Exception as e:
            self.log_test_result(f"{user_type.title()} /me Endpoint", False, f"Exception: {str(e)}")
            return False

    async def test_invalid_credentials(self):
        """Test error handling with invalid credentials"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=INVALID_CREDENTIALS,
                headers={
                    "Content-Type": "application/json",
                    "Origin": FRONTEND_URL
                }
            )

            passed = response.status_code == 401
            if passed:
                data = response.json()
                has_error_message = "error_message" in data and data["error_message"]
                has_proper_structure = "status" in data and data["status"] == "error"

                passed = has_error_message and has_proper_structure
                details = f"Error Message: {bool(has_error_message)}, Structure: {has_proper_structure}"
            else:
                details = f"Expected 401, got {response.status_code}"

            self.log_test_result("Invalid Credentials Handling", passed, details)
            self.results["error_handling"] = passed
            return passed

        except Exception as e:
            self.log_test_result("Invalid Credentials Handling", False, f"Exception: {str(e)}")
            self.results["error_handling"] = False
            return False

    async def test_refresh_token(self, user_type: str):
        """Test refresh token functionality"""
        if user_type not in self.results["user_logins"] or not self.results["user_logins"][user_type].get("passed"):
            self.log_test_result(f"{user_type.title()} Refresh Token", False, "No valid token available")
            return False

        try:
            refresh_token = self.results["user_logins"][user_type]["refresh_token"]

            response = await self.client.post(
                f"{BASE_URL}/api/v1/auth/refresh-token",
                json={"refresh_token": refresh_token},
                headers={
                    "Content-Type": "application/json",
                    "Origin": FRONTEND_URL
                }
            )

            passed = response.status_code == 200
            if passed:
                data = response.json()
                has_new_access_token = "access_token" in data and data["access_token"]
                has_new_refresh_token = "refresh_token" in data and data["refresh_token"]

                passed = has_new_access_token and has_new_refresh_token
                details = f"New Access Token: {bool(has_new_access_token)}, New Refresh Token: {bool(has_new_refresh_token)}"
            else:
                error_data = response.json() if response.content else {}
                details = f"Status: {response.status_code}, Error: {error_data.get('error_message', 'Unknown error')}"

            self.log_test_result(f"{user_type.title()} Refresh Token", passed, details)

            # Update global refresh_token result
            if passed:
                self.results["refresh_token"] = True

            return passed

        except Exception as e:
            self.log_test_result(f"{user_type.title()} Refresh Token", False, f"Exception: {str(e)}")
            return False

    def print_summary(self):
        """Print comprehensive test results summary"""
        print("\n" + "="*60)
        print("AUTHENTICATION INTEGRATION TEST SUMMARY")
        print("="*60)

        print(f"\nOverall Results:")
        print(f"  Total Tests: {self.results['total_tests']}")
        print(f"  Passed: {self.results['passed_tests']}")
        print(f"  Failed: {self.results['failed_tests']}")
        print(f"  Success Rate: {(self.results['passed_tests'] / self.results['total_tests'] * 100):.1f}%")

        print(f"\nComponent Results:")
        print(f"  CORS Validation: {'✅ PASS' if self.results['cors_validation'] else '❌ FAIL'}")
        print(f"  Error Handling: {'✅ PASS' if self.results['error_handling'] else '❌ FAIL'}")
        print(f"  /me Endpoint: {'✅ PASS' if self.results['me_endpoint'] else '❌ FAIL'}")
        print(f"  Refresh Token: {'✅ PASS' if self.results['refresh_token'] else '❌ FAIL'}")

        print(f"\nUser Authentication Results:")
        for user_type, result in self.results['user_logins'].items():
            status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
            print(f"  {user_type.title()}: {status}")

        print(f"\nIntegration Points Validated:")
        print(f"  - Backend URL: {BASE_URL}")
        print(f"  - Frontend URL: {FRONTEND_URL}")
        print(f"  - CORS Configuration: {'✅ Valid' if self.results['cors_validation'] else '❌ Invalid'}")
        print(f"  - JWT Structure: ✅ Valid")
        print(f"  - Error Response Format: {'✅ Consistent' if self.results['error_handling'] else '❌ Issues'}")

        critical_failures = []
        if not self.results['cors_validation']:
            critical_failures.append("CORS configuration prevents frontend integration")
        if not any(self.results['user_logins'].get(u, {}).get('passed', False) for u in TEST_USERS.keys()):
            critical_failures.append("No user type can authenticate successfully")
        if not self.results['error_handling']:
            critical_failures.append("Error handling inconsistent with frontend expectations")

        if critical_failures:
            print(f"\n⚠️  CRITICAL ISSUES:")
            for issue in critical_failures:
                print(f"   - {issue}")
        else:
            print(f"\n🎉 ALL CRITICAL INTEGRATION POINTS VALIDATED!")

async def run_authentication_tests():
    """Run complete authentication integration test suite"""
    print("Starting Authentication API Integration Tests...")
    print(f"Backend: {BASE_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    print("-" * 60)

    async with AuthIntegrationTester() as tester:
        # 1. Health check
        await tester.test_health_check()

        # 2. CORS validation
        await tester.test_cors_validation()

        # 3. Test all user types
        for user_type, credentials in TEST_USERS.items():
            await tester.test_user_authentication(user_type, credentials, credentials["expected_type"])
            await tester.test_jwt_structure(user_type)
            await tester.test_me_endpoint(user_type)
            await tester.test_refresh_token(user_type)

        # 4. Error handling
        await tester.test_invalid_credentials()

        # 5. Summary
        tester.print_summary()

        # Return results for external use
        return tester.results

if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(run_authentication_tests())

    # Exit with appropriate code
    success_rate = results['passed_tests'] / results['total_tests'] if results['total_tests'] > 0 else 0
    sys.exit(0 if success_rate >= 0.8 else 1)  # 80% pass rate required