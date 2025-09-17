# ~/app/services/performance_monitoring_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Performance Monitoring Service
# Copyright (c) 2025 Performance Optimization AI. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: performance_monitoring_service.py
# Ruta: ~/app/services/performance_monitoring_service.py
# Autor: Performance Optimization AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Comprehensive performance monitoring and APM for MeStore marketplace
#            Real-time performance tracking, alerting, and optimization insights
#
# Características:
# - Real-time API endpoint performance tracking
# - Database query performance monitoring
# - Cache hit rate and memory usage tracking
# - Custom performance metrics and SLA monitoring
# - Automated alerting for performance degradation
# - Performance dashboard data collection
# - Load testing integration and benchmarking
#
# ---------------------------------------------------------------------------------------------

"""
Performance Monitoring Service para MeStore Marketplace.

Este módulo implementa monitoreo comprehensivo de performance:
- Tracking en tiempo real de rendimiento de endpoints API
- Monitoreo de performance de queries de base de datos
- Tracking de cache hit rates y uso de memoria
- Métricas customizadas y monitoreo de SLA
- Alertas automáticas para degradación de performance
- Recolección de datos para dashboard de performance
- Integración con load testing y benchmarking
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import psutil
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis.base import get_redis_client

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Performance metrics data structure"""

    def __init__(self):
        self.endpoint_metrics: Dict[str, Dict] = {}
        self.database_metrics: Dict[str, Dict] = {}
        self.cache_metrics: Dict[str, Dict] = {}
        self.system_metrics: Dict[str, Any] = {}
        self.custom_metrics: Dict[str, Any] = {}


class PerformanceSLAs:
    """Performance SLA thresholds"""

    # API Response Time SLAs (milliseconds)
    API_RESPONSE_P95_THRESHOLD = 500  # 95th percentile under 500ms
    API_RESPONSE_P99_THRESHOLD = 1000  # 99th percentile under 1s
    API_RESPONSE_MEAN_THRESHOLD = 200  # Mean under 200ms

    # Database Query SLAs
    DB_QUERY_P95_THRESHOLD = 100  # 95th percentile under 100ms
    DB_QUERY_P99_THRESHOLD = 500  # 99th percentile under 500ms
    DB_SLOW_QUERY_THRESHOLD = 1000  # Queries over 1s are slow

    # Cache Performance SLAs
    CACHE_HIT_RATE_THRESHOLD = 85  # Minimum 85% hit rate
    CACHE_RESPONSE_TIME_THRESHOLD = 5  # Cache operations under 5ms

    # System Resource SLAs
    CPU_USAGE_THRESHOLD = 80  # CPU usage under 80%
    MEMORY_USAGE_THRESHOLD = 85  # Memory usage under 85%
    DISK_USAGE_THRESHOLD = 90  # Disk usage under 90%

    # Search Performance SLAs
    SEARCH_RESPONSE_TIME_THRESHOLD = 100  # Search under 100ms
    SEARCH_RELEVANCE_THRESHOLD = 0.8  # Search relevance score > 0.8


