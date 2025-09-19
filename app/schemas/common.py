"""
Common API Response Schemas for MeStore
=====================================

Standardized response wrappers, error handling, and pagination schemas
for consistent API responses across all endpoints.

Author: API Architect AI
Date: 2025-09-17
Purpose: API standardization and consistency implementation
"""

from typing import TypeVar, Generic, Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


# Type variable for generic response data
T = TypeVar('T')


class APIStatus(str, Enum):
    """Standard API status values"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class ErrorCode(str, Enum):
    """Standard error codes for consistent error handling"""
    # Authentication Errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

    # Resource Errors
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"

    # Validation Errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"

    # Business Logic Errors
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"

    # System Errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Payment Errors
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_PROCESSING_ERROR = "PAYMENT_PROCESSING_ERROR"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"

    # Vendor/Product Errors
    PRODUCT_NOT_AVAILABLE = "PRODUCT_NOT_AVAILABLE"
    VENDOR_NOT_ACTIVE = "VENDOR_NOT_ACTIVE"
    INVENTORY_INSUFFICIENT = "INVENTORY_INSUFFICIENT"


class PaginationMeta(BaseModel):
    """Standard pagination metadata"""
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, le=1000, description="Number of items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")

    @classmethod
    def create(cls, page: int, size: int, total: int) -> "PaginationMeta":
        """Create pagination metadata from basic parameters"""
        total_pages = (total + size - 1) // size if total > 0 else 0
        return cls(
            page=page,
            size=size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper for all successful operations

    Example:
        APIResponse[ProductRead](
            data=product,
            message="Product retrieved successfully"
        )
    """
    status: APIStatus = APIStatus.SUCCESS
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Human-readable message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response for list operations

    Example:
        PaginatedResponse[ProductRead](
            data=products,
            pagination=PaginationMeta.create(1, 20, 100),
            message="Products retrieved successfully"
        )
    """
    status: APIStatus = APIStatus.SUCCESS
    data: List[T] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    message: Optional[str] = Field(None, description="Human-readable message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class APIError(BaseModel):
    """
    Standard API error response for all error conditions

    Example:
        APIError(
            error_code=ErrorCode.NOT_FOUND,
            message="Product not found",
            details={"product_id": "123"}
        )
    """
    status: APIStatus = APIStatus.ERROR
    error_code: ErrorCode = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    path: Optional[str] = Field(None, description="API path where error occurred")
    request_id: Optional[str] = Field(None, description="Request ID for debugging")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationError(BaseModel):
    """Standard validation error details"""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value")
    constraint: Optional[str] = Field(None, description="Validation constraint that failed")


class APIValidationError(APIError):
    """
    Specialized error response for validation errors

    Example:
        APIValidationError(
            message="Validation failed",
            validation_errors=[
                ValidationError(field="email", message="Invalid email format")
            ]
        )
    """
    error_code: ErrorCode = ErrorCode.VALIDATION_ERROR
    validation_errors: List[ValidationError] = Field(..., description="List of validation errors")


class SuccessMessage(BaseModel):
    """Simple success message response"""
    status: APIStatus = APIStatus.SUCCESS
    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthCheckResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment (dev/staging/prod)")
    services: Dict[str, str] = Field(..., description="Dependent services status")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Helper functions for creating responses
def create_success_response(
    data: T,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> APIResponse[T]:
    """Helper function to create success response"""
    return APIResponse(
        data=data,
        message=message,
        metadata=metadata
    )


def create_paginated_response(
    data: List[T],
    page: int,
    size: int,
    total: int,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> PaginatedResponse[T]:
    """Helper function to create paginated response"""
    return PaginatedResponse(
        data=data,
        pagination=PaginationMeta.create(page, size, total),
        message=message,
        metadata=metadata
    )


def create_error_response(
    error_code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None,
    request_id: Optional[str] = None
) -> APIError:
    """Helper function to create error response"""
    return APIError(
        error_code=error_code,
        message=message,
        details=details,
        path=path,
        request_id=request_id
    )


def create_validation_error_response(
    message: str,
    validation_errors: List[ValidationError],
    path: Optional[str] = None,
    request_id: Optional[str] = None
) -> APIValidationError:
    """Helper function to create validation error response"""
    return APIValidationError(
        message=message,
        validation_errors=validation_errors,
        path=path,
        request_id=request_id
    )


# Response type aliases for common patterns
ProductListResponse = PaginatedResponse[Any]  # Will be properly typed when used
OrderListResponse = PaginatedResponse[Any]
CommissionListResponse = PaginatedResponse[Any]
UserListResponse = PaginatedResponse[Any]

# Export all public components
__all__ = [
    "APIStatus",
    "ErrorCode",
    "PaginationMeta",
    "APIResponse",
    "PaginatedResponse",
    "APIError",
    "ValidationError",
    "APIValidationError",
    "SuccessMessage",
    "HealthCheckResponse",
    "create_success_response",
    "create_paginated_response",
    "create_error_response",
    "create_validation_error_response",
]