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

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "AUTHENTICATION_SUCCESS" in call_args
            assert "test@example.com" in call_args

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
            assert "AUTHENTICATION_FAILURE" in call_args
            assert "test@example.com" in call_args

    def test_log_account_lockout(self):
        """TDD: SecurityAuditLogger should log account lockout events."""
        with patch('app.services.secure_auth_service.logger') as mock_logger:
            SecurityAuditLogger.log_account_lockout(
                email="test@example.com",
                ip_address="192.168.1.1"
            )

            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args[0][0]
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
        assert message == "Password meets all security requirements"

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
        assert "digit" in message

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
        mock_redis.incr = Mock(return_value=1)
        mock_redis.expire = Mock()
        mock_redis.delete = Mock()
        return mock_redis

    def test_brute_force_protection_initialization(self, mock_redis):
        """TDD: BruteForceProtection should initialize with Redis client."""
        protection = BruteForceProtection(redis_client=mock_redis)

        assert protection.redis_client is mock_redis
        assert protection.max_attempts == 5
        assert protection.lockout_duration == 900  # 15 minutes

    def test_get_attempt_key_format(self, mock_redis):
        """TDD: BruteForceProtection should generate correct attempt keys."""
        protection = BruteForceProtection(redis_client=mock_redis)

        key = protection._get_attempt_key("test@example.com")
        assert key == "auth_attempts:test@example.com"

    def test_get_lockout_key_format(self, mock_redis):
        """TDD: BruteForceProtection should generate correct lockout keys."""
        protection = BruteForceProtection(redis_client=mock_redis)

        key = protection._get_lockout_key("test@example.com")
        assert key == "auth_lockout:test@example.com"

    @pytest.mark.asyncio
    async def test_is_locked_out_not_locked(self, mock_redis):
        """TDD: is_locked_out should return False when account is not locked."""
        mock_redis.get.return_value = None
        protection = BruteForceProtection(redis_client=mock_redis)

        is_locked = await protection.is_locked_out("test@example.com")

        assert is_locked is False
        mock_redis.get.assert_called_with("auth_lockout:test@example.com")

    @pytest.mark.asyncio
    async def test_is_locked_out_currently_locked(self, mock_redis):
        """TDD: is_locked_out should return True when account is locked."""
        mock_redis.get.return_value = "1"
        protection = BruteForceProtection(redis_client=mock_redis)

        is_locked = await protection.is_locked_out("test@example.com")

        assert is_locked is True

    @pytest.mark.asyncio
    async def test_record_failed_attempt_under_limit(self, mock_redis):
        """TDD: record_failed_attempt should increment attempts without lockout."""
        mock_redis.incr.return_value = 3  # Under the limit of 5
        protection = BruteForceProtection(redis_client=mock_redis)

        locked_out = await protection.record_failed_attempt("test@example.com")

        assert locked_out is False
        mock_redis.incr.assert_called_with("auth_attempts:test@example.com")
        mock_redis.expire.assert_called_with("auth_attempts:test@example.com", 900)

    @pytest.mark.asyncio
    async def test_record_failed_attempt_exceeds_limit(self, mock_redis):
        """TDD: record_failed_attempt should trigger lockout when limit exceeded."""
        mock_redis.incr.return_value = 6  # Exceeds the limit of 5
        protection = BruteForceProtection(redis_client=mock_redis)

        with patch.object(SecurityAuditLogger, 'log_account_lockout') as mock_log:
            locked_out = await protection.record_failed_attempt("test@example.com", "192.168.1.1")

        assert locked_out is True
        mock_redis.set.assert_called()  # Lockout key should be set
        mock_log.assert_called_once_with("test@example.com", "192.168.1.1")

    @pytest.mark.asyncio
    async def test_record_successful_attempt_clears_attempts(self, mock_redis):
        """TDD: record_successful_attempt should clear failed attempt counter."""
        protection = BruteForceProtection(redis_client=mock_redis)

        await protection.record_successful_attempt("test@example.com")

        mock_redis.delete.assert_called_with("auth_attempts:test@example.com")