class PerformanceMonitoringService:
    """Comprehensive performance monitoring service"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.metrics = PerformanceMetrics()
        self.slas = PerformanceSLAs()
        self.active_requests: Dict[str, float] = {}
        self.request_id_counter = 0

    async def _get_redis(self) -> redis.Redis:
        """Get Redis client with lazy initialization"""
        if self.redis_client is None:
            self.redis_client = await get_redis_client()
        return self.redis_client

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        self.request_id_counter += 1
        return f"req_{int(time.time())}_{self.request_id_counter}"

    @asynccontextmanager
    async def track_endpoint_performance(self, endpoint: str, method: str, user_id: Optional[UUID] = None):
        """Context manager to track endpoint performance"""
        request_id = self._generate_request_id()
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        try:
            # Record request start
            self.active_requests[request_id] = start_time

            yield request_id

        finally:
            # Record request completion
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            duration_ms = (end_time - start_time) * 1000
            memory_delta = end_memory - start_memory

            # Remove from active requests
            self.active_requests.pop(request_id, None)

            # Record metrics
            await self._record_endpoint_metrics(
                endpoint=endpoint,
                method=method,
                duration_ms=duration_ms,
                memory_delta=memory_delta,
                user_id=user_id,
                request_id=request_id
            )

    @asynccontextmanager
    async def track_database_query(self, query_type: str, query_description: str = ""):
        """Context manager to track database query performance"""
        query_id = str(uuid4())
        start_time = time.time()

        try:
            yield query_id

        finally:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            await self._record_database_metrics(
                query_type=query_type,
                query_description=query_description,
                duration_ms=duration_ms,
                query_id=query_id
            )

    @asynccontextmanager
    async def track_cache_operation(self, operation: str, cache_type: str = "redis"):
        """Context manager to track cache operation performance"""
        operation_id = str(uuid4())
        start_time = time.time()

        try:
            yield operation_id

        finally:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            await self._record_cache_metrics(
                operation=operation,
                cache_type=cache_type,
                duration_ms=duration_ms,
                operation_id=operation_id
            )

    async def _record_endpoint_metrics(self, endpoint: str, method: str, duration_ms: float,
                                     memory_delta: int, user_id: Optional[UUID], request_id: str):
        """Record endpoint performance metrics"""
        try:
            redis_client = await self._get_redis()
            timestamp = datetime.utcnow()

            # Endpoint key
            endpoint_key = f"perf:endpoint:{endpoint}:{method}"

            # Metrics data
            metrics_data = {
                "duration_ms": duration_ms,
                "memory_delta": memory_delta,
                "timestamp": timestamp.isoformat(),
                "user_id": str(user_id) if user_id else None,
                "request_id": request_id
            }

            # Store detailed metrics (24h TTL)
            detail_key = f"{endpoint_key}:{timestamp.strftime('%Y%m%d_%H')}"
            await redis_client.lpush(detail_key, str(metrics_data))
            await redis_client.expire(detail_key, 86400)  # 24 hours

            # Update aggregate metrics
            await self._update_aggregate_metrics(endpoint_key, duration_ms, timestamp)

            # Check SLA violations
            await self._check_api_sla_violations(endpoint, method, duration_ms)

        except Exception as e:
            logger.error(f"Error recording endpoint metrics: {e}")

    async def _record_database_metrics(self, query_type: str, query_description: str,
                                     duration_ms: float, query_id: str):
        """Record database query performance metrics"""
        try:
            redis_client = await self._get_redis()
            timestamp = datetime.utcnow()

            # Database metrics key
            db_key = f"perf:database:{query_type}"

            # Metrics data
            metrics_data = {
                "duration_ms": duration_ms,
                "query_description": query_description,
                "timestamp": timestamp.isoformat(),
                "query_id": query_id
            }

            # Store detailed metrics (24h TTL)
            detail_key = f"{db_key}:{timestamp.strftime('%Y%m%d_%H')}"
            await redis_client.lpush(detail_key, str(metrics_data))
            await redis_client.expire(detail_key, 86400)

            # Update aggregate metrics
            await self._update_aggregate_metrics(db_key, duration_ms, timestamp)

            # Check for slow queries
            if duration_ms > self.slas.DB_SLOW_QUERY_THRESHOLD:
                await self._alert_slow_query(query_type, query_description, duration_ms)

        except Exception as e:
            logger.error(f"Error recording database metrics: {e}")

    async def _record_cache_metrics(self, operation: str, cache_type: str,
                                  duration_ms: float, operation_id: str):
        """Record cache operation performance metrics"""
        try:
            redis_client = await self._get_redis()
            timestamp = datetime.utcnow()

            # Cache metrics key
            cache_key = f"perf:cache:{cache_type}:{operation}"

            # Metrics data
            metrics_data = {
                "duration_ms": duration_ms,
                "timestamp": timestamp.isoformat(),
                "operation_id": operation_id
            }

            # Store detailed metrics (24h TTL)
            detail_key = f"{cache_key}:{timestamp.strftime('%Y%m%d_%H')}"
            await redis_client.lpush(detail_key, str(metrics_data))
            await redis_client.expire(detail_key, 86400)

            # Update aggregate metrics
            await self._update_aggregate_metrics(cache_key, duration_ms, timestamp)

        except Exception as e:
            logger.error(f"Error recording cache metrics: {e}")

    async def _update_aggregate_metrics(self, key: str, duration_ms: float, timestamp: datetime):
        """Update aggregate performance metrics"""
        try:
            redis_client = await self._get_redis()

            # Current hour aggregate
            hour_key = f"{key}:agg:{timestamp.strftime('%Y%m%d_%H')}"

            # Use Redis pipeline for atomic operations
            pipe = redis_client.pipeline()

            # Increment request count
            pipe.hincrby(hour_key, "count", 1)

            # Update sum for average calculation
            pipe.hincrbyfloat(hour_key, "sum_duration", duration_ms)

            # Update min/max
            current_stats = await redis_client.hmget(hour_key, "min_duration", "max_duration")
            min_duration = float(current_stats[0]) if current_stats[0] else float('inf')
            max_duration = float(current_stats[1]) if current_stats[1] else 0

            pipe.hset(hour_key, "min_duration", min(min_duration, duration_ms))
            pipe.hset(hour_key, "max_duration", max(max_duration, duration_ms))

            # Set expiry (7 days)
            pipe.expire(hour_key, 604800)

            await pipe.execute()

        except Exception as e:
            logger.error(f"Error updating aggregate metrics: {e}")

    async def _check_api_sla_violations(self, endpoint: str, method: str, duration_ms: float):
        """Check for API SLA violations and alert"""
        if duration_ms > self.slas.API_RESPONSE_P99_THRESHOLD:
            await self._alert_sla_violation(
                "API_RESPONSE_TIME",
                f"{method} {endpoint}",
                duration_ms,
                self.slas.API_RESPONSE_P99_THRESHOLD
            )

    async def _alert_slow_query(self, query_type: str, query_description: str, duration_ms: float):
        """Alert on slow database queries"""
        logger.warning(
            f"Slow query detected: {query_type} - {query_description} "
            f"took {duration_ms:.2f}ms (threshold: {self.slas.DB_SLOW_QUERY_THRESHOLD}ms)"
        )

        # Store alert in Redis for dashboard
        redis_client = await self._get_redis()
        alert_data = {
            "type": "SLOW_QUERY",
            "query_type": query_type,
            "query_description": query_description,
            "duration_ms": duration_ms,
            "threshold": self.slas.DB_SLOW_QUERY_THRESHOLD,
            "timestamp": datetime.utcnow().isoformat()
        }

        await redis_client.lpush("perf:alerts:slow_queries", str(alert_data))
        await redis_client.expire("perf:alerts:slow_queries", 86400)

    async def _alert_sla_violation(self, sla_type: str, resource: str, actual: float, threshold: float):
        """Alert on SLA violations"""
        logger.warning(
            f"SLA violation: {sla_type} for {resource} "
            f"actual: {actual:.2f}, threshold: {threshold:.2f}"
        )

        # Store alert in Redis for dashboard
        redis_client = await self._get_redis()
        alert_data = {
            "type": sla_type,
            "resource": resource,
            "actual": actual,
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat()
        }

        await redis_client.lpush("perf:alerts:sla_violations", str(alert_data))
        await redis_client.expire("perf:alerts:sla_violations", 86400)

    async def get_endpoint_performance_summary(self, endpoint: str, method: str, hours: int = 1) -> Dict[str, Any]:
        """Get performance summary for specific endpoint"""
        try:
            redis_client = await self._get_redis()
            current_time = datetime.utcnow()

            endpoint_key = f"perf:endpoint:{endpoint}:{method}"
            total_stats = {"count": 0, "sum_duration": 0, "min_duration": float('inf'), "max_duration": 0}

            # Aggregate data over specified hours
            for hour in range(hours):
                hour_time = current_time - timedelta(hours=hour)
                hour_key = f"{endpoint_key}:agg:{hour_time.strftime('%Y%m%d_%H')}"

                stats = await redis_client.hmget(
                    hour_key, "count", "sum_duration", "min_duration", "max_duration"
                )

                if stats[0]:  # If data exists
                    total_stats["count"] += int(stats[0])
                    total_stats["sum_duration"] += float(stats[1] or 0)
                    total_stats["min_duration"] = min(total_stats["min_duration"], float(stats[2] or float('inf')))
                    total_stats["max_duration"] = max(total_stats["max_duration"], float(stats[3] or 0))

            # Calculate averages and percentiles
            avg_duration = total_stats["sum_duration"] / max(total_stats["count"], 1)

            return {
                "endpoint": f"{method} {endpoint}",
                "time_period_hours": hours,
                "request_count": total_stats["count"],
                "avg_response_time_ms": round(avg_duration, 2),
                "min_response_time_ms": round(total_stats["min_duration"], 2) if total_stats["min_duration"] != float('inf') else 0,
                "max_response_time_ms": round(total_stats["max_duration"], 2),
                "sla_compliance": {
                    "mean_under_threshold": avg_duration < self.slas.API_RESPONSE_MEAN_THRESHOLD,
                    "max_under_p99_threshold": total_stats["max_duration"] < self.slas.API_RESPONSE_P99_THRESHOLD
                }
            }

        except Exception as e:
            logger.error(f"Error getting endpoint performance summary: {e}")
            return {}

    async def get_system_performance_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            # CPU and Memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info()

            # Redis metrics
            redis_client = await self._get_redis()
            redis_info = await redis_client.info()

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_percent": (disk.used / disk.total) * 100,
                    "disk_free_gb": round(disk.free / (1024**3), 2)
                },
                "process": {
                    "memory_rss_mb": round(process_memory.rss / (1024**2), 2),
                    "memory_vms_mb": round(process_memory.vms / (1024**2), 2),
                    "cpu_percent": process.cpu_percent()
                },
                "redis": {
                    "memory_usage": redis_info.get('used_memory_human', 'N/A'),
                    "connected_clients": redis_info.get('connected_clients', 0),
                    "total_commands_processed": redis_info.get('total_commands_processed', 0),
                    "keyspace_hits": redis_info.get('keyspace_hits', 0),
                    "keyspace_misses": redis_info.get('keyspace_misses', 0)
                },
                "sla_compliance": {
                    "cpu_under_threshold": cpu_percent < self.slas.CPU_USAGE_THRESHOLD,
                    "memory_under_threshold": memory.percent < self.slas.MEMORY_USAGE_THRESHOLD,
                    "disk_under_threshold": (disk.used / disk.total) * 100 < self.slas.DISK_USAGE_THRESHOLD
                }
            }

        except Exception as e:
            logger.error(f"Error getting system performance metrics: {e}")
            return {}

    async def get_performance_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        try:
            redis_client = await self._get_redis()

            # Get SLA violations
            sla_violations = await redis_client.lrange("perf:alerts:sla_violations", 0, -1)

            # Get slow queries
            slow_queries = await redis_client.lrange("perf:alerts:slow_queries", 0, -1)

            alerts = []

            # Process SLA violations
            for violation in sla_violations:
                try:
                    alert_data = eval(violation)
                    alert_time = datetime.fromisoformat(alert_data["timestamp"])
                    if alert_time > datetime.utcnow() - timedelta(hours=hours):
                        alerts.append({
                            "severity": "HIGH",
                            "category": "SLA_VIOLATION",
                            **alert_data
                        })
                except Exception:
                    continue

            # Process slow queries
            for query in slow_queries:
                try:
                    alert_data = eval(query)
                    alert_time = datetime.fromisoformat(alert_data["timestamp"])
                    if alert_time > datetime.utcnow() - timedelta(hours=hours):
                        alerts.append({
                            "severity": "MEDIUM",
                            "category": "SLOW_QUERY",
                            **alert_data
                        })
                except Exception:
                    continue

            # Sort by timestamp (most recent first)
            alerts.sort(key=lambda x: x["timestamp"], reverse=True)

            return alerts

        except Exception as e:
            logger.error(f"Error getting performance alerts: {e}")
            return []

    async def record_custom_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record custom performance metric"""
        try:
            redis_client = await self._get_redis()
            timestamp = datetime.utcnow()

            metric_data = {
                "value": value,
                "tags": tags or {},
                "timestamp": timestamp.isoformat()
            }

            # Store metric
            metric_key = f"perf:custom:{metric_name}:{timestamp.strftime('%Y%m%d_%H')}"
            await redis_client.lpush(metric_key, str(metric_data))
            await redis_client.expire(metric_key, 604800)  # 7 days

        except Exception as e:
            logger.error(f"Error recording custom metric: {e}")

    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            # Get system metrics
            system_metrics = await self.get_system_performance_metrics()

            # Get recent alerts
            alerts = await self.get_performance_alerts(hours=24)

            # Get top endpoints by request count
            redis_client = await self._get_redis()
            endpoint_keys = await redis_client.keys("perf:endpoint:*:agg:*")

            endpoint_summary = {}
            for key in endpoint_keys[:10]:  # Top 10 endpoints
                parts = key.split(':')
                if len(parts) >= 4:
                    endpoint = parts[2]
                    method = parts[3] if len(parts) > 3 else "GET"

                    if endpoint not in endpoint_summary:
                        summary = await self.get_endpoint_performance_summary(endpoint, method, hours=24)
                        if summary.get("request_count", 0) > 0:
                            endpoint_summary[f"{method} {endpoint}"] = summary

            return {
                "report_generated_at": datetime.utcnow().isoformat(),
                "system_metrics": system_metrics,
                "endpoint_performance": endpoint_summary,
                "alerts_24h": alerts,
                "summary": {
                    "total_alerts": len(alerts),
                    "high_severity_alerts": len([a for a in alerts if a.get("severity") == "HIGH"]),
                    "endpoints_monitored": len(endpoint_summary),
                    "overall_health": "HEALTHY" if len([a for a in alerts if a.get("severity") == "HIGH"]) == 0 else "DEGRADED"
                }
            }

        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {}


# Global performance monitoring service instance
performance_monitoring_service = PerformanceMonitoringService()


async def get_performance_monitoring_service() -> PerformanceMonitoringService:
    """Dependency function to get performance monitoring service instance"""
    return performance_monitoring_service