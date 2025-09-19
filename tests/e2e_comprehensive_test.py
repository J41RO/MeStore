#!/usr/bin/env python3
"""
MeStore E2E Testing Suite
Comprehensive End-to-End Testing for Complete User Journeys
"""

import asyncio
import json
import time
import requests
import pytest
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result container"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration: float
    details: Dict[str, Any]
    errors: List[str]
    screenshots: List[str]

@dataclass
class UserPersona:
    """User persona for testing"""
    role: str
    email: str
    password: str
    first_name: str
    last_name: str
    expected_redirect: str

class E2ETestSuite:
    """Comprehensive E2E Testing Suite for MeStore"""

    def __init__(self, base_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:5173"):
        self.base_url = base_url
        self.frontend_url = frontend_url
        self.session = requests.Session()
        self.test_results: List[TestResult] = []
        self.test_data = self._load_test_data()

        # Test user personas
        self.personas = {
            "admin": UserPersona(
                role="admin",
                email="admin@test.com",
                password="admin123",
                first_name="Admin",
                last_name="User",
                expected_redirect="/admin"
            ),
            "vendor": UserPersona(
                role="vendor",
                email="vendor@test.com",
                password="vendor123",
                first_name="Vendor",
                last_name="Test",
                expected_redirect="/vendor/dashboard"
            ),
            "buyer": UserPersona(
                role="buyer",
                email="buyer@test.com",
                password="buyer123",
                first_name="Buyer",
                last_name="Customer",
                expected_redirect="/buyer/dashboard"
            )
        }

    def _load_test_data(self) -> Dict[str, Any]:
        """Load test data and configuration"""
        return {
            "test_products": [
                {
                    "name": "Test Canvas Product",
                    "description": "A test product for Canvas visualization",
                    "price": 99.99,
                    "stock": 50,
                    "category": "Electronics",
                    "sku": "TEST-CANVAS-001"
                },
                {
                    "name": "E2E Test Product",
                    "description": "Product for end-to-end testing",
                    "price": 149.99,
                    "stock": 25,
                    "category": "Home & Garden",
                    "sku": "E2E-TEST-002"
                }
            ],
            "test_orders": [
                {
                    "product_sku": "TEST-CANVAS-001",
                    "quantity": 2,
                    "shipping_address": {
                        "street": "123 Test St",
                        "city": "Test City",
                        "state": "TC",
                        "zip": "12345",
                        "country": "Colombia"
                    }
                }
            ]
        }

    def _record_test_result(self, test_name: str, status: str, duration: float,
                          details: Dict[str, Any], errors: List[str] = None,
                          screenshots: List[str] = None):
        """Record test result"""
        result = TestResult(
            test_name=test_name,
            status=status,
            duration=duration,
            details=details,
            errors=errors or [],
            screenshots=screenshots or []
        )
        self.test_results.append(result)
        logger.info(f"Test '{test_name}': {status} ({duration:.2f}s)")

    def check_service_health(self) -> bool:
        """Check if backend and frontend services are running"""
        try:
            # Check backend health
            backend_response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            backend_healthy = backend_response.status_code == 200

            # Check frontend (basic connectivity)
            frontend_response = requests.get(self.frontend_url, timeout=5)
            frontend_healthy = frontend_response.status_code == 200

            return backend_healthy and frontend_healthy
        except Exception as e:
            logger.error(f"Service health check failed: {e}")
            return False

    def authenticate_user(self, persona: UserPersona) -> Optional[str]:
        """Authenticate user and return access token"""
        try:
            auth_data = {
                "username": persona.email,
                "password": persona.password
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {access_token}"})
                return access_token
            else:
                logger.error(f"Authentication failed for {persona.email}: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Authentication error for {persona.email}: {e}")
            return None

    def test_user_registration_journey(self) -> TestResult:
        """Test complete user registration journey"""
        start_time = time.time()
        test_name = "User Registration Journey"
        errors = []
        details = {}

        try:
            # Test buyer registration
            registration_data = {
                "email": f"newbuyer_{int(time.time())}@test.com",
                "password": "testpass123",
                "first_name": "New",
                "last_name": "Buyer",
                "role": "buyer"
            }

            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json=registration_data
            )

            details["registration_status"] = response.status_code
            details["registration_response"] = response.text[:500]

            if response.status_code != 201:
                errors.append(f"Registration failed: {response.text}")

            # Test vendor registration
            vendor_data = {
                "email": f"newvendor_{int(time.time())}@test.com",
                "password": "testpass123",
                "first_name": "New",
                "last_name": "Vendor",
                "role": "vendor",
                "business_name": "Test Business",
                "business_type": "retail"
            }

            vendor_response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json=vendor_data
            )

            details["vendor_registration_status"] = vendor_response.status_code
            details["vendor_registration_response"] = vendor_response.text[:500]

            if vendor_response.status_code != 201:
                errors.append(f"Vendor registration failed: {vendor_response.text}")

        except Exception as e:
            errors.append(f"Registration journey error: {str(e)}")

        duration = time.time() - start_time
        status = "PASS" if not errors else "FAIL"

        self._record_test_result(test_name, status, duration, details, errors)
        return self.test_results[-1]

    def test_vendor_complete_journey(self) -> TestResult:
        """Test complete vendor journey from login to product management"""
        start_time = time.time()
        test_name = "Vendor Complete Journey"
        errors = []
        details = {}

        try:
            # 1. Vendor Authentication
            vendor = self.personas["vendor"]
            token = self.authenticate_user(vendor)

            if not token:
                errors.append("Vendor authentication failed")

            details["authentication"] = "SUCCESS" if token else "FAILED"

            # 2. Access Vendor Dashboard
            dashboard_response = self.session.get(f"{self.base_url}/api/v1/vendor/dashboard")
            details["dashboard_access"] = dashboard_response.status_code

            if dashboard_response.status_code != 200:
                errors.append(f"Dashboard access failed: {dashboard_response.text}")

            # 3. Create Product
            product_data = self.test_data["test_products"][0].copy()
            product_data["sku"] = f"VENDOR-TEST-{int(time.time())}"

            product_response = self.session.post(
                f"{self.base_url}/api/v1/vendor/products",
                json=product_data
            )

            details["product_creation"] = product_response.status_code

            if product_response.status_code in [200, 201]:
                product_id = product_response.json().get("id")
                details["product_id"] = product_id

                # 4. Update Product
                update_data = {"price": 199.99}
                update_response = self.session.put(
                    f"{self.base_url}/api/v1/vendor/products/{product_id}",
                    json=update_data
                )
                details["product_update"] = update_response.status_code

                # 5. Check Inventory
                inventory_response = self.session.get(
                    f"{self.base_url}/api/v1/vendor/inventory"
                )
                details["inventory_check"] = inventory_response.status_code

            else:
                errors.append(f"Product creation failed: {product_response.text}")

            # 6. Check Analytics
            analytics_response = self.session.get(f"{self.base_url}/api/v1/vendor/analytics")
            details["analytics_access"] = analytics_response.status_code

        except Exception as e:
            errors.append(f"Vendor journey error: {str(e)}")

        duration = time.time() - start_time
        status = "PASS" if not errors else "FAIL"

        self._record_test_result(test_name, status, duration, details, errors)
        return self.test_results[-1]

    def test_customer_purchase_journey(self) -> TestResult:
        """Test complete customer purchase journey"""
        start_time = time.time()
        test_name = "Customer Purchase Journey"
        errors = []
        details = {}

        try:
            # 1. Customer Authentication
            buyer = self.personas["buyer"]
            token = self.authenticate_user(buyer)

            details["authentication"] = "SUCCESS" if token else "FAILED"

            # 2. Product Discovery
            search_response = self.session.get(
                f"{self.base_url}/api/v1/products/search?q=test"
            )
            details["product_search"] = search_response.status_code

            if search_response.status_code == 200:
                products = search_response.json().get("products", [])
                details["products_found"] = len(products)

                if products:
                    product_id = products[0]["id"]

                    # 3. Product Detail View
                    detail_response = self.session.get(
                        f"{self.base_url}/api/v1/products/{product_id}"
                    )
                    details["product_detail"] = detail_response.status_code

                    # 4. Add to Cart
                    cart_data = {
                        "product_id": product_id,
                        "quantity": 1
                    }
                    cart_response = self.session.post(
                        f"{self.base_url}/api/v1/buyer/cart/add",
                        json=cart_data
                    )
                    details["add_to_cart"] = cart_response.status_code

                    # 5. View Cart
                    view_cart_response = self.session.get(
                        f"{self.base_url}/api/v1/buyer/cart"
                    )
                    details["view_cart"] = view_cart_response.status_code

                    # 6. Checkout Process
                    checkout_data = {
                        "shipping_address": self.test_data["test_orders"][0]["shipping_address"],
                        "payment_method": "credit_card"
                    }
                    checkout_response = self.session.post(
                        f"{self.base_url}/api/v1/buyer/checkout",
                        json=checkout_data
                    )
                    details["checkout"] = checkout_response.status_code

                    if checkout_response.status_code in [200, 201]:
                        order_data = checkout_response.json()
                        order_id = order_data.get("order_id")
                        details["order_id"] = order_id

                        # 7. Order Tracking
                        if order_id:
                            tracking_response = self.session.get(
                                f"{self.base_url}/api/v1/buyer/orders/{order_id}"
                            )
                            details["order_tracking"] = tracking_response.status_code
                    else:
                        errors.append(f"Checkout failed: {checkout_response.text}")

                else:
                    errors.append("No products found for purchase journey")
            else:
                errors.append(f"Product search failed: {search_response.text}")

        except Exception as e:
            errors.append(f"Customer journey error: {str(e)}")

        duration = time.time() - start_time
        status = "PASS" if not errors else "FAIL"

        self._record_test_result(test_name, status, duration, details, errors)
        return self.test_results[-1]

    def test_admin_management_journey(self) -> TestResult:
        """Test complete admin management workflow"""
        start_time = time.time()
        test_name = "Admin Management Journey"
        errors = []
        details = {}

        try:
            # 1. Admin Authentication
            admin = self.personas["admin"]
            token = self.authenticate_user(admin)

            details["authentication"] = "SUCCESS" if token else "FAILED"

            if not token:
                errors.append("Admin authentication failed")

            # 2. User Management
            users_response = self.session.get(f"{self.base_url}/api/v1/admin/users")
            details["user_management"] = users_response.status_code

            # 3. Vendor Management
            vendors_response = self.session.get(f"{self.base_url}/api/v1/admin/vendors")
            details["vendor_management"] = vendors_response.status_code

            # 4. Commission Management
            commissions_response = self.session.get(f"{self.base_url}/api/v1/admin/commissions")
            details["commission_management"] = commissions_response.status_code

            # 5. System Analytics
            analytics_response = self.session.get(f"{self.base_url}/api/v1/admin/analytics")
            details["system_analytics"] = analytics_response.status_code

            # 6. Platform Configuration
            config_response = self.session.get(f"{self.base_url}/api/v1/admin/settings")
            details["platform_config"] = config_response.status_code

            # 7. Audit Logs
            audit_response = self.session.get(f"{self.base_url}/api/v1/admin/audit-logs")
            details["audit_logs"] = audit_response.status_code

        except Exception as e:
            errors.append(f"Admin journey error: {str(e)}")

        duration = time.time() - start_time
        status = "PASS" if not errors else "FAIL"

        self._record_test_result(test_name, status, duration, details, errors)
        return self.test_results[-1]

    def test_performance_metrics(self) -> TestResult:
        """Test performance metrics across the platform"""
        start_time = time.time()
        test_name = "Performance Metrics Validation"
        errors = []
        details = {}

        try:
            performance_thresholds = {
                "api_response_time": 2.0,  # seconds
                "page_load_time": 3.0,     # seconds
                "database_query_time": 1.0  # seconds
            }

            # Test API response times
            api_endpoints = [
                "/api/v1/health",
                "/api/v1/products/search?q=test",
                "/api/v1/auth/me",
                "/api/v1/vendor/dashboard",
                "/api/v1/buyer/cart"
            ]

            api_times = []
            for endpoint in api_endpoints:
                endpoint_start = time.time()
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    endpoint_time = time.time() - endpoint_start
                    api_times.append(endpoint_time)
                    details[f"api_time_{endpoint.replace('/', '_')}"] = endpoint_time

                    if endpoint_time > performance_thresholds["api_response_time"]:
                        errors.append(f"API {endpoint} exceeded threshold: {endpoint_time:.2f}s")

                except Exception as e:
                    errors.append(f"Performance test failed for {endpoint}: {str(e)}")

            details["avg_api_response_time"] = sum(api_times) / len(api_times) if api_times else 0
            details["max_api_response_time"] = max(api_times) if api_times else 0

            # Test concurrent requests
            concurrent_start = time.time()
            concurrent_responses = []

            import threading

            def make_request():
                try:
                    resp = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
                    concurrent_responses.append(resp.status_code)
                except Exception as e:
                    concurrent_responses.append(f"Error: {e}")

            threads = []
            for _ in range(10):  # 10 concurrent requests
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            concurrent_time = time.time() - concurrent_start
            details["concurrent_requests_time"] = concurrent_time
            details["concurrent_success_rate"] = len([r for r in concurrent_responses if r == 200]) / len(concurrent_responses)

        except Exception as e:
            errors.append(f"Performance testing error: {str(e)}")

        duration = time.time() - start_time
        status = "PASS" if not errors else "FAIL"

        self._record_test_result(test_name, status, duration, details, errors)
        return self.test_results[-1]

    def test_error_handling_scenarios(self) -> TestResult:
        """Test error handling and recovery scenarios"""
        start_time = time.time()
        test_name = "Error Handling Scenarios"
        errors = []
        details = {}

        try:
            # Test authentication with invalid credentials
            invalid_auth = {
                "username": "invalid@test.com",
                "password": "wrongpassword"
            }

            auth_response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                data=invalid_auth,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            details["invalid_auth_status"] = auth_response.status_code

            if auth_response.status_code != 401:
                errors.append(f"Invalid auth should return 401, got {auth_response.status_code}")

            # Test access to protected endpoint without token
            protected_response = requests.get(f"{self.base_url}/api/v1/vendor/dashboard")
            details["no_token_status"] = protected_response.status_code

            if protected_response.status_code != 401:
                errors.append(f"Protected endpoint should return 401, got {protected_response.status_code}")

            # Test malformed requests
            malformed_response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json={"invalid": "data"}
            )
            details["malformed_request_status"] = malformed_response.status_code

            if malformed_response.status_code not in [400, 422]:
                errors.append(f"Malformed request should return 400/422, got {malformed_response.status_code}")

            # Test non-existent resources
            not_found_response = requests.get(f"{self.base_url}/api/v1/products/999999")
            details["not_found_status"] = not_found_response.status_code

            if not_found_response.status_code != 404:
                errors.append(f"Non-existent resource should return 404, got {not_found_response.status_code}")

        except Exception as e:
            errors.append(f"Error handling test error: {str(e)}")

        duration = time.time() - start_time
        status = "PASS" if not errors else "FAIL"

        self._record_test_result(test_name, status, duration, details, errors)
        return self.test_results[-1]

    def test_security_validation(self) -> TestResult:
        """Test security measures and validation"""
        start_time = time.time()
        test_name = "Security Validation"
        errors = []
        details = {}

        try:
            # Test SQL injection attempts
            sql_injection_payloads = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "1; DELETE FROM products WHERE 1=1; --"
            ]

            for payload in sql_injection_payloads:
                search_response = requests.get(
                    f"{self.base_url}/api/v1/products/search",
                    params={"q": payload}
                )
                details[f"sql_injection_{payload[:10]}"] = search_response.status_code

                # Should handle gracefully, not crash
                if search_response.status_code == 500:
                    errors.append(f"SQL injection payload caused server error: {payload}")

            # Test XSS attempts
            xss_payloads = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>"
            ]

            for payload in xss_payloads:
                # Test in search
                xss_response = requests.get(
                    f"{self.base_url}/api/v1/products/search",
                    params={"q": payload}
                )
                details[f"xss_test_{payload[:10]}"] = xss_response.status_code

                # Response should not contain unescaped payload
                if payload in xss_response.text:
                    errors.append(f"XSS payload not properly escaped: {payload}")

            # Test rate limiting (if implemented)
            rate_limit_responses = []
            for i in range(20):  # Make rapid requests
                resp = requests.get(f"{self.base_url}/api/v1/health")
                rate_limit_responses.append(resp.status_code)

            # Check if rate limiting kicks in
            rate_limited = any(status == 429 for status in rate_limit_responses)
            details["rate_limiting_active"] = rate_limited

        except Exception as e:
            errors.append(f"Security validation error: {str(e)}")

        duration = time.time() - start_time
        status = "PASS" if not errors else "FAIL"

        self._record_test_result(test_name, status, duration, details, errors)
        return self.test_results[-1]

    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run the complete E2E test suite"""
        logger.info("Starting MeStore Comprehensive E2E Test Suite")

        # Check service health first
        if not self.check_service_health():
            logger.error("Services are not healthy. Cannot proceed with testing.")
            return {
                "status": "ABORTED",
                "reason": "Services not healthy",
                "timestamp": datetime.now().isoformat()
            }

        # Run all test scenarios
        test_scenarios = [
            self.test_user_registration_journey,
            self.test_vendor_complete_journey,
            self.test_customer_purchase_journey,
            self.test_admin_management_journey,
            self.test_performance_metrics,
            self.test_error_handling_scenarios,
            self.test_security_validation
        ]

        suite_start_time = time.time()

        for test_scenario in test_scenarios:
            try:
                test_scenario()
            except Exception as e:
                logger.error(f"Test scenario failed: {e}")
                self._record_test_result(
                    test_scenario.__name__,
                    "FAIL",
                    0,
                    {},
                    [f"Test execution error: {str(e)}"]
                )

        suite_duration = time.time() - suite_start_time

        # Generate test report
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])

        report = {
            "timestamp": datetime.now().isoformat(),
            "suite_duration": suite_duration,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "duration": r.duration,
                    "details": r.details,
                    "errors": r.errors
                } for r in self.test_results
            ]
        }

        return report

    def generate_detailed_report(self, report: Dict[str, Any]) -> str:
        """Generate detailed HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MeStore E2E Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2563eb; color: white; padding: 20px; border-radius: 8px; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                .metric {{ background: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; }}
                .test-result {{ margin: 15px 0; padding: 15px; border-radius: 8px; }}
                .pass {{ background: #d1fae5; border-left: 4px solid #10b981; }}
                .fail {{ background: #fee2e2; border-left: 4px solid #ef4444; }}
                .details {{ margin-top: 10px; font-size: 0.9em; color: #6b7280; }}
                .error {{ color: #dc2626; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MeStore E2E Test Report</h1>
                <p>Generated on: {report['timestamp']}</p>
            </div>

            <div class="summary">
                <div class="metric">
                    <h3>Total Tests</h3>
                    <p style="font-size: 2em; margin: 0;">{report['total_tests']}</p>
                </div>
                <div class="metric">
                    <h3>Passed</h3>
                    <p style="font-size: 2em; margin: 0; color: #10b981;">{report['passed_tests']}</p>
                </div>
                <div class="metric">
                    <h3>Failed</h3>
                    <p style="font-size: 2em; margin: 0; color: #ef4444;">{report['failed_tests']}</p>
                </div>
                <div class="metric">
                    <h3>Success Rate</h3>
                    <p style="font-size: 2em; margin: 0;">{report['success_rate']:.1f}%</p>
                </div>
                <div class="metric">
                    <h3>Duration</h3>
                    <p style="font-size: 2em; margin: 0;">{report['suite_duration']:.1f}s</p>
                </div>
            </div>

            <h2>Test Results</h2>
        """

        for test in report['test_results']:
            status_class = test['status'].lower()
            html_content += f"""
            <div class="test-result {status_class}">
                <h3>{test['test_name']} - {test['status']} ({test['duration']:.2f}s)</h3>
                <div class="details">
                    <strong>Details:</strong>
                    <pre>{json.dumps(test['details'], indent=2)}</pre>
                </div>
            """

            if test['errors']:
                html_content += '<div class="error"><strong>Errors:</strong><ul>'
                for error in test['errors']:
                    html_content += f'<li>{error}</li>'
                html_content += '</ul></div>'

            html_content += '</div>'

        html_content += """
            </body>
        </html>
        """

        return html_content

def main():
    """Main execution function"""
    # Initialize test suite
    test_suite = E2ETestSuite()

    # Run comprehensive tests
    logger.info("Executing MeStore Comprehensive E2E Test Suite...")
    report = test_suite.run_comprehensive_test_suite()

    # Save JSON report
    with open("e2e_test_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Generate and save HTML report
    html_report = test_suite.generate_detailed_report(report)
    with open("e2e_test_report.html", "w") as f:
        f.write(html_report)

    # Print summary
    print(f"\n{'='*60}")
    print("MeStore E2E Test Suite Summary")
    print(f"{'='*60}")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['passed_tests']}")
    print(f"Failed: {report['failed_tests']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print(f"Duration: {report['suite_duration']:.1f}s")
    print(f"{'='*60}")

    # Exit with appropriate code
    exit_code = 0 if report['failed_tests'] == 0 else 1
    return exit_code

if __name__ == "__main__":
    exit(main())