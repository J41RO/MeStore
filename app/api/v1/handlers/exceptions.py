# ~/app/api/v1/handlers/exceptions.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Sistema de Exception Handlers Personalizados con Response Standardization
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: exceptions.py
# Ruta: ~/app/api/v1/handlers/exceptions.py
# Autor: Jairo
# Fecha de Creación: 2025-07-20
# Última Actualización: 2025-09-17
# Versión: 2.0.0
# Propósito: Definir exception handlers centralizados para FastAPI con response standardization
#            Manejo consistente de errores con formato JSON estandarizado y response schemas
#
# Modificaciones:
# 2025-07-20 - Creación inicial del sistema de exception handlers
# 2025-09-17 - Implementación de response standardization con schemas base
#
# ---------------------------------------------------------------------------------------------

"""
Sistema de Exception Handlers Personalizados para FastAPI con Response Standardization.

Este módulo contiene:
- Clase base AppException para excepciones personalizadas
- Excepciones específicas del dominio (EmbeddingNotFoundException, etc.)
- Función register_exception_handlers para configurar FastAPI
- Handlers para HTTPException, RequestValidationError y errores globales
- Integration con standardized response schemas
"""

import logging
import uuid
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.response_base import (
    ErrorCodes,
    ErrorDetail,
    ErrorResponse,
    ValidationErrorResponse,
    create_error_response,
    create_validation_error_response
)

# Configurar logger para exceptions
logger = logging.getLogger(__name__)


class AppException(Exception):
    """
    Clase base para todas las excepciones personalizadas de la aplicación.

    Proporciona estructura consistente para manejo de errores específicos
    del dominio con código de estado HTTP asociado y standardized response format.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = None,
        details: List[ErrorDetail] = None
    ) -> None:
        """
        Inicializa excepción personalizada.

        Args:
            message: Mensaje descriptivo del error
            status_code: Código HTTP asociado (default: 500)
            error_code: Código de error específico (default: nombre de la clase)
            details: Lista de detalles específicos del error
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or []


class EmbeddingNotFoundException(AppException):
    """Excepción cuando no se encuentra un embedding solicitado."""

    def __init__(self, embedding_id: str = None) -> None:
        message = f"No se encontró el embedding solicitado"
        if embedding_id:
            message = f"No se encontró el embedding con ID: {embedding_id}"
        super().__init__(
            message=message,
            status_code=404,
            error_code=ErrorCodes.NOT_FOUND
        )


class InvalidEmbeddingPayloadException(AppException):
    """Excepción cuando el payload del embedding es inválido."""

    def __init__(self, details: str = None) -> None:
        message = "Payload de embedding inválido"
        error_details = []
        if details:
            message = f"Payload de embedding inválido: {details}"
            error_details = [ErrorDetail(
                field="embedding_payload",
                message=details,
                error_type="validation_error"
            )]
        super().__init__(
            message=message,
            status_code=422,
            error_code=ErrorCodes.VALIDATION_ERROR,
            details=error_details
        )


class EmbeddingProcessingException(AppException):
    """Excepción durante el procesamiento de embeddings."""

    def __init__(self, details: str = None) -> None:
        message = "Error procesando embedding"
        if details:
            message = f"Error procesando embedding: {details}"
        super().__init__(
            message=message,
            status_code=500,
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR
        )


# Business domain specific exceptions
class AuthenticationException(AppException):
    """Excepción de autenticación."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code=ErrorCodes.UNAUTHORIZED
        )


class AuthorizationException(AppException):
    """Excepción de autorización."""

    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code=ErrorCodes.FORBIDDEN
        )


class ResourceNotFoundException(AppException):
    """Excepción cuando un recurso no se encuentra."""

    def __init__(self, resource_type: str = "Resource", resource_id: str = None) -> None:
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(
            message=message,
            status_code=404,
            error_code=ErrorCodes.NOT_FOUND
        )


class BusinessLogicException(AppException):
    """Excepción para errores de lógica de negocio."""

    def __init__(self, message: str, error_code: str = None) -> None:
        super().__init__(
            message=message,
            status_code=409,
            error_code=error_code or ErrorCodes.CONFLICT
        )


class PaymentException(AppException):
    """Excepción para errores de pago."""

    def __init__(self, message: str = "Payment processing failed") -> None:
        super().__init__(
            message=message,
            status_code=402,
            error_code=ErrorCodes.PAYMENT_FAILED
        )


class RateLimitException(AppException):
    """Excepción para límites de tasa superados."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(
            message=message,
            status_code=429,
            error_code=ErrorCodes.TOO_MANY_REQUESTS
        )


