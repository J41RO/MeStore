#!/usr/bin/env python3
"""
Comprehensive TDD Unit Tests for Secure Authentication Service
============================================================

Testing Strategy:
- RED: Write failing test first
- GREEN: Implement minimal code to pass
- REFACTOR: Optimize while maintaining tests

Coverage Goals:
- Password hashing and verification: 100%
- Authentication flows: 100%
- Brute force protection: 100%
- Token management: 100%
- Security audit logging: 100%

File: tests/unit/services/test_secure_auth_service.py
Author: Unit Testing AI - TDD Methodology
Date: 2025-09-17
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any
import hashlib
import secrets

# Import modules under test
from app.services.secure_auth_service import (
    SecureAuthService,
    SecurityAuditLogger,
    BruteForceProtection,
    TokenBlacklist,
    PasswordValidator
)
from app.models.user import User, UserType


class TestSecurityAuditLogger:
    """Test SecurityAuditLogger with TDD methodology."""

    def test_log_authentication_attempt_success(self):
        """TDD: SecurityAuditLogger should log successful authentication attempts."""
        with patch('app.services.secure_auth_service.logger') as mock_logger:
            SecurityAuditLogger.log_authentication_attempt(
                email="test@example.com",
                success=True,
                ip_address="192.168.1.1",
                user_agent="TestAgent/1.0"
            )

            # Service actually uses .warning() for all auth attempts
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0][0]
            assert "AUTH_SUCCESS" in call_args
            assert "test@example.com" in call_args
            assert "192.168.1.1" in call_args
            assert "TestAgent/1.0" in call_args

    def test_log_authentication_attempt_failure(self):
        """TDD: SecurityAuditLogger should log failed authentication attempts."""
        with patch('app.services.secure_auth_service.logger') as mock_logger:
            SecurityAuditLogger.log_authentication_attempt(
                email="test@example.com",
                success=False,
                ip_address="192.168.1.1"
            )

            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0][0]
            assert "AUTH_FAILURE" in call_args
            assert "test@example.com" in call_args

    def test_log_account_lockout(self):
        """TDD: SecurityAuditLogger should log account lockout events."""
        with patch('app.services.secure_auth_service.logger') as mock_logger:
            SecurityAuditLogger.log_account_lockout(
                email="test@example.com",
                ip_address="192.168.1.1"
            )

            # Service actually uses .critical() for lockout events
            mock_logger.critical.assert_called_once()
            call_args = mock_logger.critical.call_args[0][0]
            assert "ACCOUNT_LOCKOUT" in call_args
            assert "test@example.com" in call_args

    def test_log_password_change(self):
        """TDD: SecurityAuditLogger should log password change events."""
        with patch('app.services.secure_auth_service.logger') as mock_logger:
            SecurityAuditLogger.log_password_change(
                email="test@example.com",
                ip_address="192.168.1.1"
            )

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "PASSWORD_CHANGE" in call_args
            assert "test@example.com" in call_args

    def test_log_token_usage(self):
        """TDD: SecurityAuditLogger should log token usage events."""
        with patch('app.services.secure_auth_service.logger') as mock_logger:
            SecurityAuditLogger.log_token_usage(
                email="test@example.com",
                action="CREATE",
                token_type="access"
            )

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "TOKEN_CREATE" in call_args
            assert "test@example.com" in call_args


class TestPasswordValidation:
    """Test password validation functionality."""

    def test_validate_password_strength_strong_password(self):
        """TDD: Password validation should accept strong passwords."""
        from app.services.secure_auth_service import PasswordValidator

        strong_password = "MyStrong123!Password"
        is_valid, message = PasswordValidator.validate_password_strength(strong_password)

        assert is_valid is True
        assert message == "Password meets security requirements"

    def test_validate_password_strength_too_short(self):
        """TDD: Password validation should reject short passwords."""
        from app.services.secure_auth_service import PasswordValidator

        short_password = "Sh0rt!"
        is_valid, message = PasswordValidator.validate_password_strength(short_password)

        assert is_valid is False
        assert "at least 8 characters" in message

    def test_validate_password_strength_no_uppercase(self):
        """TDD: Password validation should require uppercase letters."""
        from app.services.secure_auth_service import PasswordValidator

        no_upper_password = "lowercase123!"
        is_valid, message = PasswordValidator.validate_password_strength(no_upper_password)

        assert is_valid is False
        assert "uppercase letter" in message

    def test_validate_password_strength_no_lowercase(self):
        """TDD: Password validation should require lowercase letters."""
        from app.services.secure_auth_service import PasswordValidator

        no_lower_password = "UPPERCASE123!"
        is_valid, message = PasswordValidator.validate_password_strength(no_lower_password)

        assert is_valid is False
        assert "lowercase letter" in message

    def test_validate_password_strength_no_digit(self):
        """TDD: Password validation should require digits."""
        from app.services.secure_auth_service import PasswordValidator

        no_digit_password = "NoDigitsHere!"
        is_valid, message = PasswordValidator.validate_password_strength(no_digit_password)

        assert is_valid is False
        assert "number" in message

    def test_validate_password_strength_no_special_char(self):
        """TDD: Password validation should require special characters."""
        from app.services.secure_auth_service import PasswordValidator

        no_special_password = "NoSpecialChars123"
        is_valid, message = PasswordValidator.validate_password_strength(no_special_password)

        assert is_valid is False
        assert "special character" in message


class TestBruteForceProtection:
    """Test BruteForceProtection with TDD methodology."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client for testing."""
        mock_redis = Mock()
        mock_redis.get = Mock(return_value=None)
        mock_redis.set = Mock()
        mock_redis.setex = Mock()
        mock_redis.exists = Mock(return_value=False)
        mock_redis.incr = Mock(return_value=1)  # Return actual int, not MagicMock
        mock_redis.expire = Mock()
        mock_redis.delete = Mock()
        return mock_redis

    def test_brute_force_protection_initialization(self, mock_redis):
        """TDD: BruteForceProtection should initialize with Redis client."""
        protection = BruteForceProtection(redis_client=mock_redis)

        assert protection.redis_client is mock_redis
        assert protection.max_attempts == 5
        assert protection.lockout_duration == 1800  # 30 minutes in service
        assert protection.attempt_window == 900     # 15 minutes

    def test_get_attempt_key_format(self, mock_redis):
        """TDD: BruteForceProtection should generate correct attempt keys with SHA256."""
        protection = BruteForceProtection(redis_client=mock_redis)

        key = protection._get_attempt_key("test@example.com")
        # Service actually uses SHA256 hashing for keys
        expected_hash = hashlib.sha256("test@example.com".encode()).hexdigest()
        assert key == f"auth_attempts:{expected_hash}"

    def test_get_lockout_key_format(self, mock_redis):
        """TDD: BruteForceProtection should generate correct lockout keys with SHA256."""
        protection = BruteForceProtection(redis_client=mock_redis)

        key = protection._get_lockout_key("test@example.com")
        # Service actually uses SHA256 hashing for keys
        expected_hash = hashlib.sha256("test@example.com".encode()).hexdigest()
        assert key == f"auth_lockout:{expected_hash}"

    @pytest.mark.asyncio
    async def test_is_locked_out_not_locked(self, mock_redis):
        """TDD: is_locked_out should return False when account is not locked."""
        mock_redis.exists.return_value = False
        protection = BruteForceProtection(redis_client=mock_redis)

        is_locked = await protection.is_locked_out("test@example.com")

        assert is_locked is False
        # Service uses exists() and SHA256 hashed keys
        expected_hash = hashlib.sha256("test@example.com".encode()).hexdigest()
        expected_key = f"auth_lockout:{expected_hash}"
        mock_redis.exists.assert_called_with(expected_key)

    @pytest.mark.asyncio
    async def test_is_locked_out_currently_locked(self, mock_redis):
        """TDD: is_locked_out should return True when account is locked."""
        mock_redis.exists.return_value = True
        protection = BruteForceProtection(redis_client=mock_redis)

        is_locked = await protection.is_locked_out("test@example.com")

        assert is_locked is True

    @pytest.mark.asyncio
    async def test_record_failed_attempt_under_limit(self, mock_redis):
        """TDD: record_failed_attempt should increment attempts without lockout."""
        mock_redis.incr.return_value = 3  # Return actual int, not MagicMock
        protection = BruteForceProtection(redis_client=mock_redis)

        locked_out = await protection.record_failed_attempt("test@example.com")

        assert locked_out is False
        # Service uses SHA256 hashed keys
        expected_hash = hashlib.sha256("test@example.com".encode()).hexdigest()
        expected_key = f"auth_attempts:{expected_hash}"
        mock_redis.incr.assert_called_with(expected_key)
        mock_redis.expire.assert_called_with(expected_key, 900)

    @pytest.mark.asyncio
    async def test_record_failed_attempt_exceeds_limit(self, mock_redis):
        """TDD: record_failed_attempt should trigger lockout when limit exceeded."""
        mock_redis.incr.return_value = 6  # Return actual int, not MagicMock
        protection = BruteForceProtection(redis_client=mock_redis)

        with patch.object(SecurityAuditLogger, 'log_account_lockout') as mock_log:
            locked_out = await protection.record_failed_attempt("test@example.com", "192.168.1.1")

        assert locked_out is True
        # Service uses setex for lockout with TTL
        assert mock_redis.setex.called  # Lockout key should be set with TTL
        mock_log.assert_called_once_with("test@example.com", "192.168.1.1")

    @pytest.mark.asyncio
    async def test_record_successful_attempt_clears_attempts(self, mock_redis):
        """TDD: record_successful_attempt should clear failed attempt counter."""
        protection = BruteForceProtection(redis_client=mock_redis)

        await protection.record_successful_attempt("test@example.com")

        # Service uses SHA256 hashed keys
        expected_hash = hashlib.sha256("test@example.com".encode()).hexdigest()
        expected_key = f"auth_attempts:{expected_hash}"
        mock_redis.delete.assert_called_with(expected_key)


