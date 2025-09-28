"""
Secure Authentication Endpoints with Integrated Services
========================================================

Production-ready authentication endpoints using the new dependency injection system
and SecureAuthService with comprehensive security features.

Author: Backend Framework AI
Date: 2025-09-17
Purpose: Secure authentication endpoints with comprehensive DI integration
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

# Updated imports using new dependency injection system
from app.core.dependencies import (
    get_secure_auth_service,
    get_current_user,
    get_current_user_optional,
    get_service_dependencies,
    ServiceDependencies,
    require_user_type
)
from app.core.database import get_db
from app.models.user import User, UserType
from app.services.secure_auth_service import SecureAuthService
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    AuthResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    UserRegistrationRequest
)
from app.core.logger import get_logger

# Configure router and logger
router = APIRouter(prefix="/auth", tags=["authentication"])
logger = get_logger(__name__)
security = HTTPBearer()


# Helper function to extract client information
def get_client_info(request: Request) -> Dict[str, str]:
    """Extract client IP and user agent from request"""
    # Extract IP address
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"

    # Extract user agent
    user_agent = request.headers.get("user-agent", "unknown")

    return {
        "ip_address": client_ip,
        "user_agent": user_agent
    }


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def secure_login(
    login_data: LoginRequest,
    request: Request,
    services: ServiceDependencies = Depends(get_service_dependencies)
) -> TokenResponse:
    """
    Secure user authentication with comprehensive security features.
    Includes brute force protection, audit logging, and token blacklisting.
    """
    logger.info(f"Secure login attempt for email: {login_data.email}")

    # Get client information for security logging
    client_info = get_client_info(request)

    try:
        # Use secure authentication service with comprehensive security
        user = await services.auth_service.authenticate_user(
            db=services.db,
            email=login_data.email,
            password=login_data.password,
            ip_address=client_info["ip_address"],
            user_agent=client_info["user_agent"]
        )

        if not user:
            logger.warning(f"Failed login attempt for email: {login_data.email} from {client_info['ip_address']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Generate secure tokens
        tokens = await services.auth_service.generate_tokens(user)

        # Cache user session
        session_data = {
            "user_id": str(user.id),
            "email": user.email,
            "user_type": user.user_type.value,
            "login_timestamp": "2025-09-17T00:00:00Z",
            "ip_address": client_info["ip_address"]
        }

        try:
            await services.cache.set(
                key=f"session:{user.id}",
                value=session_data,
                ttl=86400  # 24 hours
            )
        except Exception as cache_error:
            logger.warning(f"Cache session storage failed: {cache_error}")

        # Audit log successful login
        await services.audit.log_event(
            event_type="USER_LOGIN_SUCCESS",
            user_id=str(user.id),
            details={
                "email": user.email,
                "ip_address": client_info["ip_address"],
                "user_agent": client_info["user_agent"]
            }
        )

        logger.info(f"Successful secure login for user: {user.email}")

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=30 * 60,  # 30 minutes
            user={
                "id": str(user.id),
                "email": user.email,
                "user_type": user.user_type.value,
                "is_active": user.is_active,
                "full_name": getattr(user, 'full_name', None),
                "phone": getattr(user, 'phone', None)
            }
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Audit log failed login attempt
        await services.audit.log_event(
            event_type="USER_LOGIN_ERROR",
            user_id=None,
            details={
                "email": login_data.email,
                "error": str(e),
                "ip_address": client_info["ip_address"],
                "user_agent": client_info["user_agent"]
            }
        )

        logger.error(f"Secure login error for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/admin-login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def secure_admin_login(
    login_data: LoginRequest,
    request: Request,
    services: ServiceDependencies = Depends(get_service_dependencies)
) -> TokenResponse:
    """
    Secure administrative authentication with enhanced security checks.
    """
    logger.info(f"Admin login attempt for email: {login_data.email}")

    # Get client information
    client_info = get_client_info(request)

    try:
        # Authenticate user
        user = await services.auth_service.authenticate_user(
            db=services.db,
            email=login_data.email,
            password=login_data.password,
            ip_address=client_info["ip_address"],
            user_agent=client_info["user_agent"]
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Verify admin privileges (allow both ADMIN and SUPERUSER)
        if user.user_type not in [UserType.ADMIN, UserType.SUPERUSER]:
            # Audit log unauthorized admin access attempt
            await services.audit.log_event(
                event_type="UNAUTHORIZED_ADMIN_ACCESS",
                user_id=str(user.id),
                details={
                    "email": user.email,
                    "user_type": user.user_type.value,
                    "ip_address": client_info["ip_address"]
                }
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrative privileges required"
            )

        # Generate admin tokens with shorter expiration
        tokens = await services.auth_service.generate_tokens(user)

        # Audit log successful admin login
        await services.audit.log_event(
            event_type="ADMIN_LOGIN_SUCCESS",
            user_id=str(user.id),
            details={
                "email": user.email,
                "ip_address": client_info["ip_address"],
                "user_agent": client_info["user_agent"]
            }
        )

        logger.info(f"Successful admin login for user: {user.email}")

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=15 * 60,  # 15 minutes for admin tokens
            user={
                "id": str(user.id),
                "email": user.email,
                "user_type": user.user_type.value,
                "is_active": user.is_active,
                "admin_privileges": True
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during admin login"
        )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def secure_register(
    registration_data: UserRegistrationRequest,
    request: Request,
    services: ServiceDependencies = Depends(get_service_dependencies)
) -> TokenResponse:
    """
    Secure user registration with password validation and audit logging.
    """
    logger.info(f"Registration attempt for email: {registration_data.email}")

    # Get client information
    client_info = get_client_info(request)

    try:
        # Validate password strength
        is_valid, error_message = await services.auth_service.validate_password_strength(
            registration_data.password
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {error_message}"
            )

        # Create new user
        new_user = await services.auth_service.create_user(
            db=services.db,
            email=registration_data.email,
            password=registration_data.password,
            user_type=getattr(registration_data, 'user_type', UserType.BUYER),
            **{k: v for k, v in registration_data.dict().items()
               if k not in ['email', 'password', 'user_type']}
        )

        # Generate tokens for new user
        tokens = await services.auth_service.generate_tokens(new_user)

        # Audit log successful registration
        await services.audit.log_event(
            event_type="USER_REGISTRATION_SUCCESS",
            user_id=str(new_user.id),
            details={
                "email": new_user.email,
                "user_type": new_user.user_type.value,
                "ip_address": client_info["ip_address"],
                "user_agent": client_info["user_agent"]
            }
        )

        logger.info(f"Successful registration for user: {new_user.email}")

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=30 * 60,
            user={
                "id": str(new_user.id),
                "email": new_user.email,
                "user_type": new_user.user_type.value,
                "is_active": new_user.is_active
            }
        )

    except HTTPException:
        raise
    except ValueError as e:
        # User already exists or other validation error
        await services.audit.log_event(
            event_type="USER_REGISTRATION_FAILED",
            user_id=None,
            details={
                "email": registration_data.email,
                "error": str(e),
                "ip_address": client_info["ip_address"]
            }
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error for {registration_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@router.post("/logout", response_model=AuthResponse)
async def secure_logout(
    logout_data: LogoutRequest,
    request: Request,
    services: ServiceDependencies = Depends(get_service_dependencies),
    current_user: User = Depends(get_current_user)
) -> AuthResponse:
    """
    Securely logout user with token revocation and audit logging.
    """
    logger.info(f"Secure logout attempt for user: {current_user.email}")

    # Get client information
    client_info = get_client_info(request)

    try:
        # Revoke access token if provided
        if logout_data.access_token:
            await services.auth_service.revoke_token(logout_data.access_token)

        # Revoke refresh token if provided
        if logout_data.refresh_token:
            await services.auth_service.revoke_token(logout_data.refresh_token)

        # Remove session from cache
        await services.cache.delete(f"session:{current_user.id}")

        # Audit log successful logout
        await services.audit.log_event(
            event_type="USER_LOGOUT_SUCCESS",
            user_id=str(current_user.id),
            details={
                "email": current_user.email,
                "ip_address": client_info["ip_address"],
                "tokens_revoked": bool(logout_data.access_token or logout_data.refresh_token)
            }
        )

        logger.info(f"Successful secure logout for user: {current_user.email}")

        return AuthResponse(
            success=True,
            message="Successfully logged out with token revocation"
        )

    except Exception as e:
        # Audit log logout error
        await services.audit.log_event(
            event_type="USER_LOGOUT_ERROR",
            user_id=str(current_user.id),
            details={
                "email": current_user.email,
                "error": str(e),
                "ip_address": client_info["ip_address"]
            }
        )

        logger.error(f"Secure logout error for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    services: ServiceDependencies = Depends(get_service_dependencies)
) -> TokenResponse:
    """
    Refresh access token using refresh token with security validation.
    """
    # Get client information
    client_info = get_client_info(request)

    try:
        # Validate refresh token
        payload = await services.auth_service.validate_token(refresh_data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Get user from database
        from sqlalchemy import select
        stmt = select(User).where(User.email == user_email)
        result = await services.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Generate new tokens
        new_tokens = await services.auth_service.generate_tokens(user)

        # Revoke old refresh token
        await services.auth_service.revoke_token(refresh_data.refresh_token)

        # Audit log token refresh
        await services.audit.log_event(
            event_type="TOKEN_REFRESH_SUCCESS",
            user_id=str(user.id),
            details={
                "email": user.email,
                "ip_address": client_info["ip_address"]
            }
        )

        return TokenResponse(
            access_token=new_tokens["access_token"],
            refresh_token=new_tokens["refresh_token"],
            token_type=new_tokens["token_type"],
            expires_in=30 * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current authenticated user information.
    """
    try:
        return {
            "id": str(current_user.id),
            "email": current_user.email,
            "user_type": current_user.user_type.value,
            "is_active": current_user.is_active,
            "full_name": getattr(current_user, 'full_name', None),
            "phone": getattr(current_user, 'phone', None),
            "email_verified": getattr(current_user, 'email_verified', False),
            "phone_verified": getattr(current_user, 'phone_verified', False),
            "created_at": getattr(current_user, 'created_at', None),
            "last_login": getattr(current_user, 'last_login', None)
        }

    except Exception as e:
        logger.error(f"Error getting current user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )


@router.get("/admin/me", response_model=Dict[str, Any])
async def get_admin_user_info(
    current_admin: User = Depends(require_user_type(UserType.ADMIN))
) -> Dict[str, Any]:
    """
    Get current authenticated admin user information with admin-specific data.
    """
    try:
        return {
            "id": str(current_admin.id),
            "email": current_admin.email,
            "user_type": current_admin.user_type.value,
            "is_active": current_admin.is_active,
            "admin_privileges": True,
            "permissions": ["admin_panel", "user_management", "system_monitoring"],
            "full_name": getattr(current_admin, 'full_name', None),
            "created_at": getattr(current_admin, 'created_at', None),
            "last_login": getattr(current_admin, 'last_login', None)
        }

    except Exception as e:
        logger.error(f"Error getting admin user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving admin user information"
        )


@router.post("/validate", response_model=Dict[str, Any])
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    services: ServiceDependencies = Depends(get_service_dependencies)
) -> Dict[str, Any]:
    """
    Validate JWT token and return token information.
    """
    try:
        payload = await services.auth_service.validate_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return {
            "valid": True,
            "token_type": "access",
            "expires_at": payload.get("exp"),
            "user_email": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "user_type": payload.get("user_type")
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )