# ~/app/api/health_simple.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Simple Health Check Endpoints (Root Level)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: health_simple.py
# Ruta: ~/app/api/health_simple.py
# Autor: Jairo
# Fecha de Creación: 2025-07-20
# Última Actualización: 2025-07-20
# Versión: 1.0.0
# Propósito: Endpoints simples /health y /ready para load balancers y Kubernetes
#            Cumple requerimientos específicos de la tarea 0.2.6.6
#
# Modificaciones:
# 2025-07-20 - Implementación inicial con endpoints /health y /ready
#
# ---------------------------------------------------------------------------------------------

"""
Simple Health Check Endpoints for Load Balancers and Kubernetes

Provides standard health monitoring endpoints:
- /health: Always returns 200 OK if app is alive
- /ready: Checks dependencies (PostgreSQL, Redis) for readiness
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import time
import asyncio
from sqlalchemy import text
from datetime import datetime
import structlog

from app.core.redis import get_redis
from app.core.database import get_db

# Configurar logger estructurado para health checks
logger = structlog.get_logger("health_check")

router = APIRouter(tags=["health-simple"])

@router.get("/health", summary="Basic Health Check", description="Always returns 200 OK if application is alive")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint for load balancers.

    Returns:
        {"status": "healthy"} with 200 OK if application is running
    """
    await logger.ainfo("Health check requested", endpoint="/health", status="healthy")
    return {"status": "healthy"}


@router.get("/ready", summary="Readiness Check", description="Checks all dependencies before accepting traffic")
async def readiness_check(
    redis_client = Depends(get_redis),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Readiness check endpoint for Kubernetes and orchestrators.

    Verifies:
    - PostgreSQL database connectivity
    - Redis cache connectivity

    Returns:
        200 OK if all dependencies are ready
        503 Service Unavailable if any dependency fails
    """
    start_time = time.time()
    checks = {}
    all_ready = True

    await logger.ainfo("Readiness check started", endpoint="/ready")

    # Check PostgreSQL
    try:
        await logger.adebug("Checking PostgreSQL connectivity")
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        checks["postgresql"] = {"status": "ready", "error": None}
        await logger.ainfo("PostgreSQL check passed", service="postgresql", status="ready")
    except Exception as e:
        checks["postgresql"] = {"status": "not_ready", "error": str(e)}
        all_ready = False
        await logger.aerror("PostgreSQL check failed", service="postgresql", error=str(e))

    # Check Redis
    try:
        await logger.adebug("Checking Redis connectivity")
        await redis_client.ping()
        checks["redis"] = {"status": "ready", "error": None}
        await logger.ainfo("Redis check passed", service="redis", status="ready")
    except Exception as e:
        checks["redis"] = {"status": "not_ready", "error": str(e)}
        all_ready = False
        await logger.aerror("Redis check failed", service="redis", error=str(e))

    response_time = round((time.time() - start_time) * 1000, 2)

    response = {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "response_time_ms": response_time,
        "timestamp": datetime.utcnow().isoformat()
    }

    if all_ready:
        await logger.ainfo("Readiness check completed", 
                          endpoint="/ready", 
                          status="ready", 
                          response_time_ms=response_time,
                          postgresql_status=checks["postgresql"]["status"],
                          redis_status=checks["redis"]["status"])
        return response
    else:
        await logger.aerror("Readiness check failed", 
                           endpoint="/ready", 
                           status="not_ready", 
                           response_time_ms=response_time,
                           failed_checks=[service for service, check in checks.items() if check["status"] != "ready"])
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response
        )
