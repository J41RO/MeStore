"""
Comprehensive Unit Tests for User Model - TDD Implementation
============================================================

Test Coverage:
- User model creation and validation
- User type enumeration behavior
- Authentication-related methods
- OTP functionality methods
- Password reset methods
- User state management
- Business logic validation

TDD Methodology:
1. RED: Write failing test first
2. GREEN: Implement minimal code to pass
3. REFACTOR: Improve code quality

Target Coverage: 90%+
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import Optional
import uuid

from app.models.user import User, UserType, VendorStatus
from app.models.base import BaseModel


@pytest.mark.unit
class TestUserModelBasics:
    """Test basic User model functionality."""

    def test_user_model_inherits_from_base_model(self):
        """Test that User model inherits from BaseModel."""
        # ARRANGE & ACT
        user = User()

        # ASSERT
        assert isinstance(user, BaseModel)
        assert hasattr(user, 'id')
        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')

    def test_user_initialization_with_defaults(self):
        """Test User model initialization with default values."""
        # ARRANGE & ACT
        user = User()
        user.email = "test@example.com"
        user.password_hash = "hashed_password"

        # ASSERT
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        # Note: Some default values are set at the database level, not at object creation
        # Test the defaults that are set at the Python object level
        assert user.is_active is True  # This is set as default in Python
        assert user.email_verified is False  # Default value
        assert user.phone_verified is False  # Default value
        assert user.otp_attempts == 0  # Default value
        assert user.is_verified is False  # Default value
        # reset_attempts and user_type defaults are set at database level, so will be None until persisted

    def test_user_initialization_with_custom_values(self):
        """Test User model initialization with custom values."""
        # ARRANGE & ACT
        user = User(
            email="vendor@example.com",
            password_hash="hashed_password",
            user_type=UserType.VENDEDOR,
            nombre="Test",
            apellido="Vendor",
            is_active=True,
            telefono="+573001234567"
        )

        # ASSERT
        assert user.email == "vendor@example.com"
        assert user.user_type == UserType.VENDEDOR
        assert user.nombre == "Test"
        assert user.apellido == "Vendor"
        assert user.telefono == "+573001234567"

    def test_user_string_representations(self):
        """Test User model string representations."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            nombre="John",
            apellido="Doe"
        )

        # ACT & ASSERT
        assert "test@example.com" in str(user)
        assert "test@example.com" in repr(user)

    def test_user_full_name_property(self):
        """Test User model full_name property."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            nombre="John",
            apellido="Doe"
        )

        # ACT
        full_name = user.full_name

        # ASSERT
        assert full_name == "John Doe"

    def test_user_full_name_with_missing_parts(self):
        """Test User model full_name property with missing name parts."""
        # Test with only nombre
        user1 = User(
            email="test1@example.com",
            password_hash="hashed_password",
            nombre="John"
        )
        assert user1.full_name == "John"

        # Test with only apellido
        user2 = User(
            email="test2@example.com",
            password_hash="hashed_password",
            apellido="Doe"
        )
        assert user2.full_name == "Doe"

        # Test with neither
        user3 = User(
            email="test3@example.com",
            password_hash="hashed_password"
        )
        assert user3.full_name == "Usuario sin nombre"


@pytest.mark.unit
class TestUserTypeEnumeration:
    """Test UserType enumeration behavior."""

    def test_user_type_enum_values(self):
        """Test UserType enum has correct values."""
        # ARRANGE & ACT & ASSERT
        assert UserType.COMPRADOR.value == "COMPRADOR"
        assert UserType.VENDEDOR.value == "VENDEDOR"
        assert UserType.ADMIN.value == "ADMIN"
        assert UserType.SUPERUSER.value == "SUPERUSER"

    def test_user_type_assignment(self):
        """Test assigning different user types to User model."""
        # ARRANGE & ACT
        buyer = User(
            email="buyer@example.com",
            password_hash="hash",
            user_type=UserType.COMPRADOR
        )
        vendor = User(
            email="vendor@example.com",
            password_hash="hash",
            user_type=UserType.VENDEDOR
        )
        admin = User(
            email="admin@example.com",
            password_hash="hash",
            user_type=UserType.ADMIN
        )
        superuser = User(
            email="super@example.com",
            password_hash="hash",
            user_type=UserType.SUPERUSER
        )

        # ASSERT
        assert buyer.user_type == UserType.COMPRADOR
        assert vendor.user_type == UserType.VENDEDOR
        assert admin.user_type == UserType.ADMIN
        assert superuser.user_type == UserType.SUPERUSER

    def test_vendor_status_enum_values(self):
        """Test VendorStatus enum has correct values."""
        # ARRANGE & ACT & ASSERT
        assert VendorStatus.DRAFT.value == "draft"
        assert VendorStatus.PENDING_DOCUMENTS.value == "pending_documents"
        assert VendorStatus.PENDING_APPROVAL.value == "pending_approval"
        assert VendorStatus.APPROVED.value == "approved"
        assert VendorStatus.REJECTED.value == "rejected"


@pytest.mark.unit
class TestUserOTPMethods:
    """Test User model OTP-related methods."""

    def test_is_otp_valid_with_valid_otp(self):
        """Test is_otp_valid returns True for valid OTP."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            otp_expires_at=datetime.utcnow() + timedelta(minutes=10)
        )

        # ACT
        is_valid = user.is_otp_valid()

        # ASSERT
        assert is_valid is True

    def test_is_otp_valid_with_expired_otp(self):
        """Test is_otp_valid returns False for expired OTP."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            otp_expires_at=datetime.utcnow() - timedelta(minutes=10)
        )

        # ACT
        is_valid = user.is_otp_valid()

        # ASSERT
        assert is_valid is False

    def test_is_otp_valid_with_no_otp_expiry(self):
        """Test is_otp_valid returns False when no OTP expiry is set."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            otp_expires_at=None
        )

        # ACT
        is_valid = user.is_otp_valid()

        # ASSERT
        assert is_valid is False

    def test_can_request_otp_no_previous_request(self):
        """Test can_request_otp returns True when no previous OTP was sent."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            last_otp_sent=None
        )

        # ACT
        can_request = user.can_request_otp()

        # ASSERT
        assert can_request is True

    def test_can_request_otp_after_cooldown(self):
        """Test can_request_otp returns True after cooldown period."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            last_otp_sent=datetime.utcnow() - timedelta(minutes=2)  # 2 minutes ago
        )

        # ACT
        can_request = user.can_request_otp()

        # ASSERT
        assert can_request is True

    def test_can_request_otp_during_cooldown(self):
        """Test can_request_otp returns False during cooldown period."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            last_otp_sent=datetime.utcnow() - timedelta(seconds=30)  # 30 seconds ago
        )

        # ACT
        can_request = user.can_request_otp()

        # ASSERT
        assert can_request is False

    def test_reset_otp_attempts(self):
        """Test reset_otp_attempts resets counter to zero."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            otp_attempts=5
        )

        # ACT
        user.reset_otp_attempts()

        # ASSERT
        assert user.otp_attempts == 0

    def test_increment_otp_attempts(self):
        """Test increment_otp_attempts increases counter."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            otp_attempts=2
        )

        # ACT
        user.increment_otp_attempts()

        # ASSERT
        assert user.otp_attempts == 3

    def test_is_otp_blocked_under_limit(self):
        """Test is_otp_blocked returns False when under attempt limit."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            otp_attempts=4  # Under the 5 attempt limit
        )

        # ACT
        is_blocked = user.is_otp_blocked()

        # ASSERT
        assert is_blocked is False

    def test_is_otp_blocked_at_limit(self):
        """Test is_otp_blocked returns True when at attempt limit."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            otp_attempts=5  # At the 5 attempt limit
        )

        # ACT
        is_blocked = user.is_otp_blocked()

        # ASSERT
        assert is_blocked is True

    def test_is_otp_blocked_over_limit(self):
        """Test is_otp_blocked returns True when over attempt limit."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            otp_attempts=10  # Over the 5 attempt limit
        )

        # ACT
        is_blocked = user.is_otp_blocked()

        # ASSERT
        assert is_blocked is True


