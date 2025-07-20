"""
Endpoint para recibir logs del frontend.

Este módulo maneja los logs enviados desde el frontend
para trazabilidad y debugging en producción.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.logger import get_logger

router = APIRouter()
logger = get_logger("app.api.logs")


class FrontendLogEntry(BaseModel):
    """Modelo para logs recibidos del frontend"""

    level: str = Field(..., description="Nivel del log: debug, info, warn, error")
    message: str = Field(..., description="Mensaje del log")
    timestamp: str = Field(..., description="Timestamp ISO del frontend")
    url: str = Field(..., description="URL donde ocurrió el evento")
    userAgent: str = Field(..., description="User Agent del navegador")
    userId: Optional[str] = Field(None, description="ID del usuario si está logueado")
    sessionId: Optional[str] = Field(None, description="ID de sesión del frontend")
    component: Optional[str] = Field(None, description="Componente donde ocurrió")
    action: Optional[str] = Field(None, description="Acción que se ejecutaba")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales")
    error: Optional[Dict[str, str]] = Field(None, description="Información del error si aplica")


class LogBatchRequest(BaseModel):
    """Modelo para recibir múltiples logs en batch"""

    logs: List[FrontendLogEntry] = Field(..., description="Lista de logs a procesar")


@router.post("/logs", response_model=Dict[str, str])
async def receive_frontend_log(
    log_entry: FrontendLogEntry,
    request: Request
) -> JSONResponse:
    """
    Recibe un log individual del frontend.

    Args:
        log_entry: Entrada de log del frontend
        request: Request de FastAPI para obtener IP

    Returns:
        Confirmación de recepción
    """
    try:
        # Obtener IP del cliente
        client_ip = request.client.host if request.client else "unknown"

        # Enriquecer log con información del servidor
        enriched_data = {
            "frontend_timestamp": log_entry.timestamp,
            "server_timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "url": log_entry.url,
            "user_agent": log_entry.userAgent,
            "user_id": log_entry.userId,
            "session_id": log_entry.sessionId,
            "component": log_entry.component,
            "action": log_entry.action,
            "additional_data": log_entry.data,
            "error_info": log_entry.error
        }

        # Loggear según el nivel recibido
        log_message = f"Frontend {log_entry.level.upper()}: {log_entry.message}"

        if log_entry.level == "error":
            logger.error(log_message, **enriched_data)
        elif log_entry.level == "warn":
            logger.warning(log_message, **enriched_data)
        elif log_entry.level == "info":
            logger.info(log_message, **enriched_data)
        else:  # debug
            logger.debug(log_message, **enriched_data)

        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "Log received"}
        )

    except Exception as e:
        logger.error(f"Error procesando log del frontend: {e}", 
                    frontend_log=log_entry.dict(),
                    client_ip=client_ip)
        raise HTTPException(
            status_code=500, 
            detail="Error interno procesando log"
        )


@router.post("/logs/batch", response_model=Dict[str, Any])
async def receive_frontend_logs_batch(
    batch_request: LogBatchRequest,
    request: Request
) -> JSONResponse:
    """
    Recibe múltiples logs del frontend en batch.

    Args:
        batch_request: Request con lista de logs
        request: Request de FastAPI para obtener IP

    Returns:
        Resumen de procesamiento
    """
    try:
        client_ip = request.client.host if request.client else "unknown"
        processed_count = 0
        error_count = 0

        for log_entry in batch_request.logs:
            try:
                # Procesar cada log individual
                enriched_data = {
                    "frontend_timestamp": log_entry.timestamp,
                    "server_timestamp": datetime.utcnow().isoformat(),
                    "client_ip": client_ip,
                    "url": log_entry.url,
                    "user_agent": log_entry.userAgent,
                    "user_id": log_entry.userId,
                    "session_id": log_entry.sessionId,
                    "component": log_entry.component,
                    "action": log_entry.action,
                    "batch_processing": True
                }

                log_message = f"Frontend {log_entry.level.upper()}: {log_entry.message}"

                if log_entry.level == "error":
                    logger.error(log_message, **enriched_data)
                elif log_entry.level == "warn":
                    logger.warning(log_message, **enriched_data)
                elif log_entry.level == "info":
                    logger.info(log_message, **enriched_data)
                else:
                    logger.debug(log_message, **enriched_data)

                processed_count += 1

            except Exception as e:
                error_count += 1
                logger.error(f"Error procesando log individual en batch: {e}",
                           log_entry=log_entry.dict())

        logger.info(f"Batch de logs procesado", 
                   total_logs=len(batch_request.logs),
                   processed=processed_count,
                   errors=error_count,
                   client_ip=client_ip)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "total_logs": len(batch_request.logs),
                "processed": processed_count,
                "errors": error_count
            }
        )

    except Exception as e:
        logger.error(f"Error procesando batch de logs: {e}", client_ip=client_ip)
        raise HTTPException(
            status_code=500,
            detail="Error interno procesando batch de logs"
        )


@router.get("/logs/health", response_model=Dict[str, str])
async def logs_health_check() -> JSONResponse:
    """
    Health check para el endpoint de logs.

    Returns:
        Estado del servicio de logs
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "frontend-logs",
            "timestamp": datetime.utcnow().isoformat()
        }
    )