"""
Integrated Performance Service
==============================

Comprehensive performance management service that integrates:
- Performance monitoring and metrics collection
- Cache service with intelligent caching strategies
- Search performance optimization
- Database query optimization
- Real-time alerting and threshold monitoring

This service orchestrates all performance-related functionality to provide
a unified interface for performance optimization across the application.

Author: System Architect AI
Date: 2025-09-17
Purpose: Complete integration of performance monitoring and optimization
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from uuid import uuid4
from dataclasses import dataclass
from functools import wraps
import time
import psutil

from sqlalchemy.ext.asyncio import AsyncSession

# Import performance services
from app.services.performance_monitoring_service import PerformanceMonitoringService
from app.services.cache_service import CacheService
from app.services.search_performance_service import SearchPerformanceService
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = None
    threshold_warning: float = None
    threshold_critical: float = None


@dataclass
class PerformanceAlert:
    """Performance alert data structure"""
    metric_name: str
    current_value: float
    threshold: float
    severity: str  # warning, critical
    timestamp: datetime
    message: str


class IntegratedPerformanceService:
    """
    Unified performance service integrating monitoring, caching, and optimization.
    """

    def __init__(self):
        self.monitoring_service = PerformanceMonitoringService()
        self.cache_service = CacheService()
        self.search_performance_service = SearchPerformanceService()

        # Performance thresholds
        self.thresholds = {
            "api_response_time": {"warning": 500, "critical": 1000},  # milliseconds
            "database_query_time": {"warning": 200, "critical": 500},
            "cache_hit_rate": {"warning": 70, "critical": 50},  # percentage
            "memory_usage": {"warning": 80, "critical": 90},  # percentage
            "cpu_usage": {"warning": 80, "critical": 95},  # percentage
        }

        self.alerts = []
        self.metrics_history = []

    async def initialize(self):
        """Initialize all performance services"""
        try:
            await self.monitoring_service.initialize()
            await self.cache_service.initialize()
            await self.search_performance_service.initialize()
            logger.info("IntegratedPerformanceService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize IntegratedPerformanceService: {str(e)}")
            raise

    # Performance Monitoring Integration

    @asynccontextmanager
    async def monitor_operation(
        self,
        operation_name: str,
        tags: Dict[str, str] = None,
        alert_on_slow: bool = True
    ):
        """
        Context manager for monitoring operation performance.

        Args:
            operation_name: Name of the operation being monitored
            tags: Additional tags for metrics
            alert_on_slow: Whether to generate alerts for slow operations

        Usage:
            async with performance_service.monitor_operation("api_call", {"endpoint": "/orders"}):
                # Your operation here
                result = await some_operation()
        """
        start_time = time.time()
        operation_id = str(uuid4())

        try:
            # Start monitoring
            await self.monitoring_service.start_operation_monitoring(
                operation_id, operation_name, tags
            )

            yield operation_id

        except Exception as e:
            # Record error in performance monitoring
            await self.monitoring_service.record_operation_error(
                operation_id, str(e)
            )
            raise

        finally:
            # End monitoring and record metrics
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            await self.monitoring_service.end_operation_monitoring(
                operation_id, duration_ms
            )

            # Check for performance alerts
            if alert_on_slow:
                await self._check_performance_thresholds(
                    operation_name, duration_ms, tags
                )

    async def monitor_database_query(
        self,
        query_name: str,
        query_func: Callable,
        *args,
        **kwargs
    ):
        """
        Monitor database query performance.

        Args:
            query_name: Name of the query for monitoring
            query_func: Database query function to execute
            *args, **kwargs: Arguments to pass to query function

        Returns:
            Query result with performance monitoring
        """
        async with self.monitor_operation(f"db_query:{query_name}"):
            return await query_func(*args, **kwargs)

    async def monitor_api_endpoint(
        self,
        endpoint_name: str,
        handler_func: Callable,
        *args,
        **kwargs
    ):
        """
        Monitor API endpoint performance.

        Args:
            endpoint_name: Name of the API endpoint
            handler_func: Endpoint handler function
            *args, **kwargs: Arguments to pass to handler

        Returns:
            Handler result with performance monitoring
        """
        tags = {"endpoint": endpoint_name}
        async with self.monitor_operation(f"api:{endpoint_name}", tags):
            return await handler_func(*args, **kwargs)

    # Cache Integration

    async def get_cached_or_compute(
        self,
        cache_key: str,
        compute_func: Callable,
        ttl: int = 3600,
        cache_namespace: str = "default",
        *args,
        **kwargs
    ):
        """
        Get value from cache or compute and cache it.

        Args:
            cache_key: Cache key
            compute_func: Function to compute value if not cached
            ttl: Time to live in seconds
            cache_namespace: Cache namespace for organization
            *args, **kwargs: Arguments for compute function

        Returns:
            Cached or computed value
        """
        # Try to get from cache first
        cached_value = await self.cache_service.get(
            cache_key, namespace=cache_namespace
        )

        if cached_value is not None:
            # Cache hit - record performance metric
            await self.monitoring_service.record_cache_hit(
                cache_key, cache_namespace
            )
            return cached_value

        # Cache miss - compute value
        async with self.monitor_operation(f"cache_compute:{cache_key}"):
            computed_value = await compute_func(*args, **kwargs)

            # Store in cache
            await self.cache_service.set(
                cache_key, computed_value, ttl=ttl, namespace=cache_namespace
            )

            # Record cache miss
            await self.monitoring_service.record_cache_miss(
                cache_key, cache_namespace
            )

            return computed_value

    async def invalidate_cache_pattern(
        self,
        pattern: str,
        namespace: str = "default"
    ):
        """
        Invalidate cache entries matching a pattern.

        Args:
            pattern: Pattern to match cache keys
            namespace: Cache namespace
        """
        await self.cache_service.invalidate_pattern(pattern, namespace)

        # Record cache invalidation
        await self.monitoring_service.record_cache_invalidation(pattern, namespace)

    # Search Performance Integration

    async def optimize_search_query(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Optimize search query with performance monitoring.

        Args:
            query: Search query string
            filters: Search filters
            user_id: User ID for personalization

        Returns:
            Optimized search results with performance metrics
        """
        async with self.monitor_operation("search_optimization"):
            return await self.search_performance_service.optimize_search(
                query=query,
                filters=filters,
                user_id=user_id
            )

    # Performance Analytics

    async def get_performance_dashboard_data(
        self,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """
        Get comprehensive performance dashboard data.

        Args:
            time_range: Time range for metrics (1h, 24h, 7d)

        Returns:
            Performance dashboard data
        """
        try:
            # Get metrics from all services
            monitoring_data = await self.monitoring_service.get_metrics_summary(time_range)
            cache_data = await self.cache_service.get_performance_metrics()
            search_data = await self.search_performance_service.get_metrics()

            # Get system metrics
            system_data = await self._get_system_metrics()

            # Compile dashboard data
            dashboard_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "time_range": time_range,
                "api_performance": monitoring_data.get("api_metrics", {}),
                "database_performance": monitoring_data.get("db_metrics", {}),
                "cache_performance": cache_data,
                "search_performance": search_data,
                "system_performance": system_data,
                "alerts": await self._get_active_alerts(),
                "health_score": await self._calculate_health_score()
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"Failed to get performance dashboard data: {str(e)}")
            return {
                "error": "Failed to retrieve performance data",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_performance_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get performance optimization recommendations based on metrics.

        Returns:
            List of performance recommendations
        """
        recommendations = []

        try:
            # Get current metrics
            cache_metrics = await self.cache_service.get_performance_metrics()
            monitoring_metrics = await self.monitoring_service.get_current_metrics()

            # Cache recommendations
            if cache_metrics.get("hit_rate", 0) < 70:
                recommendations.append({
                    "type": "cache_optimization",
                    "priority": "high",
                    "title": "Low Cache Hit Rate",
                    "description": f"Cache hit rate is {cache_metrics.get('hit_rate', 0):.1f}%. Consider increasing cache TTL or improving cache key strategies.",
                    "action": "Review cache configuration and invalidation patterns"
                })

            # Database recommendations
            avg_query_time = monitoring_metrics.get("avg_db_query_time", 0)
            if avg_query_time > 200:
                recommendations.append({
                    "type": "database_optimization",
                    "priority": "high",
                    "title": "Slow Database Queries",
                    "description": f"Average query time is {avg_query_time:.0f}ms. Consider adding indexes or optimizing queries.",
                    "action": "Analyze slow queries and add appropriate indexes"
                })

            # Memory recommendations
            memory_usage = psutil.virtual_memory().percent
            if memory_usage > 80:
                recommendations.append({
                    "type": "memory_optimization",
                    "priority": "medium",
                    "title": "High Memory Usage",
                    "description": f"Memory usage is {memory_usage:.1f}%. Consider optimizing memory-intensive operations.",
                    "action": "Review memory usage patterns and optimize data structures"
                })

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate performance recommendations: {str(e)}")
            return []

    # Performance Decorators

    def monitor_function_performance(
        self,
        operation_name: str = None,
        cache_result: bool = False,
        cache_ttl: int = 3600
    ):
        """
        Decorator to monitor function performance.

        Args:
            operation_name: Name for monitoring (defaults to function name)
            cache_result: Whether to cache function result
            cache_ttl: Cache TTL in seconds

        Usage:
            @performance_service.monitor_function_performance("user_lookup", cache_result=True)
            async def get_user_profile(user_id: str):
                # Function implementation
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                func_name = operation_name or func.__name__

                if cache_result:
                    # Generate cache key from function name and arguments
                    cache_key = f"func:{func_name}:{hash(str(args) + str(kwargs))}"

                    return await self.get_cached_or_compute(
                        cache_key=cache_key,
                        compute_func=func,
                        ttl=cache_ttl,
                        *args,
                        **kwargs
                    )
                else:
                    async with self.monitor_operation(func_name):
                        return await func(*args, **kwargs)

            return wrapper
        return decorator

    # Alert Management

    async def _check_performance_thresholds(
        self,
        metric_name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """Check performance thresholds and generate alerts"""
        threshold_config = self.thresholds.get(metric_name)
        if not threshold_config:
            return

        alert = None

        if value >= threshold_config["critical"]:
            alert = PerformanceAlert(
                metric_name=metric_name,
                current_value=value,
                threshold=threshold_config["critical"],
                severity="critical",
                timestamp=datetime.utcnow(),
                message=f"{metric_name} is critically high: {value} >= {threshold_config['critical']}"
            )
        elif value >= threshold_config["warning"]:
            alert = PerformanceAlert(
                metric_name=metric_name,
                current_value=value,
                threshold=threshold_config["warning"],
                severity="warning",
                timestamp=datetime.utcnow(),
                message=f"{metric_name} is high: {value} >= {threshold_config['warning']}"
            )

        if alert:
            self.alerts.append(alert)
            logger.warning(f"Performance alert: {alert.message}")

            # Send alert through monitoring service
            await self.monitoring_service.send_performance_alert(
                alert.metric_name,
                alert.current_value,
                alert.threshold,
                alert.severity
            )

    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active performance alerts"""
        # Filter alerts from last hour
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        active_alerts = [
            {
                "metric": alert.metric_name,
                "value": alert.current_value,
                "threshold": alert.threshold,
                "severity": alert.severity,
                "timestamp": alert.timestamp.isoformat(),
                "message": alert.message
            }
            for alert in self.alerts
            if alert.timestamp >= cutoff_time
        ]

        return active_alerts

    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "disk_usage": disk.percent,
                "disk_free_gb": disk.free // (1024 * 1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return {}

    async def _calculate_health_score(self) -> int:
        """Calculate overall system health score (0-100)"""
        try:
            scores = []

            # Cache health score
            cache_metrics = await self.cache_service.get_performance_metrics()
            cache_hit_rate = cache_metrics.get("hit_rate", 0)
            cache_score = min(100, cache_hit_rate + 20)  # Boost score for good hit rates
            scores.append(cache_score)

            # System health score
            system_metrics = await self._get_system_metrics()
            cpu_score = max(0, 100 - system_metrics.get("cpu_usage", 0))
            memory_score = max(0, 100 - system_metrics.get("memory_usage", 0))
            scores.extend([cpu_score, memory_score])

            # Alert penalty
            active_alerts = await self._get_active_alerts()
            alert_penalty = len(active_alerts) * 10  # 10 points per alert

            # Calculate weighted average
            base_score = sum(scores) / len(scores) if scores else 50
            health_score = max(0, min(100, base_score - alert_penalty))

            return int(health_score)

        except Exception as e:
            logger.error(f"Failed to calculate health score: {str(e)}")
            return 50  # Default neutral score

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for integrated performance service"""
        health_status = {
            "service": "IntegratedPerformanceService",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "overall_health_score": await self._calculate_health_score()
        }

        # Check each component
        try:
            monitoring_health = await self.monitoring_service.health_check()
            health_status["components"]["monitoring"] = monitoring_health
        except Exception as e:
            health_status["components"]["monitoring"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        try:
            cache_health = await self.cache_service.health_check()
            health_status["components"]["cache"] = cache_health
        except Exception as e:
            health_status["components"]["cache"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        try:
            search_health = await self.search_performance_service.health_check()
            health_status["components"]["search_performance"] = search_health
        except Exception as e:
            health_status["components"]["search_performance"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Overall status
        all_healthy = all(
            comp.get("status") != "unhealthy"
            for comp in health_status["components"].values()
        )
        health_status["status"] = "healthy" if all_healthy else "degraded"

        return health_status


# Global instance for application use
integrated_performance_service = IntegratedPerformanceService()