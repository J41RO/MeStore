"""
Base Pydantic schemas with consistent ID validation for MeStore API.

This module provides base schemas that ensure consistent ID handling
across all API endpoints. All schemas that involve IDs should inherit
from these base classes to maintain consistency.

Key Features:
- Consistent UUID string validation
- Standardized response formats
- Common field patterns
- Type safety for all ID fields
"""

from typing import Optional, Any, Dict, List, Union, TypeVar, Generic
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

# Generic type variable for parametrized responses
T = TypeVar('T')

from app.core.id_validation import IDValidationMixin


class BaseSchema(BaseModel):
    """
    Base schema for all Pydantic models in the API.

    Provides common configuration and patterns that should be
    consistent across all schemas.
    """

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class BaseIDSchema(BaseSchema, IDValidationMixin):
    """
    Base schema for models that include ID fields.

    Automatically includes ID validation and provides
    consistent patterns for ID-based schemas.
    """

    id: str = Field(
        ...,
        description="UUID identifier",
        min_length=36,
        max_length=36,
        json_schema_extra={
            "example": "550e8400-e29b-41d4-a716-446655440000"
        }
    )


class BaseCreateSchema(BaseSchema):
    """
    Base schema for create operations.

    Excludes ID fields since they are auto-generated.
    """
    pass


class BaseUpdateSchema(BaseSchema):
    """
    Base schema for update operations.

    All fields are optional to support partial updates.
    """
    pass


class BaseResponseSchema(BaseIDSchema):
    """
    Base schema for API responses that include entity data.

    Includes standard metadata fields like timestamps.
    """

    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    deleted_at: Optional[datetime] = Field(
        None,
        description="Soft delete timestamp"
    )


class PaginationSchema(BaseSchema):
    """
    Standard pagination response schema.
    """

    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=1000, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseSchema):
    """
    Generic paginated response wrapper.
    """

    items: List[Any] = Field(..., description="List of items")
    pagination: PaginationSchema = Field(..., description="Pagination metadata")


class APIResponse(BaseSchema, Generic[T]):
    """
    Standard API response wrapper for consistent response format.
    """

    success: bool = Field(..., description="Operation success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="List of errors if any")


class IDListSchema(BaseSchema):
    """
    Schema for operations that involve multiple IDs.
    """

    ids: List[str] = Field(
        ...,
        description="List of UUID identifiers",
        min_items=1,
        max_items=100
    )


class BulkOperationResponse(BaseSchema):
    """
    Response schema for bulk operations.
    """

    success_count: int = Field(..., ge=0, description="Number of successful operations")
    failure_count: int = Field(..., ge=0, description="Number of failed operations")
    total_count: int = Field(..., ge=0, description="Total number of operations")
    success_ids: List[str] = Field(..., description="IDs of successful operations")
    failure_ids: List[str] = Field(..., description="IDs of failed operations")
    errors: Optional[Dict[str, str]] = Field(None, description="Error details by ID")


class SearchSchema(BaseSchema):
    """
    Base schema for search operations.
    """

    query: Optional[str] = Field(None, description="Search query string")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    sort_by: Optional[str] = Field("created_at", description="Sort field")
    sort_order: Optional[str] = Field(
        "desc",
        pattern="^(asc|desc)$",
        description="Sort order"
    )
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class TimestampMixin(BaseModel):
    """
    Mixin for schemas that include timestamp fields.
    """

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SoftDeleteMixin(BaseModel):
    """
    Mixin for schemas that support soft delete.
    """

    deleted_at: Optional[datetime] = Field(None, description="Soft delete timestamp")
    is_deleted: bool = Field(False, description="Soft delete status")


class UserContextMixin(BaseModel):
    """
    Mixin for schemas that include user context.
    """

    created_by_id: Optional[str] = Field(None, description="ID of user who created this")
    updated_by_id: Optional[str] = Field(None, description="ID of user who last updated this")


class ValidationErrorDetail(BaseSchema):
    """
    Schema for detailed validation error information.
    """

    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Value that failed validation")


class ValidationErrorResponse(BaseSchema):
    """
    Response schema for validation errors.
    """

    success: bool = Field(False, description="Always false for validation errors")
    message: str = Field(..., description="General error message")
    errors: List[ValidationErrorDetail] = Field(..., description="Detailed validation errors")


# Additional response schemas for standardized APIs
class APIError(BaseSchema):
    """Standardized error response format."""

    success: bool = Field(False, description="Always false for error responses")
    error: Dict[str, Any] = Field(..., description="Error details")
    message: str = Field(..., description="Human-readable error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


# Type variable already defined above


class PaginationMetadata(BaseSchema):
    """Pagination metadata for responses."""

    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")


class PaginatedResponseV2(BaseSchema, Generic[T]):
    """Enhanced paginated response wrapper."""

    success: bool = Field(..., description="Operation success status")
    data: List[T] = Field(..., description="List of data items")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Applied filters")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


# Export all base schemas
__all__ = [
    "BaseSchema",
    "BaseIDSchema",
    "BaseCreateSchema",
    "BaseUpdateSchema",
    "BaseResponseSchema",
    "PaginationSchema",
    "PaginatedResponse",
    "PaginatedResponseV2",
    "PaginationMetadata",
    "APIResponse",
    "APIError",
    "IDListSchema",
    "BulkOperationResponse",
    "SearchSchema",
    "TimestampMixin",
    "SoftDeleteMixin",
    "UserContextMixin",
    "ValidationErrorDetail",
    "ValidationErrorResponse"
]