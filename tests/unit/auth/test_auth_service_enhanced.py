"""
Enhanced AuthService Unit Tests - TDD Implementation
===================================================

Building comprehensive test coverage for AuthService following TDD methodology.

Test Categories:
1. Password hashing/verification
2. User authentication
3. OTP functionality
4. Password reset workflow
5. Error handling
6. Performance benchmarks

Author: Unit Testing AI
Date: 2025-09-17
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Optional

from app.services.auth_service import AuthService
from app.models.user import User, UserType


@pytest.mark.unit
class TestAuthServicePasswordOperations:
    """Test password hashing and verification operations."""

    @pytest.fixture
    def auth_service(self):
        return AuthService()

    @pytest.mark.asyncio
    async def test_password_hash_generation_creates_bcrypt_hash(self, auth_service):
        """Test that password hashing generates valid bcrypt hash."""
        # ARRANGE
        password = "test_password_123"

        # ACT
        hashed = await auth_service.get_password_hash(password)

        # ASSERT
        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")
        assert len(hashed) >= 60

    @pytest.mark.asyncio
    async def test_password_verification_with_correct_password(self, auth_service):
        """Test password verification succeeds with correct password."""
        # ARRANGE
        password = "secure_password_123"
        hashed = await auth_service.get_password_hash(password)

        # ACT
        is_valid = await auth_service.verify_password(password, hashed)

        # ASSERT
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_password_verification_with_wrong_password(self, auth_service):
        """Test password verification fails with wrong password."""
        # ARRANGE
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        hashed = await auth_service.get_password_hash(correct_password)

        # ACT
        is_valid = await auth_service.verify_password(wrong_password, hashed)

        # ASSERT
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_password_hashing_produces_different_salts(self, auth_service):
        """Test that same password produces different hashes (different salts)."""
        # ARRANGE
        password = "same_password"

        # ACT
        hash1 = await auth_service.get_password_hash(password)
        hash2 = await auth_service.get_password_hash(password)

        # ASSERT
        assert hash1 != hash2  # Different salts should produce different hashes
        # Both should verify correctly
        assert await auth_service.verify_password(password, hash1)
        assert await auth_service.verify_password(password, hash2)

    @pytest.mark.asyncio
    async def test_password_verification_is_case_sensitive(self, auth_service):
        """Test that password verification is case sensitive."""
        # ARRANGE
        password = "CaseSensitivePassword"
        hashed = await auth_service.get_password_hash(password)

        # ACT & ASSERT
        assert await auth_service.verify_password(password, hashed) is True
        assert await auth_service.verify_password("casesensitivepassword", hashed) is False
        assert await auth_service.verify_password("CASESENSITIVEPASSWORD", hashed) is False


@pytest.mark.unit
class TestAuthServiceUserAuthentication:
    """Test user authentication workflow."""

    @pytest.fixture
    def auth_service(self):
        return AuthService()

    @pytest.fixture
    def mock_db(self):
        return Mock()

    @pytest.mark.asyncio
    async def test_authenticate_user_with_valid_credentials(self, auth_service, mock_db):
        """Test user authentication with valid credentials."""
        # ARRANGE
        email = "test@example.com"
        password = "test_password"
        password_hash = await auth_service.get_password_hash(password)

        with patch('sqlite3.connect') as mock_connect:
            mock_cursor = Mock()
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            # Mock successful user lookup
            mock_cursor.fetchone.return_value = (
                "user_id_123",
                email,
                password_hash,
                "BUYER",
                True,  # is_active
                "Test",
                "User"
            )

            # ACT
            user = await auth_service.authenticate_user(mock_db, email, password)

            # ASSERT
            assert user is not None
            assert user.email == email
            assert user.user_type.value == "BUYER"
            assert user.is_active is True

    @pytest.mark.asyncio
    async def test_authenticate_user_with_nonexistent_email(self, auth_service, mock_db):
        """Test authentication fails with non-existent email."""
        # ARRANGE
        email = "nonexistent@example.com"
        password = "any_password"

        with patch('sqlite3.connect') as mock_connect:
            mock_cursor = Mock()
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None

            # ACT
            user = await auth_service.authenticate_user(mock_db, email, password)

            # ASSERT
            assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_with_inactive_account(self, auth_service, mock_db):
        """Test authentication fails with inactive user account."""
        # ARRANGE
        email = "inactive@example.com"
        password = "test_password"
        password_hash = await auth_service.get_password_hash(password)

        with patch('sqlite3.connect') as mock_connect:
            mock_cursor = Mock()
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            # Mock inactive user
            mock_cursor.fetchone.return_value = (
                "user_id_123",
                email,
                password_hash,
                "BUYER",
                False,  # is_active = False
                "Test",
                "User"
            )

            # ACT
            user = await auth_service.authenticate_user(mock_db, email, password)

            # ASSERT
            assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_with_wrong_password(self, auth_service, mock_db):
        """Test authentication fails with wrong password."""
        # ARRANGE
        email = "test@example.com"
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        password_hash = await auth_service.get_password_hash(correct_password)

        with patch('sqlite3.connect') as mock_connect:
            mock_cursor = Mock()
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchone.return_value = (
                "user_id_123",
                email,
                password_hash,
                "BUYER",
                True,
                "Test",
                "User"
            )

            # ACT
            user = await auth_service.authenticate_user(mock_db, email, wrong_password)

            # ASSERT
            assert user is None


@pytest.mark.unit
class TestAuthServiceOTPFunctionality:
    """Test OTP (One-Time Password) functionality."""

    @pytest.fixture
    def auth_service(self):
        service = AuthService()
        # Mock external services to avoid real calls
        service.otp_service = Mock()
        service.email_service = Mock()
        service.sms_service = Mock()
        return service

    @pytest.fixture
    def mock_user(self):
        user = Mock()
        user.email = "test@example.com"
        user.nombre = "Test User"
        user.telefono = "+573001234567"
        return user

    @pytest.mark.asyncio
    async def test_send_email_otp_success(self, auth_service, mock_user):
        """Test successful email OTP sending."""
        # ARRANGE
        mock_db = Mock()
        auth_service.otp_service.can_send_otp.return_value = (True, "OK")
        auth_service.otp_service.create_otp_for_user.return_value = ("123456", "2024-01-01")
        auth_service.email_service.send_otp_email.return_value = True

        # ACT
        success, message = await auth_service.send_email_verification_otp(mock_db, mock_user)

        # ASSERT
        assert success is True
        assert mock_user.email in message
        auth_service.otp_service.can_send_otp.assert_called_once_with(mock_user)
        auth_service.email_service.send_otp_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_otp_rate_limited(self, auth_service, mock_user):
        """Test email OTP sending when rate limited."""
        # ARRANGE
        mock_db = Mock()
        auth_service.otp_service.can_send_otp.return_value = (False, "Rate limited")

        # ACT
        success, message = await auth_service.send_email_verification_otp(mock_db, mock_user)

        # ASSERT
        assert success is False
        assert message == "Rate limited"
        auth_service.email_service.send_otp_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_sms_otp_success(self, auth_service, mock_user):
        """Test successful SMS OTP sending."""
        # ARRANGE
        mock_db = Mock()
        auth_service.otp_service.can_send_otp.return_value = (True, "OK")
        auth_service.otp_service.create_otp_for_user.return_value = ("123456", "2024-01-01")
        auth_service.sms_service.send_otp_sms.return_value = True

        # ACT
        success, message = await auth_service.send_sms_verification_otp(mock_db, mock_user)

        # ASSERT
        assert success is True
        assert mock_user.telefono in message
        auth_service.sms_service.send_otp_sms.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_sms_otp_no_phone_number(self, auth_service, mock_user):
        """Test SMS OTP sending fails when user has no phone number."""
        # ARRANGE
        mock_db = Mock()
        mock_user.telefono = None

        # ACT
        success, message = await auth_service.send_sms_verification_otp(mock_db, mock_user)

        # ASSERT
        assert success is False
        assert "no tiene teléfono" in message.lower()
        auth_service.sms_service.send_otp_sms.assert_not_called()

    @pytest.mark.asyncio
    async def test_verify_otp_code_success(self, auth_service):
        """Test successful OTP code verification."""
        # ARRANGE
        mock_db = Mock()
        mock_user = Mock()
        otp_code = "123456"
        auth_service.otp_service.validate_otp_code.return_value = (True, "Valid code")

        # ACT
        success, message = await auth_service.verify_otp_code(mock_db, mock_user, otp_code)

        # ASSERT
        assert success is True
        assert message == "Valid code"

    @pytest.mark.asyncio
    async def test_verify_otp_code_invalid(self, auth_service):
        """Test OTP code verification with invalid code."""
        # ARRANGE
        mock_db = Mock()
        mock_user = Mock()
        otp_code = "wrong123"
        auth_service.otp_service.validate_otp_code.return_value = (False, "Invalid code")

        # ACT
        success, message = await auth_service.verify_otp_code(mock_db, mock_user, otp_code)

        # ASSERT
        assert success is False
        assert message == "Invalid code"

    @pytest.mark.asyncio
    async def test_cleanup_expired_otps(self, auth_service):
        """Test cleanup of expired OTP codes."""
        # ARRANGE
        mock_db = Mock()
        auth_service.otp_service.cleanup_expired_otps.return_value = 5

        # ACT
        count = await auth_service.cleanup_expired_otps(mock_db)

        # ASSERT
        assert count == 5
        auth_service.otp_service.cleanup_expired_otps.assert_called_once_with(mock_db)


@pytest.mark.unit
class TestAuthServicePasswordReset:
    """Test password reset functionality."""

    @pytest.fixture
    def auth_service(self):
        return AuthService()

    @pytest.fixture
    def mock_user(self):
        user = Mock()
        user.email = "test@example.com"
        user.nombre = "Test User"
        user.can_request_password_reset.return_value = True
        user.is_reset_blocked.return_value = False
        user.is_reset_token_valid.return_value = True
        user.clear_reset_data = Mock()
        return user

    @pytest.mark.asyncio
    async def test_send_password_reset_email_success(self, auth_service, mock_user):
        """Test successful password reset email sending."""
        # ARRANGE
        email = "test@example.com"
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch('app.services.email_service.EmailService') as MockEmailService:
            mock_email_service = Mock()
            MockEmailService.return_value = mock_email_service
            mock_email_service.send_password_reset_email.return_value = True

            # ACT
            success, message = await auth_service.send_password_reset_email(mock_db, email)

            # ASSERT
            assert success is True
            assert "Se ha enviado un enlace" in message

    @pytest.mark.asyncio
    async def test_send_password_reset_email_user_not_found(self, auth_service):
        """Test password reset with non-existent user (security)."""
        # ARRANGE
        email = "nonexistent@example.com"
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # ACT
        success, message = await auth_service.send_password_reset_email(mock_db, email)

        # ASSERT
        # Should return success for security (don't reveal if email exists)
        assert success is True
        assert "Si el email existe" in message

    @pytest.mark.asyncio
    async def test_reset_password_with_valid_token(self, auth_service, mock_user):
        """Test password reset with valid token."""
        # ARRANGE
        token = "valid_reset_token"
        new_password = "new_secure_password"
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # ACT
        success, message = await auth_service.reset_password_with_token(mock_db, token, new_password)

        # ASSERT
        assert success is True
        assert "Contraseña actualizada exitosamente" in message
        mock_user.clear_reset_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_with_invalid_token(self, auth_service):
        """Test password reset with invalid token."""
        # ARRANGE
        token = "invalid_token"
        new_password = "new_password"
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # ACT
        success, message = await auth_service.reset_password_with_token(mock_db, token, new_password)

        # ASSERT
        assert success is False
        assert "Token de recuperación inválido" in message


@pytest.mark.unit
class TestAuthServicePerformance:
    """Test performance benchmarks for authentication operations."""

    @pytest.fixture
    def auth_service(self):
        return AuthService()

    @pytest.mark.asyncio
    async def test_password_hashing_performance(self, auth_service):
        """Test that password hashing completes within acceptable time."""
        # ARRANGE
        password = "performance_test_password"

        # ACT
        start_time = time.time()
        await auth_service.get_password_hash(password)
        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        # ASSERT
        assert execution_time < 500, f"Password hashing took {execution_time:.2f}ms, should be under 500ms"

    @pytest.mark.asyncio
    async def test_password_verification_performance(self, auth_service):
        """Test that password verification completes within acceptable time."""
        # ARRANGE
        password = "performance_test_password"
        hashed = await auth_service.get_password_hash(password)

        # ACT
        start_time = time.time()
        await auth_service.verify_password(password, hashed)
        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        # ASSERT
        assert execution_time < 500, f"Password verification took {execution_time:.2f}ms, should be under 500ms"

    @pytest.mark.asyncio
    async def test_concurrent_password_operations(self, auth_service):
        """Test that concurrent password operations work correctly."""
        # ARRANGE
        passwords = [f"password_{i}" for i in range(3)]

        # ACT
        # Hash all passwords concurrently
        hash_tasks = [auth_service.get_password_hash(pwd) for pwd in passwords]
        hashed_passwords = await asyncio.gather(*hash_tasks)

        # Verify all passwords concurrently
        verify_tasks = [
            auth_service.verify_password(pwd, hashed)
            for pwd, hashed in zip(passwords, hashed_passwords)
        ]
        verify_results = await asyncio.gather(*verify_tasks)

        # ASSERT
        assert all(verify_results), "All password verifications should succeed"
        assert len(hashed_passwords) == len(passwords)


@pytest.mark.unit
class TestAuthServiceErrorHandling:
    """Test error handling and edge cases."""

    @pytest.fixture
    def auth_service(self):
        return AuthService()

    @pytest.mark.asyncio
    async def test_get_user_verification_status(self, auth_service):
        """Test getting user verification status."""
        # ARRANGE
        mock_user = Mock()
        mock_user.email_verified = True
        mock_user.phone_verified = False
        mock_user.otp_secret = "123456"
        mock_user.otp_type = "EMAIL"
        mock_user.otp_expires_at = datetime.now() + timedelta(minutes=10)
        mock_user.can_request_otp.return_value = True
        mock_user.is_otp_blocked.return_value = False
        mock_user.otp_attempts = 1

        # ACT
        status = await auth_service.get_user_verification_status(mock_user)

        # ASSERT
        assert status['email_verified'] is True
        assert status['phone_verified'] is False
        assert status['has_active_otp'] is True
        assert status['otp_type'] == "EMAIL"
        assert status['can_request_new_otp'] is True
        assert status['is_otp_blocked'] is False
        assert status['otp_attempts'] == 1

    @pytest.mark.asyncio
    async def test_error_handling_in_otp_verification(self, auth_service):
        """Test error handling when OTP service throws exception."""
        # ARRANGE
        mock_db = Mock()
        mock_user = Mock()
        auth_service.otp_service = Mock()
        auth_service.otp_service.validate_otp_code.side_effect = Exception("OTP service error")

        # ACT
        success, message = await auth_service.verify_otp_code(mock_db, mock_user, "123456")

        # ASSERT
        assert success is False
        assert "Error verificando código" in message

    @pytest.mark.asyncio
    async def test_error_handling_in_email_otp_sending(self, auth_service):
        """Test error handling when email OTP sending fails."""
        # ARRANGE
        mock_db = Mock()
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.nombre = "Test"

        auth_service.otp_service = Mock()
        auth_service.email_service = Mock()
        auth_service.otp_service.can_send_otp.return_value = (True, "OK")
        auth_service.otp_service.create_otp_for_user.side_effect = Exception("Service error")

        # ACT
        success, message = await auth_service.send_email_verification_otp(mock_db, mock_user)

        # ASSERT
        assert success is False
        assert "Error interno" in message