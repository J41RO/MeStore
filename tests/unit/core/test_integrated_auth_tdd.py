"""
TDD Tests for app/core/integrated_auth.py Module
===============================================

Comprehensive Test-Driven Development tests for the integrated authentication module.
Following strict RED-GREEN-REFACTOR methodology to achieve 95%+ coverage.

Test Structure:
- RED Phase: Write failing tests that describe expected behavior
- GREEN Phase: Implement minimal code to make tests pass
- REFACTOR Phase: Improve code structure while maintaining test coverage

Target Coverage: 95%+ for app/core/integrated_auth.py
Current Coverage: 29% → 95%+

Test Categories:
1. IntegratedAuthService initialization and configuration
2. User authentication methods (simple SQLite and secure)
3. User session creation and token management
4. Token verification and validation
5. User logout and security features
6. Brute force protection
7. User creation and management
8. Health check functionality
9. Migration mode handling
10. Error handling and edge cases

Author: TDD Specialist AI
Date: 2025-09-22
Purpose: Achieve comprehensive test coverage for integrated authentication functionality
"""

import pytest
import asyncio
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock, call
from typing import Dict, Any, Optional, Tuple

# FastAPI imports for testing
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

# TDD Framework imports
from tests.tdd_framework import TDDTestCase
from tests.tdd_patterns import AuthTestPattern, DatabaseTestPattern
from tests.tdd_templates import RedPhaseTemplate, GreenPhaseTemplate, RefactorPhaseTemplate

# Import modules under test
from app.core.integrated_auth import (
    IntegratedAuthService,
    integrated_auth_service
)

# Import related modules for mocking
from app.models.user import User, UserType
from app.core.auth import AuthService
from app.services.secure_auth_service import SecureAuthService, SecurityAuditLogger


@pytest.mark.tdd
@pytest.mark.unit
class TestIntegratedAuthServiceInitializationTDD:
    """
    TDD tests for IntegratedAuthService initialization and configuration.

    Testing service setup, mode configuration, and component initialization.
    """

    def setup_method(self):
        """Set up test fixtures for initialization tests."""
        self.service = IntegratedAuthService()

    @pytest.mark.red_test
    def test_integrated_auth_service_initialization_should_fail_with_invalid_config(self):
        """
        RED: Test IntegratedAuthService initialization with invalid configuration.
        """
        # Test that service handles missing dependencies gracefully
        with patch('app.core.integrated_auth.AuthService', side_effect=Exception("AuthService init failed")):
            with pytest.raises(Exception):
                IntegratedAuthService()

    @pytest.mark.green_test
    def test_integrated_auth_service_initialization_succeeds_with_valid_config(self):
        """
        GREEN: Test IntegratedAuthService initialization succeeds with valid configuration.
        """
        service = IntegratedAuthService()

        # Verify core components are initialized
        assert service.legacy_auth is not None
        assert isinstance(service.legacy_auth, AuthService)
        assert service.secure_auth is None  # Lazy initialization
        assert service.migration_enabled is False  # Default disabled
        assert service.audit_logger is not None
        assert isinstance(service.pwd_context, CryptContext)

    @pytest.mark.green_test
    def test_integrated_auth_service_has_correct_default_configuration(self):
        """
        GREEN: Test IntegratedAuthService has correct default configuration.
        """
        with patch('app.core.integrated_auth.CryptContext') as mock_crypt_context_class:
            # Configure the mock CryptContext instance
            mock_crypt_context = Mock()
            mock_crypt_context.schemes = ["bcrypt"]  # Mock the schemes property as a list
            mock_crypt_context_class.return_value = mock_crypt_context

            service = IntegratedAuthService()

            # Verify default settings
            assert service.migration_enabled is False
            assert service.legacy_auth is not None
            assert service.secure_auth is None
            assert service.audit_logger is not None

            # Verify password context is properly configured
            assert "bcrypt" in service.pwd_context.schemes

            # Verify CryptContext was initialized with correct parameters
            mock_crypt_context_class.assert_called_once_with(schemes=["bcrypt"], deprecated="auto")

    @pytest.mark.green_test
    def test_is_secure_mode_enabled_returns_migration_status(self):
        """
        GREEN: Test is_secure_mode_enabled returns correct migration status.
        """
        service = IntegratedAuthService()

        # Default should be False
        assert service.is_secure_mode_enabled() is False

        # Test with migration enabled
        service.migration_enabled = True
        assert service.is_secure_mode_enabled() is True

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_get_secure_auth_lazy_initialization(self):
        """
        REFACTOR: Test lazy initialization of SecureAuthService.
        """
        service = IntegratedAuthService()

        with patch('app.database.AsyncSessionLocal'), \
             patch('app.core.redis.session.get_redis_sessions', new_callable=AsyncMock) as mock_redis, \
             patch('app.core.integrated_auth.SecureAuthService') as mock_secure_auth_class:

            mock_redis.return_value = Mock()
            mock_secure_auth_instance = Mock()
            mock_secure_auth_class.return_value = mock_secure_auth_instance

            # First call should initialize
            secure_auth = await service._get_secure_auth()
            assert secure_auth == mock_secure_auth_instance
            assert service.secure_auth == mock_secure_auth_instance

            # Second call should return cached instance
            secure_auth2 = await service._get_secure_auth()
            assert secure_auth2 == mock_secure_auth_instance
            assert mock_secure_auth_class.call_count == 1  # Only called once


