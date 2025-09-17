# ~/app/api/v1/endpoints/performance.py
# ---------------------------------------------------------------------------------------------
# MeStore - Performance Monitoring and Optimization API Endpoints
# Copyright (c) 2025 Performance Optimization AI. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: performance.py
# Ruta: ~/app/api/v1/endpoints/performance.py
# Autor: Performance Optimization AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: API endpoints for performance monitoring, optimization, and benchmarking
#            Real-time performance metrics, cache management, and optimization controls
#
# Características:
# - Real-time performance metrics and monitoring
# - Cache management and optimization controls
# - Database optimization triggers and status
# - Search performance analytics and tuning
# - System resource monitoring and alerts
# - Performance benchmark execution and reporting
# - SLA compliance monitoring and validation
#
# ---------------------------------------------------------------------------------------------

"""
Performance API Endpoints para MeStore Marketplace.

Este módulo implementa endpoints para monitoreo y optimización de performance:
- Métricas de performance en tiempo real y monitoreo
- Gestión de cache y controles de optimización
- Triggers de optimización de base de datos y status
- Analytics de performance de búsqueda y tuning
- Monitoreo de recursos del sistema y alertas
- Ejecución de benchmarks de performance y reporting
- Monitoreo de compliance de SLA y validación
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.cache_service import cache_service, get_cache_service
from app.services.database_optimization_service import (
    database_optimization_service,
    get_database_optimization_service
)
from app.services.performance_monitoring_service import (
    performance_monitoring_service,
    get_performance_monitoring_service
)
from app.services.search_performance_service import (
    search_performance_service,
    get_search_performance_service
)
from tests.performance.performance_benchmarks import performance_benchmarks

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/metrics/overview")
async def get_performance_overview():
    """Get comprehensive performance metrics overview"""
    try:
        # Get system performance metrics
        system_metrics = await performance_monitoring_service.get_system_performance_metrics()

        # Get cache performance stats
        cache_stats = await cache_service.get_performance_stats()

        # Get search performance metrics
        search_metrics = await search_performance_service.get_search_performance_metrics()

        # Get database optimization stats
        db_stats = await database_optimization_service.get_optimization_stats()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "data": {
                "system": system_metrics,
                "cache": cache_stats,
                "search": search_metrics,
                "database": db_stats,
                "overall_health": _calculate_overall_health([
                    system_metrics.get("sla_compliance", {}),
                    {"cache_healthy": cache_stats.get("cache_metrics", {}).get("hit_rate", 0) > 80},
                    {"search_healthy": search_metrics.get("query_metrics", {}).get("avg_response_time_ms", 1000) < 200}
                ])
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting performance overview: {str(e)}"
        )


@router.get("/metrics/alerts")
async def get_performance_alerts(
    hours: int = Query(24, description="Hours to look back for alerts", ge=1, le=168)
):
    """Get recent performance alerts and SLA violations"""
    try:
        alerts = await performance_monitoring_service.get_performance_alerts(hours=hours)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "data": {
                "total_alerts": len(alerts),
                "time_period_hours": hours,
                "alerts": alerts,
                "summary": {
                    "high_severity": len([a for a in alerts if a.get("severity") == "HIGH"]),
                    "medium_severity": len([a for a in alerts if a.get("severity") == "MEDIUM"]),
                    "low_severity": len([a for a in alerts if a.get("severity") == "LOW"])
                }
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting performance alerts: {str(e)}"
        )


@router.get("/metrics/endpoints")
async def get_endpoint_performance(
    endpoint: Optional[str] = Query(None, description="Specific endpoint to analyze"),
    method: str = Query("GET", description="HTTP method"),
    hours: int = Query(1, description="Hours to analyze", ge=1, le=24)
):
    """Get performance metrics for API endpoints"""
    try:
        if endpoint:
            # Get specific endpoint performance
            endpoint_summary = await performance_monitoring_service.get_endpoint_performance_summary(
                endpoint=endpoint,
                method=method,
                hours=hours
            )
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success",
                "data": endpoint_summary
            }
        else:
            # Get comprehensive performance report
            report = await performance_monitoring_service.generate_performance_report()
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success",
                "data": report
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting endpoint performance: {str(e)}"
        )


@router.get("/cache/status")
async def get_cache_status():
    """Get comprehensive cache status and performance metrics"""
    try:
        cache_stats = await cache_service.get_performance_stats()
        cache_metrics = await cache_service.record_cache_metrics()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "data": {
                "performance_stats": cache_stats,
                "current_metrics": cache_metrics,
                "recommendations": _generate_cache_recommendations(cache_metrics)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting cache status: {str(e)}"
        )


@router.post("/cache/warm-up")
async def warm_up_cache(db: AsyncSession = Depends(get_db)):
    """Manually trigger cache warm-up process"""
    try:
        warmup_stats = await cache_service.warmup_cache(db)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "message": "Cache warm-up completed",
            "data": warmup_stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error warming up cache: {str(e)}"
        )


@router.delete("/cache/invalidate")
async def invalidate_cache(
    pattern: Optional[str] = Query(None, description="Cache key pattern to invalidate"),
    cache_type: str = Query("all", description="Type of cache to invalidate")
):
    """Invalidate cache entries based on pattern or type"""
    try:
        if pattern:
            deleted_count = await cache_service.delete_pattern(pattern)
        elif cache_type == "search":
            deleted_count = await cache_service.invalidate_search_cache()
        elif cache_type == "all":
            deleted_count = await cache_service.delete_pattern("*")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cache_type. Use 'search' or 'all', or provide a pattern."
            )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "message": f"Cache invalidation completed",
            "data": {
                "deleted_keys": deleted_count,
                "pattern": pattern,
                "cache_type": cache_type
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error invalidating cache: {str(e)}"
        )


@router.get("/database/optimization-status")
async def get_database_optimization_status():
    """Get database optimization status and statistics"""
    try:
        optimization_stats = await database_optimization_service.get_optimization_stats()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "data": optimization_stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting database optimization status: {str(e)}"
        )


@router.post("/database/optimize")
async def optimize_database(db: AsyncSession = Depends(get_db)):
    """Trigger database optimization processes"""
    try:
        # Run database optimizations
        optimization_results = {}

        # Create performance indexes
        created_indexes = await database_optimization_service.create_performance_indexes(db)
        optimization_results["created_indexes"] = created_indexes

        # Optimize connection pool
        pool_optimization = await database_optimization_service.optimize_connection_pool()
        optimization_results["connection_pool"] = pool_optimization

        # Create/refresh materialized views
        created_views = await database_optimization_service.create_materialized_views(db)
        optimization_results["materialized_views"] = created_views

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "message": "Database optimization completed",
            "data": optimization_results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error optimizing database: {str(e)}"
        )


@router.get("/database/slow-queries")
async def get_slow_queries(db: AsyncSession = Depends(get_db)):
    """Get analysis of slow database queries"""
    try:
        slow_queries = await database_optimization_service.analyze_slow_queries(db)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "data": {
                "total_slow_queries": len(slow_queries),
                "slow_queries": slow_queries,
                "recommendations": _generate_db_optimization_recommendations(slow_queries)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting slow queries: {str(e)}"
        )


@router.get("/search/performance")
async def get_search_performance():
    """Get search performance metrics and analytics"""
    try:
        search_metrics = await search_performance_service.get_search_performance_metrics()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "data": search_metrics
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting search performance: {str(e)}"
        )


@router.post("/search/warm-up")
async def warm_up_search_cache():
    """Warm up search cache with popular queries"""
    try:
        warmup_results = await search_performance_service.warm_up_search_cache()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "message": "Search cache warm-up completed",
            "data": warmup_results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error warming up search cache: {str(e)}"
        )


@router.post("/benchmarks/run")
async def run_performance_benchmarks(
    benchmark_type: str = Query("comprehensive", description="Type of benchmark to run"),
    db: AsyncSession = Depends(get_db)
):
    """Run performance benchmarks and generate report"""
    try:
        if benchmark_type == "comprehensive":
            report = await performance_benchmarks.run_comprehensive_benchmarks(db)
        elif benchmark_type == "database":
            report = {
                "simple_query": await performance_benchmarks.test_database_simple_query_performance(db),
                "complex_query": await performance_benchmarks.test_database_complex_query_performance(db),
                "aggregation": await performance_benchmarks.test_database_aggregation_performance(db)
            }
        elif benchmark_type == "cache":
            report = await performance_benchmarks.test_cache_performance_benchmarks()
        elif benchmark_type == "search":
            report = await performance_benchmarks.test_search_performance_benchmarks()
        elif benchmark_type == "memory":
            report = await performance_benchmarks.test_memory_usage_benchmarks()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid benchmark type. Use: comprehensive, database, cache, search, or memory"
            )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "benchmark_type": benchmark_type,
            "data": report
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running performance benchmarks: {str(e)}"
        )


@router.get("/sla/compliance")
async def get_sla_compliance():
    """Get SLA compliance status and violations"""
    try:
        # Get recent alerts to check SLA violations
        alerts = await performance_monitoring_service.get_performance_alerts(hours=24)

        # Get system metrics for current compliance
        system_metrics = await performance_monitoring_service.get_system_performance_metrics()

        # Calculate SLA compliance
        sla_violations = [alert for alert in alerts if alert.get("type") == "SLA_VIOLATION"]

        compliance_score = max(0, 100 - (len(sla_violations) * 5))  # Each violation -5%

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "data": {
                "compliance_score": compliance_score,
                "compliance_status": "COMPLIANT" if compliance_score >= 95 else "NON_COMPLIANT",
                "sla_violations_24h": len(sla_violations),
                "recent_violations": sla_violations[:10],  # Last 10 violations
                "system_health": system_metrics.get("sla_compliance", {}),
                "recommendations": _generate_sla_recommendations(sla_violations)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting SLA compliance: {str(e)}"
        )


@router.post("/optimization/auto-tune")
async def auto_tune_performance(db: AsyncSession = Depends(get_db)):
    """Automatically tune performance based on current metrics"""
    try:
        tuning_results = {}

        # Auto-tune cache settings based on hit rates
        cache_metrics = await cache_service.record_cache_metrics()
        if cache_metrics.get("hit_rate", 0) < 80:
            warmup_stats = await cache_service.warmup_cache(db)
            tuning_results["cache_warmup"] = warmup_stats

        # Auto-optimize database if slow queries detected
        slow_queries = await database_optimization_service.analyze_slow_queries(db)
        if len(slow_queries) > 5:
            pool_optimization = await database_optimization_service.optimize_connection_pool()
            tuning_results["database_optimization"] = pool_optimization

        # Auto-warm search cache if performance is poor
        search_metrics = await search_performance_service.get_search_performance_metrics()
        if search_metrics.get("query_metrics", {}).get("avg_response_time_ms", 0) > 200:
            search_warmup = await search_performance_service.warm_up_search_cache()
            tuning_results["search_warmup"] = search_warmup

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "message": "Auto-tuning completed",
            "data": tuning_results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error auto-tuning performance: {str(e)}"
        )


def _calculate_overall_health(health_indicators: List[Dict[str, Any]]) -> str:
    """Calculate overall system health based on indicators"""
    healthy_count = 0
    total_count = 0

    for indicator in health_indicators:
        for key, value in indicator.items():
            total_count += 1
            if isinstance(value, bool) and value:
                healthy_count += 1
            elif isinstance(value, (int, float)) and value > 0:
                healthy_count += 1

    if total_count == 0:
        return "UNKNOWN"

    health_percentage = (healthy_count / total_count) * 100

    if health_percentage >= 90:
        return "EXCELLENT"
    elif health_percentage >= 75:
        return "GOOD"
    elif health_percentage >= 60:
        return "FAIR"
    else:
        return "POOR"


def _generate_cache_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Generate cache optimization recommendations"""
    recommendations = []
    hit_rate = metrics.get("hit_rate", 0)

    if hit_rate < 70:
        recommendations.append("Cache hit rate is low. Consider increasing cache TTL and warming up popular content.")
    elif hit_rate < 85:
        recommendations.append("Cache performance is moderate. Review cache invalidation patterns.")

    if metrics.get("compression_saves", 0) > 0:
        recommendations.append("Cache compression is working well and saving memory.")

    return recommendations or ["Cache performance is optimal."]


def _generate_db_optimization_recommendations(slow_queries: List[Dict[str, Any]]) -> List[str]:
    """Generate database optimization recommendations"""
    recommendations = []

    if len(slow_queries) > 10:
        recommendations.append("High number of slow queries detected. Consider adding database indexes.")

    high_priority_queries = [q for q in slow_queries if q.get("optimization_priority") == "HIGH"]
    if high_priority_queries:
        recommendations.append(f"{len(high_priority_queries)} high-priority slow queries need immediate attention.")

    return recommendations or ["Database performance is acceptable."]


def _generate_sla_recommendations(violations: List[Dict[str, Any]]) -> List[str]:
    """Generate SLA compliance recommendations"""
    recommendations = []

    if len(violations) > 5:
        recommendations.append("Multiple SLA violations detected. Immediate performance optimization required.")
    elif len(violations) > 0:
        recommendations.append("Some SLA violations present. Monitor and optimize affected components.")

    return recommendations or ["SLA compliance is good. Continue monitoring."]