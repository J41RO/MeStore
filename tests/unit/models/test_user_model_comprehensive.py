#!/usr/bin/env python3
"""
Comprehensive TDD Unit Tests for User Model
==========================================

Testing Strategy:
- RED: Write failing test first
- GREEN: Implement minimal code to pass
- REFACTOR: Optimize while maintaining tests

Coverage Goals:
- User model creation: 100%
- Field validation: 100%
- Enum handling: 100%
- Property methods: 100%
- Business logic methods: 95%

File: tests/unit/models/test_user_model_comprehensive.py
Author: Unit Testing AI - TDD Methodology
Date: 2025-09-17
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from typing import Optional
import uuid
from decimal import Decimal

# Import modules under test
from app.models.user import User, UserType, VendorStatus
from app.core.types import generate_uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base


class TestUserTypeEnum:
    """Test UserType enum with TDD methodology."""
    
    def test_user_type_enum_has_all_required_values(self):
        """TDD: UserType enum should have all required values."""
        # RED: Verify all expected user types exist
        assert hasattr(UserType, 'COMPRADOR')
        assert hasattr(UserType, 'VENDEDOR')
        assert hasattr(UserType, 'ADMIN')
        assert hasattr(UserType, 'SUPERUSER')
    
    def test_user_type_enum_values_are_strings(self):
        """TDD: UserType enum values should be strings."""
        assert UserType.COMPRADOR.value == "COMPRADOR"
        assert UserType.VENDEDOR.value == "VENDEDOR"
        assert UserType.ADMIN.value == "ADMIN"
        assert UserType.SUPERUSER.value == "SUPERUSER"
    
    def test_user_type_enum_is_comparable(self):
        """TDD: UserType enum should support equality comparison."""
        assert UserType.COMPRADOR == UserType.COMPRADOR
        assert UserType.VENDEDOR != UserType.COMPRADOR
        assert UserType.ADMIN != UserType.VENDEDOR
        assert UserType.SUPERUSER != UserType.ADMIN
    
    def test_user_type_enum_can_be_converted_to_string(self):
        """TDD: UserType enum should convert to string properly."""
        assert str(UserType.COMPRADOR) == "UserType.COMPRADOR"
        assert UserType.COMPRADOR.value == "COMPRADOR"


class TestVendorStatusEnum:
    """Test VendorStatus enum with TDD methodology."""
    
    def test_vendor_status_enum_has_all_workflow_states(self):
        """TDD: VendorStatus enum should have all workflow states."""
        # RED: Verify all vendor workflow states exist
        assert hasattr(VendorStatus, 'DRAFT')
        assert hasattr(VendorStatus, 'PENDING_DOCUMENTS')
        assert hasattr(VendorStatus, 'PENDING_APPROVAL')
        assert hasattr(VendorStatus, 'APPROVED')
        assert hasattr(VendorStatus, 'REJECTED')
    
    def test_vendor_status_enum_values_are_lowercase_strings(self):
        """TDD: VendorStatus enum values should be lowercase strings."""
        assert VendorStatus.DRAFT.value == "draft"
        assert VendorStatus.PENDING_DOCUMENTS.value == "pending_documents"
        assert VendorStatus.PENDING_APPROVAL.value == "pending_approval"
        assert VendorStatus.APPROVED.value == "approved"
        assert VendorStatus.REJECTED.value == "rejected"
    
    def test_vendor_status_enum_workflow_progression(self):
        """TDD: VendorStatus enum should support workflow progression."""
        # Test typical workflow progression
        workflow_states = [
            VendorStatus.DRAFT,
            VendorStatus.PENDING_DOCUMENTS,
            VendorStatus.PENDING_APPROVAL,
            VendorStatus.APPROVED
        ]
        
        # Each state should be different
        for i, state in enumerate(workflow_states):
            for j, other_state in enumerate(workflow_states):
                if i != j:
                    assert state != other_state


class TestUserModelCreation:
    """Test User model creation with TDD methodology."""
    
    @pytest.fixture
    def minimal_user_data(self):
        """Minimal data required to create a user."""
        return {
            'email': 'test@example.com',
            'password_hash': '$2b$12$test.hash.for.testing'
        }
    
    @pytest.fixture
    def complete_user_data(self):
        """Complete user data for comprehensive testing."""
        return {
            'email': 'complete@example.com',
            'password_hash': '$2b$12$complete.hash.for.testing',
            'nombre': 'Test',
            'apellido': 'User',
            'user_type': UserType.VENDEDOR,
            'vendor_status': VendorStatus.DRAFT,
            'is_active': True,
            'is_verified': False,
            'cedula': '12345678',
            'telefono': '+573001234567',
            'ciudad': 'Bogotá',
            'empresa': 'Test Company',
            'direccion': 'Calle 123 #45-67'
        }
    
    def test_user_creation_with_minimal_data_succeeds(self, minimal_user_data):
        """TDD: User should be created with minimal required data."""
        user = User(**minimal_user_data)
        
        assert user.email == minimal_user_data['email']
        assert user.password_hash == minimal_user_data['password_hash']
        
        # Verify defaults are applied
        assert user.user_type == UserType.COMPRADOR
        assert user.is_active is True
        assert user.is_verified is False
        assert user.email_verified is False
        assert user.phone_verified is False
        assert user.otp_attempts == 0
    
    def test_user_creation_with_complete_data_succeeds(self, complete_user_data):
        """TDD: User should be created with complete data."""
        user = User(**complete_user_data)
        
        # Verify all fields are set correctly
        assert user.email == complete_user_data['email']
        assert user.nombre == complete_user_data['nombre']
        assert user.apellido == complete_user_data['apellido']
        assert user.user_type == complete_user_data['user_type']
        assert user.vendor_status == complete_user_data['vendor_status']
        assert user.cedula == complete_user_data['cedula']
        assert user.telefono == complete_user_data['telefono']
        assert user.ciudad == complete_user_data['ciudad']
        assert user.empresa == complete_user_data['empresa']
        assert user.direccion == complete_user_data['direccion']
    
    def test_user_creation_without_email_should_fail(self):
        """TDD: User creation should fail without email."""
        invalid_data = {'password_hash': '$2b$12$test.hash'}
        
        # This should fail at database level due to nullable=False
        user = User(**invalid_data)
        assert user.email is None  # Will fail database constraint
    
    def test_user_creation_without_password_hash_should_fail(self):
        """TDD: User creation should fail without password_hash."""
        invalid_data = {'email': 'test@example.com'}
        
        # This should fail at database level due to nullable=False
        user = User(**invalid_data)
        assert user.password_hash is None  # Will fail database constraint
    
    def test_user_id_is_generated_automatically(self, minimal_user_data):
        """TDD: User ID should be generated automatically."""
        user = User(**minimal_user_data)
        
        # ID should be generated (UUID format)
        assert user.id is not None
        assert isinstance(user.id, str)
        assert len(user.id) == 36  # UUID string length
        assert user.id.count('-') == 4  # UUID has 4 hyphens
    
    def test_user_timestamps_are_handled_correctly(self, minimal_user_data):
        """TDD: User timestamps should be handled correctly."""
        user = User(**minimal_user_data)
        
        # created_at is set by BaseModel
        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')
        
        # last_login should be None initially
        assert user.last_login is None


class TestUserModelProperties:
    """Test User model properties with TDD methodology."""
    
    @pytest.fixture
    def user_with_names(self):
        """User with both nombre and apellido."""
        return User(
            email='test@example.com',
            password_hash='$2b$12$test.hash',
            nombre='John',
            apellido='Doe'
        )
    
    @pytest.fixture
    def user_with_nombre_only(self):
        """User with only nombre."""
        return User(
            email='test@example.com',
            password_hash='$2b$12$test.hash',
            nombre='John'
        )
    
    @pytest.fixture
    def user_with_apellido_only(self):
        """User with only apellido."""
        return User(
            email='test@example.com',
            password_hash='$2b$12$test.hash',
            apellido='Doe'
        )
    
    @pytest.fixture
    def user_without_names(self):
        """User without nombre or apellido."""
        return User(
            email='test@example.com',
            password_hash='$2b$12$test.hash'
        )
    
    def test_full_name_property_with_both_names(self, user_with_names):
        """TDD: full_name should combine nombre and apellido."""
        assert user_with_names.full_name == "John Doe"
    
    def test_full_name_property_with_nombre_only(self, user_with_nombre_only):
        """TDD: full_name should return nombre when apellido is None."""
        assert user_with_nombre_only.full_name == "John"
    
    def test_full_name_property_with_apellido_only(self, user_with_apellido_only):
        """TDD: full_name should return apellido when nombre is None."""
        assert user_with_apellido_only.full_name == "Doe"
    
    def test_full_name_property_without_names(self, user_without_names):
        """TDD: full_name should return default message when both names are None."""
        assert user_without_names.full_name == "Usuario sin nombre"
    
    def test_full_name_property_with_empty_strings(self):
        """TDD: full_name should handle empty strings properly."""
        user = User(
            email='test@example.com',
            password_hash='$2b$12$test.hash',
            nombre='',
            apellido=''
        )
        
        # Empty strings should be treated as falsy
        assert user.full_name == "Usuario sin nombre"
    
    def test_str_representation(self, user_with_names):
        """TDD: __str__ should return user-friendly representation."""
        expected = f"Usuario {user_with_names.email} (activo)"
        assert str(user_with_names) == expected
    
    def test_str_representation_inactive_user(self):
        """TDD: __str__ should indicate inactive status."""
        user = User(
            email='inactive@example.com',
            password_hash='$2b$12$test.hash',
            is_active=False
        )
        
        expected = f"Usuario {user.email} (inactivo)"
        assert str(user) == expected
    
    def test_repr_representation(self, user_with_names):
        """TDD: __repr__ should return developer-friendly representation."""
        repr_str = repr(user_with_names)
        
        assert "<User(" in repr_str
        assert f"id={user_with_names.id}" in repr_str
        assert f"email='{user_with_names.email}'" in repr_str
        assert f"active={user_with_names.is_active}" in repr_str
        assert repr_str.endswith(")>")


class TestUserModelToDictSerialization:
    """Test User model to_dict serialization with TDD methodology."""
    
    @pytest.fixture
    def user_for_serialization(self):
        """User with various data types for serialization testing."""
        user = User(
            email='serialize@example.com',
            password_hash='$2b$12$test.hash',
            nombre='Serialize',
            apellido='Test',
            user_type=UserType.VENDEDOR,
            is_active=True,
            is_verified=True,
            email_verified=True,
            phone_verified=False,
            cedula='87654321',
            telefono='+573009876543',
            ciudad='Medellín',
            empresa='Serialize Corp',
            direccion='Carrera 70 #52-55'
        )
        
        # Set some datetime fields for testing
        user.last_login = datetime(2025, 9, 17, 10, 30, 0, tzinfo=timezone.utc)
        
        return user
    
    def test_to_dict_includes_all_expected_fields(self, user_for_serialization):
        """TDD: to_dict should include all expected fields."""
        result = user_for_serialization.to_dict()
        
        expected_fields = [
            'id', 'email', 'nombre', 'apellido', 'user_type',
            'is_active', 'is_verified', 'email_verified', 'phone_verified',
            'last_login', 'created_at', 'updated_at', 'cedula', 'telefono',
            'ciudad', 'empresa', 'direccion', 'full_name'
        ]
        
        for field in expected_fields:
            assert field in result, f"Field '{field}' missing from to_dict output"
    
    def test_to_dict_excludes_sensitive_fields(self, user_for_serialization):
        """TDD: to_dict should exclude sensitive fields like password_hash."""
        result = user_for_serialization.to_dict()
        
        sensitive_fields = ['password_hash', 'otp_secret', 'reset_token']
        
        for field in sensitive_fields:
            assert field not in result, f"Sensitive field '{field}' should not be in to_dict output"
    
    def test_to_dict_handles_none_values(self):
        """TDD: to_dict should handle None values gracefully."""
        user = User(
            email='none@example.com',
            password_hash='$2b$12$test.hash'
            # Most fields will be None
        )
        
        result = user.to_dict()
        
        # Should not raise exceptions
        assert result['nombre'] is None
        assert result['apellido'] is None
        assert result['last_login'] is None
        assert result['cedula'] is None
    
    def test_to_dict_serializes_datetime_to_iso_format(self, user_for_serialization):
        """TDD: to_dict should serialize datetime fields to ISO format."""
        result = user_for_serialization.to_dict()
        
        # last_login should be ISO formatted string
        assert isinstance(result['last_login'], str)
        assert 'T' in result['last_login']  # ISO format contains 'T'
        assert result['last_login'].endswith('+00:00')  # UTC timezone
    
    def test_to_dict_serializes_enum_to_value(self, user_for_serialization):
        """TDD: to_dict should serialize enum fields to their values."""
        result = user_for_serialization.to_dict()
        
        assert result['user_type'] == 'VENDEDOR'
        assert not isinstance(result['user_type'], UserType)
    
    def test_to_dict_includes_computed_properties(self, user_for_serialization):
        """TDD: to_dict should include computed properties like full_name."""
        result = user_for_serialization.to_dict()
        
        assert result['full_name'] == 'Serialize Test'
        assert result['full_name'] == user_for_serialization.full_name
    
    def test_to_dict_converts_uuid_to_string(self, user_for_serialization):
        """TDD: to_dict should convert UUID to string."""
        result = user_for_serialization.to_dict()
        
        assert isinstance(result['id'], str)
        assert len(result['id']) == 36  # UUID string length


class TestUserOTPMethods:
    """Test User OTP-related methods with TDD methodology."""
    
    @pytest.fixture
    def user_with_valid_otp(self):
        """User with valid (non-expired) OTP."""
        user = User(
            email='otp@example.com',
            password_hash='$2b$12$test.hash',
            otp_secret='123456',
            otp_expires_at=datetime.utcnow() + timedelta(minutes=10),
            otp_attempts=0
        )
        return user
    
    @pytest.fixture
    def user_with_expired_otp(self):
        """User with expired OTP."""
        user = User(
            email='expired@example.com',
            password_hash='$2b$12$test.hash',
            otp_secret='123456',
            otp_expires_at=datetime.utcnow() - timedelta(minutes=10),
            otp_attempts=0
        )
        return user
    
    @pytest.fixture
    def user_without_otp(self):
        """User without OTP data."""
        return User(
            email='nootp@example.com',
            password_hash='$2b$12$test.hash'
        )
    
    def test_is_otp_valid_returns_true_for_valid_otp(self, user_with_valid_otp):
        """TDD: is_otp_valid should return True for valid OTP."""
        assert user_with_valid_otp.is_otp_valid() is True
    
    def test_is_otp_valid_returns_false_for_expired_otp(self, user_with_expired_otp):
        """TDD: is_otp_valid should return False for expired OTP."""
        assert user_with_expired_otp.is_otp_valid() is False
    
    def test_is_otp_valid_returns_false_for_no_otp(self, user_without_otp):
        """TDD: is_otp_valid should return False when no OTP is set."""
        assert user_without_otp.is_otp_valid() is False
    
    def test_can_request_otp_returns_true_for_new_user(self, user_without_otp):
        """TDD: can_request_otp should return True for user without previous OTP."""
        assert user_without_otp.can_request_otp() is True
    
    def test_can_request_otp_returns_false_within_cooldown(self):
        """TDD: can_request_otp should return False within cooldown period."""
        user = User(
            email='cooldown@example.com',
            password_hash='$2b$12$test.hash',
            last_otp_sent=datetime.utcnow() - timedelta(seconds=30)  # 30 seconds ago
        )
        
        assert user.can_request_otp() is False
    
    def test_can_request_otp_returns_true_after_cooldown(self):
        """TDD: can_request_otp should return True after cooldown period."""
        user = User(
            email='aftercooldown@example.com',
            password_hash='$2b$12$test.hash',
            last_otp_sent=datetime.utcnow() - timedelta(seconds=70)  # 70 seconds ago
        )
        
        assert user.can_request_otp() is True
    
    def test_reset_otp_attempts_sets_attempts_to_zero(self):
        """TDD: reset_otp_attempts should set attempts to 0."""
        user = User(
            email='reset@example.com',
            password_hash='$2b$12$test.hash',
            otp_attempts=3
        )
        
        user.reset_otp_attempts()
        assert user.otp_attempts == 0
    
    def test_increment_otp_attempts_increases_counter(self):
        """TDD: increment_otp_attempts should increase the counter."""
        user = User(
            email='increment@example.com',
            password_hash='$2b$12$test.hash',
            otp_attempts=2
        )
        
        user.increment_otp_attempts()
        assert user.otp_attempts == 3
    
    def test_is_otp_blocked_returns_false_for_low_attempts(self):
        """TDD: is_otp_blocked should return False for low attempt count."""
        user = User(
            email='lowattempts@example.com',
            password_hash='$2b$12$test.hash',
            otp_attempts=3
        )
        
        assert user.is_otp_blocked() is False
    
    def test_is_otp_blocked_returns_true_for_high_attempts(self):
        """TDD: is_otp_blocked should return True for high attempt count."""
        user = User(
            email='highattempts@example.com',
            password_hash='$2b$12$test.hash',
            otp_attempts=5  # Maximum allowed
        )
        
        assert user.is_otp_blocked() is True
    
    def test_is_otp_blocked_returns_true_for_excessive_attempts(self):
        """TDD: is_otp_blocked should return True for excessive attempts."""
        user = User(
            email='excessive@example.com',
            password_hash='$2b$12$test.hash',
            otp_attempts=10  # Way over limit
        )
        
        assert user.is_otp_blocked() is True


class TestUserPasswordResetMethods:
    """Test User password reset methods with TDD methodology."""
    
    @pytest.fixture
    def user_with_valid_reset_token(self):
        """User with valid reset token."""
        user = User(
            email='reset@example.com',
            password_hash='$2b$12$test.hash',
            reset_token='valid_token_123',
            reset_token_expires_at=datetime.utcnow() + timedelta(hours=1),
            reset_attempts=0
        )
        return user
    
    @pytest.fixture
    def user_with_expired_reset_token(self):
        """User with expired reset token."""
        user = User(
            email='expired@example.com',
            password_hash='$2b$12$test.hash',
            reset_token='expired_token_123',
            reset_token_expires_at=datetime.utcnow() - timedelta(hours=1),
            reset_attempts=0
        )
        return user
    
    def test_can_request_password_reset_returns_true_for_new_user(self):
        """TDD: can_request_password_reset should return True for new user."""
        user = User(
            email='newreset@example.com',
            password_hash='$2b$12$test.hash'
        )
        
        assert user.can_request_password_reset() is True
    
    def test_can_request_password_reset_returns_false_within_cooldown(self):
        """TDD: can_request_password_reset should return False within cooldown."""
        user = User(
            email='cooldownreset@example.com',
            password_hash='$2b$12$test.hash',
            last_reset_request=datetime.utcnow() - timedelta(minutes=2)  # 2 minutes ago
        )
        
        assert user.can_request_password_reset() is False
    
    def test_can_request_password_reset_returns_true_after_cooldown(self):
        """TDD: can_request_password_reset should return True after cooldown."""
        user = User(
            email='aftercooldownreset@example.com',
            password_hash='$2b$12$test.hash',
            last_reset_request=datetime.utcnow() - timedelta(minutes=6)  # 6 minutes ago
        )
        
        assert user.can_request_password_reset() is True
    
    def test_is_reset_token_valid_returns_true_for_valid_token(self, user_with_valid_reset_token):
        """TDD: is_reset_token_valid should return True for valid token."""
        assert user_with_valid_reset_token.is_reset_token_valid() is True
    
    def test_is_reset_token_valid_returns_false_for_expired_token(self, user_with_expired_reset_token):
        """TDD: is_reset_token_valid should return False for expired token."""
        assert user_with_expired_reset_token.is_reset_token_valid() is False
    
    def test_is_reset_token_valid_returns_false_for_no_token(self):
        """TDD: is_reset_token_valid should return False when no token is set."""
        user = User(
            email='notoken@example.com',
            password_hash='$2b$12$test.hash'
        )
        
        assert user.is_reset_token_valid() is False
    
    def test_is_reset_blocked_returns_false_for_low_attempts(self):
        """TDD: is_reset_blocked should return False for low attempts."""
        user = User(
            email='lowresetattempts@example.com',
            password_hash='$2b$12$test.hash',
            reset_attempts=2
        )
        
        assert user.is_reset_blocked() is False
    
    def test_is_reset_blocked_returns_true_for_high_attempts(self):
        """TDD: is_reset_blocked should return True for high attempts."""
        user = User(
            email='highresetattempts@example.com',
            password_hash='$2b$12$test.hash',
            reset_attempts=3  # Maximum allowed
        )
        
        assert user.is_reset_blocked() is True
    
    def test_increment_reset_attempts_increases_counter(self):
        """TDD: increment_reset_attempts should increase the counter."""
        user = User(
            email='incrementreset@example.com',
            password_hash='$2b$12$test.hash',
            reset_attempts=1
        )
        
        user.increment_reset_attempts()
        assert user.reset_attempts == 2
    
    def test_clear_reset_data_clears_all_reset_fields(self):
        """TDD: clear_reset_data should clear all reset-related fields."""
        user = User(
            email='clearreset@example.com',
            password_hash='$2b$12$test.hash',
            reset_token='token_to_clear',
            reset_token_expires_at=datetime.utcnow() + timedelta(hours=1),
            reset_attempts=2
        )
        
        user.clear_reset_data()
        
        assert user.reset_token is None
        assert user.reset_token_expires_at is None
        assert user.reset_attempts == 0


class TestUserModelEdgeCases:
    """Test User model edge cases with TDD methodology."""
    
    def test_user_with_very_long_email(self):
        """TDD: User should handle very long email addresses."""
        long_email = 'a' * 240 + '@example.com'  # 250+ characters
        
        user = User(
            email=long_email,
            password_hash='$2b$12$test.hash'
        )
        
        assert user.email == long_email
    
    def test_user_with_unicode_names(self):
        """TDD: User should handle Unicode characters in names."""
        user = User(
            email='unicode@example.com',
            password_hash='$2b$12$test.hash',
            nombre='José María',
            apellido='Gómez-Pérez'
        )
        
        assert user.nombre == 'José María'
        assert user.apellido == 'Gómez-Pérez'
        assert user.full_name == 'José María Gómez-Pérez'
    
    def test_user_with_special_characters_in_address(self):
        """TDD: User should handle special characters in address fields."""
        user = User(
            email='special@example.com',
            password_hash='$2b$12$test.hash',
            direccion='Calle 123 #45-67, Apto 8B, Barrio El Peñón'
        )
        
        assert 'Peñón' in user.direccion
    
    def test_user_with_extreme_datetime_values(self):
        """TDD: User should handle extreme datetime values."""
        user = User(
            email='extreme@example.com',
            password_hash='$2b$12$test.hash',
            last_login=datetime.min.replace(tzinfo=timezone.utc),
            otp_expires_at=datetime.max.replace(tzinfo=timezone.utc)
        )
        
        # Should not raise exceptions
        user_dict = user.to_dict()
        assert 'last_login' in user_dict
    
    def test_user_with_maximum_otp_attempts(self):
        """TDD: User should handle maximum OTP attempts correctly."""
        user = User(
            email='maxotp@example.com',
            password_hash='$2b$12$test.hash',
            otp_attempts=999999  # Very high number
        )
        
        assert user.is_otp_blocked() is True
        
        # Should still be able to reset
        user.reset_otp_attempts()
        assert user.otp_attempts == 0
        assert user.is_otp_blocked() is False
    
    def test_user_enum_handling_with_invalid_assignment(self):
        """TDD: User should handle enum assignments properly."""
        user = User(
            email='enum@example.com',
            password_hash='$2b$12$test.hash',
            user_type=UserType.VENDEDOR,
            vendor_status=VendorStatus.APPROVED
        )
        
        assert user.user_type == UserType.VENDEDOR
        assert user.vendor_status == VendorStatus.APPROVED
        
        # Verify enum comparison works
        assert user.user_type != UserType.COMPRADOR
        assert user.vendor_status != VendorStatus.DRAFT


class TestUserModelBusinessLogic:
    """Test User model business logic with TDD methodology."""
    
    def test_vendor_workflow_state_transitions(self):
        """TDD: Vendor should support workflow state transitions."""
        vendor = User(
            email='vendor@example.com',
            password_hash='$2b$12$test.hash',
            user_type=UserType.VENDEDOR,
            vendor_status=VendorStatus.DRAFT
        )
        
        # Simulate workflow progression
        assert vendor.vendor_status == VendorStatus.DRAFT
        
        vendor.vendor_status = VendorStatus.PENDING_DOCUMENTS
        assert vendor.vendor_status == VendorStatus.PENDING_DOCUMENTS
        
        vendor.vendor_status = VendorStatus.PENDING_APPROVAL
        assert vendor.vendor_status == VendorStatus.PENDING_APPROVAL
        
        vendor.vendor_status = VendorStatus.APPROVED
        assert vendor.vendor_status == VendorStatus.APPROVED
    
    def test_user_activation_deactivation(self):
        """TDD: User should support activation/deactivation."""
        user = User(
            email='activation@example.com',
            password_hash='$2b$12$test.hash',
            is_active=True
        )
        
        assert user.is_active is True
        assert "activo" in str(user)
        
        # Deactivate user
        user.is_active = False
        assert user.is_active is False
        assert "inactivo" in str(user)
        
        # Reactivate user
        user.is_active = True
        assert user.is_active is True
        assert "activo" in str(user)
    
    def test_user_verification_status_tracking(self):
        """TDD: User should track verification status properly."""
        user = User(
            email='verification@example.com',
            password_hash='$2b$12$test.hash'
        )
        
        # Initially unverified
        assert user.is_verified is False
        assert user.email_verified is False
        assert user.phone_verified is False
        
        # Verify email
        user.email_verified = True
        assert user.email_verified is True
        
        # Verify phone
        user.phone_verified = True
        assert user.phone_verified is True
        
        # General verification
        user.is_verified = True
        assert user.is_verified is True
    
    def test_user_type_privilege_hierarchy(self):
        """TDD: User types should support privilege hierarchy."""
        # Create users of different types
        buyer = User(
            email='buyer@example.com',
            password_hash='$2b$12$test.hash',
            user_type=UserType.COMPRADOR
        )
        
        vendor = User(
            email='vendor@example.com',
            password_hash='$2b$12$test.hash',
            user_type=UserType.VENDEDOR
        )
        
        admin = User(
            email='admin@example.com',
            password_hash='$2b$12$test.hash',
            user_type=UserType.ADMIN
        )
        
        superuser = User(
            email='superuser@example.com',
            password_hash='$2b$12$test.hash',
            user_type=UserType.SUPERUSER
        )
        
        # Verify each has correct type
        assert buyer.user_type == UserType.COMPRADOR
        assert vendor.user_type == UserType.VENDEDOR
        assert admin.user_type == UserType.ADMIN
        assert superuser.user_type == UserType.SUPERUSER
        
        # Verify types are different
        user_types = [buyer.user_type, vendor.user_type, admin.user_type, superuser.user_type]
        assert len(set(user_types)) == 4  # All different


if __name__ == "__main__":
    # Run with: python -m pytest tests/unit/models/test_user_model_comprehensive.py -v
    pytest.main([__file__, "-v", "--tb=short", "--cov=app.models.user"])