@pytest.mark.tdd
@pytest.mark.unit
class TestIntegratedAuthServiceSimpleAuthenticationTDD:
    """
    TDD tests for simple SQLite-based authentication functionality.

    Testing direct database authentication for debugging and fallback scenarios.
    """

    def setup_method(self):
        """Set up test fixtures for simple authentication tests."""
        self.service = IntegratedAuthService()
        self.test_email = "test@example.com"
        self.test_password = "test_password_123"
        self.test_password_hash = "$2b$12$test_hash_example"
        self.test_user_id = "test_user_123"

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_authenticate_user_simple_should_fail_with_database_error(self):
        """
        RED: Test simple authentication fails gracefully with database errors.
        """
        with patch('sqlite3.connect', side_effect=Exception("Database connection failed")):
            result = await self.service._authenticate_user_simple(
                self.test_email,
                self.test_password
            )

            assert result is None

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_authenticate_user_simple_succeeds_with_valid_credentials(self):
        """
        GREEN: Test simple authentication succeeds with valid credentials.
        """
        # Mock SQLite database response
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (
            self.test_user_id,
            self.test_email,
            self.test_password_hash,
            "BUYER",  # user_type
            "Test User",  # nombre
            1  # is_active
        )
        mock_conn.execute.return_value = mock_cursor
        mock_conn.close = Mock()

        with patch('sqlite3.connect', return_value=mock_conn), \
             patch.object(self.service.pwd_context, 'verify', return_value=True):

            result = await self.service._authenticate_user_simple(
                self.test_email,
                self.test_password
            )

            # Verify user object was created correctly
            assert result is not None
            assert isinstance(result, User)
            assert result.id == self.test_user_id
            assert result.email == self.test_email
            assert result.user_type == UserType.BUYER
            assert result.is_active is True

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_authenticate_user_simple_should_fail_with_user_not_found(self):
        """
        RED: Test simple authentication fails when user is not found.
        """
        # Mock SQLite database with no user found
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None  # No user found
        mock_conn.execute.return_value = mock_cursor

        with patch('sqlite3.connect', return_value=mock_conn):
            result = await self.service._authenticate_user_simple(
                "nonexistent@example.com",
                self.test_password
            )

            assert result is None

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_authenticate_user_simple_should_fail_with_wrong_password(self):
        """
        RED: Test simple authentication fails with wrong password.
        """
        # Mock SQLite database response with user found
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (
            self.test_user_id,
            self.test_email,
            self.test_password_hash,
            "BUYER",
            "Test User",
            1
        )
        mock_conn.execute.return_value = mock_cursor

        with patch('sqlite3.connect', return_value=mock_conn), \
             patch.object(self.service.pwd_context, 'verify', return_value=False):

            result = await self.service._authenticate_user_simple(
                self.test_email,
                "wrong_password"
            )

            assert result is None

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_authenticate_user_simple_handles_invalid_user_type_gracefully(self):
        """
        GREEN: Test simple authentication handles invalid user type gracefully.
        """
        # Mock SQLite database response with invalid user type
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (
            self.test_user_id,
            self.test_email,
            self.test_password_hash,
            "INVALID_TYPE",  # Invalid user type
            "Test User",
            1
        )
        mock_conn.execute.return_value = mock_cursor

        with patch('sqlite3.connect', return_value=mock_conn), \
             patch.object(self.service.pwd_context, 'verify', return_value=True):

            result = await self.service._authenticate_user_simple(
                self.test_email,
                self.test_password
            )

            # Should succeed with default user type
            assert result is not None
            assert result.user_type == UserType.BUYER  # Default fallback

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_authenticate_user_simple_comprehensive_user_type_handling(self):
        """
        REFACTOR: Test comprehensive user type handling in simple authentication.
        """
        test_cases = [
            ("BUYER", UserType.BUYER),
            ("VENDOR", UserType.VENDOR),
            ("ADMIN", UserType.ADMIN),
            ("buyer", UserType.BUYER),  # Case insensitive
            ("vendor", UserType.BUYER),  # Invalid case -> default
            ("INVALID", UserType.BUYER),  # Fallback to BUYER
            ("", UserType.BUYER),  # Empty string fallback
        ]

        for db_user_type, expected_enum in test_cases:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = (
                self.test_user_id,
                self.test_email,
                self.test_password_hash,
                db_user_type,
                "Test User",
                1
            )
            mock_conn.execute.return_value = mock_cursor

            with patch('sqlite3.connect', return_value=mock_conn), \
                 patch.object(self.service.pwd_context, 'verify', return_value=True):

                result = await self.service._authenticate_user_simple(
                    self.test_email,
                    self.test_password
                )

                assert result is not None
                assert result.user_type == expected_enum


