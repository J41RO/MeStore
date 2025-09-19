"""
Standardized Authentication Dependencies for MeStore API
=====================================================

Centralized authentication and authorization dependencies with
consistent error handling and role-based access control.

Author: API Architect AI
Date: 2025-09-17
Purpose: API standardization - unified auth patterns
"""

from typing import Optional
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserType
from app.core.responses import AuthErrorHelper, ErrorHelper
from app.schemas.common import ErrorCode

# Initialize HTTPBearer security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Standard authentication dependency for all protected endpoints.

    Args:
        credentials: HTTPBearer credentials from Authorization header
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        StandardHTTPException: 401 if authentication fails
    """
    if not credentials:
        raise AuthErrorHelper.invalid_credentials()

    try:
        # Decode and validate JWT token
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise AuthErrorHelper.invalid_credentials()

    except Exception:
        raise AuthErrorHelper.token_expired()

    # Get user from database
    user = await db.get(User, user_id)
    if user is None:
        raise AuthErrorHelper.invalid_credentials()

    # Check if user account is active
    if not user.is_active:
        raise AuthErrorHelper.account_disabled()

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency for endpoints that work with or without auth.

    Args:
        credentials: Optional HTTPBearer credentials
        db: Database session

    Returns:
        Optional[User]: Authenticated user if valid token, None otherwise
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except Exception:
        return None


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin or superuser permissions.

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User: User with admin permissions

    Raises:
        StandardHTTPException: 403 if insufficient permissions
    """
    if current_user.user_type not in [UserType.ADMIN, UserType.SUPERUSER]:
        raise ErrorHelper.forbidden(
            "Administrator permissions required",
            details={"required_roles": ["admin", "superuser"], "user_role": current_user.user_type.value}
        )

    return current_user


async def require_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require superuser permissions.

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User: User with superuser permissions

    Raises:
        StandardHTTPException: 403 if insufficient permissions
    """
    if current_user.user_type != UserType.SUPERUSER:
        raise ErrorHelper.forbidden(
            "Superuser permissions required",
            details={"required_role": "superuser", "user_role": current_user.user_type.value}
        )

    return current_user


async def require_vendor(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require vendor permissions.

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User: User with vendor permissions

    Raises:
        StandardHTTPException: 403 if insufficient permissions
    """
    if current_user.user_type != UserType.VENDOR:
        raise ErrorHelper.forbidden(
            "Vendor permissions required",
            details={"required_role": "vendor", "user_role": current_user.user_type.value}
        )

    return current_user


