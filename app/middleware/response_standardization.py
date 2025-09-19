# ~/app/middleware/response_standardization.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Response Standardization Middleware
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Response Standardization Middleware for FastAPI.

This middleware provides:
- Automatic response formatting for non-standardized endpoints
- Response time tracking and headers
- Content-Type validation and standardization
- API version headers
- Request ID tracking
"""

import time
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
import json
import logging

from app.schemas.response_base import create_success_response

logger = logging.getLogger(__name__)


class ResponseStandardizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware para estandarizar todas las respuestas de la API.

    Features:
    - Añade headers estándar (Request-ID, Response-Time, API-Version)
    - Formatea respuestas que no siguen el formato estándar
    - Tracking de tiempo de respuesta
    - Content-Type validation
    """

    def __init__(self, app, api_version: str = "1.0.0"):
        super().__init__(app)
        self.api_version = api_version

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and standardize response."""

        # Generate request ID for tracking
        request_id = f"req_{str(uuid.uuid4())[:8]}"
        start_time = time.time()

        # Add request ID to request state for access in handlers
        request.state.request_id = request_id

        try:
            # Process request
            response = await call_next(request)

            # Calculate response time
            process_time = time.time() - start_time

            # Add standard headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{process_time:.4f}s"
            response.headers["X-API-Version"] = self.api_version

            # Only process JSON responses for standardization
            if response.headers.get("content-type", "").startswith("application/json"):
                response = await self._standardize_json_response(request, response)

            return response

        except Exception as e:
            # If middleware processing fails, log and return original response
            logger.error(f"Response standardization middleware error: {e}")
            process_time = time.time() - start_time

            # Create error response
            error_response = JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "error_code": "MIDDLEWARE_ERROR",
                    "error_message": "Response processing failed",
                    "timestamp": time.time(),
                    "version": self.api_version
                }
            )
            error_response.headers["X-Request-ID"] = request_id
            error_response.headers["X-Response-Time"] = f"{process_time:.4f}s"
            error_response.headers["X-API-Version"] = self.api_version

            return error_response

    async def _standardize_json_response(self, request: Request, response: Response) -> Response:
        """
        Standardize JSON response format if not already standardized.

        Args:
            request: The original request
            response: The response to potentially standardize

        Returns:
            Standardized response
        """
        try:
            # Skip standardization for certain paths
            skip_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
            if any(request.url.path.startswith(path) for path in skip_paths):
                return response

            # Skip if already an error response (handled by exception handlers)
            if response.status_code >= 400:
                return response

            # Get response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            if not body:
                return response

            try:
                response_data = json.loads(body.decode())
            except json.JSONDecodeError:
                return response

            # Check if response is already standardized
            if isinstance(response_data, dict) and "status" in response_data:
                # Already standardized, recreate response with same content
                return JSONResponse(
                    content=response_data,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )

            # Standardize the response
            if response.status_code == 200:
                standardized_data = create_success_response(
                    data=response_data,
                    message=self._get_success_message(request)
                )

                return JSONResponse(
                    content=standardized_data.model_dump(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )

            return response

        except Exception as e:
            logger.warning(f"Failed to standardize response: {e}")
            return response

    def _get_success_message(self, request: Request) -> str:
        """Generate appropriate success message based on request method and path."""
        method = request.method.upper()
        path = request.url.path

        method_messages = {
            "GET": "Data retrieved successfully",
            "POST": "Resource created successfully",
            "PUT": "Resource updated successfully",
            "PATCH": "Resource partially updated successfully",
            "DELETE": "Resource deleted successfully"
        }

        base_message = method_messages.get(method, "Operation completed successfully")

        # Customize message based on path patterns
        if "/auth" in path:
            if method == "POST" and "login" in path:
                return "Authentication successful"
            elif method == "POST" and "register" in path:
                return "User registration successful"
            elif method == "POST" and "logout" in path:
                return "Logout successful"

        if "/products" in path or "/productos" in path:
            if method == "GET":
                return "Products retrieved successfully"
            elif method == "POST":
                return "Product created successfully"

        if "/orders" in path:
            if method == "GET":
                return "Orders retrieved successfully"
            elif method == "POST":
                return "Order created successfully"

        if "/commissions" in path or "/comisiones" in path:
            if method == "GET":
                return "Commission data retrieved successfully"

        return base_message


class ResponseTimingMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware for response timing without standardization.
    Use this when you only need timing headers without response modification.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses with standardized format.
    """

    def __init__(self, app, log_level: str = "INFO"):
        super().__init__(app)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = logging.getLogger("request_logger")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = getattr(request.state, 'request_id', f"req_{str(uuid.uuid4())[:8]}")
        start_time = time.time()

        # Log incoming request
        self.logger.log(
            self.log_level,
            f"Request started - ID: {request_id} - Method: {request.method} - URL: {request.url}"
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log response
            self.logger.log(
                self.log_level,
                f"Request completed - ID: {request_id} - Status: {response.status_code} - Time: {process_time:.4f}s"
            )

            return response

        except Exception as e:
            process_time = time.time() - start_time
            self.logger.error(
                f"Request failed - ID: {request_id} - Error: {str(e)} - Time: {process_time:.4f}s"
            )
            raise