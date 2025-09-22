#!/usr/bin/env python3
"""
Manual Integration Verification Script
====================================

Performs direct API calls to verify integration between frontend and backend
without relying on the test framework that has import issues.

Author: Integration Testing AI
Date: 2025-09-19
Purpose: Validate MVP integration readiness for October 9th deadline
"""

import asyncio
import json
import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Any

# Test configuration
BASE_URL = "http://192.168.1.137:8000/api/v1"
FRONTEND_URL = "http://192.168.1.137:5173"

class IntegrationTester:
    """Comprehensive integration testing for MeStore MVP"""

    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def log_test(self, test_name: str, status: str, details: Dict = None, duration: float = 0):
        """Log test result"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test": test_name,
            "status": status,
            "duration_ms": round(duration * 1000, 2),
            "details": details or {}
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status} ({duration*1000:.1f}ms)")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")

    async def test_backend_health(self):
        """Test backend health and availability"""
        start_time = time.time()
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                data = await response.json()
                duration = time.time() - start_time

                if response.status == 200 and data.get("status") == "success":
                    self.log_test("Backend Health Check", "PASS", {
                        "response_time": f"{duration*1000:.1f}ms",
                        "environment": data.get("data", {}).get("environment"),
                        "version": data.get("data", {}).get("version")
                    }, duration)
                    return True
                else:
                    self.log_test("Backend Health Check", "FAIL", {
                        "status_code": response.status,
                        "response": data
                    }, duration)
                    return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Backend Health Check", "FAIL", {
                "error": str(e)
            }, duration)
            return False

    async def test_frontend_accessibility(self):
        """Test frontend accessibility"""
        start_time = time.time()
        try:
            async with self.session.get(FRONTEND_URL) as response:
                content = await response.text()
                duration = time.time() - start_time

                if response.status == 200 and "MeStore" in content:
                    self.log_test("Frontend Accessibility", "PASS", {
                        "response_time": f"{duration*1000:.1f}ms",
                        "content_length": len(content)
                    }, duration)
                    return True
                else:
                    self.log_test("Frontend Accessibility", "FAIL", {
                        "status_code": response.status
                    }, duration)
                    return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Frontend Accessibility", "FAIL", {
                "error": str(e)
            }, duration)
            return False

    async def test_authentication_flow(self):
        """Test authentication integration"""
        start_time = time.time()
        try:
            # Test with multiple user types
            test_users = [
                {"email": "admin@mestore.com", "password": "123456", "expected_type": "admin"},
                {"email": "vendor@mestore.com", "password": "123456", "expected_type": "vendor"},
                {"email": "buyer@mestore.com", "password": "123456", "expected_type": "buyer"}
            ]

            auth_results = []
            for user in test_users:
                user_start = time.time()
                try:
                    async with self.session.post(
                        f"{BASE_URL}/auth/login",
                        json={"email": user["email"], "password": user["password"]},
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        data = await response.json()
                        user_duration = time.time() - user_start

                        if response.status == 200 and "access_token" in data:
                            auth_results.append({
                                "user": user["email"],
                                "status": "SUCCESS",
                                "duration": f"{user_duration*1000:.1f}ms"
                            })

                            # Store token for further tests
                            if user["expected_type"] == "vendor":
                                self.auth_token = data["access_token"]
                        else:
                            auth_results.append({
                                "user": user["email"],
                                "status": "FAILED",
                                "error": data.get("error_message", "Unknown error"),
                                "duration": f"{user_duration*1000:.1f}ms"
                            })

                except Exception as e:
                    auth_results.append({
                        "user": user["email"],
                        "status": "ERROR",
                        "error": str(e)
                    })

            duration = time.time() - start_time
            success_count = sum(1 for r in auth_results if r["status"] == "SUCCESS")

            if success_count > 0:
                self.log_test("Authentication Flow", "PASS" if success_count == len(test_users) else "PARTIAL", {
                    "successful_logins": f"{success_count}/{len(test_users)}",
                    "results": auth_results
                }, duration)
                return True
            else:
                self.log_test("Authentication Flow", "FAIL", {
                    "results": auth_results
                }, duration)
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Authentication Flow", "FAIL", {
                "error": str(e)
            }, duration)
            return False

    async def test_api_endpoints(self):
        """Test critical API endpoints"""
        start_time = time.time()

        endpoints = [
            {"url": "/payments/methods", "method": "GET", "name": "Payment Methods"},
            {"url": "/orders", "method": "GET", "name": "Orders List", "requires_auth": True},
            {"url": "/products", "method": "GET", "name": "Products List"},
            {"url": "/vendedores/me", "method": "GET", "name": "Vendor Profile", "requires_auth": True},
        ]

        endpoint_results = []

        for endpoint in endpoints:
            endpoint_start = time.time()
            try:
                headers = {"Content-Type": "application/json"}
                if endpoint.get("requires_auth") and self.auth_token:
                    headers["Authorization"] = f"Bearer {self.auth_token}"

                if endpoint["method"] == "GET":
                    async with self.session.get(f"{BASE_URL}{endpoint['url']}", headers=headers) as response:
                        data = await response.json()
                        endpoint_duration = time.time() - endpoint_start

                        endpoint_results.append({
                            "endpoint": endpoint["name"],
                            "status_code": response.status,
                            "duration": f"{endpoint_duration*1000:.1f}ms",
                            "success": response.status < 400
                        })

            except Exception as e:
                endpoint_results.append({
                    "endpoint": endpoint["name"],
                    "error": str(e),
                    "success": False
                })

        duration = time.time() - start_time
        success_count = sum(1 for r in endpoint_results if r["success"])

        if success_count >= len(endpoints) * 0.8:  # 80% success rate
            self.log_test("API Endpoints", "PASS", {
                "successful_endpoints": f"{success_count}/{len(endpoints)}",
                "results": endpoint_results
            }, duration)
            return True
        else:
            self.log_test("API Endpoints", "FAIL", {
                "results": endpoint_results
            }, duration)
            return False

    async def test_websocket_connection(self):
        """Test WebSocket functionality for real-time features"""
        start_time = time.time()
        try:
            # Test WebSocket connection to analytics endpoint
            ws_url = "ws://192.168.1.137:8000/api/v1/ws/vendor/analytics"

            try:
                async with self.session.ws_connect(ws_url) as ws:
                    # Send a test message
                    await ws.send_str(json.dumps({"action": "subscribe", "channel": "analytics"}))

                    # Wait for response with timeout
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=5.0)
                        duration = time.time() - start_time

                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            self.log_test("WebSocket Connection", "PASS", {
                                "connection_time": f"{duration*1000:.1f}ms",
                                "response_type": data.get("type", "unknown")
                            }, duration)
                            return True
                        else:
                            self.log_test("WebSocket Connection", "FAIL", {
                                "message_type": str(msg.type)
                            }, duration)
                            return False

                    except asyncio.TimeoutError:
                        duration = time.time() - start_time
                        self.log_test("WebSocket Connection", "FAIL", {
                            "error": "Connection timeout"
                        }, duration)
                        return False

            except Exception as e:
                duration = time.time() - start_time
                self.log_test("WebSocket Connection", "FAIL", {
                    "error": str(e)
                }, duration)
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("WebSocket Connection", "FAIL", {
                "error": str(e)
            }, duration)
            return False

    async def test_performance_benchmarks(self):
        """Test system performance"""
        start_time = time.time()

        # Test multiple concurrent requests
        test_urls = [
            f"{BASE_URL}/health",
            f"{BASE_URL}/products?limit=10",
            f"{BASE_URL}/payments/methods",
            f"{FRONTEND_URL}"
        ]

        concurrent_results = []

        async def test_single_request(url):
            req_start = time.time()
            try:
                async with self.session.get(url) as response:
                    req_duration = time.time() - req_start
                    return {
                        "url": url,
                        "status": response.status,
                        "duration": req_duration,
                        "success": response.status < 400
                    }
            except Exception as e:
                req_duration = time.time() - req_start
                return {
                    "url": url,
                    "error": str(e),
                    "duration": req_duration,
                    "success": False
                }

        # Run concurrent requests
        tasks = [test_single_request(url) for url in test_urls * 3]  # 3x each URL
        results = await asyncio.gather(*tasks)

        duration = time.time() - start_time
        successful_requests = [r for r in results if r["success"]]
        avg_response_time = sum(r["duration"] for r in successful_requests) / len(successful_requests) if successful_requests else 0

        performance_status = "PASS" if avg_response_time < 1.0 and len(successful_requests) >= len(results) * 0.9 else "FAIL"

        self.log_test("Performance Benchmarks", performance_status, {
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "average_response_time": f"{avg_response_time*1000:.1f}ms",
            "test_duration": f"{duration:.2f}s"
        }, duration)

        return performance_status == "PASS"

    async def run_full_integration_test(self):
        """Run complete integration test suite"""
        print("🔍 MESTORE MVP INTEGRATION VERIFICATION")
        print("=" * 50)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Backend URL: {BASE_URL}")
        print(f"🖥️  Frontend URL: {FRONTEND_URL}")
        print()

        # Run all tests
        tests = [
            self.test_backend_health(),
            self.test_frontend_accessibility(),
            self.test_authentication_flow(),
            self.test_api_endpoints(),
            self.test_websocket_connection(),
            self.test_performance_benchmarks()
        ]

        results = await asyncio.gather(*tests, return_exceptions=True)

        # Calculate overall results
        passed_tests = sum(1 for r in results if r is True)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100

        print()
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 30)
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        # MVP Readiness Assessment
        if success_rate >= 90:
            mvp_status = "🟢 PRODUCTION READY"
        elif success_rate >= 80:
            mvp_status = "🟡 NEAR READY (Minor Issues)"
        elif success_rate >= 60:
            mvp_status = "🟠 NEEDS WORK (Major Issues)"
        else:
            mvp_status = "🔴 NOT READY (Critical Issues)"

        print(f"🎯 MVP Status: {mvp_status}")
        print(f"📅 Deadline: October 9, 2025 (3 weeks)")

        # Save detailed results
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate,
                "mvp_status": mvp_status
            },
            "detailed_results": self.test_results,
            "assessment": {
                "frontend_backend_integration": "✅" if passed_tests >= 4 else "❌",
                "authentication_working": "✅" if any("Authentication" in r["test"] and r["status"] == "PASS" for r in self.test_results) else "❌",
                "api_connectivity": "✅" if any("API" in r["test"] and r["status"] == "PASS" for r in self.test_results) else "❌",
                "realtime_features": "✅" if any("WebSocket" in r["test"] and r["status"] == "PASS" for r in self.test_results) else "❌",
                "performance_acceptable": "✅" if any("Performance" in r["test"] and r["status"] == "PASS" for r in self.test_results) else "❌"
            }
        }

        with open("integration_verification_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"📄 Detailed report saved to: integration_verification_report.json")
        return success_rate >= 80  # MVP ready if 80%+ success rate

async def main():
    """Main integration verification function"""
    async with IntegrationTester() as tester:
        success = await tester.run_full_integration_test()
        return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit_code = 0 if result else 1
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Integration test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Integration test failed with error: {e}")
        exit(1)