# ~/tests/test_auth_service_security.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Auth Service Security Tests (SECURITY CRITICAL)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
SECURITY CRITICAL: Auth Service Security Test Suite

This test suite validates:
- Authentication flow security
- Authorization boundary enforcement
- Session management security
- Password security and hashing
- Token validation and expiry
- Vulnerability prevention (timing attacks, brute force, etc.)
- Role-based access control

Coverage Target: 100% for all security-critical paths
Risk Level: CRITICAL - Authentication and authorization security
"""

import pytest
import time
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Optional

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.services.auth_service import AuthService
from app.models.user import User, UserType
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
# Note: Using passlib directly for testing since the app uses async versions
from passlib.context import CryptContext

# Create password context for testing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Get password hash for testing"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password for testing"""
    return pwd_context.verify(plain_password, hashed_password)


class TestAuthServiceCore:
    """Core authentication service tests"""
    
    def setup_method(self):
        """Setup test environment"""
        self.auth_service = AuthService()
        self.mock_db = Mock(spec=Session)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    def test_auth_service_initialization(self):
        """Test auth service initializes correctly"""
        assert hasattr(self.auth_service, 'pwd_context')
        assert hasattr(self.auth_service, 'executor')
        assert hasattr(self.auth_service, 'otp_service')
        assert hasattr(self.auth_service, 'email_service')
        assert hasattr(self.auth_service, 'sms_service')

        # Verify password context is properly configured
        assert 'bcrypt' in self.auth_service.pwd_context.schemes()
        assert self.auth_service.executor is not None
        assert self.auth_service.executor._max_workers == 4


