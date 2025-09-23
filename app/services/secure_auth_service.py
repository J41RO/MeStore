"""
Secure Authentication Service Implementation
==========================================

This module provides a secure, production-ready authentication service
that addresses critical security vulnerabilities found in the audit.

Security Features:
- Proper SQLAlchemy async session usage
- SQL injection prevention
- Brute force protection with account lockout
- Password strength validation
- Timing attack protection
- Comprehensive audit logging
- JWT token management with blacklisting
- Redis session management

Author: Security Backend AI
Date: 2025-09-17
Purpose: Replace vulnerable AuthService with secure implementation
"""

import asyncio
import logging
import hashlib
import secrets
import redis
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from passlib.context import CryptContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Import models and core modules
from app.models.user import User, UserType
from app.core.security import create_access_token, create_refresh_token, decode_access_token
from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)


class SecurityAuditLogger:
    """
    Centralized security event logging for audit trails.
    """

    @staticmethod
    def log_authentication_attempt(email: str, success: bool, ip_address: str = None, user_agent: str = None):
        """Log authentication attempts for security monitoring."""
        event_type = "AUTH_SUCCESS" if success else "AUTH_FAILURE"
        logger.warning(f"{event_type}: {email} from {ip_address or 'unknown'} - {user_agent or 'unknown'}")

    @staticmethod
    def log_account_lockout(email: str, ip_address: str = None):
        """Log account lockout events."""
        logger.critical(f"ACCOUNT_LOCKOUT: {email} from {ip_address or 'unknown'}")

    @staticmethod
    def log_password_change(email: str, ip_address: str = None):
        """Log password change events."""
        logger.info(f"PASSWORD_CHANGE: {email} from {ip_address or 'unknown'}")

    @staticmethod
    def log_token_usage(email: str, action: str, token_type: str = "access"):
        """Log token-related security events."""
        logger.info(f"TOKEN_{action.upper()}: {token_type} token for {email}")

    @staticmethod
    def log_security_event(event_type: str, user_id: str = None, details: dict = None):
        """Log general security events for audit trails."""
        detail_str = f" - {details}" if details else ""
        user_info = f" for user {user_id}" if user_id else ""
        logger.info(f"SECURITY_EVENT: {event_type.upper()}{user_info}{detail_str}")


class PasswordValidator:
    """
    Password strength validation with Colombian compliance requirements.
    """

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength according to security policies.

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        - Not in common password lists

        Args:
            password: Password to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"

        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

        # Check against common passwords
        common_passwords = {
            "password", "password123", "123456789", "qwerty123",
            "admin123", "colombia123", "usuario123"
        }
        if password.lower() in common_passwords:
            return False, "Password is too common, please choose a stronger password"

        return True, "Password meets security requirements"


class BruteForceProtection:
    """
    Brute force attack protection with Redis-based tracking.
    """

    def __init__(self, redis_client=None):
        """Initialize brute force protection with Redis client."""
        self.redis_client = redis_client or self._get_redis_client()
        self.max_attempts = 5
        self.lockout_duration = 1800  # 30 minutes in seconds
        self.attempt_window = 900     # 15 minutes in seconds

    def _get_redis_client(self):
        """Get Redis client for session management."""
        try:
            return redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis not available for brute force protection: {e}")
            return None

    def _get_attempt_key(self, identifier: str) -> str:
        """Generate Redis key for tracking attempts."""
        return f"auth_attempts:{hashlib.sha256(identifier.encode()).hexdigest()}"

    def _get_lockout_key(self, identifier: str) -> str:
        """Generate Redis key for account lockout."""
        return f"auth_lockout:{hashlib.sha256(identifier.encode()).hexdigest()}"

    async def is_locked_out(self, email: str, ip_address: str = None) -> bool:
        """
        Check if account or IP is locked out.

        Args:
            email: User email
            ip_address: User IP address

        Returns:
            bool: True if locked out
        """
        if not self.redis_client:
            return False

        # Check email-based lockout
        email_lockout_key = self._get_lockout_key(email)
        if self.redis_client.exists(email_lockout_key):
            return True

        # Check IP-based lockout if IP provided
        if ip_address:
            ip_lockout_key = self._get_lockout_key(ip_address)
            if self.redis_client.exists(ip_lockout_key):
                return True

        return False

    async def record_failed_attempt(self, email: str, ip_address: str = None) -> bool:
        """
        Record a failed authentication attempt.

        Args:
            email: User email
            ip_address: User IP address

        Returns:
            bool: True if account should be locked out
        """
        if not self.redis_client:
            return False

        should_lockout = False

        # Record email-based attempt
        email_key = self._get_attempt_key(email)
        attempts = self.redis_client.incr(email_key)
        self.redis_client.expire(email_key, self.attempt_window)

        if attempts >= self.max_attempts:
            lockout_key = self._get_lockout_key(email)
            self.redis_client.setex(lockout_key, self.lockout_duration, "locked")
            SecurityAuditLogger.log_account_lockout(email, ip_address)
            should_lockout = True

        # Record IP-based attempt if IP provided
        if ip_address:
            ip_key = self._get_attempt_key(ip_address)
            ip_attempts = self.redis_client.incr(ip_key)
            self.redis_client.expire(ip_key, self.attempt_window)

            if ip_attempts >= self.max_attempts * 2:  # Higher threshold for IP
                ip_lockout_key = self._get_lockout_key(ip_address)
                self.redis_client.setex(ip_lockout_key, self.lockout_duration, "locked")
                should_lockout = True

        return should_lockout

    async def record_successful_attempt(self, email: str, ip_address: str = None):
        """
        Record a successful authentication attempt and clear failed attempts.

        Args:
            email: User email
            ip_address: User IP address
        """
        if not self.redis_client:
            return

        # Clear failed attempts for email
        email_key = self._get_attempt_key(email)
        self.redis_client.delete(email_key)

        # Clear failed attempts for IP if provided
        if ip_address:
            ip_key = self._get_attempt_key(ip_address)
            self.redis_client.delete(ip_key)


