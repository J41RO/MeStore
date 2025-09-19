"""
Standardized Response Utilities for MeStore API
==============================================

FastAPI response utilities for consistent API responses,
error handling, and HTTP exception management.

Author: API Architect AI
Date: 2025-09-17
Purpose: Centralized response management for API standardization
"""

import uuid
from typing import TypeVar, Optional, Dict, Any, List
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.schemas.common import (
    APIResponse,
    PaginatedResponse,
    APIError,
    APIValidationError,
    ValidationError,
    ErrorCode,
    SuccessMessage,
    create_success_response,
    create_paginated_response,
    create_error_response,
    create_validation_error_response
)

# Type variable for generic responses
T = TypeVar('T')


class StandardHTTPException(HTTPException):
    """Enhanced HTTPException with standardized error response"""

    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.error_code = error_code
        self.error_details = details

        # Create standardized error response
        error_response = create_error_response(
            error_code=error_code,
            message=message,
            details=details
        )

        super().__init__(
            status_code=status_code,
            detail=error_response.model_dump(),
            headers=headers
        )


class ResponseHelper:
    """Helper class for creating standardized API responses"""

    @staticmethod
    def success(
        data: T,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """Create successful response with data"""
        response_data = create_success_response(
            data=data,
            message=message,
            metadata=metadata
        )
        return JSONResponse(
            content=jsonable_encoder(response_data),
            status_code=status_code
        )

    @staticmethod
    def created(
        data: T,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Create response for resource creation"""
        response_data = create_success_response(
            data=data,
            message=message or "Resource created successfully",
            metadata=metadata
        )
        return JSONResponse(
            content=jsonable_encoder(response_data),
            status_code=status.HTTP_201_CREATED
        )

    @staticmethod
    def updated(
        data: T,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Create response for resource update"""
        response_data = create_success_response(
            data=data,
            message=message or "Resource updated successfully",
            metadata=metadata
        )
        return JSONResponse(
            content=jsonable_encoder(response_data),
            status_code=status.HTTP_200_OK
        )

    @staticmethod
    def deleted(
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Create response for resource deletion"""
        response_data = SuccessMessage(
            message=message or "Resource deleted successfully"
        )
        return JSONResponse(
            content=jsonable_encoder(response_data),
            status_code=status.HTTP_200_OK
        )

    @staticmethod
    def paginated(
        data: List[T],
        page: int,
        size: int,
        total: int,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Create paginated response"""
        response_data = create_paginated_response(
            data=data,
            page=page,
            size=size,
            total=total,
            message=message,
            metadata=metadata
        )
        return JSONResponse(
            content=jsonable_encoder(response_data),
            status_code=status.HTTP_200_OK
        )


class ErrorHelper:
    """Helper class for creating standardized error responses"""

    @staticmethod
    def bad_request(
        message: str = "Bad request",
        details: Optional[Dict[str, Any]] = None
    ) -> StandardHTTPException:
        """Create 400 Bad Request error"""
        return StandardHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INVALID_INPUT,
            message=message,
            details=details
        )

    @staticmethod
    def unauthorized(
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None
    ) -> StandardHTTPException:
        """Create 401 Unauthorized error"""
        return StandardHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.UNAUTHORIZED,
            message=message,
            details=details,
            headers={"WWW-Authenticate": "Bearer"}
        )

    @staticmethod
    def forbidden(
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None
    ) -> StandardHTTPException:
        """Create 403 Forbidden error"""
        return StandardHTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCode.FORBIDDEN,
            message=message,
            details=details
        )

    @staticmethod
    def not_found(
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> StandardHTTPException:
        """Create 404 Not Found error"""
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"

        return StandardHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.NOT_FOUND,
            message=message,
            details=details
        )

    @staticmethod
    def conflict(
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ) -> StandardHTTPException:
        """Create 409 Conflict error"""
        return StandardHTTPException(
            status_code=status.HTTP_409_CONFLICT,
            error_code=ErrorCode.RESOURCE_CONFLICT,
            message=message,
            details=details
        )

    @staticmethod
    def validation_error(
        message: str = "Validation failed",
        validation_errors: Optional[List[ValidationError]] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> StandardHTTPException:
        """Create 422 Validation Error"""
        if validation_errors:
            error_response = create_validation_error_response(
                message=message,
                validation_errors=validation_errors
            )
        else:
            error_response = create_error_response(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=message,
                details=details
            )

        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_response.model_dump()
        )

    @staticmethod
    def rate_limit(
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ) -> StandardHTTPException:
        """Create 429 Rate Limit error"""
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)

        return StandardHTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
            headers=headers
        )

    @staticmethod
    def internal_server_error(
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None
    ) -> StandardHTTPException:
        """Create 500 Internal Server Error"""
        return StandardHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=message,
            details=details
        )

    @staticmethod
    def service_unavailable(
        message: str = "Service temporarily unavailable",
        details: Optional[Dict[str, Any]] = None
    ) -> StandardHTTPException:
        """Create 503 Service Unavailable error"""
        return StandardHTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            message=message,
            details=details
        )


