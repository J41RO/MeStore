"""
Admin Utilities - REFACTOR Phase TDD Implementation
===================================================

Consolidated utility functions and decorators for admin endpoint operations.
This module extracts common patterns and provides reusable components for
admin management functionality.

File: app/core/admin_utils.py
Author: TDD Specialist AI
Date: 2025-09-21
Phase: REFACTOR - Optimization and consolidation
Framework: TDD RED-GREEN-REFACTOR methodology

Features:
- Permission validation decorators
- Common database query optimizations
- Shared error handling patterns
- Security validation utilities
- Performance monitoring decorators
"""

import functools
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Callable, Union
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, func, desc, text
from pydantic import BaseModel

from app.models.user import User, UserType
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, RiskLevel
from app.services.admin_permission_service import admin_permission_service, PermissionDeniedError

logger = logging.getLogger(__name__)


# ============================================================================
# SHARED DATA CLASSES FOR ADMIN OPERATIONS
# ============================================================================

class AdminValidationResult:
    """Result of admin validation operations."""

    def __init__(self,
                 is_valid: bool,
                 user: Optional[User] = None,
                 error_message: Optional[str] = None,
                 error_code: int = status.HTTP_403_FORBIDDEN):
        self.is_valid = is_valid
        self.user = user
        self.error_message = error_message
        self.error_code = error_code


class QueryOptimizationResult:
    """Result of database query optimization."""

    def __init__(self,
                 query: Any,
                 total_count: Optional[int] = None,
                 execution_time: Optional[float] = None):
        self.query = query
        self.total_count = total_count
        self.execution_time = execution_time


class AdminOperationMetrics:
    """Metrics for admin operations."""

    def __init__(self):
        self.start_time = time.time()
        self.db_queries = 0
        self.permission_checks = 0
        self.validation_time = 0.0
        self.processing_time = 0.0

    def add_db_query(self):
        self.db_queries += 1

    def add_permission_check(self):
        self.permission_checks += 1

    def finish(self):
        self.processing_time = time.time() - self.start_time
        return self


# ============================================================================
# PERMISSION VALIDATION DECORATORS
# ============================================================================

def require_admin_permission(
    resource: ResourceType,
    action: PermissionAction,
    scope: PermissionScope = PermissionScope.GLOBAL,
    min_clearance_level: int = 3,
    risk_level: RiskLevel = RiskLevel.MEDIUM
):
    """
    Decorator to require specific admin permission for endpoint access.

    Args:
        resource: The resource type being accessed
        action: The action being performed
        scope: The permission scope required
        min_clearance_level: Minimum security clearance level
        risk_level: Risk level for logging

    Usage:
        @require_admin_permission(ResourceType.USERS, PermissionAction.READ)
        async def list_users(...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user and db from kwargs or args
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')

            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing required dependencies for permission validation"
                )

            # Validate permission
            try:
                await admin_permission_service.validate_permission(
                    db, current_user, resource, action, scope
                )
            except PermissionDeniedError as e:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=str(e)
                )

            # Validate security clearance
            if hasattr(current_user, 'security_clearance_level'):
                if current_user.security_clearance_level < min_clearance_level:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Security clearance level {min_clearance_level} required"
                    )

            # Execute the function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def log_admin_operation(
    action_type: AdminActionType,
    operation_name: str,
    risk_level: RiskLevel = RiskLevel.MEDIUM
):
    """
    Decorator to automatically log admin operations.

    Args:
        action_type: Type of admin action being performed
        operation_name: Name of the operation for logging
        risk_level: Risk level of the operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')

            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Log successful operation
                if current_user and db:
                    processing_time = time.time() - start_time
                    await admin_permission_service._log_admin_activity(
                        db, current_user, action_type, operation_name,
                        f"Operation completed successfully in {processing_time:.3f}s",
                        risk_level=risk_level
                    )

                return result

            except Exception as e:
                # Log failed operation
                if current_user and db:
                    processing_time = time.time() - start_time
                    await admin_permission_service._log_admin_activity(
                        db, current_user, action_type, f"{operation_name}_failed",
                        f"Operation failed after {processing_time:.3f}s: {str(e)}",
                        risk_level=RiskLevel.HIGH
                    )
                raise

        return wrapper
    return decorator


