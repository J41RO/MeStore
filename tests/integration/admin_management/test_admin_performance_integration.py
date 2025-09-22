# ~/tests/integration/admin_management/test_admin_performance_integration.py
# ---------------------------------------------------------------------------------------------
# MeStore - Admin Performance Integration Tests
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_admin_performance_integration.py
# Ruta: ~/tests/integration/admin_management/test_admin_performance_integration.py
# Autor: Integration Testing Specialist
# Fecha de Creación: 2025-09-21
# Última Actualización: 2025-09-21
# Versión: 1.0.0
# Propósito: Performance integration benchmarks for admin management system
#
# Performance Integration Testing Coverage:
# - Database performance under admin workloads
# - API endpoint response time benchmarks
# - Concurrent user session performance
# - Cache performance optimization validation
# - Memory usage and leak detection
# - Scalability threshold identification
#
# ---------------------------------------------------------------------------------------------

"""
Admin Performance Integration Tests.

Este módulo prueba el rendimiento del sistema de administración bajo carga:
- Load testing with realistic admin workloads
- Performance degradation threshold identification
- Resource utilization monitoring and optimization
- Concurrent operation performance benchmarks
- Cache hit ratio optimization and validation
- Memory usage patterns and leak detection
"""

import pytest
import asyncio
import time
import uuid
import psutil
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from httpx import AsyncClient
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from concurrent.futures import ThreadPoolExecutor

from app.models.user import User, UserType
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel
from app.services.admin_permission_service import AdminPermissionService
from app.core.security import create_access_token


class PerformanceMetrics:
    """Performance metrics collection and analysis."""

    def __init__(self):
        self.response_times = []
        self.database_query_times = []
        self.memory_usage = []
        self.cpu_usage = []
        self.cache_hit_ratio = []
        self.concurrent_user_counts = []
        self.error_rates = []

    def record_response_time(self, operation: str, duration: float):
        """Record API response time."""
        self.response_times.append({
            'operation': operation,
            'duration': duration,
            'timestamp': datetime.utcnow()
        })

    def record_database_query(self, query_type: str, duration: float):
        """Record database query performance."""
        self.database_query_times.append({
            'query_type': query_type,
            'duration': duration,
            'timestamp': datetime.utcnow()
        })

    def record_system_metrics(self):
        """Record current system resource usage."""
        process = psutil.Process()
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent()

        self.memory_usage.append({
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'timestamp': datetime.utcnow()
        })

        self.cpu_usage.append({
            'percent': cpu_percent,
            'timestamp': datetime.utcnow()
        })

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        response_durations = [r['duration'] for r in self.response_times]
        db_durations = [q['duration'] for q in self.database_query_times]

        return {
            'response_times': {
                'mean': statistics.mean(response_durations) if response_durations else 0,
                'median': statistics.median(response_durations) if response_durations else 0,
                'p95': self._percentile(response_durations, 95) if response_durations else 0,
                'p99': self._percentile(response_durations, 99) if response_durations else 0,
                'max': max(response_durations) if response_durations else 0
            },
            'database_performance': {
                'mean_query_time': statistics.mean(db_durations) if db_durations else 0,
                'total_queries': len(self.database_query_times),
                'queries_per_second': len(self.database_query_times) / 60 if self.database_query_times else 0
            },
            'resource_usage': {
                'peak_memory_mb': max(m['rss'] for m in self.memory_usage) / 1024 / 1024 if self.memory_usage else 0,
                'avg_cpu_percent': statistics.mean(c['percent'] for c in self.cpu_usage) if self.cpu_usage else 0
            },
            'cache_performance': {
                'avg_hit_ratio': statistics.mean(self.cache_hit_ratio) if self.cache_hit_ratio else 0
            }
        }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.performance