class TestTokenBlacklist:
    """Test TokenBlacklist with TDD methodology."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client for testing."""
        mock_redis = Mock()
        mock_redis.set = Mock()
        mock_redis.setex = Mock()
        mock_redis.get = Mock(return_value=None)
        mock_redis.exists = Mock(return_value=False)
        return mock_redis

    def test_token_blacklist_initialization(self, mock_redis):
        """TDD: TokenBlacklist should initialize with Redis client."""
        service = TokenBlacklist(redis_client=mock_redis)

        assert service.redis_client is mock_redis

    @pytest.mark.asyncio
    async def test_blacklist_token_with_expiration(self, mock_redis):
        """TDD: blacklist_token should store token with expiration."""
        service = TokenBlacklist(redis_client=mock_redis)
        token = "test.jwt.token"
        expires_at = datetime.utcnow() + timedelta(hours=1)

        await service.blacklist_token(token, expires_at)

        # Service uses setex with TTL
        assert mock_redis.setex.called
        call_args = mock_redis.setex.call_args
        expected_key = f"blacklist_token:{hashlib.sha256(token.encode()).hexdigest()}"
        assert expected_key == call_args[0][0]

    @pytest.mark.asyncio
    async def test_blacklist_token_without_expiration(self, mock_redis):
        """TDD: blacklist_token should handle tokens without expiration."""
        service = TokenBlacklist(redis_client=mock_redis)
        token = "test.jwt.token"

        await service.blacklist_token(token)

        # Service uses setex even without expiration (default TTL)
        assert mock_redis.setex.called

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_not_blacklisted(self, mock_redis):
        """TDD: is_token_blacklisted should return False for valid tokens."""
        mock_redis.exists.return_value = False
        service = TokenBlacklist(redis_client=mock_redis)
        token = "test.jwt.token"

        is_blacklisted = await service.is_token_blacklisted(token)

        assert is_blacklisted is False

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_currently_blacklisted(self, mock_redis):
        """TDD: is_token_blacklisted should return True for blacklisted tokens."""
        mock_redis.exists.return_value = True
        service = TokenBlacklist(redis_client=mock_redis)
        token = "test.jwt.token"

        is_blacklisted = await service.is_token_blacklisted(token)

        assert is_blacklisted is True