# Business domain specific error helpers
class AuthErrorHelper:
    """Authentication specific error helpers"""

    @staticmethod
    def invalid_credentials() -> StandardHTTPException:
        """Invalid email or password"""
        return ErrorHelper.unauthorized("Invalid email or password")

    @staticmethod
    def token_expired() -> StandardHTTPException:
        """JWT token expired"""
        return StandardHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.TOKEN_EXPIRED,
            message="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )

    @staticmethod
    def account_disabled() -> StandardHTTPException:
        """User account is disabled"""
        return ErrorHelper.forbidden("Account is disabled")


class ProductErrorHelper:
    """Product management specific error helpers"""

    @staticmethod
    def product_not_found(product_id: str) -> StandardHTTPException:
        """Product not found"""
        return ErrorHelper.not_found("Product", product_id)

    @staticmethod
    def insufficient_inventory(product_id: str, requested: int, available: int) -> StandardHTTPException:
        """Insufficient inventory"""
        return StandardHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INVENTORY_INSUFFICIENT,
            message=f"Insufficient inventory for product {product_id}",
            details={
                "product_id": product_id,
                "requested_quantity": requested,
                "available_quantity": available
            }
        )

    @staticmethod
    def product_not_available(product_id: str) -> StandardHTTPException:
        """Product not available for purchase"""
        return StandardHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.PRODUCT_NOT_AVAILABLE,
            message=f"Product {product_id} is not available for purchase",
            details={"product_id": product_id}
        )


class VendorErrorHelper:
    """Vendor management specific error helpers"""

    @staticmethod
    def vendor_not_active(vendor_id: str) -> StandardHTTPException:
        """Vendor is not active"""
        return StandardHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.VENDOR_NOT_ACTIVE,
            message=f"Vendor {vendor_id} is not active",
            details={"vendor_id": vendor_id}
        )

    @staticmethod
    def vendor_not_found(vendor_id: str) -> StandardHTTPException:
        """Vendor not found"""
        return ErrorHelper.not_found("Vendor", vendor_id)


class PaymentErrorHelper:
    """Payment processing specific error helpers"""

    @staticmethod
    def payment_failed(transaction_id: str, reason: str) -> StandardHTTPException:
        """Payment processing failed"""
        return StandardHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.PAYMENT_FAILED,
            message=f"Payment failed: {reason}",
            details={"transaction_id": transaction_id, "reason": reason}
        )

    @staticmethod
    def insufficient_funds() -> StandardHTTPException:
        """Insufficient funds for payment"""
        return StandardHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INSUFFICIENT_FUNDS,
            message="Insufficient funds for this transaction"
        )


def generate_request_id() -> str:
    """Generate unique request ID for tracing"""
    return str(uuid.uuid4())


def add_request_context(request: Request, error: APIError) -> APIError:
    """Add request context to error response"""
    error.path = str(request.url.path)
    error.request_id = generate_request_id()
    return error


# Export all public components
__all__ = [
    "StandardHTTPException",
    "ResponseHelper",
    "ErrorHelper",
    "AuthErrorHelper",
    "ProductErrorHelper",
    "VendorErrorHelper",
    "PaymentErrorHelper",
    "generate_request_id",
    "add_request_context",
]