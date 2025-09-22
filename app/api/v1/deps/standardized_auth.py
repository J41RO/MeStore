"""
Standardized Authentication Dependencies for MeStore API
=====================================================

Centralized authentication and authorization dependencies with
consistent error handling and role-based access control.

Author: API Architect AI
Date: 2025-09-17
Purpose: API standardization - unified auth patterns
"""

from typing import Optional, Union, List, Set
import logging

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserType
from app.core.responses import AuthErrorHelper, ErrorHelper
from app.schemas.common import ErrorCode

# Configure logger for authentication operations
logger = logging.getLogger(__name__)

# Initialize HTTPBearer security scheme with optimized error handling
security = HTTPBearer(auto_error=False)

# Pre-define role sets for better performance
ADMIN_ROLES: Set[UserType] = {UserType.ADMIN, UserType.SUPERUSER}
VENDOR_OR_ADMIN_ROLES: Set[UserType] = {UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER}

# Type aliases for better code readability
UserRoleType = Union[UserType, None]
AuthCredentials = Optional[HTTPAuthorizationCredentials]


async def get_current_user(
    credentials: AuthCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Standard authentication dependency for all protected endpoints.

    This function provides comprehensive authentication validation with
    proper error handling and security logging.

    Args:
        credentials: HTTPBearer credentials from Authorization header
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        StandardHTTPException: 401 if authentication fails
    """
    if not credentials:
        logger.warning("Authentication failed: No credentials provided")
        raise AuthErrorHelper.invalid_credentials()

    try:
        # Decode and validate JWT token
        payload = decode_access_token(credentials.credentials)
        if payload is None:
            logger.warning("Authentication failed: Token decode returned None")
            raise AuthErrorHelper.token_expired()
    except Exception as e:
        logger.warning(f"Authentication failed: Token decode exception: {str(e)}")
        raise AuthErrorHelper.token_expired()

    # Validate user_id from token payload
    user_id: str = payload.get("sub")
    if not user_id or not isinstance(user_id, str) or user_id.strip() == "":
        logger.warning("Authentication failed: Invalid user_id in token payload")
        raise AuthErrorHelper.invalid_credentials()

    # Get user from database
    user = await db.get(User, user_id)
    if user is None:
        logger.warning(f"Authentication failed: User not found in database: {user_id}")
        raise AuthErrorHelper.invalid_credentials()

    # Check if user account is active
    if not user.is_active:
        logger.warning(f"Authentication failed: User account disabled: {user_id}")
        raise AuthErrorHelper.account_disabled()

    logger.debug(f"Authentication successful: {user_id} ({user.user_type.value})")
    return user


async def get_current_user_optional(
    credentials: AuthCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency for endpoints that work with or without auth.

    This function gracefully handles authentication failures and returns None
    instead of raising exceptions, making it suitable for public endpoints
    with optional authentication.

    Args:
        credentials: Optional HTTPBearer credentials
        db: Database session

    Returns:
        Optional[User]: Authenticated user if valid token, None otherwise
    """
    if not credentials:
        logger.debug("Optional authentication: No credentials provided")
        return None

    try:
        user = await get_current_user(credentials, db)
        logger.debug(f"Optional authentication successful: {user.id}")
        return user
    except Exception as e:
        logger.debug(f"Optional authentication failed gracefully: {str(e)}")
        return None


# Centralized role validation helper
def _validate_user_role(
    user: User,
    allowed_roles: Set[UserType],
    operation_description: str
) -> None:
    """
    Centralized role validation helper following DRY principle.

    Args:
        user: Authenticated user object
        allowed_roles: Set of allowed user types
        operation_description: Human-readable description for error messages

    Raises:
        HTTPException: 403 if user doesn't have required permissions
    """
    if user.user_type not in allowed_roles:
        logger.warning(
            f"Authorization failed: User {user.id} ({user.user_type.value}) "
            f"attempted {operation_description}"
        )

        role_names = [role.value for role in allowed_roles]
        raise ErrorHelper.forbidden(
            operation_description,
            details={
                "required_roles": role_names,
                "user_role": user.user_type.value,
                "user_id": str(user.id)
            }
        )

    logger.debug(
        f"Authorization successful: User {user.id} ({user.user_type.value}) "
        f"for {operation_description}"
    )


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
    _validate_user_role(
        user=current_user,
        allowed_roles=ADMIN_ROLES,
        operation_description="Administrator permissions required"
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
    _validate_user_role(
        user=current_user,
        allowed_roles={UserType.SUPERUSER},
        operation_description="Superuser permissions required"
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
    _validate_user_role(
        user=current_user,
        allowed_roles={UserType.VENDOR},
        operation_description="Vendor permissions required"
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
    _validate_user_role(
        user=current_user,
        allowed_roles={UserType.BUYER},
        operation_description="Buyer permissions required"
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
    _validate_user_role(
        user=current_user,
        allowed_roles=VENDOR_OR_ADMIN_ROLES,
        operation_description="Vendor or administrator permissions required"
    )
    return current_user


async def require_admin_or_self(
    target_user_id: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin permissions or access to own resources.

    This function allows users to access their own resources or requires
    admin privileges for accessing other users' resources.

    Args:
        target_user_id: ID of the user being accessed
        current_user: Authenticated user from get_current_user

    Returns:
        User: User with admin permissions or same user

    Raises:
        StandardHTTPException: 403 if insufficient permissions
    """
    is_admin = current_user.user_type in ADMIN_ROLES
    is_self = str(current_user.id) == target_user_id

    if not (is_admin or is_self):
        logger.warning(
            f"Access denied: User {current_user.id} ({current_user.user_type.value}) "
            f"attempted to access user {target_user_id} resources"
        )
        raise ErrorHelper.forbidden(
            "Can only access own resources or admin permissions required",
            details={
                "target_user_id": target_user_id,
                "current_user_id": str(current_user.id),
                "user_role": current_user.user_type.value
            }
        )

    access_type = "admin" if is_admin else "self"
    logger.debug(
        f"Access granted ({access_type}): User {current_user.id} "
        f"accessing user {target_user_id} resources"
    )
    return current_user


async def require_vendor_ownership(
    vendor_id: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require vendor to own the resource or admin permissions.

    This function enforces that only the vendor who owns a resource
    or administrators can access vendor-specific resources.

    Args:
        vendor_id: ID of the vendor who owns the resource
        current_user: Authenticated user from get_current_user

    Returns:
        User: User with ownership or admin permissions

    Raises:
        StandardHTTPException: 403 if insufficient permissions
    """
    is_admin = current_user.user_type in ADMIN_ROLES
    is_owner = (
        str(current_user.id) == vendor_id and
        current_user.user_type == UserType.VENDOR
    )

    if not (is_admin or is_owner):
        logger.warning(
            f"Vendor access denied: User {current_user.id} ({current_user.user_type.value}) "
            f"attempted to access vendor {vendor_id} resources"
        )
        raise ErrorHelper.forbidden(
            "Can only access own vendor resources or admin permissions required",
            details={
                "vendor_id": vendor_id,
                "current_user_id": str(current_user.id),
                "user_role": current_user.user_type.value
            }
        )

    access_type = "admin" if is_admin else "owner"
    logger.debug(
        f"Vendor access granted ({access_type}): User {current_user.id} "
        f"accessing vendor {vendor_id} resources"
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