@pytest.mark.tdd
@pytest.mark.unit
class TestIntegratedAuthServiceAuthenticationTDD:
    """
    TDD tests for main authentication method with mode switching.

    Testing authentication flow with both legacy and secure modes.
    """

    def setup_method(self):
        """Set up test fixtures for authentication tests."""
        self.service = IntegratedAuthService()
        self.test_email = "auth@example.com"
        self.test_password = "auth_password_123"
        self.test_ip = "192.168.1.100"
        self.test_user_agent = "TestAgent/1.0"

        # Create mock user
        self.mock_user = Mock(spec=User)
        self.mock_user.id = "auth_user_123"
        self.mock_user.email = self.test_email
        self.mock_user.user_type = UserType.VENDOR

        # Create mock async session
        self.mock_db = Mock(spec=AsyncSession)

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_authenticate_user_should_fail_with_secure_mode_exception(self):
        """
        RED: Test authentication fails when secure mode raises exception.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.authenticate_user_secure = AsyncMock(
                side_effect=HTTPException(status_code=423, detail="Account locked")
            )
            mock_get_secure.return_value = mock_secure_auth

            # Should re-raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await self.service.authenticate_user(
                    self.test_email,
                    self.test_password,
                    self.mock_db,
                    self.test_ip,
                    self.test_user_agent
                )

            assert exc_info.value.status_code == 423
            assert "Account locked" in exc_info.value.detail

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_authenticate_user_succeeds_with_secure_mode(self):
        """
        GREEN: Test authentication succeeds with secure mode enabled.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.authenticate_user_secure = AsyncMock(return_value=self.mock_user)
            mock_get_secure.return_value = mock_secure_auth

            result = await self.service.authenticate_user(
                self.test_email,
                self.test_password,
                self.mock_db,
                self.test_ip,
                self.test_user_agent
            )

            assert result == self.mock_user

            # Verify secure auth was called with correct parameters
            mock_secure_auth.authenticate_user_secure.assert_called_once_with(
                email=self.test_email,
                password=self.test_password,
                db=self.mock_db,
                ip_address=self.test_ip
            )

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_authenticate_user_succeeds_with_legacy_mode(self):
        """
        GREEN: Test authentication succeeds with legacy mode (default).
        """
        # Legacy mode is default (migration_enabled = False)
        assert self.service.migration_enabled is False

        with patch.object(self.service, '_authenticate_user_simple', new_callable=AsyncMock) as mock_simple_auth:
            mock_simple_auth.return_value = self.mock_user

            result = await self.service.authenticate_user(
                self.test_email,
                self.test_password,
                self.mock_db,
                self.test_ip,
                self.test_user_agent
            )

            assert result == self.mock_user
            mock_simple_auth.assert_called_once_with(self.test_email, self.test_password)

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_authenticate_user_should_handle_unexpected_exceptions(self):
        """
        RED: Test authentication handles unexpected exceptions gracefully.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_get_secure.side_effect = Exception("Unexpected error")

            result = await self.service.authenticate_user(
                self.test_email,
                self.test_password,
                self.mock_db,
                self.test_ip,
                self.test_user_agent
            )

            assert result is None

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_authenticate_user_audit_logging_in_secure_mode(self):
        """
        REFACTOR: Test authentication audit logging in secure mode.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure, \
             patch.object(self.service.audit_logger, 'log_authentication_attempt') as mock_log:

            mock_secure_auth = Mock()
            mock_secure_auth.authenticate_user_secure = AsyncMock(return_value=self.mock_user)
            mock_get_secure.return_value = mock_secure_auth

            result = await self.service.authenticate_user(
                self.test_email,
                self.test_password,
                self.mock_db,
                self.test_ip,
                self.test_user_agent
            )

            assert result == self.mock_user

            # Verify audit logging was called twice (attempt and success)
            assert mock_log.call_count == 2

            # Verify first call (initial attempt)
            first_call = mock_log.call_args_list[0]
            assert first_call[1]['email'] == self.test_email
            assert first_call[1]['success'] is False
            assert first_call[1]['ip_address'] == self.test_ip

            # Verify second call (success update)
            second_call = mock_log.call_args_list[1]
            assert second_call[1]['email'] == self.test_email
            assert second_call[1]['success'] is True


