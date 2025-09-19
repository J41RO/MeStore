# ~/app/utils/response_utils.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Response Utilities for FastAPI Standardization
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Response utilities for standardized FastAPI responses.

This module provides:
- Utility functions for creating standardized responses
- Response decorators for automatic formatting
- Common response patterns for typical CRUD operations
- Type-safe response creation with proper schemas
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.schemas.response_base import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    MessageResponse,
    ErrorCodes,
    ErrorDetail,
    create_success_response,
    create_error_response,
    create_paginated_response,
    create_validation_error_response
)

T = TypeVar('T', bound=BaseModel)


class ResponseUtils:
    """Utility class for creating standardized API responses."""

    @staticmethod
    def success(
        data: Any,
        message: Optional[str] = None,
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        Create a success response with data.

        Args:
            data: Response data payload
            message: Optional success message
            status_code: HTTP status code (default: 200)

        Returns:
            JSONResponse with standardized success format
        """
        response = create_success_response(data=data, message=message)
        return JSONResponse(
            content=response.model_dump(mode='json'),
            status_code=status_code
        )

    @staticmethod
    def created(
        data: Any,
        message: Optional[str] = None
    ) -> JSONResponse:
        """
        Create a 201 Created response.

        Args:
            data: Created resource data
            message: Optional creation message

        Returns:
            JSONResponse with 201 status
        """
        return ResponseUtils.success(
            data=data,
            message=message or "Resource created successfully",
            status_code=status.HTTP_201_CREATED
        )

    @staticmethod
    def updated(
        data: Any,
        message: Optional[str] = None
    ) -> JSONResponse:
        """
        Create a response for updated resources.

        Args:
            data: Updated resource data
            message: Optional update message

        Returns:
            JSONResponse with success format
        """
        return ResponseUtils.success(
            data=data,
            message=message or "Resource updated successfully"
        )

    @staticmethod
    def deleted(message: Optional[str] = None) -> JSONResponse:
        """
        Create a response for deleted resources.

        Args:
            message: Optional deletion message

        Returns:
            JSONResponse with success format and no data
        """
        response = MessageResponse(
            message=message or "Resource deleted successfully"
        )
        return JSONResponse(
            content=response.model_dump(mode='json'),
            status_code=status.HTTP_200_OK
        )

    @staticmethod
    def paginated(
        items: List[Any],
        page: int,
        size: int,
        total: int,
        message: Optional[str] = None
    ) -> JSONResponse:
        """
        Create a paginated response.

        Args:
            items: List of items for current page
            page: Current page number
            size: Items per page
            total: Total number of items
            message: Optional message

        Returns:
            JSONResponse with paginated format
        """
        response = create_paginated_response(
            data=items,
            page=page,
            size=size,
            total=total,
            message=message
        )
        return JSONResponse(
            content=response.model_dump(mode='json'),
            status_code=status.HTTP_200_OK
        )

    @staticmethod
    def error(
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[List[ErrorDetail]] = None
    ) -> JSONResponse:
        """
        Create an error response.

        Args:
            error_code: Standardized error code
            message: Error message
            status_code: HTTP status code
            details: Optional error details

        Returns:
            JSONResponse with error format
        """
        response = create_error_response(
            error_code=error_code,
            error_message=message,
            details=details
        )
        return JSONResponse(
            content=response.model_dump(mode='json'),
            status_code=status_code
        )

    @staticmethod
    def not_found(
        resource_type: str = "Resource",
        resource_id: Optional[str] = None
    ) -> JSONResponse:
        """
        Create a 404 Not Found response.

        Args:
            resource_type: Type of resource not found
            resource_id: Optional resource identifier

        Returns:
            JSONResponse with 404 status
        """
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found"

        return ResponseUtils.error(
            error_code=ErrorCodes.NOT_FOUND,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def unauthorized(message: str = "Authentication required") -> JSONResponse:
        """
        Create a 401 Unauthorized response.

        Args:
            message: Authentication error message

        Returns:
            JSONResponse with 401 status
        """
        return ResponseUtils.error(
            error_code=ErrorCodes.UNAUTHORIZED,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def forbidden(message: str = "Access denied") -> JSONResponse:
        """
        Create a 403 Forbidden response.

        Args:
            message: Authorization error message

        Returns:
            JSONResponse with 403 status
        """
        return ResponseUtils.error(
            error_code=ErrorCodes.FORBIDDEN,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def validation_error(
        validation_errors: List[ErrorDetail],
        message: str = "Input validation failed"
    ) -> JSONResponse:
        """
        Create a 422 Validation Error response.

        Args:
            validation_errors: List of validation error details
            message: Validation error message

        Returns:
            JSONResponse with 422 status
        """
        response = create_validation_error_response(
            validation_errors=validation_errors,
            message=message
        )
        return JSONResponse(
            content=response.model_dump(mode='json'),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    @staticmethod
    def conflict(
        message: str = "Resource conflict",
        error_code: str = ErrorCodes.CONFLICT
    ) -> JSONResponse:
        """
        Create a 409 Conflict response.

        Args:
            message: Conflict error message
            error_code: Specific error code

        Returns:
            JSONResponse with 409 status
        """
        return ResponseUtils.error(
            error_code=error_code,
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )

    @staticmethod
    def rate_limited(
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ) -> JSONResponse:
        """
        Create a 429 Rate Limited response.

        Args:
            message: Rate limit error message
            retry_after: Optional retry after seconds

        Returns:
            JSONResponse with 429 status
        """
        response = ResponseUtils.error(
            error_code=ErrorCodes.TOO_MANY_REQUESTS,
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

        if retry_after:
            response.headers["Retry-After"] = str(retry_after)

        return response

    @staticmethod
    def internal_error(
        message: str = "Internal server error",
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """
        Create a 500 Internal Server Error response.

        Args:
            message: Error message
            request_id: Optional request ID for tracking

        Returns:
            JSONResponse with 500 status
        """
        response = create_error_response(
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            error_message=message,
            request_id=request_id
        )
        return JSONResponse(
            content=response.model_dump(mode='json'),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Convenience functions for common operations
def success_response(data: Any, message: Optional[str] = None) -> JSONResponse:
    """Create a success response. Alias for ResponseUtils.success."""
    return ResponseUtils.success(data=data, message=message)


def error_response(
    error_code: str,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """Create an error response. Alias for ResponseUtils.error."""
    return ResponseUtils.error(
        error_code=error_code,
        message=message,
        status_code=status_code
    )


def paginated_response(
    items: List[Any],
    page: int,
    size: int,
    total: int,
    message: Optional[str] = None
) -> JSONResponse:
    """Create a paginated response. Alias for ResponseUtils.paginated."""
    return ResponseUtils.paginated(
        items=items,
        page=page,
        size=size,
        total=total,
        message=message
    )


# Decorator for automatic response formatting
def standardize_response(
    success_message: Optional[str] = None,
    error_message: Optional[str] = None
):
    """
    Decorator to automatically standardize endpoint responses.

    Args:
        success_message: Default success message
        error_message: Default error message

    Returns:
        Decorated function with standardized responses
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                # If result is already a Response, return as-is
                if isinstance(result, JSONResponse):
                    return result

                # Standardize the result
                return ResponseUtils.success(
                    data=result,
                    message=success_message
                )

            except HTTPException as e:
                return ResponseUtils.error(
                    error_code=f"HTTP_{e.status_code}",
                    message=str(e.detail),
                    status_code=e.status_code
                )
            except Exception as e:
                return ResponseUtils.internal_error(
                    message=error_message or "An unexpected error occurred"
                )

        return wrapper
    return decorator


# Business domain specific response helpers
class AuthResponseUtils:
    """Specialized response utilities for authentication endpoints."""

    @staticmethod
    def login_success(user_data: dict, token: str) -> JSONResponse:
        """Create login success response."""
        response_data = {
            "user": user_data,
            "access_token": token,
            "token_type": "bearer"
        }
        return ResponseUtils.success(
            data=response_data,
            message="Authentication successful"
        )

    @staticmethod
    def logout_success() -> JSONResponse:
        """Create logout success response."""
        return ResponseUtils.deleted(message="Logout successful")

    @staticmethod
    def registration_success(user_data: dict) -> JSONResponse:
        """Create registration success response."""
        return ResponseUtils.created(
            data=user_data,
            message="User registration successful"
        )


class ProductResponseUtils:
    """Specialized response utilities for product endpoints."""

    @staticmethod
    def product_created(product_data: dict) -> JSONResponse:
        """Create product creation response."""
        return ResponseUtils.created(
            data=product_data,
            message="Product created successfully"
        )

    @staticmethod
    def product_updated(product_data: dict) -> JSONResponse:
        """Create product update response."""
        return ResponseUtils.updated(
            data=product_data,
            message="Product updated successfully"
        )

    @staticmethod
    def product_not_found(product_id: str) -> JSONResponse:
        """Create product not found response."""
        return ResponseUtils.not_found(
            resource_type="Product",
            resource_id=product_id
        )


class OrderResponseUtils:
    """Specialized response utilities for order endpoints."""

    @staticmethod
    def order_created(order_data: dict) -> JSONResponse:
        """Create order creation response."""
        return ResponseUtils.created(
            data=order_data,
            message="Order created successfully"
        )

    @staticmethod
    def order_status_updated(order_data: dict) -> JSONResponse:
        """Create order status update response."""
        return ResponseUtils.updated(
            data=order_data,
            message="Order status updated successfully"
        )

    @staticmethod
    def payment_failed() -> JSONResponse:
        """Create payment failure response."""
        return ResponseUtils.error(
            error_code=ErrorCodes.PAYMENT_FAILED,
            message="Payment processing failed",
            status_code=status.HTTP_402_PAYMENT_REQUIRED
        )