@pytest.mark.unit
class TestUserPasswordResetMethods:
    """Test User model password reset-related methods."""

    def test_can_request_password_reset_no_previous_request(self):
        """Test can_request_password_reset returns True when no previous request."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            last_reset_request=None
        )

        # ACT
        can_request = user.can_request_password_reset()

        # ASSERT
        assert can_request is True

    def test_can_request_password_reset_after_cooldown(self):
        """Test can_request_password_reset returns True after cooldown."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            last_reset_request=datetime.utcnow() - timedelta(minutes=6)  # 6 minutes ago
        )

        # ACT
        can_request = user.can_request_password_reset()

        # ASSERT
        assert can_request is True

    def test_can_request_password_reset_during_cooldown(self):
        """Test can_request_password_reset returns False during cooldown."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            last_reset_request=datetime.utcnow() - timedelta(minutes=2)  # 2 minutes ago
        )

        # ACT
        can_request = user.can_request_password_reset()

        # ASSERT
        assert can_request is False

    def test_is_reset_token_valid_with_valid_token(self):
        """Test is_reset_token_valid returns True for valid token."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            reset_token="valid_token",
            reset_token_expires_at=datetime.utcnow() + timedelta(hours=1)
        )

        # ACT
        is_valid = user.is_reset_token_valid()

        # ASSERT
        assert is_valid is True

    def test_is_reset_token_valid_with_expired_token(self):
        """Test is_reset_token_valid returns False for expired token."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            reset_token="expired_token",
            reset_token_expires_at=datetime.utcnow() - timedelta(hours=1)
        )

        # ACT
        is_valid = user.is_reset_token_valid()

        # ASSERT
        assert is_valid is False

    def test_is_reset_token_valid_with_no_token(self):
        """Test is_reset_token_valid returns False when no token is set."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            reset_token=None,
            reset_token_expires_at=None
        )

        # ACT
        is_valid = user.is_reset_token_valid()

        # ASSERT
        assert is_valid is False

    def test_is_reset_blocked_under_limit(self):
        """Test is_reset_blocked returns False when under attempt limit."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            reset_attempts=2  # Under the 3 attempt limit
        )

        # ACT
        is_blocked = user.is_reset_blocked()

        # ASSERT
        assert is_blocked is False

    def test_is_reset_blocked_at_limit(self):
        """Test is_reset_blocked returns True when at attempt limit."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            reset_attempts=3  # At the 3 attempt limit
        )

        # ACT
        is_blocked = user.is_reset_blocked()

        # ASSERT
        assert is_blocked is True

    def test_increment_reset_attempts(self):
        """Test increment_reset_attempts increases counter."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            reset_attempts=1
        )

        # ACT
        user.increment_reset_attempts()

        # ASSERT
        assert user.reset_attempts == 2

    def test_clear_reset_data(self):
        """Test clear_reset_data clears all reset-related fields."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            reset_token="some_token",
            reset_token_expires_at=datetime.utcnow() + timedelta(hours=1),
            reset_attempts=2
        )

        # ACT
        user.clear_reset_data()

        # ASSERT
        assert user.reset_token is None
        assert user.reset_token_expires_at is None
        assert user.reset_attempts == 0


