# ~/app/api/v1/handlers/exceptions.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Sistema de Exception Handlers Personalizados
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: exceptions.py
# Ruta: ~/app/api/v1/handlers/exceptions.py
# Autor: Jairo
# Fecha de Creación: 2025-07-20
# Última Actualización: 2025-07-20
# Versión: 1.0.0
# Propósito: Definir exception handlers centralizados para FastAPI
#            Manejo consistente de errores con formato JSON estandarizado
#
# Modificaciones:
# 2025-07-20 - Creación inicial del sistema de exception handlers
#
# ---------------------------------------------------------------------------------------------

"""
Sistema de Exception Handlers Personalizados para FastAPI.

Este módulo contiene:
- Clase base AppException para excepciones personalizadas
- Excepciones específicas del dominio (EmbeddingNotFoundException, etc.)
- Función register_exception_handlers para configurar FastAPI
- Handlers para HTTPException, RequestValidationError y errores globales
"""

import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configurar logger para exceptions
logger = logging.getLogger(__name__)


class AppException(Exception):
    """
    Clase base para todas las excepciones personalizadas de la aplicación.

    Proporciona estructura consistente para manejo de errores específicos
    del dominio con código de estado HTTP asociado.
    """

    def __init__(
        self, message: str, status_code: int = 500, error_code: str = None
    ) -> None:
        """
        Inicializa excepción personalizada.

        Args:
            message: Mensaje descriptivo del error
            status_code: Código HTTP asociado (default: 500)
            error_code: Código de error específico (default: nombre de la clase)
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__


class EmbeddingNotFoundException(AppException):
    """Excepción cuando no se encuentra un embedding solicitado."""

    def __init__(self, embedding_id: str = None) -> None:
        message = f"No se encontró el embedding solicitado"
        if embedding_id:
            message = f"No se encontró el embedding con ID: {embedding_id}"
        super().__init__(
            message=message, status_code=404, error_code="EmbeddingNotFound"
        )


class InvalidEmbeddingPayloadException(AppException):
    """Excepción cuando el payload del embedding es inválido."""

    def __init__(self, details: str = None) -> None:
        message = "Payload de embedding inválido"
        if details:
            message = f"Payload de embedding inválido: {details}"
        super().__init__(
            message=message, status_code=422, error_code="InvalidEmbeddingPayload"
        )


class EmbeddingProcessingException(AppException):
    """Excepción durante el procesamiento de embeddings."""

    def __init__(self, details: str = None) -> None:
        message = "Error procesando embedding"
        if details:
            message = f"Error procesando embedding: {details}"
        super().__init__(
            message=message, status_code=500, error_code="EmbeddingProcessingError"
        )


def create_error_response(
    error_code: str, detail: str, status_code: int, request_path: str = None
) -> Dict[str, Any]:
    """
    Crear respuesta de error estandarizada.

    Args:
        error_code: Código identificador del error
        detail: Descripción detallada del error
        status_code: Código de estado HTTP
        request_path: Ruta que generó el error (opcional)

    Returns:
        Diccionario con estructura estandarizada de error
    """
    error_response = {"error": error_code, "detail": detail, "status_code": status_code}

    if request_path:
        error_response["path"] = request_path

    return error_response


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handler para excepciones personalizadas de la aplicación.

    Args:
        request: Request de FastAPI
        exc: Instancia de AppException

    Returns:
        JSONResponse con formato estandarizado
    """
    logger.error(
        f"AppException raised: {exc.error_code} - {exc.message} - Path: {request.url.path}"
    )

    error_response = create_error_response(
        error_code=exc.error_code,
        detail=exc.message,
        status_code=exc.status_code,
        request_path=str(request.url.path),
    )

    return JSONResponse(status_code=exc.status_code, content=error_response)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler para HTTPException de FastAPI.

    Args:
        request: Request de FastAPI
        exc: Instancia de HTTPException

    Returns:
        JSONResponse con formato estandarizado
    """
    logger.warning(
        f"HTTPException: {exc.status_code} - {exc.detail} - Path: {request.url.path}"
    )

    error_response = create_error_response(
        error_code=f"HTTP{exc.status_code}",
        detail=str(exc.detail),
        status_code=exc.status_code,
        request_path=str(request.url.path),
    )

    return JSONResponse(status_code=exc.status_code, content=error_response)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handler para errores de validación de request.

    Args:
        request: Request de FastAPI
        exc: Instancia de RequestValidationError

    Returns:
        JSONResponse con formato estandarizado
    """
    logger.warning(f"Validation error: {exc.errors()} - Path: {request.url.path}")

    # Extraer detalles de errores de validación
    validation_details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        validation_details.append(f"{field}: {error['msg']}")

    detail = "Errores de validación: " + "; ".join(validation_details)

    error_response = create_error_response(
        error_code="ValidationError",
        detail=detail,
        status_code=422,
        request_path=str(request.url.path),
    )

    return JSONResponse(status_code=422, content=error_response)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler para excepciones no capturadas (fallback global).

    Args:
        request: Request de FastAPI
        exc: Cualquier excepción no manejada

    Returns:
        JSONResponse con error 500 estandarizado
    """
    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)} - Path: {request.url.path}",
        exc_info=True,
    )

    error_response = create_error_response(
        error_code="InternalServerError",
        detail="Error interno del servidor. Por favor contacte al administrador.",
        status_code=500,
        request_path=str(request.url.path),
    )

    return JSONResponse(status_code=500, content=error_response)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registrar todos los exception handlers en la aplicación FastAPI.

    Configura handlers para:
    - AppException (excepciones personalizadas)
    - HTTPException (errores HTTP estándar)
    - RequestValidationError (errores de validación)
    - Exception (fallback global para errores no manejados)

    Args:
        app: Instancia de FastAPI
    """
    # Handler para excepciones personalizadas de la app
    app.add_exception_handler(AppException, app_exception_handler)

    # Handler para HTTPException de FastAPI
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Handler para errores de validación
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Handler global para excepciones no capturadas
    app.add_exception_handler(Exception, global_exception_handler)

    logger.info("Exception handlers registered successfully")
