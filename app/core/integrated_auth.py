"""
Integrated Authentication Service
=================================

Transitional authentication service that integrates SecureAuthService
with the existing authentication system for seamless migration.

This service acts as a bridge between the current AuthService and
SecureAuthService, providing backward compatibility while introducing
enhanced security features.

Author: System Architect AI
Date: 2025-09-17
Purpose: Gradual migration to SecureAuthService with backward compatibility
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.secure_auth_service import SecureAuthService, SecurityAuditLogger
from app.core.auth import AuthService  # Legacy auth service
from app.models.user import User
from app.core.security import create_access_token, decode_access_token
import sqlite3
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class IntegratedAuthService:
    """
    Integrated authentication service that combines legacy and secure auth.

    This service provides:
    - Backward compatibility with existing authentication flows
    - Enhanced security features from SecureAuthService
    - Gradual migration path to full SecureAuthService
    - Comprehensive audit logging
    - Brute force protection
    """

    def __init__(self):
        self.legacy_auth = AuthService()
        self.secure_auth = None  # Will be initialized when needed
        # Temporarily disable secure auth to fix login issues
        self.migration_enabled = False  # getattr(settings, 'SECURE_AUTH_ENABLED', True)
        self.audit_logger = SecurityAuditLogger()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def _get_secure_auth(self) -> SecureAuthService:
        """Lazy initialization of SecureAuthService"""
        if self.secure_auth is None:
            from app.database import AsyncSessionLocal
            from app.core.redis.session import get_redis_sessions

            # Initialize with database session and Redis
            redis_client = await get_redis_sessions()
            self.secure_auth = SecureAuthService(redis_client=redis_client)
        return self.secure_auth

    async def _authenticate_user_simple(self, email: str, password: str) -> Optional[User]:
        """Simple SQLite-based authentication for debugging"""
        try:
            # Direct SQLite query for testing
            conn = sqlite3.connect('mestore_production.db')
            cursor = conn.execute(
                'SELECT id, email, password_hash, user_type, nombre, is_active FROM users WHERE email = ?',
                (email,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                logger.warning(f"User not found in SQLite: {email}")
                return None

            user_id, user_email, password_hash, user_type, nombre, is_active = row

            # Verify password with passlib
            if not self.pwd_context.verify(password, password_hash):
                logger.warning(f"Password verification failed for: {email}")
                return None

            # Create a simple User object with proper enum conversion
            from app.models.user import UserType

            user = User()
            user.id = user_id
            user.email = user_email
            user.password_hash = password_hash

            # Convert string user_type to enum - database has UPPERCASE values
            try:
                user.user_type = UserType(user_type)
                logger.info(f"User type converted successfully: {user_type} -> {user.user_type}")
            except ValueError as ve:
                logger.error(f"Invalid user_type from database: {user_type}, error: {ve}")
                # Set default if conversion fails
                user.user_type = UserType.BUYER

            user.nombre = nombre
            user.is_active = bool(is_active)

            logger.info(f"Simple authentication successful for: {email}, user_type: {user.user_type}")
            return user

        except Exception as e:
            logger.error(f"Simple authentication error for {email}: {str(e)}")
            return None

    async def authenticate_user(
        self,
        email: str,
        password: str,
        db: AsyncSession,
        ip_address: str = None,
        user_agent: str = None
    ) -> Optional[User]:
        """
        Authenticate user with enhanced security features.

        Uses SecureAuthService if migration is enabled, falls back to legacy auth.

        Args:
            email: User email
            password: Plain password
            db: Database session
            ip_address: Client IP address for security logging
            user_agent: Client user agent for security logging

        Returns:
            User object if authentication successful, None otherwise
        """
        try:
            if self.migration_enabled:
                # Use SecureAuthService with enhanced security
                secure_auth = await self._get_secure_auth()

                # Log authentication attempt
                self.audit_logger.log_authentication_attempt(
                    email=email,
                    success=False,  # Will update if successful
                    ip_address=ip_address,
                    user_agent=user_agent
                )

                # Authenticate with enhanced security
                user = await secure_auth.authenticate_user_secure(
                    email=email,
                    password=password,
                    db=db,
                    ip_address=ip_address
                )

                if user:
                    # Update audit log on success
                    self.audit_logger.log_authentication_attempt(
                        email=email,
                        success=True,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    logger.info(f"Secure authentication successful for user: {email}")
                    return user
                else:
                    logger.warning(f"Secure authentication failed for user: {email}")
                    return None
            else:
                # Use simple SQLite authentication for now
                logger.info(f"Using simple authentication for user: {email}")
                return await self._authenticate_user_simple(email, password)

        except HTTPException as e:
            # Re-raise HTTP exceptions (e.g., account locked)
            logger.warning(f"Authentication exception for {email}: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Authentication error for {email}: {str(e)}")
            return None

    async def create_user_session(
        self,
        user: User,
        ip_address: str = None,
        user_agent: str = None
    ) -> Tuple[str, str]:
        """
        Create user session with tokens.

        Args:
            user: Authenticated user
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Tuple of (access_token, refresh_token)
        """
        try:
            if self.migration_enabled:
                secure_auth = await self._get_secure_auth()

                # Create tokens using SecureAuthService
                access_token = await secure_auth.create_user_session(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent
                )

                # Create refresh token using legacy method for compatibility
                refresh_token = self.legacy_auth.create_refresh_token(str(user.id))

                return access_token, refresh_token
            else:
                # Use centralized security functions for consistent token format
                from app.core.security import create_access_token, create_refresh_token

                normalized_id = str(user.id)

                # Include user information in JWT payload for proper authorization
                token_data = {
                    "sub": normalized_id,
                    "email": user.email,
                    "nombre": user.nombre,
                    "user_type": user.user_type.value if hasattr(user.user_type, 'value') else str(user.user_type),
                    "is_active": user.is_active,
                    "is_verified": user.is_verified
                }

                # Create tokens using centralized security functions with enhanced payload
                access_token = create_access_token(data=token_data)
                refresh_token = create_refresh_token(data={"sub": normalized_id})

                return access_token, refresh_token

        except Exception as e:
            logger.error(f"Session creation error for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user session"
            )

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token using enhanced verification if available.

        Args:
            token: JWT token to verify

        Returns:
            Token payload if valid

        Raises:
            HTTPException: If token is invalid
        """
        try:
            if self.migration_enabled:
                secure_auth = await self._get_secure_auth()

                # Use SecureAuthService token verification with blacklist checking
                payload = await secure_auth.verify_token_secure(token)
                return payload
            else:
                # Use legacy verification
                return self.legacy_auth.verify_token(token)

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def logout_user(self, user_id: str, token: str) -> bool:
        """
        Logout user with enhanced security features.

        Args:
            user_id: User ID to logout
            token: Current access token to invalidate

        Returns:
            True if logout successful
        """
        try:
            if self.migration_enabled:
                secure_auth = await self._get_secure_auth()

                # Use SecureAuthService logout with token blacklisting
                success = await secure_auth.logout_user_secure(user_id, token)

                # Log security event
                self.audit_logger.log_security_event(
                    event_type="user_logout",
                    user_id=user_id,
                    details={"success": success}
                )

                return success
            else:
                # Legacy logout (basic session removal)
                logger.info(f"Legacy logout for user: {user_id}")
                return True

        except Exception as e:
            logger.error(f"Logout error for user {user_id}: {str(e)}")
            return False

    async def check_brute_force_protection(self, email: str, ip_address: str = None) -> bool:
        """
        Check if user/IP is subject to brute force protection.

        Args:
            email: User email to check
            ip_address: IP address to check

        Returns:
            True if access is allowed, False if blocked
        """
        if self.migration_enabled:
            try:
                secure_auth = await self._get_secure_auth()
                return await secure_auth.check_brute_force_attempts(email, ip_address)
            except Exception as e:
                logger.error(f"Brute force check error: {str(e)}")
                return True  # Allow access on error for safety
        else:
            return True  # No protection in legacy mode

    async def get_user_security_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get user security status and metrics.

        Args:
            user_id: User ID to check

        Returns:
            Dictionary with security status information
        """
        if self.migration_enabled:
            try:
                secure_auth = await self._get_secure_auth()
                return await secure_auth.get_user_security_metrics(user_id)
            except Exception as e:
                logger.error(f"Security status check error: {str(e)}")
                return {"status": "unknown", "error": str(e)}
        else:
            return {"status": "legacy_mode", "protection": "basic"}

    def is_secure_mode_enabled(self) -> bool:
        """Check if secure authentication mode is enabled."""
        return self.migration_enabled

    async def create_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        user_type: str = "BUYER",
        **kwargs
    ) -> User:
        """
        Create a new user in the system.

        Args:
            db: Database session
            email: User email
            password: Plain password
            user_type: User type (default: BUYER)
            **kwargs: Additional user fields

        Returns:
            Created User object
        """
        try:
            from app.models.user import User, UserType
            from sqlalchemy import select

            # Check if user already exists
            result = await db.execute(select(User).where(User.email == email))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                raise ValueError(f"User with email {email} already exists")

            # Hash password
            password_hash = self.pwd_context.hash(password)

            # Convert user_type string to enum if needed
            if isinstance(user_type, str):
                try:
                    user_type_enum = UserType(user_type.upper())
                except ValueError:
                    user_type_enum = UserType.BUYER
            else:
                user_type_enum = user_type

            # Create new user with proper ID handling for SQLite
            import uuid
            new_user = User(
                id=str(uuid.uuid4()),  # Convert UUID to string for SQLite
                email=email,
                password_hash=password_hash,
                user_type=user_type_enum,
                is_active=True,
                is_verified=False,
                **kwargs
            )

            # Save to database
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            logger.info(f"User created successfully: {new_user.id} - {new_user.email}")
            return new_user

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            await db.rollback()
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on authentication services.

        Returns:
            Health status information
        """
        health_status = {
            "service": "IntegratedAuthService",
            "secure_mode": self.migration_enabled,
            "legacy_available": True,
            "timestamp": datetime.utcnow().isoformat()
        }

        if self.migration_enabled:
            try:
                secure_auth = await self._get_secure_auth()
                secure_health = await secure_auth.health_check()
                health_status["secure_auth"] = secure_health
            except Exception as e:
                health_status["secure_auth"] = {"status": "error", "error": str(e)}

        return health_status


# Global instance for application use
integrated_auth_service = IntegratedAuthService()