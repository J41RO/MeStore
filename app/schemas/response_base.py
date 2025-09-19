# ~/app/schemas/response_base.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Base Response Schemas for FastAPI Standardization
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Base response schemas for FastAPI standardization.

This module provides:
- SuccessResponse: Standard success response with data payload
- ErrorResponse: Standard error response with error details
- PaginatedResponse: Paginated response for list endpoints
- ValidationErrorResponse: Detailed validation error response
- StandardResponse: Base response class for all API responses
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field, ConfigDict

# Generic type for data payload
T = TypeVar('T')

class PaginationInfo(BaseModel):
    """Pagination information for list responses."""

    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, le=100, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "size": 20,
                "total": 150,
                "pages": 8,
                "has_next": True,
                "has_prev": False
            }
        }
    )


class ErrorDetail(BaseModel):
    """Detailed error information."""

    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(None, description="Type of error")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "error_type": "validation_error"
            }
        }
    )


class StandardResponse(BaseModel, Generic[T]):
    """Base response class for all API responses."""

    status: str = Field(..., description="Response status: success or error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    message: Optional[str] = Field(None, description="Optional response message")
    version: str = Field(default="1.0.0", description="API version")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() + "Z"
        }
    )


class SuccessResponse(StandardResponse[T]):
    """Standard success response with data payload."""

    status: str = Field(default="success", description="Success status")
    data: T = Field(..., description="Response data payload")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "data": {"id": 1, "name": "Example"},
                "message": "Operation completed successfully",
                "timestamp": "2025-09-17T12:00:00Z",
                "version": "1.0.0"
            }
        }
    )


class ErrorResponse(StandardResponse[None]):
    """Standard error response with error details."""

    status: str = Field(default="error", description="Error status")
    error_code: str = Field(..., description="Specific error code for client handling")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "error",
                "error_code": "VALIDATION_ERROR",
                "error_message": "Invalid input data provided",
                "details": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "error_type": "validation_error"
                    }
                ],
                "message": "Request validation failed",
                "timestamp": "2025-09-17T12:00:00Z",
                "version": "1.0.0",
                "request_id": "req_12345"
            }
        }
    )


class ValidationErrorResponse(ErrorResponse):
    """Specialized error response for validation errors."""

    error_code: str = Field(default="VALIDATION_ERROR", description="Validation error code")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "error",
                "error_code": "VALIDATION_ERROR",
                "error_message": "Input validation failed",
                "details": [
                    {
                        "field": "email",
                        "message": "field required",
                        "error_type": "missing"
                    },
                    {
                        "field": "password",
                        "message": "ensure this value has at least 8 characters",
                        "error_type": "value_error"
                    }
                ],
                "timestamp": "2025-09-17T12:00:00Z",
                "version": "1.0.0"
            }
        }
    )


class PaginatedResponse(StandardResponse[List[T]]):
    """Paginated response for list endpoints."""

    status: str = Field(default="success", description="Success status")
    data: List[T] = Field(..., description="List of items for current page")
    pagination: PaginationInfo = Field(..., description="Pagination metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "data": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ],
                "pagination": {
                    "page": 1,
                    "size": 20,
                    "total": 150,
                    "pages": 8,
                    "has_next": True,
                    "has_prev": False
                },
                "message": "Items retrieved successfully",
                "timestamp": "2025-09-17T12:00:00Z",
                "version": "1.0.0"
            }
        }
    )


class HealthResponse(StandardResponse[Dict[str, Any]]):
    """Health check response."""

    status: str = Field(default="success", description="Health status")
    data: Dict[str, Any] = Field(..., description="Health check data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "data": {
                    "service": "MeStore API",
                    "environment": "development",
                    "database": "healthy",
                    "redis": "healthy",
                    "uptime": "2h 30m 15s"
                },
                "message": "All systems operational",
                "timestamp": "2025-09-17T12:00:00Z",
                "version": "1.0.0"
            }
        }
    )


class MessageResponse(StandardResponse[None]):
    """Simple message response without data payload."""

    status: str = Field(default="success", description="Operation status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "timestamp": "2025-09-17T12:00:00Z",
                "version": "1.0.0"
            }
        }
    )


# Common HTTP status codes for error responses
class ErrorCodes:
    """Standard error codes for consistent error handling."""

    # 4xx Client Errors
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"

    # 5xx Server Errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BAD_GATEWAY = "BAD_GATEWAY"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"

    # Business Logic Errors
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    PRODUCT_NOT_AVAILABLE = "PRODUCT_NOT_AVAILABLE"
    ORDER_NOT_FOUND = "ORDER_NOT_FOUND"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    COMMISSION_CALCULATION_ERROR = "COMMISSION_CALCULATION_ERROR"
    VENDOR_NOT_AUTHORIZED = "VENDOR_NOT_AUTHORIZED"
    BUYER_NOT_VERIFIED = "BUYER_NOT_VERIFIED"


# Response utilities for creating standardized responses
def create_success_response(
    data: T,
    message: Optional[str] = None,
    status_code: int = 200
) -> SuccessResponse[T]:
    """Create a standardized success response."""
    return SuccessResponse(
        data=data,
        message=message or "Operation completed successfully"
    )


def create_error_response(
    error_code: str,
    error_message: str,
    details: Optional[List[ErrorDetail]] = None,
    message: Optional[str] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create a standardized error response."""
    return ErrorResponse(
        error_code=error_code,
        error_message=error_message,
        details=details or [],
        message=message or "Operation failed",
        request_id=request_id
    )


def create_paginated_response(
    data: List[T],
    page: int,
    size: int,
    total: int,
    message: Optional[str] = None
) -> PaginatedResponse[T]:
    """Create a standardized paginated response."""
    pages = (total + size - 1) // size  # Ceiling division

    pagination = PaginationInfo(
        page=page,
        size=size,
        total=total,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )

    return PaginatedResponse(
        data=data,
        pagination=pagination,
        message=message or f"Retrieved {len(data)} items"
    )


def create_validation_error_response(
    validation_errors: List[ErrorDetail],
    message: Optional[str] = None
) -> ValidationErrorResponse:
    """Create a standardized validation error response."""
    return ValidationErrorResponse(
        error_message=message or "Input validation failed",
        details=validation_errors,
        message="Request validation failed"
    )