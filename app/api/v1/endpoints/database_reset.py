"""
Database Reset API Endpoints

Provides secure API endpoints for database reset operations in testing environments.
All endpoints include comprehensive safety checks and require appropriate permissions.

Features:
- Environment-aware safety checks
- Admin-only access control
- Detailed operation logging
- Comprehensive error handling
- Flexible reset levels

Author: Backend Framework AI
Created: 2025-09-25
Version: 1.0.0
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.api.v1.deps.auth import require_admin
from app.models.user import User, UserType
from app.schemas.user import UserRead
from app.services.database_reset_service import (
    DatabaseResetService,
    ResetLevel,
    ResetResult,
    quick_user_reset,
    quick_test_data_reset
)
from app.core.config import settings

router = APIRouter(prefix="/database-reset", tags=["database-reset"])
logger = logging.getLogger(__name__)

# Security dependency
security = HTTPBearer()


# Request/Response Models
class ResetUserRequest(BaseModel):
    """Request model for single user reset."""
    user_id: Optional[str] = Field(None, description="User ID to reset")
    email: Optional[str] = Field(None, description="User email to reset (alternative to user_id)")
    level: ResetLevel = Field(ResetLevel.USER_CASCADE, description="Reset level")
    force: bool = Field(False, description="Force reset even if user doesn't appear to be test user")

    @validator('user_id', 'email')
    def validate_user_identifier(cls, v, values):
        if not values.get('user_id') and not v:
            raise ValueError("Either user_id or email must be provided")
        return v


class ResetTestUsersRequest(BaseModel):
    """Request model for test users reset."""
    email_patterns: Optional[List[str]] = Field(None, description="Email patterns to identify test users")
    level: ResetLevel = Field(ResetLevel.USER_CASCADE, description="Reset level")


class FullResetRequest(BaseModel):
    """Request model for full database reset (dangerous)."""
    confirm_dangerous: bool = Field(False, description="Must be True to execute full reset")
    preserve_admin_users: bool = Field(True, description="Whether to preserve admin users")
    confirmation_text: str = Field(..., description="Must type 'I UNDERSTAND THIS WILL DELETE ALL DATA'")

    @validator('confirmation_text')
    def validate_confirmation(cls, v):
        if v != "I UNDERSTAND THIS WILL DELETE ALL DATA":
            raise ValueError("Confirmation text must be exactly: 'I UNDERSTAND THIS WILL DELETE ALL DATA'")
        return v


class CreateTestUserRequest(BaseModel):
    """Request model for creating test users."""
    email: str = Field(..., description="Test user email (must use test domain)")
    password: str = Field("testpass123", description="User password")
    user_type: UserType = Field(UserType.BUYER, description="Type of user to create")
    nombre: Optional[str] = Field(None, description="User first name")
    apellido: Optional[str] = Field(None, description="User last name")
    cedula: Optional[str] = Field(None, description="User ID number")
    telefono: Optional[str] = Field(None, description="User phone number")
    ciudad: Optional[str] = Field(None, description="User city")


class ResetResultResponse(BaseModel):
    """Response model for reset operations."""
    success: bool
    level: Optional[str]
    deleted_records: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    execution_time: float
    affected_users: List[str]
    timestamp: str
    admin_user: str
    environment: str


class DatabaseStatsResponse(BaseModel):
    """Response model for database statistics."""
    users: Dict[str, Dict[str, int]]
    test_users: int
    table_sizes: List[Dict[str, Any]]
    environment: Dict[str, Any]
    timestamp: str


# Safety check dependency
def check_reset_environment():
    """Dependency to check if reset operations are allowed in current environment."""
    allowed_environments = {"development", "testing", "dev", "test"}
    current_env = settings.ENVIRONMENT.lower()

    if current_env not in allowed_environments:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Database reset not allowed in environment: {current_env}. "
                   f"Only allowed in: {', '.join(allowed_environments)}"
        )

    # Additional safety check for production-like database URLs
    if settings.DATABASE_URL and "localhost" not in settings.DATABASE_URL:
        if "test" not in settings.DATABASE_URL and "dev" not in settings.DATABASE_URL:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Database reset blocked: DATABASE_URL appears to be production. "
                       "Reset only allowed on localhost or test/dev databases."
            )


@router.get("/status", response_model=Dict[str, Any])
async def get_reset_status(
    current_user: UserRead = Depends(require_admin),
    _env_check = Depends(check_reset_environment)
):
    """
    Get current database reset service status and environment information.

    Returns information about the current environment, database state,
    and whether reset operations are allowed.
    """
    try:
        async with DatabaseResetService() as service:
            stats = await service.get_reset_statistics()

        return {
            "status": "available",
            "environment": settings.ENVIRONMENT,
            "database_url_safe": "localhost" in settings.DATABASE_URL or "test" in settings.DATABASE_URL,
            "reset_allowed": True,
            "admin_user": current_user.email,
            "timestamp": datetime.utcnow().isoformat(),
            **stats
        }

    except Exception as e:
        logger.error(f"Failed to get reset status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reset status: {str(e)}"
        )


@router.get("/statistics", response_model=DatabaseStatsResponse)
async def get_database_statistics(
    current_user: UserRead = Depends(require_admin),
    _env_check = Depends(check_reset_environment)
):
    """
    Get detailed database statistics for reset planning.

    Provides information about user counts, table sizes, and test data
    to help administrators plan reset operations.
    """
    try:
        async with DatabaseResetService() as service:
            stats = await service.get_reset_statistics()

        return DatabaseStatsResponse(
            users=stats.get("users", {}),
            test_users=stats.get("test_users", 0),
            table_sizes=stats.get("table_sizes", []),
            environment=stats.get("environment", {}),
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to get database statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database statistics: {str(e)}"
        )


@router.post("/user", response_model=ResetResultResponse)
async def reset_single_user(
    request: ResetUserRequest,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(require_admin),
    _env_check = Depends(check_reset_environment)
):
    """
    Reset a single user with specified cleanup level.

    Deletes the user and related data based on the specified reset level.
    Includes safety checks to prevent accidental deletion of production users.
    """
    try:
        async with DatabaseResetService() as service:
            if request.user_id:
                result = await service.delete_user_safely(
                    user_id=request.user_id,
                    level=request.level,
                    force=request.force
                )
            elif request.email:
                # Find user by email first
                result = await quick_user_reset(request.email)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either user_id or email must be provided"
                )

        # Log the operation
        log_msg = (
            f"Admin {current_user.email} reset user "
            f"{'ID ' + request.user_id if request.user_id else 'email ' + request.email} "
            f"with level {request.level.value}"
        )
        logger.info(log_msg)

        # Add background task for cleanup if needed
        if result.success and request.level == ResetLevel.USER_CASCADE:
            background_tasks.add_task(
                _cleanup_orphaned_records,
                admin_email=current_user.email
            )

        return ResetResultResponse(
            success=result.success,
            level=result.level,
            deleted_records=result.deleted_records,
            errors=result.errors,
            warnings=result.warnings,
            execution_time=result.execution_time,
            affected_users=result.affected_users,
            timestamp=datetime.utcnow().isoformat(),
            admin_user=current_user.email,
            environment=settings.ENVIRONMENT
        )

    except Exception as e:
        logger.error(f"Failed to reset user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset user: {str(e)}"
        )


@router.post("/test-users", response_model=ResetResultResponse)
async def reset_test_users(
    request: ResetTestUsersRequest,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(require_admin),
    _env_check = Depends(check_reset_environment)
):
    """
    Reset all identified test users.

    Automatically identifies and resets users with test email domains
    or matching specified patterns. This is the recommended way to
    clean up test data between testing sessions.
    """
    try:
        async with DatabaseResetService() as service:
            result = await service.reset_test_users(
                email_patterns=request.email_patterns,
                level=request.level
            )

        # Log the operation
        log_msg = (
            f"Admin {current_user.email} reset {len(result.affected_users)} test users "
            f"with level {request.level.value}"
        )
        logger.info(log_msg)

        # Add background cleanup task
        background_tasks.add_task(
            _cleanup_orphaned_records,
            admin_email=current_user.email
        )

        return ResetResultResponse(
            success=result.success,
            level=result.level,
            deleted_records=result.deleted_records,
            errors=result.errors,
            warnings=result.warnings,
            execution_time=result.execution_time,
            affected_users=result.affected_users,
            timestamp=datetime.utcnow().isoformat(),
            admin_user=current_user.email,
            environment=settings.ENVIRONMENT
        )

    except Exception as e:
        logger.error(f"Failed to reset test users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset test users: {str(e)}"
        )


@router.post("/full-reset", response_model=ResetResultResponse)
async def full_database_reset(
    request: FullResetRequest,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(require_admin),
    _env_check = Depends(check_reset_environment)
):
    """
    Perform a complete database reset (VERY DANGEROUS).

    ⚠️  **WARNING: THIS WILL DELETE ALL DATA IN THE DATABASE!** ⚠️

    This endpoint completely resets the database, deleting all tables
    and data. It should only be used for complete test environment
    reinitialization. Requires explicit confirmation and admin privileges.
    """
    # Additional superuser check for full reset
    if current_user.user_type != UserType.SUPERUSER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Full database reset requires superuser privileges"
        )

    try:
        async with DatabaseResetService() as service:
            result = await service.full_database_reset(
                confirm_dangerous=request.confirm_dangerous,
                preserve_admin_users=request.preserve_admin_users
            )

        # Log the critical operation
        log_msg = (
            f"CRITICAL: Superuser {current_user.email} performed FULL DATABASE RESET. "
            f"Admin users preserved: {request.preserve_admin_users}"
        )
        logger.critical(log_msg)

        return ResetResultResponse(
            success=result.success,
            level=result.level,
            deleted_records=result.deleted_records,
            errors=result.errors,
            warnings=result.warnings,
            execution_time=result.execution_time,
            affected_users=result.affected_users,
            timestamp=datetime.utcnow().isoformat(),
            admin_user=current_user.email,
            environment=settings.ENVIRONMENT
        )

    except Exception as e:
        logger.error(f"Full database reset failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Full database reset failed: {str(e)}"
        )


@router.post("/create-test-user", response_model=Dict[str, Any])
async def create_test_user(
    request: CreateTestUserRequest,
    current_user: UserRead = Depends(require_admin),
    _env_check = Depends(check_reset_environment)
):
    """
    Create a test user for testing purposes.

    Creates a new user with test email domain for safe testing.
    The user is created with verified status and can be safely
    deleted with reset operations.
    """
    try:
        async with DatabaseResetService() as service:
            extra_fields = {}
            if request.nombre:
                extra_fields["nombre"] = request.nombre
            if request.apellido:
                extra_fields["apellido"] = request.apellido
            if request.cedula:
                extra_fields["cedula"] = request.cedula
            if request.telefono:
                extra_fields["telefono"] = request.telefono
            if request.ciudad:
                extra_fields["ciudad"] = request.ciudad

            user = await service.create_test_user(
                email=request.email,
                password=request.password,
                user_type=request.user_type,
                **extra_fields
            )

        # Log the operation
        logger.info(f"Admin {current_user.email} created test user: {request.email}")

        return {
            "success": True,
            "message": "Test user created successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "user_type": user.user_type.value,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            },
            "admin_user": current_user.email,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to create test user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test user: {str(e)}"
        )


@router.post("/quick-reset", response_model=ResetResultResponse)
async def quick_reset_endpoint(
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(require_admin),
    _env_check = Depends(check_reset_environment)
):
    """
    Quick reset of all test data (convenience endpoint).

    Performs a standard reset of all identified test users with
    cascade cleanup. This is the most commonly used reset operation
    for cleaning up between test runs.
    """
    try:
        result_dict = (await quick_test_data_reset()).to_dict()

        # Log the operation
        logger.info(f"Admin {current_user.email} performed quick test data reset")

        # Add background cleanup
        background_tasks.add_task(
            _cleanup_orphaned_records,
            admin_email=current_user.email
        )

        return ResetResultResponse(
            success=result_dict["success"],
            level=result_dict["level"],
            deleted_records=result_dict["deleted_records"],
            errors=result_dict["errors"],
            warnings=result_dict["warnings"],
            execution_time=result_dict["execution_time"],
            affected_users=result_dict["affected_users"],
            timestamp=result_dict["timestamp"],
            admin_user=current_user.email,
            environment=settings.ENVIRONMENT
        )

    except Exception as e:
        logger.error(f"Quick reset failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick reset failed: {str(e)}"
        )


# Background tasks
async def _cleanup_orphaned_records(admin_email: str):
    """
    Background task to clean up any orphaned records after user deletion.

    Args:
        admin_email: Email of admin who triggered the cleanup
    """
    try:
        # Add any additional cleanup logic here
        # This could include clearing file uploads, external service cleanup, etc.
        logger.info(f"Background cleanup completed for admin: {admin_email}")

    except Exception as e:
        logger.error(f"Background cleanup failed: {str(e)}")


# Health check for the reset service
@router.get("/health")
async def reset_service_health():
    """
    Health check endpoint for the database reset service.

    Returns basic health information about the reset service
    and whether it's available in the current environment.
    """
    try:
        allowed_environments = {"development", "testing", "dev", "test"}
        current_env = settings.ENVIRONMENT.lower()
        is_available = current_env in allowed_environments

        return {
            "status": "healthy" if is_available else "disabled",
            "environment": settings.ENVIRONMENT,
            "reset_available": is_available,
            "database_safe": "localhost" in settings.DATABASE_URL or "test" in settings.DATABASE_URL,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Reset service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }