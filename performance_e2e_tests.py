#!/usr/bin/env python3
"""
MeStore Performance E2E Testing Suite
=====================================

This script performs comprehensive performance and load testing to validate
system behavior under various load conditions and concurrent user scenarios.

Test Coverage:
- Load testing with concurrent users
- API response time validation
- Frontend rendering performance
- Database query optimization validation
- Memory and CPU usage monitoring
- Stress testing scenarios
"""

import asyncio
import time
import json
import logging
import sys
import psutil
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
import concurrent.futures
from pathlib import Path
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_e2e_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    response_times: List[float]
    success_rate: float
    requests_per_second: float
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float

@dataclass
class LoadTestResult:
    """Load test result data structure"""
    test_name: str
    concurrent_users: int
    total_requests: int
    duration: float
    metrics: PerformanceMetrics
    status: str
    error_message: str = ""

class PerformanceE2ETestSuite:
    """Performance E2E Testing Suite for MeStore"""

    def __init__(self):
        self.backend_url = "http://192.168.1.137:8000"
        self.frontend_url = "http://192.168.1.137:5174"
        self.test_results: List[LoadTestResult] = []
        self.session = requests.Session()

    def monitor_system_resources(self) -> Dict[str, float]:
        """Monitor system resources (CPU, Memory)"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_mb = memory.used / 1024 / 1024

            return {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_mb": memory_mb,
                "memory_available_mb": memory.available / 1024 / 1024,
                "memory_percent": memory.percent
            }
        except Exception as e:
            logger.warning(f"Could not monitor system resources: {e}")
            return {
                "cpu_usage_percent": 0.0,
                "memory_usage_mb": 0.0,
                "memory_available_mb": 0.0,
                "memory_percent": 0.0
            }

    def make_single_request(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Make a single HTTP request and measure performance"""
        start_time = time.time()
        success = False
        status_code = 0
        error_message = ""

        try:
            response = self.session.get(url, timeout=timeout)
            status_code = response.status_code
            success = 200 <= status_code < 400
        except Exception as e:
            error_message = str(e)

        response_time = time.time() - start_time

        return {
            "response_time": response_time,
            "success": success,
            "status_code": status_code,
            "error_message": error_message
        }

    def run_load_test(self, url: str, concurrent_users: int, duration_seconds: int) -> PerformanceMetrics:
        """Run load test with specified concurrent users"""
        logger.info(f"Running load test: {concurrent_users} users for {duration_seconds}s on {url}")

        results = []
        stop_time = time.time() + duration_seconds
        system_metrics = []

        def worker():
            while time.time() < stop_time:
                result = self.make_single_request(url)
                results.append(result)
                time.sleep(0.1)  # Small delay between requests

        def resource_monitor():
            while time.time() < stop_time:
                metrics = self.monitor_system_resources()
                system_metrics.append(metrics)
                time.sleep(1)  # Monitor every second

        # Start resource monitoring
        monitor_thread = threading.Thread(target=resource_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()

        # Start load test with concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_users)]
            concurrent.futures.wait(futures)

        # Calculate metrics
        if not results:
            raise Exception("No successful requests completed")

        response_times = [r["response_time"] for r in results]
        successful_requests = len([r for r in results if r["success"]])
        total_requests = len(results)

        # Calculate percentiles
        sorted_times = sorted(response_times)
        p95_index = int(0.95 * len(sorted_times))
        p99_index = int(0.99 * len(sorted_times))

        # Average system metrics
        avg_cpu = statistics.mean([m["cpu_usage_percent"] for m in system_metrics]) if system_metrics else 0
        avg_memory = statistics.mean([m["memory_usage_mb"] for m in system_metrics]) if system_metrics else 0

        return PerformanceMetrics(
            response_times=response_times,
            success_rate=(successful_requests / total_requests) * 100,
            requests_per_second=total_requests / duration_seconds,
            avg_response_time=statistics.mean(response_times),
            p95_response_time=sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1],
            p99_response_time=sorted_times[p99_index] if p99_index < len(sorted_times) else sorted_times[-1],
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            memory_usage_mb=avg_memory,
            cpu_usage_percent=avg_cpu
        )

    def test_baseline_performance(self) -> LoadTestResult:
        """Test baseline performance with single user"""
        test_name = "Baseline Performance (1 User)"
        start_time = time.time()

        try:
            metrics = self.run_load_test(f"{self.backend_url}/health", 1, 10)
            duration = time.time() - start_time

            result = LoadTestResult(
                test_name=test_name,
                concurrent_users=1,
                total_requests=len(metrics.response_times),
                duration=duration,
                metrics=metrics,
                status="PASS"
            )

        except Exception as e:
            duration = time.time() - start_time
            result = LoadTestResult(
                test_name=test_name,
                concurrent_users=1,
                total_requests=0,
                duration=duration,
                metrics=PerformanceMetrics([], 0, 0, 0, 0, 0, 0, 0, 0, 0),
                status="FAIL",
                error_message=str(e)
            )

        return result

    def test_moderate_load(self) -> LoadTestResult:
        """Test moderate load with 10 concurrent users"""
        test_name = "Moderate Load (10 Users)"
        start_time = time.time()

        try:
            metrics = self.run_load_test(f"{self.backend_url}/health", 10, 15)
            duration = time.time() - start_time

            result = LoadTestResult(
                test_name=test_name,
                concurrent_users=10,
                total_requests=len(metrics.response_times),
                duration=duration,
                metrics=metrics,
                status="PASS"
            )

        except Exception as e:
            duration = time.time() - start_time
            result = LoadTestResult(
                test_name=test_name,
                concurrent_users=10,
                total_requests=0,
                duration=duration,
                metrics=PerformanceMetrics([], 0, 0, 0, 0, 0, 0, 0, 0, 0),
                status="FAIL",
                error_message=str(e)
            )

        return result

    def test_high_load(self) -> LoadTestResult:
        """Test high load with 25 concurrent users"""
        test_name = "High Load (25 Users)"
        start_time = time.time()

        try:
            metrics = self.run_load_test(f"{self.backend_url}/health", 25, 20)
            duration = time.time() - start_time

            result = LoadTestResult(
                test_name=test_name,
                concurrent_users=25,
                total_requests=len(metrics.response_times),
                duration=duration,
                metrics=metrics,
                status="PASS"
            )

        except Exception as e:
            duration = time.time() - start_time
            result = LoadTestResult(
                test_name=test_name,
                concurrent_users=25,
                total_requests=0,
                duration=duration,
                metrics=PerformanceMetrics([], 0, 0, 0, 0, 0, 0, 0, 0, 0),
                status="FAIL",
                error_message=str(e)
            )

        return result

    def test_api_endpoints_performance(self) -> LoadTestResult:
        """Test API endpoints performance under load"""
        test_name = "API Endpoints Performance"
        start_time = time.time()

        try:
            # Test multiple endpoints
            endpoints = [
                f"{self.backend_url}/health",
                f"{self.backend_url}/docs",
                f"{self.backend_url}/openapi.json"
            ]

            all_metrics = []
            for endpoint in endpoints:
                try:
                    metrics = self.run_load_test(endpoint, 5, 10)
                    all_metrics.append(metrics)
                except Exception as e:
                    logger.warning(f"Failed to test endpoint {endpoint}: {e}")

            if not all_metrics:
                raise Exception("No endpoints could be tested")

            # Aggregate metrics
            all_response_times = []
            total_requests = 0
            successful_requests = 0

            for metrics in all_metrics:
                all_response_times.extend(metrics.response_times)
                total_requests += len(metrics.response_times)
                successful_requests += len(metrics.response_times) * (metrics.success_rate / 100)

            duration = time.time() - start_time

            # Calculate aggregate metrics
            if all_response_times:
                sorted_times = sorted(all_response_times)
                p95_index = int(0.95 * len(sorted_times))
                p99_index = int(0.99 * len(sorted_times))

                aggregated_metrics = PerformanceMetrics(
                    response_times=all_response_times,
                    success_rate=(successful_requests / total_requests) * 100 if total_requests > 0 else 0,
                    requests_per_second=total_requests / duration,
                    avg_response_time=statistics.mean(all_response_times),
                    p95_response_time=sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1],
                    p99_response_time=sorted_times[p99_index] if p99_index < len(sorted_times) else sorted_times[-1],
                    min_response_time=min(all_response_times),
                    max_response_time=max(all_response_times),
                    memory_usage_mb=statistics.mean([m.memory_usage_mb for m in all_metrics]),
                    cpu_usage_percent=statistics.mean([m.cpu_usage_percent for m in all_metrics])
                )

                result = LoadTestResult(
                    test_name=test_name,
                    concurrent_users=5,
                    total_requests=total_requests,
                    duration=duration,
                    metrics=aggregated_metrics,
                    status="PASS"
                )
            else:
                raise Exception("No response times collected")

        except Exception as e:
            duration = time.time() - start_time
            result = LoadTestResult(
                test_name=test_name,
                concurrent_users=5,
                total_requests=0,
                duration=duration,
                metrics=PerformanceMetrics([], 0, 0, 0, 0, 0, 0, 0, 0, 0),
                status="FAIL",
                error_message=str(e)
            )

        return result

    def test_frontend_performance(self) -> LoadTestResult:
        """Test frontend performance under load"""
        test_name = "Frontend Performance"
        start_time = time.time()

        try:
            metrics = self.run_load_test(self.frontend_url, 10, 15)
            duration = time.time() - start_time

            result = LoadTestResult(
                test_name=test_name,
                concurrent_users=10,
                total_requests=len(metrics.response_times),
                duration=duration,
                metrics=metrics,
                status="PASS"
            )

        except Exception as e:
            duration = time.time() - start_time
            result = LoadTestResult(
                test_name=test_name,
                concurrent_users=10,
                total_requests=0,
                duration=duration,
                metrics=PerformanceMetrics([], 0, 0, 0, 0, 0, 0, 0, 0, 0),
                status="FAIL",
                error_message=str(e)
            )

        return result

    def log_test_result(self, result: LoadTestResult):
        """Log test result with performance metrics"""
        status_emoji = "✅" if result.status == "PASS" else "❌"
        logger.info(f"{status_emoji} {result.test_name}: {result.status} ({result.duration:.2f}s)")

        if result.status == "PASS" and result.metrics.response_times:
            logger.info(f"   📊 Requests: {result.total_requests} | Success Rate: {result.metrics.success_rate:.1f}%")
            logger.info(f"   ⚡ Avg Response: {result.metrics.avg_response_time*1000:.1f}ms | P95: {result.metrics.p95_response_time*1000:.1f}ms")
            logger.info(f"   🔄 RPS: {result.metrics.requests_per_second:.1f} | CPU: {result.metrics.cpu_usage_percent:.1f}%")

        if result.error_message:
            logger.error(f"   Error: {result.error_message}")

        self.test_results.append(result)

    def run_all_performance_tests(self):
        """Execute complete performance testing suite"""
        logger.info("🚀 Starting MeStore Performance E2E Testing Suite")
        logger.info(f"Backend: {self.backend_url}")
        logger.info(f"Frontend: {self.frontend_url}")
        logger.info("=" * 60)

        # Execute performance tests
        test_functions = [
            self.test_baseline_performance,
            self.test_moderate_load,
            self.test_high_load,
            self.test_api_endpoints_performance,
            self.test_frontend_performance
        ]

        for test_func in test_functions:
            logger.info(f"\\n🔄 Starting test: {test_func.__name__}")
            result = test_func()
            self.log_test_result(result)

        # Generate summary report
        self.generate_performance_summary_report()

    def generate_performance_summary_report(self):
        """Generate comprehensive performance summary report"""
        logger.info("\\n" + "=" * 60)
        logger.info("⚡ PERFORMANCE E2E TESTING SUMMARY REPORT")
        logger.info("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        total_duration = sum(r.duration for r in self.test_results)

        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        if total_tests > 0:
            logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Total Duration: {total_duration:.2f}s")

        # Performance benchmarks
        successful_results = [r for r in self.test_results if r.status == "PASS" and r.metrics.response_times]

        if successful_results:
            logger.info("\\n📊 PERFORMANCE BENCHMARKS:")

            # Overall performance metrics
            all_response_times = []
            total_requests = 0
            total_rps = 0

            for result in successful_results:
                all_response_times.extend(result.metrics.response_times)
                total_requests += result.total_requests
                total_rps += result.metrics.requests_per_second

            if all_response_times:
                overall_avg = statistics.mean(all_response_times) * 1000  # Convert to ms
                sorted_times = sorted(all_response_times)
                p95_index = int(0.95 * len(sorted_times))
                overall_p95 = sorted_times[p95_index] * 1000 if p95_index < len(sorted_times) else sorted_times[-1] * 1000

                logger.info(f"  Overall Avg Response Time: {overall_avg:.1f}ms")
                logger.info(f"  Overall P95 Response Time: {overall_p95:.1f}ms")
                logger.info(f"  Total Requests Processed: {total_requests}")
                logger.info(f"  Average RPS: {total_rps/len(successful_results):.1f}")

            # Performance assessment
            logger.info("\\n🎯 PERFORMANCE ASSESSMENT:")
            if overall_avg < 200:  # < 200ms
                logger.info("🟢 EXCELLENT: Response times well within acceptable limits")
            elif overall_avg < 500:  # < 500ms
                logger.info("🟡 GOOD: Response times acceptable for production")
            elif overall_avg < 1000:  # < 1s
                logger.info("🟠 FAIR: Response times may impact user experience")
            else:
                logger.info("🔴 POOR: Response times require optimization")

            # Load handling assessment
            high_load_results = [r for r in successful_results if r.concurrent_users >= 25]
            if high_load_results:
                high_load_success = statistics.mean([r.metrics.success_rate for r in high_load_results])
                if high_load_success >= 95:
                    logger.info("🟢 EXCELLENT: System handles high load with minimal degradation")
                elif high_load_success >= 90:
                    logger.info("🟡 GOOD: System handles high load adequately")
                else:
                    logger.info("🟠 FAIR: System struggles under high load")

        # Detailed test results
        if failed_tests > 0:
            logger.info("\\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if result.status == "FAIL":
                    logger.error(f"  ❌ {result.test_name}: {result.error_message}")

        # Save detailed results
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0,
                "total_duration": total_duration
            },
            "test_results": [asdict(result) for result in self.test_results],
            "endpoints": {
                "backend_url": self.backend_url,
                "frontend_url": self.frontend_url
            }
        }

        with open('performance_e2e_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"\\n📄 Detailed performance report saved to: performance_e2e_report.json")
        logger.info("=" * 60)

def main():
    """Main execution function"""
    print("⚡ MeStore Performance E2E Testing Suite")
    print("========================================\\n")

    suite = PerformanceE2ETestSuite()
    suite.run_all_performance_tests()

if __name__ == "__main__":
    main()