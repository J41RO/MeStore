"""
Comprehensive API Testing Suite for MeStore Payment Endpoints
==============================================================

Test Coverage:
1. POST /api/v1/payments/process/payu (CREDIT_CARD, PSE, invalid data)
2. POST /api/v1/payments/process/efecty (code generation)
3. POST /api/v1/payments/efecty/confirm (admin only)
4. GET /api/v1/payments/efecty/validate/{payment_code}

Author: API Testing Specialist
Date: 2025-10-01
Purpose: Comprehensive validation of payment integration endpoints
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List


class PaymentAPITester:
    """Comprehensive payment API testing suite"""

    def __init__(self, base_url: str = "http://192.168.1.137:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.token = None
        self.test_results = []

    def log_test(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)

        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"\n{status_symbol} {test_name}: {status}")
        if details.get("error"):
            print(f"   Error: {details['error']}")
        if details.get("response_code"):
            print(f"   HTTP: {details['response_code']}")

    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate and get JWT token"""
        print(f"\n🔐 Authenticating as {email}...")

        try:
            response = requests.post(
                f"{self.api_base}/auth/admin-login",
                json={
                    "email": email,
                    "password": password
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print(f"✅ Authentication successful")
                print(f"   Token: {self.token[:50]}...")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    # ===== TEST 1: PayU CREDIT_CARD Payment =====

    def test_payu_credit_card(self):
        """Test PayU payment with credit card"""
        test_name = "PayU Credit Card Payment"

        # First, we need to create an order
        # For testing purposes, we'll use a mock order_id
        # In real scenario, you'd create an order first

        payload = {
            "order_id": "1",  # Assuming order 1 exists
            "amount": 5000000,  # 50,000.00 COP
            "currency": "COP",
            "payment_method": "CREDIT_CARD",
            "payer_email": "test@example.com",
            "payer_full_name": "Test User",
            "payer_phone": "+573001234567",
            "card_number": "4111111111111111",  # Test Visa card
            "card_expiration_date": "2025/12",
            "card_security_code": "123",
            "card_holder_name": "TEST USER",
            "installments": 1,
            "response_url": "http://localhost:5173/payment-result"
        }

        try:
            response = requests.post(
                f"{self.api_base}/payments/process/payu",
                json=payload,
                headers=self.get_headers(),
                timeout=30
            )

            details = {
                "request": payload,
                "response_code": response.status_code,
                "response_body": response.json() if response.status_code < 500 else response.text
            }

            # Validate response structure
            if response.status_code == 200:
                data = response.json()
                required_fields = ["success", "transaction_id", "state", "gateway"]

                if all(field in data for field in required_fields):
                    self.log_test(test_name, "PASS", details)
                else:
                    details["error"] = f"Missing required fields: {[f for f in required_fields if f not in data]}"
                    self.log_test(test_name, "FAIL", details)
            elif response.status_code == 404:
                # Order not found is expected in test environment
                details["note"] = "Order not found - expected in test environment without existing order"
                self.log_test(test_name, "WARN", details)
            elif response.status_code == 403:
                details["note"] = "Unauthorized - expected if order doesn't belong to user"
                self.log_test(test_name, "WARN", details)
            else:
                details["error"] = f"Unexpected status code: {response.status_code}"
                self.log_test(test_name, "FAIL", details)

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    # ===== TEST 2: PayU PSE Payment =====

    def test_payu_pse(self):
        """Test PayU payment with PSE bank transfer"""
        test_name = "PayU PSE Payment"

        payload = {
            "order_id": "1",
            "amount": 5000000,
            "currency": "COP",
            "payment_method": "PSE",
            "payer_email": "test@example.com",
            "payer_full_name": "Test User",
            "payer_phone": "+573001234567",
            "pse_bank_code": "1007",  # Bancolombia
            "pse_user_type": "N",  # Natural person
            "pse_identification_type": "CC",
            "pse_identification_number": "1234567890",
            "response_url": "http://localhost:5173/payment-result"
        }

        try:
            response = requests.post(
                f"{self.api_base}/payments/process/payu",
                json=payload,
                headers=self.get_headers(),
                timeout=30
            )

            details = {
                "request": payload,
                "response_code": response.status_code,
                "response_body": response.json() if response.status_code < 500 else response.text
            }

            if response.status_code == 200:
                data = response.json()
                # PSE should return payment_url for redirect
                if "payment_url" in data or data.get("state") == "PENDING":
                    self.log_test(test_name, "PASS", details)
                else:
                    details["error"] = "PSE payment should include payment_url or PENDING state"
                    self.log_test(test_name, "FAIL", details)
            elif response.status_code in [404, 403]:
                details["note"] = "Expected error in test environment"
                self.log_test(test_name, "WARN", details)
            else:
                details["error"] = f"Unexpected status code: {response.status_code}"
                self.log_test(test_name, "FAIL", details)

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    # ===== TEST 3: PayU Invalid Data =====

    def test_payu_invalid_data(self):
        """Test PayU payment with invalid data"""
        test_name = "PayU Invalid Data Validation"

        # Missing required card fields
        payload = {
            "order_id": "1",
            "amount": 5000000,
            "currency": "COP",
            "payment_method": "CREDIT_CARD",
            "payer_email": "test@example.com",
            "payer_full_name": "Test User",
            "payer_phone": "+573001234567"
            # Missing card_number, card_expiration_date, etc.
        }

        try:
            response = requests.post(
                f"{self.api_base}/payments/process/payu",
                json=payload,
                headers=self.get_headers(),
                timeout=30
            )

            details = {
                "request": payload,
                "response_code": response.status_code,
                "response_body": response.json() if response.status_code < 500 else response.text
            }

            # Should return 422 for validation error
            if response.status_code == 422:
                self.log_test(test_name, "PASS", details)
            elif response.status_code == 400:
                # Also acceptable for bad request
                details["note"] = "Got 400 instead of 422, still acceptable"
                self.log_test(test_name, "PASS", details)
            else:
                details["error"] = f"Expected 422 validation error, got {response.status_code}"
                self.log_test(test_name, "FAIL", details)

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    # ===== TEST 4: Efecty Code Generation =====

    def test_efecty_code_generation(self):
        """Test Efecty payment code generation"""
        test_name = "Efecty Code Generation"

        payload = {
            "order_id": "1",
            "amount": 5000000,
            "customer_email": "test@example.com",
            "customer_phone": "+573001234567",
            "expiration_hours": 72
        }

        try:
            response = requests.post(
                f"{self.api_base}/payments/process/efecty",
                json=payload,
                headers=self.get_headers(),
                timeout=30
            )

            details = {
                "request": payload,
                "response_code": response.status_code,
                "response_body": response.json() if response.status_code < 500 else response.text
            }

            if response.status_code == 200:
                data = response.json()
                required_fields = ["success", "payment_code", "barcode_data", "expires_at", "instructions"]

                if all(field in data for field in required_fields):
                    # Save payment code for validation test
                    self.efecty_payment_code = data.get("payment_code")
                    details["payment_code"] = self.efecty_payment_code
                    self.log_test(test_name, "PASS", details)
                else:
                    details["error"] = f"Missing fields: {[f for f in required_fields if f not in data]}"
                    self.log_test(test_name, "FAIL", details)
            elif response.status_code in [404, 403]:
                details["note"] = "Expected error in test environment"
                self.log_test(test_name, "WARN", details)
            else:
                details["error"] = f"Unexpected status code: {response.status_code}"
                self.log_test(test_name, "FAIL", details)

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    # ===== TEST 5: Efecty Code Validation =====

    def test_efecty_code_validation(self):
        """Test Efecty payment code validation"""
        test_name = "Efecty Code Validation"

        # Test with a mock payment code
        payment_code = getattr(self, 'efecty_payment_code', 'MST-12345-6789')

        try:
            response = requests.get(
                f"{self.api_base}/payments/efecty/validate/{payment_code}",
                headers=self.get_headers(),
                timeout=30
            )

            details = {
                "payment_code": payment_code,
                "response_code": response.status_code,
                "response_body": response.json() if response.status_code < 500 else response.text
            }

            if response.status_code == 200:
                data = response.json()
                required_fields = ["valid", "payment_code"]

                if all(field in data for field in required_fields):
                    self.log_test(test_name, "PASS", details)
                else:
                    details["error"] = f"Missing fields: {[f for f in required_fields if f not in data]}"
                    self.log_test(test_name, "FAIL", details)
            else:
                details["error"] = f"Unexpected status code: {response.status_code}"
                self.log_test(test_name, "FAIL", details)

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    # ===== TEST 6: Efecty Admin Confirmation =====

    def test_efecty_admin_confirmation(self):
        """Test Efecty payment confirmation (admin only)"""
        test_name = "Efecty Admin Confirmation"

        payment_code = getattr(self, 'efecty_payment_code', 'MST-12345-6789')

        payload = {
            "payment_code": payment_code,
            "paid_amount": 5000000,
            "receipt_number": "EFEC-TEST-123"
        }

        try:
            response = requests.post(
                f"{self.api_base}/payments/efecty/confirm",
                json=payload,
                headers=self.get_headers(),
                timeout=30
            )

            details = {
                "request": payload,
                "response_code": response.status_code,
                "response_body": response.json() if response.status_code < 500 else response.text
            }

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(test_name, "PASS", details)
                else:
                    details["error"] = "Confirmation returned success=false"
                    self.log_test(test_name, "FAIL", details)
            elif response.status_code == 400:
                # Invalid/expired code is expected
                details["note"] = "Invalid or expired code - expected for test code"
                self.log_test(test_name, "WARN", details)
            elif response.status_code == 403:
                details["error"] = "Admin authorization failed - check user is SUPERUSER"
                self.log_test(test_name, "FAIL", details)
            else:
                details["error"] = f"Unexpected status code: {response.status_code}"
                self.log_test(test_name, "FAIL", details)

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    # ===== TEST 7: Authentication Requirements =====

    def test_authentication_requirements(self):
        """Test that endpoints require proper authentication"""
        test_name = "Authentication Requirements"

        # Try accessing endpoint without token
        try:
            response = requests.post(
                f"{self.api_base}/payments/process/payu",
                json={"order_id": "1", "amount": 1000},
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            details = {
                "response_code": response.status_code,
                "response_body": response.text[:200]
            }

            # Should return 401 or 403 for unauthorized
            if response.status_code in [401, 403]:
                self.log_test(test_name, "PASS", details)
            else:
                details["error"] = f"Expected 401/403, got {response.status_code}"
                self.log_test(test_name, "FAIL", details)

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    # ===== GENERATE REPORT =====

    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])

        report = f"""
{'=' * 80}
MESTORE PAYMENT API TEST REPORT
{'=' * 80}

Test Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
API Base URL: {self.api_base}
Test User: admin@mestocker.com

{'=' * 80}
SUMMARY
{'=' * 80}

Total Tests: {total_tests}
✅ Passed: {passed}
❌ Failed: {failed}
⚠️  Warnings: {warnings}

Pass Rate: {(passed/total_tests*100) if total_tests > 0 else 0:.1f}%

{'=' * 80}
DETAILED RESULTS
{'=' * 80}
"""

        for i, result in enumerate(self.test_results, 1):
            status_symbol = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            report += f"\n{i}. {status_symbol} {result['test_name']}\n"
            report += f"   Status: {result['status']}\n"
            report += f"   Timestamp: {result['timestamp']}\n"

            if result["details"].get("response_code"):
                report += f"   HTTP Status: {result['details']['response_code']}\n"

            if result["details"].get("error"):
                report += f"   Error: {result['details']['error']}\n"

            if result["details"].get("note"):
                report += f"   Note: {result['details']['note']}\n"

            if result["details"].get("payment_code"):
                report += f"   Payment Code: {result['details']['payment_code']}\n"

            report += "\n"

        report += f"\n{'=' * 80}\n"
        report += "RECOMMENDATIONS\n"
        report += f"{'=' * 80}\n\n"

        if failed > 0:
            report += "🔴 CRITICAL ISSUES FOUND:\n"
            for result in self.test_results:
                if result["status"] == "FAIL":
                    report += f"   - {result['test_name']}: {result['details'].get('error', 'Unknown error')}\n"
            report += "\n"

        if warnings > 0:
            report += "🟡 WARNINGS:\n"
            for result in self.test_results:
                if result["status"] == "WARN":
                    report += f"   - {result['test_name']}: {result['details'].get('note', 'Check details')}\n"
            report += "\n"

        if passed == total_tests:
            report += "✅ ALL TESTS PASSED - Payment endpoints are functioning correctly!\n\n"

        report += f"{'=' * 80}\n"
        report += "END OF REPORT\n"
        report += f"{'=' * 80}\n"

        return report

    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "=" * 80)
        print("MESTORE PAYMENT API TESTING SUITE")
        print("=" * 80)

        # Authenticate first
        if not self.authenticate("admin@mestocker.com", "Admin123456"):
            print("\n❌ Authentication failed - cannot proceed with tests")
            return

        print("\n🚀 Starting payment endpoint tests...\n")

        # Run all tests
        self.test_authentication_requirements()
        self.test_payu_credit_card()
        self.test_payu_pse()
        self.test_payu_invalid_data()
        self.test_efecty_code_generation()
        self.test_efecty_code_validation()
        self.test_efecty_admin_confirmation()

        # Generate and display report
        print("\n" + "=" * 80)
        print("GENERATING TEST REPORT...")
        print("=" * 80)

        report = self.generate_report()
        print(report)

        return report


def main():
    """Main execution"""
    tester = PaymentAPITester()
    report = tester.run_all_tests()

    # Save report to file
    report_file = "/home/admin-jairo/MeStore/PAYMENT_API_TEST_REPORT.md"
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_file}")

    # Return exit code based on test results
    failed = len([r for r in tester.test_results if r["status"] == "FAIL"])
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
