#!/usr/bin/env python3
"""
Comprehensive TDD Unit Tests for Role-Based Access Control
=========================================================

Testing Strategy:
- RED: Write failing test first
- GREEN: Implement minimal code to pass
- REFACTOR: Optimize while maintaining tests

Coverage Goals:
- Role validation: 100%
- Permission checking: 100%
- Access control enforcement: 100%
- User type verification: 100%
- Authorization edge cases: 95%

File: tests/unit/auth/test_role_based_access.py
Author: Unit Testing AI - TDD Methodology
Date: 2025-09-17
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Optional, List
import uuid
from datetime import datetime, timezone

# Import modules under test
from app.api.v1.deps.auth import (
    get_current_user,
    get_current_active_user,
    require_roles,
    require_admin,
    require_vendor,
    require_buyer
)
from app.models.user import User, UserType
from app.core.security import create_access_token, decode_access_token
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class TestUserTypeValidation:
    """Test user type validation with TDD methodology."""
    
    @pytest.fixture
    def mock_user_admin(self):
        """Mock admin user."""
        user = Mock(spec=User)
        user.id = uuid.uuid4()
        user.email = "admin@example.com"
        user.user_type = UserType.SUPERUSER
        user.is_active = True
        user.nombre = "Admin"
        user.apellido = "User"
        return user
    
    @pytest.fixture
    def mock_user_vendor(self):
        """Mock vendor user."""
        user = Mock(spec=User)
        user.id = uuid.uuid4()
        user.email = "vendor@example.com"
        user.user_type = UserType.VENDOR
        user.is_active = True
        user.nombre = "Vendor"
        user.apellido = "User"
        return user
    
    @pytest.fixture
    def mock_user_buyer(self):
        """Mock buyer user."""
        user = Mock(spec=User)
        user.id = uuid.uuid4()
        user.email = "buyer@example.com"
        user.user_type = UserType.BUYER
        user.is_active = True
        user.nombre = "Buyer"
        user.apellido = "User"
        return user
    
    @pytest.fixture
    def mock_user_inactive(self):
        """Mock inactive user."""
        user = Mock(spec=User)
        user.id = uuid.uuid4()
        user.email = "inactive@example.com"
        user.user_type = UserType.BUYER
        user.is_active = False
        user.nombre = "Inactive"
        user.apellido = "User"
        return user
    
    def test_user_type_enum_values_are_correctly_defined(self):
        """TDD: UserType enum should have correct values."""
        # RED: Verify UserType enum values
        assert hasattr(UserType, 'SUPERUSER')
        assert hasattr(UserType, 'VENDOR')
        assert hasattr(UserType, 'BUYER')
        
        # GREEN: Verify enum values
        assert UserType.SUPERUSER.value == 'SUPERUSER'
        assert UserType.VENDOR.value == 'VENDOR'
        assert UserType.BUYER.value == 'BUYER'
    
    def test_admin_user_has_superuser_type(self, mock_user_admin):
        """TDD: Admin user should have SUPERUSER type."""
        assert mock_user_admin.user_type == UserType.SUPERUSER
        assert mock_user_admin.user_type.value == 'SUPERUSER'
    
    def test_vendor_user_has_vendedor_type(self, mock_user_vendor):
        """TDD: Vendor user should have VENDEDOR type."""
        assert mock_user_vendor.user_type == UserType.VENDOR
        assert mock_user_vendor.user_type.value == 'VENDOR'
    
    def test_buyer_user_has_comprador_type(self, mock_user_buyer):
        """TDD: Buyer user should have COMPRADOR type."""
        assert mock_user_buyer.user_type == UserType.BUYER
        assert mock_user_buyer.user_type.value == 'BUYER'


class TestGetCurrentUser:
    """Test get_current_user dependency with TDD methodology."""
    
    @pytest.fixture
    def valid_token_payload(self):
        """Valid token payload for testing."""
        return {
            "sub": str(uuid.uuid4()),
            "email": "test@example.com",
            "user_type": "SUPERUSER",
            "nombre": "Test",
            "apellido": "User",
            "exp": int((datetime.now(timezone.utc).timestamp())) + 3600
        }
    
    @pytest.fixture
    def mock_credentials(self):
        """Mock HTTP authorization credentials."""
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "valid.jwt.token"
        return credentials
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token_returns_user(self, valid_token_payload, mock_credentials):
        """TDD: get_current_user should return user for valid token."""
        with patch('app.api.v1.deps.auth.decode_access_token', return_value=valid_token_payload):
            user = await get_current_user(credentials=mock_credentials)
            
            assert user is not None
            assert user.id == valid_token_payload["sub"]
            assert user.email == valid_token_payload["email"]
            assert user.user_type.value == valid_token_payload["user_type"]
            assert user.nombre == valid_token_payload["nombre"]
            assert user.apellido == valid_token_payload["apellido"]
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token_raises_http_exception(self, mock_credentials):
        """TDD: get_current_user should raise HTTPException for invalid token."""
        with patch('app.api.v1.deps.auth.decode_access_token', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=mock_credentials)
            
            assert exc_info.value.status_code == 401
            assert "Could not validate credentials" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_current_user_missing_user_id_raises_http_exception(self, mock_credentials):
        """TDD: get_current_user should raise HTTPException for token without user ID."""
        invalid_payload = {
            "email": "test@example.com",
            "user_type": "SUPERUSER"
            # Missing 'sub' field
        }
        
        with patch('app.api.v1.deps.auth.decode_access_token', return_value=invalid_payload):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=mock_credentials)
            
            assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_missing_email_raises_http_exception(self, mock_credentials):
        """TDD: get_current_user should raise HTTPException for token without email."""
        invalid_payload = {
            "sub": str(uuid.uuid4()),
            "user_type": "SUPERUSER"
            # Missing 'email' field
        }
        
        with patch('app.api.v1.deps.auth.decode_access_token', return_value=invalid_payload):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=mock_credentials)
            
            assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_user_type_raises_http_exception(self, mock_credentials):
        """TDD: get_current_user should raise HTTPException for invalid user type."""
        invalid_payload = {
            "sub": str(uuid.uuid4()),
            "email": "test@example.com",
            "user_type": "INVALID_TYPE",
            "nombre": "Test",
            "apellido": "User"
        }
        
        with patch('app.api.v1.deps.auth.decode_access_token', return_value=invalid_payload):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=mock_credentials)
            
            assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_none_credentials_raises_http_exception(self):
        """TDD: get_current_user should raise HTTPException for None credentials."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=None)
        
        assert exc_info.value.status_code == 401