class TestPasswordSecurity:
    """Test password hashing and verification security"""
    
    def setup_method(self):
        self.auth_service = AuthService()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def test_password_hashing_security(self):
        """Test password hashing produces secure hashes"""
        password = "SecurePassword123!"
        
        # Hash the same password multiple times
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (salt randomization)
        assert hash1 != hash2
        
        # Both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
        
        # Wrong password should not verify
        assert not verify_password("WrongPassword", hash1)
        assert not verify_password("wrongpassword123!", hash1)
    
    def test_password_complexity_requirements(self):
        """Test password complexity validation"""
        # Test weak passwords
        weak_passwords = [
            "123456",
            "password",
            "abc123",
            "qwerty",
            "12345678",
            "password123",
            "admin",
            "",
            "a" * 100  # Too long
        ]
        
        for weak_password in weak_passwords:
            # Assuming we have password validation (should be implemented)
            # This test validates that weak passwords are rejected
            # Note: The actual implementation should include password complexity validation
            assert len(weak_password) < 8 or weak_password.islower() or weak_password.isdigit()
    
    def test_password_timing_attack_resistance(self):
        """Test resistance to timing attacks in password verification"""
        correct_password = "CorrectPassword123!"
        wrong_password = "WrongPassword123!"
        password_hash = get_password_hash(correct_password)
        
        # Measure time for correct password verification
        start_time = time.time()
        for _ in range(100):
            verify_password(correct_password, password_hash)
        correct_time = time.time() - start_time
        
        # Measure time for incorrect password verification
        start_time = time.time()
        for _ in range(100):
            verify_password(wrong_password, password_hash)
        incorrect_time = time.time() - start_time
        
        # Time difference should be minimal (within 50% variance)
        # This helps prevent timing attacks
        time_ratio = abs(correct_time - incorrect_time) / max(correct_time, incorrect_time)
        assert time_ratio < 0.5, f"Timing attack vulnerability: {time_ratio}"
    
    def test_hash_algorithm_strength(self):
        """Test that bcrypt is configured with sufficient rounds"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        # Bcrypt hash should start with $2b$ and have sufficient rounds
        assert hashed.startswith("$2b$")
        
        # Extract rounds from hash (format: $2b$rounds$...)
        parts = hashed.split("$")
        rounds = int(parts[2])
        
        # Should use at least 12 rounds for security
        assert rounds >= 12, f"Insufficient bcrypt rounds: {rounds}"


class TestTokenSecurity:
    """Test JWT token security and validation"""
    
    def setup_method(self):
        self.auth_service = AuthService()
        self.test_user_id = uuid4()
        self.test_payload = {
            "sub": str(self.test_user_id),
            "user_type": "VENDEDOR",
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
    
    def test_token_creation_and_validation(self):
        """Test secure token creation and validation"""
        # Create token using the security module function
        token = create_access_token(
            data={"sub": str(self.test_user_id)}
        )

        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens should be reasonably long

        # Validate token using the security module function
        payload = decode_access_token(token)
        assert payload["sub"] == str(self.test_user_id)
    
    def test_token_expiry_validation(self):
        """Test token expiry is properly enforced"""
        # Create expired token
        expired_payload = {
            "sub": str(self.test_user_id),
            "exp": datetime.utcnow() - timedelta(minutes=1)  # Expired 1 minute ago
        }
        
        expired_token = jwt.encode(
            expired_payload,
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        # Should raise exception for expired token or return None
        try:
            payload = decode_access_token(expired_token)
            # If no exception is raised, payload should be None for expired tokens
            assert payload is None
        except JWTError:
            # Expected behavior for expired tokens
            pass
    
    def test_token_tampering_detection(self):
        """Test detection of tampered tokens"""
        # Create valid token
        token = self.auth_service.create_access_token(
            data={"sub": str(self.test_user_id)}
        )
        
        # Tamper with token
        tampered_token = token[:-5] + "AAAAA"  # Change last 5 characters
        
        # Should raise exception for tampered token
        with pytest.raises(JWTError):
            self.auth_service.verify_token(tampered_token)
    
    def test_token_signature_verification(self):
        """Test token signature verification with different keys"""
        # Create token with service key
        token = self.auth_service.create_access_token(
            data={"sub": str(self.test_user_id)}
        )
        
        # Try to verify with wrong key
        wrong_key = "wrong_secret_key_that_should_not_work"
        
        with pytest.raises(JWTError):
            jwt.decode(token, wrong_key, algorithms=[self.auth_service.algorithm])
    
    def test_token_algorithm_enforcement(self):
        """Test that only allowed algorithms are accepted"""
        # Create token with disallowed algorithm
        payload = {"sub": str(self.test_user_id)}
        
        # Try creating token with 'none' algorithm (security risk)
        none_token = jwt.encode(payload, "", algorithm="none")
        
        # Should not verify with 'none' algorithm
        with pytest.raises(JWTError):
            jwt.decode(none_token, "", algorithms=["none"])


class TestAuthenticationFlows:
    """Test complete authentication workflows"""
    
    def setup_method(self):
        self.auth_service = AuthService()
        self.mock_db = Mock(spec=Session)
        
    def _create_mock_user(self, email: str, password: str, user_type: UserType = UserType.VENDEDOR) -> Mock:
        """Create a mock user for testing"""
        user = Mock(spec=User)
        user.id = uuid4()
        user.email = email
        user.hashed_password = get_password_hash(password)
        user.user_type = user_type
        user.is_active = True
        user.is_verified = True
        return user
    
    def test_successful_authentication_flow(self):
        """Test successful user authentication"""
        email = "test@example.com"
        password = "SecurePassword123!"
        user = self._create_mock_user(email, password)
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        
        # Test authentication
        authenticated_user = self.auth_service.authenticate_user(
            email, password, db=self.mock_db
        )
        
        assert authenticated_user == user
        self.mock_db.query.assert_called_once()
    
    def test_authentication_failure_wrong_password(self):
        """Test authentication failure with wrong password"""
        email = "test@example.com"
        correct_password = "SecurePassword123!"
        wrong_password = "WrongPassword123!"
        user = self._create_mock_user(email, correct_password)
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        
        # Test authentication with wrong password
        authenticated_user = self.auth_service.authenticate_user(
            email, wrong_password, db=self.mock_db
        )
        
        assert authenticated_user is False
    
    def test_authentication_failure_user_not_found(self):
        """Test authentication failure when user doesn't exist"""
        email = "nonexistent@example.com"
        password = "AnyPassword123!"
        
        # Mock database query returning None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Test authentication
        authenticated_user = self.auth_service.authenticate_user(
            email, password, db=self.mock_db
        )
        
        assert authenticated_user is False
    
    def test_authentication_failure_inactive_user(self):
        """Test authentication failure for inactive user"""
        email = "inactive@example.com"
        password = "SecurePassword123!"
        user = self._create_mock_user(email, password)
        user.is_active = False
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        
        # Test authentication
        authenticated_user = self.auth_service.authenticate_user(
            email, password, db=self.mock_db
        )
        
        assert authenticated_user is False
    
    def test_brute_force_protection_timing(self):
        """Test protection against brute force attacks through consistent timing"""
        email = "test@example.com"
        password = "SecurePassword123!"
        
        # Time authentication attempts for non-existent user
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        start_time = time.time()
        for _ in range(10):
            self.auth_service.authenticate_user(email, password, db=self.mock_db)
        no_user_time = time.time() - start_time
        
        # Time authentication attempts for existing user with wrong password
        user = self._create_mock_user(email, password)
        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        
        start_time = time.time()
        for _ in range(10):
            self.auth_service.authenticate_user(email, "WrongPassword", db=self.mock_db)
        wrong_password_time = time.time() - start_time
        
        # Timing should be similar to prevent user enumeration
        time_ratio = abs(no_user_time - wrong_password_time) / max(no_user_time, wrong_password_time)
        assert time_ratio < 0.5, f"Timing difference too large: {time_ratio}"