class TestTokenBlacklist:
    """Test TokenBlacklist with TDD methodology."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client for testing."""
        mock_redis = Mock()
        mock_redis.set = Mock()
        mock_redis.get = Mock(return_value=None)
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

        # Verify Redis set was called with correct parameters
        assert mock_redis.set.called
        call_args = mock_redis.set.call_args
        assert f"blacklist:{hashlib.sha256(token.encode()).hexdigest()}" in call_args[0]

    @pytest.mark.asyncio
    async def test_blacklist_token_without_expiration(self, mock_redis):
        """TDD: blacklist_token should handle tokens without expiration."""
        service = TokenBlacklist(redis_client=mock_redis)
        token = "test.jwt.token"

        await service.blacklist_token(token)

        assert mock_redis.set.called

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_not_blacklisted(self, mock_redis):
        """TDD: is_token_blacklisted should return False for valid tokens."""
        mock_redis.get.return_value = None
        service = TokenBlacklist(redis_client=mock_redis)
        token = "test.jwt.token"

        is_blacklisted = await service.is_token_blacklisted(token)

        assert is_blacklisted is False

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_currently_blacklisted(self, mock_redis):
        """TDD: is_token_blacklisted should return True for blacklisted tokens."""
        mock_redis.get.return_value = "blacklisted"
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
        """Mock user object."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.password_hash = "$2b$12$hash"
        user.user_type = UserType.BUYER
        user.is_active = True
        user.failed_login_attempts = 0
        user.locked_until = None
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
        """TDD: get_password_hash should generate valid bcrypt hashes."""
        password = "testpassword123"

        hashed = await auth_service.get_password_hash(password)

        assert hashed.startswith("$2b$")
        assert len(hashed) > 50  # Bcrypt hashes are typically 60 characters

    @pytest.mark.asyncio
    async def test_validate_password_strength_integration(self, auth_service):
        """TDD: validate_password_strength should work with async interface."""
        strong_password = "StrongPass123!"

        is_valid, message = await auth_service.validate_password_strength(strong_password)

        assert is_valid is True
        assert "meets all security requirements" in message

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_db, mock_user):
        """TDD: authenticate_user should return user for valid credentials."""
        email = "test@example.com"
        password = "testpassword123"

        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        # Mock password verification
        with patch.object(auth_service, 'verify_password', return_value=True):
            with patch.object(auth_service.brute_force_protection, 'is_locked_out', return_value=False):
                with patch.object(auth_service.brute_force_protection, 'record_successful_attempt'):
                    result = await auth_service.authenticate_user(email, password, mock_db)

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
                    result = await auth_service.authenticate_user(email, password, mock_db)

        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_account_locked(self, auth_service, mock_db):
        """TDD: authenticate_user should return None for locked accounts."""
        email = "test@example.com"
        password = "testpassword123"

        # Mock account lockout
        with patch.object(auth_service.brute_force_protection, 'is_locked_out', return_value=True):
            result = await auth_service.authenticate_user(email, password, mock_db)

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

        with patch.object(auth_service, 'validate_password_strength', return_value=(True, "Valid")):
            with patch.object(auth_service, 'get_password_hash', return_value="$2b$12$hashedpassword"):
                # Mock user creation
                mock_db.add = Mock()
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()

                user = await auth_service.create_user(user_data, mock_db)

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

        with patch.object(auth_service.token_blacklist, 'blacklist_token') as mock_blacklist:
            await auth_service.revoke_token(token)

        mock_blacklist.assert_called_once_with(token)

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
        """TDD: validate_token should return None for blacklisted tokens."""
        token = "blacklisted.jwt.token"

        with patch.object(auth_service.token_blacklist, 'is_token_blacklisted', return_value=True):
            payload = await auth_service.validate_token(token)

        assert payload is None


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

        password = "testpassword123"
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

        password = "testpassword123"
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