def generate_request_id() -> str:
    """Generate a unique request ID for error tracking."""
    return f"req_{str(uuid.uuid4())[:8]}"


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handler para excepciones personalizadas de la aplicación.

    Args:
        request: Request de FastAPI
        exc: Instancia de AppException

    Returns:
        JSONResponse con formato estandarizado usando ErrorResponse schema
    """
    request_id = generate_request_id()

    logger.error(
        f"AppException raised: {exc.error_code} - {exc.message} - Path: {request.url.path} - RequestID: {request_id}"
    )

    error_response = create_error_response(
        error_code=exc.error_code,
        error_message=exc.message,
        details=exc.details,
        message=f"Request failed at {request.url.path}",
        request_id=request_id
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json')
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler para HTTPException de FastAPI.

    Args:
        request: Request de FastAPI
        exc: Instancia de HTTPException

    Returns:
        JSONResponse con formato estandarizado usando ErrorResponse schema
    """
    request_id = generate_request_id()

    logger.warning(
        f"HTTPException: {exc.status_code} - {exc.detail} - Path: {request.url.path} - RequestID: {request_id}"
    )

    # Map HTTP status codes to standardized error codes
    error_code_mapping = {
        400: ErrorCodes.BAD_REQUEST,
        401: ErrorCodes.UNAUTHORIZED,
        403: ErrorCodes.FORBIDDEN,
        404: ErrorCodes.NOT_FOUND,
        405: ErrorCodes.METHOD_NOT_ALLOWED,
        409: ErrorCodes.CONFLICT,
        429: ErrorCodes.TOO_MANY_REQUESTS,
        500: ErrorCodes.INTERNAL_SERVER_ERROR,
        502: ErrorCodes.BAD_GATEWAY,
        503: ErrorCodes.SERVICE_UNAVAILABLE,
        504: ErrorCodes.GATEWAY_TIMEOUT,
    }

    error_code = error_code_mapping.get(exc.status_code, f"HTTP_{exc.status_code}")

    error_response = create_error_response(
        error_code=error_code,
        error_message=str(exc.detail),
        message=f"HTTP error {exc.status_code} at {request.url.path}",
        request_id=request_id
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json')
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handler para errores de validación de request.

    Args:
        request: Request de FastAPI
        exc: Instancia de RequestValidationError

    Returns:
        JSONResponse con formato estandarizado usando ValidationErrorResponse schema
    """
    request_id = generate_request_id()

    logger.warning(
        f"Validation error: {exc.errors()} - Path: {request.url.path} - RequestID: {request_id}"
    )

    # Convertir errores de validación a ErrorDetail objects
    validation_details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        validation_details.append(ErrorDetail(
            field=field,
            message=error.get("msg", "Validation error"),
            error_type=error.get("type", "validation_error")
        ))

    error_response = create_validation_error_response(
        validation_errors=validation_details,
        message=f"Request validation failed at {request.url.path}"
    )
    error_response.request_id = request_id

    return JSONResponse(
        status_code=422,
        content=error_response.model_dump(mode='json')
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler para excepciones no capturadas (fallback global).

    Args:
        request: Request de FastAPI
        exc: Cualquier excepción no manejada

    Returns:
        JSONResponse con error 500 estandarizado usando ErrorResponse schema
    """
    request_id = generate_request_id()

    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)} - Path: {request.url.path} - RequestID: {request_id}",
        exc_info=True,
    )

    error_response = create_error_response(
        error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
        error_message="Error interno del servidor. Por favor contacte al administrador.",
        message=f"Unexpected error at {request.url.path}",
        request_id=request_id
    )

    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(mode='json')
    )


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