class TestSecureAuthService:
    """Test SecureAuthService main class with TDD methodology."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_user(self):
        """Mock user object with proper synchronous attributes."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.password_hash = "$2b$12$hash"
        user.user_type = UserType.BUYER
        user.is_active = True  # Ensure this is not a coroutine
        user.failed_login_attempts = 0
        user.locked_until = None
        # Configure mock to return actual values, not coroutines
        type(user).is_active = Mock(return_value=True)
        return user

    @pytest.fixture
    def auth_service(self):
        """SecureAuthService instance for testing."""
        with patch('app.services.secure_auth_service.redis.Redis'):
            return SecureAuthService()

    def test_secure_auth_service_initialization(self, auth_service):
        """TDD: SecureAuthService should initialize with all components."""
        assert auth_service.pwd_context is not None
        assert auth_service.brute_force_protection is not None
        assert auth_service.token_blacklist is not None

    @pytest.mark.asyncio
    async def test_verify_password_correct_password(self, auth_service):
        """TDD: verify_password should return True for correct passwords."""
        plain_password = "testpassword123"
        # Use the actual password context to create a real hash
        hashed_password = auth_service.pwd_context.hash(plain_password)

        result = await auth_service.verify_password(plain_password, hashed_password)

        assert result is True

    @pytest.mark.asyncio
    async def test_verify_password_incorrect_password(self, auth_service):
        """TDD: verify_password should return False for incorrect passwords."""
        plain_password = "wrongpassword"
        hashed_password = auth_service.pwd_context.hash("correctpassword")

        result = await auth_service.verify_password(plain_password, hashed_password)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_password_hash_generates_valid_hash(self, auth_service):
        """TDD: get_password_hash should generate valid bcrypt hashes for strong passwords."""
        password = "StrongPassword123!"  # Must meet validation requirements

        hashed = await auth_service.get_password_hash(password)

        assert hashed.startswith("$2b$")
        assert len(hashed) > 50  # Bcrypt hashes are typically 60 characters

    @pytest.mark.asyncio
    async def test_validate_password_strength_integration(self, auth_service):
        """TDD: validate_password_strength should work with async interface."""
        strong_password = "StrongPass123!"

        is_valid, message = await auth_service.validate_password_strength(strong_password)

        assert is_valid is True
        assert "meets security requirements" in message

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_db, mock_user):
        """TDD: authenticate_user should return user for valid credentials."""
        email = "test@example.com"
        password = "StrongPassword123!"

        # Mock database query - ensure scalar_one_or_none returns the mock_user synchronously
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_user)  # Synchronous return
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Mock password verification to return True directly
        with patch.object(auth_service, 'verify_password', new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = True
            with patch.object(auth_service.brute_force_protection, 'is_locked_out', new_callable=AsyncMock) as mock_is_locked:
                mock_is_locked.return_value = False
                with patch.object(auth_service.brute_force_protection, 'record_successful_attempt', new_callable=AsyncMock) as mock_record_success:
                    mock_record_success.return_value = None
                    result = await auth_service.authenticate_user(mock_db, email, password)

        assert result is mock_user

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_credentials(self, auth_service, mock_db, mock_user):
        """TDD: authenticate_user should return None for invalid credentials."""
        email = "test@example.com"
        password = "wrongpassword"

        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        # Mock password verification failure
        with patch.object(auth_service, 'verify_password', return_value=False):
            with patch.object(auth_service.brute_force_protection, 'is_locked_out', return_value=False):
                with patch.object(auth_service.brute_force_protection, 'record_failed_attempt', return_value=False):
                    result = await auth_service.authenticate_user(mock_db, email, password)

        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_account_locked(self, auth_service, mock_db):
        """TDD: authenticate_user should return None for locked accounts."""
        email = "test@example.com"
        password = "testpassword123"

        # Mock account lockout
        with patch.object(auth_service.brute_force_protection, 'is_locked_out', return_value=True):
            result = await auth_service.authenticate_user(mock_db, email, password)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_user_success(self, auth_service, mock_db):
        """TDD: create_user should create new user with hashed password."""
        user_data = {
            "email": "newuser@example.com",
            "password": "StrongPass123!",
            "nombre": "Test",
            "apellido": "User",
            "user_type": UserType.BUYER
        }

        # Mock the database query to check for existing user (return None = no existing user)
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)  # No existing user
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch.object(auth_service, 'validate_password_strength', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = (True, "Valid")
            with patch.object(auth_service, 'get_password_hash', new_callable=AsyncMock) as mock_hash:
                mock_hash.return_value = "$2b$12$hashedpassword"
                # Mock user creation operations
                mock_db.add = Mock()
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()

                user = await auth_service.create_user(
                    mock_db,
                    user_data["email"],
                    user_data["password"],
                    user_data["user_type"],
                    **{"nombre": user_data["nombre"], "apellido": user_data["apellido"]}
                )

                assert user.email == "newuser@example.com"
                assert user.password_hash == "$2b$12$hashedpassword"
                mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_tokens_creates_valid_tokens(self, auth_service, mock_user):
        """TDD: generate_tokens should create access and refresh tokens."""
        with patch('app.services.secure_auth_service.create_access_token', return_value="access.token"):
            with patch('app.services.secure_auth_service.create_refresh_token', return_value="refresh.token"):
                tokens = await auth_service.generate_tokens(mock_user)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["access_token"] == "access.token"
        assert tokens["refresh_token"] == "refresh.token"

    @pytest.mark.asyncio
    async def test_revoke_token_blacklists_token(self, auth_service):
        """TDD: revoke_token should add token to blacklist."""
        token = "test.jwt.token"
        mock_payload = {"sub": "test@example.com", "exp": 1234567890}

        with patch('app.services.secure_auth_service.decode_access_token', return_value=mock_payload):
            with patch.object(auth_service.token_blacklist, 'blacklist_token', new_callable=AsyncMock) as mock_blacklist:
                mock_blacklist.return_value = None
                await auth_service.revoke_token(token)

            mock_blacklist.assert_called_once()  # Token and expires_at are passed, but we just verify it's called

    @pytest.mark.asyncio
    async def test_validate_token_valid_token(self, auth_service):
        """TDD: validate_token should return payload for valid tokens."""
        token = "valid.jwt.token"
        expected_payload = {"sub": "1", "email": "test@example.com"}

        with patch.object(auth_service.token_blacklist, 'is_token_blacklisted', return_value=False):
            with patch('app.services.secure_auth_service.decode_access_token', return_value=expected_payload):
                payload = await auth_service.validate_token(token)

        assert payload == expected_payload

    @pytest.mark.asyncio
    async def test_validate_token_blacklisted_token(self, auth_service):
        """TDD: validate_token should raise ValueError for blacklisted tokens."""
        token = "blacklisted.jwt.token"

        with patch.object(auth_service.token_blacklist, 'is_token_blacklisted', new_callable=AsyncMock) as mock_is_blacklisted:
            mock_is_blacklisted.return_value = True
            with pytest.raises(ValueError, match="Token has been revoked"):
                await auth_service.validate_token(token)


class TestSecureAuthServicePerformance:
    """Performance tests for SecureAuthService."""

    @pytest.fixture
    def auth_service(self):
        """SecureAuthService instance for testing."""
        with patch('app.services.secure_auth_service.redis.Redis'):
            return SecureAuthService()

    @pytest.mark.asyncio
    async def test_password_hashing_performance(self, auth_service):
        """TDD: Password hashing should be performant but secure."""
        import time

        password = "StrongTestPassword123!"  # Use a strong password that passes validation
        start_time = time.time()

        hashed = await auth_service.get_password_hash(password)

        end_time = time.time()
        duration = end_time - start_time

        # Password hashing should take reasonable time (bcrypt is intentionally slow)
        assert duration < 1.0  # Should complete within 1 second
        assert hashed is not None
        assert len(hashed) > 50

    @pytest.mark.asyncio
    async def test_password_verification_performance(self, auth_service):
        """TDD: Password verification should be reasonably fast."""
        import time

        password = "StrongTestPassword123!"  # Use a strong password
        hashed = auth_service.pwd_context.hash(password)

        start_time = time.time()

        result = await auth_service.verify_password(password, hashed)

        end_time = time.time()
        duration = end_time - start_time

        # Verification should be faster than hashing
        assert duration < 0.5  # Should complete within 500ms
        assert result is True


if __name__ == "__main__":
    # Run with: python -m pytest tests/unit/services/test_secure_auth_service.py -v
    pytest.main([__file__, "-v", "--tb=short", "--cov=app.services.secure_auth_service"])