class TestGetCurrentActiveUser:
    """Test get_current_active_user dependency with TDD methodology."""
    
    @pytest.fixture
    def mock_active_user(self):
        """Mock active user."""
        user = Mock()
        user.is_active = True
        user.email = "active@example.com"
        user.user_type = UserType.BUYER
        return user
    
    @pytest.fixture
    def mock_inactive_user(self):
        """Mock inactive user."""
        user = Mock()
        user.is_active = False
        user.email = "inactive@example.com"
        user.user_type = UserType.BUYER
        return user
    
    @pytest.mark.asyncio
    async def test_get_current_active_user_active_user_returns_user(self, mock_active_user):
        """TDD: get_current_active_user should return active user."""
        user = await get_current_active_user(current_user=mock_active_user)
        
        assert user is mock_active_user
        assert user.is_active is True
    
    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive_user_raises_http_exception(self, mock_inactive_user):
        """TDD: get_current_active_user should raise HTTPException for inactive user."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(current_user=mock_inactive_user)
        
        assert exc_info.value.status_code == 400
        assert "Inactive user" in str(exc_info.value.detail)


class TestRoleRequirements:
    """Test role requirement functions with TDD methodology."""
    
    @pytest.fixture
    def mock_admin_user(self):
        """Mock admin user."""
        user = Mock()
        user.user_type = UserType.SUPERUSER
        user.is_active = True
        user.email = "admin@example.com"
        return user
    
    @pytest.fixture
    def mock_vendor_user(self):
        """Mock vendor user."""
        user = Mock()
        user.user_type = UserType.VENDOR
        user.is_active = True
        user.email = "vendor@example.com"
        return user
    
    @pytest.fixture
    def mock_buyer_user(self):
        """Mock buyer user."""
        user = Mock()
        user.user_type = UserType.BUYER
        user.is_active = True
        user.email = "buyer@example.com"
        return user
    
    def test_require_roles_with_matching_role_returns_user(self, mock_admin_user):
        """TDD: require_roles should return user when role matches."""
        required_roles = [UserType.SUPERUSER, UserType.VENDOR]
        
        user = require_roles(required_roles)(mock_admin_user)
        
        assert user is mock_admin_user
    
    def test_require_roles_with_non_matching_role_raises_http_exception(self, mock_buyer_user):
        """TDD: require_roles should raise HTTPException when role doesn't match."""
        required_roles = [UserType.SUPERUSER, UserType.VENDOR]
        
        with pytest.raises(HTTPException) as exc_info:
            require_roles(required_roles)(mock_buyer_user)
        
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)
    
    def test_require_roles_with_multiple_valid_roles_accepts_any(self, mock_vendor_user):
        """TDD: require_roles should accept user with any of the required roles."""
        required_roles = [UserType.SUPERUSER, UserType.VENDOR]
        
        user = require_roles(required_roles)(mock_vendor_user)
        
        assert user is mock_vendor_user
    
    def test_require_roles_with_empty_roles_list_accepts_all(self, mock_buyer_user):
        """TDD: require_roles with empty list should accept all users."""
        required_roles = []
        
        user = require_roles(required_roles)(mock_buyer_user)
        
        assert user is mock_buyer_user
    
    def test_require_admin_accepts_superuser(self, mock_admin_user):
        """TDD: require_admin should accept SUPERUSER."""
        user = require_admin(mock_admin_user)
        
        assert user is mock_admin_user
    
    def test_require_admin_rejects_vendor(self, mock_vendor_user):
        """TDD: require_admin should reject VENDEDOR."""
        with pytest.raises(HTTPException) as exc_info:
            require_admin(mock_vendor_user)
        
        assert exc_info.value.status_code == 403
    
    def test_require_admin_rejects_buyer(self, mock_buyer_user):
        """TDD: require_admin should reject COMPRADOR."""
        with pytest.raises(HTTPException) as exc_info:
            require_admin(mock_buyer_user)
        
        assert exc_info.value.status_code == 403
    
    def test_require_vendor_accepts_vendor(self, mock_vendor_user):
        """TDD: require_vendor should accept VENDEDOR."""
        user = require_vendor(mock_vendor_user)
        
        assert user is mock_vendor_user
    
    def test_require_vendor_accepts_admin(self, mock_admin_user):
        """TDD: require_vendor should accept SUPERUSER (admin privileges)."""
        user = require_vendor(mock_admin_user)
        
        assert user is mock_admin_user
    
    def test_require_vendor_rejects_buyer(self, mock_buyer_user):
        """TDD: require_vendor should reject COMPRADOR."""
        with pytest.raises(HTTPException) as exc_info:
            require_vendor(mock_buyer_user)
        
        assert exc_info.value.status_code == 403
    
    def test_require_buyer_accepts_buyer(self, mock_buyer_user):
        """TDD: require_buyer should accept COMPRADOR."""
        user = require_buyer(mock_buyer_user)
        
        assert user is mock_buyer_user
    
    def test_require_buyer_accepts_admin(self, mock_admin_user):
        """TDD: require_buyer should accept SUPERUSER (admin privileges)."""
        user = require_buyer(mock_admin_user)
        
        assert user is mock_admin_user
    
    def test_require_buyer_rejects_vendor(self, mock_vendor_user):
        """TDD: require_buyer should reject VENDEDOR."""
        with pytest.raises(HTTPException) as exc_info:
            require_buyer(mock_vendor_user)
        
        assert exc_info.value.status_code == 403


