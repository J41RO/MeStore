# ~/app/api/v1/health.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Health Check Endpoints with Redis
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: health.py
# Ruta: ~/app/api/v1/health.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Endpoints de salud del sistema incluyendo Redis, PostgreSQL y servicios
#            Monitoreo completo del estado de la aplicación
#
# Modificaciones:
# 2025-07-17 - Implementación inicial con Redis health check
#
# ---------------------------------------------------------------------------------------------

"""
Health Check Endpoints for MeStock

Provides comprehensive health monitoring for:
- Redis cache and queuing system
- PostgreSQL database
- Application services
- System resources
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import time
import asyncio
from sqlalchemy import text
from datetime import datetime

from app.core.redis import get_redis, RedisService, get_redis_service
from app.api.v1.deps import get_db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def basic_health():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MeStock API",
        "version": "1.0.0"
    }

@router.get("/redis")
async def redis_health(redis_client = Depends(get_redis)):
    """Redis health and functionality check"""
    try:
        start_time = time.time()

        # Test basic connectivity
        ping_result = await redis_client.ping()

        # Test SET/GET operations
        test_key = f"health_check_{int(time.time())}"
        await redis_client.set(test_key, "health_test_value", ex=60)
        test_value = await redis_client.get(test_key)
        await redis_client.delete(test_key)

        # Test HASH operations (sessions)
        session_key = f"session_health_{int(time.time())}"
        await redis_client.hset(session_key, mapping={"user_id": "test", "role": "health_check"})
        session_data = await redis_client.hgetall(session_key)
        await redis_client.delete(session_key)

        # Test LIST operations (queues)
        queue_key = f"queue_health_{int(time.time())}"
        await redis_client.lpush(queue_key, "health_task_1", "health_task_2")
        queue_length = await redis_client.llen(queue_key)
        await redis_client.delete(queue_key)

        response_time = time.time() - start_time

        return {
            "status": "healthy",
            "service": "Redis",
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": round(response_time * 1000, 2),
            "tests": {
                "ping": ping_result,
                "string_operations": test_value == "health_test_value",
                "hash_operations": session_data.get("user_id") == "test",
                "list_operations": queue_length == 2
            },
            "details": {
                "connection_pool": "active",
                "operations_tested": ["PING", "SET/GET", "HSET/HGETALL", "LPUSH/LLEN"]
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "Redis",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@router.get("/redis/services")
async def redis_services_health(redis_svc = Depends(get_redis_service)):
    """Test Redis high-level services (cache, sessions, queues)"""
    try:
        start_time = time.time()
        results = {}

        # Test cache service
        cache_key = f"cache_test_{int(time.time())}"
        cache_success = await redis_svc.cache_set(cache_key, "cache_test_data", expire=60)
        cache_data = await redis_svc.cache_get(cache_key)
        cache_delete = await redis_svc.cache_delete(cache_key)

        results["cache_service"] = {
            "set": cache_success,
            "get": cache_data == "cache_test_data",
            "delete": cache_delete
        }

        # Test session service
        session_id = f"session_test_{int(time.time())}"
        session_data = {"user_id": 123, "username": "test_user", "role": "admin"}
        session_success = await redis_svc.session_set(session_id, session_data, expire=60)
        retrieved_session = await redis_svc.session_get(session_id)
        session_delete = await redis_svc.session_delete(session_id)

        results["session_service"] = {
            "set": session_success,
            "get": retrieved_session == session_data,
            "delete": session_delete
        }

        # Test queue service
        queue_name = f"test_queue_{int(time.time())}"
        queue_message = {"task": "health_check", "data": "test_payload"}
        queue_push = await redis_svc.queue_push(queue_name, queue_message)
        queue_messages = await redis_svc.queue_pop(queue_name, "health_group", "health_worker")

        results["queue_service"] = {
            "push": queue_push,
            "pop": len(queue_messages) > 0 and queue_messages[0]["data"] == queue_message
        }

        response_time = time.time() - start_time

        # Check if all services are healthy
        all_healthy = all(
            all(test_results.values()) 
            for test_results in results.values()
        )

        return {
            "status": "healthy" if all_healthy else "degraded",
            "service": "Redis High-Level Services",
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": round(response_time * 1000, 2),
            "services": results,
            "summary": {
                "cache_service": "healthy" if all(results["cache_service"].values()) else "unhealthy",
                "session_service": "healthy" if all(results["session_service"].values()) else "unhealthy",
                "queue_service": "healthy" if all(results["queue_service"].values()) else "unhealthy"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "Redis High-Level Services",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@router.get("/database")
async def database_health(db = Depends(get_db)):
    """PostgreSQL database health check"""
    try:
        start_time = time.time()

        # Test basic connectivity
        result = await db.execute(text("SELECT 1 as health_check"))
        health_value = result.scalar()

        # Test current timestamp (ensures DB is responsive)
        result = await db.execute(text("SELECT NOW() as current_time"))
        current_time = result.scalar()

        response_time = time.time() - start_time

        return {
            "status": "healthy",
            "service": "PostgreSQL",
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": round(response_time * 1000, 2),
            "tests": {
                "connectivity": health_value == 1,
                "timestamp_query": current_time is not None
            },
            "database_time": current_time.isoformat() if current_time else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "PostgreSQL",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@router.get("/full")
async def full_health_check(
    redis_client = Depends(get_redis),
    redis_svc = Depends(get_redis_service),
    db = Depends(get_db)
):
    """Comprehensive health check of all services"""
    try:
        start_time = time.time()

        # Run all health checks concurrently
        redis_task = redis_health(redis_client)
        redis_services_task = redis_services_health(redis_svc)
        db_task = database_health(db)

        redis_result, redis_services_result, db_result = await asyncio.gather(
            redis_task, redis_services_task, db_task,
            return_exceptions=True
        )

        response_time = time.time() - start_time

        # Process results
        services = {}
        overall_status = "healthy"

        # Redis basic
        if isinstance(redis_result, Exception):
            services["redis"] = {"status": "unhealthy", "error": str(redis_result)}
            overall_status = "unhealthy"
        else:
            services["redis"] = {"status": redis_result["status"]}

        # Redis services
        if isinstance(redis_services_result, Exception):
            services["redis_services"] = {"status": "unhealthy", "error": str(redis_services_result)}
            overall_status = "unhealthy"
        else:
            services["redis_services"] = {"status": redis_services_result["status"]}

        # Database
        if isinstance(db_result, Exception):
            services["database"] = {"status": "unhealthy", "error": str(db_result)}
            overall_status = "unhealthy"
        else:
            services["database"] = {"status": db_result["status"]}

        return {
            "status": overall_status,
            "service": "MeStock Full System",
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": round(response_time * 1000, 2),
            "services": services,
            "summary": {
                "total_services": len(services),
                "healthy_services": sum(1 for s in services.values() if s["status"] == "healthy"),
                "unhealthy_services": sum(1 for s in services.values() if s["status"] != "healthy")
            }
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "MeStock Full System",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }