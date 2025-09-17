# ~/tests/performance/performance_benchmarks.py
# ---------------------------------------------------------------------------------------------
# MeStore - Performance Benchmarks and SLA Tests
# Copyright (c) 2025 Performance Optimization AI. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: performance_benchmarks.py
# Ruta: ~/tests/performance/performance_benchmarks.py
# Autor: Performance Optimization AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Performance benchmarks and SLA validation tests for MeStore
#            TDD approach with RED-GREEN-REFACTOR methodology
#
# Características:
# - Comprehensive performance SLA definitions and validation
# - TDD performance testing with measurable benchmarks
# - Database performance benchmarks with query optimization
# - Cache performance validation and hit rate testing
# - API endpoint performance benchmarks
# - Search performance benchmarks with relevance scoring
# - Memory usage and resource consumption testing
# - Real-time performance monitoring integration
#
# ---------------------------------------------------------------------------------------------

"""
Performance Benchmarks para MeStore Marketplace.

Este módulo implementa benchmarks comprehensivos y validación de SLAs:
- Definiciones comprehensivas de SLAs de performance y validación
- Testing de performance TDD con benchmarks medibles
- Benchmarks de performance de base de datos con optimización de queries
- Validación de performance de cache y testing de hit rate
- Benchmarks de performance de endpoints API
- Benchmarks de performance de búsqueda con scoring de relevancia
- Testing de uso de memoria y consumo de recursos
- Integración con monitoreo de performance en tiempo real
"""

import asyncio
import logging
import statistics
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import pytest
import psutil
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.product import Product, ProductStatus
from app.models.user import User, UserType
from app.models.category import Category
from app.services.cache_service import cache_service
from app.services.database_optimization_service import database_optimization_service
from app.services.performance_monitoring_service import performance_monitoring_service
from app.services.search_performance_service import search_performance_service

logger = logging.getLogger(__name__)


class PerformanceSLA:
    """Performance SLA definitions for MeStore marketplace"""

    # API Response Time SLAs (milliseconds)
    API_RESPONSE_MEAN_MAX = 200
    API_RESPONSE_P95_MAX = 500
    API_RESPONSE_P99_MAX = 1000

    # Database Query SLAs (milliseconds)
    DB_QUERY_SIMPLE_MAX = 50
    DB_QUERY_COMPLEX_MAX = 200
    DB_QUERY_AGGREGATION_MAX = 500

    # Cache Performance SLAs
    CACHE_HIT_RATE_MIN = 85  # Minimum 85% hit rate
    CACHE_RESPONSE_TIME_MAX = 10  # Maximum 10ms cache response

    # Search Performance SLAs
    SEARCH_RESPONSE_TIME_MAX = 100  # Maximum 100ms search response
    SEARCH_RELEVANCE_SCORE_MIN = 0.8  # Minimum relevance score

    # System Resource SLAs
    MEMORY_USAGE_MAX = 512  # Maximum 512MB memory usage
    CPU_USAGE_MAX = 70  # Maximum 70% CPU usage

    # Throughput SLAs
    API_THROUGHPUT_MIN = 100  # Minimum 100 requests per second
    SEARCH_THROUGHPUT_MIN = 50  # Minimum 50 searches per second


