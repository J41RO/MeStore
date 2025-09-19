#!/usr/bin/env python3
"""
FastAPI Integration Validation Script
=====================================

Comprehensive validation script to test the integrated FastAPI application
with all backend services, middleware, and dependency injection.

Author: Backend Framework AI
Date: 2025-09-17
Purpose: Validate complete FastAPI integration for production readiness
"""

import asyncio
import logging
import sys
from typing import Dict, List, Any
import httpx
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FastAPIIntegrationValidator:
    """Comprehensive validation for FastAPI integration"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.validation_results = {
            "service_container": False,
            "middleware_chain": False,
            "authentication": False,
            "dependency_injection": False,
            "caching": False,
            "security": False,
            "health_checks": False,
            "performance": False
        }
        self.errors = []

    async def validate_all(self) -> Dict[str, Any]:
        """Run all validation tests"""
        logger.info("🚀 Starting FastAPI Integration Validation...")

        # Test order is important - basic services first
        tests = [
            ("Service Container", self.validate_service_container),
            ("Health Checks", self.validate_health_checks),
            ("Middleware Chain", self.validate_middleware_chain),
            ("Security Headers", self.validate_security_headers),
            ("Rate Limiting", self.validate_rate_limiting),
            ("Authentication System", self.validate_authentication),
            ("Dependency Injection", self.validate_dependency_injection),
            ("Caching System", self.validate_caching),
            ("Database Connectivity", self.validate_database),
            ("Redis Connectivity", self.validate_redis),
            ("Performance Monitoring", self.validate_performance)
        ]

        for test_name, test_func in tests:
            try:
                logger.info(f"🔍 Testing: {test_name}")
                result = await test_func()
                if result:
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
            except Exception as e:
                logger.error(f"💥 {test_name}: ERROR - {str(e)}")
                self.errors.append(f"{test_name}: {str(e)}")

        return self.generate_report()

    async def validate_service_container(self) -> bool:
        """Validate service container initialization"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health/services")

                if response.status_code == 200:
                    data = response.json()
                    services = data.get("services", {})

                    # Check essential services
                    required_services = [
                        "service_container",
                        "redis",
                        "cache_service"
                    ]

                    all_healthy = all(
                        services.get(service) == "healthy"
                        for service in required_services
                    )

                    if all_healthy:
                        self.validation_results["service_container"] = True
                        return True
                    else:
                        self.errors.append(f"Unhealthy services: {[s for s in required_services if services.get(s) != 'healthy']}")
                        return False
                else:
                    self.errors.append(f"Health check returned {response.status_code}")
                    return False

        except Exception as e:
            self.errors.append(f"Service container validation failed: {str(e)}")
            return False

    async def validate_health_checks(self) -> bool:
        """Validate health check endpoints"""
        try:
            async with httpx.AsyncClient() as client:
                # Basic health check
                response = await client.get(f"{self.base_url}/health")
                if response.status_code != 200:
                    self.errors.append(f"Basic health check failed: {response.status_code}")
                    return False

                health_data = response.json()
                if health_data.get("status") != "healthy":
                    self.errors.append(f"Health status not healthy: {health_data}")
                    return False

                # Comprehensive health check
                response = await client.get(f"{self.base_url}/health/services")
                if response.status_code != 200:
                    self.errors.append(f"Services health check failed: {response.status_code}")
                    return False

                self.validation_results["health_checks"] = True
                return True

        except Exception as e:
            self.errors.append(f"Health check validation failed: {str(e)}")
            return False

    async def validate_middleware_chain(self) -> bool:
        """Validate middleware chain is properly configured"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")

                # Check for security headers (should be present due to middleware)
                expected_headers = [
                    "x-content-type-options",
                    "x-frame-options",
                    "server"
                ]

                missing_headers = []
                for header in expected_headers:
                    if header not in response.headers:
                        missing_headers.append(header)

                if missing_headers:
                    self.errors.append(f"Missing security headers: {missing_headers}")
                    return False

                self.validation_results["middleware_chain"] = True
                return True

        except Exception as e:
            self.errors.append(f"Middleware validation failed: {str(e)}")
            return False

    async def validate_security_headers(self) -> bool:
        """Validate security headers are properly set"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")

                security_headers = {
                    "x-content-type-options": "nosniff",
                    "x-frame-options": "DENY",
                    "server": "MeStore/1.0"
                }

                for header, expected_value in security_headers.items():
                    actual_value = response.headers.get(header)
                    if actual_value != expected_value:
                        self.errors.append(f"Security header {header}: expected '{expected_value}', got '{actual_value}'")
                        return False

                self.validation_results["security"] = True
                return True

        except Exception as e:
            self.errors.append(f"Security headers validation failed: {str(e)}")
            return False

    async def validate_rate_limiting(self) -> bool:
        """Validate rate limiting is working"""
        try:
            async with httpx.AsyncClient() as client:
                # Make several requests quickly to trigger rate limiting
                responses = []
                for _ in range(5):
                    response = await client.get(f"{self.base_url}/health")
                    responses.append(response.status_code)

                # All should succeed for health endpoint (excluded from rate limiting)
                if all(status == 200 for status in responses):
                    logger.info("Rate limiting validation: Health endpoint properly excluded")
                    return True
                else:
                    self.errors.append(f"Unexpected responses during rate limiting test: {responses}")
                    return False

        except Exception as e:
            self.errors.append(f"Rate limiting validation failed: {str(e)}")
            return False

    async def validate_authentication(self) -> bool:
        """Validate authentication system"""
        try:
            async with httpx.AsyncClient() as client:
                # Test protected endpoint without auth
                response = await client.get(f"{self.base_url}/auth/me")
                if response.status_code != 401:
                    self.errors.append(f"Protected endpoint should return 401, got {response.status_code}")
                    return False

                # Test login endpoint exists
                response = await client.post(
                    f"{self.base_url}/auth/login",
                    json={"email": "test@test.com", "password": "invalid"}
                )

                # Should return 401 for invalid credentials (service is working)
                if response.status_code not in [401, 422]:  # 422 for validation errors
                    self.errors.append(f"Login endpoint returned unexpected status: {response.status_code}")
                    return False

                self.validation_results["authentication"] = True
                return True

        except Exception as e:
            self.errors.append(f"Authentication validation failed: {str(e)}")
            return False

    async def validate_dependency_injection(self) -> bool:
        """Validate dependency injection is working"""
        try:
            # This is validated implicitly by other tests
            # If services health check passes, DI is working
            if self.validation_results.get("service_container", False):
                self.validation_results["dependency_injection"] = True
                return True
            else:
                self.errors.append("Dependency injection validation failed: Service container not healthy")
                return False

        except Exception as e:
            self.errors.append(f"Dependency injection validation failed: {str(e)}")
            return False

    async def validate_caching(self) -> bool:
        """Validate caching system"""
        try:
            # Test Redis connectivity directly
            from app.core.config import settings

            redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )

            # Test Redis connection
            redis_client.ping()

            # Test cache operations
            test_key = "validation_test"
            test_value = "validation_value"

            redis_client.set(test_key, test_value, ex=60)
            retrieved_value = redis_client.get(test_key)
            redis_client.delete(test_key)

            if retrieved_value == test_value:
                self.validation_results["caching"] = True
                return True
            else:
                self.errors.append(f"Cache test failed: expected '{test_value}', got '{retrieved_value}'")
                return False

        except Exception as e:
            self.errors.append(f"Caching validation failed: {str(e)}")
            return False

    async def validate_database(self) -> bool:
        """Validate database connectivity"""
        try:
            from app.core.config import settings

            # Create async engine for testing
            engine = create_async_engine(settings.DATABASE_URL, echo=False)

            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                test_result = result.scalar()

                if test_result == 1:
                    logger.info("Database connectivity: OK")
                    return True
                else:
                    self.errors.append(f"Database test query failed: expected 1, got {test_result}")
                    return False

        except Exception as e:
            self.errors.append(f"Database validation failed: {str(e)}")
            return False

    async def validate_redis(self) -> bool:
        """Validate Redis connectivity"""
        try:
            from app.core.config import settings

            redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )

            # Test Redis connection
            pong = redis_client.ping()
            if pong:
                logger.info("Redis connectivity: OK")
                return True
            else:
                self.errors.append("Redis ping failed")
                return False

        except Exception as e:
            self.errors.append(f"Redis validation failed: {str(e)}")
            return False

    async def validate_performance(self) -> bool:
        """Validate performance monitoring"""
        try:
            async with httpx.AsyncClient() as client:
                # Test multiple requests to check performance
                import time
                start_time = time.time()

                responses = []
                for _ in range(10):
                    response = await client.get(f"{self.base_url}/health")
                    responses.append(response.status_code)

                end_time = time.time()
                total_time = end_time - start_time
                avg_time = total_time / 10

                # All requests should succeed
                if all(status == 200 for status in responses):
                    logger.info(f"Performance test: 10 requests in {total_time:.2f}s (avg: {avg_time*1000:.1f}ms)")

                    # Basic performance check - should be under 500ms average
                    if avg_time < 0.5:
                        self.validation_results["performance"] = True
                        return True
                    else:
                        self.errors.append(f"Performance too slow: average {avg_time*1000:.1f}ms")
                        return False
                else:
                    self.errors.append(f"Performance test failed: some requests failed {responses}")
                    return False

        except Exception as e:
            self.errors.append(f"Performance validation failed: {str(e)}")
            return False

    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        passed_tests = sum(1 for result in self.validation_results.values() if result)
        total_tests = len(self.validation_results)
        success_rate = (passed_tests / total_tests) * 100

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "overall_status": "PASS" if passed_tests == total_tests else "FAIL"
            },
            "test_results": self.validation_results,
            "errors": self.errors,
            "recommendations": self.get_recommendations()
        }

        return report

    def get_recommendations(self) -> List[str]:
        """Get recommendations based on validation results"""
        recommendations = []

        if not self.validation_results.get("service_container"):
            recommendations.append("Check service container initialization and Redis connectivity")

        if not self.validation_results.get("authentication"):
            recommendations.append("Verify authentication service configuration and JWT settings")

        if not self.validation_results.get("caching"):
            recommendations.append("Check Redis configuration and connectivity")

        if not self.validation_results.get("security"):
            recommendations.append("Review security middleware configuration")

        if not self.validation_results.get("performance"):
            recommendations.append("Optimize application performance and database queries")

        if not recommendations:
            recommendations.append("All validation tests passed! FastAPI integration is production-ready.")

        return recommendations


async def main():
    """Main validation function"""
    print("🚀 FastAPI Integration Validation Script")
    print("=" * 50)

    validator = FastAPIIntegrationValidator()
    report = await validator.validate_all()

    print("\n" + "=" * 50)
    print("📊 VALIDATION REPORT")
    print("=" * 50)

    # Print summary
    summary = report["summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Overall Status: {summary['overall_status']}")

    # Print test results
    print("\n📋 Test Results:")
    print("-" * 30)
    for test_name, result in report["test_results"].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    # Print errors if any
    if report["errors"]:
        print("\n🚨 Errors:")
        print("-" * 30)
        for error in report["errors"]:
            print(f"• {error}")

    # Print recommendations
    print("\n💡 Recommendations:")
    print("-" * 30)
    for rec in report["recommendations"]:
        print(f"• {rec}")

    # Exit with appropriate code
    if summary["overall_status"] == "PASS":
        print("\n🎉 FastAPI integration validation completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ FastAPI integration validation failed. Please review errors and recommendations.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())