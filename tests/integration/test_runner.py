#!/usr/bin/env python3
"""
Integration Test Runner
======================
Comprehensive test runner for all integration test suites with:
- Test orchestration and execution
- Performance monitoring
- Result aggregation and reporting
- Test environment validation
- Failure analysis and reporting

Author: Integration Testing AI
Date: 2025-09-17
"""

import asyncio
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.main import app
from tests.conftest import async_session, async_client


@dataclass
class TestSuiteResult:
    """Test suite execution result."""
    name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    execution_time: float
    success_rate: float
    errors: List[str]
    warnings: List[str]


@dataclass
class IntegrationTestReport:
    """Complete integration test report."""
    timestamp: str
    total_execution_time: float
    environment: str
    test_suites: List[TestSuiteResult]
    overall_success_rate: float
    critical_failures: List[str]
    performance_metrics: Dict[str, Any]
    recommendations: List[str]


class IntegrationTestRunner:
    """Orchestrates and executes all integration tests."""

    def __init__(self):
        self.test_suites = [
            "test_comprehensive_integration.py",
            "test_api_endpoints_integration.py",
            "test_service_communication.py",
            "test_performance_integration.py"
        ]
        self.results: List[TestSuiteResult] = []
        self.start_time = None
        self.end_time = None

    async def validate_test_environment(self) -> Dict[str, bool]:
        """Validate test environment is ready for integration testing."""
        print("🔍 Validating test environment...")

        validations = {
            "database_connection": False,
            "application_startup": False,
            "middleware_loaded": False,
            "models_imported": False
        }

        try:
            # Test database connection
            from app.core.database import async_test_engine
            async with async_test_engine.connect() as conn:
                await conn.execute("SELECT 1")
            validations["database_connection"] = True
            print("   ✅ Database connection validated")

        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")

        try:
            # Test application startup
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.get("/health")
            if response.status_code == 200:
                validations["application_startup"] = True
                print("   ✅ Application startup validated")

        except Exception as e:
            print(f"   ❌ Application startup failed: {e}")

        try:
            # Test middleware loaded
            middleware_count = len(app.middleware_stack)
            if middleware_count > 0:
                validations["middleware_loaded"] = True
                print(f"   ✅ Middleware loaded ({middleware_count} middleware)")

        except Exception as e:
            print(f"   ❌ Middleware validation failed: {e}")

        try:
            # Test models imported
            from app.models.user import User
            from app.models.product import Product
            from app.models.order import Order
            validations["models_imported"] = True
            print("   ✅ Models imported successfully")

        except Exception as e:
            print(f"   ❌ Model import failed: {e}")

        return validations

    def run_test_suite(self, test_file: str) -> TestSuiteResult:
        """Run a single test suite and return results."""
        print(f"\n🧪 Running test suite: {test_file}")

        test_path = Path(__file__).parent / test_file
        if not test_path.exists():
            return TestSuiteResult(
                name=test_file,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                execution_time=0.0,
                success_rate=0.0,
                errors=[f"Test file {test_file} not found"],
                warnings=[]
            )

        start_time = time.time()

        # Run pytest on the specific file
        pytest_args = [
            str(test_path),
            "-v",
            "--tb=short",
            "--maxfail=10",  # Stop after 10 failures
            "-x",  # Stop on first failure for critical tests
            "--disable-warnings",
            "-q"  # Quiet mode
        ]

        try:
            # Capture pytest results
            exit_code = pytest.main(pytest_args)

            execution_time = time.time() - start_time

            # Parse results (simplified - in real scenario would parse pytest output)
            if exit_code == 0:
                # All tests passed
                return TestSuiteResult(
                    name=test_file,
                    total_tests=1,  # Simplified
                    passed_tests=1,
                    failed_tests=0,
                    skipped_tests=0,
                    execution_time=execution_time,
                    success_rate=1.0,
                    errors=[],
                    warnings=[]
                )
            else:
                # Some tests failed
                return TestSuiteResult(
                    name=test_file,
                    total_tests=1,
                    passed_tests=0,
                    failed_tests=1,
                    skipped_tests=0,
                    execution_time=execution_time,
                    success_rate=0.0,
                    errors=[f"Test suite failed with exit code {exit_code}"],
                    warnings=[]
                )

        except Exception as e:
            execution_time = time.time() - start_time
            return TestSuiteResult(
                name=test_file,
                total_tests=1,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                execution_time=execution_time,
                success_rate=0.0,
                errors=[f"Test execution error: {str(e)}"],
                warnings=[]
            )

    def analyze_performance_metrics(self) -> Dict[str, Any]:
        """Analyze performance metrics from test runs."""
        total_time = sum(result.execution_time for result in self.results)
        avg_time_per_suite = total_time / len(self.results) if self.results else 0

        return {
            "total_execution_time": total_time,
            "average_suite_time": avg_time_per_suite,
            "fastest_suite": min(self.results, key=lambda x: x.execution_time).name if self.results else None,
            "slowest_suite": max(self.results, key=lambda x: x.execution_time).name if self.results else None,
            "performance_threshold_breaches": [
                result.name for result in self.results
                if result.execution_time > 300  # 5 minutes threshold
            ]
        }

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Check overall success rate
        total_tests = sum(r.total_tests for r in self.results)
        total_passed = sum(r.passed_tests for r in self.results)
        overall_success_rate = total_passed / total_tests if total_tests > 0 else 0

        if overall_success_rate < 0.8:
            recommendations.append("Overall success rate is below 80%. Review failing tests and fix critical issues.")

        # Check performance
        slow_suites = [r for r in self.results if r.execution_time > 120]  # 2 minutes
        if slow_suites:
            recommendations.append(f"Performance optimization needed for: {', '.join(s.name for s in slow_suites)}")

        # Check for critical failures
        critical_errors = []
        for result in self.results:
            if "authentication" in result.name.lower() and result.failed_tests > 0:
                critical_errors.append("Authentication system has failures - critical security issue")
            if "performance" in result.name.lower() and result.success_rate < 0.5:
                critical_errors.append("Performance tests failing - system may not handle production load")

        recommendations.extend(critical_errors)

        if not recommendations:
            recommendations.append("All integration tests are passing with good performance. System ready for production.")

        return recommendations

    def generate_report(self) -> IntegrationTestReport:
        """Generate comprehensive test report."""
        total_tests = sum(r.total_tests for r in self.results)
        total_passed = sum(r.passed_tests for r in self.results)
        overall_success_rate = total_passed / total_tests if total_tests > 0 else 0

        critical_failures = []
        for result in self.results:
            if result.success_rate < 0.5:  # Less than 50% success rate
                critical_failures.extend(result.errors)

        return IntegrationTestReport(
            timestamp=datetime.now().isoformat(),
            total_execution_time=self.end_time - self.start_time if self.end_time and self.start_time else 0,
            environment="test",
            test_suites=self.results,
            overall_success_rate=overall_success_rate,
            critical_failures=critical_failures,
            performance_metrics=self.analyze_performance_metrics(),
            recommendations=self.generate_recommendations()
        )

    def save_report(self, report: IntegrationTestReport, output_file: str = None):
        """Save test report to file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"integration_test_report_{timestamp}.json"

        output_path = Path(__file__).parent / "reports" / output_file
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)

        print(f"\n📊 Test report saved to: {output_path}")

    def print_summary(self, report: IntegrationTestReport):
        """Print test execution summary."""
        print("\n" + "="*80)
        print("INTEGRATION TEST EXECUTION SUMMARY")
        print("="*80)

        print(f"Execution Time: {report.total_execution_time:.2f} seconds")
        print(f"Overall Success Rate: {report.overall_success_rate:.1%}")
        print(f"Test Suites: {len(report.test_suites)}")

        print(f"\nSUITE BREAKDOWN:")
        for suite in report.test_suites:
            status = "✅ PASS" if suite.success_rate >= 0.8 else "❌ FAIL"
            print(f"   {status} {suite.name}: {suite.success_rate:.1%} "
                  f"({suite.passed_tests}/{suite.total_tests}) in {suite.execution_time:.2f}s")

        if report.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in report.critical_failures:
                print(f"   - {failure}")

        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report.recommendations:
            print(f"   - {rec}")

        print("\n" + "="*80)

    async def run_all_tests(self) -> IntegrationTestReport:
        """Run all integration test suites and return comprehensive report."""
        print("🚀 Starting comprehensive integration test execution...")
        self.start_time = time.time()

        # Validate environment first
        validations = await self.validate_test_environment()
        failed_validations = [k for k, v in validations.items() if not v]

        if failed_validations:
            print(f"\n⚠️  Environment validation failed for: {', '.join(failed_validations)}")
            print("Some tests may fail due to environment issues.")

        # Run each test suite
        for test_suite in self.test_suites:
            try:
                result = self.run_test_suite(test_suite)
                self.results.append(result)

                # Print immediate feedback
                status = "✅" if result.success_rate >= 0.8 else "❌"
                print(f"   {status} {test_suite}: {result.success_rate:.1%} success in {result.execution_time:.2f}s")

            except Exception as e:
                print(f"   ❌ {test_suite}: Failed to execute - {e}")
                error_result = TestSuiteResult(
                    name=test_suite,
                    total_tests=0,
                    passed_tests=0,
                    failed_tests=1,
                    skipped_tests=0,
                    execution_time=0.0,
                    success_rate=0.0,
                    errors=[str(e)],
                    warnings=[]
                )
                self.results.append(error_result)

        self.end_time = time.time()

        # Generate and return report
        report = self.generate_report()
        self.save_report(report)
        self.print_summary(report)

        return report


async def main():
    """Main entry point for integration test runner."""
    runner = IntegrationTestRunner()

    try:
        report = await runner.run_all_tests()

        # Exit with appropriate code
        if report.overall_success_rate >= 0.8:
            print("\n🎉 Integration tests completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Integration tests failed. Please review the report.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user.")
        sys.exit(130)

    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())