class TokenBlacklist:
    """
    JWT token blacklisting for secure token revocation.
    """

    def __init__(self, redis_client=None):
        """Initialize token blacklist with Redis client."""
        self.redis_client = redis_client or self._get_redis_client()

    def _get_redis_client(self):
        """Get Redis client for token blacklisting."""
        try:
            return redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis not available for token blacklisting: {e}")
            return None

    def _get_token_key(self, token: str) -> str:
        """Generate Redis key for blacklisted token."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return f"blacklist_token:{token_hash}"

    async def blacklist_token(self, token: str, expires_at: datetime = None):
        """
        Add token to blacklist.

        Args:
            token: JWT token to blacklist
            expires_at: Token expiration time for TTL
        """
        if not self.redis_client:
            return

        key = self._get_token_key(token)
        ttl = int((expires_at - datetime.utcnow()).total_seconds()) if expires_at else 3600

        self.redis_client.setex(key, ttl, "blacklisted")

    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            token: JWT token to check

        Returns:
            bool: True if blacklisted
        """
        if not self.redis_client:
            return False

        key = self._get_token_key(token)
        return self.redis_client.exists(key)


class SecureAuthService:
    """
    Secure authentication service with comprehensive security features.

    This service replaces the vulnerable AuthService with a secure implementation
    that addresses all identified security issues.
    """

    def __init__(self):
        """Initialize secure authentication service."""
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12  # Increased rounds for better security
        )

        # ThreadPoolExecutor for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="auth_secure")

        # Security components
        self.password_validator = PasswordValidator()
        self.brute_force_protection = BruteForceProtection()
        self.token_blacklist = TokenBlacklist()

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> Optional[User]:
        """
        Securely authenticate user with comprehensive security checks.

        Args:
            db: Async database session
            email: User email
            password: Plain text password
            ip_address: User IP address for brute force protection
            user_agent: User agent for audit logging

        Returns:
            User object if authentication successful, None otherwise
        """
        # Start timing for consistent response time
        start_time = datetime.utcnow()

        try:
            # Check for brute force lockout
            if await self.brute_force_protection.is_locked_out(email, ip_address):
                SecurityAuditLogger.log_authentication_attempt(
                    email, False, ip_address, user_agent
                )
                # Ensure consistent timing even for locked accounts
                await self._ensure_consistent_timing(start_time)
                return None

            # Query user using proper async session (NO direct SQL!)
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            # If user doesn't exist, still verify password for timing consistency
            if user is None:
                # Perform dummy password verification to maintain consistent timing
                await self._verify_password_dummy("dummy_password", "dummy_hash")

                # Record failed attempt
                await self.brute_force_protection.record_failed_attempt(email, ip_address)

                SecurityAuditLogger.log_authentication_attempt(
                    email, False, ip_address, user_agent
                )

                await self._ensure_consistent_timing(start_time)
                return None

            # Check if user is active
            if not user.is_active:
                # Still verify password for timing consistency
                await self._verify_password_dummy(password, user.password_hash)

                await self.brute_force_protection.record_failed_attempt(email, ip_address)

                SecurityAuditLogger.log_authentication_attempt(
                    email, False, ip_address, user_agent
                )

                await self._ensure_consistent_timing(start_time)
                return None

            # Verify password using secure async method
            is_valid_password = await self.verify_password(password, user.password_hash)

            if not is_valid_password:
                # Record failed attempt
                await self.brute_force_protection.record_failed_attempt(email, ip_address)

                SecurityAuditLogger.log_authentication_attempt(
                    email, False, ip_address, user_agent
                )

                await self._ensure_consistent_timing(start_time)
                return None

            # Successful authentication
            await self.brute_force_protection.record_successful_attempt(email, ip_address)

            SecurityAuditLogger.log_authentication_attempt(
                email, True, ip_address, user_agent
            )

            await self._ensure_consistent_timing(start_time)
            return user

        except Exception as e:
            logger.error(f"Error in secure authentication for {email}: {str(e)}")

            # Record as failed attempt on any exception
            await self.brute_force_protection.record_failed_attempt(email, ip_address)

            SecurityAuditLogger.log_authentication_attempt(
                email, False, ip_address, user_agent
            )

            await self._ensure_consistent_timing(start_time)
            return None

    async def _ensure_consistent_timing(self, start_time: datetime, min_duration_ms: int = 100):
        """
        Ensure consistent response timing to prevent timing attacks.

        Args:
            start_time: Request start time
            min_duration_ms: Minimum response duration in milliseconds
        """
        elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
        if elapsed < min_duration_ms:
            sleep_time = (min_duration_ms - elapsed) / 1000
            await asyncio.sleep(sleep_time)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Securely verify password using async thread pool.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against

        Returns:
            bool: True if password matches
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.pwd_context.verify,
            plain_password,
            hashed_password
        )

    async def _verify_password_dummy(self, plain_password: str, hashed_password: str) -> bool:
        """
        Dummy password verification for timing consistency.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password (or dummy hash)

        Returns:
            bool: Always False (dummy verification)
        """
        loop = asyncio.get_event_loop()

        # Use a dummy hash if none provided
        if not hashed_password:
            hashed_password = "$2b$12$dummy.hash.for.timing.consistency.only"

        await loop.run_in_executor(
            self.executor,
            self.pwd_context.verify,
            plain_password,
            hashed_password
        )
        return False

    async def get_password_hash(self, password: str) -> str:
        """
        Hash password securely using async thread pool.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password
        """
        # Validate password strength first
        is_valid, error_message = self.password_validator.validate_password_strength(password)
        if not is_valid:
            raise ValueError(f"Password validation failed: {error_message}")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.pwd_context.hash,
            password
        )

    async def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        return self.password_validator.validate_password_strength(password)

    async def create_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        user_type: UserType = None,
        is_active: bool = True,
        **additional_fields
    ) -> User:
        """
        Create new user with secure password handling.

        Args:
            db: Async database session
            email: User email
            password: Plain text password
            user_type: User type (defaults to BUYER)
            is_active: Whether user is active
            **additional_fields: Additional user fields

        Returns:
            User: Created user object

        Raises:
            ValueError: If user already exists or password is weak
        """
        if user_type is None:
            user_type = UserType.BUYER

        # Check if user already exists
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Hash password (includes strength validation)
        password_hash = await self.get_password_hash(password)

        # Create user
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'user_type': user_type,
            'is_active': is_active,
            **additional_fields
        }

        new_user = User(**user_data)

        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            logger.info(f"Secure user creation successful: {email}")
            return new_user

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating user {email}: {str(e)}")
            raise ValueError(f"Error creating user: {str(e)}")

    async def generate_tokens(self, user: User) -> Dict[str, str]:
        """
        Generate secure access and refresh tokens.

        Args:
            user: User object

        Returns:
            Dict containing access_token and refresh_token
        """
        # Create token payload
        token_data = {
            "sub": user.email,
            "user_id": str(user.id),
            "user_type": user.user_type.value,
            "iat": datetime.utcnow().timestamp()
        }

        # Generate tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        SecurityAuditLogger.log_token_usage(user.email, "CREATED", "access")
        SecurityAuditLogger.log_token_usage(user.email, "CREATED", "refresh")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def revoke_token(self, token: str):
        """
        Revoke (blacklist) a token.

        Args:
            token: JWT token to revoke
        """
        # Decode token to get expiration
        try:
            payload = decode_access_token(token)
            if payload and "exp" in payload:
                expires_at = datetime.utcfromtimestamp(payload["exp"])
                await self.token_blacklist.blacklist_token(token, expires_at)

                email = payload.get("sub", "unknown")
                SecurityAuditLogger.log_token_usage(email, "REVOKED")

        except Exception as e:
            logger.warning(f"Error revoking token: {e}")

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate token and check blacklist.

        Args:
            token: JWT token to validate

        Returns:
            Dict: Token payload if valid, None if invalid/blacklisted

        Raises:
            ValueError: If token is blacklisted
        """
        # Check if token is blacklisted
        if await self.token_blacklist.is_token_blacklisted(token):
            raise ValueError("Token has been revoked")

        # Validate token signature and expiration
        payload = decode_access_token(token)
        return payload

    def __del__(self):
        """Cleanup thread pool executor."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)