class TestAuthorizationEdgeCases:
    """Test edge cases in authorization with TDD methodology."""
    
    @pytest.fixture
    def mock_user_with_none_type(self):
        """Mock user with None user_type."""
        user = Mock()
        user.user_type = None
        user.is_active = True
        user.email = "notype@example.com"
        return user
    
    def test_require_roles_with_none_user_type_raises_http_exception(self, mock_user_with_none_type):
        """TDD: require_roles should handle None user_type gracefully."""
        required_roles = [UserType.SUPERUSER]
        
        with pytest.raises(HTTPException) as exc_info:
            require_roles(required_roles)(mock_user_with_none_type)
        
        assert exc_info.value.status_code == 403
    
    def test_require_admin_with_none_user_type_raises_http_exception(self, mock_user_with_none_type):
        """TDD: require_admin should handle None user_type gracefully."""
        with pytest.raises(HTTPException) as exc_info:
            require_admin(mock_user_with_none_type)
        
        assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_malformed_token_payload(self):
        """TDD: get_current_user should handle malformed token payload."""
        malformed_payloads = [
            {},  # Empty payload
            {"sub": "invalid-uuid"},  # Invalid UUID
            {"sub": str(uuid.uuid4())},  # Missing other required fields
            {"email": "test@example.com"},  # Missing sub
            {"sub": str(uuid.uuid4()), "email": "invalid-email"},  # Invalid email
        ]
        
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "malformed.jwt.token"
        
        for payload in malformed_payloads:
            with patch('app.api.v1.deps.auth.decode_access_token', return_value=payload):
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(credentials=mock_credentials)
                
                assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_token_decode_exception(self):
        """TDD: get_current_user should handle token decode exceptions."""
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "exception.jwt.token"
        
        with patch('app.api.v1.deps.auth.decode_access_token', side_effect=Exception("Decode error")):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=mock_credentials)
            
            assert exc_info.value.status_code == 401