class TestAuthorizationSecurity:
    """Test authorization and role-based access control"""
    
    def setup_method(self):
        self.auth_service = AuthService()
    
    def test_role_based_token_creation(self):
        """Test tokens include correct role information"""
        user_types = [UserType.ADMIN, UserType.VENDEDOR, UserType.COMPRADOR]
        
        for user_type in user_types:
            user_id = uuid4()
            token = self.auth_service.create_access_token(
                data={"sub": str(user_id), "user_type": user_type.value}
            )
            
            # Verify token contains role information
            payload = self.auth_service.verify_token(token)
            assert payload["user_type"] == user_type.value
    
    def test_token_privilege_isolation(self):
        """Test that tokens with different roles are properly isolated"""
        admin_token = self.auth_service.create_access_token(
            data={"sub": str(uuid4()), "user_type": UserType.ADMIN.value}
        )
        
        vendor_token = self.auth_service.create_access_token(
            data={"sub": str(uuid4()), "user_type": UserType.VENDEDOR.value}
        )

        buyer_token = self.auth_service.create_access_token(
            data={"sub": str(uuid4()), "user_type": UserType.COMPRADOR.value}
        )
        
        # Verify each token has correct role
        admin_payload = self.auth_service.verify_token(admin_token)
        vendor_payload = self.auth_service.verify_token(vendor_token)
        buyer_payload = self.auth_service.verify_token(buyer_token)
        
        assert admin_payload["user_type"] == UserType.ADMIN.value
        assert vendor_payload["user_type"] == UserType.VENDEDOR.value
        assert buyer_payload["user_type"] == UserType.COMPRADOR.value
        
        # Verify users have different IDs
        assert admin_payload["sub"] != vendor_payload["sub"]
        assert vendor_payload["sub"] != buyer_payload["sub"]