class PerformanceBenchmarks:
    """Performance benchmark test suite with TDD methodology"""

    def __init__(self):
        self.test_results = {}
        self.benchmark_start_time = None
        self.sla = PerformanceSLA()

    async def setup_benchmark_environment(self, db: AsyncSession):
        """Setup test environment for benchmarks (TDD: RED phase)"""
        logger.info("Setting up benchmark environment...")

        self.benchmark_start_time = datetime.utcnow()

        # Create test data for benchmarks
        await self._create_benchmark_test_data(db)

        # Warm up caches
        await cache_service.warmup_cache(db)

        # Initialize search performance service
        await search_performance_service.initialize_chroma_optimization()

        logger.info("Benchmark environment setup complete")

    async def _create_benchmark_test_data(self, db: AsyncSession):
        """Create test data for benchmark testing"""
        try:
            # Create test categories
            categories = []
            for i in range(10):
                category = Category(
                    name=f"Benchmark Category {i}",
                    description=f"Test category for benchmarks {i}",
                    level=1
                )
                db.add(category)
                categories.append(category)

            # Create test users
            users = []
            for i in range(50):
                user = User(
                    email=f"benchmark_user_{i}@test.com",
                    username=f"benchmark_user_{i}",
                    user_type=UserType.VENDOR if i % 3 == 0 else UserType.BUYER,
                    is_active=True
                )
                db.add(user)
                users.append(user)

            await db.commit()

            # Create test products
            vendor_users = [u for u in users if u.user_type == UserType.VENDOR]
            for i in range(1000):
                product = Product(
                    name=f"Benchmark Product {i}",
                    description=f"Test product for performance benchmarks {i}",
                    precio_venta=100.0 + (i % 500),
                    status=ProductStatus.ACTIVE,
                    vendor_id=vendor_users[i % len(vendor_users)].id if vendor_users else None
                )
                db.add(product)

            await db.commit()

            logger.info("Benchmark test data created successfully")

        except Exception as e:
            logger.error(f"Error creating benchmark test data: {e}")
            await db.rollback()
            raise

    # === DATABASE PERFORMANCE BENCHMARKS ===

    @pytest.mark.asyncio
    async def test_database_simple_query_performance(self, db: AsyncSession):
        """Test simple database query performance (TDD: GREEN phase)"""
        logger.info("Testing database simple query performance...")

        query_times = []

        # Run multiple iterations for statistical significance
        for _ in range(100):
            start_time = time.time()

            # Simple product query
            result = await db.execute(
                select(Product).where(Product.status == ProductStatus.ACTIVE).limit(10)
            )
            products = result.scalars().all()

            query_time = (time.time() - start_time) * 1000
            query_times.append(query_time)

        # Calculate statistics
        avg_time = statistics.mean(query_times)
        p95_time = statistics.quantiles(query_times, n=20)[18]  # 95th percentile
        max_time = max(query_times)

        # Benchmark validation
        assert avg_time < self.sla.DB_QUERY_SIMPLE_MAX, f"Average query time {avg_time:.2f}ms exceeds SLA {self.sla.DB_QUERY_SIMPLE_MAX}ms"
        assert p95_time < self.sla.DB_QUERY_SIMPLE_MAX * 2, f"P95 query time {p95_time:.2f}ms exceeds threshold"
        assert len(products) > 0, "Query must return results"

        self.test_results["db_simple_query"] = {
            "avg_time_ms": avg_time,
            "p95_time_ms": p95_time,
            "max_time_ms": max_time,
            "sla_compliant": avg_time < self.sla.DB_QUERY_SIMPLE_MAX
        }

        logger.info(f"Simple query benchmark: avg={avg_time:.2f}ms, p95={p95_time:.2f}ms")
        return self.test_results["db_simple_query"]

    @pytest.mark.asyncio
    async def test_database_complex_query_performance(self, db: AsyncSession):
        """Test complex database query performance with joins"""
        logger.info("Testing database complex query performance...")

        query_times = []

        for _ in range(50):
            start_time = time.time()

            # Complex query with joins
            result = await db.execute(
                text("""
                    SELECT p.id, p.name, p.precio_venta, u.username as vendor_name
                    FROM products p
                    JOIN users u ON p.vendor_id = u.id
                    WHERE p.status = 'ACTIVE'
                    AND p.precio_venta BETWEEN 100 AND 500
                    ORDER BY p.created_at DESC
                    LIMIT 20
                """)
            )
            rows = result.fetchall()

            query_time = (time.time() - start_time) * 1000
            query_times.append(query_time)

        avg_time = statistics.mean(query_times)
        p95_time = statistics.quantiles(query_times, n=20)[18]

        assert avg_time < self.sla.DB_QUERY_COMPLEX_MAX, f"Complex query avg time {avg_time:.2f}ms exceeds SLA"
        assert len(rows) > 0, "Complex query must return results"

        self.test_results["db_complex_query"] = {
            "avg_time_ms": avg_time,
            "p95_time_ms": p95_time,
            "sla_compliant": avg_time < self.sla.DB_QUERY_COMPLEX_MAX
        }

        logger.info(f"Complex query benchmark: avg={avg_time:.2f}ms, p95={p95_time:.2f}ms")
        return self.test_results["db_complex_query"]

    @pytest.mark.asyncio
    async def test_database_aggregation_performance(self, db: AsyncSession):
        """Test database aggregation query performance"""
        logger.info("Testing database aggregation performance...")

        query_times = []

        for _ in range(20):
            start_time = time.time()

            # Aggregation query
            result = await db.execute(
                text("""
                    SELECT
                        u.username,
                        COUNT(p.id) as product_count,
                        AVG(p.precio_venta) as avg_price,
                        MAX(p.precio_venta) as max_price
                    FROM users u
                    LEFT JOIN products p ON u.id = p.vendor_id
                    WHERE u.user_type = 'VENDOR'
                    GROUP BY u.id, u.username
                    HAVING COUNT(p.id) > 0
                    ORDER BY product_count DESC
                    LIMIT 10
                """)
            )
            rows = result.fetchall()

            query_time = (time.time() - start_time) * 1000
            query_times.append(query_time)

        avg_time = statistics.mean(query_times)

        assert avg_time < self.sla.DB_QUERY_AGGREGATION_MAX, f"Aggregation query avg time {avg_time:.2f}ms exceeds SLA"

        self.test_results["db_aggregation_query"] = {
            "avg_time_ms": avg_time,
            "sla_compliant": avg_time < self.sla.DB_QUERY_AGGREGATION_MAX
        }

        logger.info(f"Aggregation query benchmark: avg={avg_time:.2f}ms")
        return self.test_results["db_aggregation_query"]

    # === CACHE PERFORMANCE BENCHMARKS ===

    @pytest.mark.asyncio
    async def test_cache_performance_benchmarks(self):
        """Test cache performance and hit rates"""
        logger.info("Testing cache performance benchmarks...")

        # Cache performance test
        cache_times = []
        cache_hits = 0
        cache_misses = 0

        test_data = {"test": "data", "value": 123, "timestamp": datetime.utcnow().isoformat()}

        # Test cache set performance
        set_times = []
        for i in range(100):
            start_time = time.time()
            await cache_service.set(f"benchmark_key_{i}", test_data, ttl=60)
            set_time = (time.time() - start_time) * 1000
            set_times.append(set_time)

        # Test cache get performance
        get_times = []
        for i in range(100):
            start_time = time.time()
            result = await cache_service.get(f"benchmark_key_{i}")
            get_time = (time.time() - start_time) * 1000
            get_times.append(get_time)

            if result is not None:
                cache_hits += 1
            else:
                cache_misses += 1

        avg_set_time = statistics.mean(set_times)
        avg_get_time = statistics.mean(get_times)
        hit_rate = (cache_hits / (cache_hits + cache_misses)) * 100

        assert avg_get_time < self.sla.CACHE_RESPONSE_TIME_MAX, f"Cache get time {avg_get_time:.2f}ms exceeds SLA"
        assert hit_rate >= self.sla.CACHE_HIT_RATE_MIN, f"Cache hit rate {hit_rate:.1f}% below SLA"

        self.test_results["cache_performance"] = {
            "avg_set_time_ms": avg_set_time,
            "avg_get_time_ms": avg_get_time,
            "hit_rate_percent": hit_rate,
            "sla_compliant": avg_get_time < self.sla.CACHE_RESPONSE_TIME_MAX and hit_rate >= self.sla.CACHE_HIT_RATE_MIN
        }

        logger.info(f"Cache benchmark: get={avg_get_time:.2f}ms, hit_rate={hit_rate:.1f}%")
        return self.test_results["cache_performance"]

    # === SEARCH PERFORMANCE BENCHMARKS ===

    @pytest.mark.asyncio
    async def test_search_performance_benchmarks(self):
        """Test search performance with various query types"""
        logger.info("Testing search performance benchmarks...")

        search_queries = [
            "smartphone", "laptop", "telefono", "computadora", "electronico",
            "ropa mujer", "zapatos hombre", "casa hogar", "cocina", "dormitorio"
        ]

        search_times = []
        relevance_scores = []

        for query in search_queries:
            # Test each query multiple times
            for _ in range(5):
                start_time = time.time()

                # Execute optimized search
                result = await search_performance_service.optimize_search_query(query)

                search_time = (time.time() - start_time) * 1000
                search_times.append(search_time)

                # Calculate average relevance score
                if result.get("results"):
                    scores = [r.get("relevance_score", 0) for r in result["results"]]
                    if scores:
                        relevance_scores.append(statistics.mean(scores))

        avg_search_time = statistics.mean(search_times)
        avg_relevance = statistics.mean(relevance_scores) if relevance_scores else 0

        assert avg_search_time < self.sla.SEARCH_RESPONSE_TIME_MAX, f"Search time {avg_search_time:.2f}ms exceeds SLA"
        assert avg_relevance >= self.sla.SEARCH_RELEVANCE_SCORE_MIN, f"Search relevance {avg_relevance:.2f} below SLA"

        self.test_results["search_performance"] = {
            "avg_search_time_ms": avg_search_time,
            "avg_relevance_score": avg_relevance,
            "sla_compliant": (
                avg_search_time < self.sla.SEARCH_RESPONSE_TIME_MAX and
                avg_relevance >= self.sla.SEARCH_RELEVANCE_SCORE_MIN
            )
        }

        logger.info(f"Search benchmark: avg_time={avg_search_time:.2f}ms, relevance={avg_relevance:.2f}")
        return self.test_results["search_performance"]

    # === MEMORY AND RESOURCE BENCHMARKS ===

    @pytest.mark.asyncio
    async def test_memory_usage_benchmarks(self):
        """Test memory usage under load"""
        logger.info("Testing memory usage benchmarks...")

        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate workload
        test_data = []
        for i in range(10000):
            test_data.append({
                "id": i,
                "name": f"Product {i}",
                "description": f"Description for product {i}" * 10,
                "price": 100.0 + i,
                "tags": [f"tag{j}" for j in range(10)]
            })

        # Cache some data
        for i in range(1000):
            await cache_service.set(f"memory_test_{i}", test_data[i], ttl=300)

        # Measure peak memory usage
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory

        # CPU usage test
        cpu_percent = process.cpu_percent(interval=1)

        assert peak_memory < self.sla.MEMORY_USAGE_MAX, f"Memory usage {peak_memory:.2f}MB exceeds SLA"
        assert cpu_percent < self.sla.CPU_USAGE_MAX, f"CPU usage {cpu_percent:.1f}% exceeds SLA"

        self.test_results["memory_usage"] = {
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": peak_memory,
            "memory_increase_mb": memory_increase,
            "cpu_percent": cpu_percent,
            "sla_compliant": peak_memory < self.sla.MEMORY_USAGE_MAX and cpu_percent < self.sla.CPU_USAGE_MAX
        }

        logger.info(f"Memory benchmark: peak={peak_memory:.2f}MB, CPU={cpu_percent:.1f}%")
        return self.test_results["memory_usage"]

    # === THROUGHPUT BENCHMARKS ===

    @pytest.mark.asyncio
    async def test_api_throughput_benchmarks(self, db: AsyncSession):
        """Test API throughput under concurrent load"""
        logger.info("Testing API throughput benchmarks...")

        # Simulate concurrent API calls
        async def simulate_api_call():
            """Simulate an API call with database query"""
            start_time = time.time()

            # Simulate product listing API call
            result = await db.execute(
                select(Product).where(Product.status == ProductStatus.ACTIVE).limit(20)
            )
            products = result.scalars().all()

            response_time = (time.time() - start_time) * 1000
            return response_time, len(products)

        # Run concurrent requests
        start_time = time.time()
        tasks = [simulate_api_call() for _ in range(200)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Calculate throughput
        successful_requests = len([r for r in results if r[1] > 0])
        throughput = successful_requests / total_time
        avg_response_time = statistics.mean([r[0] for r in results])

        assert throughput >= self.sla.API_THROUGHPUT_MIN, f"API throughput {throughput:.1f} RPS below SLA"
        assert avg_response_time < self.sla.API_RESPONSE_MEAN_MAX, f"API response time {avg_response_time:.2f}ms exceeds SLA"

        self.test_results["api_throughput"] = {
            "throughput_rps": throughput,
            "avg_response_time_ms": avg_response_time,
            "successful_requests": successful_requests,
            "total_requests": len(tasks),
            "sla_compliant": (
                throughput >= self.sla.API_THROUGHPUT_MIN and
                avg_response_time < self.sla.API_RESPONSE_MEAN_MAX
            )
        }

        logger.info(f"API throughput benchmark: {throughput:.1f} RPS, avg_time={avg_response_time:.2f}ms")
        return self.test_results["api_throughput"]

    # === COMPREHENSIVE BENCHMARK SUITE ===

    @pytest.mark.asyncio
    async def run_comprehensive_benchmarks(self, db: AsyncSession) -> Dict[str, Any]:
        """Run all performance benchmarks (TDD: REFACTOR phase)"""
        logger.info("Running comprehensive performance benchmarks...")

        await self.setup_benchmark_environment(db)

        # Run all benchmark tests
        benchmark_results = {}

        try:
            benchmark_results["database"] = {
                "simple_query": await self.test_database_simple_query_performance(db),
                "complex_query": await self.test_database_complex_query_performance(db),
                "aggregation_query": await self.test_database_aggregation_performance(db)
            }

            benchmark_results["cache"] = await self.test_cache_performance_benchmarks()

            benchmark_results["search"] = await self.test_search_performance_benchmarks()

            benchmark_results["memory"] = await self.test_memory_usage_benchmarks()

            benchmark_results["throughput"] = await self.test_api_throughput_benchmarks(db)

        except Exception as e:
            logger.error(f"Error running benchmarks: {e}")
            benchmark_results["error"] = str(e)

        # Generate comprehensive report
        report = self._generate_benchmark_report(benchmark_results)

        logger.info("Comprehensive benchmarks completed")
        return report

    def _generate_benchmark_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        sla_violations = []
        passed_tests = 0
        total_tests = 0

        def check_results(category: str, tests: Dict[str, Any]):
            nonlocal passed_tests, total_tests
            for test_name, result in tests.items():
                total_tests += 1
                if isinstance(result, dict):
                    if result.get("sla_compliant", False):
                        passed_tests += 1
                    else:
                        sla_violations.append(f"{category}.{test_name}")

        # Check all test results
        for category, category_results in results.items():
            if category == "error":
                continue

            if isinstance(category_results, dict):
                if "sla_compliant" in category_results:
                    # Single test result
                    total_tests += 1
                    if category_results["sla_compliant"]:
                        passed_tests += 1
                    else:
                        sla_violations.append(category)
                else:
                    # Multiple test results
                    check_results(category, category_results)

        # Calculate overall rating
        success_rate = (passed_tests / max(total_tests, 1)) * 100
        overall_rating = self._calculate_overall_rating(success_rate)

        return {
            "benchmark_report": {
                "timestamp": datetime.utcnow().isoformat(),
                "duration_minutes": (datetime.utcnow() - self.benchmark_start_time).total_seconds() / 60 if self.benchmark_start_time else 0,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "success_rate_percent": round(success_rate, 2),
                    "overall_rating": overall_rating
                },
                "sla_violations": sla_violations,
                "detailed_results": results,
                "recommendations": self._generate_recommendations(results, sla_violations)
            }
        }

    def _calculate_overall_rating(self, success_rate: float) -> str:
        """Calculate overall performance rating"""
        if success_rate >= 95:
            return "EXCELLENT"
        elif success_rate >= 85:
            return "GOOD"
        elif success_rate >= 70:
            return "FAIR"
        else:
            return "POOR"

    def _generate_recommendations(self, results: Dict[str, Any], violations: List[str]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        if "database.simple_query" in violations:
            recommendations.append("Optimize database indexes for simple queries")

        if "database.complex_query" in violations:
            recommendations.append("Review complex query joins and consider query optimization")

        if "cache" in violations:
            recommendations.append("Improve cache configuration and hit rates")

        if "search" in violations:
            recommendations.append("Optimize search algorithms and indexing")

        if "memory" in violations:
            recommendations.append("Implement memory optimization and garbage collection tuning")

        if "throughput" in violations:
            recommendations.append("Consider horizontal scaling and load balancing")

        return recommendations or ["Performance benchmarks are meeting SLAs. Continue monitoring."]


# Global benchmark instance
performance_benchmarks = PerformanceBenchmarks()


# Pytest test functions
@pytest.mark.asyncio
async def test_comprehensive_performance_benchmarks(db_session):
    """Run comprehensive performance benchmark suite"""
    report = await performance_benchmarks.run_comprehensive_benchmarks(db_session)

    # Assert overall performance requirements
    assert report["benchmark_report"]["summary"]["success_rate_percent"] >= 80, "Performance benchmark success rate too low"
    assert len(report["benchmark_report"]["sla_violations"]) <= 2, "Too many SLA violations"


@pytest.mark.asyncio
async def test_database_performance_sla(db_session):
    """Test database performance meets SLA requirements"""
    db_results = await performance_benchmarks.test_database_simple_query_performance(db_session)
    assert db_results["sla_compliant"], "Database performance does not meet SLA"


@pytest.mark.asyncio
async def test_cache_performance_sla():
    """Test cache performance meets SLA requirements"""
    cache_results = await performance_benchmarks.test_cache_performance_benchmarks()
    assert cache_results["sla_compliant"], "Cache performance does not meet SLA"


@pytest.mark.asyncio
async def test_search_performance_sla():
    """Test search performance meets SLA requirements"""
    search_results = await performance_benchmarks.test_search_performance_benchmarks()
    assert search_results["sla_compliant"], "Search performance does not meet SLA"


if __name__ == "__main__":
    # Run benchmarks when executed directly
    async def main():
        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            print("Running comprehensive performance benchmarks...")
            report = await performance_benchmarks.run_comprehensive_benchmarks(db)

            print("\n" + "="*80)
            print("PERFORMANCE BENCHMARK REPORT")
            print("="*80)
            import json
            print(json.dumps(report, indent=2))

    asyncio.run(main())