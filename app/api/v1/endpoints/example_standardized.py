# ~/app/api/v1/endpoints/example_standardized.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Example Standardized Endpoints Implementation
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Example endpoints showing standardized response implementation.

This module demonstrates:
- Proper use of standardized response schemas
- Error handling with consistent error responses
- Pagination with standardized format
- CRUD operations with standard patterns
- Authentication endpoints with standard responses
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.product import Product
from app.schemas.response_base import (
    SuccessResponse,
    PaginatedResponse,
    MessageResponse,
    ErrorResponse
)
from app.schemas.user import UserRead
from app.schemas.product import ProductRead
from app.utils.response_utils import (
    ResponseUtils,
    AuthResponseUtils,
    ProductResponseUtils
)
from app.api.v1.handlers.exceptions import (
    ResourceNotFoundException,
    AuthenticationException,
    BusinessLogicException
)

router = APIRouter()


@router.get(
    "/users",
    response_model=PaginatedResponse[UserRead],
    summary="Get paginated users",
    description="Retrieve users with pagination using standardized response format"
)
async def get_users_paginated(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated users with standardized response."""
    try:
        # Calculate offset
        offset = (page - 1) * size

        # Query users (simplified - in real implementation would use proper queries)
        # This is just for demonstration
        users = []  # Would be actual user query results
        total = 0   # Would be actual total count

        return ResponseUtils.paginated(
            items=users,
            page=page,
            size=size,
            total=total,
            message=f"Retrieved {len(users)} users for page {page}"
        )

    except Exception as e:
        return ResponseUtils.internal_error(
            message="Failed to retrieve users"
        )


@router.get(
    "/users/{user_id}",
    response_model=SuccessResponse[UserRead],
    summary="Get user by ID",
    description="Retrieve a specific user by ID with standardized response"
)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID with standardized response."""
    try:
        # In real implementation, would query the database
        user = None  # Would be actual user query

        if not user:
            raise ResourceNotFoundException(
                resource_type="User",
                resource_id=str(user_id)
            )

        return ResponseUtils.success(
            data=user,
            message=f"User {user_id} retrieved successfully"
        )

    except ResourceNotFoundException:
        return ResponseUtils.not_found(
            resource_type="User",
            resource_id=str(user_id)
        )
    except Exception as e:
        return ResponseUtils.internal_error(
            message="Failed to retrieve user"
        )


@router.post(
    "/products",
    response_model=SuccessResponse[ProductRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Create a new product with standardized response"
)
async def create_product(
    product_data: dict,  # Would be ProductCreate schema in real implementation
    db: AsyncSession = Depends(get_db)
):
    """Create product with standardized response."""
    try:
        # Validate business rules
        if not product_data.get("name"):
            raise BusinessLogicException(
                message="Product name is required",
                error_code="MISSING_PRODUCT_NAME"
            )

        # In real implementation, would create the product
        created_product = {}  # Would be actual created product

        return ProductResponseUtils.product_created(created_product)

    except BusinessLogicException as e:
        return ResponseUtils.error(
            error_code=e.error_code,
            message=e.message,
            status_code=e.status_code
        )
    except Exception as e:
        return ResponseUtils.internal_error(
            message="Failed to create product"
        )


@router.put(
    "/products/{product_id}",
    response_model=SuccessResponse[ProductRead],
    summary="Update product",
    description="Update an existing product with standardized response"
)
async def update_product(
    product_id: int,
    product_data: dict,  # Would be ProductUpdate schema in real implementation
    db: AsyncSession = Depends(get_db)
):
    """Update product with standardized response."""
    try:
        # Check if product exists
        existing_product = None  # Would be actual product query

        if not existing_product:
            raise ResourceNotFoundException(
                resource_type="Product",
                resource_id=str(product_id)
            )

        # In real implementation, would update the product
        updated_product = {}  # Would be actual updated product

        return ProductResponseUtils.product_updated(updated_product)

    except ResourceNotFoundException:
        return ProductResponseUtils.product_not_found(str(product_id))
    except Exception as e:
        return ResponseUtils.internal_error(
            message="Failed to update product"
        )


@router.delete(
    "/products/{product_id}",
    response_model=MessageResponse,
    summary="Delete product",
    description="Delete a product with standardized response"
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete product with standardized response."""
    try:
        # Check if product exists
        existing_product = None  # Would be actual product query

        if not existing_product:
            raise ResourceNotFoundException(
                resource_type="Product",
                resource_id=str(product_id)
            )

        # In real implementation, would delete the product
        # delete_product_logic(product_id)

        return ResponseUtils.deleted(
            message=f"Product {product_id} deleted successfully"
        )

    except ResourceNotFoundException:
        return ProductResponseUtils.product_not_found(str(product_id))
    except Exception as e:
        return ResponseUtils.internal_error(
            message="Failed to delete product"
        )


@router.post(
    "/auth/login",
    response_model=SuccessResponse[dict],
    summary="User login",
    description="Authenticate user with standardized response"
)
async def login_example(
    login_data: dict,  # Would be LoginRequest schema in real implementation
    db: AsyncSession = Depends(get_db)
):
    """Login with standardized response."""
    try:
        email = login_data.get("email")
        password = login_data.get("password")

        if not email or not password:
            return ResponseUtils.validation_error(
                validation_errors=[
                    {"field": "email", "message": "Email is required", "error_type": "missing"},
                    {"field": "password", "message": "Password is required", "error_type": "missing"}
                ]
            )

        # In real implementation, would authenticate user
        user = None  # Would be actual user authentication

        if not user:
            raise AuthenticationException("Invalid email or password")

        # Generate tokens (simplified)
        token = "example_token"
        user_data = {"id": 1, "email": email, "user_type": "USER"}

        return AuthResponseUtils.login_success(
            user_data=user_data,
            token=token
        )

    except AuthenticationException:
        return ResponseUtils.unauthorized("Invalid email or password")
    except Exception as e:
        return ResponseUtils.internal_error(
            message="Authentication failed"
        )


@router.post(
    "/auth/logout",
    response_model=MessageResponse,
    summary="User logout",
    description="Logout user with standardized response"
)
async def logout_example():
    """Logout with standardized response."""
    try:
        # In real implementation, would invalidate token
        # invalidate_token_logic()

        return AuthResponseUtils.logout_success()

    except Exception as e:
        return ResponseUtils.internal_error(
            message="Logout failed"
        )


@router.get(
    "/search",
    response_model=SuccessResponse[dict],
    summary="Search with filters",
    description="Search with query parameters and standardized response"
)
async def search_example(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, gt=0, description="Maximum price")
):
    """Search with standardized response."""
    try:
        # Validate search parameters
        if min_price and max_price and min_price > max_price:
            return ResponseUtils.error(
                error_code="INVALID_PRICE_RANGE",
                message="Minimum price cannot be greater than maximum price",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # In real implementation, would perform search
        search_results = {
            "query": q,
            "filters": {
                "category": category,
                "price_range": {"min": min_price, "max": max_price}
            },
            "results": [],  # Would be actual search results
            "total": 0
        }

        return ResponseUtils.success(
            data=search_results,
            message=f"Search completed for query: '{q}'"
        )

    except Exception as e:
        return ResponseUtils.internal_error(
            message="Search failed"
        )


# Health check endpoint for testing standardized responses
@router.get(
    "/health/standardized",
    response_model=SuccessResponse[dict],
    summary="Standardized health check",
    description="Health check endpoint demonstrating standardized response format"
)
async def health_check_standardized():
    """Health check with standardized response format."""
    health_data = {
        "service": "Example Standardized Endpoints",
        "status": "healthy",
        "timestamp": "2025-09-17T12:00:00Z",
        "features": [
            "Standardized responses",
            "Error handling",
            "Pagination",
            "Validation"
        ]
    }

    return ResponseUtils.success(
        data=health_data,
        message="Standardized health check completed successfully"
    )