@pytest.mark.tdd
@pytest.mark.unit
class TestIntegratedAuthServiceSessionManagementTDD:
    """
    TDD tests for user session creation and token management.

    Testing session creation, token generation, and session handling.
    """

    def setup_method(self):
        """Set up test fixtures for session management tests."""
        self.service = IntegratedAuthService()
        self.mock_user = Mock(spec=User)
        self.mock_user.id = "session_user_123"
        self.mock_user.email = "session@example.com"
        self.test_ip = "10.0.0.1"
        self.test_user_agent = "SessionTestAgent/1.0"

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_create_user_session_should_fail_with_secure_mode_error(self):
        """
        RED: Test session creation fails when secure mode encounters error.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.create_user_session = AsyncMock(side_effect=Exception("Session creation failed"))
            mock_get_secure.return_value = mock_secure_auth

            with pytest.raises(HTTPException) as exc_info:
                await self.service.create_user_session(
                    self.mock_user,
                    self.test_ip,
                    self.test_user_agent
                )

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to create user session" in exc_info.value.detail

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_create_user_session_succeeds_with_secure_mode(self):
        """
        GREEN: Test session creation succeeds with secure mode enabled.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        expected_access_token = "secure_access_token_123"
        expected_refresh_token = "legacy_refresh_token_123"

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure, \
             patch.object(self.service.legacy_auth, 'create_refresh_token') as mock_create_refresh:

            mock_secure_auth = Mock()
            mock_secure_auth.create_user_session = AsyncMock(return_value=expected_access_token)
            mock_get_secure.return_value = mock_secure_auth
            mock_create_refresh.return_value = expected_refresh_token

            access_token, refresh_token = await self.service.create_user_session(
                self.mock_user,
                self.test_ip,
                self.test_user_agent
            )

            assert access_token == expected_access_token
            assert refresh_token == expected_refresh_token

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_create_user_session_succeeds_with_legacy_mode(self):
        """
        GREEN: Test session creation succeeds with legacy mode.
        """
        # Legacy mode is default
        assert self.service.migration_enabled is False

        expected_access_token = "legacy_access_token_123"
        expected_refresh_token = "legacy_refresh_token_123"

        with patch('app.core.security.create_access_token') as mock_create_access, \
             patch('app.core.security.create_refresh_token') as mock_create_refresh:

            mock_create_access.return_value = expected_access_token
            mock_create_refresh.return_value = expected_refresh_token

            access_token, refresh_token = await self.service.create_user_session(
                self.mock_user,
                self.test_ip,
                self.test_user_agent
            )

            assert access_token == expected_access_token
            assert refresh_token == expected_refresh_token

            # Verify tokens were created with correct user ID
            normalized_id = str(self.mock_user.id)
            mock_create_access.assert_called_once_with(data={"sub": normalized_id})
            mock_create_refresh.assert_called_once_with(data={"sub": normalized_id})

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_create_user_session_handles_user_id_normalization(self):
        """
        REFACTOR: Test session creation handles various user ID formats.
        """
        test_user_ids = [
            123,  # Integer
            "string_id",  # String
            None,  # None (should handle gracefully)
        ]

        for user_id in test_user_ids:
            mock_user = Mock(spec=User)
            mock_user.id = user_id

            with patch('app.core.security.create_access_token') as mock_create_access, \
                 patch('app.core.security.create_refresh_token') as mock_create_refresh:

                mock_create_access.return_value = "access_token"
                mock_create_refresh.return_value = "refresh_token"

                if user_id is None:
                    # Should handle None gracefully
                    access_token, refresh_token = await self.service.create_user_session(mock_user)

                    assert access_token == "access_token"
                    assert refresh_token == "refresh_token"

                    # Verify None was converted to string "None"
                    expected_normalized_id = str(user_id)  # str(None) = "None"
                    mock_create_access.assert_called_once_with(data={"sub": expected_normalized_id})
                else:
                    access_token, refresh_token = await self.service.create_user_session(mock_user)

                    assert access_token == "access_token"
                    assert refresh_token == "refresh_token"

                    # Verify normalized ID was used
                    expected_normalized_id = str(user_id)
                    mock_create_access.assert_called_once_with(data={"sub": expected_normalized_id})


@pytest.mark.tdd
@pytest.mark.unit
class TestIntegratedAuthServiceTokenVerificationTDD:
    """
    TDD tests for token verification functionality.

    Testing token validation with both secure and legacy modes.
    """

    def setup_method(self):
        """Set up test fixtures for token verification tests."""
        self.service = IntegratedAuthService()
        self.test_token = "test_jwt_token_example"
        self.test_payload = {"sub": "user_123", "exp": 1234567890}

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_verify_token_should_fail_with_secure_mode_exception(self):
        """
        RED: Test token verification fails when secure mode raises exception.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.verify_token_secure = AsyncMock(
                side_effect=HTTPException(status_code=401, detail="Token expired")
            )
            mock_get_secure.return_value = mock_secure_auth

            with pytest.raises(HTTPException) as exc_info:
                await self.service.verify_token(self.test_token)

            assert exc_info.value.status_code == 401
            assert "Token expired" in exc_info.value.detail

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_verify_token_succeeds_with_secure_mode(self):
        """
        GREEN: Test token verification succeeds with secure mode.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.verify_token_secure = AsyncMock(return_value=self.test_payload)
            mock_get_secure.return_value = mock_secure_auth

            result = await self.service.verify_token(self.test_token)

            assert result == self.test_payload
            mock_secure_auth.verify_token_secure.assert_called_once_with(self.test_token)

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_verify_token_succeeds_with_legacy_mode(self):
        """
        GREEN: Test token verification succeeds with legacy mode.
        """
        # Legacy mode is default
        assert self.service.migration_enabled is False

        with patch.object(self.service.legacy_auth, 'verify_token') as mock_verify:
            mock_verify.return_value = self.test_payload

            result = await self.service.verify_token(self.test_token)

            assert result == self.test_payload
            mock_verify.assert_called_once_with(self.test_token)

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_verify_token_should_handle_unexpected_exceptions(self):
        """
        RED: Test token verification handles unexpected exceptions.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_get_secure.side_effect = Exception("Unexpected verification error")

            with pytest.raises(HTTPException) as exc_info:
                await self.service.verify_token(self.test_token)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_verify_token_comprehensive_error_handling(self):
        """
        REFACTOR: Test comprehensive error handling in token verification.
        """
        test_scenarios = [
            # (exception_type, should_re_raise)
            (HTTPException(401, "Unauthorized"), True),
            (Exception("Generic error"), False),  # Should convert to HTTPException
            (ValueError("Invalid token"), False),
            (KeyError("Missing claim"), False),
        ]

        for exception, should_re_raise in test_scenarios:
            # Test with secure mode
            self.service.migration_enabled = True

            with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
                mock_secure_auth = Mock()
                mock_secure_auth.verify_token_secure = AsyncMock(side_effect=exception)
                mock_get_secure.return_value = mock_secure_auth

                if should_re_raise and isinstance(exception, HTTPException):
                    with pytest.raises(HTTPException) as exc_info:
                        await self.service.verify_token(self.test_token)
                    assert exc_info.value.status_code == exception.status_code
                else:
                    with pytest.raises(HTTPException) as exc_info:
                        await self.service.verify_token(self.test_token)
                    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.tdd
@pytest.mark.unit
class TestIntegratedAuthServiceLogoutTDD:
    """
    TDD tests for user logout functionality.

    Testing logout with token invalidation and security logging.
    """

    def setup_method(self):
        """Set up test fixtures for logout tests."""
        self.service = IntegratedAuthService()
        self.test_user_id = "logout_user_123"
        self.test_token = "logout_token_example"

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_logout_user_should_handle_secure_mode_failure(self):
        """
        RED: Test logout handles secure mode failure gracefully.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.logout_user_secure = AsyncMock(side_effect=Exception("Logout failed"))
            mock_get_secure.return_value = mock_secure_auth

            result = await self.service.logout_user(self.test_user_id, self.test_token)

            assert result is False

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_logout_user_succeeds_with_secure_mode(self):
        """
        GREEN: Test logout succeeds with secure mode enabled.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure, \
             patch.object(self.service.audit_logger, 'log_security_event') as mock_log:

            mock_secure_auth = Mock()
            mock_secure_auth.logout_user_secure = AsyncMock(return_value=True)
            mock_get_secure.return_value = mock_secure_auth

            result = await self.service.logout_user(self.test_user_id, self.test_token)

            assert result is True

            # Verify logout was called with correct parameters
            mock_secure_auth.logout_user_secure.assert_called_once_with(
                self.test_user_id,
                self.test_token
            )

            # Verify security logging
            mock_log.assert_called_once_with(
                event_type="user_logout",
                user_id=self.test_user_id,
                details={"success": True}
            )

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_logout_user_succeeds_with_legacy_mode(self):
        """
        GREEN: Test logout succeeds with legacy mode.
        """
        # Legacy mode is default
        assert self.service.migration_enabled is False

        result = await self.service.logout_user(self.test_user_id, self.test_token)

        # Legacy mode always returns True
        assert result is True

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_logout_user_security_logging_comprehensive(self):
        """
        REFACTOR: Test comprehensive security logging for logout operations.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        test_scenarios = [
            (True, {"success": True}),   # Successful logout
            (False, {"success": False}), # Failed logout
        ]

        for logout_success, expected_details in test_scenarios:
            with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure, \
                 patch.object(self.service.audit_logger, 'log_security_event') as mock_log:

                mock_secure_auth = Mock()
                mock_secure_auth.logout_user_secure = AsyncMock(return_value=logout_success)
                mock_get_secure.return_value = mock_secure_auth

                result = await self.service.logout_user(self.test_user_id, self.test_token)

                assert result == logout_success

                # Verify security logging with correct details
                mock_log.assert_called_once_with(
                    event_type="user_logout",
                    user_id=self.test_user_id,
                    details=expected_details
                )