def monitor_performance(threshold_ms: int = 1000):
    """
    Decorator to monitor and log slow admin operations.

    Args:
        threshold_ms: Threshold in milliseconds for logging slow operations
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                execution_time = (time.time() - start_time) * 1000

                if execution_time > threshold_ms:
                    logger.warning(
                        f"Slow admin operation detected: {func.__name__} "
                        f"took {execution_time:.2f}ms (threshold: {threshold_ms}ms)"
                    )

                return result

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(
                    f"Admin operation failed: {func.__name__} "
                    f"failed after {execution_time:.2f}ms: {str(e)}"
                )
                raise

        return wrapper
    return decorator


# ============================================================================
# ADMIN USER VALIDATION UTILITIES
# ============================================================================

async def validate_admin_user_access(
    db: Session,
    current_user: User,
    target_user_id: str,
    operation: str = "access"
) -> AdminValidationResult:
    """
    Validate access to admin user operations.

    Args:
        db: Database session
        current_user: Current authenticated user
        target_user_id: ID of target user being accessed
        operation: Type of operation being performed

    Returns:
        AdminValidationResult with validation outcome
    """
    try:
        # Get target user
        target_user = db.query(User).filter(
            User.id == target_user_id,
            User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
        ).first()

        if not target_user:
            return AdminValidationResult(
                is_valid=False,
                error_message="Admin user not found",
                error_code=status.HTTP_404_NOT_FOUND
            )

        # Validate security clearance hierarchy
        if hasattr(current_user, 'security_clearance_level') and hasattr(target_user, 'security_clearance_level'):
            if operation in ['update', 'delete', 'manage_permissions']:
                if current_user.security_clearance_level <= target_user.security_clearance_level:
                    return AdminValidationResult(
                        is_valid=False,
                        error_message="Cannot perform operation on user with equal or higher security clearance",
                        error_code=status.HTTP_403_FORBIDDEN
                    )

        # Validate SUPERUSER restrictions
        if target_user.user_type == UserType.SUPERUSER:
            if not current_user.is_superuser():
                return AdminValidationResult(
                    is_valid=False,
                    error_message="Only SUPERUSERs can access other SUPERUSER accounts",
                    error_code=status.HTTP_403_FORBIDDEN
                )

        return AdminValidationResult(
            is_valid=True,
            user=target_user
        )

    except Exception as e:
        logger.error(f"Error validating admin user access: {str(e)}")
        return AdminValidationResult(
            is_valid=False,
            error_message="Internal validation error",
            error_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def validate_security_clearance_change(
    current_user: User,
    target_user: User,
    new_clearance_level: int
) -> AdminValidationResult:
    """
    Validate security clearance level changes.

    Args:
        current_user: User making the change
        target_user: User being modified
        new_clearance_level: New security clearance level

    Returns:
        AdminValidationResult with validation outcome
    """
    # Validate current user can make changes
    if not hasattr(current_user, 'security_clearance_level'):
        return AdminValidationResult(
            is_valid=False,
            error_message="Current user has no security clearance level"
        )

    # Cannot set clearance equal to or higher than current user's
    if new_clearance_level >= current_user.security_clearance_level:
        return AdminValidationResult(
            is_valid=False,
            error_message="Cannot set security clearance equal to or higher than your own"
        )

    # SUPERUSER restriction
    if new_clearance_level == 5 and not current_user.is_superuser():
        return AdminValidationResult(
            is_valid=False,
            error_message="Only SUPERUSERs can grant level 5 clearance"
        )

    return AdminValidationResult(is_valid=True)


# ============================================================================
# DATABASE QUERY OPTIMIZATION UTILITIES
# ============================================================================

class OptimizedAdminQueries:
    """Optimized database queries for admin operations."""

    @staticmethod
    def get_admin_list_query(
        db: Session,
        user_type: Optional[UserType] = None,
        department_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        include_permission_count: bool = True,
        include_last_activity: bool = True
    ) -> QueryOptimizationResult:
        """
        Get optimized query for admin user listing with minimal N+1 queries.

        Returns:
            QueryOptimizationResult with optimized query
        """
        start_time = time.time()

        # Base query with eager loading
        query = db.query(User).filter(
            User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
        )

        # Apply filters
        if user_type:
            query = query.filter(User.user_type == user_type)
        if department_id:
            query = query.filter(User.department_id == department_id)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_term),
                    User.nombre.ilike(search_term),
                    User.apellido.ilike(search_term)
                )
            )

        # Get total count efficiently
        total_count = query.count()

        execution_time = time.time() - start_time

        return QueryOptimizationResult(
            query=query,
            total_count=total_count,
            execution_time=execution_time
        )

    @staticmethod
    def get_admin_with_permissions_query(
        db: Session,
        admin_id: str
    ) -> QueryOptimizationResult:
        """
        Get admin user with permissions in a single optimized query.

        Returns:
            QueryOptimizationResult with admin and permissions
        """
        start_time = time.time()

        # Single query with joins to get admin and permission count
        query = db.query(User).filter(
            User.id == admin_id,
            User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
        ).options(
            selectinload(User.admin_permissions)
        )

        execution_time = time.time() - start_time

        return QueryOptimizationResult(
            query=query,
            execution_time=execution_time
        )

    @staticmethod
    def get_permission_counts_batch(
        db: Session,
        user_ids: List[str]
    ) -> Dict[str, int]:
        """
        Get permission counts for multiple users in a single query.

        Args:
            db: Database session
            user_ids: List of user IDs

        Returns:
            Dictionary mapping user_id to permission count
        """
        from app.models.admin_permission import admin_user_permissions

        result = db.query(
            admin_user_permissions.c.user_id,
            func.count(admin_user_permissions.c.permission_id).label('permission_count')
        ).filter(
            admin_user_permissions.c.user_id.in_(user_ids),
            admin_user_permissions.c.is_active == True
        ).group_by(admin_user_permissions.c.user_id).all()

        return {str(row.user_id): row.permission_count for row in result}

    @staticmethod
    def get_last_activity_batch(
        db: Session,
        user_ids: List[str]
    ) -> Dict[str, datetime]:
        """
        Get last activity timestamps for multiple users in a single query.

        Args:
            db: Database session
            user_ids: List of user IDs

        Returns:
            Dictionary mapping user_id to last activity timestamp
        """
        subquery = db.query(
            AdminActivityLog.admin_user_id,
            func.max(AdminActivityLog.created_at).label('last_activity')
        ).filter(
            AdminActivityLog.admin_user_id.in_(user_ids)
        ).group_by(AdminActivityLog.admin_user_id).subquery()

        result = db.query(subquery).all()

        return {str(row.admin_user_id): row.last_activity for row in result}


# ============================================================================
# ERROR HANDLING UTILITIES
# ============================================================================

class AdminErrorHandler:
    """Consolidated error handling for admin operations."""

    @staticmethod
    def handle_permission_error(
        error: PermissionDeniedError,
        operation: str,
        user_id: Optional[str] = None
    ) -> HTTPException:
        """Handle permission denied errors consistently."""
        logger.warning(
            f"Permission denied for operation '{operation}' "
            f"by user {user_id}: {str(error)}"
        )
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error)
        )

    @staticmethod
    def handle_validation_error(
        error: Exception,
        operation: str,
        data: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """Handle validation errors consistently."""
        logger.error(
            f"Validation error in operation '{operation}': {str(error)}"
        )
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {str(error)}"
        )

    @staticmethod
    def handle_database_error(
        error: Exception,
        operation: str,
        rollback_db: Optional[Session] = None
    ) -> HTTPException:
        """Handle database errors consistently."""
        if rollback_db:
            rollback_db.rollback()

        logger.error(
            f"Database error in operation '{operation}': {str(error)}"
        )
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation failed: {operation}"
        )

    @staticmethod
    def handle_not_found_error(
        resource_type: str,
        resource_id: Optional[str] = None
    ) -> HTTPException:
        """Handle not found errors consistently."""
        detail = f"{resource_type.title()} not found"
        if resource_id:
            detail += f" (ID: {resource_id})"

        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


# ============================================================================
# BULK OPERATION UTILITIES
# ============================================================================

async def process_bulk_admin_operation(
    db: Session,
    current_user: User,
    user_ids: List[str],
    operation: str,
    operation_func: Callable,
    reason: str,
    max_batch_size: int = 50
) -> Dict[str, Any]:
    """
    Process bulk admin operations with consistent error handling and logging.

    Args:
        db: Database session
        current_user: User performing the operation
        user_ids: List of user IDs to process
        operation: Name of the operation
        operation_func: Function to apply to each user
        reason: Reason for the bulk operation
        max_batch_size: Maximum batch size for processing

    Returns:
        Dictionary with operation results
    """
    if len(user_ids) > max_batch_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bulk operation limited to {max_batch_size} users"
        )

    # Get all admin users in one query
    admins = db.query(User).filter(
        User.id.in_(user_ids),
        User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
    ).all()

    if len(admins) != len(user_ids):
        missing_ids = set(user_ids) - {str(admin.id) for admin in admins}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin users not found: {list(missing_ids)}"
        )

    # Process each admin user
    processed_count = 0
    action_results = []

    for admin in admins:
        try:
            # Validate access to this admin
            validation = await validate_admin_user_access(
                db, current_user, str(admin.id), operation
            )

            if not validation.is_valid:
                action_results.append({
                    "user_id": str(admin.id),
                    "email": admin.email,
                    "status": "error",
                    "error": validation.error_message
                })
                continue

            # Apply operation
            await operation_func(admin)

            processed_count += 1
            action_results.append({
                "user_id": str(admin.id),
                "email": admin.email,
                "status": "success"
            })

        except Exception as e:
            action_results.append({
                "user_id": str(admin.id),
                "email": admin.email,
                "status": "error",
                "error": str(e)
            })

    # Log bulk operation
    await admin_permission_service._log_admin_activity(
        db, current_user, AdminActionType.USER_MANAGEMENT, f"bulk_{operation}",
        f"Bulk {operation} on {processed_count}/{len(user_ids)} admin users. Reason: {reason}",
        risk_level=RiskLevel.HIGH
    )

    return {
        "message": f"Bulk {operation} completed. Processed {processed_count}/{len(user_ids)} users",
        "operation": operation,
        "processed_count": processed_count,
        "total_requested": len(user_ids),
        "results": action_results
    }


# ============================================================================
# RESPONSE FORMATTING UTILITIES
# ============================================================================

def format_admin_response(
    admin: User,
    permission_count: Optional[int] = None,
    last_activity: Optional[datetime] = None,
    include_sensitive: bool = False
) -> Dict[str, Any]:
    """
    Format admin user data for consistent API responses.

    Args:
        admin: Admin user object
        permission_count: Number of permissions (optional)
        last_activity: Last activity timestamp (optional)
        include_sensitive: Whether to include sensitive fields

    Returns:
        Formatted admin response dictionary
    """
    response_data = admin.to_enterprise_dict()

    # Add computed fields
    if permission_count is not None:
        response_data['permission_count'] = permission_count
    if last_activity is not None:
        response_data['last_activity'] = last_activity

    # Remove sensitive fields if requested
    if not include_sensitive:
        sensitive_fields = ['password_hash', 'refresh_token', 'reset_token']
        for field in sensitive_fields:
            response_data.pop(field, None)

    return response_data


def format_permission_response(
    permissions: List[AdminPermission],
    include_expired: bool = False
) -> List[Dict[str, Any]]:
    """
    Format permissions data for consistent API responses.

    Args:
        permissions: List of permission objects
        include_expired: Whether to include expired permissions

    Returns:
        List of formatted permission dictionaries
    """
    formatted_permissions = []

    for permission in permissions:
        # Skip expired permissions if not requested
        if not include_expired and hasattr(permission, 'expires_at'):
            if permission.expires_at and permission.expires_at < datetime.utcnow():
                continue

        formatted_permissions.append({
            'id': str(permission.id),
            'name': permission.name,
            'description': permission.description,
            'resource_type': permission.resource_type.value,
            'action': permission.action.value,
            'scope': permission.scope.value,
            'is_active': getattr(permission, 'is_active', True),
            'granted_at': getattr(permission, 'granted_at', None),
            'expires_at': getattr(permission, 'expires_at', None)
        })

    return formatted_permissions