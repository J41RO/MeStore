# ~/tests/performance/load_testing_suite.py
# ---------------------------------------------------------------------------------------------
# MeStore - Load Testing Suite
# Copyright (c) 2025 Performance Optimization AI. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: load_testing_suite.py
# Ruta: ~/tests/performance/load_testing_suite.py
# Autor: Performance Optimization AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Comprehensive load testing suite for MeStore marketplace
#            Performance benchmarking, SLA validation, and scalability testing
#
# Características:
# - Multi-scenario load testing with realistic user patterns
# - Performance benchmarking with SLA validation
# - Scalability testing with gradual load increase
# - API endpoint stress testing
# - Database performance under load
# - Cache performance validation
# - Search performance benchmarking
# - Real-time performance monitoring during tests
#
# ---------------------------------------------------------------------------------------------

"""
Load Testing Suite para MeStore Marketplace.

Este módulo implementa testing comprehensivo de carga y performance:
- Testing multi-escenario con patrones realistas de usuario
- Benchmarking de performance con validación de SLA
- Testing de escalabilidad con incremento gradual de carga
- Stress testing de endpoints API
- Performance de base de datos bajo carga
- Validación de performance de cache
- Benchmarking de performance de búsquedas
- Monitoreo de performance en tiempo real durante tests
"""

import asyncio
import json
import logging
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import aiohttp
import pytest
from dataclasses import dataclass

from app.core.config import settings
from app.services.cache_service import cache_service
from app.services.performance_monitoring_service import performance_monitoring_service

logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Load test result data structure"""
    scenario_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    error_rate: float
    duration_seconds: float
    sla_compliance: Dict[str, bool]


@dataclass
class LoadTestScenario:
    """Load test scenario configuration"""
    name: str
    endpoint: str
    method: str
    payload: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    concurrent_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 10
    expected_response_time_ms: int = 500
    expected_success_rate: float = 99.0


class LoadTestingService:
    """Comprehensive load testing service"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results: List[LoadTestResult] = []

    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "MeStore-LoadTester/1.0"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def run_load_test_scenario(self, scenario: LoadTestScenario) -> LoadTestResult:
        """Run a single load test scenario"""
        logger.info(f"Starting load test scenario: {scenario.name}")

        start_time = time.time()
        response_times = []
        errors = []
        successful_requests = 0

        # Semaphore to control concurrent requests
        semaphore = asyncio.Semaphore(scenario.concurrent_users)

        async def make_request() -> Tuple[float, bool]:
            """Make a single request and return response time and success status"""
            async with semaphore:
                request_start = time.time()
                try:
                    url = f"{self.base_url}{scenario.endpoint}"

                    if scenario.method.upper() == "GET":
                        async with self.session.get(url, headers=scenario.headers) as response:
                            await response.text()  # Consume response body
                            success = 200 <= response.status < 400
                    elif scenario.method.upper() == "POST":
                        async with self.session.post(
                            url,
                            json=scenario.payload,
                            headers=scenario.headers
                        ) as response:
                            await response.text()
                            success = 200 <= response.status < 400
                    else:
                        raise ValueError(f"Unsupported method: {scenario.method}")

                    response_time = (time.time() - request_start) * 1000
                    return response_time, success

                except Exception as e:
                    response_time = (time.time() - request_start) * 1000
                    errors.append(str(e))
                    return response_time, False

        # Calculate request intervals for duration-based testing
        total_duration = scenario.duration_seconds
        ramp_up_duration = scenario.ramp_up_seconds

        tasks = []
        current_time = 0

        # Ramp-up phase
        while current_time < ramp_up_duration:
            # Gradually increase concurrent users
            current_users = int((current_time / ramp_up_duration) * scenario.concurrent_users)
            current_users = max(1, current_users)

            for _ in range(current_users):
                task = asyncio.create_task(make_request())
                tasks.append(task)

            await asyncio.sleep(1)  # 1 second intervals
            current_time += 1

        # Steady state phase
        while current_time < total_duration:
            for _ in range(scenario.concurrent_users):
                task = asyncio.create_task(make_request())
                tasks.append(task)

            await asyncio.sleep(1)
            current_time += 1

        # Wait for all requests to complete
        logger.info(f"Waiting for {len(tasks)} requests to complete...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in results:
            if isinstance(result, tuple):
                response_time, success = result
                response_times.append(response_time)
                if success:
                    successful_requests += 1

        # Calculate metrics
        total_requests = len(response_times)
        failed_requests = total_requests - successful_requests
        actual_duration = time.time() - start_time

        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            sorted_times = sorted(response_times)
            p95_response_time = sorted_times[int(0.95 * len(sorted_times))]
            p99_response_time = sorted_times[int(0.99 * len(sorted_times))]
        else:
            avg_response_time = 0
            min_response_time = 0
            max_response_time = 0
            p95_response_time = 0
            p99_response_time = 0

        requests_per_second = total_requests / max(actual_duration, 1)
        error_rate = (failed_requests / max(total_requests, 1)) * 100

        # SLA compliance
        sla_compliance = {
            "avg_response_time": avg_response_time <= scenario.expected_response_time_ms,
            "p95_response_time": p95_response_time <= scenario.expected_response_time_ms * 1.5,
            "success_rate": (100 - error_rate) >= scenario.expected_success_rate
        }

        result = LoadTestResult(
            scenario_name=scenario.name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            duration_seconds=actual_duration,
            sla_compliance=sla_compliance
        )

        self.test_results.append(result)
        logger.info(f"Completed load test scenario: {scenario.name}")
        return result

    async def run_comprehensive_load_test(self) -> Dict[str, Any]:
        """Run comprehensive load test suite"""
        logger.info("Starting comprehensive load test suite")

        # Define test scenarios
        scenarios = [
            # Product listing performance
            LoadTestScenario(
                name="Product Listing - Light Load",
                endpoint="/api/v1/productos",
                method="GET",
                concurrent_users=10,
                duration_seconds=60,
                expected_response_time_ms=200
            ),
            LoadTestScenario(
                name="Product Listing - Heavy Load",
                endpoint="/api/v1/productos",
                method="GET",
                concurrent_users=50,
                duration_seconds=120,
                expected_response_time_ms=500
            ),

            # Search performance
            LoadTestScenario(
                name="Search - Light Load",
                endpoint="/api/v1/search?q=smartphone",
                method="GET",
                concurrent_users=15,
                duration_seconds=60,
                expected_response_time_ms=100
            ),
            LoadTestScenario(
                name="Search - Heavy Load",
                endpoint="/api/v1/search?q=laptop",
                method="GET",
                concurrent_users=75,
                duration_seconds=120,
                expected_response_time_ms=200
            ),

            # Category browsing
            LoadTestScenario(
                name="Category Browsing",
                endpoint="/api/v1/categories",
                method="GET",
                concurrent_users=20,
                duration_seconds=60,
                expected_response_time_ms=150
            ),

            # Authentication stress test
            LoadTestScenario(
                name="Authentication Load",
                endpoint="/api/v1/auth/login",
                method="POST",
                payload={
                    "email": "test@example.com",
                    "password": "testpassword"
                },
                concurrent_users=30,
                duration_seconds=60,
                expected_response_time_ms=300
            ),

            # Vendor dashboard
            LoadTestScenario(
                name="Vendor Dashboard",
                endpoint="/api/v1/vendor/products",
                method="GET",
                headers={"Authorization": "Bearer test-token"},
                concurrent_users=25,
                duration_seconds=60,
                expected_response_time_ms=250
            )
        ]

        # Run all scenarios
        results = []
        for scenario in scenarios:
            try:
                result = await self.run_load_test_scenario(scenario)
                results.append(result)

                # Cool down between scenarios
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error running scenario {scenario.name}: {e}")
                continue

        # Generate comprehensive report
        report = await self._generate_load_test_report(results)

        logger.info("Comprehensive load test suite completed")
        return report

    async def run_scalability_test(self) -> Dict[str, Any]:
        """Run scalability test with gradual load increase"""
        logger.info("Starting scalability test")

        endpoint = "/api/v1/productos"
        user_levels = [5, 10, 25, 50, 100, 200]
        results = []

        for user_count in user_levels:
            scenario = LoadTestScenario(
                name=f"Scalability Test - {user_count} users",
                endpoint=endpoint,
                method="GET",
                concurrent_users=user_count,
                duration_seconds=30,  # Shorter duration for scalability test
                ramp_up_seconds=5,
                expected_response_time_ms=500
            )

            result = await self.run_load_test_scenario(scenario)
            results.append(result)

            # Short break between tests
            await asyncio.sleep(10)

        # Analyze scalability
        scalability_analysis = self._analyze_scalability(results)

        return {
            "test_type": "scalability",
            "results": [self._result_to_dict(r) for r in results],
            "analysis": scalability_analysis,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def stress_test_endpoints(self) -> Dict[str, Any]:
        """Stress test critical endpoints to find breaking points"""
        logger.info("Starting stress test")

        # Critical endpoints to stress test
        critical_endpoints = [
            ("/api/v1/productos", "GET"),
            ("/api/v1/search", "GET"),
            ("/api/v1/categories", "GET")
        ]

        results = {}

        for endpoint, method in critical_endpoints:
            logger.info(f"Stress testing {method} {endpoint}")

            # Find breaking point by gradually increasing load
            breaking_point = await self._find_breaking_point(endpoint, method)
            results[f"{method} {endpoint}"] = breaking_point

        return {
            "test_type": "stress_test",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _find_breaking_point(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Find the breaking point for an endpoint"""
        user_counts = [10, 25, 50, 100, 200, 400, 800]
        breaking_point_data = []

        for user_count in user_counts:
            scenario = LoadTestScenario(
                name=f"Stress {endpoint} - {user_count} users",
                endpoint=endpoint,
                method=method,
                concurrent_users=user_count,
                duration_seconds=20,
                expected_response_time_ms=1000,
                expected_success_rate=95.0
            )

            result = await self.run_load_test_scenario(scenario)

            breaking_point_data.append({
                "users": user_count,
                "avg_response_time": result.avg_response_time,
                "error_rate": result.error_rate,
                "rps": result.requests_per_second,
                "sla_compliant": all(result.sla_compliance.values())
            })

            # Check if we've found breaking point
            if result.error_rate > 5.0 or result.avg_response_time > 2000:
                logger.info(f"Breaking point found at {user_count} users")
                break

            await asyncio.sleep(5)

        return {
            "endpoint": endpoint,
            "method": method,
            "breaking_point_data": breaking_point_data,
            "estimated_max_users": self._estimate_max_capacity(breaking_point_data)
        }

    def _estimate_max_capacity(self, data: List[Dict[str, Any]]) -> int:
        """Estimate maximum capacity based on test data"""
        compliant_data = [d for d in data if d["sla_compliant"]]
        if compliant_data:
            return max(d["users"] for d in compliant_data)
        return 0

    def _analyze_scalability(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Analyze scalability test results"""
        if not results:
            return {}

        user_counts = []
        response_times = []
        throughputs = []
        error_rates = []

        for result in results:
            # Extract user count from scenario name
            user_count = int(result.scenario_name.split(" - ")[1].split(" ")[0])
            user_counts.append(user_count)
            response_times.append(result.avg_response_time)
            throughputs.append(result.requests_per_second)
            error_rates.append(result.error_rate)

        # Calculate scalability metrics
        linear_scalability_score = self._calculate_linear_scalability_score(user_counts, throughputs)
        performance_degradation = self._calculate_performance_degradation(user_counts, response_times)

        return {
            "linear_scalability_score": linear_scalability_score,
            "performance_degradation": performance_degradation,
            "max_tested_users": max(user_counts),
            "peak_throughput_rps": max(throughputs),
            "scalability_rating": self._rate_scalability(linear_scalability_score)
        }

    def _calculate_linear_scalability_score(self, users: List[int], throughputs: List[float]) -> float:
        """Calculate how close to linear scalability the system performs"""
        if len(users) < 2:
            return 0.0

        # Calculate expected linear throughput
        base_users = users[0]
        base_throughput = throughputs[0]

        linear_scores = []
        for i in range(1, len(users)):
            expected_throughput = base_throughput * (users[i] / base_users)
            actual_throughput = throughputs[i]
            score = min(1.0, actual_throughput / expected_throughput)
            linear_scores.append(score)

        return statistics.mean(linear_scores) if linear_scores else 0.0

    def _calculate_performance_degradation(self, users: List[int], response_times: List[float]) -> float:
        """Calculate performance degradation as load increases"""
        if len(response_times) < 2:
            return 0.0

        base_time = response_times[0]
        max_time = max(response_times)

        return ((max_time - base_time) / base_time) * 100

    def _rate_scalability(self, score: float) -> str:
        """Rate scalability based on score"""
        if score >= 0.9:
            return "EXCELLENT"
        elif score >= 0.7:
            return "GOOD"
        elif score >= 0.5:
            return "FAIR"
        else:
            return "POOR"

    async def _generate_load_test_report(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Generate comprehensive load test report"""
        if not results:
            return {"error": "No test results available"}

        # Calculate aggregate metrics
        total_requests = sum(r.total_requests for r in results)
        total_successful = sum(r.successful_requests for r in results)
        avg_response_time = statistics.mean(r.avg_response_time for r in results)
        avg_p95_time = statistics.mean(r.p95_response_time for r in results)
        avg_error_rate = statistics.mean(r.error_rate for r in results)
        total_rps = sum(r.requests_per_second for r in results)

        # SLA compliance analysis
        sla_violations = []
        for result in results:
            for sla_type, compliant in result.sla_compliance.items():
                if not compliant:
                    sla_violations.append({
                        "scenario": result.scenario_name,
                        "sla_type": sla_type,
                        "actual_value": getattr(result, sla_type.replace("_", "_"), "N/A")
                    })

        # Performance rating
        overall_rating = self._calculate_overall_performance_rating(results)

        return {
            "test_type": "comprehensive_load_test",
            "summary": {
                "total_scenarios": len(results),
                "total_requests": total_requests,
                "successful_requests": total_successful,
                "overall_success_rate": (total_successful / max(total_requests, 1)) * 100,
                "avg_response_time_ms": round(avg_response_time, 2),
                "avg_p95_response_time_ms": round(avg_p95_time, 2),
                "avg_error_rate": round(avg_error_rate, 2),
                "total_throughput_rps": round(total_rps, 2),
                "overall_rating": overall_rating
            },
            "detailed_results": [self._result_to_dict(r) for r in results],
            "sla_violations": sla_violations,
            "recommendations": self._generate_performance_recommendations(results),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_overall_performance_rating(self, results: List[LoadTestResult]) -> str:
        """Calculate overall performance rating"""
        scores = []

        for result in results:
            # Response time score (lower is better)
            response_score = max(0, 1 - (result.avg_response_time / 1000))  # 1s = 0 score

            # Success rate score
            success_score = (100 - result.error_rate) / 100

            # SLA compliance score
            sla_score = sum(1 for compliant in result.sla_compliance.values() if compliant) / len(result.sla_compliance)

            # Combined score
            combined_score = (response_score + success_score + sla_score) / 3
            scores.append(combined_score)

        avg_score = statistics.mean(scores)

        if avg_score >= 0.9:
            return "EXCELLENT"
        elif avg_score >= 0.7:
            return "GOOD"
        elif avg_score >= 0.5:
            return "FAIR"
        else:
            return "POOR"

    def _generate_performance_recommendations(self, results: List[LoadTestResult]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        # Analyze results for common issues
        high_response_times = [r for r in results if r.avg_response_time > 500]
        high_error_rates = [r for r in results if r.error_rate > 5]
        low_throughput = [r for r in results if r.requests_per_second < 10]

        if high_response_times:
            recommendations.append(
                f"High response times detected in {len(high_response_times)} scenarios. "
                "Consider implementing response caching and database query optimization."
            )

        if high_error_rates:
            recommendations.append(
                f"High error rates detected in {len(high_error_rates)} scenarios. "
                "Review error handling and implement circuit breakers."
            )

        if low_throughput:
            recommendations.append(
                f"Low throughput detected in {len(low_throughput)} scenarios. "
                "Consider horizontal scaling and load balancing improvements."
            )

        # Check for specific performance patterns
        search_results = [r for r in results if "search" in r.scenario_name.lower()]
        if search_results and any(r.avg_response_time > 200 for r in search_results):
            recommendations.append(
                "Search performance needs optimization. Implement search result caching "
                "and consider search index optimization."
            )

        return recommendations or ["Performance looks good! Continue monitoring for optimization opportunities."]

    def _result_to_dict(self, result: LoadTestResult) -> Dict[str, Any]:
        """Convert LoadTestResult to dictionary"""
        return {
            "scenario_name": result.scenario_name,
            "total_requests": result.total_requests,
            "successful_requests": result.successful_requests,
            "failed_requests": result.failed_requests,
            "avg_response_time_ms": round(result.avg_response_time, 2),
            "p95_response_time_ms": round(result.p95_response_time, 2),
            "p99_response_time_ms": round(result.p99_response_time, 2),
            "min_response_time_ms": round(result.min_response_time, 2),
            "max_response_time_ms": round(result.max_response_time, 2),
            "requests_per_second": round(result.requests_per_second, 2),
            "error_rate_percent": round(result.error_rate, 2),
            "duration_seconds": round(result.duration_seconds, 2),
            "sla_compliance": result.sla_compliance
        }


# Test functions for pytest integration
@pytest.mark.asyncio
async def test_product_listing_performance():
    """Test product listing performance"""
    async with LoadTestingService() as load_tester:
        scenario = LoadTestScenario(
            name="Product Listing Performance Test",
            endpoint="/api/v1/productos",
            method="GET",
            concurrent_users=20,
            duration_seconds=30,
            expected_response_time_ms=300
        )

        result = await load_tester.run_load_test_scenario(scenario)

        # Assert SLA compliance
        assert result.sla_compliance["avg_response_time"], f"Average response time {result.avg_response_time}ms exceeds SLA"
        assert result.sla_compliance["success_rate"], f"Success rate {100 - result.error_rate}% below SLA"
        assert result.avg_response_time < 500, "Average response time must be under 500ms"


@pytest.mark.asyncio
async def test_search_performance():
    """Test search performance"""
    async with LoadTestingService() as load_tester:
        scenario = LoadTestScenario(
            name="Search Performance Test",
            endpoint="/api/v1/search?q=test",
            method="GET",
            concurrent_users=30,
            duration_seconds=30,
            expected_response_time_ms=200
        )

        result = await load_tester.run_load_test_scenario(scenario)

        # Assert search-specific requirements
        assert result.avg_response_time < 300, "Search response time must be under 300ms"
        assert result.error_rate < 2, "Search error rate must be under 2%"


@pytest.mark.asyncio
async def test_comprehensive_load_test():
    """Run comprehensive load test suite"""
    async with LoadTestingService() as load_tester:
        report = await load_tester.run_comprehensive_load_test()

        # Assert overall system performance
        assert report["summary"]["overall_success_rate"] >= 95, "Overall success rate must be >= 95%"
        assert report["summary"]["avg_response_time_ms"] < 1000, "Average response time must be under 1s"
        assert len(report["sla_violations"]) < 3, "Too many SLA violations detected"


if __name__ == "__main__":
    # Run load test when executed directly
    async def main():
        async with LoadTestingService() as load_tester:
            print("Running comprehensive load test...")
            report = await load_tester.run_comprehensive_load_test()

            print("\n" + "="*80)
            print("LOAD TEST REPORT")
            print("="*80)
            print(json.dumps(report, indent=2))

    asyncio.run(main())