@pytest.mark.tdd
@pytest.mark.unit
class TestIntegratedAuthServiceBruteForceProtectionTDD:
    """
    TDD tests for brute force protection functionality.

    Testing IP and user-based brute force protection.
    """

    def setup_method(self):
        """Set up test fixtures for brute force protection tests."""
        self.service = IntegratedAuthService()
        self.test_email = "bruteforce@example.com"
        self.test_ip = "192.168.1.100"

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_check_brute_force_protection_should_handle_secure_mode_error(self):
        """
        RED: Test brute force protection handles secure mode errors gracefully.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.check_brute_force_attempts = AsyncMock(side_effect=Exception("BF check failed"))
            mock_get_secure.return_value = mock_secure_auth

            result = await self.service.check_brute_force_protection(self.test_email, self.test_ip)

            # Should return True (allow access) on error for safety
            assert result is True

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_check_brute_force_protection_succeeds_with_secure_mode(self):
        """
        GREEN: Test brute force protection succeeds with secure mode enabled.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.check_brute_force_attempts = AsyncMock(return_value=False)  # Blocked
            mock_get_secure.return_value = mock_secure_auth

            result = await self.service.check_brute_force_protection(self.test_email, self.test_ip)

            assert result is False
            mock_secure_auth.check_brute_force_attempts.assert_called_once_with(
                self.test_email,
                self.test_ip
            )

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_check_brute_force_protection_returns_true_in_legacy_mode(self):
        """
        GREEN: Test brute force protection always returns True in legacy mode.
        """
        # Legacy mode is default
        assert self.service.migration_enabled is False

        result = await self.service.check_brute_force_protection(self.test_email, self.test_ip)

        # Legacy mode has no protection
        assert result is True

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_check_brute_force_protection_various_scenarios(self):
        """
        REFACTOR: Test brute force protection with various input scenarios.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        test_scenarios = [
            # (email, ip, bf_result, expected_result)
            ("user1@example.com", "10.0.0.1", True, True),    # Allowed
            ("user2@example.com", "10.0.0.2", False, False),  # Blocked
            ("user3@example.com", None, True, True),          # No IP provided
            (None, "10.0.0.3", True, True),                   # No email provided
        ]

        for email, ip, bf_result, expected in test_scenarios:
            with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
                mock_secure_auth = Mock()
                mock_secure_auth.check_brute_force_attempts = AsyncMock(return_value=bf_result)
                mock_get_secure.return_value = mock_secure_auth

                result = await self.service.check_brute_force_protection(email, ip)

                assert result == expected


@pytest.mark.tdd
@pytest.mark.unit
class TestIntegratedAuthServiceUserCreationTDD:
    """
    TDD tests for user creation functionality.

    Testing user creation with proper validation and database handling.
    """

    def setup_method(self):
        """Set up test fixtures for user creation tests."""
        self.service = IntegratedAuthService()
        self.test_email = "newuser@example.com"
        self.test_password = "new_password_123"
        self.mock_db = AsyncMock(spec=AsyncSession)

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_create_user_should_fail_with_existing_user(self):
        """
        RED: Test user creation fails when user already exists.
        """
        # Mock database to return existing user
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = Mock(spec=User)  # Existing user
        self.mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="User with email .* already exists"):
            await self.service.create_user(
                self.mock_db,
                self.test_email,
                self.test_password
            )

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_create_user_succeeds_with_valid_data(self):
        """
        GREEN: Test user creation succeeds with valid data.
        """
        # Mock database to return no existing user
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None  # No existing user
        self.mock_db.execute.return_value = mock_result

        with patch.object(self.service.pwd_context, 'hash') as mock_hash, \
             patch('uuid.uuid4') as mock_uuid:

            mock_hash.return_value = "$2b$12$hashed_password"
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__.return_value = "new_user_uuid"

            result = await self.service.create_user(
                self.mock_db,
                self.test_email,
                self.test_password
            )

            # Verify user creation
            assert isinstance(result, User)
            assert result.email == self.test_email
            assert result.user_type == UserType.BUYER  # Default
            assert result.is_active is True
            assert result.is_verified is False

            # Verify database operations
            self.mock_db.add.assert_called_once()
            self.mock_db.commit.assert_called_once()
            self.mock_db.refresh.assert_called_once()

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_create_user_with_custom_user_type(self):
        """
        GREEN: Test user creation with custom user type.
        """
        # Mock database to return no existing user
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result

        with patch.object(self.service.pwd_context, 'hash') as mock_hash, \
             patch('uuid.uuid4') as mock_uuid:

            mock_hash.return_value = "$2b$12$hashed_password"
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__.return_value = "vendor_user_uuid"

            result = await self.service.create_user(
                self.mock_db,
                self.test_email,
                self.test_password,
                user_type="VENDOR",
                nombre="Test Vendor"
            )

            assert result.user_type == UserType.VENDOR
            assert result.nombre == "Test Vendor"

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_create_user_should_handle_database_error(self):
        """
        RED: Test user creation handles database errors gracefully.
        """
        # Mock database to fail on commit
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        self.mock_db.commit.side_effect = Exception("Database commit failed")

        with patch.object(self.service.pwd_context, 'hash') as mock_hash:
            mock_hash.return_value = "$2b$12$hashed_password"

            with pytest.raises(Exception):
                await self.service.create_user(
                    self.mock_db,
                    self.test_email,
                    self.test_password
                )

            # Verify rollback was called
            self.mock_db.rollback.assert_called_once()

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_create_user_user_type_conversion_comprehensive(self):
        """
        REFACTOR: Test comprehensive user type conversion in user creation.
        """
        test_cases = [
            # (input_type, expected_enum)
            ("BUYER", UserType.BUYER),
            ("VENDOR", UserType.VENDOR),
            ("ADMIN", UserType.ADMIN),
            ("buyer", UserType.BUYER),   # Case insensitive
            ("vendor", UserType.BUYER), # Invalid case -> default
            ("invalid", UserType.BUYER), # Invalid -> default
            (UserType.VENDOR, UserType.VENDOR), # Already enum
        ]

        for input_type, expected_enum in test_cases:
            # Mock database to return no existing user
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            self.mock_db.execute.return_value = mock_result
            # Reset call counts
            self.mock_db.reset_mock()

            with patch.object(self.service.pwd_context, 'hash') as mock_hash, \
                 patch('uuid.uuid4') as mock_uuid:

                mock_hash.return_value = "$2b$12$hashed_password"
                mock_uuid.return_value = Mock()
                mock_uuid.return_value.__str__.return_value = f"user_uuid_{input_type}"

                result = await self.service.create_user(
                    self.mock_db,
                    f"test_{input_type}@example.com",
                    self.test_password,
                    user_type=input_type
                )

                assert result.user_type == expected_enum


@pytest.mark.tdd
@pytest.mark.unit
class TestIntegratedAuthServiceHealthCheckTDD:
    """
    TDD tests for health check functionality.

    Testing service health monitoring and status reporting.
    """

    def setup_method(self):
        """Set up test fixtures for health check tests."""
        self.service = IntegratedAuthService()

    @pytest.mark.red_test
    @pytest.mark.asyncio
    async def test_health_check_should_handle_secure_auth_error(self):
        """
        RED: Test health check handles secure auth health check errors.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.health_check = AsyncMock(side_effect=Exception("Health check failed"))
            mock_get_secure.return_value = mock_secure_auth

            result = await self.service.health_check()

            # Should include error information
            assert "service" in result
            assert "secure_mode" in result
            assert "legacy_available" in result
            assert "timestamp" in result
            assert "secure_auth" in result
            assert result["secure_auth"]["status"] == "error"

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_health_check_succeeds_with_secure_mode_enabled(self):
        """
        GREEN: Test health check succeeds with secure mode enabled.
        """
        # Enable secure mode
        self.service.migration_enabled = True

        secure_health = {"status": "healthy", "components": ["redis", "database"]}

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.health_check = AsyncMock(return_value=secure_health)
            mock_get_secure.return_value = mock_secure_auth

            result = await self.service.health_check()

            # Verify health check structure
            assert result["service"] == "IntegratedAuthService"
            assert result["secure_mode"] is True
            assert result["legacy_available"] is True
            assert result["secure_auth"] == secure_health
            assert "timestamp" in result

    @pytest.mark.green_test
    @pytest.mark.asyncio
    async def test_health_check_succeeds_with_legacy_mode_only(self):
        """
        GREEN: Test health check succeeds with legacy mode only.
        """
        # Legacy mode is default
        assert self.service.migration_enabled is False

        result = await self.service.health_check()

        # Verify health check structure for legacy mode
        assert result["service"] == "IntegratedAuthService"
        assert result["secure_mode"] is False
        assert result["legacy_available"] is True
        assert "secure_auth" not in result
        assert "timestamp" in result

        # Verify timestamp format
        timestamp = result["timestamp"]
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO format

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_health_check_comprehensive_status_reporting(self):
        """
        REFACTOR: Test comprehensive health status reporting.
        """
        test_scenarios = [
            # (secure_mode_enabled, secure_health_result, should_include_secure_auth)
            (False, None, False),  # Legacy only
            (True, {"status": "healthy"}, True),  # Secure mode healthy
            (True, {"status": "degraded", "issues": ["redis_slow"]}, True),  # Secure mode degraded
        ]

        for secure_enabled, secure_health, should_include in test_scenarios:
            self.service.migration_enabled = secure_enabled

            if secure_enabled and secure_health:
                with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
                    mock_secure_auth = Mock()
                    mock_secure_auth.health_check = AsyncMock(return_value=secure_health)
                    mock_get_secure.return_value = mock_secure_auth

                    result = await self.service.health_check()
            else:
                result = await self.service.health_check()

            # Verify common fields
            assert result["service"] == "IntegratedAuthService"
            assert result["secure_mode"] == secure_enabled
            assert result["legacy_available"] is True
            assert "timestamp" in result

            # Verify secure auth inclusion
            if should_include:
                assert "secure_auth" in result
                assert result["secure_auth"] == secure_health
            else:
                assert "secure_auth" not in result


