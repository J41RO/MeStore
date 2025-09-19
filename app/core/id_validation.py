"""
FastAPI ID Validation Utilities for MeStore

This module provides comprehensive ID validation utilities for consistent handling
of UUID-based IDs across all FastAPI endpoints. Ensures type safety, validation,
and error handling for all ID parameters.

Key Features:
- UUID string validation with comprehensive error handling
- Path parameter validation dependencies
- Pydantic validators for schema consistency
- Custom exceptions for ID validation errors
- Performance-optimized validation functions
"""

import uuid
from typing import Union, Optional, Any
from uuid import UUID
from fastapi import HTTPException, status, Path
from pydantic import field_validator, BaseModel
import re


class IDValidationError(Exception):
    """Custom exception for ID validation errors."""

    def __init__(self, message: str, field_name: str = "id", status_code: int = 400):
        self.message = message
        self.field_name = field_name
        self.status_code = status_code
        super().__init__(self.message)


class IDValidator:
    """
    Comprehensive ID validation utilities for FastAPI endpoints.

    Provides consistent validation for:
    - UUID strings (primary format)
    - Path parameters
    - Request/response schemas
    - Database queries
    """

    @staticmethod
    def is_valid_uuid_string(value: Any) -> bool:
        """
        Check if a value is a valid UUID string.

        Args:
            value: Value to validate

        Returns:
            bool: True if valid UUID string, False otherwise
        """
        if not value:
            return False

        try:
            # Convert to string if not already
            str_value = str(value).strip()

            # Check basic format (36 characters with hyphens)
            if len(str_value) != 36:
                return False

            # Validate UUID format
            uuid.UUID(str_value)
            return True
        except (ValueError, TypeError, AttributeError):
            return False

    @staticmethod
    def validate_uuid_string(value: Any, field_name: str = "id") -> str:
        """
        Validate and normalize UUID string with detailed error handling.

        Args:
            value: Value to validate
            field_name: Name of the field being validated

        Returns:
            str: Validated UUID string

        Raises:
            IDValidationError: If validation fails
        """
        if not value:
            raise IDValidationError(
                f"{field_name} is required and cannot be empty",
                field_name=field_name,
                status_code=400
            )

        try:
            # Convert to string and normalize
            str_value = str(value).strip().lower()

            # Validate length
            if len(str_value) != 36:
                raise IDValidationError(
                    f"Invalid {field_name} format: must be 36 characters (UUID format)",
                    field_name=field_name,
                    status_code=400
                )

            # Validate UUID format and create UUID object to ensure validity
            uuid_obj = uuid.UUID(str_value)

            # Return normalized string format
            return str(uuid_obj)

        except ValueError as e:
            raise IDValidationError(
                f"Invalid {field_name} format: {str(e)}",
                field_name=field_name,
                status_code=400
            )
        except Exception as e:
            raise IDValidationError(
                f"Unexpected error validating {field_name}: {str(e)}",
                field_name=field_name,
                status_code=500
            )

    @staticmethod
    def validate_optional_uuid_string(value: Optional[Any], field_name: str = "id") -> Optional[str]:
        """
        Validate optional UUID string (allows None/empty values).

        Args:
            value: Value to validate (can be None)
            field_name: Name of the field being validated

        Returns:
            Optional[str]: Validated UUID string or None

        Raises:
            IDValidationError: If validation fails for non-empty values
        """
        if not value:
            return None

        return IDValidator.validate_uuid_string(value, field_name)

    @staticmethod
    def create_path_validator(field_name: str = "id", description: str = None) -> Any:
        """
        Create a FastAPI Path validator for UUID parameters.

        Args:
            field_name: Name of the field for error messages
            description: Description for OpenAPI documentation

        Returns:
            FastAPI Path dependency with validation
        """
        if description is None:
            description = f"UUID identifier for {field_name}"

        def validate_path_uuid(
            value: str = Path(
                ...,
                description=description,
                min_length=36,
                max_length=36,
                regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
            )
        ) -> str:
            try:
                return IDValidator.validate_uuid_string(value, field_name)
            except IDValidationError as e:
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.message
                )

        return validate_path_uuid


# FastAPI Dependencies for common ID validations
def validate_user_id(
    user_id: str = Path(
        ...,
        description="User UUID identifier",
        min_length=36,
        max_length=36,
        regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    )
) -> str:
    """Validate user ID path parameter."""
    try:
        return IDValidator.validate_uuid_string(user_id, "user_id")
    except IDValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


def validate_product_id(
    product_id: str = Path(
        ...,
        description="Product UUID identifier",
        min_length=36,
        max_length=36,
        regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    )
) -> str:
    """Validate product ID path parameter."""
    try:
        return IDValidator.validate_uuid_string(product_id, "product_id")
    except IDValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


def validate_order_id(
    order_id: str = Path(
        ...,
        description="Order UUID identifier",
        min_length=36,
        max_length=36,
        regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    )
) -> str:
    """Validate order ID path parameter."""
    try:
        return IDValidator.validate_uuid_string(order_id, "order_id")
    except IDValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