@pytest.mark.unit
class TestUserModelToDict:
    """Test User model to_dict method."""

    def test_to_dict_includes_expected_fields(self):
        """Test to_dict method includes all expected fields."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            nombre="John",
            apellido="Doe",
            user_type=UserType.VENDEDOR,
            telefono="+573001234567",
            ciudad="Bogotá"
        )

        # ACT
        user_dict = user.to_dict()

        # ASSERT
        expected_fields = [
            'id', 'email', 'nombre', 'apellido', 'user_type',
            'is_active', 'is_verified', 'telefono', 'ciudad',
            'email_verified', 'phone_verified', 'created_at',
            'last_login', 'full_name'
        ]

        for field in expected_fields:
            assert field in user_dict

    def test_to_dict_excludes_sensitive_fields(self):
        """Test to_dict method excludes sensitive fields."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="sensitive_hash",
            reset_token="sensitive_token",
            otp_secret="123456"
        )

        # ACT
        user_dict = user.to_dict()

        # ASSERT
        sensitive_fields = ['password_hash', 'reset_token', 'otp_secret']

        for field in sensitive_fields:
            assert field not in user_dict

    def test_to_dict_with_full_name(self):
        """Test to_dict includes computed full_name field."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            nombre="Jane",
            apellido="Smith"
        )

        # ACT
        user_dict = user.to_dict()

        # ASSERT
        assert user_dict['full_name'] == "Jane Smith"

    def test_to_dict_user_type_serialization(self):
        """Test to_dict properly serializes user_type enum."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            user_type=UserType.ADMIN
        )

        # ACT
        user_dict = user.to_dict()

        # ASSERT
        assert user_dict['user_type'] == "ADMIN"