@pytest.mark.tdd
@pytest.mark.unit
class TestIntegratedAuthServiceIntegrationTDD:
    """
    TDD integration tests for the complete integrated auth service.

    Testing interactions between all components and end-to-end workflows.
    """

    def setup_method(self):
        """Set up test fixtures for integration tests."""
        self.service = IntegratedAuthService()
        self.test_email = "integration@example.com"
        self.test_password = "integration_password_123"
        self.test_ip = "203.0.113.1"
        self.test_user_agent = "IntegrationTestAgent/1.0"

        # Create comprehensive mock user
        self.mock_user = Mock(spec=User)
        self.mock_user.id = "integration_user_123"
        self.mock_user.email = self.test_email
        self.mock_user.user_type = UserType.VENDOR
        self.mock_user.is_active = True
        self.mock_user.is_verified = True

        # Mock database session
        self.mock_db = AsyncMock(spec=AsyncSession)

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_complete_authentication_workflow_legacy_mode(self):
        """
        REFACTOR: Test complete authentication workflow in legacy mode.

        This test validates the entire auth system working together:
        1. User authentication
        2. Session creation
        3. Token verification
        4. User logout
        5. Health check
        """
        # Ensure legacy mode
        self.service.migration_enabled = False

        # Phase 1: Authentication
        with patch.object(self.service, '_authenticate_user_simple', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = self.mock_user

            authenticated_user = await self.service.authenticate_user(
                self.test_email,
                self.test_password,
                self.mock_db,
                self.test_ip,
                self.test_user_agent
            )

            assert authenticated_user == self.mock_user

        # Phase 2: Session creation
        with patch('app.core.security.create_access_token') as mock_create_access, \
             patch('app.core.security.create_refresh_token') as mock_create_refresh:

            mock_create_access.return_value = "integration_access_token"
            mock_create_refresh.return_value = "integration_refresh_token"

            access_token, refresh_token = await self.service.create_user_session(
                authenticated_user,
                self.test_ip,
                self.test_user_agent
            )

            assert access_token == "integration_access_token"
            assert refresh_token == "integration_refresh_token"

        # Phase 3: Token verification
        with patch.object(self.service.legacy_auth, 'verify_token') as mock_verify:
            mock_verify.return_value = {"sub": str(authenticated_user.id)}

            token_payload = await self.service.verify_token(access_token)

            assert token_payload["sub"] == str(authenticated_user.id)

        # Phase 4: Logout
        logout_success = await self.service.logout_user(
            str(authenticated_user.id),
            access_token
        )

        assert logout_success is True

        # Phase 5: Health check
        health_status = await self.service.health_check()

        assert health_status["service"] == "IntegratedAuthService"
        assert health_status["secure_mode"] is False
        assert health_status["legacy_available"] is True

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_mode_switching_behavior(self):
        """
        REFACTOR: Test behavior when switching between legacy and secure modes.
        """
        # Start in legacy mode
        assert self.service.migration_enabled is False
        assert self.service.is_secure_mode_enabled() is False

        # Test legacy mode authentication
        with patch.object(self.service, '_authenticate_user_simple', new_callable=AsyncMock) as mock_simple:
            mock_simple.return_value = self.mock_user

            result1 = await self.service.authenticate_user(
                self.test_email,
                self.test_password,
                self.mock_db
            )

            assert result1 == self.mock_user
            mock_simple.assert_called_once()

        # Switch to secure mode
        self.service.migration_enabled = True
        assert self.service.is_secure_mode_enabled() is True

        # Test secure mode authentication
        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure:
            mock_secure_auth = Mock()
            mock_secure_auth.authenticate_user_secure = AsyncMock(return_value=self.mock_user)
            mock_get_secure.return_value = mock_secure_auth

            result2 = await self.service.authenticate_user(
                self.test_email,
                self.test_password,
                self.mock_db,
                self.test_ip,
                self.test_user_agent
            )

            assert result2 == self.mock_user
            mock_secure_auth.authenticate_user_secure.assert_called_once()

        # Switch back to legacy mode
        self.service.migration_enabled = False

        # Test that it reverts to legacy behavior
        with patch.object(self.service, '_authenticate_user_simple', new_callable=AsyncMock) as mock_simple2:
            mock_simple2.return_value = self.mock_user

            result3 = await self.service.authenticate_user(
                self.test_email,
                self.test_password,
                self.mock_db
            )

            assert result3 == self.mock_user
            mock_simple2.assert_called_once()

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_error_resilience_across_all_operations(self):
        """
        REFACTOR: Test error resilience across all service operations.
        """
        # Test authentication resilience
        with patch.object(self.service, '_authenticate_user_simple', side_effect=Exception("Auth error")):
            result = await self.service.authenticate_user(self.test_email, self.test_password, self.mock_db)
            assert result is None  # Should not crash

        # Test session creation resilience
        with patch('app.core.security.create_access_token', side_effect=Exception("Token error")):
            with pytest.raises(HTTPException):
                await self.service.create_user_session(self.mock_user)

        # Test token verification resilience
        with patch.object(self.service.legacy_auth, 'verify_token', side_effect=Exception("Verify error")):
            with pytest.raises(HTTPException):
                await self.service.verify_token("invalid_token")

        # Test logout resilience
        result = await self.service.logout_user("user_id", "token")
        assert result is True  # Legacy mode always succeeds

        # Test brute force check resilience
        result = await self.service.check_brute_force_protection(self.test_email, self.test_ip)
        assert result is True  # Legacy mode has no protection

        # Test health check resilience
        health = await self.service.health_check()
        assert "service" in health  # Should always return basic info

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_security_audit_and_logging_integration(self):
        """
        REFACTOR: Test security audit and logging across operations.
        """
        # Enable secure mode for audit logging
        self.service.migration_enabled = True

        with patch.object(self.service, '_get_secure_auth', new_callable=AsyncMock) as mock_get_secure, \
             patch.object(self.service.audit_logger, 'log_authentication_attempt') as mock_log_auth, \
             patch.object(self.service.audit_logger, 'log_security_event') as mock_log_security:

            mock_secure_auth = Mock()
            mock_secure_auth.authenticate_user_secure = AsyncMock(return_value=self.mock_user)
            mock_secure_auth.logout_user_secure = AsyncMock(return_value=True)
            mock_get_secure.return_value = mock_secure_auth

            # Test authentication logging
            await self.service.authenticate_user(
                self.test_email,
                self.test_password,
                self.mock_db,
                self.test_ip,
                self.test_user_agent
            )

            # Verify authentication attempt logging (should be called twice: attempt + success)
            assert mock_log_auth.call_count == 2

            # Test logout logging
            await self.service.logout_user(str(self.mock_user.id), "test_token")

            # Verify security event logging
            mock_log_security.assert_called_once_with(
                event_type="user_logout",
                user_id=str(self.mock_user.id),
                details={"success": True}
            )

    @pytest.mark.refactor_test
    @pytest.mark.asyncio
    async def test_performance_characteristics_integration(self):
        """
        REFACTOR: Test performance characteristics of integrated auth service.
        """
        import time

        # Test multiple authentication attempts performance
        start_time = time.time()

        with patch.object(self.service, '_authenticate_user_simple', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = self.mock_user

            # Perform 50 authentication attempts
            auth_results = []
            for i in range(50):
                result = await self.service.authenticate_user(
                    f"user{i}@example.com",
                    "password123",
                    self.mock_db
                )
                auth_results.append(result)

        auth_time = time.time() - start_time

        # Should complete 50 authentications quickly
        assert auth_time < 2.0
        assert len(auth_results) == 50
        assert all(result == self.mock_user for result in auth_results)

        # Test session creation performance
        start_time = time.time()

        with patch('app.core.security.create_access_token') as mock_create_access, \
             patch('app.core.security.create_refresh_token') as mock_create_refresh:

            mock_create_access.return_value = "perf_access_token"
            mock_create_refresh.return_value = "perf_refresh_token"

            # Create 100 sessions
            session_results = []
            for i in range(100):
                access_token, refresh_token = await self.service.create_user_session(self.mock_user)
                session_results.append((access_token, refresh_token))

        session_time = time.time() - start_time

        # Should complete 100 session creations quickly
        assert session_time < 1.0
        assert len(session_results) == 100


if __name__ == "__main__":
    # Run TDD tests with specific markers
    import subprocess
    import sys

    print("🧪 Running TDD Integrated Auth Module Tests")
    print("=" * 50)

    # Run RED phase tests
    print("\n🔴 RED Phase - Testing failing scenarios...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        __file__, "-v", "-m", "red_test",
        "--tb=short"
    ])

    # Run GREEN phase tests
    print("\n🟢 GREEN Phase - Testing passing scenarios...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        __file__, "-v", "-m", "green_test",
        "--tb=short"
    ])

    # Run REFACTOR phase tests
    print("\n🔄 REFACTOR Phase - Testing optimized scenarios...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        __file__, "-v", "-m", "refactor_test",
        "--tb=short"
    ])

    # Run all tests with coverage
    print("\n📊 Full Coverage Analysis...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        __file__, "-v", "--cov=app.core.integrated_auth",
        "--cov-report=term-missing",
        "--tb=short"
    ])