def validate_vendor_id(
    vendor_id: str = Path(
        ...,
        description="Vendor UUID identifier",
        min_length=36,
        max_length=36,
        regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    )
) -> str:
    """Validate vendor ID path parameter."""
    try:
        return IDValidator.validate_uuid_string(vendor_id, "vendor_id")
    except IDValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


def validate_commission_id(
    commission_id: str = Path(
        ...,
        description="Commission UUID identifier",
        min_length=36,
        max_length=36,
        regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    )
) -> str:
    """Validate commission ID path parameter."""
    try:
        return IDValidator.validate_uuid_string(commission_id, "commission_id")
    except IDValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


def validate_category_id(
    category_id: str = Path(
        ...,
        description="Category UUID identifier",
        min_length=36,
        max_length=36,
        regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    )
) -> str:
    """Validate category ID path parameter."""
    try:
        return IDValidator.validate_uuid_string(category_id, "category_id")
    except IDValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Pydantic Field Validators for Schemas
class IDValidationMixin:
    """
    Mixin class for Pydantic models to add consistent ID validation.

    Usage:
        class MySchema(BaseModel, IDValidationMixin):
            id: str
            user_id: Optional[str] = None
    """

    @field_validator("id", mode="before", check_fields=False)
    @classmethod
    def validate_id_field(cls, v: Any) -> str:
        """Validate main ID field."""
        return IDValidator.validate_uuid_string(v, "id")

    @field_validator("user_id", mode="before", check_fields=False)
    @classmethod
    def validate_user_id_field(cls, v: Any) -> Optional[str]:
        """Validate user_id field."""
        return IDValidator.validate_optional_uuid_string(v, "user_id")

    @field_validator("product_id", mode="before", check_fields=False)
    @classmethod
    def validate_product_id_field(cls, v: Any) -> Optional[str]:
        """Validate product_id field."""
        return IDValidator.validate_optional_uuid_string(v, "product_id")

    @field_validator("order_id", mode="before", check_fields=False)
    @classmethod
    def validate_order_id_field(cls, v: Any) -> Optional[str]:
        """Validate order_id field."""
        return IDValidator.validate_optional_uuid_string(v, "order_id")

    @field_validator("vendor_id", mode="before", check_fields=False)
    @classmethod
    def validate_vendor_id_field(cls, v: Any) -> Optional[str]:
        """Validate vendor_id field."""
        return IDValidator.validate_optional_uuid_string(v, "vendor_id")

    @field_validator("commission_id", mode="before", check_fields=False)
    @classmethod
    def validate_commission_id_field(cls, v: Any) -> Optional[str]:
        """Validate commission_id field."""
        return IDValidator.validate_optional_uuid_string(v, "commission_id")

    @field_validator("category_id", mode="before", check_fields=False)
    @classmethod
    def validate_category_id_field(cls, v: Any) -> Optional[str]:
        """Validate category_id field."""
        return IDValidator.validate_optional_uuid_string(v, "category_id")


# Performance-optimized validators for high-traffic endpoints
class FastIDValidator:
    """
    Performance-optimized ID validators for high-traffic scenarios.
    Uses precompiled regex patterns and minimal exception handling.
    """

    # Precompiled UUID regex pattern for performance
    UUID_PATTERN = re.compile(
        r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
        re.IGNORECASE
    )

    @classmethod
    def is_valid_uuid_fast(cls, value: str) -> bool:
        """Fast UUID validation using precompiled regex."""
        if not value or len(value) != 36:
            return False
        return bool(cls.UUID_PATTERN.match(value.lower()))

    @classmethod
    def validate_uuid_fast(cls, value: str, field_name: str = "id") -> str:
        """Fast UUID validation with minimal error handling."""
        if not value:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} is required"
            )

        str_value = str(value).strip().lower()

        if not cls.is_valid_uuid_fast(str_value):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {field_name} format"
            )

        return str_value


# Utility functions for common operations
def normalize_uuid_string(value: Union[str, UUID, None]) -> Optional[str]:
    """
    Normalize UUID value to consistent string format.

    Args:
        value: UUID value in various formats

    Returns:
        Optional[str]: Normalized UUID string or None
    """
    if not value:
        return None

    try:
        if isinstance(value, UUID):
            return str(value).lower()

        str_value = str(value).strip().lower()
        if IDValidator.is_valid_uuid_string(str_value):
            return str_value

        return None
    except:
        return None


def convert_to_uuid_object(value: Union[str, UUID, None]) -> Optional[UUID]:
    """
    Convert string or UUID to UUID object.

    Args:
        value: UUID value to convert

    Returns:
        Optional[UUID]: UUID object or None
    """
    if not value:
        return None

    try:
        if isinstance(value, UUID):
            return value

        str_value = str(value).strip()
        return uuid.UUID(str_value)
    except:
        return None


# Export all validators and utilities
__all__ = [
    "IDValidationError",
    "IDValidator",
    "IDValidationMixin",
    "FastIDValidator",
    "validate_user_id",
    "validate_product_id",
    "validate_order_id",
    "validate_vendor_id",
    "validate_commission_id",
    "validate_category_id",
    "normalize_uuid_string",
    "convert_to_uuid_object"
]