@pytest.mark.unit
class TestUserModelEdgeCases:
    """Test User model edge cases and error conditions."""

    def test_user_with_empty_email(self):
        """Test User model behavior with empty email."""
        # ARRANGE & ACT
        user = User(
            email="",
            password_hash="hash"
        )

        # ASSERT
        assert user.email == ""

    def test_user_with_very_long_email(self):
        """Test User model with very long email."""
        # ARRANGE
        long_email = "a" * 250 + "@example.com"

        # ACT
        user = User(
            email=long_email,
            password_hash="hash"
        )

        # ASSERT
        assert user.email == long_email

    def test_user_with_unicode_in_name(self):
        """Test User model with unicode characters in name."""
        # ARRANGE & ACT
        user = User(
            email="test@example.com",
            password_hash="hash",
            nombre="José María",
            apellido="Ñoño"
        )

        # ASSERT
        assert user.nombre == "José María"
        assert user.apellido == "Ñoño"
        assert user.full_name == "José María Ñoño"

    def test_user_with_extreme_otp_attempts(self):
        """Test User model with extreme OTP attempt counts."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            otp_attempts=999999
        )

        # ACT & ASSERT
        assert user.is_otp_blocked() is True

        # Reset and test zero
        user.reset_otp_attempts()
        assert user.otp_attempts == 0
        assert user.is_otp_blocked() is False

    def test_user_with_extreme_reset_attempts(self):
        """Test User model with extreme reset attempt counts."""
        # ARRANGE
        user = User(
            email="test@example.com",
            password_hash="hash",
            reset_attempts=999999
        )

        # ACT & ASSERT
        assert user.is_reset_blocked() is True

    def test_user_datetime_handling_with_timezone(self):
        """Test User model datetime handling with different timezone scenarios."""
        # ARRANGE
        now = datetime.utcnow()
        user = User(
            email="test@example.com",
            password_hash="hash",
            otp_expires_at=now + timedelta(minutes=10),
            reset_token="valid_token",
            reset_token_expires_at=now + timedelta(hours=1),
            last_otp_sent=now - timedelta(minutes=2),
            last_reset_request=now - timedelta(minutes=10)
        )

        # ACT & ASSERT
        assert user.is_otp_valid() is True
        assert user.is_reset_token_valid() is True
        assert user.can_request_otp() is True  # 2 minutes > 1 minute cooldown
        assert user.can_request_password_reset() is True  # 10 minutes > 5 minute cooldown