class TestRoleBasedAccessIntegration:
    """Integration tests for role-based access control."""
    
    @pytest.mark.asyncio
    async def test_full_authentication_authorization_flow_admin(self):
        """TDD: Test complete auth flow for admin user."""
        # Create token for admin user
        admin_data = {
            "sub": str(uuid.uuid4()),
            "email": "admin@example.com",
            "user_type": "SUPERUSER",
            "nombre": "Admin",
            "apellido": "User"
        }
        
        token = create_access_token(admin_data)
        
        # Create credentials
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        # Test authentication
        current_user = await get_current_user(credentials=credentials)
        assert current_user.user_type == UserType.SUPERUSER
        
        # Test active user check
        current_user.is_active = True
        active_user = await get_current_active_user(current_user=current_user)
        assert active_user is current_user
        
        # Test admin authorization
        admin_user = require_admin(active_user)
        assert admin_user is active_user
        
        # Test vendor authorization (admin should have access)
        vendor_user = require_vendor(active_user)
        assert vendor_user is active_user
        
        # Test buyer authorization (admin should have access)
        buyer_user = require_buyer(active_user)
        assert buyer_user is active_user
    
    @pytest.mark.asyncio
    async def test_full_authentication_authorization_flow_vendor(self):
        """TDD: Test complete auth flow for vendor user."""
        # Create token for vendor user
        vendor_data = {
            "sub": str(uuid.uuid4()),
            "email": "vendor@example.com",
            "user_type": "VENDOR",
            "nombre": "Vendor",
            "apellido": "User"
        }
        
        token = create_access_token(vendor_data)
        
        # Create credentials
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        # Test authentication
        current_user = await get_current_user(credentials=credentials)
        assert current_user.user_type == UserType.VENDOR
        
        # Test active user check
        current_user.is_active = True
        active_user = await get_current_active_user(current_user=current_user)
        assert active_user is current_user
        
        # Test vendor authorization (should pass)
        vendor_user = require_vendor(active_user)
        assert vendor_user is active_user
        
        # Test admin authorization (should fail)
        with pytest.raises(HTTPException):
            require_admin(active_user)
        
        # Test buyer authorization (should fail)
        with pytest.raises(HTTPException):
            require_buyer(active_user)
    
    @pytest.mark.asyncio
    async def test_full_authentication_authorization_flow_buyer(self):
        """TDD: Test complete auth flow for buyer user."""
        # Create token for buyer user
        buyer_data = {
            "sub": str(uuid.uuid4()),
            "email": "buyer@example.com",
            "user_type": "BUYER",
            "nombre": "Buyer",
            "apellido": "User"
        }
        
        token = create_access_token(buyer_data)
        
        # Create credentials
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        # Test authentication
        current_user = await get_current_user(credentials=credentials)
        assert current_user.user_type == UserType.BUYER
        
        # Test active user check
        current_user.is_active = True
        active_user = await get_current_active_user(current_user=current_user)
        assert active_user is current_user
        
        # Test buyer authorization (should pass)
        buyer_user = require_buyer(active_user)
        assert buyer_user is active_user
        
        # Test admin authorization (should fail)
        with pytest.raises(HTTPException):
            require_admin(active_user)
        
        # Test vendor authorization (should fail)
        with pytest.raises(HTTPException):
            require_vendor(active_user)


class TestRoleBasedAccessPerformance:
    """Performance tests for role-based access control."""
    
    def test_role_checking_performance(self):
        """TDD: Role checking should be performant."""
        import time
        
        # Create mock user
        user = Mock()
        user.user_type = UserType.SUPERUSER
        user.is_active = True
        
        # Measure role checking time
        start_time = time.time()
        for _ in range(1000):  # Check role 1000 times
            require_admin(user)
        end_time = time.time()
        
        duration = end_time - start_time
        avg_time = duration / 1000
        
        # Should check role in less than 0.1ms on average
        assert avg_time < 0.0001, f"Role checking took {avg_time:.6f}s, expected < 0.0001s"
    
    @pytest.mark.asyncio
    async def test_user_authentication_performance(self):
        """TDD: User authentication should be performant."""
        import time
        
        # Create valid token
        user_data = {
            "sub": str(uuid.uuid4()),
            "email": "test@example.com",
            "user_type": "SUPERUSER",
            "nombre": "Test",
            "apellido": "User"
        }
        
        token = create_access_token(user_data)
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        # Measure authentication time
        start_time = time.time()
        for _ in range(100):  # Authenticate 100 times
            await get_current_user(credentials=credentials)
        end_time = time.time()
        
        duration = end_time - start_time
        avg_time = duration / 100
        
        # Should authenticate in less than 10ms on average
        assert avg_time < 0.01, f"Authentication took {avg_time:.4f}s, expected < 0.01s"


if __name__ == "__main__":
    # Run with: python -m pytest tests/unit/auth/test_role_based_access.py -v
    pytest.main([__file__, "-v", "--tb=short", "--cov=app.api.v1.deps.auth"])
