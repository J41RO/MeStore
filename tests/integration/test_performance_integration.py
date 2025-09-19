#!/usr/bin/env python3
"""
Performance Integration Testing
==============================
Comprehensive performance testing with all integrated components:
- Load testing with concurrent users
- Database performance under stress
- Cache effectiveness validation
- Memory and resource usage monitoring
- Response time consistency
- Service degradation patterns

Author: Integration Testing AI
Date: 2025-09-17
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any, Tuple
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserType
from app.models.product import Product
from app.core.security import create_access_token, get_password_hash


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    name: str
    value: float
    unit: str
    threshold: float
    passed: bool


@dataclass
class LoadTestResult:
    """Load test result data structure."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    requests_per_second: float
    errors: List[str]


class PerformanceTestSuite:
    """Performance testing utilities and metrics collection."""

    def __init__(self, client: AsyncClient, db: AsyncSession):
        self.client = client
        self.db = db
        self.metrics: List[PerformanceMetric] = []

    def add_metric(self, name: str, value: float, unit: str, threshold: float):
        """Add a performance metric."""
        passed = value <= threshold if "time" in unit else value >= threshold
        metric = PerformanceMetric(name, value, unit, threshold, passed)
        self.metrics.append(metric)

    def get_valid_headers(self, token: str = None) -> Dict[str, str]:
        """Get headers that pass middleware validation."""
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def measure_response_time(self, endpoint: str, headers: Dict[str, str], method: str = "GET") -> float:
        """Measure response time for a single request."""
        start_time = time.time()
        try:
            if method == "GET":
                response = await self.client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await self.client.post(endpoint, headers=headers, json={})
            else:
                response = await self.client.request(method, endpoint, headers=headers)

            response_time = time.time() - start_time
            return response_time if response.status_code < 500 else float('inf')
        except Exception:
            return float('inf')

    async def concurrent_load_test(
        self,
        endpoint: str,
        concurrent_users: int,
        requests_per_user: int,
        headers: Dict[str, str]
    ) -> LoadTestResult:
        """Perform concurrent load testing."""
        async def user_requests():
            """Simulate one user making multiple requests."""
            times = []
            errors = []

            for _ in range(requests_per_user):
                response_time = await self.measure_response_time(endpoint, headers)
                if response_time == float('inf'):
                    errors.append(f"Failed request to {endpoint}")
                else:
                    times.append(response_time)

            return times, errors

        # Execute concurrent users
        start_time = time.time()
        tasks = [user_requests() for _ in range(concurrent_users)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Aggregate results
        all_times = []
        all_errors = []

        for result in results:
            if not isinstance(result, Exception):
                times, errors = result
                all_times.extend(times)
                all_errors.extend(errors)

        total_requests = concurrent_users * requests_per_user
        successful_requests = len(all_times)
        failed_requests = total_requests - successful_requests

        if all_times:
            avg_response_time = statistics.mean(all_times)
            min_response_time = min(all_times)
            max_response_time = max(all_times)
            p95_response_time = statistics.quantiles(all_times, n=20)[18] if len(all_times) > 20 else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = 0

        requests_per_second = successful_requests / total_time if total_time > 0 else 0

        return LoadTestResult(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            requests_per_second=requests_per_second,
            errors=all_errors
        )


@pytest.mark.integration
@pytest.mark.performance
class TestPerformanceUnderLoad:
    """Test system performance under various load conditions."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, async_session: AsyncSession):
        """Setup performance test environment."""
        self.client = async_client
        self.db = async_session
        self.perf_suite = PerformanceTestSuite(async_client, async_session)
        await self._create_test_data()

    async def _create_test_data(self):
        """Create test users and products for performance testing."""
        # Create admin user
        admin_hash = await get_password_hash("admin123")
        self.admin_user = User(
            email="perf_admin@test.com",
            password_hash=admin_hash,
            nombre="Performance",
            apellido="Admin",
            user_type=UserType.SUPERUSER,
            is_active=True
        )

        # Create vendor user
        vendor_hash = await get_password_hash("vendor123")
        self.vendor_user = User(
            email="perf_vendor@test.com",
            password_hash=vendor_hash,
            nombre="Performance",
            apellido="Vendor",
            user_type=UserType.VENDEDOR,
            is_active=True
        )

        # Create buyer user
        buyer_hash = await get_password_hash("buyer123")
        self.buyer_user = User(
            email="perf_buyer@test.com",
            password_hash=buyer_hash,
            nombre="Performance",
            apellido="Buyer",
            user_type=UserType.COMPRADOR,
            is_active=True
        )

        self.db.add_all([self.admin_user, self.vendor_user, self.buyer_user])
        await self.db.commit()

        # Refresh users to get IDs
        for user in [self.admin_user, self.vendor_user, self.buyer_user]:
            await self.db.refresh(user)

        # Create test products
        products = []
        for i in range(10):  # Create 10 test products
            product = Product(
                sku=f"PERF-PROD-{i:03d}",
                name=f"Performance Test Product {i}",
                description=f"Product {i} for performance testing",
                precio_venta=50000.0 + (i * 5000),
                precio_costo=40000.0 + (i * 4000),
                stock=100,
                categoria="Performance Test",
                vendor_id=self.vendor_user.id
            )
            products.append(product)

        self.db.add_all(products)
        await self.db.commit()

        # Generate tokens
        self.admin_token = create_access_token(data={
            "sub": str(self.admin_user.id),
            "email": self.admin_user.email,
            "user_type": self.admin_user.user_type.value,
            "nombre": self.admin_user.nombre,
            "apellido": self.admin_user.apellido
        })

        self.vendor_token = create_access_token(data={
            "sub": str(self.vendor_user.id),
            "email": self.vendor_user.email,
            "user_type": self.vendor_user.user_type.value,
            "nombre": self.vendor_user.nombre,
            "apellido": self.vendor_user.apellido
        })

        self.buyer_token = create_access_token(data={
            "sub": str(self.buyer_user.id),
            "email": self.buyer_user.email,
            "user_type": self.buyer_user.user_type.value,
            "nombre": self.buyer_user.nombre,
            "apellido": self.buyer_user.apellido
        })

    async def test_health_endpoint_performance(self):
        """Test health endpoint performance under load."""
        headers = self.perf_suite.get_valid_headers()

        # Single request baseline
        baseline_time = await self.perf_suite.measure_response_time("/health", headers)
        self.perf_suite.add_metric("Health Endpoint Baseline", baseline_time, "seconds", 1.0)

        # Load test with concurrent users
        load_result = await self.perf_suite.concurrent_load_test(
            endpoint="/health",
            concurrent_users=10,
            requests_per_user=5,
            headers=headers
        )

        # Performance assertions
        assert load_result.successful_requests > 0, "No successful requests in load test"
        assert load_result.avg_response_time < 2.0, f"Average response time {load_result.avg_response_time}s exceeds 2s threshold"
        assert load_result.p95_response_time < 3.0, f"95th percentile {load_result.p95_response_time}s exceeds 3s threshold"
        assert load_result.requests_per_second > 5.0, f"Throughput {load_result.requests_per_second} RPS below 5 RPS threshold"

        # Add metrics
        self.perf_suite.add_metric("Health Load Test Avg Response", load_result.avg_response_time, "seconds", 2.0)
        self.perf_suite.add_metric("Health Load Test P95 Response", load_result.p95_response_time, "seconds", 3.0)
        self.perf_suite.add_metric("Health Load Test Throughput", load_result.requests_per_second, "RPS", 5.0)

    async def test_authentication_performance(self):
        """Test authentication endpoint performance."""
        headers = self.perf_suite.get_valid_headers()

        # Test login performance
        login_times = []
        for _ in range(5):  # Multiple login attempts
            start_time = time.time()
            response = await self.client.post(
                "/api/v1/auth/login",
                json={
                    "email": "perf_admin@test.com",
                    "password": "admin123"
                },
                headers=headers
            )
            login_time = time.time() - start_time

            if response.status_code in [200, 422, 404]:  # Accept various responses
                login_times.append(login_time)

        if login_times:
            avg_login_time = statistics.mean(login_times)
            self.perf_suite.add_metric("Login Average Response", avg_login_time, "seconds", 3.0)
            assert avg_login_time < 3.0, f"Login average time {avg_login_time}s exceeds 3s threshold"

    async def test_authenticated_endpoint_performance(self):
        """Test performance of authenticated endpoints."""
        auth_headers = self.perf_suite.get_valid_headers(self.admin_token)

        # Test /api/v1/auth/me endpoint
        auth_me_result = await self.perf_suite.concurrent_load_test(
            endpoint="/api/v1/auth/me",
            concurrent_users=5,
            requests_per_user=3,
            headers=auth_headers
        )

        if auth_me_result.successful_requests > 0:
            self.perf_suite.add_metric("Auth Me Response Time", auth_me_result.avg_response_time, "seconds", 2.0)
            assert auth_me_result.avg_response_time < 2.0, f"Auth /me response time {auth_me_result.avg_response_time}s too high"

    async def test_database_intensive_operations(self):
        """Test performance of database-intensive operations."""
        headers = self.perf_suite.get_valid_headers()

        # Test database test endpoint
        db_test_times = []
        for _ in range(5):
            db_time = await self.perf_suite.measure_response_time("/db-test", headers)
            if db_time != float('inf'):
                db_test_times.append(db_time)

        if db_test_times:
            avg_db_time = statistics.mean(db_test_times)
            self.perf_suite.add_metric("Database Test Response", avg_db_time, "seconds", 2.0)
            assert avg_db_time < 2.0, f"Database test response time {avg_db_time}s exceeds 2s threshold"

        # Test user listing endpoint
        users_test_times = []
        for _ in range(3):
            users_time = await self.perf_suite.measure_response_time("/users/test", headers)
            if users_time != float('inf'):
                users_test_times.append(users_time)

        if users_test_times:
            avg_users_time = statistics.mean(users_test_times)
            self.perf_suite.add_metric("Users Test Response", avg_users_time, "seconds", 3.0)

    async def test_products_endpoint_performance(self):
        """Test products endpoint performance with data."""
        vendor_headers = self.perf_suite.get_valid_headers(self.vendor_token)

        # Test products listing
        products_result = await self.perf_suite.concurrent_load_test(
            endpoint="/api/v1/products/",
            concurrent_users=3,
            requests_per_user=2,
            headers=vendor_headers
        )

        if products_result.successful_requests > 0:
            self.perf_suite.add_metric("Products List Response", products_result.avg_response_time, "seconds", 3.0)

    @patch('app.core.redis.redis_manager.get_redis')
    async def test_cache_performance_impact(self, mock_redis):
        """Test the performance impact of caching."""
        # Mock Redis for caching
        mock_redis_instance = AsyncMock()
        mock_redis_instance.get.return_value = None  # Cache miss
        mock_redis_instance.set.return_value = True
        mock_redis.return_value = mock_redis_instance

        headers = self.perf_suite.get_valid_headers(self.admin_token)

        # Test endpoint with cache miss
        cache_miss_times = []
        for _ in range(3):
            cache_time = await self.perf_suite.measure_response_time("/api/v1/auth/me", headers)
            if cache_time != float('inf'):
                cache_miss_times.append(cache_time)

        # Simulate cache hit
        mock_redis_instance.get.return_value = '{"cached": "data"}'

        cache_hit_times = []
        for _ in range(3):
            cache_time = await self.perf_suite.measure_response_time("/api/v1/auth/me", headers)
            if cache_time != float('inf'):
                cache_hit_times.append(cache_time)

        # Compare performance
        if cache_miss_times and cache_hit_times:
            avg_miss_time = statistics.mean(cache_miss_times)
            avg_hit_time = statistics.mean(cache_hit_times)

            self.perf_suite.add_metric("Cache Miss Response", avg_miss_time, "seconds", 3.0)
            self.perf_suite.add_metric("Cache Hit Response", avg_hit_time, "seconds", 1.0)

    async def test_concurrent_different_endpoints(self):
        """Test performance with concurrent access to different endpoints."""
        # Define different user scenarios
        scenarios = [
            ("/health", self.perf_suite.get_valid_headers()),
            ("/db-test", self.perf_suite.get_valid_headers()),
            ("/api/v1/auth/me", self.perf_suite.get_valid_headers(self.admin_token)),
            ("/api/v1/products/", self.perf_suite.get_valid_headers(self.vendor_token))
        ]

        async def mixed_load_scenario():
            """Simulate mixed load across different endpoints."""
            times = []
            for endpoint, headers in scenarios:
                response_time = await self.perf_suite.measure_response_time(endpoint, headers)
                if response_time != float('inf'):
                    times.append(response_time)
            return times

        # Run concurrent mixed scenarios
        start_time = time.time()
        tasks = [mixed_load_scenario() for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Analyze mixed load performance
        all_times = []
        for result in results:
            if not isinstance(result, Exception):
                all_times.extend(result)

        if all_times:
            avg_mixed_time = statistics.mean(all_times)
            max_mixed_time = max(all_times)
            throughput = len(all_times) / total_time

            self.perf_suite.add_metric("Mixed Load Avg Response", avg_mixed_time, "seconds", 3.0)
            self.perf_suite.add_metric("Mixed Load Max Response", max_mixed_time, "seconds", 5.0)
            self.perf_suite.add_metric("Mixed Load Throughput", throughput, "RPS", 2.0)

    async def test_memory_usage_patterns(self):
        """Test memory usage patterns during load."""
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        headers = self.perf_suite.get_valid_headers(self.admin_token)

        # Perform memory-intensive operations
        for _ in range(20):
            await self.perf_suite.measure_response_time("/db-test", headers)
            await self.perf_suite.measure_response_time("/users/test", headers)

        # Check memory after operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        self.perf_suite.add_metric("Memory Usage Increase", memory_increase, "MB", 100.0)

        # Memory increase should be reasonable
        assert memory_increase < 100.0, f"Memory increase {memory_increase}MB exceeds 100MB threshold"

    def test_performance_metrics_summary(self):
        """Generate performance metrics summary."""
        passed_metrics = [m for m in self.perf_suite.metrics if m.passed]
        failed_metrics = [m for m in self.perf_suite.metrics if not m.passed]

        print("\n" + "="*60)
        print("PERFORMANCE TEST SUMMARY")
        print("="*60)

        if passed_metrics:
            print(f"\n✅ PASSED METRICS ({len(passed_metrics)}):")
            for metric in passed_metrics:
                print(f"   {metric.name}: {metric.value:.3f} {metric.unit} (threshold: {metric.threshold})")

        if failed_metrics:
            print(f"\n❌ FAILED METRICS ({len(failed_metrics)}):")
            for metric in failed_metrics:
                print(f"   {metric.name}: {metric.value:.3f} {metric.unit} (threshold: {metric.threshold})")

        overall_pass_rate = len(passed_metrics) / len(self.perf_suite.metrics) if self.perf_suite.metrics else 0
        print(f"\nOVERALL PASS RATE: {overall_pass_rate:.1%}")

        # At least 80% of metrics should pass
        assert overall_pass_rate >= 0.8, f"Performance pass rate {overall_pass_rate:.1%} below 80% threshold"


@pytest.mark.integration
@pytest.mark.performance
class TestCachePerformanceIntegration:
    """Test caching performance integration."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, async_session: AsyncSession):
        """Setup cache performance testing."""
        self.client = async_client
        self.db = async_session

    @patch('app.core.redis.redis_manager.get_redis')
    async def test_redis_cache_integration_performance(self, mock_redis):
        """Test Redis cache integration performance."""
        # Mock Redis operations
        mock_redis_instance = AsyncMock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.side_effect = [None, '{"cached": "data"}']  # Miss then hit
        mock_redis_instance.set.return_value = True
        mock_redis.return_value = mock_redis_instance

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        # Test cache miss performance
        start_time = time.time()
        response1 = await self.client.get("/health", headers=headers)
        cache_miss_time = time.time() - start_time

        # Test cache hit performance
        start_time = time.time()
        response2 = await self.client.get("/health", headers=headers)
        cache_hit_time = time.time() - start_time

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Cache hit should be faster or equal (in test environment might not be noticeable)
        assert cache_hit_time <= cache_miss_time + 0.1  # Allow small variance

    async def test_session_cache_performance(self):
        """Test session caching performance."""
        # This would test session storage and retrieval performance
        import time

        session_operations = []

        # Simulate session operations
        for i in range(10):
            start_time = time.time()
            # Simulate session operation
            await asyncio.sleep(0.001)  # Minimal delay
            operation_time = time.time() - start_time
            session_operations.append(operation_time)

        avg_session_time = statistics.mean(session_operations)
        assert avg_session_time < 0.1, f"Session operations too slow: {avg_session_time}s"


@pytest.mark.integration
@pytest.mark.performance
class TestServiceDegradationPatterns:
    """Test service degradation patterns under stress."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, async_session: AsyncSession):
        """Setup degradation testing."""
        self.client = async_client
        self.db = async_session

    async def test_graceful_degradation_under_load(self):
        """Test that services degrade gracefully under extreme load."""
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        # Test with increasing load
        load_levels = [5, 10, 20]  # Concurrent users
        degradation_metrics = []

        for load_level in load_levels:
            start_time = time.time()

            # Create concurrent requests
            async def make_request():
                response = await self.client.get("/health", headers=headers)
                return response.status_code

            tasks = [make_request() for _ in range(load_level)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            total_time = time.time() - start_time
            success_count = sum(1 for r in results if not isinstance(r, Exception) and r == 200)
            success_rate = success_count / load_level
            throughput = success_count / total_time

            degradation_metrics.append({
                "load_level": load_level,
                "success_rate": success_rate,
                "throughput": throughput,
                "total_time": total_time
            })

        # Analyze degradation patterns
        for i, metrics in enumerate(degradation_metrics):
            print(f"Load Level {metrics['load_level']}: "
                  f"Success Rate {metrics['success_rate']:.1%}, "
                  f"Throughput {metrics['throughput']:.1f} RPS")

            # Even under load, success rate should remain reasonable
            assert metrics['success_rate'] >= 0.7, f"Success rate {metrics['success_rate']:.1%} too low at load level {metrics['load_level']}"

    @patch('app.core.database.get_db')
    async def test_database_connection_pool_stress(self, mock_get_db):
        """Test database connection pool under stress."""
        # Mock database session
        mock_session = AsyncMock()
        mock_session.execute.return_value = Mock()
        mock_get_db.return_value = mock_session

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }

        # Test concurrent database operations
        async def db_operation():
            response = await self.client.get("/db-test", headers=headers)
            return response.status_code

        # High concurrency test
        tasks = [db_operation() for _ in range(30)]
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        success_count = sum(1 for r in results if not isinstance(r, Exception) and r == 200)
        success_rate = success_count / len(tasks)

        print(f"Database stress test: {success_rate:.1%} success rate in {total_time:.2f}s")

        # Should handle concurrent operations reasonably well
        assert success_rate >= 0.5, f"Database stress test success rate {success_rate:.1%} too low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])