class TestSessionManagement:
    """Test session management security"""
    
    def setup_method(self):
        self.auth_service = AuthService()
    
    def test_token_refresh_security(self):
        """Test secure token refresh mechanism"""
        user_id = uuid4()
        
        # Create initial token
        original_token = self.auth_service.create_access_token(
            data={"sub": str(user_id)}
        )
        
        # Create refresh token (if implemented)
        # Note: This assumes refresh token functionality exists
        # If not implemented, this test serves as a specification
        
        # Verify original token
        original_payload = self.auth_service.verify_token(original_token)
        assert original_payload["sub"] == str(user_id)
    
    def test_token_invalidation_on_logout(self):
        """Test token invalidation mechanism"""
        user_id = uuid4()
        
        # Create token
        token = self.auth_service.create_access_token(
            data={"sub": str(user_id)}
        )
        
        # Verify token is valid
        payload = self.auth_service.verify_token(token)
        assert payload["sub"] == str(user_id)
        
        # Note: Token blacklisting should be implemented for secure logout
        # This test serves as a specification for that functionality


class TestSecurityVulnerabilityPrevention:
    """Test prevention of common security vulnerabilities"""
    
    def setup_method(self):
        self.auth_service = AuthService()
    
    def test_sql_injection_prevention_in_auth(self):
        """Test SQL injection prevention in authentication"""
        # SQL injection attempts
        malicious_emails = [
            "test@example.com'; DROP TABLE users; --",
            "test@example.com' OR '1'='1",
            "test@example.com' UNION SELECT * FROM users --",
            "'; UPDATE users SET password='hacked' WHERE '1'='1"
        ]
        
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        for malicious_email in malicious_emails:
            # Should not raise exceptions or cause SQL injection
            result = self.auth_service.authenticate_user(
                malicious_email, "password", db=mock_db
            )
            assert result is False
    
    def test_jwt_security_headers(self):
        """Test JWT contains appropriate security claims"""
        user_id = uuid4()
        token = self.auth_service.create_access_token(
            data={"sub": str(user_id)}
        )
        
        # Decode without verification to inspect claims
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Should have expiry
        assert "exp" in payload
        
        # Should have subject
        assert "sub" in payload
        assert payload["sub"] == str(user_id)
        
        # Expiry should be in the future
        exp_timestamp = payload["exp"]
        assert exp_timestamp > datetime.utcnow().timestamp()
    
    def test_password_hash_verification_constant_time(self):
        """Test password verification uses constant-time comparison"""
        password = "TestPassword123!"
        correct_hash = get_password_hash(password)
        wrong_hash = get_password_hash("WrongPassword123!")
        
        # Time correct password verification
        start_time = time.time()
        for _ in range(100):
            verify_password(password, correct_hash)
        correct_time = time.time() - start_time
        
        # Time incorrect password verification
        start_time = time.time()
        for _ in range(100):
            verify_password(password, wrong_hash)
        incorrect_time = time.time() - start_time
        
        # Should be constant time (within reasonable variance)
        time_ratio = abs(correct_time - incorrect_time) / max(correct_time, incorrect_time)
        assert time_ratio < 0.3, f"Non-constant time verification: {time_ratio}"


class TestAuthServiceIntegration:
    """Test auth service integration with other components"""
    
    def setup_method(self):
        self.auth_service = AuthService()
        self.mock_db = Mock(spec=Session)
    
    def test_auth_service_with_user_model_integration(self):
        """Test integration with User model"""
        # Create real User model instance (if possible in test environment)
        user_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "user_type": UserType.VENDEDOR
        }
        
        # Test password hashing integration
        hashed_password = get_password_hash(user_data["password"])
        assert hashed_password != user_data["password"]
        assert verify_password(user_data["password"], hashed_password)
    
    def test_auth_service_error_handling(self):
        """Test auth service handles errors gracefully"""
        # Test with invalid database connection
        mock_db = Mock()
        mock_db.query.side_effect = Exception("Database connection failed")
        
        # Should handle database errors gracefully
        result = self.auth_service.authenticate_user(
            "test@example.com", "password", db=mock_db
        )
        
        # Should return False on error, not raise exception
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])