async def require_buyer(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require buyer permissions.

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User: User with buyer permissions

    Raises:
        StandardHTTPException: 403 if insufficient permissions
    """
    if current_user.user_type != UserType.BUYER:
        raise ErrorHelper.forbidden(
            "Buyer permissions required",
            details={"required_role": "buyer", "user_role": current_user.user_type.value}
        )

    return current_user


async def require_vendor_or_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require vendor or admin permissions.

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User: User with vendor or admin permissions

    Raises:
        StandardHTTPException: 403 if insufficient permissions
    """
    allowed_roles = [UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]
    if current_user.user_type not in allowed_roles:
        raise ErrorHelper.forbidden(
            "Vendor or administrator permissions required",
            details={
                "required_roles": ["vendor", "admin", "superuser"],
                "user_role": current_user.user_type.value
            }
        )

    return current_user


async def require_admin_or_self(
    target_user_id: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin permissions or access to own resources.

    Args:
        target_user_id: ID of the user being accessed
        current_user: Authenticated user from get_current_user

    Returns:
        User: User with admin permissions or same user

    Raises:
        StandardHTTPException: 403 if insufficient permissions
    """
    is_admin = current_user.user_type in [UserType.ADMIN, UserType.SUPERUSER]
    is_self = str(current_user.id) == target_user_id

    if not (is_admin or is_self):
        raise ErrorHelper.forbidden(
            "Can only access own resources or admin permissions required",
            details={
                "target_user_id": target_user_id,
                "current_user_id": str(current_user.id),
                "user_role": current_user.user_type.value
            }
        )

    return current_user


async def require_vendor_ownership(
    vendor_id: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require vendor to own the resource or admin permissions.

    Args:
        vendor_id: ID of the vendor who owns the resource
        current_user: Authenticated user from get_current_user

    Returns:
        User: User with ownership or admin permissions

    Raises:
        StandardHTTPException: 403 if insufficient permissions
    """
    is_admin = current_user.user_type in [UserType.ADMIN, UserType.SUPERUSER]
    is_owner = str(current_user.id) == vendor_id and current_user.user_type == UserType.VENDOR

    if not (is_admin or is_owner):
        raise ErrorHelper.forbidden(
            "Can only access own vendor resources or admin permissions required",
            details={
                "vendor_id": vendor_id,
                "current_user_id": str(current_user.id),
                "user_role": current_user.user_type.value
            }
        )

    return current_user


# Permission matrix for documentation and validation
ENDPOINT_PERMISSIONS = {
    # Authentication endpoints (public)
    "POST /api/v1/auth/login": ["PUBLIC"],
    "POST /api/v1/auth/register": ["PUBLIC"],
    "POST /api/v1/auth/refresh-token": ["PUBLIC"],

    # Protected authentication endpoints
    "GET /api/v1/auth/me": ["AUTHENTICATED"],
    "POST /api/v1/auth/logout": ["AUTHENTICATED"],

    # Product endpoints
    "GET /api/v1/productos/": ["PUBLIC"],
    "GET /api/v1/productos/{id}": ["PUBLIC"],
    "POST /api/v1/productos/": ["vendor", "admin"],
    "PUT /api/v1/productos/{id}": ["VENDOR_OWNER", "admin"],
    "PATCH /api/v1/productos/{id}": ["VENDOR_OWNER", "admin"],
    "DELETE /api/v1/productos/{id}": ["VENDOR_OWNER", "admin"],

    # Commission endpoints
    "GET /api/v1/commissions/": ["vendor", "admin"],
    "GET /api/v1/commissions/{id}": ["VENDOR_OWNER", "admin"],
    "GET /api/v1/commissions/earnings": ["vendor", "admin"],
    "POST /api/v1/commissions/calculate": ["admin"],
    "PATCH /api/v1/commissions/{id}/approve": ["admin"],

    # Order endpoints
    "GET /api/v1/orders/": ["buyer", "vendor", "admin"],
    "POST /api/v1/orders/": ["buyer"],
    "GET /api/v1/orders/{id}": ["BUYER_OWNER", "VENDOR_INVOLVED", "admin"],
    "PUT /api/v1/orders/{id}": ["BUYER_OWNER", "VENDOR_INVOLVED", "admin"],

    # Payment endpoints
    "POST /api/v1/payments/process": ["buyer"],
    "GET /api/v1/payments/status/{id}": ["BUYER_OWNER", "admin"],
    "POST /api/v1/payments/webhook": ["SYSTEM"],

    # Admin endpoints
    "GET /api/v1/admin/*": ["admin"],
    "POST /api/v1/admin/*": ["admin"],
    "PUT /api/v1/admin/*": ["admin"],
    "DELETE /api/v1/admin/*": ["admin"],

    # Vendor profile endpoints
    "GET /api/v1/vendors/profile": ["vendor", "admin"],
    "PUT /api/v1/vendors/profile": ["vendor"],

    # Search endpoints (public with optional auth)
    "GET /api/v1/search/": ["PUBLIC", "OPTIONAL_AUTH"],
    "POST /api/v1/search/": ["PUBLIC", "OPTIONAL_AUTH"],
}


def validate_endpoint_permission(endpoint: str, user_type: UserType) -> bool:
    """
    Validate if user has permission for endpoint.

    Args:
        endpoint: Endpoint pattern (e.g., "GET /api/v1/productos/")
        user_type: User's role type

    Returns:
        bool: True if user has permission
    """
    permissions = ENDPOINT_PERMISSIONS.get(endpoint, [])

    if "PUBLIC" in permissions:
        return True

    if "AUTHENTICATED" in permissions and user_type:
        return True

    user_type_str = user_type.value if user_type else None
    return user_type_str in permissions


# Export all dependencies and utilities
__all__ = [
    "get_current_user",
    "get_current_user_optional",
    "require_admin",
    "require_superuser",
    "require_vendor",
    "require_buyer",
    "require_vendor_or_admin",
    "require_admin_or_self",
    "require_vendor_ownership",
    "ENDPOINT_PERMISSIONS",
    "validate_endpoint_permission",
]