class TestAdminPerformanceIntegration:
    """Test admin system performance under various load conditions."""

    @pytest.fixture
    def performance_metrics(self):
        """Performance metrics collection fixture."""
        return PerformanceMetrics()

    async def test_api_endpoint_response_time_benchmarks(
        self,
        async_client: AsyncClient,
        superuser: User,
        multiple_admin_users: List[User],
        system_permissions: List[AdminPermission],
        performance_metrics: PerformanceMetrics,
        integration_test_context
    ):
        """Test API endpoint response time benchmarks under normal load."""
        auth_token = create_access_token(
            data={"sub": str(superuser.id), "email": superuser.email}
        )
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Benchmark 1: User List Endpoint
        for _ in range(10):
            start_time = time.time()
            response = await async_client.get("/api/v1/admin/users", headers=headers)
            duration = time.time() - start_time

            assert response.status_code == 200
            performance_metrics.record_response_time("list_users", duration)
            assert duration < 1.0, f"User list endpoint too slow: {duration}s"

        # Benchmark 2: User Detail Endpoint
        test_user = multiple_admin_users[0]
        for _ in range(10):
            start_time = time.time()
            response = await async_client.get(f"/api/v1/admin/users/{test_user.id}", headers=headers)
            duration = time.time() - start_time

            assert response.status_code == 200
            performance_metrics.record_response_time("user_detail", duration)
            assert duration < 0.5, f"User detail endpoint too slow: {duration}s"

        # Benchmark 3: Permission Grant Endpoint
        permission = system_permissions[0]
        for i in range(5):
            user = multiple_admin_users[i % len(multiple_admin_users)]
            grant_data = {
                "user_id": str(user.id),
                "permission_id": str(permission.id)
            }

            start_time = time.time()
            response = await async_client.post(
                "/api/v1/admin/permissions/grant",
                json=grant_data,
                headers=headers
            )
            duration = time.time() - start_time

            performance_metrics.record_response_time("grant_permission", duration)
            assert duration < 2.0, f"Permission grant too slow: {duration}s"

        # Benchmark 4: Audit Log Endpoint
        for _ in range(5):
            start_time = time.time()
            response = await async_client.get(
                f"/api/v1/admin/audit/user/{test_user.id}",
                headers=headers
            )
            duration = time.time() - start_time

            performance_metrics.record_response_time("audit_logs", duration)
            assert duration < 1.5, f"Audit logs endpoint too slow: {duration}s"

        integration_test_context.record_operation(
            "api_response_time_benchmarks",
            time.time() - time.time()
        )

    async def test_concurrent_user_session_performance(
        self,
        async_client: AsyncClient,
        superuser: User,
        multiple_admin_users: List[User],
        system_permissions: List[AdminPermission],
        performance_metrics: PerformanceMetrics,
        integration_test_context
    ):
        """Test performance under concurrent user sessions."""
        start_test_time = time.time()

        # Create multiple concurrent sessions
        concurrent_sessions = 20

        async def simulate_user_session(session_id: int):
            """Simulate a complete user session."""
            session_start = time.time()

            # Use different users for different sessions
            user = multiple_admin_users[session_id % len(multiple_admin_users)]
            auth_token = create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            headers = {"Authorization": f"Bearer {auth_token}"}

            session_operations = []

            try:
                # Operation 1: Get user profile
                start_op = time.time()
                profile_response = await async_client.get("/api/v1/auth/me", headers=headers)
                session_operations.append(("profile", time.time() - start_op, profile_response.status_code))

                # Operation 2: List users (if permitted)
                start_op = time.time()
                users_response = await async_client.get("/api/v1/admin/users", headers=headers)
                session_operations.append(("list_users", time.time() - start_op, users_response.status_code))

                # Operation 3: Check permissions
                start_op = time.time()
                permissions_response = await async_client.get(
                    f"/api/v1/admin/users/{user.id}/permissions",
                    headers=headers
                )
                session_operations.append(("permissions", time.time() - start_op, permissions_response.status_code))

                # Operation 4: View audit logs
                start_op = time.time()
                audit_response = await async_client.get(
                    f"/api/v1/admin/audit/user/{user.id}",
                    headers=headers
                )
                session_operations.append(("audit", time.time() - start_op, audit_response.status_code))

                session_duration = time.time() - session_start

                return {
                    "session_id": session_id,
                    "user_id": str(user.id),
                    "success": True,
                    "duration": session_duration,
                    "operations": session_operations
                }

            except Exception as e:
                return {
                    "session_id": session_id,
                    "success": False,
                    "error": str(e),
                    "duration": time.time() - session_start
                }

        # Execute concurrent sessions
        tasks = [simulate_user_session(i) for i in range(concurrent_sessions)]
        session_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results
        successful_sessions = [r for r in session_results if isinstance(r, dict) and r.get("success")]
        failed_sessions = [r for r in session_results if isinstance(r, Exception) or (isinstance(r, dict) and not r.get("success"))]

        # Performance assertions
        success_rate = len(successful_sessions) / concurrent_sessions
        assert success_rate >= 0.9, f"Concurrent session success rate too low: {success_rate}"

        if successful_sessions:
            session_durations = [s["duration"] for s in successful_sessions]
            avg_session_duration = statistics.mean(session_durations)
            assert avg_session_duration < 5.0, f"Average session duration too high: {avg_session_duration}s"

            # Record metrics
            for session in successful_sessions:
                for op_name, op_duration, status_code in session["operations"]:
                    performance_metrics.record_response_time(f"concurrent_{op_name}", op_duration)

        performance_metrics.concurrent_user_counts.append(concurrent_sessions)

        integration_test_context.record_operation(
            "concurrent_user_session_performance",
            time.time() - start_test_time
        )

    async def test_database_performance_under_admin_load(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        multiple_admin_users: List[User],
        system_permissions: List[AdminPermission],
        performance_metrics: PerformanceMetrics,
        integration_test_context
    ):
        """Test database performance under realistic admin workloads."""
        start_time = time.time()

        # Test 1: Bulk User Query Performance
        query_start = time.time()
        large_user_query = integration_db_session.query(User).filter(
            User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
        ).limit(100).all()
        query_duration = time.time() - query_start

        performance_metrics.record_database_query("bulk_user_query", query_duration)
        assert query_duration < 1.0, f"Bulk user query too slow: {query_duration}s"

        # Test 2: Complex Permission Query Performance
        query_start = time.time()
        permission_query = integration_db_session.query(AdminPermission).join(
            admin_permission_service_with_redis.admin_user_permissions
        ).filter(
            admin_permission_service_with_redis.admin_user_permissions.c.is_active == True
        ).limit(50).all()
        query_duration = time.time() - query_start

        performance_metrics.record_database_query("complex_permission_query", query_duration)
        assert query_duration < 2.0, f"Complex permission query too slow: {query_duration}s"

        # Test 3: Audit Log Query Performance
        query_start = time.time()
        recent_logs = integration_db_session.query(AdminActivityLog).filter(
            AdminActivityLog.created_at >= datetime.utcnow() - timedelta(days=1)
        ).order_by(AdminActivityLog.created_at.desc()).limit(100).all()
        query_duration = time.time() - query_start

        performance_metrics.record_database_query("audit_log_query", query_duration)
        assert query_duration < 1.5, f"Audit log query too slow: {query_duration}s"

        # Test 4: Concurrent Database Operations
        async def database_operation_task(task_id: int):
            """Simulate concurrent database operations."""
            operation_start = time.time()

            try:
                # Query user count
                user_count = integration_db_session.query(func.count(User.id)).scalar()

                # Query permission count
                permission_count = integration_db_session.query(func.count(AdminPermission.id)).scalar()

                # Query recent activity
                activity_count = integration_db_session.query(func.count(AdminActivityLog.id)).filter(
                    AdminActivityLog.created_at >= datetime.utcnow() - timedelta(hours=1)
                ).scalar()

                operation_duration = time.time() - operation_start
                return {
                    "task_id": task_id,
                    "success": True,
                    "duration": operation_duration,
                    "results": {
                        "user_count": user_count,
                        "permission_count": permission_count,
                        "activity_count": activity_count
                    }
                }

            except Exception as e:
                return {
                    "task_id": task_id,
                    "success": False,
                    "error": str(e),
                    "duration": time.time() - operation_start
                }

        # Execute concurrent database operations
        concurrent_db_tasks = 15
        db_tasks = [database_operation_task(i) for i in range(concurrent_db_tasks)]
        db_results = await asyncio.gather(*db_tasks, return_exceptions=True)

        # Analyze concurrent database performance
        successful_db_ops = [r for r in db_results if isinstance(r, dict) and r.get("success")]
        assert len(successful_db_ops) >= concurrent_db_tasks * 0.9  # 90% success rate

        if successful_db_ops:
            db_durations = [op["duration"] for op in successful_db_ops]
            avg_db_duration = statistics.mean(db_durations)
            assert avg_db_duration < 0.5, f"Average concurrent DB operation too slow: {avg_db_duration}s"

            for duration in db_durations:
                performance_metrics.record_database_query("concurrent_operation", duration)

        integration_test_context.record_operation(
            "database_performance_under_load",
            time.time() - start_time
        )

    async def test_cache_performance_optimization(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        multiple_admin_users: List[User],
        system_permissions: List[AdminPermission],
        integration_redis_client,
        performance_metrics: PerformanceMetrics,
        integration_test_context
    ):
        """Test cache performance and optimization under load."""
        start_time = time.time()

        # Clear cache to start fresh
        integration_redis_client.flushall()

        permission = system_permissions[0]
        test_users = multiple_admin_users[:5]

        # Grant permissions to test users
        for user in test_users:
            await admin_permission_service_with_redis.grant_permission(
                integration_db_session, superuser, user, permission
            )

        # Test 1: Cache Miss Performance (First Access)
        cache_miss_times = []
        for user in test_users:
            start_check = time.time()
            result = await admin_permission_service_with_redis.validate_permission(
                integration_db_session, user,
                permission.resource_type, permission.action, permission.scope
            )
            duration = time.time() - start_check
            cache_miss_times.append(duration)
            assert result is True

        avg_cache_miss_time = statistics.mean(cache_miss_times)

        # Test 2: Cache Hit Performance (Subsequent Access)
        cache_hit_times = []
        for user in test_users:
            start_check = time.time()
            result = await admin_permission_service_with_redis.validate_permission(
                integration_db_session, user,
                permission.resource_type, permission.action, permission.scope
            )
            duration = time.time() - start_check
            cache_hit_times.append(duration)
            assert result is True

        avg_cache_hit_time = statistics.mean(cache_hit_times)

        # Cache hits should be significantly faster
        cache_improvement_ratio = avg_cache_miss_time / avg_cache_hit_time
        assert cache_improvement_ratio >= 2.0, f"Cache improvement ratio too low: {cache_improvement_ratio}"

        # Test 3: Cache Hit Ratio Under Load
        validation_tasks = []
        for _ in range(50):  # Many validations
            user = test_users[_ % len(test_users)]
            task = admin_permission_service_with_redis.validate_permission(
                integration_db_session, user,
                permission.resource_type, permission.action, permission.scope
            )
            validation_tasks.append(task)

        validation_start = time.time()
        validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        total_validation_time = time.time() - validation_start

        successful_validations = [r for r in validation_results if r is True]
        assert len(successful_validations) == 50

        # Average validation time should be closer to cache hit time
        avg_validation_time = total_validation_time / 50
        assert avg_validation_time < avg_cache_miss_time, "Cache not being utilized effectively"

        # Calculate cache hit ratio (approximate)
        cache_hit_ratio = max(0, 1 - (avg_validation_time / avg_cache_miss_time))
        performance_metrics.cache_hit_ratio.append(cache_hit_ratio)
        assert cache_hit_ratio >= 0.7, f"Cache hit ratio too low: {cache_hit_ratio}"

        integration_test_context.record_operation(
            "cache_performance_optimization",
            time.time() - start_time
        )

    async def test_memory_usage_and_leak_detection(
        self,
        async_client: AsyncClient,
        integration_db_session: Session,
        superuser: User,
        multiple_admin_users: List[User],
        performance_metrics: PerformanceMetrics,
        integration_test_context
    ):
        """Test memory usage patterns and detect potential memory leaks."""
        start_time = time.time()

        auth_token = create_access_token(
            data={"sub": str(superuser.id), "email": superuser.email}
        )
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Record initial memory usage
        performance_metrics.record_system_metrics()
        initial_memory = performance_metrics.memory_usage[-1]['rss']

        # Perform memory-intensive operations
        for iteration in range(10):
            # Large user list requests
            for _ in range(5):
                response = await async_client.get("/api/v1/admin/users?limit=100", headers=headers)
                assert response.status_code == 200

            # Permission operations
            for user in multiple_admin_users[:3]:
                permissions_response = await async_client.get(
                    f"/api/v1/admin/users/{user.id}/permissions",
                    headers=headers
                )
                assert permissions_response.status_code == 200

            # Audit log requests
            for user in multiple_admin_users[:3]:
                audit_response = await async_client.get(
                    f"/api/v1/admin/audit/user/{user.id}",
                    headers=headers
                )
                assert audit_response.status_code in [200, 404]

            # Record memory usage after each iteration
            performance_metrics.record_system_metrics()

            # Force garbage collection
            import gc
            gc.collect()

        # Analyze memory usage pattern
        memory_measurements = [m['rss'] for m in performance_metrics.memory_usage]
        final_memory = memory_measurements[-1]
        peak_memory = max(memory_measurements)

        # Memory growth should be reasonable
        memory_growth = final_memory - initial_memory
        memory_growth_mb = memory_growth / 1024 / 1024

        assert memory_growth_mb < 50, f"Excessive memory growth: {memory_growth_mb}MB"

        # Peak memory should not be excessive
        peak_memory_mb = peak_memory / 1024 / 1024
        assert peak_memory_mb < 500, f"Peak memory usage too high: {peak_memory_mb}MB"

        # Check for memory leak pattern (continuous growth)
        if len(memory_measurements) >= 5:
            recent_measurements = memory_measurements[-5:]
            memory_trend = statistics.linear_regression(
                range(len(recent_measurements)), recent_measurements
            )

            # Slope should not indicate significant continuous growth
            slope_mb_per_iteration = memory_trend.slope / 1024 / 1024
            assert slope_mb_per_iteration < 5, f"Potential memory leak detected: {slope_mb_per_iteration}MB/iteration"

        integration_test_context.record_operation(
            "memory_usage_leak_detection",
            time.time() - start_time
        )

    async def test_scalability_threshold_identification(
        self,
        async_client: AsyncClient,
        integration_db_session: Session,
        superuser: User,
        multiple_admin_users: List[User],
        performance_metrics: PerformanceMetrics,
        integration_test_context
    ):
        """Identify performance degradation thresholds under increasing load."""
        start_time = time.time()

        auth_token = create_access_token(
            data={"sub": str(superuser.id), "email": superuser.email}
        )
        headers = {"Authorization": f"Bearer {auth_token}"}

        load_levels = [5, 10, 20, 30, 50]  # Concurrent requests
        performance_results = []

        for load_level in load_levels:
            print(f"Testing load level: {load_level} concurrent requests")

            async def load_test_request(request_id: int):
                """Single request for load testing."""
                request_start = time.time()

                try:
                    # Mix of different operations
                    if request_id % 3 == 0:
                        response = await async_client.get("/api/v1/admin/users", headers=headers)
                    elif request_id % 3 == 1:
                        user = multiple_admin_users[request_id % len(multiple_admin_users)]
                        response = await async_client.get(f"/api/v1/admin/users/{user.id}", headers=headers)
                    else:
                        user = multiple_admin_users[request_id % len(multiple_admin_users)]
                        response = await async_client.get(
                            f"/api/v1/admin/users/{user.id}/permissions",
                            headers=headers
                        )

                    request_duration = time.time() - request_start

                    return {
                        "success": response.status_code == 200,
                        "duration": request_duration,
                        "status_code": response.status_code
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "duration": time.time() - request_start,
                        "error": str(e)
                    }

            # Execute load test for current level
            load_start = time.time()
            tasks = [load_test_request(i) for i in range(load_level)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_load_time = time.time() - load_start

            # Analyze results for this load level
            successful_requests = [r for r in results if isinstance(r, dict) and r.get("success")]
            failed_requests = [r for r in results if isinstance(r, Exception) or (isinstance(r, dict) and not r.get("success"))]

            success_rate = len(successful_requests) / load_level
            avg_response_time = statistics.mean([r["duration"] for r in successful_requests]) if successful_requests else float('inf')
            p95_response_time = performance_metrics._percentile([r["duration"] for r in successful_requests], 95) if successful_requests else float('inf')

            performance_results.append({
                "load_level": load_level,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "p95_response_time": p95_response_time,
                "total_time": total_load_time,
                "failed_requests": len(failed_requests)
            })

            # Record system metrics
            performance_metrics.record_system_metrics()

            # Wait between load levels
            await asyncio.sleep(1)

        # Analyze scalability patterns
        for i, result in enumerate(performance_results):
            print(f"Load {result['load_level']}: Success Rate {result['success_rate']:.2f}, "
                  f"Avg Response {result['avg_response_time']:.3f}s, "
                  f"P95 Response {result['p95_response_time']:.3f}s")

            # Performance should not degrade dramatically
            if i > 0:
                prev_result = performance_results[i-1]

                # Success rate should not drop below 90%
                assert result['success_rate'] >= 0.9, f"Success rate too low at load {result['load_level']}: {result['success_rate']}"

                # Response time should not increase more than 3x
                response_time_ratio = result['avg_response_time'] / prev_result['avg_response_time']
                assert response_time_ratio <= 3.0, f"Response time degradation too high at load {result['load_level']}: {response_time_ratio}x"

        # Identify recommended maximum load
        acceptable_results = [r for r in performance_results if r['success_rate'] >= 0.95 and r['avg_response_time'] <= 1.0]
        if acceptable_results:
            max_recommended_load = max(r['load_level'] for r in acceptable_results)
            print(f"Recommended maximum concurrent load: {max_recommended_load}")
            assert max_recommended_load >= 10, "System should handle at least 10 concurrent requests efficiently"

        integration_test_context.record_operation(
            "scalability_threshold_identification",
            time.time() - start_time
        )

    async def test_performance_regression_detection(
        self,
        async_client: AsyncClient,
        superuser: User,
        performance_metrics: PerformanceMetrics,
        integration_test_context
    ):
        """Detect performance regressions against baseline metrics."""
        start_time = time.time()

        auth_token = create_access_token(
            data={"sub": str(superuser.id), "email": superuser.email}
        )
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Define baseline performance expectations
        baseline_expectations = {
            "list_users": 0.5,  # seconds
            "user_detail": 0.3,
            "permissions": 0.4,
            "audit_logs": 0.6
        }

        regression_results = {}

        # Test each endpoint against baseline
        for endpoint_name, baseline_time in baseline_expectations.items():
            endpoint_times = []

            for _ in range(5):  # Multiple samples
                if endpoint_name == "list_users":
                    start_req = time.time()
                    response = await async_client.get("/api/v1/admin/users", headers=headers)
                    duration = time.time() - start_req
                elif endpoint_name == "user_detail":
                    start_req = time.time()
                    response = await async_client.get(f"/api/v1/admin/users/{superuser.id}", headers=headers)
                    duration = time.time() - start_req
                elif endpoint_name == "permissions":
                    start_req = time.time()
                    response = await async_client.get(f"/api/v1/admin/users/{superuser.id}/permissions", headers=headers)
                    duration = time.time() - start_req
                elif endpoint_name == "audit_logs":
                    start_req = time.time()
                    response = await async_client.get(f"/api/v1/admin/audit/user/{superuser.id}", headers=headers)
                    duration = time.time() - start_req

                assert response.status_code == 200
                endpoint_times.append(duration)

            avg_time = statistics.mean(endpoint_times)
            regression_ratio = avg_time / baseline_time

            regression_results[endpoint_name] = {
                "baseline": baseline_time,
                "current": avg_time,
                "ratio": regression_ratio,
                "regression": regression_ratio > 1.5  # 50% slower is regression
            }

            # Assert no significant regression
            assert regression_ratio <= 2.0, f"Significant performance regression in {endpoint_name}: {regression_ratio}x slower"

        # Report regression analysis
        for endpoint, result in regression_results.items():
            if result["regression"]:
                print(f"WARNING: Performance regression detected in {endpoint}: {result['ratio']:.2f}x slower")
            else:
                print(f"OK: {endpoint} performance within acceptable range: {result['ratio']:.2f}x")

        integration_test_context.record_operation(
            "performance_regression_detection",
            time.time() - start_time
        )

        # Record final performance summary
        summary = performance_metrics.get_performance_summary()
        print("\n=== PERFORMANCE SUMMARY ===")
        print(f"Average Response Time: {summary['response_times']['mean']:.3f}s")
        print(f"P95 Response Time: {summary['response_times']['p95']:.3f}s")
        print(f"Peak Memory Usage: {summary['resource_usage']['peak_memory_mb']:.1f}MB")
        print(f"Average CPU Usage: {summary['resource_usage']['avg_cpu_percent']:.1f}%")
        if summary['cache_performance']['avg_hit_ratio'] > 0:
            print(f"Cache Hit Ratio: {summary['cache_performance']['avg_hit_ratio']:.2f}")